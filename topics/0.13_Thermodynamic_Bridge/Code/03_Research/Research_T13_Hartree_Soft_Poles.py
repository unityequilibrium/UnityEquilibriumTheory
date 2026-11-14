"""Local Landau-sheet continuation of the accepted collisionless soft kernel.

The added term is a derived spectral discontinuity, not an assigned width.
Only the unchanged natural-unit fixed-Phi witnesses are evaluated here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from math import pi, sqrt
from pathlib import Path
import runpy

import numpy as np
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREVIOUS_CODE = PREFIX+"Code/03_Research/Research_T13_Hartree_Soft_Collective.py"
PREVIOUS_ARTIFACT = PREFIX+"Result/artifacts/t13_hartree_soft_collective.json"
M = runpy.run_path(str(ROOT/PREVIOUS_CODE))
R, G, F = M["R"], M["G"], M["F"]
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_soft_poles.json")
POWERS = np.array([0, 0, 0, 0, 1])
MATRIX_POWERS = POWERS[:, None]+POWERS[None, :]
SPLIT_VELOCITIES = (.1, .2, .3, .4, .5, .6, .8)
ALTERNATE_SPLITS = (.15, .25, .35, .45, .55, .75)
ORDERS = (64, 96, 128)
ROOT_TOLERANCE = 1e-8
REFINEMENT_TOLERANCE = 2e-5
UPPER_CONTOUR = (-1.5, 1.5, .002, .5)
LOWER_CONTOUR = (.12, .58, -.02, -.0005)
WINDING_STEPS = (64, 128, 256, 512)
SEEDS = (.2-.01j, .4-.005j)
JUMP_RAYS = (.2, .3, .4)
CONTINUITY_ETA = (.002, .001, .0005)


def validate_example(example, order):
    F["validate"](example["T"], example["mu"], example["a"], example["b"])
    if (min(example[key] for key in ("T", "mu", "a", "b", "s", "u_canonical")) <= 0
            or any(not np.isfinite(example[key]) for key in ("s", "u_canonical"))
            or isinstance(order, bool) or not isinstance(order, int) or order < 32):
        raise ValueError("positive gapped finite-T fixed-Phi input and integer order>=32 required")


def complex_poles(k, mu, a, b):
    """Analytic continuation of the original determinant near positive real k."""
    k = np.atleast_1d(np.asarray(k, complex))
    discriminant = np.sqrt((a-b)**2+8*mu*mu*(a+b)+16*mu**4+16*mu*mu*k*k)
    high_sq = k*k+(a+b)/2+2*mu*mu+discriminant/2
    high = np.sqrt(high_sq)
    low = np.sqrt((k*k+a)*(k*k+b)/high_sq)
    poles = np.stack((-high, -low, low, high), axis=-1)
    residues = np.zeros(poles.shape+(2, 2), complex)
    residues[..., 0, 0] = k[:, None]**2+b-poles*poles
    residues[..., 1, 1] = k[:, None]**2+a-poles*poles
    residues[..., 0, 1] = -2j*mu*poles
    residues[..., 1, 0] = 2j*mu*poles
    derivative = 4*poles*(poles*poles-k[:, None]**2-(a+b)/2-2*mu*mu)
    residues /= derivative[..., None, None]
    signed_speed = k[:, None]/poles*(1+np.array([1., -1., -1., 1.])*4*mu*mu/discriminant[:, None])
    return poles, residues, signed_speed


def thermal_weights(k, example):
    """Joint spectral weights including the original full radial measure."""
    k = np.atleast_1d(np.asarray(k, complex))
    validate_example(example, 32)
    t, mu, a, b = (example[key] for key in ("T", "mu", "a", "b"))
    poles, residues, speeds = complex_poles(k, mu, a, b)
    matrix = np.zeros((len(k), 4, 5, 5), complex)
    transverse = np.zeros((len(k), 4), complex)
    for mode in range(4):
        p, residue = poles[:, mode], residues[:, mode]
        energy = p if mode >= 2 else -p
        occupation = np.exp(-energy/t)/(-np.expm1(-energy/t))
        derivative = -occupation*(1+occupation)/t
        operators = np.zeros((len(k), 5, 2, 2), complex)
        operators[:, :3] = G["BASIS"]
        operators[:, 3] = -2*p[:, None, None]*G["ROTATION"]+2j*mu*np.eye(2)
        operators[:, 4] = -2j*k[:, None, None]*G["ROTATION"]
        trace = np.einsum("...aij,...jk,...bkl,...li->...ab", operators, residue, operators, residue)
        matrix[:, mode] = -.5*derivative[:, None, None]*trace*k[:, None, None]**2/(2*pi*pi)
        trace_j = np.einsum("ij,...jk,kl,...li->...", G["ROTATION"], residue, G["ROTATION"], residue)
        transverse[:, mode] = derivative*k**4*trace_j/(2*pi*pi)
    return matrix, transverse, speeds


def velocity_root(v, example, mode):
    """Continue a unique positive-real velocity threshold into a local k strip."""
    if mode not in (2, 3) or not (.1 <= complex(v).real <= .6) or abs(complex(v).imag) > .025:
        raise ValueError("declared positive-cut local domain and positive branch required")
    mu, a, b = (example[key] for key in ("mu", "a", "b"))
    candidates = M["velocity_endpoints"](float(complex(v).real), mu, a, b)
    matching = [k for k in candidates if abs(float(M["group_velocities"](k, mu, a, b)[0, mode])-complex(v).real) < 1e-8]
    if len(matching) != 1:
        raise ValueError("velocity threshold is not uniquely bracketed; no selection repair")
    def equations(values):
        k = complex(*values)
        residual = complex_poles(k, mu, a, b)[2][0, mode]-v
        return [residual.real, residual.imag]
    result = root(equations, [matching[0], 0.], tol=1e-11)
    k = complex(*result.x)
    error = abs(complex_poles(k, mu, a, b)[2][0, mode]-v)
    if not result.success or error > 1e-9 or k.real <= 0:
        raise ValueError("local velocity-root continuation failed")
    return k, float(error)


def spectral_tail(v, example, order=96, contour="horizontal"):
    """Analytic spectral density D(v), with a complex threshold lower endpoint."""
    if contour not in ("horizontal", "return_to_real"):
        raise ValueError("declared analytic tail contour required")
    validate_example(example, order)
    v = complex(v)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    x, weights = (nodes+1)/2, weights/2
    scale = max(example["mu"], sqrt(example["a"]), sqrt(example["b"]), 1.)
    joint, transverse = np.zeros((5, 5), complex), 0j
    checks = []
    for branch, signed_modes in ((2, (1, 2)), (3, (0, 3))):
        threshold, root_error = velocity_root(v, example, branch)
        k = threshold+scale*x/(1-x)
        dk = scale/(1-x)**2+np.zeros_like(x, complex)
        if contour == "return_to_real":
            k -= 1j*threshold.imag*x
            dk -= 1j*threshold.imag
        matrix, trweight, speeds = thermal_weights(k, example)
        positive_speed = speeds[:, branch]
        for mode in signed_modes:
            speed = speeds[:, mode]
            density = v**(MATRIX_POWERS+1)/(2*positive_speed[:, None, None]*speed[:, None, None]**MATRIX_POWERS)
            joint += np.sum((weights*dk)[:, None, None]*matrix[:, mode]*density, axis=0)
            tdensity = v/(2*positive_speed)-v**3/(2*positive_speed*speed*speed)
            transverse += np.sum(weights*dk*trweight[:, mode]*tdensity)
        energies = complex_poles(k, example["mu"], example["a"], example["b"])[0][:, branch]
        checks.append({"positive_branch": branch, "threshold_k": [threshold.real, threshold.imag],
                       "velocity_root_residual": root_error, "minimum_energy_real": float(np.min(energies.real)),
                       "minimum_Bose_denominator": float(np.min(abs(-np.expm1(-energies/example["T"]))))})
    bubble, mixed, reverse, current = R["unpack_joint"](joint, transverse)
    return {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": current}, checks


class SoftKernel:
    """Fixed quadrature nodes keep the numerical pole function locally analytic."""

    def __init__(self, example, order=96, split_velocities=SPLIT_VELOCITIES):
        validate_example(example, order)
        if not split_velocities or any(not np.isfinite(v) or not 0 < v < 1 for v in split_velocities):
            raise ValueError("finite positive subluminal quadrature split velocities required")
        self.example = example
        self.order = order
        self.anchor = M["static_anchor"](example["T"], example["mu"], example["a"], example["b"])
        scale = max(example["mu"], sqrt(example["a"]), sqrt(example["b"]), 1.)
        thresholds = []
        for velocity in split_velocities:
            thresholds += M["velocity_endpoints"](velocity, example["mu"], example["a"], example["b"])
        splits = np.unique([0.]+[k/(scale+k) for k in thresholds]+[1.])
        nodes, weights = np.polynomial.legendre.leggauss(order)
        u, weights = (nodes+1)/2, weights/2
        ks, dks = [], []
        for lo, hi in zip(splits[:-1], splits[1:]):
            x = lo+(hi-lo)*np.sin(pi*u/2)**2
            dx = (hi-lo)*pi/2*np.sin(pi*u)
            ks.append(scale*x/(1-x))
            dks.append(weights*dx*scale/(1-x)**2)
        self.k, self.dk = np.concatenate(ks), np.concatenate(dks)
        self.matrix, self.transverse, self.speeds = thermal_weights(self.k, example)
        self.speeds = self.speeds.real

    def principal_difference(self, v):
        v = complex(v)
        joint, transverse = np.zeros((5, 5), complex), 0j
        for mode in range(4):
            speed = self.speeds[:, mode]
            if v.imag < 0:
                moments = M["angular_moments"](v.conjugate(), speed).conjugate()
            else:
                moments = M["angular_moments"](v, speed)
            difference = moments-np.array([-1., 0., -1/3])
            joint += np.sum(self.dk[:, None, None]*self.matrix[:, mode]*difference[:, MATRIX_POWERS], axis=0)
            transverse += np.sum(self.dk*self.transverse[:, mode]*(difference[:, 0]-difference[:, 2]))
        bubble, mixed, reverse, current = R["unpack_joint"](joint, transverse)
        return {"bubble": bubble, "mixed": mixed, "reverse": reverse, "loop_current": current}

    def response(self, v, sheet="retarded_local", contour="horizontal"):
        v = complex(v)
        if not np.isfinite(v) or sheet not in ("retarded_local", "principal_lower"):
            raise ValueError("finite velocity and declared sheet required")
        if v.imag < 0 and not (.1 <= v.real <= .6 and v.imag >= -.025):
            raise ValueError("lower-sheet pole domain is local, not globally admitted")
        difference = self.principal_difference(v)
        if v.imag < 0 and sheet == "retarded_local":
            density, _ = spectral_tail(v, self.example, self.order, contour)
            for key in difference:
                difference[key] -= 2j*pi*density[key]
        loops = {key: self.anchor[key]+difference[key] for key in self.anchor}
        e = self.example
        result = M["soft_response"](v, e["mu"], e["a"], e["b"], e["s"], e["u_canonical"], loops)
        kernel = F["source_vertices"](e["s"], e["u_canonical"])[1]
        result["covariance_determinant"] = complex(np.linalg.det(np.eye(3)-kernel@loops["bubble"]))
        result["uneliminated_soft_determinant"] = (result["covariance_determinant"]
                                                  *result["radial_inverse"]*result["phase_coefficient"])
        return result

    def pole(self, seed, contour="horizontal"):
        def equations(values):
            value = self.response(complex(*values), contour=contour)["phase_coefficient"]
            return [value.real, value.imag]
        result = root(equations, [complex(seed).real, complex(seed).imag], tol=1e-10)
        pole = complex(*result.x)
        value = self.response(pole, contour=contour)["phase_coefficient"]
        if not result.success or abs(value) > ROOT_TOLERANCE or pole.imag >= 0:
            raise ValueError("conditional lower-sheet pole not established")
        return pole, abs(value)


def contour_points(bounds, steps):
    """Counterclockwise rectangle, closed without duplicating its corners."""
    left, right, bottom, top = bounds
    if left >= right or bottom >= top or isinstance(steps, bool) or not isinstance(steps, int) or steps < 8:
        raise ValueError("ordered rectangle and integer edge resolution>=8 required")
    corners = [complex(left, bottom), complex(right, bottom), complex(right, top), complex(left, top)]
    points = np.concatenate([np.linspace(corners[i], corners[(i+1) % 4], steps, endpoint=False) for i in range(4)])
    return np.append(points, points[0])


def sampled_winding(values):
    values = np.asarray(values, complex)
    if values.ndim != 1 or len(values) < 4 or not np.all(np.isfinite(values)) or np.any(values == 0) or values[0] != values[-1]:
        raise ValueError("finite closed nonzero contour values required")
    increments = np.angle(values[1:]/values[:-1])
    return {"sampled_winding": float(np.sum(increments)/(2*pi)),
            "maximum_phase_increment": float(np.max(np.abs(increments))),
            "minimum_boundary_modulus": float(np.min(np.abs(values))),
            "certified_zero_count": False}


def contour_audit(kernel, bounds, steps):
    responses = [kernel.response(v) for v in contour_points(bounds, steps)]
    return contour_record(responses, bounds, steps)


def contour_record(responses, bounds, steps):
    return {"bounds": bounds, "steps_per_edge": steps,
            "phase": sampled_winding([r["phase_coefficient"] for r in responses]),
            "uneliminated": sampled_winding([r["uneliminated_soft_determinant"] for r in responses]),
            "covariance": sampled_winding([r["covariance_determinant"] for r in responses]),
            "radial": sampled_winding([r["radial_inverse"] for r in responses]),
            "minimum_covariance_singular_value": min(r["covariance_min_singular_value"] for r in responses),
            "classification": "SAMPLED_ARGUMENT_PRINCIPLE_NOT_CERTIFIED"}


def contour_family(kernel, bounds, steps=WINDING_STEPS):
    if any(steps[-1] % n != 0 for n in steps):
        raise ValueError("nested contour resolutions required")
    responses = [kernel.response(v) for v in contour_points(bounds, steps[-1])]
    return [contour_record(responses[::steps[-1]//n], bounds, n) for n in steps]


def spectral_jump_check(example, velocity, order=128):
    density, checks = spectral_tail(velocity, example, order)
    direct = M["soft_difference"](velocity, example["T"], example["mu"], example["a"], example["b"], order)
    signature = np.diag([-1., 1., 1., 1.])
    jumps = {"bubble": (direct["bubble"]-direct["bubble"].conj().T)/(2j),
             "mixed": (direct["mixed"]-direct["reverse"].conj().T@signature)/(2j),
             "reverse": (direct["reverse"]-signature@direct["mixed"].conj().T)/(2j),
             "loop_current": (direct["loop_current"]-signature@direct["loop_current"].conj().T@signature)/(2j)}
    return {"velocity_ray": velocity,
            "independent_original_angular_cut_errors": {key: float(np.max(abs(jumps[key]+pi*density[key]))) for key in density},
            "threshold_checks": checks}


def derivative_audit(kernel, pole, h=1e-5):
    fn = lambda v: kernel.response(v)["phase_coefficient"]
    derivative_x = (fn(pole+h)-fn(pole-h))/(2*h)
    derivative_y = (fn(pole+1j*h)-fn(pole-1j*h))/(2j*h)
    refined = (fn(pole+h/2)-fn(pole-h/2))/h
    increments = (h, 1j*h, h*(1+1j))
    return {"step": h, "derivative": F["complex_matrix"](np.asarray(refined)),
            "Cauchy_Riemann_disagreement": float(abs(derivative_x-derivative_y)),
            "derivative_refinement": float(abs(refined-derivative_x)),
            "nonzero_derivative_modulus": float(abs(refined)),
            "local_inverse_residue_in_v": F["complex_matrix"](np.asarray(1/refined)),
            "linearization_errors": [float(abs(fn(pole+d)-refined*d)) for d in increments]}


def continuation_boundary(kernel, velocity):
    e = kernel.example
    direct = M["soft_difference"](velocity, e["T"], e["mu"], e["a"], e["b"], kernel.order)
    loops = {key: kernel.anchor[key]+direct[key] for key in kernel.anchor}
    reference = M["soft_response"](velocity, e["mu"], e["a"], e["b"], e["s"], e["u_canonical"], loops)["phase_coefficient"]
    rows = []
    for eta in CONTINUITY_ETA:
        above = kernel.response(velocity+1j*eta)["phase_coefficient"]
        below = kernel.response(velocity-1j*eta)["phase_coefficient"]
        rows.append({"eta_verification_only": eta, "above_error_from_real_axis": float(abs(above-reference)),
                     "below_error_from_real_axis": float(abs(below-reference)),
                     "upper_lower_difference": float(abs(above-below))})
    return {"velocity_ray": velocity, "real_axis_inverse": F["complex_matrix"](np.asarray(reference)), "runs": rows}


def independent_upper_reference(kernel):
    e, v = kernel.example, .3+.02j
    fixed = kernel.principal_difference(v)
    rows = []
    for n in (128, 256, 512):
        original = M["soft_difference"](v, e["T"], e["mu"], e["a"], e["b"], n)
        rows.append({"original_unsplit_order": n,
                     "loop_disagreements": {key: float(np.max(abs(fixed[key]-original[key]))) for key in fixed}})
    return {"velocity_ray": F["complex_matrix"](np.asarray(v)), "runs": rows}


def audit(progress=None):
    predecessor = json.loads((ROOT/PREVIOUS_ARTIFACT).read_text(encoding="utf-8"))
    examples = []
    for e in predecessor["examples"]:
        kernels = [SoftKernel(e, n) for n in ORDERS]
        runs = []
        for kernel in kernels:
            pole, residual = kernel.pole(SEEDS[0])
            response = kernel.response(pole)
            runs.append({"order": kernel.order, "velocity_pole": F["complex_matrix"](np.asarray(pole)),
                         "inverse_residual": float(residual), "radial_inverse": F["complex_matrix"](np.asarray(response["radial_inverse"])),
                         "covariance_determinant": F["complex_matrix"](np.asarray(response["covariance_determinant"])),
                         "covariance_min_singular_value": response["covariance_min_singular_value"],
                         "uneliminated_determinant_residual": float(abs(response["uneliminated_soft_determinant"])),
                         "zero_order_phase_Ward_residual": response["zero_order_phase_Ward_residual"]})
        kernel, pole = kernels[-1], G["unpack"](runs[-1]["velocity_pole"])
        alternate = SoftKernel(e, ORDERS[-1], ALTERNATE_SPLITS)
        second_seed = kernel.pole(SEEDS[1])[0]
        alternate_pole = alternate.pole(SEEDS[0])[0]
        alternate_contour = kernel.pole(SEEDS[0], contour="return_to_real")[0]
        _, tail_checks = spectral_tail(pole, e, ORDERS[-1])
        wrong_sheet = abs(kernel.response(pole, sheet="principal_lower")["phase_coefficient"])
        if progress:
            progress(f"mu={e['mu']}: local poles, alternate grids/contours and derivatives")
        upper = contour_family(kernel, UPPER_CONTOUR)
        if progress:
            progress(f"mu={e['mu']}: upper contour evaluated; local lower contour next")
        lower = contour_family(kernel, LOWER_CONTOUR)
        examples.append({key: e[key] for key in ("T", "mu", "Phi_fixed", "a", "b", "s", "u_canonical")}
                        | {"pole_runs": runs, "pole_refinements": [float(abs(G["unpack"](runs[i]["velocity_pole"])-G["unpack"](runs[i-1]["velocity_pole"]))) for i in (1, 2)],
                           "second_seed_disagreement": float(abs(second_seed-pole)),
                           "alternate_grid_disagreement": float(abs(alternate_pole-pole)),
                           "alternate_contour_disagreement": float(abs(alternate_contour-pole)),
                           "principal_lower_negative_control_residual": float(wrong_sheet),
                           "spectral_jump_checks": [spectral_jump_check(e, v) for v in JUMP_RAYS],
                           "local_tail_checks_at_pole": tail_checks, "analytic_derivative": derivative_audit(kernel, pole),
                           "independent_upper_reference": independent_upper_reference(kernel),
                           "continuation_boundaries": [continuation_boundary(kernel, v) for v in JUMP_RAYS],
                           "upper_contour": upper, "local_lower_contour": lower,
                           "pole_in_v_not_physical_mode_speed": True})
        if progress:
            progress(f"mu={e['mu']}: witness checks completed")
    checks = {
        "accepted_predecessor_and_hash_lineage": predecessor["closure_level"] == "CLOSED_FOR_LANE" and all(predecessor["checks"].values()) and R["predecessor_hashes_match"](predecessor),
        "independent_original_cut_matches_continued_density": all(max(row["independent_original_angular_cut_errors"].values()) < 1e-10 for e in examples for row in e["spectral_jump_checks"]),
        "independent_upper_integral_refines_to_same_kernel": all(max(e["independent_upper_reference"]["runs"][-1]["loop_disagreements"].values()) < 1e-9 and max(e["independent_upper_reference"]["runs"][-1]["loop_disagreements"].values()) < max(e["independent_upper_reference"]["runs"][0]["loop_disagreements"].values()) for e in examples),
        "same_branch_local_thresholds_and_Bose_domain": all(c["velocity_root_residual"] < 1e-9 and c["minimum_energy_real"] > 0 and c["minimum_Bose_denominator"] > .01 for e in examples for c in e["local_tail_checks_at_pole"]),
        "pole_without_assigned_width": all(r["inverse_residual"] < ROOT_TOLERANCE and G["unpack"](r["velocity_pole"]).imag < 0 for e in examples for r in e["pole_runs"]),
        "pole_refinement_and_independent_seeds": all(max(e["pole_refinements"]+[e["second_seed_disagreement"], e["alternate_grid_disagreement"], e["alternate_contour_disagreement"]]) < REFINEMENT_TOLERANCE for e in examples),
        "principal_lower_is_not_retarded_Landau_sheet": all(e["principal_lower_negative_control_residual"] > 1e-3 for e in examples),
        "simple_pole_and_local_analyticity": all(e["analytic_derivative"]["nonzero_derivative_modulus"] > 1e-3 and max(e["analytic_derivative"]["Cauchy_Riemann_disagreement"], e["analytic_derivative"]["derivative_refinement"], *e["analytic_derivative"]["linearization_errors"]) < REFINEMENT_TOLERANCE for e in examples),
        "radial_covariance_elimination_not_false_pole": all(abs(G["unpack"](r["radial_inverse"])) > .01 and abs(G["unpack"](r["covariance_determinant"])) > .01 and r["covariance_min_singular_value"] > .01 and r["uneliminated_determinant_residual"] < ROOT_TOLERANCE for e in examples for r in e["pole_runs"]),
        "continuation_matches_retarded_real_axis_boundary": all(row["runs"][-1]["above_error_from_real_axis"] < row["runs"][0]["above_error_from_real_axis"] and row["runs"][-1]["below_error_from_real_axis"] < row["runs"][0]["below_error_from_real_axis"] and row["runs"][-1]["upper_lower_difference"] < row["runs"][0]["upper_lower_difference"] for e in examples for row in e["continuation_boundaries"]),
        "sampled_upper_and_local_lower_windings_converge": all(abs(row[key]["sampled_winding"]-target) < 1e-6 for e in examples for family, target in (("upper_contour", 0), ("local_lower_contour", 1)) for row in e[family] for key in ("phase", "uneliminated")),
        "elimination_denominator_windings_are_zero": all(abs(row[key]["sampled_winding"]) < 1e-6 and row[key]["minimum_boundary_modulus"] > .01 for e in examples for family in ("upper_contour", "local_lower_contour") for row in e[family] for key in ("covariance", "radial")),
        "finest_contour_phase_steps_resolved_not_certified": all(e[family][-1][key]["maximum_phase_increment"] < pi/2 for e in examples for family in ("upper_contour", "local_lower_contour") for key in ("phase", "uneliminated", "covariance", "radial")),
        "zero_order_phase_Ward_without_projection": all(r["zero_order_phase_Ward_residual"] < REFINEMENT_TOLERANCE for e in examples for r in e["pole_runs"]),
        "protected_evidence_hashes_unchanged": all(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"] for item in predecessor["protected_evidence_hashes"])}
    passed = all(checks.values())
    record = {"schema_version": "t13-hartree-local-soft-poles-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
              "major_result_id": "T13_FIXED_PHI_HARTREE_LOCAL_LANDAU_POLE", "topic": "0.13", "branch_id": predecessor["branch_id"],
              "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL", "verification_status": "PASS_SCOPED_LOCAL_LANDAU_POLE" if passed else "FAIL_LOCAL_LANDAU_POLE",
              "what_is_closed": ["analytic_spectral_density_continuation_of_same_candidate_positive_cut", "simple_collisionless_phase_pole_at_both_fixed_Phi_witnesses", "same_pole_with_independent_seeds_quadrature_grid_and_complex_tail_contour", "sampled_upper_and_local_lower_determinant_winding_diagnostic"],
              "equation_or_mapping": "D_ab(v)=sum_j int_{|w_j|>|v|} W_ab,j(k)*v^(n+1)/(2*|w_j|*w_j^n) dk; B_L=B_principal_lower-2*pi*i*D_analytic; K_phase(v_pole)=0; D_full=det(I-K_cov*J)*Gamma_radial*K_phase",
              "units": {"v_w_pole_inverse_residue": "dimensionless", "k_omega_T_mu": "E", "bubble_density": "dimensionless", "mixed_density": "E", "current_density": "E^2", "uneliminated_soft_determinant": "E^2"},
              "derivation_class": "LOCAL_CAUCHY_SPECTRAL_CONTINUATION_WITH_COMPLEX_THRESHOLD_QUADRATURE_AND_NUMERICAL_ROOT",
              "observable": "conditional_phase_resolvent_pole_not_material_sound_or_heat_transport", "data_role": "DERIVED_NO_EMPIRICAL_ROWS",
              "equation_registry_ids": ["t13.diagnostic.hartree_local_Landau_continuation", "t13.diagnostic.hartree_soft_uneliminated_determinant"],
              "examples": examples, "checks": checks,
              "config": {"orders": ORDERS, "split_velocities": SPLIT_VELOCITIES, "alternate_split_velocities": ALTERNATE_SPLITS,
                         "seeds": [[v.real, v.imag] for v in SEEDS], "spectral_jump_rays": JUMP_RAYS, "continuity_eta_verification_only": CONTINUITY_ETA,
                         "lower_continuation_domain": {"Re_v": [.1, .6], "Im_v": [-.025, 0]}, "upper_contour": UPPER_CONTOUR,
                         "local_lower_contour": LOWER_CONTOUR, "nested_contour_steps": WINDING_STEPS,
                         "tail_contours": ["horizontal", "return_to_real"], "radial_domain": "0<=k<infinity", "assigned_output_width": None},
              "thresholds": {"root_absolute": ROOT_TOLERANCE, "numerical_refinement_absolute": REFINEMENT_TOLERANCE, "original_cut_absolute": 1e-10,
                             "sampled_winding_integer_distance": 1e-6, "finest_phase_increment": pi/2, "causal_leakage_unchanged": 1e-6},
              "evidence_artifacts": [{"path": path, "sha256": hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in (PREVIOUS_ARTIFACT, PREVIOUS_CODE, Path(__file__).relative_to(ROOT).as_posix())],
              "protected_evidence_hashes": predecessor["protected_evidence_hashes"],
              "open_blockers": ["certified_global_complex_domain_and_finite_q_pole_control", "Hartree_truncation_and_regulator_RG_full_action", "joint_Phi_stationarity_and_material_source_detector", "physical_normal_heat_collision_KMS_entropy_transport", "independent_measurement_input"],
              "controlling_blocker": "global_domain_truncation_joint_Phi_material_transport_not_closed",
              "dependency_unlocked": ["same_candidate_validity_and_joint_Phi_research_only"], "conditional_collisionless_soft_pole_computed": bool(passed),
              "certified_zero_count": False, "global_stability_proved": False, "finite_q_complex_pole_computed": False,
              "physical_mode_speed_emitted": False, "collision_rate_emitted": False, "controlled_truncation_error_established": False,
              "joint_Phi_stationarity_derived": False, "g1_physical_unlock": False, "g2_science_unlock": False, "full_core_unlock": False, "claim_promotion": False,
              "parameter_fitting": False, "artificial_width": False, "clipping": False, "IR_filter": False, "imposed_Ward_projection": False,
              "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED", "core_composition_gate_overwritten": False,
              "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False, "excluded_variables": ["R_gen", "R_obs", "nondynamical_A"],
              "claim_boundary": "Local analytically continued collisionless soft phase pole of the unchanged fixed-Phi Hartree candidate. Numerical contour winding is not a certified zero count or global stability theorem. Not finite-q pole, hydrodynamic/material sound, physical collision/Kubo/SK-KMS/heat/entropy, controlled Hartree remainder, empirical validation or Full Topic13."}
    record["report"] = {"MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"], "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"],
                        "WHAT_REMAINS_OPEN": record["open_blockers"], "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
                        "WHAT_CHANGED": "Derived spectral-tail Landau continuation and complex soft poles; tested original cuts, local analyticity, denominator controls and nested determinant contours.",
                        "EQUATION_OR_MAPPING": record["equation_or_mapping"], "VERIFICATION": checks, "CONTROLLING_BLOCKER": record["controlling_blocker"],
                        "NEXT_ACTION": "Control candidate complex-domain and approximation/action obligations, then joint-Phi/material input; do not call a local pole a thermal transport law.", "CLAIM_BOUNDARY": record["claim_boundary"]}
    return record


if __name__ == "__main__":
    result = audit(progress=lambda message: print(message, flush=True))
    OUTPUT.write_bytes((json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2), flush=True)
