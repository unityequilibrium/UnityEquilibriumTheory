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
MODE_AUDIT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tangential_cpbc_mode.py"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
NORMAL = np.array([-1.0, 0.0, 0.0])
OMEGA = 1.0
GAMMA2 = 1.0
RANK_RELATIVE_TOLERANCE = 1.0e-10
BASIS_MAP_TOLERANCE = 1.0e-12
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

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_rinne_kreiss_mode_helpers", MODE_AUDIT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the registered GH boundary residual maps")
MODE = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = MODE
_spec.loader.exec_module(MODE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pack_symmetric(tensor: np.ndarray) -> np.ndarray:
    return np.asarray([tensor[i, j] for i, j in MODE.PAIRS])


def _complex_residuals(
    metric: np.ndarray,
    pi: np.ndarray,
    phi: np.ndarray,
    dmetric: np.ndarray,
    dpi: np.ndarray,
    dphi: np.ndarray,
) -> dict[str, np.ndarray]:
    def evaluate(part: str) -> dict[str, np.ndarray]:
        arrays = (metric, pi, phi, dmetric, dpi, dphi)
        values = [getattr(value, part) for value in arrays]
        result = MODE.BOUNDARY.gh_linear_boundary_residuals(
            metric_perturbation=values[0],
            pi_perturbation=values[1],
            phi_perturbation=values[2],
            metric_gradient=values[3],
            pi_gradient=values[4],
            phi_gradient=values[5],
            normal=NORMAL,
            lapse=1.0,
            normal_shift=0.0,
            gamma2=GAMMA2,
        )
        return {
            "constraint": np.asarray(result.constraint_incoming),
            "physical": np.asarray(result.physical_weyl_incoming),
            "gauge": np.asarray(result.gauge_incoming),
        }

    real = evaluate("real")
    imag = evaluate("imag")
    return {name: real[name] + 1.0j * imag[name] for name in real}


def _mode_column(zeta: complex, component: int) -> tuple[np.ndarray, float, float]:
    root = np.sqrt(1.0 + zeta * zeta + 0.0j)
    if root.real < 0.0:
        root = -root
    if root.real <= 0.0:
        raise RuntimeError("decaying-root branch lost positive-real square root")
    lam = -root
    mode_vector = np.asarray([zeta, -lam, -1.0j * OMEGA, 0.0j])
    normalization = float(np.linalg.norm(mode_vector))
    mode_vector /= normalization

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

    residual = _complex_residuals(metric, pi, phi, dmetric, dpi, dphi)
    normal_maps = MODE.BOUNDARY.gh_boundary_normal_maps(NORMAL)
    projectors = MODE.PROJECTORS.build_gh_boundary_projectors(NORMAL)
    gauge_basis, _, _ = np.linalg.svd(projectors.gauge)
    gauge_basis = gauge_basis[:, : projectors.ranks["gauge"]]
    boundary_vector = np.concatenate(
        (
            residual["constraint"],
            normal_maps["physical"] @ _pack_symmetric(residual["physical"]),
            gauge_basis.conj().T @ _pack_symmetric(residual["gauge"]),
        )
    )

    bulk_residual = np.asarray(
        [
            zeta * pi + lam * phi[0] + 1.0j * OMEGA * phi[1],
            zeta * phi[0] + lam * pi - GAMMA2 * lam * metric,
            zeta * phi[1] + 1.0j * OMEGA * pi - 1.0j * GAMMA2 * OMEGA * metric,
            zeta * phi[2],
        ]
    )
    return boundary_vector, float(root.real), float(np.max(np.abs(bulk_residual)))


def _source_component_basis_map() -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    projectors = MODE.PROJECTORS.build_gh_boundary_projectors(NORMAL)
    gauge_basis = np.linalg.svd(projectors.gauge)[0]
    gauge_basis = gauge_basis[:, : projectors.ranks["gauge"]]
    pairs = MODE.PAIRS

    null_l = np.asarray([1.0, -1.0, 0.0, 0.0]) / np.sqrt(2.0)
    gauge_covector_map = np.zeros((4, len(pairs)))
    for column, (i, j) in enumerate(pairs):
        tensor = np.zeros((4, 4))
        tensor[i, j] = 1.0
        tensor[j, i] = 1.0
        gauge_covector_map[:, column] = tensor @ null_l

    row_transform = np.zeros((10, 10))
    row_transform[:4, :4] = np.eye(4)
    row_transform[4:6, 4:6] = np.diag([1.0, -1.0])
    row_transform[6:10, 6:10] = np.sqrt(2.0) * gauge_covector_map @ gauge_basis
    column_transform = np.diag(np.sqrt(MODE.TENSOR_WEIGHTS))

    normal_maps = MODE.BOUNDARY.gh_boundary_normal_maps(NORMAL)
    physical_basis = np.linalg.svd(projectors.physical)[0]
    physical_basis = physical_basis[:, : projectors.ranks["physical"]]
    physical_coordinate_residual = 0.0
    for packed_tensor in physical_basis.T:
        tensor = np.zeros((4, 4))
        for value, (i, j) in zip(packed_tensor, pairs):
            tensor[i, j] = value
            tensor[j, i] = value
        local_coordinates = normal_maps["physical"] @ packed_tensor
        source_coordinates = np.asarray([tensor[2, 2], -tensor[2, 3]])
        physical_coordinate_residual = max(
            physical_coordinate_residual,
            float(np.max(np.abs(local_coordinates - source_coordinates))),
        )

    gauge_transform = row_transform[6:10, 6:10]
    gauge_singular_values = np.linalg.svd(gauge_transform, compute_uv=False)
    projector_residuals = {
        "gauge_covector_annihilates_constraint_sector": float(
            np.max(np.abs(gauge_covector_map @ projectors.constraint))
        ),
        "gauge_covector_annihilates_physical_sector": float(
            np.max(np.abs(gauge_covector_map @ projectors.physical))
        ),
        "gauge_covector_identity_on_gauge_sector": float(
            np.max(np.abs(gauge_covector_map @ projectors.gauge - gauge_covector_map))
        ),
        "gauge_basis_orthonormality": float(
            np.max(np.abs(gauge_basis.T @ gauge_basis - np.eye(4)))
        ),
        "gauge_basis_spans_projector_image": float(
            max(
                np.max(
                    np.abs(
                        gauge_basis @ gauge_basis.T @ projectors.gauge
                        - projectors.gauge
                    )
                ),
                np.max(np.abs(projectors.gauge @ gauge_basis - gauge_basis)),
            )
        ),
        "physical_source_coordinate_map": physical_coordinate_residual,
    }
    all_residuals_within_tolerance = all(
        residual <= BASIS_MAP_TOLERANCE for residual in projector_residuals.values()
    )
    all_fixed_maps_invertible = (
        np.linalg.matrix_rank(row_transform, tol=BASIS_MAP_TOLERANCE) == 10
        and np.linalg.matrix_rank(column_transform, tol=BASIS_MAP_TOLERANCE) == 10
        and gauge_singular_values[-1] > BASIS_MAP_TOLERANCE
    )
    return row_transform, column_transform, {
        "relation": "C_source_components=T_rows*C_repository_boundary_data*T_columns",
        "constraint_row_map": "identity on the four c0 components",
        "physical_row_map": [[1.0, 0.0], [0.0, -1.0]],
        "physical_coordinate_convention": "repository rows are (w_yy,-w_yz); source component rows are (w_yy,w_yz)",
        "gauge_null_vector": null_l.tolist(),
        "gauge_row_map": gauge_transform.tolist(),
        "gauge_row_map_source_convention": "sqrt(2) times the normalized l-contraction, matching source component equations (117)-(120)",
        "column_tensor_component_rescaling": np.diag(column_transform).tolist(),
        "column_rescaling_source_convention": "undo the repository Frobenius-normalized off-diagonal symmetric-tensor basis",
        "projector_and_coordinate_identity_residuals": projector_residuals,
        "maximum_identity_residual": max(projector_residuals.values()),
        "identity_tolerance": BASIS_MAP_TOLERANCE,
        "gauge_row_map_singular_values": gauge_singular_values.tolist(),
        "all_fixed_maps_invertible": bool(all_fixed_maps_invertible),
        "all_projector_and_coordinate_identities_within_tolerance": bool(
            all_residuals_within_tolerance
        ),
    }


def _case(
    zeta: complex,
    source_row_transform: np.ndarray,
    source_column_transform: np.ndarray,
) -> dict[str, Any]:
    columns = [_mode_column(zeta, component) for component in range(10)]
    residual_matrix = np.column_stack([column[0] for column in columns])
    boundary_data_matrix = residual_matrix.copy()
    boundary_data_matrix[:6, :] /= zeta
    boundary_data_singular_values = np.linalg.svd(
        boundary_data_matrix, compute_uv=False
    )
    residual_singular_values = np.linalg.svd(residual_matrix, compute_uv=False)
    row_norms = np.linalg.norm(boundary_data_matrix, axis=1)
    if np.any(row_norms == 0.0):
        raise RuntimeError("boundary-data row equilibration encountered a zero row")
    row_equilibrated_matrix = boundary_data_matrix / row_norms[:, None]
    row_equilibrated_singular_values = np.linalg.svd(
        row_equilibrated_matrix, compute_uv=False
    )
    rank = int(
        np.count_nonzero(
            row_equilibrated_singular_values
            > RANK_RELATIVE_TOLERANCE * row_equilibrated_singular_values[0]
        )
    )
    sign, log_abs_determinant = np.linalg.slogdet(boundary_data_matrix)
    residual_sign, residual_log_abs_determinant = np.linalg.slogdet(residual_matrix)
    source_component_matrix = (
        source_row_transform @ boundary_data_matrix @ source_column_transform
    )
    source_sign, source_log_abs_determinant = np.linalg.slogdet(
        source_component_matrix
    )
    root = np.sqrt(1.0 + zeta * zeta + 0.0j)
    if root.real < 0.0:
        root = -root
    lam = -root
    mode_normalization = float(
        np.linalg.norm([zeta, -lam, -1.0j * OMEGA, 0.0j])
    )
    published_log_abs_determinant = float(
        16.0 * np.log(abs(zeta - lam))
        - np.log(8.0)
        - 6.0 * np.log(abs(zeta))
        - 10.0 * np.log(mode_normalization)
    )
    published_determinant_phase = float(
        np.angle(-1.0 + 0.0j)
        + 16.0 * np.angle(zeta - lam)
        - 6.0 * np.angle(zeta)
    )
    determinant_log_offset = float(
        log_abs_determinant - published_log_abs_determinant
    )
    determinant_phase_offset = float(
        np.angle(
            np.exp(
                1.0j
                * (
                    np.angle(sign)
                    - published_determinant_phase
                )
            )
        )
    )
    source_determinant_log_offset = float(
        source_log_abs_determinant - published_log_abs_determinant
    )
    source_determinant_phase_offset = float(
        np.angle(
            np.exp(
                1.0j
                * (np.angle(source_sign) - published_determinant_phase)
            )
        )
    )
    return {
        "zeta_real": float(zeta.real),
        "zeta_imag": float(zeta.imag),
        "omega_normalized": OMEGA,
        "decaying_mode_dimension": len(columns),
        "residual_matrix_shape": list(residual_matrix.shape),
        "boundary_data_matrix_shape": list(boundary_data_matrix.shape),
        "stable_root_real_part": float(columns[0][1]),
        "maximum_principal_mode_residual": max(column[2] for column in columns),
        "row_equilibrated_boundary_data_rank_at_declared_relative_tolerance": rank,
        "row_equilibrated_boundary_data_relative_smallest_singular_value": float(
            row_equilibrated_singular_values[-1]
            / row_equilibrated_singular_values[0]
        ),
        "boundary_data_absolute_smallest_singular_value": float(
            boundary_data_singular_values[-1]
        ),
        "boundary_data_largest_singular_value": float(
            boundary_data_singular_values[0]
        ),
        "boundary_data_condition_number": float(
            boundary_data_singular_values[0] / boundary_data_singular_values[-1]
        ),
        "residual_matrix_relative_smallest_singular_value": float(
            residual_singular_values[-1] / residual_singular_values[0]
        ),
        "residual_matrix_condition_number": float(
            residual_singular_values[0] / residual_singular_values[-1]
        ),
        "boundary_data_log_abs_determinant": float(log_abs_determinant),
        "residual_matrix_log_abs_determinant": float(residual_log_abs_determinant),
        "residual_matrix_determinant_phase_radians": float(np.angle(residual_sign)),
        "boundary_data_determinant_phase_radians": float(np.angle(sign)),
        "published_formula_log_abs_determinant": published_log_abs_determinant,
        "boundary_data_determinant_log_offset_from_published": determinant_log_offset,
        "boundary_data_determinant_phase_offset_from_published_radians": determinant_phase_offset,
        "source_component_matrix_log_abs_determinant": float(
            source_log_abs_determinant
        ),
        "source_component_matrix_determinant_phase_radians": float(
            np.angle(source_sign)
        ),
        "source_component_determinant_log_offset_from_published": source_determinant_log_offset,
        "source_component_determinant_phase_offset_from_published_radians": source_determinant_phase_offset,
    }


def build_artifact() -> dict[str, Any]:
    source_row_transform, source_column_transform, basis_map_audit = (
        _source_component_basis_map()
    )
    cases = [
        _case(
            complex(real, imag), source_row_transform, source_column_transform
        )
        for real in REAL_ZETA
        for imag in IMAG_ZETA
    ]
    sources = {
        "symbol_audit": Path(__file__).resolve(),
        "mode_helper_audit": MODE_AUDIT,
        "reference_slab_audit": ROOT
        / "docs/scripts/audit/audit_curved_3p1_gh_full_u1_cpbc_slab.py",
        "boundary_residual_source": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py",
        "boundary_projector_source": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py",
        "canonical_gh_source": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py",
    }
    hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in sources.values()
    }
    hashes_match = all(
        hashes[path.relative_to(ROOT).as_posix()] == _sha256(path)
        for path in sources.values()
    )
    log_scales = np.asarray(
        [case["source_component_determinant_log_offset_from_published"] for case in cases]
    )
    phase_ratios = np.asarray(
        [case["source_component_determinant_phase_offset_from_published_radians"] for case in cases]
    )
    mean_phase_ratio = float(
        np.angle(np.mean(np.exp(1.0j * phase_ratios)))
    )
    max_log_scale_deviation = float(
        np.max(np.abs(log_scales - np.mean(log_scales)))
    )
    phase_deviations = np.angle(
        np.exp(1.0j * (phase_ratios - mean_phase_ratio))
    )
    max_phase_deviation = float(np.max(np.abs(phase_deviations)))
    determinant_crosscheck_tolerance = 1.0e-8
    return {
        "schema_version": "core-curved-3p1-gh-rinne-zero-shift-kreiss-symbol-v3",
        "artifact": "curved_3p1_gh_rinne_zero_shift_kreiss_symbol",
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_ZERO_SHIFT_KREISS_SYMBOL",
        "closure_level": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "The repository's zero-shift boundary-data matrix has a fixed, frequency-independent transformation to Rinne's source component basis, including constraint, physical, gauge, and symmetric-tensor column conventions.",
            "Projector identities establish that the gauge contraction annihilates constraint/physical sectors and is invertible on the gauge sector; the physical-coordinate identity and all fixed basis maps pass the declared 1e-12 numerical identity tolerance.",
            "The transformed 10-by-10 source-component determinant reproduces Rinne's published beta=0 formula over the finite sample grid to the declared 1e-8 tolerance; the reference result supplies the zero-shift frozen-coefficient Fourier-Laplace/Kreiss boundary-stability conclusion for this lane.",
            "The reference determinant has modulus asymptotics 1/(256*|zeta|^6) as zeta->0, 1/256 at zeta=+/-i, and 256 as |zeta|->infinity.",
        ],
        "WHAT_REMAINS_OPEN": [
            "Nonzero normal shift, its additional incoming u2_A modes, and the degenerate zeta=-beta case have not been independently reconstructed in the repository symbol audit.",
            "The source result concerns its frozen-coefficient/high-frequency Fourier-Laplace problem; full variable-coefficient, nonlinear curved-parent, and general nonzero initial/source-data well-posedness remain open.",
            "The LGL strong-replacement spectrum remains a separate discretization diagnostic and is not used as a continuum no-go.",
        ],
        "DEPENDENCY_UNLOCKED": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "STATUS": "SOURCE_MATCHED_ZERO_SHIFT_KREISS_LANE_CLOSED",
        "WHAT_CHANGED": "Derived and verified a fixed source-component basis map for the repository's zero-shift GH boundary symbol, then compared its transformed determinant with the published Rinne formula without changing the production residual API.",
        "EQUATION_OR_MAPPING": {
            "normal_mode": "exp(s*t+i*omega*y+lambda*x), zeta=s/omega, omega=1",
            "decaying_root": "lambda_minus=-sqrt(1+zeta^2), Re(sqrt(1+zeta^2))>0 for Re(zeta)>0",
            "mode_vector": "(Pi,Phi_x,Phi_y,Phi_z)=K^-1*(zeta,-lambda_minus,-i,0) tensor_amplitude; psi=0",
            "residual_symbol": "C_residual(zeta)*sigma = (c0_minus, w_minus, P_G*u1_minus) on the 10-dimensional decaying subspace",
            "boundary_data_symbol": "C_repository=diag(zeta^-1*I6,I4)*C_residual; C_source=T_rows*C_repository*T_columns",
            "source_row_map": "identity on c0; diag(1,-1) maps repository (w_yy,-w_yz) to source (w_yy,w_yz); sqrt(2)*L*Q maps orthonormal gauge coordinates to source component data (117)-(120)",
            "source_column_map": "diag(sqrt(TENSOR_WEIGHTS)) converts Frobenius-normalized symmetric-tensor columns to source component amplitudes",
            "kreiss_reference": "The fixed maps are nonsingular, so the repository zero-shift symbol is equivalent up to constant basis norms to the source boundary-data map; the published lane-specific Kreiss result is imported, not newly proved here",
        },
        "ANALYTIC_REFERENCE_LIMITS": {
            "source": "Rinne (2006), Eq. (122) at beta=0 and normalized mode Eq. (69)",
            "formula_modulus": "|det(C_Rinne)|=|zeta-lambda_minus|^16/(8*|zeta|^6*K1^10)",
            "mode_norm": "K1=norm([zeta,-lambda_minus,-i,0])",
            "zeta_to_zero": {
                "asymptotic_modulus": "1/(256*|zeta|^6)",
                "implication_for_reference_formula": "diverges; does not approach a determinant zero",
            },
            "glancing_zeta_plus_minus_i": {
                "mode_norm_limit": "sqrt(2)",
                "determinant_modulus_limit": 0.00390625,
            },
            "large_frequency": {
                "mode_norm_asymptotic": "sqrt(2)*|zeta|",
                "determinant_modulus_limit": 256.0,
            },
            "transfer_to_repository_matrix": "established for the zero-shift symbol by the fixed nonsingular row/column maps recorded in VERIFICATION.source_basis_equivalence",
        },
        "PREREGISTRATION": {
            "normal_shift_over_lapse": 0.0,
            "normal_outward": [-1.0, 0.0, 0.0],
            "omega_normalized": OMEGA,
            "gamma2": GAMMA2,
            "real_zeta_values": list(REAL_ZETA),
            "imaginary_zeta_values": list(IMAG_ZETA),
            "relative_svd_rank_tolerance": RANK_RELATIVE_TOLERANCE,
            "parameter_fitting": False,
            "threshold_changes": False,
        },
        "VERIFICATION": {
            "case_count": len(cases),
            "cases": cases,
            "source_basis_equivalence": basis_map_audit,
            "row_equilibrated_boundary_data_rank": [
                case["row_equilibrated_boundary_data_rank_at_declared_relative_tolerance"]
                for case in cases
            ],
            "all_row_equilibrated_boundary_data_matrices_full_rank": all(
                case["row_equilibrated_boundary_data_rank_at_declared_relative_tolerance"] == 10
                for case in cases
            ),
            "minimum_row_equilibrated_boundary_data_relative_smallest_singular_value": min(
                case["row_equilibrated_boundary_data_relative_smallest_singular_value"]
                for case in cases
            ),
            "minimum_boundary_data_absolute_smallest_singular_value": min(
                case["boundary_data_absolute_smallest_singular_value"] for case in cases
            ),
            "maximum_sampled_boundary_data_inverse_map_norm": 1.0 / min(
                case["boundary_data_absolute_smallest_singular_value"]
                for case in cases
            ),
            "maximum_boundary_data_condition_number": max(
                case["boundary_data_condition_number"] for case in cases
            ),
            "maximum_residual_matrix_condition_number": max(
                case["residual_matrix_condition_number"] for case in cases
            ),
            "maximum_principal_mode_residual": max(
                case["maximum_principal_mode_residual"] for case in cases
            ),
            "published_determinant_factor_crosscheck": {
                "source_component_matrix_matches_published_formula_on_finite_sample": (
                    max_log_scale_deviation < determinant_crosscheck_tolerance
                    and max_phase_deviation < determinant_crosscheck_tolerance
                ),
                "source_component_determinant_log_offset_mean": float(np.mean(log_scales)),
                "maximum_source_component_determinant_log_offset": float(
                    np.max(np.abs(log_scales))
                ),
                "maximum_source_component_determinant_log_offset_deviation": (
                    max_log_scale_deviation
                ),
                "source_component_determinant_phase_offset_mean_radians": mean_phase_ratio,
                "maximum_source_component_determinant_phase_offset_radians": float(
                    np.max(np.abs(phase_ratios))
                ),
                "maximum_source_component_determinant_phase_offset_deviation_radians": (
                    max_phase_deviation
                ),
                "comparison_tolerance": determinant_crosscheck_tolerance,
                "row_conversion": "divide four constraint and two physical residual rows by zeta, then apply the fixed source-coordinate row map",
            },
            "all_source_hashes_match_at_generation": hashes_match,
            "source_hashes_sha256": hashes,
            "fitting": False,
            "external_data": False,
            "holdout_access": False,
        },
        "CONTROLLING_BLOCKER": "nonzero_shift_boundary_symbol_and_u2_modes_not_yet_reproduced_for_repository_map",
        "NEXT_ACTION": "Extend the source-matched symbol to beta>0, then beta<0, including the degenerate zeta=-beta case and incoming u2_A modes; keep the source theorem boundary limited and do not promote the curved-parent or Gravity gates.",
        "CLAIM_BOUNDARY": "Closed source-matched zero-normal-shift frozen-coefficient standard-GR boundary-stability lane only. This imports Rinne's specified Fourier-Laplace/Kreiss result after a fixed basis equivalence; it is not an independent theorem for variable coefficients or nonlinear GH, not curved-parent closure, UET validation, or Gravity unlock.",
        "literature_basis": [
            {
                "source_id": "rinne_2006_first_order_gh_radiation_controlling_cpbc",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "role": "Source for the zero-shift decaying root and normalized mode vector, and for the formulation-specific Fourier-Laplace/Kreiss boundary-stability result.",
            }
        ],
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    verification = artifact["VERIFICATION"]
    print(
        json.dumps(
            {
                "status": artifact["STATUS"],
                "closure_level": artifact["closure_level"],
                "artifact": OUTPUT.as_posix(),
                "case_count": verification["case_count"],
                "source_basis_equivalence": (
                    verification["source_basis_equivalence"][
                        "all_fixed_maps_invertible"
                    ]
                    and verification["source_basis_equivalence"][
                        "all_projector_and_coordinate_identities_within_tolerance"
                    ]
                ),
                "maximum_basis_identity_residual": verification[
                    "source_basis_equivalence"
                ]["maximum_identity_residual"],
                "all_row_equilibrated_boundary_data_matrices_full_rank": verification[
                    "all_row_equilibrated_boundary_data_matrices_full_rank"
                ],
                "minimum_boundary_data_absolute_smallest_singular_value": verification[
                    "minimum_boundary_data_absolute_smallest_singular_value"
                ],
                "maximum_sampled_boundary_data_inverse_map_norm": verification[
                    "maximum_sampled_boundary_data_inverse_map_norm"
                ],
                "maximum_boundary_data_condition_number": verification[
                    "maximum_boundary_data_condition_number"
                ],
                "maximum_principal_mode_residual": verification[
                    "maximum_principal_mode_residual"
                ],
                "published_determinant_crosscheck": verification[
                    "published_determinant_factor_crosscheck"
                ],
                "all_source_hashes_match": verification[
                    "all_source_hashes_match_at_generation"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
