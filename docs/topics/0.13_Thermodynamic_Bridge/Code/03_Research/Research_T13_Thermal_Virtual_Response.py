"""One-acoustic thermal insertion with virtual tree propagation and source contact.

The real-time Gaussian covariance response is a named extension, not a
silent heavy quantum-loop addition or a contact fitted to static residuals.
"""

from datetime import datetime, timezone
from decimal import Decimal, localcontext
from itertools import permutations
import json
from math import isfinite, pi
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Thermal_Source_Curvature as CURV

EFT, TH, INT, MOD, LAND, PREFIX = CURV.EFT, CURV.TH, CURV.INT, CURV.MOD, CURV.LAND, CURV.PREFIX
BRANCH = "t13.candidate.acoustic_thermal_insertion_tree_virtual_response_v1"
REGISTRY = PREFIX+"Data/03_Research/t13_thermal_virtual_response_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_thermal_virtual_response.json")
MU_GRID, MOMENTA = (1.05, 1.2), (.005, .02, .04)
TEMPERATURE_DIVISORS, ORDERS, TAILS = (256, 512), (24, 48, 96), (32., 40.)
FREQUENCIES = (.02j, .05j, .1j, .03+.02j)
GATES = {"identity_relative": 1e-9, "covariance_relative": 1e-7,
         "quadrature_relative": 1e-6, "thermal_tail_relative": 1e-8,
         "original_causal_leakage": 1e-6}


def matrices(p, state, action):
    EFT.validate(action)
    if state["xi"] != 0 or not isfinite(p) or p < 0:
        raise ValueError("rest-domain finite nonnegative momentum required")
    kinetic = np.diag([1., 1., action["epsilon"]*action["response_kinetic"]])
    linear = np.array([[0., 2j*state["mu"], 0.], [-2j*state["mu"], 0., 0.], [0., 0., 0.]])
    potential = LAND.parent_mass_matrix(state, action)+p*p*kinetic
    return kinetic, linear, potential


def kernel(p, z, state, action):
    kinetic, linear, potential = matrices(p, state, action)
    if not np.isfinite(z):
        raise ValueError("finite frequency required")
    return potential-z*z*kinetic+z*linear


def tree_modes(p, state, action):
    TH.validate(p, 0., state, action, 2)
    kinetic, linear, potential = matrices(p, state, action)
    companion = np.block([[np.zeros((3, 3)), np.eye(3)],
                          [np.linalg.solve(kinetic, potential), np.linalg.solve(kinetic, linear)]])
    eigenvalues = np.linalg.eigvals(companion)
    if max(abs(eigenvalues.imag)) > 1e-9:
        raise ValueError("real stable tree frequencies required")
    energies = sorted(value.real for value in eigenvalues if value.real > 0)
    if len(energies) != 3 or min(np.diff(energies)) < 1e-6:
        raise ValueError("three separated positive tree modes required")
    acoustic = MOD.mode(p, state, action)
    result = [(acoustic["omega"], acoustic["polarization"])]
    for energy in energies[1:]:
        values, vectors = np.linalg.eigh(potential-energy*energy*kinetic+energy*linear)
        unit = vectors[:, int(np.argmin(abs(values)))]
        norm = float(-np.vdot(unit, (-2*energy*kinetic+linear)@unit).real)
        if norm <= 0:
            raise ValueError("positive tree pole norm required")
        result.append((float(energy), unit*np.sqrt(2*energy/norm)))
    return result


def spectral_propagator(p, z, state, action, modes=None):
    modes = tree_modes(p, state, action) if modes is None else modes
    return sum((np.outer(unit, unit.conjugate())/(energy-z)
                +np.outer(unit.conjugate(), unit)/(energy+z))/(2*energy)
               for energy, unit in modes)


def static_completion(p, state, action, modes=None):
    modes = tree_modes(p, state, action) if modes is None else modes
    energy, unit = modes[0]
    jets = CURV.source_jets(state, action)
    vertex = jets["D_h"]
    pair = float(abs(unit@vertex@unit)**2/(4*energy**3))
    mixed = []
    for other_energy, other_unit in modes[1:]:
        normal = abs(np.vdot(unit, vertex@other_unit))**2
        anomalous = abs(unit@vertex@other_unit)**2
        mixed.append(float((anomalous/(energy+other_energy)
                            +normal/(other_energy-energy))/(2*energy*other_energy)))
    contact = float(np.vdot(unit, jets["D_hh"]@unit).real/(2*energy))
    return {"pair_per_n": pair, "mixed_per_n": mixed, "contact_per_n": contact,
            "nonpopulation_per_n": pair+sum(mixed)-contact}


def contact_matrix(p, state, action):
    acoustic = MOD.mode(p, state, action)
    energy, unit = acoustic["omega"], acoustic["polarization"]
    cubic, quartic = MOD.cubic_tensor(state, action), CURV.quartic_tensor(action)
    force = np.einsum("a,iab,b->i", unit.conjugate(), cubic, unit).real/(2*energy)
    shift = np.zeros(3)
    active = (0, 2)
    block = LAND.parent_mass_matrix(state, action)[np.ix_(active, active)]
    shift[list(active)] = -np.linalg.solve(block, force[list(active)])
    seagull = np.einsum("a,ijab,b->ij", unit.conjugate(), quartic, unit).real/(2*energy)
    return seagull+np.einsum("ijk,k->ij", cubic, shift), force, shift


def decimal_contact_projection(p, state, action):
    acoustic = MOD.mode(p, state, action)
    with localcontext() as context:
        context.prec = 50
        d = lambda x: Decimal(str(float(x)))
        zero = Decimal(0)
        u, g, eps, lam = [d(action[k]) for k in ("u", "gamma", "epsilon", "response_quartic")]
        s, v = d(state["s"]), d(state["V_curvature"])
        r, displacement = s.sqrt(), d(state["Phi"])-d(action["Phi_reference"])
        cubic, quartic = {}, {}
        for indices, value in (((0, 0, 0), 6*u*r), ((0, 1, 1), 2*u*r),
                               ((2, 0, 0), -g), ((2, 1, 1), -g), ((2, 2, 2), 6*eps*lam*displacement)):
            for index in set(permutations(indices)):
                cubic[index] = value
        for indices, value in (((0, 0, 0, 0), 6*u), ((1, 1, 1, 1), 6*u),
                               ((0, 0, 1, 1), 2*u), ((2, 2, 2, 2), 6*eps*lam)):
            for index in set(permutations(indices)):
                quartic[index] = value
        unit = acoustic["polarization"]
        covariance = [[d(unit[i].real)*d(unit[j].real)+d(unit[i].imag)*d(unit[j].imag)
                       for j in range(3)] for i in range(3)]
        energy = d(acoustic["omega"])
        force = [sum(cubic.get((i, a, b), zero)*covariance[a][b] for a in range(3) for b in range(3))/(2*energy) for i in range(3)]
        aa, ab, bb = 2*u*s, -g*r, v
        determinant = aa*bb-ab*ab
        first = [-ab/determinant, zero, aa/determinant]
        shift = [(-bb*force[0]+ab*force[2])/determinant, zero,
                 (ab*force[0]-aa*force[2])/determinant]
        result = zero
        for i in range(3):
            for j in range(3):
                seagull = sum(quartic.get((i, j, a, b), zero)*covariance[a][b] for a in range(3) for b in range(3))/(2*energy)
                background = sum(cubic.get((i, j, k), zero)*shift[k] for k in range(3))
                result += first[i]*(seagull+background)*first[j]
        return float(result)


def source_response(z, state, action, ensemble="dynamic"):
    if ensemble == "grand_canonical_static":
        if z != 0:
            raise ValueError("static ensemble requires zero frequency")
        return CURV.source_jets(state, action)["first"].astype(complex)
    if ensemble != "dynamic" or not np.isfinite(z) or z.imag == 0:
        raise ValueError("non-real complex frequency required for this response audit")
    return np.linalg.solve(kernel(0., z, state, action), [0., 0., 1.])


def insertion_bubble(p, z, state, action, spectral=False):
    if not np.isfinite(z) or z.imag == 0:
        raise ValueError("off-real-axis frequency required; no pole width assigned")
    acoustic = MOD.mode(p, state, action)
    energy, unit = acoustic["omega"], acoustic["polarization"]
    cubic = MOD.cubic_tensor(state, action)
    if spectral:
        modes = tree_modes(p, state, action)
        plus = spectral_propagator(p, energy+z, state, action, modes)
        minus = spectral_propagator(p, energy-z, state, action, modes)
    else:
        plus = np.linalg.inv(kernel(p, energy+z, state, action))
        minus = np.linalg.inv(kernel(p, energy-z, state, action))
    legs = cubic@unit
    first = legs.conjugate()@plus@legs.T
    second = (legs.conjugate()@minus@legs.T).T
    return (first+second)/(2*energy)


def covariance_bubble(p, z, state, action):
    kinetic, linear, potential = matrices(p, state, action)
    gyro = (1j*linear).real
    evolution = np.block([[np.zeros((3, 3)), np.eye(3)],
                          [-np.linalg.solve(kinetic, potential), -np.linalg.solve(kinetic, gyro)]])
    acoustic = MOD.mode(p, state, action)
    energy, unit = acoustic["omega"], acoustic["polarization"]
    phase_vector = np.concatenate([unit, -1j*energy*unit])
    covariance = np.outer(phase_vector, phase_vector.conjugate()).real/energy
    operator = -1j*z*np.eye(36)-np.kron(evolution, np.eye(6))-np.kron(np.eye(6), evolution)
    cubic, answer = MOD.cubic_tensor(state, action), np.zeros((3, 3), dtype=complex)
    for j in range(3):
        perturbation = np.zeros((6, 6))
        perturbation[3:, :3] = -np.linalg.solve(kinetic, cubic[j])
        drive = perturbation@covariance+covariance@perturbation.T
        response = np.linalg.solve(operator, drive.reshape(36)).reshape(6, 6)
        answer[:, j] = -.5*np.einsum("iab,ab->i", cubic, response[:3, :3])
    return answer


def dynamic_point(p, z, state, action, method="inverse"):
    if method not in ("inverse", "spectral", "covariance"):
        raise ValueError("named independent response method required")
    left, right = source_response(-z, state, action), source_response(z, state, action)
    bubble = covariance_bubble(p, z, state, action) if method == "covariance" else insertion_bubble(p, z, state, action, spectral=method == "spectral")
    contact = contact_matrix(p, state, action)[0]
    return complex(left@(bubble-contact)@right)


def thermal_completion(temperature, state, action, order=48, tail=40.):
    TH.validate(.02, temperature, state, action, order)
    if not isfinite(tail) or tail <= 16:
        raise ValueError("declared finite tail >16 required")
    names = ("pair", "mixed_lower", "mixed_upper", "contact", "population", "chi_completed", "static_target")
    result = dict.fromkeys(names, 0.)
    if temperature == 0:
        return result
    c = INT.dispersion_coefficients(state, action)["c"]
    for x, weight in TH.radial_nodes(order, tail):
        p = temperature*x/c
        modes = tree_modes(p, state, action)
        point = static_completion(p, state, action, modes)
        jets = CURV.energy_jets(p, state, action)
        n = TH.bose(jets["E"]/temperature)
        measure = weight*temperature/c*p*p/(2*pi*pi)
        for key, value in (("pair", point["pair_per_n"]), ("mixed_lower", point["mixed_per_n"][0]),
                           ("mixed_upper", point["mixed_per_n"][1]), ("contact", point["contact_per_n"])):
            result[key] += measure*n*value
        result["population"] += measure*n*(1+n)*jets["E_h"]**2/temperature
        result["static_target"] += measure*(n*(1+n)*jets["E_h"]**2/temperature-n*jets["E_hh"])
    result["chi_completed"] = result["population"]+result["pair"]+result["mixed_lower"]+result["mixed_upper"]-result["contact"]
    result["matching_error"] = INT.relative(result["chi_completed"], result["static_target"])
    return result


def dynamic_thermal(z, temperature, state, action, order=48, tail=40.):
    TH.validate(.02, temperature, state, action, order)
    source_response(z, state, action)
    if not isfinite(tail) or tail <= 16:
        raise ValueError("declared finite tail >16 required")
    if temperature == 0:
        return 0j
    c, result = INT.dispersion_coefficients(state, action)["c"], 0j
    for x, weight in TH.radial_nodes(order, tail):
        p = temperature*x/c
        n = TH.bose(TH.energy_value(p, state, action)/temperature)
        result += weight*temperature/c*p*p/(2*pi*pi)*n*dynamic_point(p, z, state, action)
    return complex(result)


def matrix_error(a, b):
    return float(np.linalg.norm(a-b)/max(np.linalg.norm(a), np.linalg.norm(b), 1e-30))


def encode_complex(value):
    return {"real": float(value.real), "imag": float(value.imag)}


def audit():
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        points = []
        for p in MOMENTA:
            modes, jets = tree_modes(p, state, action), CURV.energy_jets(p, state, action)
            static = static_completion(p, state, action, modes)
            contact, force, shift = contact_matrix(p, state, action)
            first = CURV.source_jets(state, action)["first"]
            frequency_checks = []
            for z in FREQUENCIES:
                inverse = np.linalg.inv(kernel(p, z, state, action))
                bubble = insertion_bubble(p, z, state, action)
                value = dynamic_point(p, z, state, action)
                source = source_response(z, state, action)
                frequency_checks.append({"z": encode_complex(z), "response_per_n": encode_complex(value),
                    "propagator_error": matrix_error(inverse, spectral_propagator(p, z, state, action, modes)),
                    "bubble_spectral_error": matrix_error(bubble, insertion_bubble(p, z, state, action, True)),
                    "bubble_covariance_error": matrix_error(bubble, covariance_bubble(p, z, state, action)),
                    "source_covariance_error": INT.relative(value, dynamic_point(p, z, state, action, "covariance")),
                    "reciprocity_error": matrix_error(bubble.T, insertion_bubble(p, -z, state, action)),
                    "source_charge_constraint_error": float(abs(2*mu*source[0]-1j*z*source[1])/max(abs(2*mu*source[0]), 1e-30)),
                    "response_reality_error": INT.relative(value.conjugate(), dynamic_point(p, -z.conjugate(), state, action))})
            points.append({"p": p, "tree_energies": [e for e, _ in modes], **static,
                "static_identity_error": INT.relative(static["nonpopulation_per_n"], -jets["E_hh"]),
                "contact_projection_error": INT.relative(decimal_contact_projection(p, state, action), static["contact_per_n"]),
                "raw_binary64_contact_projection_error": INT.relative(first@contact@first, static["contact_per_n"]),
                "background_shift_equation_error": float(np.linalg.norm((LAND.parent_mass_matrix(state, action)@shift+force)[[0, 2]])),
                "frequency_checks": frequency_checks})
        cf, rows = INT.dispersion_coefficients(state, action), []
        for divisor in TEMPERATURE_DIVISORS:
            temperature = cf["c"]*cf["dispersion_scale"]/divisor
            runs = [thermal_completion(temperature, state, action, order) for order in ORDERS]
            short = thermal_completion(temperature, state, action, ORDERS[-1], TAILS[0])
            dynamic = []
            for z in FREQUENCIES:
                values = [dynamic_thermal(z, temperature, state, action, order) for order in ORDERS]
                tail = dynamic_thermal(z, temperature, state, action, ORDERS[-1], TAILS[0])
                dynamic.append({"z": encode_complex(z), "delta_chi_q0": encode_complex(values[-1]),
                                "quadrature_error": INT.relative(values[-2], values[-1]), "tail_error": INT.relative(tail, values[-1])})
            rows.append({"T": temperature, "divisor": divisor, **runs[-1], "dynamic_q0": dynamic,
                         "quadrature_error": INT.relative(runs[-2]["chi_completed"], runs[-1]["chi_completed"]),
                         "tail_error": INT.relative(short["chi_completed"], runs[-1]["chi_completed"])})
        static_tree = CURV.source_jets(state, action)["first"][2]
        _, _, v0 = matrices(0., state, action)
        closed_charge_tree = 1/(v0[2, 2]-v0[0, 2]**2/(v0[0, 0]+4*mu*mu))
        small_z = source_response(1e-5j, state, action)[2].real
        examples.append({"mu": mu, "points": points, "thermal_rows": rows,
                         "static_fixed_mu_tree_chi": float(static_tree), "q0_fixed_charge_tree_chi": float(closed_charge_tree),
                         "fixed_charge_limit_error": INT.relative(small_z, closed_charge_tree),
                         "noncommuting_tree_limit_fraction": INT.relative(static_tree, closed_charge_tree)})
    checks = {
        "virtual_tree_and_contact_close_static_pressure_target": all(p["static_identity_error"] < GATES["identity_relative"] and p["contact_projection_error"] < GATES["identity_relative"] for e in examples for p in e["points"]),
        "full_tree_inverse_has_independent_modal_decomposition": all(f["propagator_error"] < GATES["identity_relative"] and f["bubble_spectral_error"] < GATES["identity_relative"] for e in examples for p in e["points"] for f in p["frequency_checks"]),
        "real_time_covariance_independently_checks_dynamic_bubble_and_source": all(max(f["bubble_covariance_error"], f["source_covariance_error"]) < GATES["covariance_relative"] for e in examples for p in e["points"] for f in p["frequency_checks"]),
        "frequency_reciprocity_and_derived_background_shift": all(p["background_shift_equation_error"] < GATES["identity_relative"] and all(f["reciprocity_error"] < GATES["identity_relative"] for f in p["frequency_checks"]) for e in examples for p in e["points"]),
        "source_charge_constraint_and_response_reality": all(max(f["source_charge_constraint_error"], f["response_reality_error"]) < GATES["identity_relative"] for e in examples for p in e["points"] for f in p["frequency_checks"]),
        "integrated_static_and_dynamic_quadrature_and_tail": all(r["matching_error"] < GATES["identity_relative"] and r["quadrature_error"] < GATES["quadrature_relative"] and r["tail_error"] < GATES["thermal_tail_relative"] and all(d["quadrature_error"] < GATES["quadrature_relative"] and d["tail_error"] < GATES["thermal_tail_relative"] for d in r["dynamic_q0"]) for e in examples for r in e["thermal_rows"]),
        "static_and_q0_dynamic_ensembles_are_not_silently_identified": all(e["fixed_charge_limit_error"] < GATES["identity_relative"] and e["noncommuting_tree_limit_fraction"] > .01 for e in examples)}
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_thermal_virtual_response.py"]
    protected = [PREFIX+"Result/artifacts/t13_thermal_source_curvature.json", PREFIX+"Code/03_Research/Research_T13_Thermal_Source_Curvature.py", PREFIX+"Result/artifacts/t13_acoustic_source_Landau.json", PREFIX+"Result/artifacts/t13_thermal_virtual_response_first_failure.json"]+list(EFT.ACTION_PATHS)
    closed = all(checks.values())
    record = {"major_result_id": "T13_THERMAL_VIRTUAL_SOURCE_STATIC_COMPLETION_AND_DYNAMIC_COVARIANCE", "topic": "0.13_Thermodynamic_Bridge", "branch_id": BRANCH, "parent_branch_id": EFT.BRANCH,
        "created_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if closed else "PARTIAL",
        "verification_status": "PASS_SCOPED_THERMAL_VIRTUAL_RESPONSE" if closed else "FAIL_SCOPED_THERMAL_VIRTUAL_RESPONSE",
        "what_is_closed": "Derived mixed virtual tree propagation/contact completes the acoustic thermal static susceptibility; non-real q0 dynamic source correction independently agrees with real-time covariance evolution",
        "equation_or_mapping": "chi_static=population+pair+mixed_virtual-contact; delta_chi(z,0)=d(-z)^T [B_acoustic_insertion(z)-S-T delta_x] d(z)",
        "units": {"h": "E^3", "Phi": "E", "P": "E^4", "chi": "E^-2", "B_and_contact": "E^2 after d^3p integration", "d": "E^-2"},
        "derivation_class": "ONE_ACOUSTIC_THERMAL_COVARIANCE_INSERTION_WITH_VIRTUAL_CLASSICAL_TREE_PROPAGATION", "observable": "conditional action-source susceptibility, not calibrated heat response", "data_role": "DERIVED_NOT_CALIBRATION",
        "action_controls": action, "checks": checks, "examples": examples,
        "state_variables": ["radial_fluctuation", "phase_fluctuation", "Phi_fluctuation", "their_time_derivatives_for_covariance_only"],
        "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs"],
        "equation_registry_ids": [r["id"] for r in json.loads((ROOT/REGISTRY).read_text())["entries"]],
        "declared_grids": {"mu": MU_GRID, "momenta": MOMENTA, "T_divisors": TEMPERATURE_DIVISORS, "orders": ORDERS, "tails": TAILS, "frequencies": [encode_complex(z) for z in FREQUENCIES], "locked_before_first_audit": True}, "thresholds": GATES,
        "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
        "prescription": {"thermal_population": "acoustic only", "heavy_modes": "virtual classical tree propagation; zero assigned thermal occupations", "vacuum": "not included", "dynamic_population_relaxation": "not included", "static_population": "grand canonical equilibrium variance, not a q0 dynamical term", "new_named_extension": True},
        "controlling_blocker": "finite_q_source_transport_and_complete_interacting_thermal_matching_open",
        "open_blockers": ["finite_q_source_response_and_population_relaxation", "vacuum_and_full_interacting_thermal_sunset_matching", "independent_material_readout_scale_KMS_Kubo_and_uncertainty"],
        "dependency_unlocked": ["finite_q_source_and_population_relaxation_research_only"],
        "static_virtual_contact_matching_closed_for_prescription": closed, "q0_complex_dynamic_covariance_checked": closed,
        "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False, "dynamic_contact_fixed_from_static_residual": False,
        "all_parent_modes_and_quantum_Phi_loops_included": False, "full_two_loop_pressure_computed": False, "full_SK_KMS_matching_closed": False,
        "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False, "controlled_full_action_truncation_error_established": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False, "claim_promotion": False, "parameter_fitting": False, "assigned_width": False,
        "clipping": False, "cone_padding": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
        "primary_references": ["https://arxiv.org/abs/cond-mat/0305138"],
        "claim_boundary": "Named acoustic-thermal-insertion Gaussian extension, finite rest-domain grids and non-real q0 frequency samples. Not heavy quantum/vacuum loops, equilibrated dynamic transport, global retarded stability, physical calibration, original conserved-C repair or Full Topic13/Core/UET closure."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived virtual/contact completion and independent time-domain covariance check", record["equation_or_mapping"], checks, record["controlling_blocker"], "Finite-q source and population-relaxation matching, then interacting thermal and physical input", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
