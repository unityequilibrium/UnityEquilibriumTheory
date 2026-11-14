"""Charge and first-order energy balance for the named thermal insertion.

Pair-local contact uses the average of both stationary covariances. Its
continuum interpretation requires translation of the full momentum domain;
it is not a collision operator or a finite-cutoff transport prescription.
"""

from datetime import datetime, timezone
import json
from math import isfinite, sqrt
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Finite_Q_Thermal_Source as FQ

VIRT, EFT, TH, INT, MOD, CURV, PREFIX = FQ.VIRT, FQ.EFT, FQ.TH, FQ.INT, FQ.MOD, FQ.CURV, FQ.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_thermal_noether_response_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_thermal_noether_response.json")
MU_GRID = (1.05, 1.2)
MOMENTUM_TRIPLES = ((.005, .011, .008), (.02, .031, .02), (.04, .037, .02), (.02, .02, 0.))
TEMPERATURES = (.002, .004)
FREQUENCIES = (.02j, .05j, .03+.02j)
GATES = {"ward_relative": 1e-9, "method_relative": 1e-7, "negative_control_minimum": 1e-3,
         "original_causal_leakage": 1e-6}


def geometry(p, r, q):
    if not all(isfinite(x) for x in (p, r, q)) or min(p, r) <= 0 or q < 0:
        raise ValueError("finite positive internal momenta and nonnegative q required")
    if q == 0:
        if p != r:
            raise ValueError("q0 requires identical momenta")
        return 0., 0., p*p
    if q < abs(p-r) or q > p+r:
        raise ValueError("physical momentum triangle required")
    pz = (r*r-p*p-q*q)/(2*q)
    return pz, pz+q, (p*p+r*r-q*q)/2


def covariance_response(p, r, z, temperature, drive, state, action):
    FQ.validate(p, r, temperature, state, action)
    if not np.isfinite(z) or z.imag == 0 or np.shape(drive) != (3,) or not np.all(np.isfinite(drive)):
        raise ValueError("non-real frequency and finite three-component drive required")
    ap, cp = FQ.evolution_and_covariance(p, temperature, state, action)
    ar, cr = FQ.evolution_and_covariance(r, temperature, state, action)
    kinetic = VIRT.matrices(0., state, action)[0]
    vertex = np.einsum("ijk,k->ij", MOD.cubic_tensor(state, action), drive)
    delta_a = np.zeros((6, 6), dtype=complex)
    delta_a[3:, :3] = -np.linalg.solve(kinetic, vertex)
    rhs = delta_a@cp+cr@delta_a.T
    operator = -1j*z*np.eye(36)-np.kron(ar, np.eye(6))-np.kron(np.eye(6), ap)
    response = np.linalg.solve(operator, rhs.reshape(36)).reshape(6, 6)
    return response, (cp+cr)/2, rhs


def pair_contact(covariance, state, action):
    cubic, quartic = MOD.cubic_tensor(state, action), CURV.quartic_tensor(action)
    force = .5*np.einsum("iab,ab->i", cubic, covariance[:3, :3])
    seagull = .5*np.einsum("ijab,ab->ij", quartic, covariance[:3, :3])
    shift = np.zeros(3)
    active = (0, 2)
    v0 = VIRT.matrices(0., state, action)[2]
    shift[list(active)] = -np.linalg.solve(v0[np.ix_(active, active)], force[list(active)])
    return seagull+np.einsum("ijk,k->ij", cubic, shift), force, shift, seagull


def moments(response, p, r, q, state, action):
    pz, rz, product = geometry(p, r, q)
    kinetic, _, v0 = VIRT.matrices(0., state, action)
    xx, xv, vx, vv = response[:3, :3], response[:3, 3:], response[3:, :3], response[3:, 3:]
    density = state["mu"]*(xx[0, 0]+xx[1, 1])+.5*(xv[0, 1]+vx[1, 0]-xv[1, 0]-vx[0, 1])
    current = .5j*(pz+rz)*(xx[0, 1]-xx[1, 0])
    rotating_energy = .5*np.sum((v0+product*kinetic)*xx)+.5*np.sum(kinetic*vv)
    rotating_flux = .5j*(pz*np.sum(kinetic*vx)-rz*np.sum(kinetic*xv))
    return {"density": complex(density), "current": complex(current),
            "rotating_energy": complex(rotating_energy), "rotating_flux": complex(rotating_flux),
            "energy_term_scale": float(.5*np.sum(abs((v0+product*kinetic)*xx))+.5*np.sum(abs(kinetic*vv))),
            "flux_term_scale": float(.5*(abs(pz)*np.sum(abs(kinetic*vx))+abs(rz)*np.sum(abs(kinetic*xv))))}


def normalized_residual(value, terms):
    scale = sum(abs(term) for term in terms)
    return float(abs(value)/scale) if scale else float(abs(value))


def source_balance(p, r, q, z, temperature, state, action):
    geometry(p, r, q)
    if state["h"] != 0:
        raise ValueError("first-order source-work boundary requires stationary h0=0")
    drive = FQ.source_response(q, z, state, action)
    response, covariance, rhs = covariance_response(p, r, z, temperature, drive, state, action)
    values = moments(response, p, r, q, state, action)
    contact, force, shift, seagull = pair_contact(covariance, state, action)
    delta_force = .5*np.einsum("iab,ab->i", MOD.cubic_tensor(state, action), response[:3, :3])
    kernel = VIRT.kernel(q, z, state, action)
    correction = np.linalg.solve(kernel, -delta_force-contact@drive)
    v, mu = sqrt(state["s"]), state["mu"]
    mean_density = v*(2*mu*correction[0]-1j*z*correction[1])+shift[0]*(2*mu*drive[0]-1j*z*drive[1])
    mean_current = -1j*q*(v*correction[1]+shift[0]*drive[1])
    total_density, total_current = values["density"]+mean_density, values["current"]+mean_current
    fluctuation_divergence = -1j*z*values["density"]+1j*q*values["current"]
    phase_torque = v*(delta_force[1]+contact[1]@drive)
    total_divergence = -1j*z*total_density+1j*q*total_current
    energy_divergence = -1j*z*values["rotating_energy"]+1j*q*values["rotating_flux"]
    physical_energy = values["rotating_energy"]+mu*total_density
    physical_flux = values["rotating_flux"]+mu*total_current
    physical_divergence = -1j*z*physical_energy+1j*q*physical_flux
    independent_force = -FQ.paired_bubble(p, r, z, temperature, state, action)@drive
    if temperature:
        f_per_p = VIRT.contact_matrix(p, state, action)[0]*TH.bose(TH.energy_value(p, state, action)/temperature)
        f_per_r = VIRT.contact_matrix(r, state, action)[0]*TH.bose(TH.energy_value(r, state, action)/temperature)
        reference_contact = (f_per_p+f_per_r)/2
    else:
        reference_contact = np.zeros((3, 3))
    # Removing the tadpole background shift is a genuinely different response.
    wrong_correction = np.linalg.solve(kernel, -delta_force-seagull@drive)
    wrong_density = values["density"]+v*(2*mu*wrong_correction[0]-1j*z*wrong_correction[1])
    wrong_current = values["current"]-1j*q*v*wrong_correction[1]
    raw_terms = [-1j*z*values["density"], 1j*q*values["current"], -1j*z*mean_density, 1j*q*mean_current]
    explicit_contact = complex(force@drive)
    mean_contact = complex((VIRT.matrices(0., state, action)[2]@shift)@drive)
    return {"values": values, "total_density": total_density, "total_current": total_current,
            "physical_energy": physical_energy, "physical_flux": physical_flux,
            "fluctuation_ward_error": normalized_residual(fluctuation_divergence-phase_torque, [fluctuation_divergence, phase_torque]),
            "total_charge_ward_error": normalized_residual(total_divergence, raw_terms),
            "rotating_energy_ward_error": normalized_residual(energy_divergence, [abs(z)*values["energy_term_scale"], abs(q)*values["flux_term_scale"]]),
            "physical_energy_ward_error": normalized_residual(physical_divergence, [-1j*z*values["rotating_energy"], 1j*q*values["rotating_flux"]]+[mu*t for t in raw_terms]),
            "source_force_method_error": VIRT.matrix_error(delta_force[:, None], independent_force[:, None]),
            "contact_method_error": VIRT.matrix_error(contact, reference_contact),
            "phase_contact_identity_error": normalized_residual(v*contact[1, 1]-v*seagull[1, 1]+force[0], [v*seagull[1, 1], force[0]]),
            "omitted_background_shift_ward_error": normalized_residual(-1j*z*wrong_density+1j*q*wrong_current, raw_terms),
            "covariance_stationary_energy_drive": complex(np.sum(VIRT.matrices(0., state, action)[0]*rhs[3:, 3:])/2),
            "explicit_energy_contact": explicit_contact, "mean_energy_contact": mean_contact,
            "energy_contact_cancellation_error": normalized_residual(explicit_contact+mean_contact, [explicit_contact, mean_contact])}


def audit():
    action, rows = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        for temperature in TEMPERATURES:
            for p, r, q in MOMENTUM_TRIPLES:
                for z in FREQUENCIES:
                    result = source_balance(p, r, q, z, temperature, state, action)
                    encoded = {key: ({k: VIRT.encode_complex(v) for k, v in value.items()} if isinstance(value, dict)
                                     else VIRT.encode_complex(value) if isinstance(value, complex) else value)
                               for key, value in result.items()}
                    rows.append({"mu": mu, "T": temperature, "p": p, "r": r, "q": q, "z": VIRT.encode_complex(z), **encoded})
    errors = ("fluctuation_ward_error", "total_charge_ward_error", "rotating_energy_ward_error", "physical_energy_ward_error", "phase_contact_identity_error", "energy_contact_cancellation_error")
    checks = {key: all(row[key] < GATES["ward_relative"] for row in rows) for key in errors}
    checks["independent_source_force_and_contact"] = all(max(row["source_force_method_error"], row["contact_method_error"]) < GATES["method_relative"] for row in rows)
    checks["missing_background_contact_is_detected"] = max(row["omitted_background_shift_ward_error"] for row in rows) > GATES["negative_control_minimum"]
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_thermal_noether_response.py"]
    protected = [PREFIX+"Result/artifacts/t13_finite_q_thermal_source.json", PREFIX+"Code/03_Research/Research_T13_Finite_Q_Thermal_Source.py", PREFIX+"Result/artifacts/t13_thermal_virtual_response.json"]+list(EFT.ACTION_PATHS)
    passed = all(checks.values())
    record = {"major_result_id": "T13_GAUSSIAN_THERMAL_SOURCE_NOETHER_BALANCE", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
        "created_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "verification_status": "PASS_SCOPED_GAUSSIAN_NOETHER_RESPONSE" if passed else "FAIL_SCOPED_GAUSSIAN_NOETHER_RESPONSE",
        "what_is_closed": "Pair-local Gaussian source charge and first-order rotating/physical energy balance, conditional on recorded checks and momentum translation for continuum integration",
        "equation_or_mapping": "-iz delta_n+iq delta_j=0 after covariance, seagull, stationary shift and mean correction; delta_E=delta_Hrot+mu delta_n",
        "units": {"h": "E^3", "integrated_density_current_per_h": "E^0", "integrated_energy_flux_per_h": "E", "Phi": "E"},
        "derivation_class": "DERIVED_NOETHER_MOMENTS_OF_NAMED_ONE_THERMAL_INSERTION", "observable": "conditional natural-energy charge/energy source response, not calibrated heat flux", "data_role": "DERIVED_NOT_CALIBRATION",
        "action_controls": action, "checks": checks, "examples": rows,
        "declared_grids": {"mu": MU_GRID, "T": TEMPERATURES, "momentum_triples": MOMENTUM_TRIPLES, "frequencies": [VIRT.encode_complex(z) for z in FREQUENCIES], "locked_before_first_audit": True}, "thresholds": GATES,
        "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
        "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
        "controlling_blocker": "collisionless_soft_limit_full_interacting_energy_and_physical_transport_open",
        "open_blockers": ["collisionless_soft_frequency_and_collision_operator", "full_interacting_vacuum_thermal_matching_and_truncation_control", "second_order_source_work_entropy_and_dissipative_balance", "independent_material_source_readout_scale_and_uncertainty"],
        "dependency_unlocked": ["collisionless_limit_and_physical_heat_source_mapping_research_only"] if passed else [],
        "gaussian_pair_local_charge_Ward_closed": passed, "first_order_Gaussian_energy_balance_closed": passed,
        "full_loop_source_current_Ward_closed": False, "full_energy_exchange_ledger_closed": False,
        "full_collision_operator_computed": False, "physical_Kubo_emitted": False, "full_SK_KMS_matching_closed": False,
        "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False, "full_two_loop_pressure_computed": False,
        "all_parent_modes_and_quantum_Phi_loops_included": False, "independent_alpha_Phi_K_admitted": False,
        "controlled_full_action_truncation_error_established": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "state_variables": ["classical_tree_radial_phase_Phi_fluctuations_and_covariance_velocities"], "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs"],
        "claim_promotion": False, "parameter_fitting": False, "assigned_width": False, "assigned_relaxation_time": False,
        "clipping": False, "cone_padding": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
        "primary_references": ["https://journals.aps.org/pr/abstract/10.1103/PhysRev.124.287", "https://arxiv.org/abs/cond-mat/0307246"],
        "claim_boundary": "Pair-local rest-domain Gaussian first-order Noether identities with full-domain translation assumption only. Not full collision/transport/KMS/entropy or second-order heating/physical material/calibration; no original conserved-C repair or Full Topic13/Core/global closure."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived Noether covariance and stationary mean/contact response", record["equation_or_mapping"], checks, record["controlling_blocker"], "Collisionless limits, interacting matching and actual heat-source/readout without assigned rates", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
