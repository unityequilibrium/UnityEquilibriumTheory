"""Finite-q acoustic thermal insertion, cross-covariance and static population.

No relaxation time is assigned. The Bose divided difference supplies the
equilibrium static intrabranch term; it is not a homogeneous collision rate.
"""

from datetime import datetime, timezone
import json
from math import isfinite, pi
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Thermal_Virtual_Response as VIRT
import Research_T13_Thermal_Mode_Quadrature as QUAD

EFT, TH, INT, MOD, CURV, PREFIX = VIRT.EFT, VIRT.TH, VIRT.INT, VIRT.MOD, VIRT.CURV, VIRT.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_finite_q_thermal_source_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_finite_q_thermal_source.json")
MU_GRID, MOMENTUM_TRIPLES = (1.05, 1.2), ((.005, .011, .008), (.02, .031, .02), (.04, .037, .02))
COVARIANCE_TEMPERATURE = .004
TEMPERATURE_DIVISORS = (256, 512)
ORDERS, ANGULAR_ORDERS, TAILS = (24, 48, 96), (32, 64, 128), (32., 40.)
STATIC_Q_RATIOS = (1/16, 1/32, 1/64)
DYNAMIC_Q_GRID, FREQUENCIES = (.01, .005, .0025), (.02j, .05j, .03+.02j)
GATES = {"identity_relative": 1e-9, "covariance_relative": 1e-7,
         "quadrature_relative": 1e-6, "thermal_tail_relative": 1e-8,
         "static_soft_limit_relative": 1e-3, "original_causal_leakage": 1e-6}


def validate(p, r, temperature, state, action):
    TH.validate(p, temperature, state, action, 2)
    TH.validate(r, temperature, state, action, 2)


def source_response(q, z, state, action):
    if not isfinite(q) or q < 0 or not np.isfinite(z) or (z.imag == 0 and z != 0):
        raise ValueError("nonnegative q and zero or non-real frequency required")
    if q == 0 and z == 0:
        return CURV.source_jets(state, action)["first"].astype(complex)
    return np.linalg.solve(VIRT.kernel(q, z, state, action), [0., 0., 1.])


def insertion(p, r, z, state, action):
    if not np.isfinite(z) or z.imag == 0:
        raise ValueError("non-real dynamic frequency required")
    validate(p, r, 0., state, action)
    acoustic = MOD.mode(p, state, action)
    energy, unit = acoustic["omega"], acoustic["polarization"]
    legs = MOD.cubic_tensor(state, action)@unit
    plus = np.linalg.inv(VIRT.kernel(r, energy+z, state, action))
    minus = np.linalg.inv(VIRT.kernel(r, energy-z, state, action))
    return (legs.conjugate()@plus@legs.T+(legs.conjugate()@minus@legs.T).T)/(2*energy)


def angular_insertion(p, q, z, state, action, angles, weights):
    acoustic = MOD.mode(p, state, action)
    energy, unit = acoustic["omega"], acoustic["polarization"]
    kinetic, linear, v0 = VIRT.matrices(0., state, action)
    r_squared = (p-q)**2+2*p*q*(1+angles)
    potentials = v0+r_squared[:, None, None]*kinetic
    plus = np.linalg.inv(potentials-(energy+z)**2*kinetic+(energy+z)*linear)
    minus = np.linalg.inv(potentials-(energy-z)**2*kinetic+(energy-z)*linear)
    legs = MOD.cubic_tensor(state, action)@unit
    first = np.einsum("ia,nab,jb->nij", legs.conjugate(), plus, legs)
    second = np.einsum("ia,nab,jb->nji", legs.conjugate(), minus, legs)
    return np.einsum("n,nij->ij", weights/2, first+second)/(2*energy)


def paired_bubble(p, r, z, temperature, state, action):
    validate(p, r, temperature, state, action)
    if temperature == 0:
        return np.zeros((3, 3), dtype=complex)
    npop = TH.bose(TH.energy_value(p, state, action)/temperature)
    rpop = TH.bose(TH.energy_value(r, state, action)/temperature)
    return .5*(npop*insertion(p, r, z, state, action)+rpop*insertion(r, p, z, state, action))


def evolution_and_covariance(p, temperature, state, action):
    kinetic, linear, potential = VIRT.matrices(p, state, action)
    evolution = np.block([[np.zeros((3, 3)), np.eye(3)],
                          [-np.linalg.solve(kinetic, potential), -np.linalg.solve(kinetic, (1j*linear).real)]])
    acoustic = MOD.mode(p, state, action)
    energy, unit = acoustic["omega"], acoustic["polarization"]
    vector = np.concatenate([unit, -1j*energy*unit])
    occupation = TH.bose(energy/temperature) if temperature else 0.
    return evolution, occupation*np.outer(vector, vector.conjugate()).real/energy


def cross_covariance_bubble(p, r, z, temperature, state, action):
    validate(p, r, temperature, state, action)
    if not np.isfinite(z) or z.imag == 0:
        raise ValueError("non-real frequency required for cross-covariance solve")
    ap, cp = evolution_and_covariance(p, temperature, state, action)
    ar, cr = evolution_and_covariance(r, temperature, state, action)
    kinetic = VIRT.matrices(p, state, action)[0]
    operator = -1j*z*np.eye(36)-np.kron(ar, np.eye(6))-np.kron(np.eye(6), ap)
    cubic, result = MOD.cubic_tensor(state, action), np.zeros((3, 3), dtype=complex)
    for j in range(3):
        drive_matrix = np.zeros((6, 6))
        drive_matrix[3:, :3] = -np.linalg.solve(kinetic, cubic[j])
        drive = drive_matrix@cp+cr@drive_matrix.T
        response = np.linalg.solve(operator, drive.reshape(36)).reshape(6, 6)
        result[:, j] = -.5*np.einsum("iab,ab->i", cubic, response[:3, :3])
    return result


def bose_divided_difference(first, second, temperature):
    if not all(isfinite(x) and x > 0 for x in (first, second, temperature)):
        raise ValueError("positive finite energies and T required")
    lower, upper = min(first, second), max(first, second)
    width = (upper-lower)/temperature
    factor = -np.expm1(-width)/width if width else 1.
    return float(TH.bose(lower/temperature)*(1+TH.bose(upper/temperature))*factor/temperature)


def static_vertex(q, state, action):
    source = source_response(q, 0., state, action).real
    vertex = np.einsum("ijk,k->ij", MOD.cubic_tensor(state, action), source)
    # The radial static equation fixes this small phase entry exactly.
    vertex[1, 1] = -q*q*source[0]/np.sqrt(state["s"])
    return vertex, source


def static_channels(p, r, q, temperature, state, action, modes_p=None, modes_r=None):
    validate(p, r, temperature, state, action)
    if temperature == 0:
        return {"pair": 0., "intrabranch_population": 0., "mixed_number": 0.}
    modes_p = VIRT.tree_modes(p, state, action) if modes_p is None else modes_p
    modes_r = VIRT.tree_modes(r, state, action) if modes_r is None else modes_r
    vertex, _ = static_vertex(q, state, action)
    result = {"pair": 0., "intrabranch_population": 0., "mixed_number": 0.}
    for i, (ep, up) in enumerate(modes_p):
        for j, (er, ur) in enumerate(modes_r):
            if i != 0 and j != 0:
                continue
            npop = TH.bose(ep/temperature) if i == 0 else 0.
            rpop = TH.bose(er/temperature) if j == 0 else 0.
            pair = abs(up@vertex@ur)**2
            number = abs(np.vdot(up, vertex@ur))**2
            result["pair"] += float((npop+rpop)*pair/(4*ep*er*(ep+er)))
            if i == j == 0:
                divided = bose_divided_difference(ep, er, temperature)
                result["intrabranch_population"] += float(divided*number/(4*ep*er))
            else:
                if er == ep:
                    raise ValueError("unadmitted acoustic-heavy degeneracy")
                result["mixed_number"] += float((npop-rpop)*number/(4*ep*er*(er-ep)))
    return result


def radial_nodes(order, tail, split):
    if order < 2 or not isfinite(tail) or tail <= 16:
        raise ValueError("finite declared integration rule required")
    edges = sorted(set([0., 1., 4., 8., 16., tail]+([split] if 0 < split < tail else [])))
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return [(left+(node+1)*(right-left)/2, weight*(right-left)/2)
            for left, right in zip(edges[:-1], edges[1:]) for node, weight in zip(nodes, weights)]


def static_thermal(q, temperature, state, action, order=48, angular_order=64, tail=40.):
    TH.validate(.02, temperature, state, action, order)
    vertex, source = static_vertex(q, state, action)
    if angular_order < 2:
        raise ValueError("declared angular order required")
    names = ("pair", "intrabranch_population", "mixed_number", "contact", "chi")
    result = dict.fromkeys(names, 0.)
    if temperature == 0:
        return result
    c, angular = INT.dispersion_coefficients(state, action)["c"], np.polynomial.legendre.leggauss(angular_order)
    for x, weight in radial_nodes(order, tail, q*c/temperature):
        p = temperature*x/c
        modes_p = VIRT.tree_modes(p, state, action)
        measure = weight*temperature/c*p*p/(2*pi*pi)
        n = TH.bose(modes_p[0][0]/temperature)
        if q == 0:
            channels = static_channels(p, p, q, temperature, state, action, modes_p, modes_p)
        else:
            cosines, angular_weights = angular
            momenta_r = np.sqrt((p-q)**2+2*p*q*(1+cosines))
            batch = QUAD.static_channels_batch(p, momenta_r, vertex, temperature, state, action, modes_p)
            channels = {key: float(np.dot(angular_weights/2, values)) for key, values in batch.items()}
        for key in channels:
            result[key] += measure*channels[key]
        contact = VIRT.contact_matrix(p, state, action)[0]
        result["contact"] += measure*n*float(source@contact@source)
    result["chi"] = result["pair"]+result["intrabranch_population"]+result["mixed_number"]-result["contact"]
    return result


def dynamic_thermal(q, z, temperature, state, action, order=48, angular_order=64, tail=40.):
    TH.validate(.02, temperature, state, action, order)
    left, right = source_response(q, -z, state, action), source_response(q, z, state, action)
    if z.imag == 0 or angular_order < 2:
        raise ValueError("non-real dynamic frequency and declared angular rule required")
    if temperature == 0:
        return 0j
    c, result = INT.dispersion_coefficients(state, action)["c"], 0j
    angles, weights = np.polynomial.legendre.leggauss(angular_order)
    for x, weight in radial_nodes(order, tail, q*c/temperature):
        p = temperature*x/c
        n = TH.bose(TH.energy_value(p, state, action)/temperature)
        if q == 0:
            bubble = insertion(p, p, z, state, action)
        else:
            bubble = angular_insertion(p, q, z, state, action, angles, weights)
        contact = VIRT.contact_matrix(p, state, action)[0]
        result += weight*temperature/c*p*p/(2*pi*pi)*n*(left@(bubble-contact)@right)
    return complex(result)


def audit():
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        temperature = COVARIANCE_TEMPERATURE
        points = []
        for p, r, q in MOMENTUM_TRIPLES:
            frequency_checks = []
            for z in FREQUENCIES:
                bubble = paired_bubble(p, r, z, temperature, state, action)
                covariance = cross_covariance_bubble(p, r, z, temperature, state, action)
                left, right = source_response(q, -z, state, action), source_response(q, z, state, action)
                continuity = -1j*z*(2*mu*right[0]-1j*z*right[1])+q*q*right[1]
                frequency_checks.append({"z": VIRT.encode_complex(z), "matrix_error": VIRT.matrix_error(bubble, covariance),
                    "source_projection_error": INT.relative(left@bubble@right, left@covariance@right),
                    "continuity_error": float(abs(continuity)/max(abs(z*2*mu*right[0]), 1e-30))})
            diagonal = static_channels(p, p, 0., temperature, state, action)
            modes = MOD.mode(p, state, action)
            jets = CURV.energy_jets(p, state, action)
            n = TH.bose(modes["omega"]/temperature)
            expected = n*(1+n)/temperature*jets["E_h"]**2
            points.append({"p": p, "r": r, "q": q, "momentum_cosine": (r*r-p*p-q*q)/(2*p*q), "frequency_checks": frequency_checks,
                           "diagonal_population_error": INT.relative(diagonal["intrabranch_population"], expected)})
        test_momenta = np.array([1e-7, .001, .005, .02, .031, .039])
        p, q = .02, .02
        vertex, _ = static_vertex(q, state, action)
        batch = QUAD.static_channels_batch(p, test_momenta, vertex, temperature, state, action, VIRT.tree_modes(p, state, action))
        direct = [static_channels(p, float(r), q, temperature, state, action) for r in test_momenta]
        batch_errors = {key: float(max(INT.relative(batch[key][i], row[key]) for i, row in enumerate(direct))) for key in batch}
        cf, rows = INT.dispersion_coefficients(state, action), []
        for divisor in TEMPERATURE_DIVISORS:
            temperature = cf["c"]*cf["dispersion_scale"]/divisor
            target = CURV.thermal_response(temperature, state, action, ORDERS[-1])
            zero = static_thermal(0., temperature, state, action, ORDERS[-1], ANGULAR_ORDERS[-1])
            static = []
            for ratio in STATIC_Q_RATIOS:
                q = ratio*temperature/cf["c"]
                runs = [static_thermal(q, temperature, state, action, order, angle) for order, angle in zip(ORDERS, ANGULAR_ORDERS)]
                short = static_thermal(q, temperature, state, action, ORDERS[-1], ANGULAR_ORDERS[-1], TAILS[0])
                static.append({"q": q, "q_over_thermal_momentum": ratio, **runs[-1],
                    "target_error": INT.relative(runs[-1]["chi"], target["chi_thermal"]),
                    "quadrature_error": INT.relative(runs[-2]["chi"], runs[-1]["chi"]),
                    "tail_error": INT.relative(short["chi"], runs[-1]["chi"])})
            dynamics = []
            for q in DYNAMIC_Q_GRID:
                for z in FREQUENCIES:
                    runs = [dynamic_thermal(q, z, temperature, state, action, order, angle) for order, angle in zip(ORDERS, ANGULAR_ORDERS)]
                    short = dynamic_thermal(q, z, temperature, state, action, ORDERS[-1], ANGULAR_ORDERS[-1], TAILS[0])
                    dynamics.append({"q": q, "z": VIRT.encode_complex(z), "delta_chi": VIRT.encode_complex(runs[-1]),
                                     "quadrature_error": INT.relative(runs[-2], runs[-1]), "tail_error": INT.relative(short, runs[-1])})
            rows.append({"T": temperature, "divisor": divisor, "zero_q_static": zero,
                         "zero_q_target_error": INT.relative(zero["chi"], target["chi_thermal"]),
                         "static_soft_rows": static, "dynamic_rows": dynamics})
        examples.append({"mu": mu, "cross_covariance_points": points, "thermal_rows": rows,
                         "batch_equivalence_momenta": test_momenta.tolist(), "batch_scalar_channel_errors": batch_errors})
    checks = {
        "cross_covariance_independently_matches_finite_momentum_bubble": all(max(f["matrix_error"], f["source_projection_error"]) < GATES["covariance_relative"] for e in examples for p in e["cross_covariance_points"] for f in p["frequency_checks"]),
        "finite_q_source_satisfies_charge_continuity": all(f["continuity_error"] < GATES["identity_relative"] for e in examples for p in e["cross_covariance_points"] for f in p["frequency_checks"]),
        "Bose_divided_difference_supplies_static_population": all(p["diagonal_population_error"] < GATES["identity_relative"] for e in examples for p in e["cross_covariance_points"]),
        "batched_exact_modes_and_scalar_channel_methods_agree": all(max(e["batch_scalar_channel_errors"].values()) < GATES["identity_relative"] for e in examples),
        "static_limit_returns_pressure_and_converges": all(r["zero_q_target_error"] < GATES["quadrature_relative"] and r["static_soft_rows"][-1]["target_error"] < GATES["static_soft_limit_relative"] and all(a["target_error"] > b["target_error"] for a, b in zip(r["static_soft_rows"][:-1], r["static_soft_rows"][1:])) for e in examples for r in e["thermal_rows"]),
        "static_and_dynamic_quadrature_and_tail": all(all(s["quadrature_error"] < GATES["quadrature_relative"] and s["tail_error"] < GATES["thermal_tail_relative"] for s in r["static_soft_rows"]+r["dynamic_rows"]) for e in examples for r in e["thermal_rows"])}
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_finite_q_thermal_source.py", PREFIX+"Code/03_Research/Research_T13_Thermal_Mode_Quadrature.py"]
    protected = [PREFIX+"Result/artifacts/t13_thermal_virtual_response.json", PREFIX+"Code/03_Research/Research_T13_Thermal_Virtual_Response.py", PREFIX+"Result/artifacts/t13_thermal_source_curvature.json"]+list(EFT.ACTION_PATHS)
    closed = all(checks.values())
    record = {"major_result_id": "T13_FINITE_Q_THERMAL_SOURCE_AND_STATIC_POPULATION_LIMIT", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
        "created_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if closed else "PARTIAL",
        "verification_status": "PASS_SCOPED_FINITE_Q_THERMAL_SOURCE" if closed else "FAIL_SCOPED_FINITE_Q_THERMAL_SOURCE",
        "what_is_closed": "Finite-q thermal source/cross-covariance and analytic static Bose-population limit, subject to the recorded checks",
        "equation_or_mapping": "(-iz-L_Ar,Ap) delta_Cov=delta_A Cov_p+Cov_r delta_A^T; static population uses [n(Ep)-n(Er)]/(Er-Ep)",
        "units": {"h": "E^3", "Phi": "E", "chi": "E^-2", "integrated_bubble_contact": "E^2", "Bose_divided_difference": "E^-1"},
        "derivation_class": "DERIVED_FINITE_MOMENTUM_GAUSSIAN_COVARIANCE_AND_THERMAL_SPECTRAL_RESOLUTION", "observable": "conditional action-source susceptibility, not calibrated heat transport", "data_role": "DERIVED_NOT_CALIBRATION",
        "action_controls": action, "checks": checks, "examples": examples,
        "state_variables": ["radial_fluctuation", "phase_fluctuation", "Phi_fluctuation", "tree_velocities_for_cross_covariance_only"],
        "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs"],
        "execution_note": "Initial scalar-only audit deliberately stopped before artifact after an independently verified batched-equivalence check; no failure/completion inferred from timeout. Same declared grids/gates retained.",
        "primary_references": ["https://arxiv.org/abs/cond-mat/0307246", "https://arxiv.org/abs/2310.01988"],
        "equation_registry_ids": [r["id"] for r in json.loads((ROOT/REGISTRY).read_text())["entries"]],
        "declared_grids": {"mu": MU_GRID, "momentum_triples": MOMENTUM_TRIPLES, "cross_covariance_T": COVARIANCE_TEMPERATURE, "T_divisors": TEMPERATURE_DIVISORS, "orders": ORDERS, "angular_orders": ANGULAR_ORDERS, "tails": TAILS, "static_q_ratios": STATIC_Q_RATIOS, "dynamic_q": DYNAMIC_Q_GRID, "frequencies": [VIRT.encode_complex(z) for z in FREQUENCIES], "locked_before_first_audit": True}, "thresholds": GATES,
        "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
        "controlling_blocker": "collisionless_soft_limit_full_interacting_matching_and_physical_transport_open",
        "open_blockers": ["collisionless_soft_frequency_limit_and_population_relaxation", "full_loop_source_current_Ward_and_energy_ledger", "full_vacuum_interacting_thermal_matching_and_approximation_control", "independent_material_source_readout_scale_KMS_Kubo_uncertainty"],
        "dependency_unlocked": ["collisionless_population_and_interacting_matching_research_only"] if closed else [],
        "static_population_limit_derived": True, "finite_q_source_checked_for_prescription": closed,
        "full_loop_source_current_Ward_closed": False, "full_energy_exchange_ledger_closed": False,
        "assigned_relaxation_time": False, "full_collision_operator_computed": False, "physical_Kubo_emitted": False,
        "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False, "full_two_loop_pressure_computed": False,
        "all_parent_modes_and_quantum_Phi_loops_included": False, "full_SK_KMS_matching_closed": False, "independent_alpha_Phi_K_admitted": False,
        "controlled_full_action_truncation_error_established": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "claim_promotion": False, "parameter_fitting": False, "assigned_width": False, "clipping": False, "cone_padding": False,
        "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
        "claim_boundary": "Named acoustic thermal-insertion rest-domain finite grids only. Bose static occupation variance is not a collision rate, homogeneous equilibration, physical conductivity, full SK/KMS/material/calibration, original conserved-C repair or Full Topic13/Core/UET closure."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Finite-q source/cross-covariance and static divided Bose population", record["equation_or_mapping"], checks, record["controlling_blocker"], "Resolve full recorded checks then soft-frequency/collision and physical matching without assigned relaxation", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
