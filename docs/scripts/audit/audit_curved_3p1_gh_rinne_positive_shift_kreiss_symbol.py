from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BASELINE_SCRIPT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_zero_shift_kreiss_symbol.py"
BASELINE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_positive_shift_kreiss_symbol.json"
GH_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
BOUNDARY_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py"
MODE_SOURCE = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tangential_cpbc_mode.py"
NORMAL = np.array([-1.0, 0.0, 0.0])
OMEGA = 1.0
GAMMA2 = 1.0
BETA_VALUES = (0.1, 0.5, 0.9)
REAL_ZETA = (1.0e-10, 1.0e-8, 1.0e-6, 1.0e-4, 1.0e-2, 0.1, 1.0, 10.0, 1.0e2, 1.0e4, 1.0e6)
IMAG_ZETA = (
    0.0,
    0.5,
    0.999999,
    1.0,
    1.000001,
    2.0,
    10.0,
    1.0e2,
    1.0e4,
    1.0e6,
    -0.5,
    -0.999999,
    -1.0,
    -1.000001,
    -2.0,
    -10.0,
    -1.0e2,
    -1.0e4,
    -1.0e6,
)
RANK_RELATIVE_TOLERANCE = 1.0e-10
MODE_RESIDUAL_TOLERANCE = 1.0e-8
DETERMINANT_TOLERANCE = 1.0e-8
CHARACTERISTIC_TOLERANCE = 1.0e-12
RINNE_URL = "https://arxiv.org/abs/gr-qc/0606053"

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_rinne_zero_shift_helpers", BASELINE_SCRIPT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the frozen zero-shift basis-map audit")
BASELINE = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = BASELINE
_spec.loader.exec_module(BASELINE)
MODE = BASELINE.MODE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _root_and_lambda(zeta: complex, beta: float) -> tuple[complex, complex]:
    gamma_squared = 1.0 / (1.0 - beta * beta)
    root = complex(np.sqrt(zeta * zeta + 1.0 - beta * beta + 0.0j))
    if root.real < 0.0:
        root = -root
    if root.real <= 0.0:
        raise RuntimeError("positive-shift decaying-root branch lost positive real part")
    lam = gamma_squared * (-beta * zeta - root)
    if lam.real >= 0.0:
        raise RuntimeError("Rinne lambda_1_minus is not decaying on Re(zeta)>0")
    return root, lam


def _complex_residuals(
    beta: float,
    metric: np.ndarray,
    pi: np.ndarray,
    phi: np.ndarray,
    dmetric: np.ndarray,
    dpi: np.ndarray,
    dphi: np.ndarray,
) -> tuple[dict[str, np.ndarray], str]:
    def evaluate(part: str):
        arrays = (metric, pi, phi, dmetric, dpi, dphi)
        values = [getattr(value, part) for value in arrays]
        return MODE.BOUNDARY.gh_linear_boundary_residuals(
            metric_perturbation=values[0],
            pi_perturbation=values[1],
            phi_perturbation=values[2],
            metric_gradient=values[3],
            pi_gradient=values[4],
            phi_gradient=values[5],
            normal=NORMAL,
            lapse=1.0,
            normal_shift=-beta,
            gamma2=GAMMA2,
        )

    real = evaluate("real")
    imag = evaluate("imag")
    if real.boundary_regime != imag.boundary_regime:
        raise RuntimeError("complex split changed the incoming characteristic regime")
    residuals = {
        "constraint": np.asarray(real.constraint_incoming)
        + 1.0j * np.asarray(imag.constraint_incoming),
        "physical": np.asarray(real.physical_weyl_incoming)
        + 1.0j * np.asarray(imag.physical_weyl_incoming),
        "gauge": np.asarray(real.gauge_incoming)
        + 1.0j * np.asarray(imag.gauge_incoming),
    }
    return residuals, real.boundary_regime


def _local_characteristics(beta: float) -> dict[str, Any]:
    parameters = MODE.CANONICAL_GH.GHParameters(shift=(beta, 0.0, 0.0))
    symbol = MODE.CANONICAL_GH.gh_principal_symbol(NORMAL, parameters)
    speeds = np.asarray(symbol.characteristic_speeds, dtype=float)
    labels = ("u0", "u1_plus", "u1_minus", "u2_tangent_1", "u2_tangent_2")
    incoming = [
        label for label, speed in zip(labels, speeds)
        if speed < -CHARACTERISTIC_TOLERANCE
    ]
    return {
        "rinne_coordinate_shift_beta": beta,
        "local_outward_normal": NORMAL.tolist(),
        "local_normal_shift": float(np.asarray(parameters.shift) @ NORMAL),
        "characteristic_speeds_by_label": dict(zip(labels, speeds.tolist())),
        "incoming_modes": incoming,
        "u2_modes_are_outgoing": bool(np.all(speeds[3:] > CHARACTERISTIC_TOLERANCE)),
        "expected_regime": "U1_ONLY_INCOMING_SUBLUMINAL",
    }


def _mode_column(zeta: complex, beta: float, component: int) -> tuple[np.ndarray, float, float, str]:
    root, lam = _root_and_lambda(zeta, beta)
    effective_zeta = zeta - beta * lam
    mode_vector = np.asarray(
        [effective_zeta, -lam, -1.0j * OMEGA, 0.0j], dtype=complex
    )
    mode_vector /= np.linalg.norm(mode_vector)

    tensor = np.zeros((4, 4), dtype=complex)
    i, j = MODE.PAIRS[component]
    tensor[i, j] = 1.0
    tensor[j, i] = 1.0
    tensor /= np.sqrt(MODE.TENSOR_WEIGHTS[component])

    metric = np.zeros((4, 4), dtype=complex)
    pi = mode_vector[0] * tensor
    phi = np.stack(
        (mode_vector[1] * tensor, mode_vector[2] * tensor, mode_vector[3] * tensor)
    )
    dmetric = np.zeros((3, 4, 4), dtype=complex)
    dpi = np.zeros_like(dmetric)
    dphi = np.zeros((3, 3, 4, 4), dtype=complex)
    dpi[0] = lam * pi
    dpi[1] = 1.0j * OMEGA * pi
    dphi[0] = lam * phi
    dphi[1] = 1.0j * OMEGA * phi

    residuals, regime = _complex_residuals(
        beta, metric, pi, phi, dmetric, dpi, dphi
    )
    normal_maps = MODE.BOUNDARY.gh_boundary_normal_maps(NORMAL)
    projectors = MODE.PROJECTORS.build_gh_boundary_projectors(NORMAL)
    gauge_basis = np.linalg.svd(projectors.gauge)[0]
    gauge_basis = gauge_basis[:, : projectors.ranks["gauge"]]
    boundary_vector = np.concatenate(
        (
            residuals["constraint"],
            normal_maps["physical"] @ BASELINE._pack_symmetric(residuals["physical"]),
            gauge_basis.conj().T @ BASELINE._pack_symmetric(residuals["gauge"]),
        )
    )

    bulk_residual = np.asarray(
        [
            effective_zeta * pi + lam * phi[0] + 1.0j * OMEGA * phi[1],
            effective_zeta * phi[0] + lam * pi,
            effective_zeta * phi[1] + 1.0j * OMEGA * pi,
            effective_zeta * phi[2],
        ]
    )
    return boundary_vector, float(-lam.real), float(np.max(np.abs(bulk_residual))), regime


def _case(
    beta: float,
    zeta: complex,
    source_row_transform: np.ndarray,
    source_column_transform: np.ndarray,
) -> dict[str, Any]:
    columns = [_mode_column(zeta, beta, component) for component in range(10)]
    residual_matrix = np.column_stack([column[0] for column in columns])
    boundary_data_matrix = residual_matrix.copy()
    boundary_data_matrix[:6, :] /= zeta
    row_norms = np.linalg.norm(boundary_data_matrix, axis=1)
    if np.any(row_norms == 0.0):
        raise RuntimeError("boundary-data row equilibration encountered a zero row")
    row_equilibrated = boundary_data_matrix / row_norms[:, None]
    singular_values = np.linalg.svd(row_equilibrated, compute_uv=False)
    rank = int(
        np.count_nonzero(singular_values > RANK_RELATIVE_TOLERANCE * singular_values[0])
    )

    source_matrix = source_row_transform @ boundary_data_matrix @ source_column_transform
    sign, log_abs_determinant = np.linalg.slogdet(source_matrix)
    _, lam = _root_and_lambda(zeta, beta)
    mode_norm = float(np.linalg.norm([zeta - beta * lam, -lam, -1.0j, 0.0j]))
    determinant_factor = zeta - (1.0 + beta) * lam
    expected_log_abs = float(
        16.0 * np.log(abs(determinant_factor))
        - np.log(8.0)
        - 6.0 * np.log(abs(zeta))
        - 10.0 * np.log(mode_norm)
    )
    expected_phase = float(
        np.angle(-1.0 + 0.0j)
        + 16.0 * np.angle(determinant_factor)
        - 6.0 * np.angle(zeta)
    )
    log_offset = float(log_abs_determinant - expected_log_abs)
    phase_offset = float(
        np.angle(np.exp(1.0j * (np.angle(sign) - expected_phase)))
    )
    local_shift = _local_characteristics(beta)
    regimes = {column[3] for column in columns}
    if len(regimes) != 1:
        raise RuntimeError("decaying mode columns disagree on the local boundary regime")

    return {
        "beta": beta,
        "zeta_real": float(zeta.real),
        "zeta_imag": float(zeta.imag),
        "decaying_subspace_dimension": len(columns),
        "boundary_matrix_rank": rank,
        "boundary_matrix_relative_smallest_singular_value": float(
            singular_values[-1] / singular_values[0]
        ),
        "maximum_principal_mode_residual": max(column[2] for column in columns),
        "local_normal_shift": local_shift["local_normal_shift"],
        "incoming_mode_count": len(local_shift["incoming_modes"]),
        "u2_modes_are_outgoing": local_shift["u2_modes_are_outgoing"],
        "boundary_regime": next(iter(regimes)),
        "source_determinant_log_offset_from_eq_122": log_offset,
        "source_determinant_phase_offset_from_eq_122_radians": phase_offset,
    }


def build_artifact() -> dict[str, Any]:
    source_row_transform, source_column_transform, basis_map_audit = (
        BASELINE._source_component_basis_map()
    )
    cases = [
        _case(beta, complex(real, imag), source_row_transform, source_column_transform)
        for beta in BETA_VALUES
        for real in REAL_ZETA
        for imag in IMAG_ZETA
    ]
    per_beta: list[dict[str, Any]] = []
    for beta in BETA_VALUES:
        rows = [row for row in cases if row["beta"] == beta]
        char = _local_characteristics(beta)
        per_beta.append(
            {
                "beta": beta,
                "local_normal_shift": char["local_normal_shift"],
                "incoming_modes": char["incoming_modes"],
                "u2_modes_are_outgoing": char["u2_modes_are_outgoing"],
                "case_count": len(rows),
                "minimum_boundary_relative_smallest_singular_value": min(
                    row["boundary_matrix_relative_smallest_singular_value"]
                    for row in rows
                ),
                "maximum_principal_mode_residual": max(
                    row["maximum_principal_mode_residual"] for row in rows
                ),
                "maximum_abs_eq_122_log_offset": max(
                    abs(row["source_determinant_log_offset_from_eq_122"])
                    for row in rows
                ),
                "maximum_abs_eq_122_phase_offset_radians": max(
                    abs(row["source_determinant_phase_offset_from_eq_122_radians"])
                    for row in rows
                ),
                "minimum_boundary_matrix_rank": min(
                    row["boundary_matrix_rank"] for row in rows
                ),
                "maximum_decaying_subspace_dimension": max(
                    row["decaying_subspace_dimension"] for row in rows
                ),
                "boundary_regimes": sorted({row["boundary_regime"] for row in rows}),
            }
        )

    max_mode_residual = max(row["maximum_principal_mode_residual"] for row in cases)
    max_log_offset = max(
        abs(row["source_determinant_log_offset_from_eq_122"]) for row in cases
    )
    max_phase_offset = max(
        abs(row["source_determinant_phase_offset_from_eq_122_radians"])
        for row in cases
    )
    checks = {
        "three_preregistered_strictly_subluminal_positive_shifts": all(
            0.0 < beta < 1.0 for beta in BETA_VALUES
        ),
        "mapped_local_shift_is_negative_rinne_beta": all(
            np.isclose(row["local_normal_shift"], -row["beta"], atol=1.0e-15)
            for row in cases
        ),
        "u1_minus_is_the_only_incoming_characteristic_family": all(
            row["incoming_mode_count"] == 1
            and row["boundary_regime"] == "U1_ONLY_INCOMING_SUBLUMINAL"
            for row in cases
        ),
        "u2_tangent_modes_are_outgoing_in_mapped_positive_shift_lane": all(
            row["u2_modes_are_outgoing"] for row in cases
        ),
        "ten_decaying_metric_amplitudes": all(
            row["decaying_subspace_dimension"] == 10 for row in cases
        ),
        "source_basis_map_identities_pass": bool(
            basis_map_audit["all_projector_and_coordinate_identities_within_tolerance"]
        ),
        "all_boundary_data_matrices_have_rank_10": all(
            row["boundary_matrix_rank"] == 10 for row in cases
        ),
        "principal_mode_equations_pass": max_mode_residual < MODE_RESIDUAL_TOLERANCE,
        "eq_122_determinant_log_crosscheck_passes": max_log_offset < DETERMINANT_TOLERANCE,
        "eq_122_determinant_phase_crosscheck_passes": max_phase_offset < DETERMINANT_TOLERANCE,
    }
    passed = all(checks.values())
    source_hashes = {
        path: _sha256(ROOT / path)
        for path in (
            _rel(Path(__file__)),
            _rel(BASELINE_SCRIPT),
            _rel(BASELINE_ARTIFACT),
            _rel(MODE_SOURCE),
            _rel(BOUNDARY_SOURCE),
            _rel(GH_SOURCE),
        )
    }
    status = (
        "PASS_SOURCE_MATCHED_POSITIVE_SHIFT_KREISS_SAMPLE"
        if passed
        else "PARTIAL_POSITIVE_SHIFT_KREISS_SAMPLE"
    )
    closure_level = "CLOSED_FOR_LANE" if passed else "PARTIAL"
    claim_boundary = (
        "Source-matched, frozen-coefficient standard-GR boundary-symbol result "
        "for the preregistered Rinne inward-shift samples beta={0.1,0.5,0.9} only. "
        "It imports Rinne's specified Fourier-Laplace/Kreiss theorem after the "
        "fixed repository-to-source basis map; the finite sample is not a new "
        "continuum proof, does not cover all beta in (0,1), and does not close "
        "the nonlinear/variable-coefficient curved 3+1 parent, UET, or Gravity."
    )
    major_result = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_POSITIVE_SHIFT_KREISS_SYMBOL",
        "topic": "core_curved_3p1",
        "closure_level": closure_level,
        "what_is_closed": [
            "For Rinne's coordinate shift beta={0.1,0.5,0.9}, the registered Core residual map yields a 10-dimensional decaying boundary symbol whose source-basis determinant agrees with Rinne Eq. (122) on the preregistered complex-frequency grid.",
            "The sign map is verified: Rinne's inward-pointing N^x=beta corresponds to local outward-normal shift beta_n=-beta; only u1_minus is incoming and u2_A is outgoing in these cases.",
        ] if passed else ["The preregistered positive-shift sample was evaluated, but one or more verification checks did not pass."],
        "equation_or_mapping": {
            "rinne_shift_to_core_normal_shift": "beta_Rinne=N^x in the x>0 half-space; with outward normal n=-x, beta_n=shift dot n=-beta_Rinne",
            "decaying_root": "lambda_1_minus=(1-beta^2)^-1*(-beta*zeta-sqrt(zeta^2+1-beta^2)); choose sqrt with positive real part for Re(zeta)>0",
            "mode_vector": "(Pi,Phi_x,Phi_y,Phi_z)=K1^-1*(zeta-beta*lambda_1_minus,-lambda_1_minus,-i,0); psi=0",
            "source_determinant": "det(C)=-[zeta-(1+beta)*lambda_1_minus]^16/(8*zeta^6*K1^10)",
            "repository_to_source_map": "C_source=T_rows*diag(zeta^-1*I6,I4)*C_residual*T_columns; fixed maps imported unchanged from the zero-shift audit",
        },
        "units": "Frozen local orthonormal geometric units; omega normalized to 1 and zeta=s/omega dimensionless.",
        "derivation_class": "source-matched analytic Fourier-Laplace mode and determinant cross-check; finite numerical sampling",
        "observable": "10x10 boundary-data symbol determinant, rank, characteristic incidence, and principal-mode residual",
        "data_role": "primary-literature formula cross-check; no empirical data, fitting, or calibration",
        "verification_status": status,
        "open_blockers": [
            "Rinne beta<0 requires the additional decaying u2_A modes and twenty extra incoming constraint-curl rows, including the degenerate zeta=-beta generalized mode; that lane is not covered here.",
            "The sample does not independently prove a uniform bound over every beta in (0,1) or the closed half-plane in zeta; it relies on the fixed source correspondence and Rinne's theorem for the specified system.",
            "Variable-coefficient/nonlinear GH evolution, corners, matter boundaries, dimensional observables, and Core curved-parent requirements remain open.",
        ],
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "claim_boundary": claim_boundary,
    }
    return {
        "schema_version": "core-curved-3p1-gh-rinne-positive-shift-kreiss-symbol-v1",
        "artifact": "curved_3p1_gh_rinne_positive_shift_kreiss_symbol",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "major_result_id": major_result["major_result_id"],
        "major_result": major_result,
        "closure_level": closure_level,
        "MAJOR_RESULT_CLOSURE": closure_level,
        "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
        "WHAT_REMAINS_OPEN": major_result["open_blockers"],
        "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added a separate positive-Rinne-shift Fourier-Laplace audit using the frozen zero-shift basis map; the zero-shift artifact, production GH equations, boundary residual API, and parent/dependency gates were not modified.",
        "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
        "VERIFICATION": {
            "checks": checks,
            "case_count": len(cases),
            "case_grid_per_beta": {
                "real_zeta": list(REAL_ZETA),
                "imag_zeta": list(IMAG_ZETA),
                "points_per_beta": len(REAL_ZETA) * len(IMAG_ZETA),
                "excluded": "Re(zeta)=0 and zeta=0 are not sampled; this is a finite Re(zeta)>0 grid",
            },
            "per_beta": per_beta,
            "maximum_principal_mode_residual": max_mode_residual,
            "maximum_abs_eq_122_determinant_log_offset": max_log_offset,
            "maximum_abs_eq_122_determinant_phase_offset_radians": max_phase_offset,
            "source_basis_map_audit": basis_map_audit,
            "source_hashes": source_hashes,
        },
        "PREREGISTRATION": {
            "source_beta_values": list(BETA_VALUES),
            "source_beta_domain": "0 < beta < 1; Rinne coordinate shift points into x>0 domain",
            "mapped_local_normal_shift": "normal_shift=-beta because repository outward normal is (-1,0,0)",
            "frequency_grid_locked_before_run": True,
            "parameter_fitting": False,
            "threshold_changes": False,
            "clipping_or_cone_padding": False,
            "basis_map_refit": False,
        },
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": RINNE_URL,
                "equations": "Eq. (72) for beta>0 decaying mode; Eq. (122) for the boundary determinant; Eqs. (109)-(120) for constraint, physical, and gauge boundary rows",
                "scope": "Rinne's frozen-coefficient high-frequency Fourier-Laplace/Kreiss result for the specified first-order GH system and subluminal normal shift; imported conditionally after source-basis correspondence",
            }
        ],
        "CONTROLLING_BLOCKER": "negative_rinne_shift_u2_decaying_modes_and_zeta_equals_minus_beta_degenerate_basis_not_yet_reproduced",
        "NEXT_ACTION": "Build the separate Rinne beta<0 symbol with both additional decaying u2_A families and the generalized zeta=-beta mode; reconstruct all 20 incoming definition-curl rows and compare with Eq. (123)-(124), without changing this positive-shift artifact.",
        "CLAIM_BOUNDARY": claim_boundary,
        "claim_promotion": False,
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "artifact": _rel(OUTPUT),
                "status": artifact["STATUS"],
                "case_count": artifact["VERIFICATION"]["case_count"],
                "checks": artifact["VERIFICATION"]["checks"],
            },
            indent=2,
        )
    )
    return 0 if artifact["STATUS"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
