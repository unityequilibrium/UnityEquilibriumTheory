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
SPECTRUM_ARTIFACT = (
    ROOT / "docs/core/07_artifacts/verification/"
    / "curved_3p1_gh_tangential_cpbc_spectrum.json"
)
OUTPUT = (
    ROOT / "docs/core/07_artifacts/verification/"
    / "curved_3p1_gh_tangential_cpbc_resolution_refinement.json"
)

_spec = importlib.util.spec_from_file_location(
    "_uet_curved_3p1_gh_refinement_spectrum_audit", SPECTRUM_AUDIT
)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load the registered GH spectrum audit")
SPECTRUM = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = SPECTRUM
_spec.loader.exec_module(SPECTRUM)
MODE = SPECTRUM.MODE


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _case(degree: int, wave_number: float) -> dict[str, Any]:
    grid = MODE.TangentialGrid(degree, wave_number)
    operators = SPECTRUM.LGL.legendre_lobatto_operators(degree)
    grid.nodes = operators.nodes
    grid.derivative = operators.derivative
    grid.node_count = len(grid.nodes)
    gamma0 = 1.0
    gamma2 = 1.0

    norm_matrix = np.diag(operators.norm_weights)
    boundary_form = np.zeros_like(norm_matrix)
    boundary_form[0, 0] = -1.0
    boundary_form[-1, -1] = 1.0
    sbp_residual = (
        norm_matrix @ grid.derivative
        + grid.derivative.T @ norm_matrix
        - boundary_form
    )
    sbp_scale = max(
        float(np.linalg.norm(norm_matrix @ grid.derivative, ord="fro")),
        float(np.linalg.norm(boundary_form, ord="fro")),
        1.0,
    )
    operator = SPECTRUM._assemble_rhs_matrix(grid, gamma2, gamma0)
    eigenvalues = np.linalg.eigvals(operator)
    rng = np.random.default_rng(12000 + degree)
    probe = rng.standard_normal(operator.shape[0])
    direct_rhs = SPECTRUM._flatten(
        MODE._rhs(
            grid,
            SPECTRUM._unpack(probe, grid.node_count),
            gamma2,
            gamma0,
        )
    )
    matrix_rhs = operator @ probe
    probe_residual = float(
        np.linalg.norm(direct_rhs - matrix_rhs)
        / max(np.linalg.norm(direct_rhs), np.linalg.norm(matrix_rhs), 1.0e-300)
    )
    order = np.argsort(eigenvalues.real)[::-1]
    return {
        "degree": degree,
        "node_count": grid.node_count,
        "state_dimension": int(operator.shape[0]),
        "tangential_wavenumber_over_L0": wave_number,
        "gamma0_L0": gamma0,
        "gamma2_L0": gamma2,
        "normal_operator_family": "legendre_gauss_lobatto_sbp",
        "sbp_identity_relative_frobenius_residual": float(
            np.linalg.norm(sbp_residual, ord="fro") / sbp_scale
        ),
        "spectral_abscissa_over_L0_inverse": float(np.max(eigenvalues.real)),
        "positive_mode_count_above_existing_1e-6_tolerance": int(
            np.count_nonzero(eigenvalues.real > 1.0e-6)
        ),
        "leading_eigenvalues_over_L0_inverse": [
            {"real": float(value.real), "imag": float(value.imag)}
            for value in eigenvalues[order[:8]]
        ],
        "operator_assembly_probe_relative_residual": probe_residual,
    }


def build_artifact() -> dict[str, Any]:
    source_artifact = json.loads(
        SPECTRUM_ARTIFACT.read_text(encoding="utf-8")
    )
    source_hash = source_artifact["VERIFICATION"]["source_hashes_sha256"].get(
        SPECTRUM_AUDIT.relative_to(ROOT).as_posix()
    )
    if source_hash != _sha256(SPECTRUM_AUDIT):
        raise RuntimeError(
            "the source spectrum artifact is stale; rerun it before refinement"
        )

    wave_number = float(np.pi)
    baseline = [
        {
            **case,
            "origin": "source_locked_degree8_or_12_baseline",
            "positive_mode_count_above_existing_1e-6_tolerance": case[
                "eigenvalue_count_real_part_above_existing_1e-6_tolerance"
            ],
        }
        for case in source_artifact["VERIFICATION"]["cases"]
        if case["normal_operator_family"] == "legendre_gauss_lobatto_sbp"
        and case["degree"] in (8, 12)
        and np.isclose(case["tangential_wavenumber_over_L0"], wave_number)
    ]
    if {case["degree"] for case in baseline} != {8, 12}:
        raise RuntimeError("source artifact lacks the required degree-8/12 baselines")

    refined = [
        dict(_case(degree, wave_number), origin="followup_exploratory_refinement")
        for degree in (10, 14, 16)
    ]
    cases = sorted(baseline + refined, key=lambda row: row["degree"])
    sources = {
        "resolution_refinement_audit": Path(__file__).resolve(),
        "spectrum_audit": SPECTRUM_AUDIT,
        "spectrum_artifact_input": SPECTRUM_ARTIFACT,
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
        "schema_version": "core-curved-3p1-gh-tangential-refinement-v1",
        "artifact": "curved_3p1_gh_tangential_cpbc_resolution_refinement",
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "MAJOR_RESULT_CLOSURE": "PARTIAL",
        "major_result_id": "CORE_CURVED_3P1_GH_TANGENTIAL_CPBC_RESOLUTION_REFINEMENT",
        "closure_level": "PARTIAL",
        "WHAT_IS_ACTUALLY_CLOSED": [
            "A fixed tangential wavenumber k_y*L0=pi and fixed damping parameters are compared across LGL degrees 8, 10, 12, 14, and 16.",
            "Degrees 8 and 12 are linked to the source-hashed matched-spectrum artifact; degrees 10, 14, and 16 are recalculated with the same full boundary RHS.",
            "Each newly assembled case records the exact SBP identity defect, direct-RHS assembly residual, spectral abscissa, and positive-mode count under the unchanged 1e-6 reference threshold.",
        ],
        "WHAT_REMAINS_OPEN": [
            "This is an exploratory follow-up after the degree-12 mode was observed; it is not a preregistered external confirmation.",
            "Finite-grid spectral persistence or disappearance does not prove continuum well-posedness or instability.",
            "No projector-compatible energy estimate, nonlinear evolution, positive shift, edges/corners, or matter boundary is closed.",
        ],
        "DEPENDENCY_UNLOCKED": "none; the Core curved-3+1 parent remains PARTIAL and Gravity remains blocked",
        "STATUS": "OPEN_TANGENTIAL_LGL_RESOLUTION_REFINEMENT",
        "WHAT_CHANGED": "Added a fixed-wavenumber LGL order refinement around the isolated degree-12 tangential growth case, keeping the registered full boundary RHS and all existing thresholds unchanged.",
        "EQUATION_OR_MAPPING": {
            "semidiscrete_system": "U_dot = A_h(k_y) U with the registered full first-order GH RHS and differential CPBC targets",
            "sbp_identity": "H D + D^T H = diag(-1, 0, ..., 0, +1)",
            "spectral_diagnostic": "max(Re(lambda(A_h))) and count(Re(lambda)>1e-6)",
            "fixed_parameters": "k_y*L0=pi; gamma0*L0=gamma2*L0=1",
        },
        "PREREGISTRATION": {
            "operator_family": "Legendre-Gauss-Lobatto diagonal-norm SBP",
            "degrees": [8, 10, 12, 14, 16],
            "tangential_wavenumber_over_L0": wave_number,
            "gamma0_L0": 1.0,
            "gamma2_L0": 1.0,
            "positive_real_part_reference_tolerance": 1.0e-6,
            "parameter_fitting": False,
            "threshold_changes": False,
        },
        "VERIFICATION": {
            "cases": cases,
            "positive_mode_case_count": sum(
                case["positive_mode_count_above_existing_1e-6_tolerance"] > 0
                for case in cases
            ),
            "case_count": len(cases),
            "all_cases_have_sbp_and_rhs_residuals": all(
                "sbp_identity_relative_frobenius_residual" in case
                and "operator_assembly_probe_relative_residual" in case
                for case in cases
            ),
            "all_source_hashes_match_at_generation": True,
            "source_hashes_sha256": source_hashes,
            "fitting": False,
            "clipping": False,
            "external_data": False,
            "holdout_access": False,
        },
        "CONTROLLING_BLOCKER": "full_first_order_gh_differential_cpbc_stability_and_resolution_convergence_missing",
        "NEXT_ACTION": "Interpret the order trend together with the physical-heavy mode attribution, then derive the two-face projector-compatible boundary energy estimate before broadening to more wavenumbers.",
        "CLAIM_BOUNDARY": "Exploratory finite-grid, frozen-background standard-GR diagnostic only; not a continuum result, UET validation, Core-parent closure, or Gravity unlock.",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": artifact["STATUS"],
                "artifact": OUTPUT.as_posix(),
                "cases": [
                    {
                        "degree": case["degree"],
                        "origin": case["origin"],
                        "spectral_abscissa": case[
                            "spectral_abscissa_over_L0_inverse"
                        ],
                        "positive_modes": case[
                            "positive_mode_count_above_existing_1e-6_tolerance"
                        ],
                        "sbp_residual": case[
                            "sbp_identity_relative_frobenius_residual"
                        ],
                        "rhs_probe_residual": case[
                            "operator_assembly_probe_relative_residual"
                        ],
                    }
                    for case in artifact["VERIFICATION"]["cases"]
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
