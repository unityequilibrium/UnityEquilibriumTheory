"""Collisionless soft phase response of the unchanged fixed-Phi candidate.

The ray z=v*q, q->0 is not the thermodynamic z=0 derivative. No width,
collision input or SI/material calibration is introduced by taking this limit.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREVIOUS_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Real_Axis.py"
PREVIOUS_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_real_axis.json"
R = runpy.run_path(str(ROOT/PREVIOUS_CODE))
G, F, H = R["G"], R["F"], R["H"]
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_soft_collective.json")
RAYS = (.1, .3, .6, 1.2)
Q_GRID = (.04, .02, .01)
SOFT_ORDERS = (64, 96, 128)
LOOP_TOLERANCE = R["QUADRATURE_TOLERANCE"]
WARD_TOLERANCE = R["WARD_TOLERANCE"]


def angular_moments(velocity, group_velocity):
    """A_n = (1/2) int_-1^1 c^n w*c/(v-w*c+i0) dc, n=0,1,2."""
    v = complex(velocity)
    w = np.atleast_1d(np.asarray(group_velocity, float))
    if not np.isfinite(v) or v.imag < 0 or np.any(~np.isfinite(w)) or np.any(w == 0):
        raise ValueError("finite real/upper-half-plane ray and nonzero group velocities required")
    if v == 0:
        return np.tile(np.array([-1., 0., -1/3], complex), (len(w), 1))
    result = np.zeros((len(w), 3), complex)
    series = np.abs(w/v) <= .125
    # An absolutely convergent angular series avoids subtracting large moments.
    for n in range(3):
        for j in range(1, 33):
            moment = 1/(n+j+1) if (n+j) % 2 == 0 else 0.
            result[series, n] += (w[series]/v)**j*moment
    remaining = ~series
    wr = w[remaining]
    if len(wr):
        if v.imag == 0:
            if np.any(abs(v.real) == np.abs(wr)):
                raise ValueError("exact ray/group-velocity endpoint; split radial integration")
            logarithm = np.log(np.abs((v.real+wr)/(v.real-wr)))
            integral = logarithm/(2*wr)-1j*pi*(abs(v.real) < np.abs(wr))/(2*np.abs(wr))
        else:
            integral = np.log1p(2*wr/(v-wr))/(2*wr)
        for n in range(3):
            moment = 1/(n+1) if n % 2 == 0 else 0.
            result[remaining, n] = v*integral-moment
            integral = (v*integral-moment)/wr
    return result


def angular_check(velocity, group_velocity):
    """Independent Cauchy-weight quad of the original angular numerator."""
    v, w = float(velocity), float(group_velocity)
    if w == 0 or abs(v) == abs(w):
        raise ValueError("nonzero w away from exact endpoint required")
    target = v/w
    values = []
    for n in range(3):
        if abs(target) < 1:
            real = -quad(lambda c: c**(n+1), -1., 1., weight="cauchy", wvar=target,
                         epsabs=1e-12)[0]
            imaginary = -pi*w*target**(n+1)/(2*abs(w))
            values.append(real/2+1j*imaginary)
        else:
            values.append(quad(lambda c: c**n*w*c/(v-w*c), -1., 1., epsabs=1e-12)[0]/2)
    return float(np.max(np.abs(np.asarray(values)-angular_moments(v, w)[0])))


def group_velocities(k, mu, a, b):
    k = np.atleast_1d(np.asarray(k, np.longdouble))
    if np.any(~np.isfinite(k)) or np.any(k <= 0):
        raise ValueError("positive finite momentum required")
    poles, _ = G["extended_poles"](k, mu, a, b)
    if mu == 0:
        return k[:, None]/poles
    discriminant = np.sqrt((a-b)**2+8*mu*mu*(a+b)+16*mu**4+16*mu*mu*k*k)
    branch = np.array([1., -1., -1., 1.])
    return k[:, None]/poles*(1+branch[None, :]*4*mu*mu/discriminant[:, None])


def velocity_endpoints(velocity, mu, a, b):
    """Find thermal Landau thresholds as integration splits, not excisions."""
    v = abs(float(np.real(velocity)))
    if complex(velocity).imag != 0 or v == 0:
        return []
    scale = max(mu, sqrt(a), sqrt(b), 1.)
    grid = np.geomspace(scale*1e-7, scale*1e5, 1024)
    speeds = np.abs(group_velocities(grid, mu, a, b))
    roots = []
    for mode in (0, 1):
        differences = speeds[:, mode]-v
        for j in np.flatnonzero(differences[:-1]*differences[1:] < 0):
            root = brentq(lambda k: float(abs(group_velocities(k, mu, a, b)[0, mode])-v),
                          grid[j], grid[j+1], xtol=1e-13)
            if not any(np.isclose(root, old, rtol=1e-9, atol=1e-12) for old in roots):
                roots.append(root)
    return sorted(roots)


def soft_difference(velocity, t, mu, a, b, order=96):
    """Only equal-branch thermal poles differ from the static soft anchor."""
    F["validate"](t, mu, a, b)
    if min(a, b) <= 0 or isinstance(order, bool) or not isinstance(order, int) or order < 32:
        raise ValueError("positive unchanged internal masses and integer order>=32 required")
    angular_moments(velocity, .5)
    if t == 0 or velocity == 0:
        return {"bubble": np.zeros((3, 3), complex), "mixed": np.zeros((3, 4), complex),
                "reverse": np.zeros((4, 3), complex), "loop_current": np.zeros((4, 4), complex),
                "velocity_endpoints": []}
    scale = max(t, mu, sqrt(a), sqrt(b), 1.)
    endpoints = velocity_endpoints(velocity, mu, a, b)
    splits = np.unique([0.]+[k/(scale+k) for k in endpoints]+[1.])
    nodes, weights = np.polynomial.legendre.leggauss(order)
    u, weights = (nodes+1)/2, weights/2
    joint = np.zeros((5, 5), complex)
    transverse = 0j
    for lo, hi in zip(splits[:-1], splits[1:]):
        x = lo+(hi-lo)*np.sin(pi*u/2)**2
        dx = (hi-lo)*pi/2*np.sin(pi*u)
        k = scale*x/(1-x)
        measure = weights*dx*scale/(1-x)**2*k*k/(2*pi*pi)
        poles, residues = G["extended_poles"](k, mu, a, b)
        speeds = group_velocities(k, mu, a, b)
        subtotal = np.zeros((len(k), 5, 5), np.clongdouble)
        trtotal = np.zeros(len(k), np.clongdouble)
        for mode in range(4):
            p, residue = poles[:, mode], residues[:, mode]
            occupation = np.exp(-np.abs(p)/t)/(-np.expm1(-np.abs(p)/t))
            derivative = -occupation*(1+occupation)/t
            difference = angular_moments(velocity, speeds[:, mode])-np.array([-1., 0., -1/3])
            operators = np.zeros((len(k), 5, 2, 2), np.clongdouble)
            operators[:, :3] = G["BASIS"]
            operators[:, 3] = -2*p[:, None, None]*G["ROTATION"]+2j*mu*np.eye(2)
            operators[:, 4] = -2j*k[:, None, None]*G["ROTATION"]
            traces = np.einsum("...aij,...jk,...bkl,...li->...ab", operators, residue, operators, residue)
            powers = np.array([0, 0, 0, 0, 1])
            moments = difference[:, powers[:, None]+powers[None, :]]
            subtotal -= .5*derivative[:, None, None]*traces*moments
            trtrace = np.einsum("ij,...jk,kl,...li->...", G["ROTATION"], residue, G["ROTATION"], residue)
            trtotal += derivative*k*k*trtrace*(difference[:, 0]-difference[:, 2])
        joint += np.asarray(np.sum(measure[:, None, None]*subtotal, axis=0), complex)
        transverse += complex(np.sum(measure*trtotal))
    bubble, mixed, reverse, current = R["unpack_joint"](joint, transverse)
    return {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": current,
            "velocity_endpoints": endpoints}


def static_anchor(t, mu, a, b):
    loops = G["gauge_loops"](0., 0j, t, mu, a, b, radial_order=144, angular_order=72)
    return {"bubble": F["static_finite_bubble"](t, mu, a, b),
            "mixed": loops[0], "reverse": loops[1], "loop_current": loops[2]}


def soft_response(velocity, mu, a, b, s, coupling, loops):
    """Eliminate covariance and radial mean field, but NOT the phase state."""
    bubble = loops["bubble"]
    _, kernel, vertices = F["source_vertices"](s, coupling)
    mass_response = np.linalg.solve(np.eye(3)-kernel@bubble, vertices)
    field = np.diag([a, b]).astype(complex)+.5*vertices.T@bubble@mass_response
    forward, reverse, aa = G["classical_vertices"](0., 0j, mu, s)
    forward += .5*vertices.T@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    reverse += .5*loops["reverse"]@mass_response
    aa += loops["loop_current"]+.5*loops["reverse"]@kernel@np.linalg.solve(np.eye(3)-bubble@kernel, loops["mixed"])
    if field[0, 0] == 0:
        raise ValueError("radial inverse is singular; no pseudoinverse")
    radial_source = aa-np.outer(reverse[:, 0], forward[0, :])/field[0, 0]
    ray = np.array([complex(velocity), 1j, 0., 0.])
    phase_coefficient = -ray@radial_source@ray/s
    return {"phase_coefficient": complex(phase_coefficient), "radial_source": radial_source,
            "radial_inverse": complex(field[0, 0]),
            "covariance_min_singular_value": float(np.linalg.svd(np.eye(3)-kernel@bubble, compute_uv=False)[-1]),
            "zero_order_phase_Ward_residual": float(max(abs(field[1, 1]), abs(field[1, 0]), abs(field[0, 1]),
                                                         np.max(np.abs(forward[1])), np.max(np.abs(reverse[:, 1]))))}


def finite_phase_coefficient(q, velocity, example, order=64):
    loops = R["retarded_loops"](q, velocity*q, example["T"], example["mu"], example["a"], example["b"],
                                radial_order=order, angular_order=order)
    response = R["reoptimized_response"](q, velocity*q, example["mu"], example["a"], example["b"],
                                         example["s"], example["u_canonical"], loops)
    field, forward, reverse, aa = response[:4]
    phase = field[1, 1]-field[1, 0]*field[0, 1]/field[0, 0]
    radial = aa-np.outer(reverse[:, 0], forward[0, :])/field[0, 0]
    ray = np.array([velocity, 1j, 0., 0.])
    ward_estimate = -ray@radial@ray/example["s"]
    return {"q": q, "omega": velocity*q, "phase_over_q_squared": F["complex_matrix"](np.asarray(phase/q**2)),
            "radial_current_Ward_estimate": F["complex_matrix"](np.asarray(ward_estimate)),
            "phase_vs_current_Ward_disagreement": float(abs(phase/q**2-ward_estimate)),
            "loop_max_disagreement_from_soft": None,
            "bubble": loops["bubble"], "mixed": loops["mixed"], "reverse": loops["reverse"],
            "loop_current": loops["loop_current"]}


def reactive_zero(example, anchor, order=128):
    """Zero of Re phase inverse only; absorption prevents calling it a pole."""
    def coefficient(velocity):
        difference = soft_difference(velocity, example["T"], example["mu"], example["a"], example["b"], order)
        loops = {key: anchor[key]+difference[key] for key in anchor}
        return soft_response(velocity, example["mu"], example["a"], example["b"], example["s"], example["u_canonical"], loops)["phase_coefficient"]
    bracket = (.1, .6)
    left, right = coefficient(bracket[0]), coefficient(bracket[1])
    if left.real*right.real >= 0:
        raise ValueError("declared reactive-zero bracket has no sign change; do not tune it")
    zero = brentq(lambda velocity: coefficient(velocity).real, *bracket, xtol=1e-10)
    value = coefficient(zero)
    return {"bracket": bracket, "velocity_ray_at_Re_inverse_zero": float(zero),
            "phase_inverse_at_reactive_zero": F["complex_matrix"](np.asarray(value)),
            "is_a_real_frequency_pole": False,
            "interpretation": "absorptive collective response; complex pole continuation is not computed"}


def audit():
    predecessor = json.loads((ROOT/PREVIOUS_ARTIFACT).read_text(encoding="utf-8"))
    lineage = R["predecessor_hashes_match"](predecessor)
    examples = []
    for example in predecessor["examples"]:
        t, mu, a, b, s, coupling = (example[key] for key in ("T", "mu", "a", "b", "s", "u_canonical"))
        anchor = static_anchor(t, mu, a, b)
        static = soft_response(0., mu, a, b, s, coupling, anchor)
        susceptibility = static["radial_source"][0, 0].real
        stiffness = static["radial_source"][1, 1].real
        rows = []
        for velocity in RAYS:
            differences = [soft_difference(velocity, t, mu, a, b, n) for n in SOFT_ORDERS]
            soft = {key: anchor[key]+differences[-1][key] for key in anchor}
            response = soft_response(velocity, mu, a, b, s, coupling, soft)
            runs = [finite_phase_coefficient(q, velocity, example) for q in Q_GRID]
            for row in runs:
                row["loop_max_disagreement_from_soft"] = float(max(np.max(np.abs(row[key]-soft[key])) for key in anchor))
                row["phase_error_from_soft"] = float(abs(G["unpack"](row["phase_over_q_squared"])-response["phase_coefficient"]))
                for key in anchor:
                    row.pop(key)
            refined = finite_phase_coefficient(Q_GRID[-1], velocity, example, 80)
            refinement = float(abs(G["unpack"](refined["phase_over_q_squared"])-G["unpack"](runs[-1]["phase_over_q_squared"])))
            rows.append({"velocity_ray": velocity, "phase_coefficient": F["complex_matrix"](np.asarray(response["phase_coefficient"])),
                         "radial_source": F["complex_matrix"](response["radial_source"]),
                         "static_polynomial_coefficient": float((stiffness-velocity**2*susceptibility)/s),
                         "difference_from_static_polynomial": float(abs(response["phase_coefficient"]-(stiffness-velocity**2*susceptibility)/s)),
                         "soft_quadrature_refinements": [float(max(np.max(np.abs(differences[i][key]-differences[i-1][key])) for key in anchor)) for i in (1, 2)],
                         "velocity_endpoints": differences[-1]["velocity_endpoints"],
                         "zero_order_phase_Ward_residual": response["zero_order_phase_Ward_residual"],
                         "radial_inverse": F["complex_matrix"](np.asarray(response["radial_inverse"])),
                         "covariance_min_singular_value": response["covariance_min_singular_value"],
                         "finite_q_phase_refinement": refinement, "finite_q_runs": runs})
        zero = reactive_zero(example, anchor)
        coarse_zero = reactive_zero(example, anchor, 96)
        zero["quadrature_ray_difference"] = abs(zero["velocity_ray_at_Re_inverse_zero"]-coarse_zero["velocity_ray_at_Re_inverse_zero"])
        finite_zero = finite_phase_coefficient(.01, zero["velocity_ray_at_Re_inverse_zero"], example, 80)
        zero["finite_q_independent_inverse"] = finite_zero["phase_over_q_squared"]
        zero["finite_q_disagreement"] = float(abs(G["unpack"](finite_zero["phase_over_q_squared"])-G["unpack"](zero["phase_inverse_at_reactive_zero"])))
        examples.append({key: example[key] for key in ("T", "mu", "Phi_fixed", "a", "b", "s", "u_canonical")}
                        | {"static_source_susceptibility": float(susceptibility), "static_spatial_stiffness": float(stiffness),
                           "thermodynamic_ratio_not_admitted_mode_speed": float(sqrt(stiffness/susceptibility)), "rays": rows, "reactive_zero": zero})
    checks = {"accepted_predecessor": predecessor["closure_level"] == "CLOSED_FOR_LANE" and all(predecessor["checks"].values()),
              "predecessor_hash_lineage": lineage,
              "angular_original_integral_independent_check": max(angular_check(v, w) for v in (.1, .3, 1.2) for w in (-.2, .5, -.8)) < 1e-10,
              "soft_radial_refinement": all(row["soft_quadrature_refinements"][-1] < LOOP_TOLERANCE for e in examples for row in e["rays"]),
              "finite_q_approaches_derived_soft_limit": all(row["finite_q_runs"][-1]["phase_error_from_soft"] < row["finite_q_runs"][0]["phase_error_from_soft"] for e in examples for row in e["rays"]),
              "finite_q_loop_approaches_soft_limit": all(row["finite_q_runs"][-1]["loop_max_disagreement_from_soft"] < row["finite_q_runs"][0]["loop_max_disagreement_from_soft"] for e in examples for row in e["rays"]),
              "finite_q_independent_field_current_Ward": all(run["phase_vs_current_Ward_disagreement"] < 1e-3 for e in examples for row in e["rays"] for run in row["finite_q_runs"]),
              "finite_q_phase_numerical_refinement": all(row["finite_q_phase_refinement"] < 1e-3 for e in examples for row in e["rays"]),
              "zero_order_phase_Ward_without_imposed_mass": all(row["zero_order_phase_Ward_residual"] < WARD_TOLERANCE for e in examples for row in e["rays"]),
              "thermal_ray_not_static_polynomial": all(any(row["difference_from_static_polynomial"] > 1e-3 for row in e["rays"]) for e in examples),
              "reactive_zero_is_absorptive_not_an_undamped_pole": all(abs(e["reactive_zero"]["phase_inverse_at_reactive_zero"]["real"]) < 1e-8 and e["reactive_zero"]["phase_inverse_at_reactive_zero"]["imaginary"] < -1e-3 for e in examples),
              "reactive_zero_quadrature_refinement": all(e["reactive_zero"]["quadrature_ray_difference"] < 1e-5 for e in examples),
              "cold_equal_branch_correction_absent": not np.any(soft_difference(.3, 0., 1.05, .2, .01)["bubble"]),
              "protected_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in predecessor["protected_evidence_hashes"])}
    passed = all(checks.values())
    record = {"schema_version": "t13-hartree-soft-collective-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_FIXED_PHI_HARTREE_COLLISIONLESS_SOFT_PHASE_RESPONSE", "topic": "0.13", "branch_id": predecessor["branch_id"],
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_COLLISIONLESS_SOFT_RESPONSE" if passed else "FAIL_SOFT_RESPONSE",
              "what_is_closed": ["derived_equal_branch_thermal_ray_limit", "phase_collective_kernel_from_radial_source_Ward", "thermodynamic_static_ratio_not_same_as_collisionless_mode_equation", "reactive_zero_absorption_distinguished_from_a_real_axis_pole"],
              "equation_or_mapping": "A_n(v,w)=1/2 int c^n*w*c/(v-w*c+i0) dc; delta B=-N'(p)*Tr(Va Rp Vb Rp)*(A_n(v,w)-A_n(0,w))/2; lim Gamma_phase/q^2=-l*Gamma_AA_radial*l/s, l=(v,i,0,0)",
              "units": {"v_and_w": "dimensionless", "q_omega_T_mu_A": "E", "a_b_s": "E^2", "source_Hessian": "E^2", "phase_over_q_squared": "dimensionless", "covariance_bubble": "dimensionless"},
              "derivation_class": "ANALYTIC_COLLISIONLESS_RAY_LIMIT_OF_DECLARED_HARTREE_LOOPS_WITH_NUMERICAL_RADIAL_INTEGRATION",
              "observable": "conditional_phase_and_O2_source_response_not_material_sound_or_temperature", "data_role": "DERIVED_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.hartree_soft_ray", "t13.diagnostic.hartree_radial_source_phase_Ward"],
              "examples": examples, "checks": checks, "config": {"rays": RAYS, "finite_q_grid": Q_GRID, "soft_orders": SOFT_ORDERS, "finite_q_orders": [64, 80], "output_width": 0., "radial_domain": "0<=k<infinity"},
              "thresholds": {"soft_loop_absolute": LOOP_TOLERANCE, "phase_current_Ward_scaled_absolute": 1e-3, "phase_refinement_scaled_absolute": 1e-3, "static_phase_Ward_absolute": WARD_TOLERANCE},
              "evidence_artifacts": [{"path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in (PREVIOUS_ARTIFACT, PREVIOUS_CODE, R["CURRENT_ARTIFACT"], R["CURRENT_CODE"], Path(__file__).relative_to(ROOT).as_posix())],
              "protected_evidence_hashes": predecessor["protected_evidence_hashes"],
              "open_blockers": ["collective_complex_poles_and_global_validity_domain", "controlled_truncation_error_and_regulator_RG_action", "joint_Phi_and_material_source_detector_admission", "normal_heat_collision_KMS_entropy_transport", "independent_measurement_input"],
              "controlling_blocker": "collective_pole_domain_truncation_joint_Phi_material_transport_not_closed",
              "dependency_unlocked": ["same_candidate_collective_pole_research_only"],
              "global_real_axis_stability_proved": False, "collective_mode_speed_emitted": False, "collision_rate_emitted": False,
              "controlled_truncation_error_established": False, "joint_Phi_stationarity_derived": False,
              "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "claim_promotion": False,
              "parameter_fitting": False, "artificial_width": False, "clipping": False, "IR_filter": False, "imposed_Ward_projection": False,
              "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "core_composition_gate_overwritten": False,
              "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False, "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "claim_boundary": "Same fixed-Phi Hartree collisionless soft phase/source limit on declared rays. Not a physical sound speed, collision width, hydrodynamic heat/Kubo/KMS law, global pole proof, controlled approximation remainder, material TTG/He-II validation or Full Topic13 closure."}
    record["report"] = {"MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"], "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"],
                        "WHAT_REMAINS_OPEN": record["open_blockers"], "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
                        "WHAT_CHANGED": "Derived thermal collisionless ray moments and phase Ward kernel; checked against unchanged full finite-q PV response.",
                        "EQUATION_OR_MAPPING": record["equation_or_mapping"], "VERIFICATION": checks, "CONTROLLING_BLOCKER": record["controlling_blocker"],
                        "NEXT_ACTION": "Use the derived nonlocal soft kernel for collective pole/domain analysis; do not replace it by the equilibrium susceptibility ratio.", "CLAIM_BOUNDARY": record["claim_boundary"]}
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
