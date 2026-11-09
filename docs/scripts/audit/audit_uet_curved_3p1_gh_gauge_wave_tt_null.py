"""Verify the periodic GH harmonic gauge wave is null in the TT response lane."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path


_gh_evolution = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_evolution"
)
_gw_response = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gw_detector_response"
)

SOURCE_RECORD = ROOT / "docs/data/external/gr_3p1/gw_interferometer_response/wave_extraction_route_screen.json"
GH_EVOLUTION = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_evolution.py"
GH_SYSTEM = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
GW_RESPONSE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gw_detector_response.py"
TEST = ROOT / "docs/core/05_tests/regression/root/test_uet_curved_3p1_gh_gauge_wave_tt_null.py"
AUDIT_SCRIPT = Path(__file__).resolve()
AUDIT = canonical_artifact_path(
    "curved_3p1_gh_gauge_wave_tt_null_audit.json", "verification"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict:
    shape = (12, 5, 5)
    domain_lengths = (1.0, 1.0, 1.0)
    amplitude = 0.05
    target_time = 0.02
    propagation = np.array([1.0, 0.0, 0.0])
    arm_u = np.array([0.0, 1.0, 0.0])
    arm_v = np.array([0.0, 0.0, 1.0])
    initial, gauge_source, gauge_source_derivative, spacing = (
        _gh_evolution.harmonic_gauge_wave_state(
            shape, domain_lengths, amplitude=amplitude
        )
    )
    evolved = _gh_evolution.evolve_periodic_vacuum_gh(
        initial,
        gauge_source,
        gauge_source_derivative,
        spacing,
        target_time,
    )

    raw_spatial_mode = (
        evolved.state.spacetime_metric[..., 1:, 1:] - np.eye(3)
    )
    tt_modes = np.empty_like(raw_spatial_mode, dtype=np.complex128)
    detector_strains = np.empty(shape, dtype=np.complex128)
    for index in np.ndindex(shape):
        tt_modes[index] = _gw_response.project_spatial_metric_mode_to_tt(
            raw_spatial_mode[index], propagation
        )
        detector_strains[index] = _gw_response.equal_arm_interferometer_response(
            tt_modes[index],
            propagation,
            arm_u,
            arm_v,
            frequency_hz=0.0,
            arm_length_m=1.0,
        ).strain_response

    raw_metric_linf = float(np.max(np.abs(raw_spatial_mode)))
    tt_projection_linf = float(np.max(np.abs(tt_modes)))
    detector_strain_linf = float(np.max(np.abs(detector_strains)))
    run_contract = evolved.run_contract
    metric_history_fields = {"state_history", "metric_snapshots", "metric_history"}
    result_fields = set(evolved.__dataclass_fields__)
    has_metric_history = bool(metric_history_fields & result_fields)

    source_record = json.loads(SOURCE_RECORD.read_text(encoding="utf-8"))
    source_paths = (
        SOURCE_RECORD,
        GH_EVOLUTION,
        GH_SYSTEM,
        GW_RESPONSE,
        TEST,
        AUDIT_SCRIPT,
    )
    checks = {
        "periodic_gh_gauge_wave_reaches_declared_final_time": abs(
            evolved.final_time - target_time
        )
        <= 1e-14,
        "gauge_wave_has_nonzero_raw_metric_perturbation": raw_metric_linf > 0.01,
        "evolved_gauge_wave_is_null_after_tt_projection": tt_projection_linf
        <= 1e-14,
        "evolved_gauge_wave_has_zero_ideal_detector_strain": detector_strain_linf
        <= 1e-14,
        "gh_control_did_not_project_filter_clip_or_fit": (
            run_contract.get("constraint_projection") is False
            and run_contract.get("numerical_filtering") is False
            and run_contract.get("field_clipping") is False
            and run_contract.get("parameter_fitting") is False
        ),
        "literature_route_screen_and_code_hashes_are_available": all(
            path.is_file() for path in source_paths
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path) for path in source_paths
    }
    status = (
        "PASS_GH_HARMONIC_GAUGE_WAVE_TT_NULL_CONTROL"
        if all(checks.values())
        else "FAIL_GH_HARMONIC_GAUGE_WAVE_TT_NULL_CONTROL"
    )
    route_fields = [
        {
            "source_id": reference["source_id"],
            "url": reference["url"],
            "locators": reference["locators"],
            "route_requirements": reference["route_requirements"],
            "screen_finding": reference["screen_finding"],
        }
        for reference in source_record["references"]
    ]
    result = {
        "schema_version": "uet-curved-3p1-gh-gauge-wave-tt-null-v1",
        "artifact": "curved_3p1_gh_gauge_wave_tt_null_audit",
        "diagnostic_id": "uet.main_theory.curved_3p1.gh_gauge_wave_tt_null_control",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_promotion": False,
        "checks": checks,
        "metrics": {
            "raw_metric_perturbation_linf": raw_metric_linf,
            "tt_projection_linf": tt_projection_linf,
            "detector_strain_linf": detector_strain_linf,
            "grid_shape": list(shape),
            "input_wave_amplitude": amplitude,
            "final_time_coordinate_units": evolved.final_time,
            "integration_steps": evolved.step_count,
            "tt_projection_direction": propagation.tolist(),
            "detector_frequency_hz": 0.0,
            "arm_length_m": 1.0,
        },
        "gh_time_series_output": {
            "result_fields": sorted(result_fields),
            "metric_snapshot_history_available": has_metric_history,
            "constraint_diagnostic_sample_count": len(evolved.diagnostics),
            "interpretation": "the current integrator returns a final metric state and scalar constraint diagnostics, not a metric time history or extracted waveform",
        },
        "mapping": {
            "gh_state_metric": "psi_ab(t,x) from the existing periodic vacuum GH integrator",
            "spatial_perturbation": "h_ij = gamma_ij - delta_ij",
            "tt_projection": "h_TT = P h P - 1/2 P tr(P h P), P_ij=delta_ij-n_i n_j",
            "negative_control_result": "the exact harmonic gauge wave varies only in the propagation-direction metric component; h_TT=0 and the ideal detector strain is zero",
        },
        "input_identity": {
            "control": "existing periodic vacuum harmonic gauge-wave manufactured solution",
            "detector_data_consumed": False,
            "holdout_consumed": False,
            "parameter_fit": False,
            "raw_source_rows_consumed": 0,
        },
        "source_hashes": source_hashes,
        "literature_route_screen": route_fields,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_GAUGE_WAVE_TT_NULL_CONTROL",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "the existing evolved periodic harmonic gauge-wave control has nonzero raw spatial metric perturbation but zero TT projection",
                "the bounded ideal detector measurement operator reports zero strain for that gauge control",
                "the test exercises actual GH final-state output rather than only a hand-constructed longitudinal tensor",
            ],
            "equation_or_mapping": {
                "h_ij": "gamma_ij - delta_ij",
                "h_TT_ij": "P_i^k P_j^l h_kl - 1/2 P_ij P^kl h_kl",
                "negative_control": "h_TT_ij = 0 => h_D = D_ij h_TT_ij = 0",
            },
            "units": "GH coordinate units remain unspecified; metric perturbation and strain are dimensionless; f=0 and L=1 m are only the exact transfer-limit control inputs",
            "derivation_class": "standard linearized-GR gauge-mode null control plus internal periodic GH evolution",
            "observable": "TT-projected ideal detector strain of the periodic harmonic gauge-wave control",
            "data_role": "manufactured internal negative control only; no detector data or physical radiative waveform",
            "verification_status": status,
            "open_blockers": [
                "no physical outgoing radiative GH solution or non-periodic CPBC evolution",
                "no metric snapshots, extraction sphere/worldtube, retarded-time map, or temporal Fourier waveform",
                "published RWZ, finite-radius Psi4, and Cauchy-characteristic routes are screened but not implemented",
            ],
            "dependency_unlocked": "none; this is a gauge-false-positive exclusion control only",
            "claim_boundary": "the current periodic harmonic gauge-wave control is not physical gravitational radiation; zero TT response validates only this negative-control case, not a waveform extraction method or UET prediction",
            "evidence_artifacts": [
                {
                    "path": SOURCE_RECORD.relative_to(ROOT).as_posix(),
                    "sha256": source_hashes[
                        SOURCE_RECORD.relative_to(ROOT).as_posix()
                    ],
                }
            ],
        },
        "claim_boundary": "No physical waveform, detector data, calibration, UET prediction, parent closure, or downstream dependency is claimed.",
    }
    return result


def main() -> int:
    artifact = build_artifact()
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": artifact["status"], "checks": artifact["checks"], "metrics": artifact["metrics"]}, indent=2))
    return 0 if artifact["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
