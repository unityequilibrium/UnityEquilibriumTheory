"""Same-parent thermal source curvature and an acoustic static matching target.

Only the tree acoustic thermal determinant is differentiated. A residual
against acoustic cuts is a matching obligation, not a fitted contact term.
"""

from datetime import datetime, timezone
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
import Research_T13_Acoustic_Source_Landau as LAND

PAIR, MOD, TH, EFT, INT, PREFIX = LAND.PAIR, LAND.MOD, LAND.TH, LAND.EFT, LAND.INT, LAND.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_thermal_source_curvature_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_thermal_source_curvature.json")
MU_GRID, TEMPERATURE_DIVISORS = (1.05, 1.2), (256, 512)
ORDERS, TAILS, SOURCE_STEPS = (24, 48, 96), (32., 40.), (1e-4, 5e-5, 2.5e-5)
MOMENTA = (.005, .02, .04)
GATES = {"identity_relative": 1e-9, "source_FD_relative": 1e-4,
         "quadrature_relative": 1e-6, "thermal_tail_relative": 1e-8,
         "original_causal_leakage": 1e-6}


def quartic_tensor(action):
    tensor = np.zeros((3, 3, 3, 3))
    tensor[0, 0, 0, 0] = tensor[1, 1, 1, 1] = 6*action["u"]
    tensor[2, 2, 2, 2] = 6*action["epsilon"]*action["response_quartic"]
    for indices in set(permutations((0, 0, 1, 1))):
        tensor[indices] = 2*action["u"]
    return tensor


def source_jets(state, action):
    EFT.validate(action)
    if state["xi"] != 0:
        raise ValueError("rest stationary source path required")
    active = (0, 2)
    v0 = LAND.parent_mass_matrix(state, action)
    block = v0[np.ix_(active, active)]
    if np.linalg.eigvalsh(block)[0] <= 0:
        raise ValueError("positive static radial/response Hessian required")
    first = np.zeros(3)
    first[list(active)] = np.linalg.solve(block, [0., 1.])
    cubic = MOD.cubic_tensor(state, action)
    curvature = np.einsum("ijk,j,k->i", cubic, first, first)
    second = np.zeros(3)
    second[list(active)] = -np.linalg.solve(block, curvature[list(active)])
    dh = np.einsum("ijk,k->ij", cubic, first)
    dhh = np.einsum("ijkl,k,l->ij", quartic_tensor(action), first, first)+np.einsum("ijk,k->ij", cubic, second)
    ward = max(abs(dh[1, 1]), abs(dhh[1, 1]))
    # Along the stationary path u*r^2=X-m^2+gamma*Phi: both phase-mass
    # derivatives vanish identically. Eliminate that algebraic cancellation.
    dh[1, 1] = dhh[1, 1] = 0.
    return {"first": first, "second": second, "D_h": dh, "D_hh": dhh,
            "stationary_Ward_cancellation": ward}


def energy_jets(p, state, action):
    TH.validate(p, 0., state, action, 2)
    jets = source_jets(state, action)
    mode = MOD.mode(p, state, action)
    energy, unit = mode["omega"], mode["polarization"]
    kinetic = np.diag([1., 1., action["epsilon"]*action["response_kinetic"]])
    linear = np.array([[0., 2j*state["mu"], 0.], [-2j*state["mu"], 0., 0.], [0., 0., 0.]])
    de = -2*energy*kinetic+linear
    denominator = float(-np.vdot(unit, de@unit).real)
    first = float(np.vdot(unit, jets["D_h"]@unit).real/denominator)
    total = jets["D_h"]+first*de
    kernel = MOD.kernel(p, energy, state, action)
    values, vectors = np.linalg.eigh(kernel)
    null = int(np.argmin(abs(values)))
    other = [i for i in range(3) if i != null]
    if min(abs(values[other])) < 1e-8 or abs(values[null])/max(abs(values)) > 1e-9:
        raise ValueError("isolated acoustic kernel nullspace required")
    inverse = (vectors[:, other]/values[other])@vectors[:, other].conjugate().T
    unit_h = -inverse@total@unit
    seagull = float(np.vdot(unit, jets["D_hh"]@unit).real/denominator)
    kinematic = float(-2*first*first*np.vdot(unit, kinetic@unit).real/denominator)
    virtual = float(2*np.vdot(unit, total@unit_h).real/denominator)
    second = seagull+kinematic+virtual
    raw_landau = float(np.vdot(jets["first"], LAND.landau_vector(p, p, state, action)).real)
    raw_pair = np.vdot(jets["first"], PAIR.pair_vector(p, p, state, action))
    # Contract after exact stationary phase-mass cancellation, rather than
    # subtract O(1) source components to recover their O(p^2) sum.
    landau_vertex = float(np.vdot(unit, jets["D_h"]@unit).real)
    pair_vertex = unit@jets["D_h"]@unit
    return {"E": energy, "E_h": first, "E_hh": second,
            "E_hh_seagull_background": seagull, "E_hh_kinematic": kinematic,
            "E_hh_virtual_polarization": virtual,
            "Landau_vertex": landau_vertex, "pair_vertex_squared": float(abs(pair_vertex)**2),
            "raw_source_contraction_error": max(INT.relative(raw_landau, landau_vertex), INT.relative(raw_pair, pair_vertex)),
            "vertex_derivative_error": INT.relative(landau_vertex, 2*energy*first),
            "mode_norm_error": INT.relative(denominator, 2*energy),
            "kernel_derivative_residual": float(np.linalg.norm(kernel@unit_h+total@unit)/max(np.linalg.norm(total@unit), 1e-30))}


def thermal_response(temperature, state, action, order=48, tail=40.):
    TH.validate(.02, temperature, state, action, order)
    if not isfinite(tail) or tail <= 16:
        raise ValueError("finite declared thermal tail >16 required")
    if temperature == 0:
        return {name: 0. for name in ("pressure", "thermal_Phi", "chi_population", "chi_energy_curvature", "chi_thermal", "chi_pair_static", "required_additional_static_matching", "chi_seagull_background", "chi_kinematic", "chi_virtual_polarization")}
    c = INT.dispersion_coefficients(state, action)["c"]
    result = {name: 0. for name in ("pressure", "thermal_Phi", "chi_population", "chi_energy_curvature", "chi_pair_static", "chi_seagull_background", "chi_kinematic", "chi_virtual_polarization")}
    errors, raw_errors = [], []
    for x, weight in TH.radial_nodes(order, tail):
        p = temperature*x/c
        jets = energy_jets(p, state, action)
        energy, first, second = jets["E"], jets["E_h"], jets["E_hh"]
        occupation = TH.bose(energy/temperature)
        measure = weight*temperature/c*p*p/(2*pi*pi)
        result["pressure"] -= measure*temperature*np.log(-np.expm1(-energy/temperature))
        result["thermal_Phi"] -= measure*occupation*first
        result["chi_population"] += measure*occupation*(1+occupation)/temperature*first*first
        result["chi_energy_curvature"] -= measure*occupation*second
        result["chi_seagull_background"] -= measure*occupation*jets["E_hh_seagull_background"]
        result["chi_kinematic"] -= measure*occupation*jets["E_hh_kinematic"]
        result["chi_virtual_polarization"] -= measure*occupation*jets["E_hh_virtual_polarization"]
        result["chi_pair_static"] += measure*occupation*jets["pair_vertex_squared"]/(4*energy**3)
        errors.append(max(jets["vertex_derivative_error"], jets["mode_norm_error"], jets["kernel_derivative_residual"]))
        raw_errors.append(jets["raw_source_contraction_error"])
    result["chi_thermal"] = result["chi_population"]+result["chi_energy_curvature"]
    result["required_additional_static_matching"] = result["chi_pair_static"]-result["chi_energy_curvature"]
    result["missing_curvature_fraction"] = abs(result["chi_energy_curvature"])/max(abs(result["chi_thermal"]), 1e-30)
    result["acoustic_cut_only_relative_mismatch"] = abs(result["required_additional_static_matching"])/max(abs(result["chi_thermal"]), 1e-30)
    result["pointwise_identity_error"] = max(errors)
    result["curvature_decomposition_error"] = INT.relative(sum(result[name] for name in ("chi_seagull_background", "chi_kinematic", "chi_virtual_polarization")), result["chi_energy_curvature"])
    result["raw_source_contraction_error"] = max(raw_errors)
    result["p_max"] = tail*temperature/c
    return result


def pressure_at_source(h, temperature, reference, action, order=96, tail=40.):
    other = EFT.tree_state(reference["mu"], h=h, action=action)
    c0 = INT.dispersion_coefficients(reference, action)["c"]
    value = 0.
    # A common fixed p-domain is mandatory when differentiating h.
    for x, weight in TH.radial_nodes(order, tail):
        p = temperature*x/c0
        energy = TH.energy_value(p, other, action)
        value -= weight*temperature/c0*p*p/(2*pi*pi)*temperature*np.log(-np.expm1(-energy/temperature))
    return float(value)


def audit():
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf = INT.dispersion_coefficients(state, action)
        points = []
        for p in MOMENTA:
            point = energy_jets(p, state, action)
            differences = []
            for step in SOURCE_STEPS:
                minus, plus = [TH.energy_value(p, EFT.tree_state(mu, h=h, action=action), action) for h in (-step, step)]
                differences.append({"step": step, "first_error": INT.relative((plus-minus)/(2*step), point["E_h"]),
                                    "second_error": INT.relative((plus-2*point["E"]+minus)/step**2, point["E_hh"])})
            points.append({"p": p, **point, "source_FD": differences})
        rows = []
        for divisor in TEMPERATURE_DIVISORS:
            temperature = cf["c"]*cf["dispersion_scale"]/divisor
            runs = [thermal_response(temperature, state, action, order) for order in ORDERS]
            result = runs[-1]
            short = thermal_response(temperature, state, action, ORDERS[-1], TAILS[0])
            differences = []
            for step in SOURCE_STEPS:
                minus, zero, plus = [pressure_at_source(h, temperature, state, action) for h in (-step, 0., step)]
                differences.append({"step": step, "first_error": INT.relative((plus-minus)/(2*step), result["thermal_Phi"]),
                                    "second_error": INT.relative((plus-2*zero+minus)/step**2, result["chi_thermal"])})
            rows.append({"T": temperature, "temperature_divisor": divisor, **result, "pressure_FD": differences,
                         "quadrature_error": INT.relative(runs[-2]["chi_thermal"], result["chi_thermal"]),
                         "tail_error": INT.relative(short["chi_thermal"], result["chi_thermal"]),
                         "static_matching_residual_is_not_fitted_contact": True})
        examples.append({"mu": mu, "source_Ward_cancellation": source_jets(state, action)["stationary_Ward_cancellation"],
                         "energy_derivative_points": points, "thermal_rows": rows})
    checks = {
        "stationary_source_and_Landau_vertex_identity": all(e["source_Ward_cancellation"] < GATES["identity_relative"] and all(max(p["vertex_derivative_error"], p["mode_norm_error"], p["kernel_derivative_residual"]) < GATES["identity_relative"] for p in e["energy_derivative_points"]) for e in examples),
        "energy_source_derivatives_independent_FD": all(max(p["source_FD"][0]["first_error"], p["source_FD"][0]["second_error"]) < GATES["source_FD_relative"] for e in examples for p in e["energy_derivative_points"]),
        "thermal_pressure_derivatives_independent_FD": all(max(r["pressure_FD"][0]["first_error"], r["pressure_FD"][0]["second_error"]) < GATES["source_FD_relative"] for e in examples for r in e["thermal_rows"]),
        "thermal_quadrature_tail_and_pointwise_identities": all(r["quadrature_error"] < GATES["quadrature_relative"] and r["tail_error"] < GATES["thermal_tail_relative"] and r["pointwise_identity_error"] < GATES["identity_relative"] for e in examples for r in e["thermal_rows"]),
        "source_curvature_resolves_seagull_kinematic_virtual_terms": all(r["curvature_decomposition_error"] < GATES["identity_relative"] for e in examples for r in e["thermal_rows"]),
        "population_and_acoustic_pair_are_not_total_static_response": all(r["chi_population"] > 0 and r["chi_pair_static"] > 0 and r["missing_curvature_fraction"] > .01 and r["acoustic_cut_only_relative_mismatch"] > .01 for e in examples for r in e["thermal_rows"])}
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_thermal_source_curvature.py"]
    protected = [PREFIX+"Result/artifacts/t13_acoustic_source_Landau.json", PREFIX+"Result/artifacts/t13_acoustic_source_pair.json", PREFIX+"Code/03_Research/Research_T13_Acoustic_Source_Landau.py", PREFIX+"Result/artifacts/t13_thermal_source_curvature_first_failure.json"]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_THERMAL_STATIC_SOURCE_CURVATURE_MATCHING_TARGET", "topic": "0.13_Thermodynamic_Bridge",
              "branch_id": EFT.BRANCH, "created_at": datetime.now(timezone.utc).isoformat(),
              "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
              "verification_status": "PASS_SCOPED_THERMAL_SOURCE_CURVATURE" if all(checks.values()) else "FAIL_SCOPED_THERMAL_SOURCE_CURVATURE",
              "what_is_closed": "Source energy derivatives and thermal acoustic determinant Hessian, with an independently checked static matching obligation beyond acoustic cuts",
              "equation_or_mapping": "chi_th=integral [n(1+n) E_h^2/T - n E_hh]; V_L source=2E E_h; required static supplement=chi_pair-chi_energy_curvature",
              "units": {"h": "E^3", "Phi": "E", "P": "E^4", "E_h": "E^-2", "E_hh": "E^-5", "chi": "E^-2"},
              "derivation_class": "SAME_TREE_ACTION_SOURCE_EIGENVALUE_VARIATION_AND_ONE_ACOUSTIC_THERMAL_DETERMINANT",
              "observable": "Conditional equilibrium h susceptibility and static source matching target, not material heat/calibration",
              "data_role": "DERIVED_NOT_CALIBRATION", "action_controls": action, "checks": checks, "examples": examples,
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "declared_grids": {"mu": MU_GRID, "T_divisors": TEMPERATURE_DIVISORS, "momenta": MOMENTA, "orders": ORDERS, "tails": TAILS, "source_steps": SOURCE_STEPS, "locked_before_first_audit": True},
              "thresholds": GATES, "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "controlling_blocker": "dynamic_source_contact_virtual_mode_and_full_thermal_matching_open",
              "open_blockers": ["derive_dynamic_contact_virtual_mode_real_matching_not_assign_static_residual", "complete_thermal_sunset_and_all_mode_quantum_admission", "independent_material_readout_scale_transport_and_uncertainty"],
              "dependency_unlocked": ["source_contact_and_virtual_mode_matching_research_only"],
              "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False,
              "dynamic_contact_fixed_from_static_residual": False, "full_two_loop_pressure_computed": False,
              "all_parent_modes_and_quantum_Phi_loops_included": False, "full_SK_KMS_matching_closed": False,
              "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False,
              "controlled_full_action_truncation_error_established": False, "full_core_unlock": False,
              "core_composition_gate_overwritten": False, "claim_promotion": False, "parameter_fitting": False,
              "assigned_width": False, "clipping": False, "cone_padding": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "primary_references": ["https://arxiv.org/abs/cond-mat/0305138"],
              "claim_boundary": "One tree acoustic thermal determinant/source curvature on stated rest-domain and finite p grid. Virtual tree eigenvector variation is not a new quantum-heavy prescription; static target is not assigned dynamic contact, full response/EOS/transport/material calibration or UET/Core closure."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived source energy curvature and independently checked pressure Hessian", record["equation_or_mapping"], checks, record["controlling_blocker"], "Derive actual dynamic contact/virtual-mode matching and complete thermal consistency", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
