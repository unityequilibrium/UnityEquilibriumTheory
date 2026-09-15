"""Build a focused cross-topic correspondence matrix from the F0 inventory.

The full inventory contains every parsed topic formula row.  This matrix selects the
foundation/dependency rows that answer the two research questions directly:

1. Does the relation itself match a standard mathematical/physical counterpart?
2. Has UET actually derived that relation, or is it a baseline, comparator, heuristic,
   or blocked implementation?
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
INVENTORY_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"
COMPATIBILITY_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_compatibility_gate.json"
OUTPUT = ROOT / "docs/core/07_artifacts/gates/uet_foundation_correspondence_matrix.json"


SELECTED_ROWS: dict[str, dict[str, Any]] = {
    "T01-001": {
        "lane": "0.1 galaxy rotation",
        "standard_counterpart": "not yet specified; formula audit scaffold",
        "compatibility_status": "BLOCKED",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "NOT_TESTABLE",
        "reason": "topic formula audit contains calculation-path placeholders rather than explicit equations",
    },
    "FD-UET-MASTER-STEP": {
        "lane": "0.10 fluid benchmark",
        "standard_counterpart": "numerical field update / fluid comparator",
        "compatibility_status": "OPEN_UNIT_AND_CONSTITUTIVE_MAP",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "COMPARATOR_ONLY",
        "reason": "C/I normalized update is delegated to legacy master engine; physical mobility bridge is heuristic",
    },
    "PT-CH-EVOLUTION": {
        "lane": "0.11 phase transition",
        "standard_counterpart": "Cahn-Hilliard conserved gradient flow",
        "compatibility_status": "COMPATIBLE_CONDITIONAL",
        "uet_derivation_status": "INTERNAL_IMPLEMENTATION_CHECK_ONLY",
        "special_case_status": "STANDARD_CONSTITUTIVE_LIMIT",
        "reason": "the standard CH form is a benchmark structure; UET-specific coupling and material units remain open",
    },
    "T13-004": {
        "lane": "0.13 thermodynamic bridge",
        "standard_counterpart": "Landauer lower bound E_min=k_B*T*ln(2)",
        "compatibility_status": "COMPATIBLE_STANDARD_IDENTITY",
        "uet_derivation_status": "EXTERNAL_STANDARD_CONSTRAINT",
        "special_case_status": "NOT_A_UET_SPECIAL_CASE",
        "reason": "this is a standard dimensional lower bound and cannot derive normalized beta without a conversion lane",
    },
    "T13-010": {
        "lane": "0.13 heat-flux control",
        "standard_counterpart": "Cattaneo-Vernotte delayed heat flux",
        "compatibility_status": "SIMULATION_ONLY",
        "uet_derivation_status": "CONTROL_COMPARATOR",
        "special_case_status": "COMPARATOR_ONLY",
        "reason": "current q/T data are synthetic/proxy and conductivity is fitted in the control script",
    },
    "EW-01": {
        "lane": "0.6 electroweak",
        "standard_counterpart": "weak mixing angle / electroweak benchmark relation",
        "compatibility_status": "OPEN_HEURISTIC_BRIDGE",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "BENCHMARK_COMPATIBILITY_ONLY",
        "reason": "bridge_factor and symmetry seed are topic parameters, not a gauge-field derivation",
    },
    "NUPMNS-ANGLE-GEOM": {
        "lane": "0.7 neutrino",
        "standard_counterpart": "PMNS angle benchmark",
        "compatibility_status": "OPEN_HEURISTIC_BRIDGE",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "BENCHMARK_COMPATIBILITY_ONLY",
        "reason": "Cabibbo calibration pivot is a heuristic bridge; tri-generation dynamics is not derived",
    },
    "T17-KOIDE-001": {
        "lane": "0.17 mass generation",
        "standard_counterpart": "empirical Koide mass relation",
        "compatibility_status": "COMPATIBLE_EMPIRICAL_RELATION",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "CONSTRAINED_INFERENCE_ONLY",
        "reason": "matching a relation is not a derivation of the lepton mass mechanism",
    },
    "T05-SEMF-001": {
        "lane": "0.5 nuclear binding",
        "standard_counterpart": "semi-empirical mass formula baseline",
        "compatibility_status": "COMPATIBLE_BASELINE_WITH_OPEN_CORRECTION",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "STANDARD_BASELINE_ONLY",
        "reason": "the UET entropy/Yukawa corrections are heuristic and must be separated from SEMF performance",
    },
    "T05-QCD-010": {
        "lane": "0.5 QCD bridge",
        "standard_counterpart": "running alpha_s comparator",
        "compatibility_status": "BLOCKED_IMPLEMENTATION_ORIGIN",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "COMPARATOR_ONLY",
        "reason": "formula audit reports an alpha_s_uet_v2 data-shape bug and unresolved UET correction origin",
    },
    "GR19-NEWTON-ACCELERATION": {
        "lane": "0.19 gravity",
        "standard_counterpart": "Newtonian weak-field acceleration",
        "compatibility_status": "COMPATIBLE_STANDARD_BASELINE",
        "uet_derivation_status": "EXTERNAL_STANDARD_RELATION",
        "special_case_status": "BASELINE_ONLY",
        "reason": "using GM/r^2 is a baseline and does not derive G or Einstein equations",
    },
    "AT20-RYDBERG-WAVELENGTH": {
        "lane": "0.20 atomic",
        "standard_counterpart": "Rydberg hydrogen spectrum relation",
        "compatibility_status": "COMPATIBLE_STANDARD_BASELINE",
        "uet_derivation_status": "EXTERNAL_STANDARD_RELATION",
        "special_case_status": "BASELINE_ONLY",
        "reason": "the current verifier checks NIST/CODATA consistency, not a UET derivation of R_H",
    },
    "T23-005": {
        "lane": "0.23 unity scale",
        "standard_counterpart": "renormalization/running-coupling concept",
        "compatibility_status": "OPEN_HEURISTIC_BRIDGE",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "NOT_A_DERIVED_RG_FLOW",
        "reason": "listed kappa points are anchors/heuristics, not a beta function with uncertainty and prediction",
    },
    "T26-004": {
        "lane": "0.26 cosmic dynamic frame",
        "standard_counterpart": "force/velocity combination rule",
        "compatibility_status": "OPEN_HEURISTIC_BRIDGE",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "FIT_RULE_ONLY",
        "reason": "V_total=sqrt(V_newton^2+V_fluid^2) has no declared action or force-balance derivation",
    },
    "QN09-SINGLET-CORRELATION": {
        "lane": "0.9 quantum nonlocality",
        "standard_counterpart": "standard singlet-state quantum correlation",
        "compatibility_status": "COMPATIBLE_STANDARD_BASELINE",
        "uet_derivation_status": "EXTERNAL_STANDARD_RELATION",
        "special_case_status": "BASELINE_ONLY",
        "reason": "the QM relation is a comparator; the proposed topological UET explanation remains open",
    },
    "VAC-DARK-ENERGY-ANCHOR": {
        "lane": "0.12 vacuum/cosmology",
        "standard_counterpart": "observational dark-energy density scale",
        "compatibility_status": "OPEN_HEURISTIC_ANCHOR",
        "uet_derivation_status": "NOT_ESTABLISHED",
        "special_case_status": "OBSERVATIONAL_PRIOR_ONLY",
        "reason": "rho_vac=5.38e-10*beta is an anchor near an observed scale, not a Casimir or vacuum derivation",
    },
    "uet.legacy.master_potential": {
        "lane": "core legacy master equation",
        "standard_counterpart": "effective free-energy potential only if derivative pair closes",
        "compatibility_status": "CONTRADICTION",
        "uet_derivation_status": "LEGACY_IMPLEMENTATION_CONFLICT",
        "special_case_status": "NOT_A_VALID_VARIATIONAL_LIMIT",
        "reason": "coded potential and coded derivative have a measured residual of 1.025",
    },
    "uet.matter_space.candidate": {
        "lane": "core matter-space operator",
        "standard_counterpart": "coupled Landau-Ginzburg plus damped response",
        "compatibility_status": "COMPATIBLE_CONDITIONAL_BUT_BLOCKED_NUMERICALLY",
        "uet_derivation_status": "INTERNAL_NORMALIZED_CANDIDATE",
        "special_case_status": "g=0_DECOUPLED_AND_ADIABATIC_LIMITS_ONLY",
        "reason": "variational/ledger gates pass internally but causal pre-arrival leakage fails",
    },
    "uet.o2.finite_density_eos": {
        "lane": "core O(2) finite-density EOS",
        "standard_counterpart": "relativistic O(2) mean-field condensate",
        "compatibility_status": "COMPATIBLE_CONDITIONAL_NATURAL_UNITS",
        "uet_derivation_status": "TREE_LEVEL_DECLARED_O2_LANE",
        "special_case_status": "O2_LANE_ONLY_NOT_UNIVERSAL_C_MEANING",
        "reason": "EOS/Legendre/reciprocity gates pass, while transport/SI/full finite-temperature remain open",
    },
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def build_matrix() -> dict[str, Any]:
    inventory = load(INVENTORY_PATH)
    compatibility = load(COMPATIBILITY_PATH)
    records = {row["formula_id"]: row for row in inventory.get("records", [])}
    missing_rows = [key for key in SELECTED_ROWS if key not in records and not key.startswith("uet.")]
    if missing_rows:
        raise ValueError(f"selected inventory rows missing: {missing_rows}")

    matrix_rows: list[dict[str, Any]] = []
    for key, definition in SELECTED_ROWS.items():
        source_record = records.get(key)
        core_finding = next(
            (item for item in compatibility.get("findings", []) if item.get("equation_family") == key),
            None,
        )
        matrix_rows.append(
            {
                "matrix_id": key,
                **definition,
                "inventory_record": {
                    "topic_id": source_record.get("topic_id") if source_record else "core",
                    "source": source_record.get("source") if source_record else {"path": "docs/core/07_artifacts/gates/uet_foundation_compatibility_gate.json"},
                    "evidence_class": source_record.get("evidence_class") if source_record else None,
                    "proof_status": source_record.get("proof_status") if source_record else None,
                    "constant_origin": source_record.get("constant_origin") if source_record else None,
                },
                "core_compatibility_finding": core_finding,
            }
        )

    counts: dict[str, int] = {}
    for row in matrix_rows:
        status = row["compatibility_status"]
        counts[status] = counts.get(status, 0) + 1
    return {
        "schema_version": "1.0",
        "artifact": "uet_foundation_correspondence_matrix",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "matrix_status": "BLOCKED" if inventory.get("inventory_gate_status") == "BLOCKED" or compatibility.get("compatibility_status") == "BLOCKED" else "PASS_CONDITIONAL",
        "coverage": {
            "role": "focused critical-row correspondence matrix, not exhaustive code inventory",
            "selected_row_count": len(matrix_rows),
            "full_inventory_artifact": "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json",
            "inventory_gate_status": inventory.get("inventory_gate_status"),
            "compatibility_gate_status": compatibility.get("compatibility_status"),
        },
        "status_vocabulary": {
            "COMPATIBLE_STANDARD_BASELINE": "standard relation is internally recognizable, but not UET-derived",
            "COMPATIBLE_CONDITIONAL": "compatible only in the declared lane and evidence class",
            "OPEN_HEURISTIC_BRIDGE": "no completed UET derivation or full physical correspondence",
            "CONTRADICTION": "implementation violates its declared relation",
            "BLOCKED": "a foundation or numerical gate prevents promotion",
        },
        "summary": {"compatibility_status_counts": dict(sorted(counts.items()))},
        "rows": matrix_rows,
        "principle_implications": [
            "A standard counterpart is a baseline, not evidence that UET derived it.",
            "A benchmark-compatible heuristic is not a special-case proof.",
            "A special case requires an explicit limit and residual in the same ontology and unit lane.",
            "Open/scaffold rows cannot support downstream physical claims.",
        ],
        "next_controller": "repair core conflicts, complete 0.1 formula inventory, and manually close correspondence/observable maps for selected foundation rows",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the full matrix")
    parser.add_argument("--no-write", action="store_true", help="do not write artifact")
    args = parser.parse_args()
    try:
        matrix = build_matrix()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(matrix, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={matrix['audit_status']}")
        print(f"matrix_status={matrix['matrix_status']}")
        print(f"selected_row_count={matrix['coverage']['selected_row_count']}")
        print(f"compatibility_status_counts={matrix['summary']['compatibility_status_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
