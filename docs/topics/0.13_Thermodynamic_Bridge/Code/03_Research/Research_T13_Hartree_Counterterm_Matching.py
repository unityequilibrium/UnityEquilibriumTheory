"""Homogeneous fixed-Phi Hartree counterterm and on-gap potential matching.

D,D2 are independent formal vacuum-divergence probes, not measured inputs
or numerical cutoffs. Match coefficients for arbitrary finite tadpoles and
amplitude before testing the previously declared stationary witnesses.
"""

from __future__ import annotations

import hashlib
import json
from math import isfinite
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[5]
PREFIX = "docs/topics/0.13_Thermodynamic_Bridge/"
PREVIOUS = PREFIX+"Result/artifacts/t13_renormalized_hartree_background.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_hartree_counterterm_matching.json")
HARTREE_MATRIX = np.array([[3., 1.], [1., 3.]])
IDENTITY_TOLERANCE = 1e-10
D_PROBES = (-.08, .03, .2)
D2_PROBES = (-.07, .11)
COUPLING_PROBES = (.1, 1., 2.)
STATE_PROBES = ((0., 0., 0.), (.27, .06, -.02), (.4, .03, .17), (.2, -.1, .5))


def counterterms(coupling, D, D2, mass_sq, reference_sq):
    values = (coupling, D, D2, mass_sq, reference_sq)
    if not all(isfinite(v) for v in values) or coupling <= 0 or reference_sq <= 0:
        raise ValueError("finite probes, u>0 and reference mass squared>0 required")
    d2, d4 = 1+2*coupling*D, 1+4*coupling*D
    if d2 == 0 or d4 == 0:
        raise ValueError("counterterm projection pole; no clipping or continuation")
    B = coupling/d2
    A = coupling/(d2*d4)
    mb = mass_sq-2*(A+B)*(D2+(mass_sq-reference_sq)*D)
    u4 = A+2*B-2*coupling
    return {"A": A, "B": B, "u4": u4, "bare_mass_sq": mb,
            "delta_A": A-coupling, "delta_B": B-coupling,
            "delta_4": u4-coupling, "delta_mass_sq": mb-mass_sq}


def projection_matrix(A, B):
    return np.array([[A+2*B, A], [A, A+2*B]])


def finite_masses(s, finite_tadpoles, mass_sq, coupling):
    if not isfinite(s) or s < 0:
        raise ValueError("finite nonnegative canonical amplitude squared required")
    F = np.asarray(finite_tadpoles, dtype=float)
    if F.shape != (2,) or not np.all(np.isfinite(F)):
        raise ValueError("two finite renormalized tadpoles required; signs are not clipped")
    return mass_sq+coupling*s*np.array([3., 1.])+coupling*HARTREE_MATRIX@F


def normalization_constant(ct, D, D2, mass_sq, reference_sq, reference_logdet=0.):
    delta = mass_sq-reference_sq
    return (reference_logdet+delta*D2+delta*delta*D/2
            -(ct["A"]+ct["B"])*(D2+delta*D)**2)


def state_match(s, finite_tadpoles, mass_sq, coupling, mu, D, D2,
                reference_sq, finite_logdet=.19, reference_logdet=.17):
    if not all(isfinite(v) for v in (mu, finite_logdet, reference_logdet)) or mu < 0:
        raise ValueError("finite source probes and nonnegative chemical potential required")
    ct = counterterms(coupling, D, D2, mass_sq, reference_sq)
    F = np.asarray(finite_tadpoles, dtype=float)
    M = finite_masses(s, F, mass_sq, coupling)
    T = F+D2+(M-reference_sq)*D
    Kb = projection_matrix(ct["A"], ct["B"])
    bare_masses = ct["bare_mass_sq"]+Kb@np.array([s, 0.])+Kb@T
    field = ct["bare_mass_sq"]-mu*mu+ct["u4"]*s+Kb[0]@T
    finite_field = M[0]-mu*mu-2*coupling*s
    divergent_logdet = (reference_logdet+(M.sum()-2*reference_sq)*D2/2
                         +np.sum((M-reference_sq)**2)*D/4)
    bare_potential = ((ct["bare_mass_sq"]-mu*mu)*s/2+ct["u4"]*s*s/4
                      +finite_logdet+divergent_logdet
                      -(ct["A"]+ct["B"])*T.sum()**2/4
                      -ct["B"]*(T[0]-T[1])**2/4)
    finite_potential = ((mass_sq-mu*mu)*s/2+coupling*s*s/4+finite_logdet
                        -coupling*(3*F[0]**2+2*F[0]*F[1]+3*F[1]**2)/4)
    constant = normalization_constant(ct, D, D2, mass_sq, reference_sq, reference_logdet)
    return {"counterterms": ct, "finite_masses_sq": M.tolist(),
            "unsubtracted_tadpoles": T.tolist(), "bare_gap_residual": (bare_masses-M).tolist(),
            "bare_field_bracket": float(field), "finite_field_bracket": float(finite_field),
            "field_match_residual": float(field-finite_field),
            "bare_on_gap_potential": float(bare_potential),
            "finite_on_gap_potential": float(finite_potential),
            "state_independent_normalization": float(constant),
            "potential_match_residual": float(bare_potential-finite_potential-constant)}


def coefficient_match(coupling, D, D2, mass_sq, reference_sq):
    ct = counterterms(coupling, D, D2, mass_sq, reference_sq)
    Kb = projection_matrix(ct["A"], ct["B"])
    finite = coupling*HARTREE_MATRIX
    # This coefficient identity covers arbitrary finite tadpoles and s,
    # not only a collection of stationary numerical roots.
    matrix_residual = Kb@(np.eye(2)+D*finite)-finite
    offset_residual = (ct["bare_mass_sq"]-mass_sq
                       +2*(ct["A"]+ct["B"])*(D2+(mass_sq-reference_sq)*D))
    field_residual = ct["u4"]-(ct["A"]+2*ct["B"]-2*coupling)
    return {"tadpole_and_amplitude_coefficient_residual": matrix_residual.tolist(),
            "mass_offset_residual": offset_residual, "field_quartic_residual": field_residual,
            "singlet_bare_eigenvalue": 2*(ct["A"]+ct["B"]),
            "traceless_bare_eigenvalue": 2*ct["B"]}


def single_coupling_obstruction(coupling, D):
    if not isfinite(coupling) or coupling <= 0 or not isfinite(D):
        raise ValueError("u>0 and finite D required")
    if 1+2*coupling*D == 0 or 1+4*coupling*D == 0:
        raise ValueError("counterterm projection pole")
    singlet_required = coupling/(1+4*coupling*D)
    traceless_required = coupling/(1+2*coupling*D)
    return {"single_u_b_required_by_singlet": singlet_required,
            "single_u_b_required_by_traceless": traceless_required,
            "difference": singlet_required-traceless_required,
            "difference_formula": -2*coupling*coupling*D/((1+4*coupling*D)*(1+2*coupling*D))}


def symmetric_tensor_projection(coupling, D):
    """Orthonormal trace, diagonal-traceless and offdiagonal O(2) channels."""
    ct = counterterms(coupling, D, 0., 1., 1.)
    finite = np.diag([4*coupling, 2*coupling, 2*coupling])
    bare = np.diag([2*(ct["A"]+ct["B"]), 2*ct["B"], 2*ct["B"]])
    return finite, bare


def conditional_vertex_subtraction(coupling, D, finite_bubble):
    """Conditional vertex algebra, assuming J_b=J_F+D*identity.

    The finite bubble is an algebra probe, not a computed physical loop.
    This identity does not establish its UV decomposition or continuation.
    """
    J = np.asarray(finite_bubble, dtype=complex)
    if J.shape != (3, 3) or not np.all(np.isfinite(J)):
        raise ValueError("finite three-channel bubble required")
    finite, bare = symmetric_tensor_projection(coupling, D)
    response_finite = np.linalg.inv(np.linalg.inv(finite)-J)
    response_bare = np.linalg.inv(np.linalg.inv(bare)-J-D*np.eye(3))
    return {"maximum_response_residual": float(np.max(np.abs(response_bare-response_finite))),
            "noncommuting_bubble_residual": float(np.max(np.abs(finite@J-J@finite))),
            "bare_inverse_subtraction_residual": float(np.max(np.abs(np.linalg.inv(bare)-D*np.eye(3)-np.linalg.inv(finite))))}


def audit():
    previous = json.loads((ROOT/PREVIOUS).read_text(encoding="utf-8"))
    formal = []
    for u in COUPLING_PROBES:
        for D in D_PROBES:
            for D2 in D2_PROBES:
                coeff = coefficient_match(u, D, D2, 1.3, .7)
                states = [state_match(s, (f1, f2), 1.3, u, .85, D, D2, .7)
                          for s, f1, f2 in STATE_PROBES]
                formal.append({"u": u, "D": D, "D2": D2, "coefficient_match": coeff,
                               "states": states, "single_coupling": single_coupling_obstruction(u, D)})
    examples = []
    for e in previous["examples"]:
        bg, loops = e["background"], e["background"]["loops"]
        mass_sq = e["mu"]**2-e["r"]
        rows = [state_match(bg["s"], (loops["sigma"], loops["phase"]), mass_sq,
                            e["u_canonical"], e["mu"], D, D2, 1., loops["loop_free_energy"], 0.)
                for D in D_PROBES for D2 in D2_PROBES]
        examples.append({"mu": e["mu"], "T": e["T"], "Phi_fixed": e["Phi_fixed"],
                         "mass_sq": mass_sq, "rows": rows,
                         "previous_variational_potential": bg["potential"],
                         "on_gap_potential_to_previous_residual": max(abs(v["finite_on_gap_potential"]-bg["potential"]) for v in rows),
                         "shifted_masses_to_previous_residual": max(abs(v["finite_masses_sq"][i]-e["mu"]**2-bg[name]) for v in rows for i, name in enumerate(("a", "b")))})
    def maximum_residual(row):
        return max(max(abs(v) for v in row["bare_gap_residual"]),
                   abs(row["field_match_residual"]), abs(row["potential_match_residual"]))
    formal_error = max(maximum_residual(s) for e in formal for s in e["states"])
    actual_error = max(maximum_residual(s) for e in examples for s in e["rows"])
    matrix_error = max(abs(v) for e in formal for row in e["coefficient_match"]["tadpole_and_amplitude_coefficient_residual"] for v in row)
    tensor_rows = []
    for u in COUPLING_PROBES:
        for D in D_PROBES:
            finite, bare = symmetric_tensor_projection(u, D)
            J = np.array([[.03, .02, -.01], [.02, -.04, .015], [-.01, .015, .06]])
            vertex = conditional_vertex_subtraction(u, D, J+1j*.01*np.eye(3))
            tensor_rows.append({"u": u, "D": D,
                                "tensor_coefficient_residual": float(np.max(np.abs(bare@(np.eye(3)+D*finite)-finite))),
                                "conditional_vertex": vertex})
    checks = {
        "previous_candidate_acceptance_and_scope_preserved": previous["verification_status"] == "PASS_FIXED_PHI_HARTREE_SOURCE_BACKGROUND" and previous["closure_level"] == "CLOSED_FOR_LANE" and all(previous["checks"].values()) and all(previous[flag] is False for flag in ("full_core_unlock", "g1_physical_unlock", "g2_science_unlock", "claim_promotion")),
        "two_tensor_gap_coefficient_identity": matrix_error < IDENTITY_TOLERANCE,
        "mass_and_field_counterterm_coefficients": all(abs(e["coefficient_match"]["mass_offset_residual"]) < IDENTITY_TOLERANCE and abs(e["coefficient_match"]["field_quartic_residual"]) < IDENTITY_TOLERANCE for e in formal),
        "arbitrary_probe_gap_field_and_potential_cancellation": formal_error < IDENTITY_TOLERANCE,
        "single_coupling_obstruction_for_nonzero_divergence": all(abs(e["single_coupling"]["difference"]) > IDENTITY_TOLERANCE and abs(e["single_coupling"]["difference"]-e["single_coupling"]["difference_formula"]) < IDENTITY_TOLERANCE for e in formal),
        "matched_previous_fixed_Phi_stationary_witnesses": actual_error < IDENTITY_TOLERANCE and all(e["shifted_masses_to_previous_residual"] < IDENTITY_TOLERANCE for e in examples),
        "finite_on_gap_potential_matches_previous_without_retuning": all(e["on_gap_potential_to_previous_residual"] < IDENTITY_TOLERANCE for e in examples),
        "full_symmetric_two_tensor_channels": all(e["tensor_coefficient_residual"] < IDENTITY_TOLERANCE for e in tensor_rows),
        "conditional_noncommuting_vertex_subtraction_identity": all(e["conditional_vertex"]["maximum_response_residual"] < IDENTITY_TOLERANCE and e["conditional_vertex"]["noncommuting_bubble_residual"] > IDENTITY_TOLERANCE for e in tensor_rows),
    }
    paths = (PREVIOUS, Path(__file__).relative_to(ROOT).as_posix())
    protected = (PREFIX+"Result/artifacts/t13_conditional_twofluid_operator.json",
                 PREFIX+"Result/artifacts/t13_polar_dynamic_composite.json",
                 "docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json",
                 "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json")
    record = {
        "major_result_id": "T13_FIXED_PHI_HARTREE_COUNTERTERM_AND_ON_GAP_POTENTIAL_MATCH",
        "topic": "0.13", "branch_id": previous["branch_id"],
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": "PASS_HOMOGENEOUS_HARTREE_COUNTERTERM_MATCH" if all(checks.values()) else "FAIL_HARTREE_COUNTERTERM_MATCH",
        "what_is_closed": ["two_tensor_homogeneous_gap_coefficient_cancellation", "distinct_field_quartic_counterterm", "on_gap_potential_cancellation_up_to_state_independent_constant", "previous_stationary_witnesses_matched_without_retuning", "symmetric_trace_and_two_traceless_tensor_channels", "conditional_vertex_subtraction_identity_given_declared_bubble_divergence"],
        "equation_or_mapping": "H=[[3,1],[1,3]] (not UET C); K_b(I+D*u*H)=u*H; B=u/(1+2uD); A=u/[(1+2uD)(1+4uD)]; u4=A+2B-2u; F_b_on_gap=F_finite_on_gap+N(D,D2,m2,M02)",
        "units": {"u_A_B_u4_D": "dimensionless", "D2_mass_sq_reference_s_tadpole": "E^2", "mu_T": "E", "potential_normalization": "E^4"},
        "derivation_class": "HOMOGENEOUS_TWO_TENSOR_ALGEBRA_AND_FINITE_POTENTIAL_MATCH_NOT_FULL_REGULATOR_PROOF",
        "observable": "canonical_static_background_and_potential_not_material_thermal_response",
        "data_role": "DERIVED_FORMAL_DIVERGENCE_PROBES_NO_MEASURED_ROWS",
        "method_references": [{"url": "https://arxiv.org/pdf/1410.1337", "locator": "II-IV, independent invariant couplings, finite gap/field and potential; Eq. (6) tensor transcription independently contracted", "role": "standard_2PI_Hartree_method_not_UET_novelty_or_material_calibration"}],
        "formal_probe_grid": formal, "previous_stationary_witnesses": examples,
        "symmetric_tensor_and_conditional_vertex_checks": tensor_rows, "checks": checks,
        "maximum_formal_residual": formal_error, "maximum_previous_witness_residual": actual_error,
        "thresholds": {"algebraic_identity": IDENTITY_TOLERANCE},
        "evidence_artifacts": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],
        "protected_evidence_hashes": [{"path": p, "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in protected],
        "probe_policy": "D and D2 are independent formal vacuum-divergence values. No finite probe is claimed to implement a regulator or continuum UV limit. Counterterms contain no T,mu,Phi or finite-tadpole input; mass_sq is a fixed-Phi action input, not a new calibration. Bare quartic sign at these probes is not a global-stability claim.",
        "open_blockers": ["vacuum_regulator_tensor_and_translation_shift_match", "source_dependent_external_finite_q_frequency_vertex_renormalization", "RG_and_action_material_coefficient_identity", "joint_Phi_and_global_phase_state", "microscopic_IR_remainder_normal_component_SK_KMS_and_transport"],
        "controlling_blocker": "external_vertex_and_regulator_RG_material_matching_not_closed",
        "dependency_unlocked": ["external_vertex_matching_with_homogeneous_counterterm_contract_only"],
        "homogeneous_counterterm_projection_derived": True,
        "on_gap_potential_counterterm_cancellation_derived": True,
        "conditional_vertex_subtraction_identity_derived": True,
        "finite_frequency_bubble_divergence_computed": False,
        "same_coupling_counterterm_sufficient": False,
        "finite_probe_is_physical_UV_limit": False,
        "temperature_dependent_counterterms": False,
        "full_covariant_counterterm_match": False, "RG_invariance_established": False,
        "external_finite_frequency_response_derived": False, "joint_Phi_stationarity_derived": False,
        "internal_gap_used_as_physical_Goldstone_mass": False,
        "physical_Kubo_emitted": False, "g1_physical_unlock": False, "g2_science_unlock": False,
        "full_core_unlock": False, "core_composition_gate_overwritten": False,
        "claim_promotion": False, "parameter_fitting": False, "xie_2026_accessed": False,
        "C_relabelled_as_charge_or_mass": False, "R_gen_added_as_state": False,
        "claim_boundary": "Homogeneous fixed-Phi Hartree counterterm and on-gap potential matching only. Formal divergence cancellation is not a covariant regulator construction, RG/material matching, full external response, physical prediction or global UET closure. The original Gaussian and physical admission blockers remain."
    }
    record["report"] = {
        "MAJOR_RESULT_CLOSURE": record["major_result_id"]+": "+record["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": record["what_is_closed"], "WHAT_REMAINS_OPEN": record["open_blockers"],
        "DEPENDENCY_UNLOCKED": record["dependency_unlocked"], "STATUS": record["verification_status"],
        "WHAT_CHANGED": "Matched gap/field tensor projections and on-gap potential to the previous fixed-Phi finite candidate, without retuning.",
        "EQUATION_OR_MAPPING": record["equation_or_mapping"],
        "VERIFICATION": "Coefficient identities, independent formal divergence/state probes, on-gap normalization and previous witness matching.",
        "CONTROLLING_BLOCKER": record["controlling_blocker"],
        "NEXT_ACTION": "Construct regulator/source-dependent external vertex and RG input matching; do not use the internal Hartree gap as physical response.",
        "CLAIM_BOUNDARY": record["claim_boundary"],
    }
    return record


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"],
                      "maximum_formal_residual": result["maximum_formal_residual"],
                      "maximum_previous_witness_residual": result["maximum_previous_witness_residual"]}, indent=2))
