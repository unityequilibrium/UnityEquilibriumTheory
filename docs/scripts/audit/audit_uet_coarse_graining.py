"""Verify lane-specific coarse graining and emit Wave 3 artifacts."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)
COARSE_GRAINING_SOURCE = canonical_existing_path(ROOT / ("docs/core/" + "uet_coarse_graining.py")).relative_to(ROOT).as_posix()

from docs.core.uet_coarse_graining import (
    CoarseGrainingRecord, coarse_grain, coarse_graining_consistency,
    coarse_graining_contract, refine_coarse_graining, scale_dependence_audit,
)

ARTIFACTS = CANONICAL_ARTIFACT_ROOT


def _record(lane: str, cells: int) -> CoarseGrainingRecord:
    types = {"phase": "microscopic_order_field", "charge": "coarse_o2_noether_charge_density", "density": "si_mass_density_field", "telegraph": "finite_cone_collective_field"}
    units = {"phase": "normalized", "charge": "natural_to_normalized", "density": "si_mass_density", "telegraph": "normalized"}
    return CoarseGrainingRecord(
        lane_id=lane, microscopic_state_type=types[lane],
        kernel="uniform_block_average_v1", reference_frame="declared_rest_frame",
        spatial_scale=1.0 / cells, temporal_scale=0.1, boundary_rule="periodic",
        unit_lane=units[lane], parameter_provenance="preregistered_audit_fixture",
        information_lost=("within_cell_fluctuations", "microscopic_labels"),
        observable_target=f"{lane}_lane_candidate_observable", output_cells=cells,
    )


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    field = np.linspace(0.25, 2.0, 16)
    lanes = ("phase", "charge", "density", "telegraph")
    results = {lane: coarse_grain(field, _record(lane, 4)) for lane in lanes}
    consistency = {
        lane: coarse_graining_consistency(refine_coarse_graining(
            field, tuple(_record(lane, cells) for cells in (2, 4, 8, 16))))
        for lane in lanes
    }
    left = np.array([0., 2., 2., 4., 4., 6., 6., 8.])
    right = np.array([1., 1., 3., 3., 5., 5., 7., 7.])
    many_error = float(np.max(np.abs(
        coarse_grain(left, _record("phase", 4)).C
        - coarse_grain(right, _record("phase", 4)).C)))
    scale = scale_dependence_audit({
        1.0: {"a": 1.0, "b": 1.0, "kappa": 0.5, "g": 0.2},
        2.0: {"a": 1.2, "b": 0.9, "kappa": 0.4, "g": 0.18},
        4.0: {"a": 1.3, "b": 0.85, "kappa": 0.35, "g": 0.17},
    })
    metrics = {
        "maximum_mean_preservation_error": max(r.diagnostics["mean_preservation_error"] for r in results.values()),
        "maximum_refinement_mean_drift": max(r.global_mean_drift for r in consistency.values()),
        "many_to_one_output_error": many_error,
        "lane_count": len(results),
    }
    thresholds = {"mean_preservation": 1e-12, "many_to_one_identity": 0.0}
    checks = {
        "all_four_lanes_explicit": metrics["lane_count"] == 4,
        "declared_mean_preserved": metrics["maximum_mean_preservation_error"] <= thresholds["mean_preservation"],
        "refinement_mean_preserved": metrics["maximum_refinement_mean_drift"] <= thresholds["mean_preservation"],
        "many_to_one_counterexample_passes": metrics["many_to_one_output_error"] == 0.0,
        "information_loss_declared": all(r.information_loss_declared for r in consistency.values()),
        "universal_identity_not_claimed": all(not r.universal_identity_claimed for r in consistency.values()),
        "scale_audit_not_rg_claim": scale.status == "DESCRIPTIVE_SCALE_AUDIT_ONLY",
    }
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0", "artifact": "coarse_graining_verification",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "research_status": "INTERNAL_DECLARED_FIELD_TO_COLLECTIVE_MAP_ONLY",
        "metrics": metrics, "thresholds": thresholds, "checks": checks,
        "lane_diagnostics": {lane: dict(r.diagnostics) for lane, r in results.items()},
        "scale_dependence": {"status": scale.status, "claim_boundary": scale.claim_boundary,
            "slopes": {name: list(values) for name, values in scale.logarithmic_slopes.items()}},
        "contract": coarse_graining_contract(),
        "claim_boundary": "deterministic lane-specific averaging from a declared lower-level field; not microscopic derivation, RG flow, SI observable closure, or universal C identity",
    }
    formula = {
        "schema_version": "1.0", "artifact": "coarse_graining_formula_audit",
        "generated_at": now, "status": "WARN",
        "relations": [
            {"formula_id": "UET-CG-BLOCK-001", "relation": "C_l=(block_average[X_l]-C_ref)/C_scale", "derivation_class": "declared coarse-graining operator", "unit_lane": "lane_specific", "proof_status": "mean preservation and many-to-one behavior verified", "code_path": COARSE_GRAINING_SOURCE},
            {"formula_id": "UET-CG-SCALE-002", "relation": "Delta parameter / Delta log(scale)", "derivation_class": "descriptive finite-difference audit", "unit_lane": "parameter_specific", "proof_status": "not an RG beta function", "code_path": COARSE_GRAINING_SOURCE},
        ],
        "open_items": ["microscopic dynamics to declared lower-level field", "covariant averaging and frame transport", "RG beta functions", "lane-specific dimensional observable calibration"],
        "claim_ceiling": "candidate declared-field coarse-graining contract",
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave3_gate",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "coarse_graining_status": "PASS_DECLARED_FIELD_TO_COLLECTIVE_COORDINATE_ONLY" if passed else "BLOCKED",
        "upstream_gate": "uet_main_theory_wave2_gate.json", "checks": checks,
        "controlling_blocker": "open_system_sk_kms_memory_not_derived" if passed else "lane_specific_coarse_graining_internal_failure",
        "claim_promotion": False,
        "next_controller": "derive a provenance-bearing linear open-system response with KMS, noise positivity, entropy accounting, and physical memory distinct from trace",
    }
    addendum = {
        "schema_version": "1.0", "artifact": "uet_equation_correspondence_registry_coarse_graining_addendum",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [{
            "equation_id": "uet.main_theory.coarse_graining", "version": "lane-coarse-graining-v1",
            "classification": "constitutive_lane_specific_equation", "relation_or_code_path": COARSE_GRAINING_SOURCE,
            "variables": {"X_lane": "declared lower-level lane field", "C_lane": "lane-specific collective coordinate", "ell": "phase, charge, density, or telegraph"},
            "mathematical_role": "many-to-one averaging and normalization map",
            "standard_physics_counterpart": "block-spin, volume-average, charge-density, and continuum coarse graining",
            "observable_mapping": {"status": "PARTIAL", "reason": "targets declared but material/catalog calibration remains open"},
            "unit_lane": "lane_specific", "parameter_dimensions": "recorded per lane; C may be normalized",
            "source_or_origin": "UET foundation Wave 3 constitutive contract",
            "assumptions": ["uniform block averaging v1", "declared frame and boundary", "many-to-one information loss", "no universal identity among C lanes"],
            "symmetry_and_conservation": "global mean preserved for equal-volume blocks",
            "limiting_cases": ["single-sample cell reproduces the lower-level field up to affine normalization", "coarser blocks erase within-cell fluctuations"],
            "implementation_paths": [COARSE_GRAINING_SOURCE],
            "verifier_paths": ["docs/scripts/audit/audit_uet_coarse_graining.py", "docs/core/07_artifacts/correspondence/coarse_graining_verification.json", "docs/core/test/test_uet_coarse_graining.py"],
            "evidence_class": "INTERNAL_FORMAL", "proof_status": "operator consistency verified; microscopic and observable closure open",
            "downstream_dependencies": ["uet.main_theory.covariant_parent", "uet.main_theory.open_system", "uet.main_theory.observables"],
            "claim_boundary": "lane-specific candidate coarse coordinate; C is not mass, charge, or order universally",
            "failure_mode": "mapping assumes desired observable or silently identifies distinct lane coordinates",
            "next_hardening_step": "derive open-system memory and calibrate one dimensional observable lane",
        }],
    }
    return verification, formula, gate, addendum


def main() -> int:
    names = ("coarse_graining_verification.json", "coarse_graining_formula_audit.json", "uet_main_theory_wave3_gate.json", "uet_equation_correspondence_registry_coarse_graining_addendum.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        path = canonical_artifact_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gate = outputs["uet_main_theory_wave3_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"coarse_graining_status={gate['coarse_graining_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
