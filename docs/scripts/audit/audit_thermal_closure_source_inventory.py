"""Regenerate the thermal closure cross-lane inventory from local sources."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_closure_source_inventory.json"

SOURCE_SPECS = [
    {
        "id": "pt_011_normalized_a_T_comparator",
        "relation": "a_C(T) = a_0 * (T - T_c) / T_c",
        "source_paths": [
            "docs/topics/0.11_Phase_Transitions/Code/simulate_uet_scaling.py",
            "docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Scaling.py",
        ],
        "native_variable": "C as phase/order parameter",
        "unit_lane": "normalized",
        "derivation_class": "standard Ginzburg-Landau/Cahn-Hilliard comparator in synthetic lane",
        "status": "COMPARATOR_ONLY",
        "can_define_a_Phi_T": False,
        "reason": "No accepted correspondence maps the C/order-parameter lane to the matter-space Phi response.",
        "markers": {
            "docs/topics/0.11_Phase_Transitions/Code/simulate_uet_scaling.py": ["a_T = 1.0 * (T - T_c) / T_c"],
            "docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Scaling.py": ["alpha_t = temperature - critical_temperature"],
        },
    },
    {
        "id": "o2_finite_density_eos",
        "relation": "tree-level finite-density O(2) equilibrium EOS",
        "source_paths": ["docs/core/02_equations/o2/uet_o2_finite_density_eos.py"],
        "native_variable": "signed global O(2) Noether charge density",
        "unit_lane": "natural",
        "derivation_class": "tree-level equilibrium derivation",
        "status": "FINITE_TEMPERATURE_LAYER_NOT_DERIVED",
        "can_define_a_Phi_T": False,
        "reason": "The contract explicitly marks the finite-temperature normal component as NOT_DERIVED.",
        "markers": {
            "docs/core/02_equations/o2/uet_o2_finite_density_eos.py": [
                '"finite_temperature_normal_component": "NOT_DERIVED"',
                '"transport_coefficients": "NOT_DERIVED_FROM_CONSERVATIVE_ACTION"',
            ]
        },
    },
    {
        "id": "topic_013_temperature_proxy",
        "relation": "T_proxy = 1 / ln(1 + N/E)",
        "source_paths": [
            "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md",
            "docs/topics/0.13_Thermodynamic_Bridge/Code/01_Engine/Engine_Thermodynamics.py",
        ],
        "native_variable": "topic entropy-proxy variables E and N",
        "unit_lane": "dimensionless",
        "derivation_class": "derivative of topic-local entropy proxy",
        "status": "PROXY_ONLY",
        "can_define_a_Phi_T": False,
        "reason": "No accepted map connects E,N proxy variables to Phi or TTG quasi-temperature.",
        "markers": {
            "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md": ["T13-002"],
            "docs/topics/0.13_Thermodynamic_Bridge/Code/01_Engine/Engine_Thermodynamics.py": ["def compute_temperature"],
        },
    },
    {
        "id": "matter_space_candidate_a_Phi_T",
        "relation": "a_Phi(T) is required by the conditional local-equilibrium map",
        "source_paths": ["docs/topics/0.13_Thermodynamic_Bridge/THERMAL_CLOSURE_DERIVATION_AUDIT.md"],
        "native_variable": "Phi as effective space-response variable",
        "unit_lane": "not closed",
        "derivation_class": "conditional closure",
        "status": "OPEN",
        "can_define_a_Phi_T": True,
        "reason": "Requires an explicit temperature-dependent functional, dimensional scale, and provenance not obtained from target data.",
        "markers": {
            "docs/topics/0.13_Thermodynamic_Bridge/THERMAL_CLOSURE_DERIVATION_AUDIT.md": [
                "dimensional free-energy-density scale",
                "No `alpha_Phi_K` value is fitted",
            ]
        },
    },
]


def read_source(relative_path: str) -> tuple[str, str | None, bool]:
    path = ROOT / relative_path
    if not path.exists():
        return "", None, False
    payload = path.read_bytes()
    return payload.decode("utf-8"), hashlib.sha256(payload).hexdigest(), True


def build_record(spec: dict[str, object]) -> dict[str, object]:
    marker_map = spec["markers"]
    source_rows = []
    for source_path in spec["source_paths"]:
        text, digest, exists = read_source(source_path)
        markers = marker_map.get(source_path, [])
        marker_results = {marker: marker in text for marker in markers}
        source_rows.append(
            {
                "path": source_path,
                "exists": exists,
                "sha256": digest,
                "required_markers": marker_results,
                "marker_gate": exists and all(marker_results.values()),
            }
        )
    return {
        key: value
        for key, value in spec.items()
        if key != "markers"
    } | {"source_rows": source_rows}


def main() -> None:
    records = [build_record(spec) for spec in SOURCE_SPECS]
    source_integrity = all(
        row["marker_gate"]
        for record in records
        for row in record["source_rows"]
    )
    artifact = {
        "schema_version": "thermal-closure-source-inventory-v1",
        "topic": "0.13_Thermodynamic_Bridge",
        "status": "ADJACENT_TEMPERATURE_LAWS_FOUND_CROSS_LANE_MAPPING_BLOCKED",
        "audit_status": "PASS_WITH_CROSS_LANE_BLOCKER" if source_integrity else "FAIL_SOURCE_INTEGRITY",
        "records": records,
        "cross_lane_gate": {
            "adjacent_temperature_relation_exists": True,
            "accepted_C_to_Phi_correspondence": False,
            "accepted_O2_finite_temperature_closure": False,
            "accepted_Phi_to_kelvin_map": False,
            "target_data_used_for_mapping": False,
            "2026_holdout_consumed": False,
        },
        "safe_reuse": {
            "normalized_a_T_as_explicit_comparator": True,
            "a_T_as_UET_derived_a_Phi_T": False,
            "kelvin_prediction": False,
        },
        "next_controller": "derive_or_source_lock_cross_lane_correspondence_for_Phi_and_temperature_before_dimensional_thermal_claims",
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit_status": artifact["audit_status"], "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()

