"""Screen graphite literature for an independent axial-strain Raman row."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_axial_raman_source_screen.json"
RAMAN_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_raman_deformation_constraint_audit.json"
FULL_GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)

SOURCES = [
    {
        "source_id": "andrada_chacon_2017_hopg_quasi_uniaxial",
        "citation": "A. Andrada-Chacon, V. G. Baonza, and J. Sanchez-Benitez, Carbon 113, 205-211 (2017)",
        "doi": "10.1016/j.carbon.2016.11.058",
        "primary_locator": "https://doi.org/10.1016/j.carbon.2016.11.058",
        "material_and_state": "HOPG under quasi-uniaxial strain along c; moissanite-anvil-cell experiment",
        "measurement": "Simultaneous Raman spectroscopy and electrical resistance; relative D/D-prime defect-band intensities are the stated Raman measure.",
        "direct_axial_strain_measurement": False,
        "same_run_raman_and_independent_strain": False,
        "e2g_axial_frequency_rows": False,
        "source_grade_row_uncertainty": False,
        "numeric_payload_acquired": False,
        "disposition": "DEFECT_AND_RESISTANCE_COMPARATOR_NOT_E2G_STRAIN_CALIBRATION",
        "reason": "The publicly inspectable abstract describes D/D-prime defect-band intensity and resistance, not an independently measured epsilon_zz paired with E2g frequency rows; full numeric rows and uncertainties were not acquired.",
    },
    {
        "source_id": "wang_2019_graphite_ultrafast_xray_strain_wave",
        "citation": "X. Wang et al., Structural Dynamics 6, 024501 (2019)",
        "doi": "10.1063/1.5089291",
        "primary_locator": "https://doi.org/10.1063/1.5089291",
        "material_and_state": "Natural single-crystal graphite; 1 ps laser excitation above ablation threshold; transient c-axis compression",
        "measurement": "Time-resolved non-coplanar X-ray diffraction measures strain from reciprocal-space peak displacement; no Raman spectrum is co-measured.",
        "reported_aggregate_values": {
            "compressive_strain_at_100_ps": "10.0 +/- 0.5 percent",
            "compressive_strain_at_200_ps": "8.5 +/- 0.5 percent",
            "xray_pulse_duration": "100 ps",
        },
        "direct_axial_strain_measurement": True,
        "same_run_raman_and_independent_strain": False,
        "e2g_axial_frequency_rows": False,
        "source_grade_row_uncertainty": False,
        "numeric_payload_acquired": False,
        "disposition": "AXIAL_STRAIN_METHOD_COMPARATOR_OUT_OF_TARGET_REGIME",
        "reason": "The strain is measured directly, but the experiment is a high-amplitude, above-ablation, transient strain wave; it has no paired Raman E2g response and is not a low-strain TTG calibration row. The paper's temperature map is simulation-derived.",
    },
    {
        "source_id": "he_2020_graphite_shear_high_pressure_raman_xrd",
        "citation": "Y. He et al., Physical Review Letters 124, 065701 (2020)",
        "doi": "10.1103/PhysRevLett.124.065701",
        "primary_locator": "https://doi.org/10.1103/PhysRevLett.124.065701",
        "material_and_state": "Nanocrystalline graphite microspheres in a diamond-anvil cell under strong nonhydrostatic compression and nonuniform shear",
        "measurement": "Raman G-band evolution and X-ray phase observations are reported; indentation pressure is inferred from the high-frequency edge of the diamond Raman line.",
        "direct_axial_strain_measurement": False,
        "same_run_raman_and_independent_strain": False,
        "e2g_axial_frequency_rows": False,
        "source_grade_row_uncertainty": False,
        "numeric_payload_acquired": False,
        "disposition": "PHASE_TRANSFORMATION_COMPARATOR_NOT_LINEAR_STRAIN_ROW",
        "reason": "The stress field is highly nonuniform, the graphite strain tensor is not measured as a paired numeric row, and the G-band changes accompany high-pressure interlayer bonding/phase transformation rather than a matched small-strain elastic response.",
    },
]


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact():
    if not RAMAN_AUDIT.is_file() or not FULL_GATE.is_file():
        raise FileNotFoundError("required Topic 13 controller artifacts are missing")
    gate = json.loads(FULL_GATE.read_text(encoding="utf-8"))
    raman = json.loads(RAMAN_AUDIT.read_text(encoding="utf-8"))
    if raman.get("controlling_blocker") != "independent_strain_and_UET_mode_identification_missing":
        raise ValueError("the current Raman controller no longer matches this screen")

    required = [
        "same declared graphite specimen and preparation",
        "independently measured epsilon_zz (or a full strain tensor) paired with Raman",
        "identified E2g mode frequency and located source rows",
        "same temperature, phase, loading path, and observation time for strain and Raman",
        "predeclared elastic fit range and independent loading direction",
        "row-level uncertainty and covariance for strain and frequency",
        "permitted numeric payload, preprocessing record, and source hash",
        "no target-curve fitting and no holdout access",
    ]
    accepted = [
        source["source_id"]
        for source in SOURCES
        if source["direct_axial_strain_measurement"]
        and source["same_run_raman_and_independent_strain"]
        and source["e2g_axial_frequency_rows"]
        and source["source_grade_row_uncertainty"]
        and source["numeric_payload_acquired"]
    ]
    if accepted:
        raise ValueError("source screen must fail closed until every acceptance field is present")

    return {
        "schema_version": "t13-axial-raman-source-screen-v1",
        "artifact": "t13_axial_raman_source_screen",
        "generated_at": "2026-09-25",
        "status": "PASS_SCOPED_AXIAL_RAMAN_SOURCE_SCREEN_NO_ACCEPTED_ROW",
        "major_result": {
            "major_result_id": "T13_AXIAL_RAMAN_SOURCE_SCREEN",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "Three primary-literature routes were screened against a same-state independent axial-strain Raman acceptance contract; none supplies a qualifying row.",
            "equation_or_mapping": "D_c/x_mode = 2*dln(nu_E2g)/d epsilon_zz at fixed in-plane strain; no experimental value is emitted.",
            "units": {
                "epsilon_zz": "dimensionless",
                "nu_E2g": "cm^-1",
                "D_c/x_mode": "dimensionless",
            },
            "derivation_class": "primary-literature source-route screen; no UET derivation",
            "observable": "same-state graphite axial strain and E2g Raman frequency response",
            "data_role": "LITERATURE_ROUTE_SCREEN_NOT_CALIBRATION",
            "evidence_artifacts": [
                {
                    "path": str(RAMAN_AUDIT.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": _sha256(RAMAN_AUDIT),
                },
                {
                    "path": str(FULL_GATE.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": _sha256(FULL_GATE),
                },
            ],
            "verification_status": "PASS_SOURCE_SCREEN_ZERO_ACCEPTED_ROWS",
            "open_blockers": [
                "same_state_independent_axial_strain_raman_row_missing",
                "graphite_dimensional_Phi_anchor_or_independent_alpha_Phi_K_missing",
                "Ding_compatible_C_src_or_accepted_same_regime_reproduction_missing",
            ],
            "dependency_unlocked": "No physical dependency; literature screen and experimental-design boundary only.",
            "claim_boundary": "This closes only the bounded literature-screen question. It supplies no graphite deformation coefficient, alpha_Phi_K, C_src, TTG validation, Full Topic 13 closure, or global UET claim.",
        },
        "acceptance_contract": required,
        "sources": SOURCES,
        "decision": {
            "candidate_count": len(SOURCES),
            "accepted_row_count": len(accepted),
            "matched_state_axial_raman_source_found": False,
            "new_experiment_design": "Use one declared HOPG specimen with simultaneous Raman E2g acquisition and independent X-ray measurement of epsilon_zz (preferably the full strain tensor), source-calibrated temperature, declared loading path, and row-level covariance. Lock the elastic fit interval before acquisition; keep stress inference independent of the Raman frequency used as response.",
            "scope_relation": "This sublane is ancillary to graphite TTG validation. O(2)/He-4 remains separately CLOSED_FOR_CORE; graphite TTG remains open in the controlling gate.",
        },
        "integrity": {
            "raw_numeric_payload_acquired": False,
            "literature_aggregate_values_consulted": True,
            "alpha_fit_performed": False,
            "target_curve_used": False,
            "xie_2026_accessed": False,
            "holdout_accessed": False,
            "source_hashes_available": False,
            "claim_promotion": False,
            "full_core_unlock": False,
            "full_gate_status_unchanged": gate.get("status") == "BLOCKED_OPEN_T13_FULL_BRIDGE",
        },
        "controlling_blocker": "same_state_independent_axial_strain_raman_row_missing",
        "next_action": "Stop unchanged literature-gate reruns. Treat the missing row as an experiment/data-acquisition requirement; proceed only if permissioned numeric data or a same-specimen XRD-plus-Raman dataset becomes available. Continue graphite C_src and Phi-scale work as separate controllers.",
        "claim_boundary": "No experimental graphite E2g axial coefficient, no alpha_Phi_K, no Ding C_src, no TTG validation, no Full Topic 13 closure, and no global UET promotion.",
    }


def main():
    artifact = build_artifact()
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(artifact["status"])
    print("accepted_rows=" + str(artifact["decision"]["accepted_row_count"]))
    print("full_gate_status_unchanged=" + str(artifact["integrity"]["full_gate_status_unchanged"]))


if __name__ == "__main__":
    main()
