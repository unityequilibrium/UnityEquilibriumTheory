"""Audit the microscopic current-to-ladder handoff after one-loop matching.

The audit closes the tree on-shell source normalization and proves that the
longitudinal Ward identity plus the static point do not determine a finite-k
transverse vertex.  It also exposes the default-action mismatch between the
new one-loop lane and older finite-cutoff kinetic lanes.  No transport
coefficient or analytic continuation is manufactured here.
"""
from __future__ import annotations

from dataclasses import asdict
from math import sqrt
from pathlib import Path
import hashlib
import json
import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_charged_current_correlator import charged_current_correlator_contract
from docs.core.uet_o2_continuum_collision_operator import continuum_collision_operator_contract
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import energy_momentum_conserving_bs_contract
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import FiniteTemperatureO2QuasiparticleConfig
from docs.core.uet_o2_heat_current_kubo_match import heat_current_kubo_match_contract
from docs.scripts.audit import audit_topic13_charged_one_loop_current_vertex as current

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_microscopic_current_ladder_matching_boundary_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_current_ladder_boundary_addendum.json"
EQUATION_ID = "uet.o2.thermal.microscopic_current_ladder_matching_boundary"
ONE_LOOP_CFG = current.CFG


def tree_on_shell_source(momentum, q=1, mass=1.):
    p = np.asarray(momentum, dtype=float)
    if p.shape != (3,) or np.any(~np.isfinite(p)) or q not in (-1, 1):
        raise ValueError("finite three-momentum and signed charge required")
    if not np.isfinite(mass) or mass <= 0:
        raise ValueError("positive finite mass required")
    energy = sqrt(float(p @ p) + mass * mass)
    vertex = 2 * q * p
    ls_z_source = vertex / (2 * energy)
    kinetic_source = q * p / energy
    return {"momentum": p, "charge": q, "mass": mass, "energy": energy,
            "tree_spatial_vertex": vertex, "lsz_normalized_source": ls_z_source,
            "kinetic_source": kinetic_source,
            "relative_residual": float(np.linalg.norm(ls_z_source - kinetic_source)
                                       / max(np.linalg.norm(kinetic_source), 1.))}


def transverse_family(vertex, transfer, coefficient):
    """Add the 1+1 dimensional transverse basis (Qz,-Q0)*F."""
    gamma = np.asarray(vertex, dtype=complex)
    Q = np.asarray(transfer, dtype=float)
    if gamma.shape != (2,) or Q.shape != (2,) or not np.all(np.isfinite(Q)):
        raise ValueError("finite two-component vertex and transfer required")
    if not np.isfinite(coefficient):
        raise ValueError("finite transverse coefficient required")
    addition = complex(coefficient) * np.array([Q[1], -Q[0]], complex)
    return {"vertex": gamma + addition, "addition": addition,
            "longitudinal_change": complex(Q @ addition),
            "static_addition_norm": float(np.linalg.norm(addition)) if np.linalg.norm(Q) == 0 else None}


def _parameter_vector_from_one_loop(cfg=ONE_LOOP_CFG):
    return {"matter_kinetic": cfg.z, "matter_mass_sq": cfg.mass_squared,
            "matter_quartic": cfg.quartic, "response_coupling": cfg.response_coupling,
            "epsilon_nc": cfg.epsilon, "response_kinetic": cfg.response_kinetic,
            "response_mass_sq": cfg.response_mass_squared,
            "response_quartic": cfg.response_quartic}


def _parameter_vector_from_kinetic(cfg):
    eos = cfg.eos
    return {"matter_kinetic": eos.matter.matter_kinetic,
            "matter_mass_sq": eos.matter.matter_mass_sq,
            "matter_quartic": eos.matter.matter_quartic,
            "response_coupling": eos.matter.response_coupling,
            "epsilon_nc": eos.response.epsilon_nc,
            "response_kinetic": eos.response.response_kinetic,
            "response_mass_sq": eos.response.response_mass_sq,
            "response_quartic": eos.response.response_quartic}


def action_parameter_match():
    target = _parameter_vector_from_one_loop()
    default = _parameter_vector_from_kinetic(FiniteTemperatureO2QuasiparticleConfig())
    matched = FiniteTemperatureO2QuasiparticleConfig(eos=O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(matter_kinetic=ONE_LOOP_CFG.z,
            matter_mass_sq=ONE_LOOP_CFG.mass_squared, matter_quartic=ONE_LOOP_CFG.quartic,
            response_coupling=ONE_LOOP_CFG.response_coupling),
        response=CovariantResponseConfig(epsilon_nc=ONE_LOOP_CFG.epsilon,
            response_kinetic=ONE_LOOP_CFG.response_kinetic,
            response_mass_sq=ONE_LOOP_CFG.response_mass_squared,
            response_quartic=ONE_LOOP_CFG.response_quartic)))
    aligned = _parameter_vector_from_kinetic(matched)
    default_residuals = {k: default[k] - v for k, v in target.items()}
    aligned_residuals = {k: aligned[k] - v for k, v in target.items()}
    return {"one_loop": target, "kinetic_default": default,
            "default_residuals": default_residuals, "matched_kinetic": aligned,
            "matched_residuals": aligned_residuals,
            "default_matches": all(v == 0 for v in default_residuals.values()),
            "explicit_bridge_matches": all(v == 0 for v in aligned_residuals.values())}


def contract_boundary():
    current_contract = charged_current_correlator_contract()
    continuum = continuum_collision_operator_contract()
    bs = energy_momentum_conserving_bs_contract()
    heat = heat_current_kubo_match_contract()
    return {
        "current_correlator_excludes_microscopic_vertex": current_contract["excluded"]["microscopic_current_vertex"],
        "continuum_excludes_microscopic_bs": continuum["excluded"]["microscopic_bethe_salpeter_vertex"],
        "energy_momentum_bs_excludes_microscopic_bs": bs["excluded"]["microscopic_bethe_salpeter_vertex"],
        "heat_lane_excludes_continuum_limit": heat["excluded"]["continuum_limit"],
        "heat_lane_excludes_physical_SI_Kubo": heat["excluded"]["physical_SI_Kubo_coefficient"],
    }


def _serial(value):
    if isinstance(value, complex): return [value.real, value.imag]
    if isinstance(value, np.ndarray): return [_serial(x) for x in value]
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, dict): return {k: _serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [_serial(v) for v in value]
    return value


def main():
    source_rows = [tree_on_shell_source(p, q, ONE_LOOP_CFG.mass)
                   for p in ((.1, 0., 0.), (.3, -.2, .4), (1., .5, -.25)) for q in (-1, 1)]
    explicit = current.current_vertex()
    Q = np.array([explicit["Q0"], explicit["Qz"]])
    transverse_rows = []
    for coefficient in (0., .1, 1.):
        row = transverse_family(explicit["total"], Q, coefficient)
        row["coefficient"] = coefficient
        row["ward_lhs"] = complex(Q @ row["vertex"])
        row["vertex_change_norm"] = float(np.linalg.norm(row["vertex"] - explicit["total"]))
        transverse_rows.append(row)
    static_rows = [transverse_family(np.zeros(2), np.zeros(2), coefficient) for coefficient in (.1, 1.)]
    parameters = action_parameter_match()
    boundaries = contract_boundary()
    checks = {
        "tree_vertex_matches_kinetic_source": max(r["relative_residual"] for r in source_rows) < 1e-14,
        "transverse_family_preserves_ward": max(abs(r["longitudinal_change"]) for r in transverse_rows) < 1e-14,
        "transverse_family_is_nontrivial_at_finite_transfer": all(r["vertex_change_norm"] > 0 for r in transverse_rows if r["coefficient"]),
        "transverse_family_vanishes_at_static_point": all(r["static_addition_norm"] == 0 for r in static_rows),
        "default_action_mismatch_is_exposed": not parameters["default_matches"],
        "explicit_action_bridge_is_exact": parameters["explicit_bridge_matches"],
        "legacy_contracts_disclose_microscopic_boundary": all(boundaries.values()),
        "prior_explicit_vertex_passes": explicit["Ward_relative_error"] < 2e-8,
    }
    paths = ["docs/scripts/audit/audit_topic13_microscopic_current_ladder_matching_boundary.py",
             "docs/core/test/test_topic13_microscopic_current_ladder_matching_boundary.py",
             "docs/scripts/audit/audit_topic13_charged_one_loop_current_vertex.py",
             "docs/core/uet_o2_charged_current_correlator.py",
             "docs/core/uet_o2_continuum_collision_operator.py",
             "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
             "docs/core/uet_o2_heat_current_kubo_match.py"]
    sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
    prior_paths = ["docs/core/artifacts/t13_charged_one_loop_current_vertex_audit.json",
                   "docs/core/artifacts/t13_charged_static_confluent_vertex_audit.json"]
    artifact = {
        "schema_version": "t13-microscopic-current-ladder-boundary-v1",
        "major_result_id": "T13_MICROSCOPIC_CURRENT_LADDER_MATCHING_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge", "closure_level": "CLOSED_FOR_LANE",
        "closure_disposition": "CLOSED_AS_TRANSVERSE_NONUNIQUENESS_NO_GO_WITH_TREE_HANDOFF",
        "verification_status": "PASS_SCOPED_TREE_SOURCE_MATCH_AND_TRANSVERSE_NO_GO" if all(checks.values()) else "WARN_CURRENT_LADDER_BOUNDARY",
        "what_is_closed": [
            "The canonical tree spatial current vertex reduces on shell to the kinetic source q*p/E after the 1/(2E) external-leg normalization.",
            "Ward contraction plus the P=Q=0 static vertex is insufficient to determine a finite-transfer transverse correction.",
            "The one-loop and legacy kinetic default action parameters are not identical; an exact explicit configuration bridge is available and required."],
        "equation_registry_ids": [EQUATION_ID], "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": {
            "tree_handoff": "Gamma_tree^i=2*q*p^i; Gamma_tree^i/(2E)=q*p^i/E=b_kin^i/sqrt(w)",
            "transverse_family": "Gamma_F^mu=Gamma^mu+F(P,Q)*(Q_z,-Q_0); Q_mu*(Gamma_F-Gamma)^mu=0",
            "static_boundary": "bounded F implies transverse addition vanishes at Q=0",
            "required_ladder_handoff": "Gamma_R,on-shell with LSZ/residue and K_4,R -> Bethe-Salpeter resolvent on the same action/state"},
        "ontology": {"C": "collective coordinate, not q", "Phi": "effective response, not a kinetic particle identity", "R_gen": "derived trace excluded", "R_obs": "excluded"},
        "unit_lane": "natural_units", "units": {"Gamma_spatial": 1, "energy": 1, "kinetic_velocity_source_without_weight": 0, "transverse_F": 0},
        "derivation_class": "exact_tree_mapping_and_structural_no_go",
        "observable": "Microscopic-to-kinetic current-source interface boundary, not a transport coefficient",
        "data_role": "DERIVED_SYNTHETIC_DIAGNOSTIC", "source_rows": _serial(source_rows),
        "transverse_nonuniqueness_rows": _serial(transverse_rows), "static_rows": _serial(static_rows),
        "action_parameter_match": parameters, "legacy_contract_boundaries": boundaries,
        "checks": checks, "open_blockers": ["retarded_finite_k_three_point_spectral_continuation",
            "same_state_on_shell_residue_and_LSZ_matching", "microscopic_retarded_four_point_kernel",
            "collision_ladder_continuum_and_heat_current_matching"],
        "controlling_blocker": "state_matched_retarded_three_and_four_point_spectral_kernel_missing",
        "source_hashes": {p: sha(p) for p in paths},
        "evidence_artifacts": [{"path": p, "sha256": sha(p)} for p in prior_paths],
        "dependency_unlocked": ["explicit_action_configured_tree_current_source_handoff"],
        "full_core_unlock": False, "claim_promotion": False, "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Tree on-shell source match and transverse non-uniqueness no-go only; not a retarded microscopic vertex, Bethe-Salpeter kernel, continuum Kubo coefficient, SI transport, external validation, or Full Topic 13 closure."}
    artifact["report"] = {"MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE/CLOSED_AS_NO_GO",
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"], "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"], "STATUS": artifact["verification_status"],
        "WHAT_CHANGED": "Matched the tree on-shell current source, exposed default action drift, and proved the remaining transverse vertex is not identified by Ward/static evidence.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"], "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Derive a state-matched retarded finite-k three-point spectral kernel and microscopic four-point ladder kernel using the explicit bridged action parameters.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {k: artifact[k] for k in ("ontology", "unit_lane", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary")}
    entry.update({"equation_id": EQUATION_ID, "version": "1", "classification": "structural_interface_no_go",
        "relation_or_code_path": artifact["equation_or_mapping"], "standard_physics_counterpart": "LSZ/on-shell current source and transverse Ward ambiguity",
        "variables": {"Gamma": "1PI current vertex", "b_kin": "kinetic source", "q": "O(2) charge sign, not C"},
        "mathematical_role": "Microscopic-to-kinetic matching boundary", "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"], "source_or_origin": "Canonical action and existing finite-cutoff contracts",
        "assumptions": {"external_state": "tree on shell for the closed mapping", "transverse_no_go": "bounded arbitrary F at finite Q", "action_bridge": "all canonical coefficients explicitly matched"},
        "symmetry_and_conservation": "Ward contraction preserved for the full transverse family",
        "limiting_cases": ["tree on shell", "Q=0", "finite Q transverse addition"],
        "implementation_paths": [paths[0]], "verifier_paths": [paths[1]],
        "evidence_class": "INTERNAL_STRUCTURAL_DIAGNOSTIC", "proof_status": "TREE_HANDOFF_AND_TRANSVERSE_NONUNIQUENESS_CHECKED",
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": sha(OUT)}],
        "downstream_dependencies": [], "dependency_role": "narrowed_microscopic_transport_controller", "physical_dependency_unlock": False,
        "failure_mode": artifact["open_blockers"], "next_hardening_step": artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version": "uet-equation-registry-addendum-v1", "status": "CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json", "equation_entries": [entry],
        "full_core_unlock": False, "claim_promotion": False}, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["verification_status"], "checks": checks,
        "default_action_residuals": parameters["default_residuals"],
        "max_tree_source_residual": max(r["relative_residual"] for r in source_rows)}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
