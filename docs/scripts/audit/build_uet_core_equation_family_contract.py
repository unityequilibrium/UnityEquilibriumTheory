"""Build the core equation-family contract from current code and verifier evidence."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CODE_SURFACE_PATH = ROOT / "docs/core/artifacts/uet_code_surface_inventory.json"
COMPATIBILITY_PATH = ROOT / "docs/core/artifacts/uet_foundation_compatibility_gate.json"
MATTER_VERIFY_PATH = ROOT / "docs/core/artifacts/matter_space_variational_verification.json"
GR_VERIFY_PATH = ROOT / "docs/core/artifacts/gr_closed_limit_verification.json"
O2_VERIFY_PATH = ROOT / "docs/core/artifacts/o2_finite_density_eos_verification.json"
O2_FORMULA_PATH = ROOT / "docs/core/artifacts/o2_eos_formula_audit.json"
TRACE_VERIFY_PATH = ROOT / "docs/core/artifacts/spacetime_trace_verification.json"
OUTPUT = ROOT / "docs/core/artifacts/uet_core_equation_family_contract.json"


def p(relative: str) -> Path:
    return ROOT / relative


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def family(
    family_id: str,
    name: str,
    paths: list[str],
    variables: dict[str, str],
    counterpart: str,
    unit_lane: str,
    derivation: str,
    math_status: str,
    special_case: str,
    claim_ceiling: str,
    evidence: list[str],
    next_gate: str,
    *,
    equation_family: bool = True,
    formula_ids: list[str] | None = None,
    verifier_paths: list[str] | None = None,
    organization_review_required: bool = False,
) -> dict[str, Any]:
    result = {
        "family_id": family_id,
        "name": name,
        "module_paths": paths,
        "equation_family": equation_family,
        "variables": variables,
        "standard_physics_counterpart": counterpart,
        "unit_lane": unit_lane,
        "derivation_class": derivation,
        "mathematical_compatibility_status": math_status,
        "old_theory_special_case_status": special_case,
        "claim_ceiling": claim_ceiling,
        "evidence_paths": evidence,
        "next_gate": next_gate,
    }
    if formula_ids is not None:
        result["formula_ids"] = list(formula_ids)
    if verifier_paths is not None:
        result["verifier_paths"] = list(verifier_paths)
    if organization_review_required:
        result["organization_review_required"] = True
    return result


FAMILIES = [
    family(
        "core.legacy_master",
        "Legacy master functional and dynamics",
        ["docs/core/uet_master_equation.py"],
        {"C": "legacy normalized state label", "I": "legacy information field label", "V": "legacy velocity/value tuple label", "beta": "normalized coupling"},
        "effective free-energy/gradient-flow model only after exact functional-derivative closure",
        "normalized_or_legacy_open",
        "legacy implementation with heuristic constitutive bridges",
        "CONTRADICTION_AND_CONFLICT",
        "NOT_ESTABLISHED",
        "legacy comparator only; no universal physical interpretation",
        ["docs/core/artifacts/uet_foundation_compatibility_gate.json", "docs/core/artifacts/master_equation_alignment_gate_v2.json"],
        "repair potential/derivative pair, information operator declaration, and beta unit surface",
    ),
    family(
        "core.matter_space",
        "Matter-space coupled state/response dynamics",
        ["docs/core/uet_matter_space.py", "docs/core/uet_spatial.py", "docs/core/uet_matter_space_causal.py", "docs/core/uet_matter_space_split.py", "docs/core/uet_matter_space_finite_cone.py", "docs/core/uet_matter_space_characteristic.py"],
        {"C": "lane-specific matter/order state", "Phi": "effective space-response variable", "Pi": "d_t Phi", "sigma": "derived dissipation", "R": "derived trace, no feedback"},
        "coupled Landau-Ginzburg functional plus conserved/nonconserved gradient flow and damped response",
        "normalized_v1",
        "candidate variational functional and constitutive dynamics",
        "INTERNAL_VARIATIONAL_GATES_PASS_CAUSAL_GATE_FAILS",
        "g=0/adiabatic/closed limits conditionally supported; physical standard limit not complete",
        "candidate normalized effective model; not SI or total-universe energy law",
        ["docs/core/artifacts/matter_space_variational_verification.json", "docs/core/artifacts/matter_space_dependency_gate.json"],
        "repair pre-arrival leakage and then define dimensional observable map",
    ),
    family(
        "core.matter_space_flux",
        "Conserved matter-space flux and causal response branch",
        [
            "docs/core/uet_matter_space_flux_telegraph.py",
            "docs/core/uet_matter_space_flux_phi.py",
        ],
        {
            "C": "conserved collective-coordinate field on the named flux lane",
            "J_C": "conserved face flux",
            "Phi": "effective response variable",
            "Pi": "discrete Phi response rate",
            "R_gen": "derived trace absent from physical dynamics",
        },
        "one-dimensional continuity equation with Maxwell-Cattaneo-like flux relaxation and a damped coupled response",
        "normalized_v1",
        "named constitutive flux branch with internal numerical energy-ledger verification; not a first-principles universal law",
        "INTERNAL_FLUX_BRANCH_GATES_PASS_ORIGINAL_KAPPA_C_GT_0_CLASS_BLOCKED",
        "kappa_C=0 named branch only; the original kappa_C>0 conserved-gradient causal class remains separate and blocked",
        "candidate normalized conserved flux/response comparator; not SI thermal closure, not a universal C ontology, and not global energy law",
        [
            "docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json",
            "docs/core/artifacts/matter_space_flux_phi_coupled_verification.json",
        ],
        "complete dimensional observable mapping and independently locked external comparison",
        formula_ids=[
            "uet.matter_space_flux.conservation",
            "uet.matter_space_flux.relaxation",
            "uet.matter_space_flux.phi_response",
            "uet.matter_space_flux.shared_energy_ledger",
        ],
        verifier_paths=[
            "docs/scripts/audit/audit_matter_space_conserved_flux_telegraph.py",
            "docs/scripts/audit/audit_matter_space_flux_phi_coupled.py",
            "docs/core/test/test_matter_space_conserved_flux_telegraph.py",
            "docs/core/test/test_matter_space_flux_phi_coupled.py",
        ],
        organization_review_required=True,
    ),
    family(
        "core.trace",
        "Causal derived history trace",
        ["docs/core/uet_trace.py"],
        {"R": "I_trace history observable", "G_ret": "retarded kernel", "sigma": "dissipation source"},
        "causal memory/convolution observable",
        "normalized_v1",
        "derived observable from physical dynamics, not an independent state",
        "INTERNAL_TRACE_COMPARATOR",
        "zero-source/zero-memory/static limits conditionally support a Markovian comparator",
        "diagnostic derived observable; no substance/energy-reservoir claim",
        ["docs/core/artifacts/spacetime_trace_verification.json", "docs/core/artifacts/trace_kernel_formula_audit.json"],
        "close compact-support and dimensional measurement operator",
        formula_ids=["uet.trace.derived_observable"],
        verifier_paths=[
            "docs/core/test/test_spacetime_trace.py",
            "docs/core/artifacts/spacetime_trace_verification.json",
        ],
        organization_review_required=True,
    ),
    family(
        "core.covariant_response",
        "Covariant response/GR parent evaluator",
        ["docs/core/uet_covariant_response.py", "docs/core/uet_covariant_matter.py", "docs/core/uet_covariant_balance.py", "docs/core/uet_covariant_nonclosed.py", "docs/core/uet_covariant_reduction.py"],
        {"g_mu_nu": "metric", "Psi_m": "matter fields", "Phi": "effective response scalar", "Q^nu": "exchange current", "epsilon_nc": "nesting coupling"},
        "covariant scalar/tensor response model with an Einstein/GR closed-response comparator",
        "natural_units_candidate",
        "candidate conservative covariant tensor/action formulas with local algebraic verification",
        "CONDITIONALLY_COMPATIBLE_NOT_FULL_GR",
        "epsilon_nc=0/ordered reference gives exact algebraic-local null contract only",
        "candidate covariant parent; not Einstein derivation or global-universe closure",
        ["docs/core/artifacts/gr_closed_limit_verification.json", "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"],
        "add field-equation, Bianchi/Noether, metric PDE and initial-value verification",
    ),
    family(
        "core.covariant_parent",
        "Integrated covariant conservative parent formula evaluator",
        ["docs/core/uet_covariant_parent.py"],
        {
            "g_mu_nu": "Lorentz metric",
            "chi_A": "global O(2) scalar matter doublet",
            "Phi": "candidate response scalar",
            "epsilon_nc": "closed/non-closed nesting parameter",
            "Q^nu": "reciprocal local exchange source",
        },
        "scalar-tensor effective action with global O(2) matter and local reciprocal exchange",
        "natural_only_v1",
        "candidate conservative action evaluator with locally checked variational identities",
        "INTERNAL_CONSERVATIVE_PARENT_IDENTITIES_PASS_CURVED_DYNAMICS_BLOCKED",
        "epsilon_nc=0 gives an algebraic/local Einstein-GR residual comparison only; it is not a full GR derivation",
        "candidate natural-unit conservative parent formula evaluator; not a metric PDE solver, open-system closure, or physical GR validation",
        [
            "docs/core/artifacts/covariant_parent_verification.json",
            "docs/core/artifacts/covariant_parent_formula_audit.json",
            "docs/core/artifacts/uet_main_theory_wave2_gate.json",
        ],
        "close lane-specific covariant coarse-graining, then curved 3+1 initial-value/constraint evolution and dimensional observables",
        formula_ids=["uet.main_theory.covariant_parent"],
        verifier_paths=[
            "docs/scripts/audit/audit_uet_covariant_parent.py",
            "docs/core/test/test_uet_covariant_parent.py",
        ],
        organization_review_required=True,
    ),
    family(
        "core.covariant_diffusion",
        "Covariant diffusion/current constitutive lane",
        ["docs/core/uet_covariant_diffusion.py"],
        {"N_mu": "matter current", "u_mu": "frame velocity", "D": "diffusion coefficient", "tau": "relaxation time", "mu": "chemical potential"},
        "relativistic diffusion and Maxwell-Cattaneo constitutive transport",
        "natural_or_normalized_control",
        "constitutive ansatz with covariant projection and causal control gates",
        "CONDITIONAL_CONSTITUTIVE_NOT_MICROSCOPIC",
        "parabolic/Markovian limit is a comparator, not a derivation of microscopic transport",
        "candidate constitutive transport; coefficient provenance and SI map remain open",
        ["docs/core/artifacts/covariant_diffusion_formula_audit.json", "docs/core/artifacts/covariant_diffusive_current_verification.json"],
        "close coefficient origin, Kubo relation and dimensional observable lane",
        formula_ids=[
            "uet.covariant_diffusion.frame_decomposition",
            "uet.covariant_diffusion.finite_relaxation_current",
            "uet.covariant_diffusion.energy_identity",
            "uet.covariant_diffusion.adiabatic_model_b_limit",
        ],
        verifier_paths=[
            "docs/scripts/audit/audit_uet_gr_covariant_diffusion.py",
            "docs/core/test/test_covariant_diffusion.py",
            "docs/core/test/test_gr_covariant_diffusion_alignment.py",
        ],
        organization_review_required=True,
    ),
    family(
        "core.hyperbolic_phase",
        "Hyperbolic phase-field/telegraph comparator",
        ["docs/core/uet_hyperbolic_phase_field.py", "docs/core/uet_hyperbolic_phase_field_bridge.py"],
        {"C": "normalized phase/order field", "tau": "relaxation time", "kappa": "gradient coefficient", "v": "normalized characteristic speed"},
        "telegraph/hyperbolic phase-field equation and causal propagation comparator",
        "normalized_external_comparator",
        "external fixed-form comparator; UET derivation not closed",
        "COMPATIBLE_COMPARATOR_ONLY",
        "fixed light-cone/causal feasibility limit is analytic comparator, not UET special-case proof",
        "simulation/comparator only",
        ["docs/core/artifacts/hyperbolic_phase_field_formula_audit.json", "docs/core/artifacts/hyperbolic_phase_field_covariant_mapping_gate.json"],
        "derive from declared action or keep permanently as external comparator",
    ),
    family(
        "core.o2_superfluid",
        "Finite-density O(2) EOS and ideal superfluid transport",
        ["docs/core/uet_o2_finite_density_eos.py", "docs/core/uet_covariant_superfluid_transport.py"],
        {"n": "signed O(2) Noether charge density", "mu": "chemical potential", "A": "condensate amplitude", "Phi": "response input", "xi_mu": "phase gradient"},
        "relativistic finite-density O(2) mean-field condensate and T=0 ideal superfluid constitutive sector",
        "natural_units",
        "tree-level EOS/ideal constitutive derivation; dissipative coefficients require Kubo matching",
        "CONDITIONALLY_COMPATIBLE_NATURAL_UNITS",
        "O(2) lane is a controlled realization; does not establish universal C=mass or legacy double-well reduction",
        "tree-level EOS and ideal transport only; physical Kubo/SI/full finite-T blocked",
        ["docs/core/artifacts/o2_finite_density_eos_verification.json", "docs/core/artifacts/o2_eos_formula_audit.json", "docs/core/artifacts/covariant_superfluid_transport_contract.json"],
        "complete Kubo provenance, finite-T normal component and SI/observable map",
    ),
    family(
        "core.noether_mapping",
        "Noether phase field and coarse-state map",
        ["docs/core/uet_noether.py", "docs/core/uet_noether_phase_field_map.py"],
        {"chi": "complex O(2) matter field", "theta": "phase", "N_mu": "Noether current", "C": "coarse hydrodynamic coordinate"},
        "global O(2)/U(1) Noether current and hydrodynamic state-coordinate map",
        "natural_parent_plus_normalized_map",
        "action-level Noether relation plus constitutive/coarse-graining map",
        "CONDITIONALLY_COMPATIBLE_MANY_TO_ONE_MAP",
        "Noether charge map does not prove legacy C field or microscopic Cahn-Hilliard dissipation",
        "mapping/diagnostic only; no universal C ontology",
        [
            "docs/core/artifacts/noether_phase_field_map_formula_audit.json",
            "docs/core/artifacts/noether_phase_field_state_map_verification.json",
            "docs/core/artifacts/noether_phase_field_dependency_gate.json",
        ],
        "derive coarse-graining/gradient EFT and prove observable map without many-to-one ambiguity",
        formula_ids=[
            "uet.noether_mapping.frame_projected_charge_density",
            "uet.noether_mapping.affine_phase_coordinate",
            "uet.noether_mapping.normalized_current_coordinate",
            "uet.noether_mapping.continuity_residual_scaling",
            "uet.noether_mapping.o2_polar_current",
            "uet.noether_mapping.symmetric_double_well_conjugacy",
            "uet.noether_mapping.normalized_constitutive_scales",
        ],
        verifier_paths=[
            "docs/scripts/audit/audit_uet_noether_phase_field_map.py",
            "docs/core/test/test_noether_phase_field_map.py",
            "docs/core/test/test_gr_noether_phase_field_map_alignment.py",
            "docs/core/test/test_noether_phase_field_topic_0_11_dependency.py",
        ],
        organization_review_required=True,
    ),
    family(
        "core.lorentz",
        "Lorentz transformation/causal utilities",
        ["docs/core/uet_lorentz.py"],
        {"x_mu": "spacetime coordinate", "Lambda": "Lorentz transform", "c": "normalized light speed"},
        "special-relativistic Lorentz transformation and causal cone",
        "normalized_or_natural",
        "mathematical utility/transform tests, not a covariant legacy dynamics derivation",
        "UTILITY_COMPATIBILITY_NOT_THEORY_PROOF",
        "Lorentz transform utility can support a lane but does not establish Lorentz invariance of all operators",
        "support utility; no global invariance claim",
        ["docs/core/test/test_lorentz_noether_comprehensive.py", "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"],
        "connect each physical operator to a covariant action and transformation residual",
    ),
    family(
        "core.parameter_contract",
        "Parameter/constants and unit bridge",
        ["docs/core/uet_parameters.py"],
        {"beta": "normalized coupling in core lane", "kappa": "lane-dependent coefficient", "SI constants": "physical constants with provenance"},
        "dimensional parameter registry and external-constant provenance",
        "mixed_normalized_natural_SI",
        "parameter policy/heuristic bridge, not a physical equation derivation",
        "UNIT_SEMANTICS_OPEN",
        "Landauer SI lower bound and normalized beta are not the same quantity",
        "parameter support only; no beta-as-energy claim",
        ["docs/core/artifacts/uet_foundation_compatibility_gate.json", "docs/core/uet_parameters.py"],
        "split normalized/SI APIs and close provenance for every physical coefficient",
        equation_family=False,
    ),
    family(
        "core.observable_contract",
        "Observable and measurement helpers",
        ["docs/core/uet_observables.py"],
        {"y_pred": "measurement operator output", "C/Phi/Pi/R": "candidate inputs"},
        "measurement operator mapping model state to a measured quantity",
        "lane_specific_open",
        "observable definitions/helpers; physical measurement map incomplete",
        "OBSERVABLE_MAP_OPEN",
        "without observable map no real-data fit can test the theory",
        "diagnostic/internal only",
        ["docs/core/artifacts/uet_foundation_dependency_gate.json", "docs/core/UET_FOUNDATION_COMPATIBILITY_AUDIT.md"],
        "define O[C,Phi,Pi,R], units, uncertainty, resolution and nuisance parameters",
        equation_family=False,
    ),
    family(
        "core.support_and_adapters",
        "Solvers, adapters, validation, proof and visualization support",
        [
            "docs/core/__init__.py", "docs/core/uet_base_solver.py", "docs/core/uet_lite_engine.py", "docs/core/uet_matrix_engine.py",
            "docs/core/uet_data_orchestrator.py", "docs/core/uet_glass_box.py", "docs/core/scientific_validation.py",
            "docs/core/uet_bug_hunter.py", "docs/core/truth_auditor.py", "docs/core/reproducibility.py", "docs/core/uet_references.py",
            "docs/core/uet_viz.py", "docs/core/02_Proof/Proof_00_Master_Balance.py", "docs/core/mass_density_correspondence.py", "docs/core/matter_interaction_forward.py", "docs/core/persistence_energy_diagnostic.py", "docs/core/relational_two_body_baseline.py", "docs/core/resource_selection_thermal_bridge.py", "docs/core/thermal_observable_bridge.py", "docs/core/thermal_source_observable_map.py", "docs/core/uet_impact_effect.py", "docs/core/uet_resource_selection.py", "docs/core/mass_density_3d.py", "docs/core/mass_density_amplitude.py", "docs/core/mass_density_dimensional.py", "docs/core/photon_observer_baseline.py", "docs/core/uet_matter_space_observable.py",
            "docs/core/resource_selection_physical_cost_map.py",
        ],
        {},
        "numerical implementation and audit support, not a unified physical equation",
        "not_applicable",
        "adapter/numerical/proof-support code; each formula-bearing path must link to a family",
        "NOT_AN_EQUATION_FAMILY",
        "not applicable until a support path is promoted into a declared equation family",
        "no independent physics claim",
        ["docs/core/artifacts/uet_code_surface_inventory.json"],
        "link formula-bearing support paths to an owning equation family or quarantine as legacy",
        equation_family=False,
    ),
]


def build_contract() -> dict[str, Any]:
    code_surface = load(CODE_SURFACE_PATH)
    compatibility = load(COMPATIBILITY_PATH)
    matter = load(MATTER_VERIFY_PATH)
    gr = load(GR_VERIFY_PATH)
    o2 = load(O2_VERIFY_PATH)
    o2_formula = load(O2_FORMULA_PATH)
    trace = load(TRACE_VERIFY_PATH)
    code_records = code_surface.get("records", [])
    count_by_path: dict[str, int] = {}
    for record in code_records:
        path = record["path"]
        count_by_path[path] = count_by_path.get(path, 0) + 1

    all_core_paths = set(count_by_path)
    assigned_paths = {path for item in FAMILIES for path in item["module_paths"]}
    missing_paths = sorted(all_core_paths - assigned_paths)
    nonexistent_paths = sorted(path for path in assigned_paths if not p(path).exists())
    enriched: list[dict[str, Any]] = []
    for item in FAMILIES:
        current = dict(item)
        current["candidate_surface_count"] = sum(count_by_path.get(path, 0) for path in item["module_paths"])
        current["module_paths_exist"] = all(p(path).exists() for path in item["module_paths"])
        enriched.append(current)

    hard_block = bool(missing_paths or nonexistent_paths or code_surface.get("inventory_gate_status") == "BLOCKED" or compatibility.get("compatibility_status") == "BLOCKED")
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_equation_family_contract",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "contract_status": "BLOCKED" if hard_block else "PASS_CONDITIONAL",
        "controlling_blocker": "core_code_surface_classification_or_upstream_compatibility_incomplete" if hard_block else None,
        "coverage": {
            "core_code_surface_file_count": len(all_core_paths),
            "assigned_module_path_count": len(assigned_paths),
            "missing_core_paths": missing_paths,
            "nonexistent_declared_paths": nonexistent_paths,
            "equation_family_count": sum(1 for item in enriched if item["equation_family"]),
            "support_or_contract_family_count": sum(1 for item in enriched if not item["equation_family"]),
        },
        "upstream_evidence_snapshot": {
            "compatibility_status": compatibility.get("compatibility_status"),
            "matter_space_status": matter.get("status"),
            "matter_space_blocker": matter.get("controlling_blocker"),
            "gr_closed_limit_status": gr.get("status"),
            "o2_eos_status": o2.get("audit_status", o2.get("status")),
            "o2_formula_status": o2_formula.get("status"),
            "trace_status": trace.get("status"),
        },
        "families": enriched,
        "principles_locked_by_contract": [
            "No universal physical meaning is assigned to C outside a declared lane.",
            "A standard counterpart is not a UET derivation.",
            "A special case requires an explicit limit, same ontology/units, and residual verification.",
            "Support code cannot create a physical claim without an owning equation family.",
            "R/I_trace remains derived and non-backreacting in the new mode.",
        ],
        "next_controller": "classify missing code paths and close observable/unit maps for each equation family before real-data claims",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        contract = build_contract()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(contract, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={contract['audit_status']}")
        print(f"contract_status={contract['contract_status']}")
        print(f"equation_family_count={contract['coverage']['equation_family_count']}")
        print(f"missing_core_paths={len(contract['coverage']['missing_core_paths'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
