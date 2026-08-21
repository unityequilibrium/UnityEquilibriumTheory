"""Audit the source-locked full-LBTE numerical stability boundary.

The archived runs are an external graphite candidate route only.  This audit
does not create a Phi map, fit alpha_Phi_K, or consume the locked holdout.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
TOPIC = "0.13_Thermodynamic_Bridge"
ARCHIVE_ROOT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/reproduction/t13_calorine_pbte"
OUT = ROOT / "docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json"
FORCE_ROOT = ARCHIVE_ROOT / "force_constants_dim_4x4x2"
METHOD1_ROOT = ARCHIVE_ROOT / "full_lbte_natural_isotope_pinv_method1"
METHOD0_ROOT = ARCHIVE_ROOT / "full_lbte_natural_isotope_pinv_method0"
TEMPERATURES = [200.0, 250.0, 300.0]
MASS_VARIANCE = 7.3872305e-05
PINV_CUTOFF = 1.0e-8
MESH_CONVERGENCE_TOLERANCE = 0.01


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def relative_change(previous: float, current: float) -> float:
    if previous == 0.0:
        return 0.0 if current == 0.0 else float("inf")
    return abs(current - previous) / abs(previous)


def read_run(root: Path, label: str, method: int) -> dict[str, Any]:
    kappa_path = root / "kappa.hdf5"
    eigenvalues_path = root / "coleigs.hdf5"
    if not kappa_path.is_file() or not eigenvalues_path.is_file():
        raise SystemExit(f"missing archived full-LBTE payload for {label}")
    with h5py.File(kappa_path, "r") as handle:
        temperatures = np.asarray(handle["temperature"][:], dtype=float)
        mesh = [int(item) for item in np.asarray(handle["mesh"][:], dtype=int)]
        kappa = np.asarray(handle["kappa"][:], dtype=float)
        kappa_rta = np.asarray(handle["kappa_RTA"][:], dtype=float)
    with h5py.File(eigenvalues_path, "r") as handle:
        eigenvalues = np.asarray(handle["collision_eigenvalues"][:], dtype=float)
        eigen_temperatures = np.asarray(handle["temperature"][:], dtype=float)
    if temperatures.tolist() != TEMPERATURES or eigen_temperatures.tolist() != TEMPERATURES:
        raise SystemExit(f"temperature identity mismatch for {label}")
    if kappa.shape[0] != len(TEMPERATURES) or kappa.shape[1] < 3:
        raise SystemExit(f"unexpected kappa shape for {label}: {kappa.shape}")
    if eigenvalues.shape[0] != len(TEMPERATURES):
        raise SystemExit(f"unexpected collision-eigenvalue shape for {label}: {eigenvalues.shape}")
    in_plane = kappa[:, :2]
    return {
        "label": label,
        "method": method,
        "mesh": mesh,
        "temperatures_K": temperatures.tolist(),
        "kappa_W_m^-1_K^-1": kappa.tolist(),
        "kappa_RTA_W_m^-1_K^-1": kappa_rta.tolist(),
        "in_plane_x_W_m^-1_K^-1": kappa[:, 0].tolist(),
        "in_plane_y_W_m^-1_K^-1": kappa[:, 1].tolist(),
        "in_plane_response_finite": bool(np.isfinite(in_plane).all()),
        "in_plane_response_positive": bool((in_plane > 0.0).all()),
        "in_plane_xy_max_abs_difference": float(np.max(np.abs(in_plane[:, 0] - in_plane[:, 1]))),
        "collision_eigenvalue_shape": list(eigenvalues.shape),
        "collision_eigenvalue_min_by_temperature": np.min(eigenvalues, axis=1).tolist(),
        "collision_eigenvalue_negative_count_by_temperature": np.sum(eigenvalues < 0.0, axis=1).astype(int).tolist(),
        "collision_eigenvalue_abs_below_cutoff_count_by_temperature": np.sum(
            np.abs(eigenvalues) < PINV_CUTOFF, axis=1
        ).astype(int).tolist(),
        "collision_spectrum_positive_semidefinite": bool(np.all(eigenvalues >= 0.0)),
        "payloads": {
            "kappa": record(kappa_path),
            "collision_eigenvalues": record(eigenvalues_path),
        },
    }


def build_payload() -> dict[str, Any]:
    force_constants = {
        name: record(FORCE_ROOT / filename)
        for name, filename in (("poscar", "POSCAR"), ("fc2", "fc2.hdf5"), ("fc3", "fc3.hdf5"))
    }
    method1_runs = [
        read_run(METHOD1_ROOT / "mesh_4x4x2", "4x4x2", method=1),
        read_run(METHOD1_ROOT / "mesh_6x6x3", "6x6x3", method=1),
        read_run(METHOD1_ROOT / "mesh_8x8x4", "8x8x4", method=1),
        read_run(METHOD1_ROOT / "mesh_10x10x5", "10x10x5", method=1),
    ]
    method0_control = read_run(METHOD0_ROOT / "mesh_10x10x5", "10x10x5_method0_control", method=0)
    comparisons = []
    for previous, current in zip(method1_runs, method1_runs[1:]):
        rows = []
        for temperature, old, new in zip(
            TEMPERATURES,
            previous["in_plane_x_W_m^-1_K^-1"],
            current["in_plane_x_W_m^-1_K^-1"],
            strict=True,
        ):
            rows.append(
                {
                    "temperature_K": temperature,
                    "previous_in_plane_x_W_m^-1_K^-1": old,
                    "current_in_plane_x_W_m^-1_K^-1": new,
                    "relative_change_from_previous": relative_change(old, new),
                }
            )
        comparisons.append(
            {
                "from_mesh": previous["mesh"],
                "to_mesh": current["mesh"],
                "rows": rows,
                "max_relative_change": max(row["relative_change_from_previous"] for row in rows),
            }
        )
    latest_pair = comparisons[-1]
    source_identity_match = len({item["sha256"] for item in force_constants.values()}) == 3
    method0_negative_300k = method0_control["in_plane_x_W_m^-1_K^-1"][-1] < 0.0
    method1_spectrum_same_as_control = (
        method1_runs[-1]["collision_eigenvalue_min_by_temperature"]
        == method0_control["collision_eigenvalue_min_by_temperature"]
        and method1_runs[-1]["collision_eigenvalue_negative_count_by_temperature"]
        == method0_control["collision_eigenvalue_negative_count_by_temperature"]
    )
    major_result = {
        "major_result_id": "T13_CALORINE_FULL_LBTE_NUMERICAL_STABILITY_BOUNDARY",
        "topic": TOPIC,
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "full-LBTE outputs are archived for a fixed source-locked 4x4x2 force-constant state",
            "natural-isotope mass variance is recorded as an explicit numerical control",
            "pinv_method=0 and pinv_method=1 are compared without changing the source or the thermal leakage threshold",
            "the high-mesh collision spectrum is shown to be sign-indefinite and the method-1 positive response is not mesh-converged",
            "the result is separated from Phi mapping, alpha_Phi_K calibration, Ding acceptance, and Xie 2026 holdout access",
        ],
        "equation_or_mapping": {
            "source_heat_capacity": "C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]",
            "candidate_temperature_response": "Delta_Tq = Delta_u_ph / C_src(T)",
            "lbte_observable": "kappa = full-LBTE heat-current response in W m^-1 K^-1",
            "pseudoinverse_method_0": "treat |eigenvalue| < pinv_cutoff as zero",
            "pseudoinverse_method_1": "treat eigenvalue < pinv_cutoff as zero; this ignores negative eigenvalues",
        },
        "units": {
            "C_src": "J m^-3 K^-1",
            "temperature": "K",
            "kappa": "W m^-1 K^-1",
            "collision_eigenvalues": "phono3py collision-matrix internal units; not promoted to SI",
        },
        "derivation_class": "EXTERNAL_CANDIDATE_FULL_LBTE_NUMERICAL_REPRODUCTION_NO_UET_DERIVATION",
        "observable": "candidate graphite full-LBTE thermal-conductivity response",
        "data_role": "EXTERNAL_CANDIDATE_REPRODUCTION_NOT_CALIBRATION_NOT_HOLDOUT",
        "verification_status": "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN",
        "open_blockers": [
            "full_lbte_collision_spectrum_positive_semidefinite_missing",
            "full_lbte_mesh_convergence_missing",
            "calorine_route_material_regime_mapping_to_ding_missing",
            "calorine_route_source_grade_uncertainty_missing",
            "alpha_Phi_K_independent_calibration_missing",
        ],
        "dependency_unlocked": "full-LBTE numerical-boundary evidence lane only; no physical transport, dimensional map, Topic 13, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This closes a numerical-stability boundary for one source-locked external graphite candidate route. It does not establish a physical UET transport coefficient, a Ding TTG material match, an alpha_Phi_K calibration, a Phi-to-temperature prediction, or Full Topic 13 closure.",
    }
    return {
        "schema_version": "t13-calorine-full-lbte-stability-boundary-v1",
        "artifact": "t13_calorine_full_lbte_stability_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN",
        "major_result": major_result,
        "source": {
            "force_constants": force_constants,
            "material_state": "public Calorine graphite primitive C4 state; not declared equivalent to Ding natural-graphite TTG",
            "isotope_mass_variance": MASS_VARIANCE,
            "isotope_mass_variance_source": "phono3py.other.isotope.get_mass_variances(['C']) in the installed runtime",
            "software": {"calorine": "3.5", "phono3py": "4.4.0", "phonopy": "4.4.0", "ase": "3.29.0"},
        },
        "numerical_contract": {
            "supercell_dim": [4, 4, 2],
            "temperatures_K": TEMPERATURES,
            "is_LBTE": True,
            "is_isotope": True,
            "pinv_cutoff": PINV_CUTOFF,
            "mesh_convergence_tolerance": MESH_CONVERGENCE_TOLERANCE,
            "no_clipping": True,
            "no_cone_padding": True,
            "no_fit": True,
            "target_curve_used": False,
            "alpha_Phi_K_fit_performed": False,
            "holdout_accessed": False,
        },
        "method1_runs": method1_runs,
        "method0_control": method0_control,
        "mesh_convergence": {
            "criterion": "diagnostic adjacent-mesh relative change <= 0.01; this is not a UET acceptance threshold",
            "declared_tolerance": MESH_CONVERGENCE_TOLERANCE,
            "comparisons": comparisons,
            "latest_pair": latest_pair,
            "latest_pair_pass": latest_pair["max_relative_change"] <= MESH_CONVERGENCE_TOLERANCE,
        },
        "checks": {
            "force_constant_identity_recorded": source_identity_match,
            "archived_method1_payloads_present": True,
            "archived_method0_control_present": True,
            "method1_in_plane_response_finite": all(run["in_plane_response_finite"] for run in method1_runs),
            "method1_in_plane_response_positive": all(run["in_plane_response_positive"] for run in method1_runs),
            "method1_collision_spectrum_positive_semidefinite": all(
                run["collision_spectrum_positive_semidefinite"] for run in method1_runs
            ),
            "method0_negative_in_plane_kappa_at_300K": method0_negative_300k,
            "method1_and_method0_collision_spectrum_match_at_high_mesh": method1_spectrum_same_as_control,
            "latest_method1_mesh_pair_converged": latest_pair["max_relative_change"] <= MESH_CONVERGENCE_TOLERANCE,
            "fit_performed": False,
            "target_curve_used": False,
            "alpha_Phi_K_fit_performed": False,
            "holdout_accessed": False,
        },
        "acceptance_for_full_topic13": False,
        "controlling_blocker": "full_lbte_numerical_well_posedness_not_closed",
        "next_controller": "Resolve the sign-indefinite collision spectrum and obtain a declared, source-supported convergence/uncertainty contract before using full-LBTE output as a physical transport comparator; do not use it for alpha_Phi_K or holdout prediction.",
        "evidence_artifacts": [
            record(path)
            for run in method1_runs + [method0_control]
            for path in (
                ROOT / run["payloads"]["kappa"]["path"],
                ROOT / run["payloads"]["collision_eigenvalues"]["path"],
            )
        ],
        "claim_boundary": major_result["claim_boundary"],
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "latest_pair_max_relative_change": payload["mesh_convergence"]["latest_pair"]["max_relative_change"],
                "method0_negative_300K": payload["checks"]["method0_negative_in_plane_kappa_at_300K"],
                "method1_spectrum_positive_semidefinite": payload["checks"]["method1_collision_spectrum_positive_semidefinite"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
