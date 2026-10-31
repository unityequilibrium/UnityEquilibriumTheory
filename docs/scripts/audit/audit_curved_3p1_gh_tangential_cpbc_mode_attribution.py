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
SPECTRUM_AUDIT = (
    ROOT / "docs/scripts/audit/audit_curved_3p1_gh_tangential_cpbc_spectrum.py"
)
OUTPUT = (
    ROOT
    / "docs/core/07_artifacts/verification/"
    / "curved_3p1_gh_tangential_cpbc_mode_attribution.json"
)

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_gh_spectrum_audit", SPECTRUM_AUDIT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the source-matched GH spectrum audit")
SPECTRUM = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = SPECTRUM
_spec.loader.exec_module(SPECTRUM)
MODE = SPECTRUM.MODE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _spectrum_summary(operator: np.ndarray) -> dict[str, Any]:
    eigenvalues = np.linalg.eigvals(operator)
    order = np.argsort(eigenvalues.real)[::-1]
    return {
        "spectral_abscissa_over_L0_inverse": float(np.max(eigenvalues.real)),
        "positive_mode_count_above_existing_1e-6_tolerance": int(
            np.count_nonzero(eigenvalues.real > 1.0e-6)
        ),
        "leading_eigenvalues_over_L0_inverse": [
            {"real": float(value.real), "imag": float(value.imag)}
            for value in eigenvalues[order[:8]]
        ],
    }


def _bulk_operator(
    grid: Any, gamma2: float, gamma0: float
) -> np.ndarray:
    dimension = SPECTRUM._state_size(grid.node_count)
    operator = np.empty((dimension, dimension), dtype=float)
    basis = np.zeros(dimension, dtype=float)
    for column in range(dimension):
        basis[column] = 1.0
        rhs = SPECTRUM._bulk_rhs(
            grid,
            SPECTRUM._unpack(basis, grid.node_count),
            gamma2,
            gamma0,
        )
        operator[:, column] = SPECTRUM._flatten(rhs)
        basis[column] = 0.0
    return operator


def _unpack_complex_symmetric(values: np.ndarray) -> np.ndarray:
    tensor = np.zeros((4, 4), dtype=complex)
    for value, (row, column) in zip(values, MODE.PAIRS):
        tensor[row, column] = value
        tensor[column, row] = value
    return tensor


def _constraint_norm(
    state: tuple[np.ndarray, ...], spatial_weights: np.ndarray
) -> float:
    _, pi, phi = state
    eta = np.array([-1.0, 1.0, 1.0, 1.0])
    values = np.zeros((pi.shape[0], pi.shape[1], 4), dtype=complex)
    for node in range(pi.shape[0]):
        for phase in range(pi.shape[1]):
            derivative_fields = [
                -_unpack_complex_symmetric(pi[node, phase]),
                *(
                    _unpack_complex_symmetric(phi[node, phase, direction])
                    for direction in range(3)
                ),
            ]
            for component in range(4):
                divergence = sum(
                    eta[direction]
                    * derivative_fields[direction][component, direction]
                    for direction in range(4)
                )
                trace_derivative = sum(
                    eta[index]
                    * derivative_fields[component][index, index]
                    for index in range(4)
                )
                values[node, phase, component] = (
                    divergence - 0.5 * trace_derivative
                )
    return float(
        np.sqrt(
            np.sum(
                spatial_weights[:, None, None] * np.abs(values) ** 2
            )
        )
    )


def _incoming_sector_fractions(
    state: tuple[np.ndarray, ...], gamma2: float
) -> dict[str, Any]:
    metric, pi, phi = state
    sector_names = ("constraint", "physical", "gauge")
    total_norms = {name: 0.0 for name in sector_names}
    face_results: dict[str, Any] = {}
    for face, normal, label in (
        (0, -1.0, "left"),
        (metric.shape[0] - 1, 1.0, "right"),
    ):
        projectors = MODE.PROJECTORS.build_gh_boundary_projectors(
            np.array([normal, 0.0, 0.0])
        )
        projector_map = {
            "constraint": projectors.constraint,
            "physical": projectors.physical,
            "gauge": projectors.gauge,
        }
        norms = {name: 0.0 for name in sector_names}
        incoming_norm = 0.0
        reconstruction_norm = 0.0
        for phase in range(metric.shape[1]):
            incoming = (
                pi[face, phase]
                - normal * phi[face, phase, 0]
                - gamma2 * metric[face, phase]
            )
            incoming_norm += float(
                np.sum(np.abs(incoming) ** 2 * MODE.TENSOR_WEIGHTS)
            )
            reconstructed = np.zeros_like(incoming)
            for name, projector in projector_map.items():
                projected = projector @ incoming
                reconstructed += projected
                norms[name] += float(
                    np.sum(np.abs(projected) ** 2 * MODE.TENSOR_WEIGHTS)
                )
            reconstruction_norm += float(
                np.sum(
                    np.abs(incoming - reconstructed) ** 2
                    * MODE.TENSOR_WEIGHTS
                )
            )
        sector_sum = sum(norms.values())
        fractions = {
            name: (value / sector_sum if sector_sum else 0.0)
            for name, value in norms.items()
        }
        face_results[label] = {
            "incoming_characteristic_norm_squared": incoming_norm,
            "projected_sector_norm_squared": norms,
            "projected_sector_fractions": fractions,
            "projector_reconstruction_relative_residual": float(
                np.sqrt(reconstruction_norm)
                / max(np.sqrt(incoming_norm), 1.0e-300)
            ),
        }
        for name, value in norms.items():
            total_norms[name] += value
    total = sum(total_norms.values())
    return {
        "faces": face_results,
        "two_face_projected_sector_fractions": {
            name: (value / total if total else 0.0)
            for name, value in total_norms.items()
        },
    }


def _mode_energy(
    state: tuple[np.ndarray, ...],
    spatial_weights: np.ndarray,
    gamma2: float,
) -> float:
    metric, pi, phi = state
    density = (
        4.0 * np.abs(metric) ** 2
        - 2.0 * gamma2 * np.real(np.conjugate(metric) * pi)
        + np.abs(pi) ** 2
        + np.sum(np.abs(phi) ** 2, axis=2)
    )
    return float(
        0.5
        * np.sum(
            density
            * spatial_weights[:, None, None]
            * MODE.TENSOR_WEIGHTS
        )
    )


def build_artifact() -> dict[str, Any]:
    degree = 12
    wave_number = float(np.pi)
    gamma0 = 1.0
    gamma2 = 1.0
    spectrum_artifact_path = SPECTRUM.OUTPUT
    spectrum_artifact = json.loads(
        spectrum_artifact_path.read_text(encoding="utf-8")
    )
    spectrum_source_hash = spectrum_artifact["VERIFICATION"][
        "source_hashes_sha256"
    ].get(SPECTRUM_AUDIT.relative_to(ROOT).as_posix())
    if spectrum_source_hash != _sha256(SPECTRUM_AUDIT):
        raise RuntimeError(
            "the spectrum artifact is stale relative to its audit source; "
            "rerun the matched spectrum audit first"
        )
    grid = MODE.TangentialGrid(degree, wave_number)
    operators = SPECTRUM.LGL.legendre_lobatto_operators(degree)
    grid.nodes = operators.nodes
    grid.derivative = operators.derivative
    grid.node_count = len(grid.nodes)

    full_operator = SPECTRUM._assemble_rhs_matrix(
        grid, gamma2=gamma2, gamma0=gamma0
    )
    eigenvalues, eigenvectors = np.linalg.eig(full_operator)
    positive_indices = np.flatnonzero(eigenvalues.real > 1.0e-6)
    mode_records: list[dict[str, Any]] = []
    for index in positive_indices:
        eigenvalue = eigenvalues[index]
        vector = eigenvectors[:, index]
        vector_norm = float(np.linalg.norm(vector))
        vector = vector / vector_norm
        residual = full_operator @ vector - eigenvalue * vector
        relative_residual = float(
            np.linalg.norm(residual)
            / max(
                np.linalg.norm(full_operator @ vector),
                abs(eigenvalue) * np.linalg.norm(vector),
                1.0e-300,
            )
        )
        state = SPECTRUM._unpack(vector, grid.node_count)
        energy = _mode_energy(state, operators.norm_weights, gamma2)
        mode_records.append(
            {
                "eigenvalue_over_L0_inverse": {
                    "real": float(eigenvalue.real),
                    "imag": float(eigenvalue.imag),
                },
                "right_eigenvector_relative_residual": relative_residual,
                "normalized_gh_energy": energy,
                "harmonic_constraint_l2_over_slab": _constraint_norm(
                    state, operators.norm_weights
                ),
                "incoming_sector_decomposition": _incoming_sector_fractions(
                    state, gamma2
                ),
            }
        )

    no_damping_operator = SPECTRUM._assemble_rhs_matrix(
        grid, gamma2=gamma2, gamma0=0.0
    )
    no_damping_summary = _spectrum_summary(no_damping_operator)
    bulk_operator = _bulk_operator(grid, gamma2=gamma2, gamma0=gamma0)
    bulk_summary = _spectrum_summary(bulk_operator)

    case = next(
        result
        for result in spectrum_artifact["VERIFICATION"]["cases"]
        if result["normal_operator_family"] == "legendre_gauss_lobatto_sbp"
        and result["degree"] == degree
        and np.isclose(result["tangential_wavenumber_over_L0"], wave_number)
    )
    sources = {
        "mode_attribution_audit": Path(__file__).resolve(),
        "spectrum_audit": SPECTRUM_AUDIT,
        "spectrum_artifact_input": spectrum_artifact_path,
        "matched_profile_audit": SPECTRUM.MODE_AUDIT,
        "lgl_sbp_operator_audit": SPECTRUM.LGL_AUDIT,
        "boundary_residuals": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_linear_boundary.py",
        "boundary_projectors": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py",
        "slab_equations": ROOT
        / "docs/core/02_equations/covariant/uet_curved_3p1_gh_full_u1_slab.py",
        "canonical_gh_equations": MODE.GH_EQUATIONS,
    }
    source_hashes = {
        path.relative_to(ROOT).as_posix(): _sha256(path)
        for path in sources.values()
    }
    return {
        "schema_version": "core-curved-3p1-gh-mode-attribution-v1",
        "artifact": "curved_3p1_gh_tangential_cpbc_mode_attribution",
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "major_result_id": "CORE_CURVED_3P1_GH_TANGENTIAL_CPBC_POSITIVE_MODE_ATTRIBUTION",
        "closure_level": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "The 16 positive-real-part modes in the declared LGL degree-12, k_y*L0=pi, gamma0*L0=gamma2*L0=1 finite operator are represented by right eigenvectors and checked against the assembled RHS.",
            "The incoming constraint/physical/gauge projector content of those modes is measured separately at both slab faces.",
            "A gamma0=0 structural control retains the growing-mode count and nearly the same spectral abscissa, so constraint damping alone does not explain this finite-grid growth.",
            "The uncorrected bulk RHS has a broader positive spectrum; the registered boundary correction reduces, but does not eliminate, the positive-mode count in this finite-grid comparison.",
        ],
        "WHAT_REMAINS_OPEN": [
            "Mode-sector content is a finite-grid incoming-characteristic decomposition, not proof that the modes are pure constraint, physical, or gauge solutions in the continuum.",
            "No spatial-resolution convergence study of this tangential growing spectrum has been completed.",
            "The bulk-only control omits boundary closure and is not a well-posed initial-boundary evolution.",
            "The result does not establish continuum or nonlinear GH initial-boundary instability, nor does it close the curved 3+1 parent.",
        ],
        "DEPENDENCY_UNLOCKED": "none; the Core curved-3+1 parent remains PARTIAL and Gravity remains blocked",
        "STATUS": "OPEN_EXPLORATORY_MODE_ATTRIBUTION",
        "WHAT_CHANGED": "Added an eigenvector-level attribution screen for the isolated LGL tangential spectrum, including both-face characteristic projector fractions, a constraint-damping ablation, and a bulk-only reference control.",
        "EQUATION_OR_MAPPING": {
            "semidiscrete_system": "U_dot = A_h(k_y) U for the source-matched frozen-background linear GH slab",
            "boundary_characteristic": "q_in = Pi - n*Phi_x - gamma2*psi",
            "sector_map": "q_in = P_constraint*q_in + P_physical*q_in + P_gauge*q_in, evaluated independently on left and right",
            "harmonic_constraint": "C_a = eta^(bc)*partial_b h_ac - 0.5*eta^(bc)*partial_a h_bc using (Pi, Phi_i) in the registered first-order state",
            "energy": "E = 0.5*integral(4|psi|^2 - 2*gamma2*Re(conj(psi)*Pi) + |Pi|^2 + sum_i|Phi_i|^2) d(x/L0), with LGL norm and tensor Frobenius weights",
        },
        "PREREGISTRATION": {
            "operator_family": "Legendre-Gauss-Lobatto diagonal-norm SBP",
            "degree": degree,
            "tangential_wavenumber_over_L0": wave_number,
            "gamma0_L0": gamma0,
            "gamma2_L0": gamma2,
            "positive_real_part_reference_tolerance": 1.0e-6,
            "control_cases": [
                "full boundary RHS with gamma0=0",
                "bulk RHS without boundary correction at gamma0=1",
            ],
            "decision_policy": "Post-observation structural attribution only; no fitting, no threshold changes, no dependency unlock",
        },
        "VERIFICATION": {
            "baseline_case": {
                "spectral_abscissa_over_L0_inverse": case[
                    "spectral_abscissa_over_L0_inverse"
                ],
                "positive_mode_count_above_existing_1e-6_tolerance": case[
                    "eigenvalue_count_real_part_above_existing_1e-6_tolerance"
                ],
                "sbp_identity_relative_frobenius_residual": case[
                    "sbp_identity_relative_frobenius_residual"
                ],
                "matrix_rhs_probe_relative_residual": case[
                    "operator_assembly_probe_relative_residual"
                ],
                "recomputed_positive_eigenvalue_count_matches_source_artifact": (
                    len(positive_indices)
                    == case[
                        "eigenvalue_count_real_part_above_existing_1e-6_tolerance"
                    ]
                ),
                "recomputed_spectral_abscissa_abs_difference": abs(
                    float(np.max(eigenvalues.real))
                    - case["spectral_abscissa_over_L0_inverse"]
                ),
            },
            "positive_mode_count": len(mode_records),
            "positive_mode_records": mode_records,
            "gamma0_zero_full_boundary_control": no_damping_summary,
            "bulk_rhs_without_boundary_correction_control": bulk_summary,
            "maximum_right_eigenvector_relative_residual": max(
                (record["right_eigenvector_relative_residual"] for record in mode_records),
                default=0.0,
            ),
            "maximum_projector_reconstruction_relative_residual": max(
                record["incoming_sector_decomposition"]["faces"][face][
                    "projector_reconstruction_relative_residual"
                ]
                for record in mode_records
                for face in ("left", "right")
            ),
            "source_hashes_sha256": source_hashes,
            "fitting": False,
            "clipping": False,
            "external_data": False,
            "holdout_access": False,
        },
        "CONTROLLING_BLOCKER": "full_first_order_gh_differential_cpbc_stability_and_resolution_convergence_missing",
        "NEXT_ACTION": "Use the measured incoming-sector composition to target a projector-compatible SBP-SAT energy estimate; then test adjacent LGL orders at the same wavenumber without changing thresholds.",
        "CLAIM_BOUNDARY": "Finite-grid, frozen-background standard-GR linear-boundary mode attribution only; not continuum instability, nonlinear well-posedness, UET validation, curved 3+1 parent closure, or Gravity unlock.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    fractions = [
        mode["incoming_sector_decomposition"][
            "two_face_projected_sector_fractions"
        ]
        for mode in artifact["VERIFICATION"]["positive_mode_records"]
    ]
    print(
        json.dumps(
            {
                "status": artifact["STATUS"],
                "artifact": OUTPUT.as_posix(),
                "positive_mode_count": artifact["VERIFICATION"][
                    "positive_mode_count"
                ],
                "gamma0_zero_control": artifact["VERIFICATION"][
                    "gamma0_zero_full_boundary_control"
                ],
                "bulk_only_control": artifact["VERIFICATION"][
                    "bulk_rhs_without_boundary_correction_control"
                ],
                "mean_incoming_sector_fractions": {
                    name: float(np.mean([row[name] for row in fractions]))
                    for name in ("constraint", "physical", "gauge")
                },
                "max_eigenvector_residual": artifact["VERIFICATION"][
                    "maximum_right_eigenvector_relative_residual"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
