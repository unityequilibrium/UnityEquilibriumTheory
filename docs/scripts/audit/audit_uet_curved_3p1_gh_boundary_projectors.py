"""Verify local GH constraint/physical/gauge boundary projector algebra."""

from __future__ import annotations

import hashlib
import importlib
import itertools
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_projector_module = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_boundary_projectors"
)
apply_gh_boundary_projector = _projector_module.apply_gh_boundary_projector
build_gh_boundary_projectors = _projector_module.build_gh_boundary_projectors

OUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_boundary_projector_audit.json"
MODULE_SOURCE = "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
AUDIT_SOURCE = "docs/scripts/audit/audit_uet_curved_3p1_gh_boundary_projectors.py"
T13_SUPPORT_SOURCE = "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
RESIDUAL_TOLERANCE = 1.0e-12


def _directions() -> tuple[np.ndarray, ...]:
    values = [
        np.asarray(item, dtype=float)
        for item in itertools.product((-1.0, 0.0, 1.0), repeat=3)
        if item != (0.0, 0.0, 0.0)
    ]
    return tuple(value / np.linalg.norm(value) for value in values)


def build_artifact() -> dict[str, Any]:
    rng = np.random.default_rng(20260925)
    cases: list[dict[str, Any]] = []
    maximum_projector_residual = 0.0
    maximum_reconstruction_residual = 0.0
    maximum_physical_transversality_residual = 0.0
    maximum_physical_trace_residual = 0.0

    for direction in _directions():
        projectors = build_gh_boundary_projectors(direction)
        maximum_projector_residual = max(
            maximum_projector_residual, *projectors.residuals.values()
        )
        component_checks = []
        for _ in range(8):
            raw = rng.normal(size=(4, 4))
            incoming = 0.5 * (raw + raw.T)
            constraint = apply_gh_boundary_projector(incoming, projectors.constraint)
            physical = apply_gh_boundary_projector(incoming, projectors.physical)
            gauge = apply_gh_boundary_projector(incoming, projectors.gauge)
            reconstruction = float(np.max(np.abs(incoming - constraint - physical - gauge)))
            t_up = projectors.timelike_normal
            n_up = np.concatenate(([0.0], np.asarray(projectors.normal)))
            physical_transversality = max(
                float(np.max(np.abs(t_up @ physical))),
                float(np.max(np.abs(n_up @ physical))),
            )
            physical_trace = float(
                abs(np.einsum("ab,ab->", projectors.spatial_projector_contravariant, physical))
            )
            maximum_reconstruction_residual = max(maximum_reconstruction_residual, reconstruction)
            maximum_physical_transversality_residual = max(
                maximum_physical_transversality_residual, physical_transversality
            )
            maximum_physical_trace_residual = max(maximum_physical_trace_residual, physical_trace)
            component_checks.append(
                {
                    "reconstruction_residual": reconstruction,
                    "physical_transversality_residual": physical_transversality,
                    "physical_trace_residual": physical_trace,
                }
            )
        cases.append(
            {
                "normal": projectors.normal,
                "ranks": projectors.ranks,
                "projector_residuals": projectors.residuals,
                "component_sample_count": len(component_checks),
                "maximum_component_reconstruction_residual": max(
                    item["reconstruction_residual"] for item in component_checks
                ),
                "maximum_physical_transversality_residual": max(
                    item["physical_transversality_residual"] for item in component_checks
                ),
                "maximum_physical_trace_residual": max(
                    item["physical_trace_residual"] for item in component_checks
                ),
            }
        )

    checks = {
        "all_26_cube_directions_have_rank_4_2_4": all(
            case["ranks"] == {"constraint": 4, "physical": 2, "gauge": 4}
            for case in cases
        ),
        "all_projector_idempotence_completeness_and_cross_products_below_tolerance":
        maximum_projector_residual < RESIDUAL_TOLERANCE,
        "all_random_symmetric_inputs_reconstruct_below_tolerance":
        maximum_reconstruction_residual < RESIDUAL_TOLERANCE,
        "physical_projection_is_transverse_and_trace_free":
        max(maximum_physical_transversality_residual, maximum_physical_trace_residual)
        < RESIDUAL_TOLERANCE,
    }
    passed = all(checks.values())
    source_paths = (MODULE_SOURCE, AUDIT_SOURCE, T13_SUPPORT_SOURCE)
    return {
        "schema_version": "core-curved-3p1-gh-boundary-projectors-v1",
        "diagnostic_id": "uet.curved_3p1.gh.boundary_projector_decomposition",
        "artifact": "curved_3p1_gh_boundary_projector_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_GH_BOUNDARY_PROJECTOR_DECOMPOSITION" if passed else "FAIL_GH_BOUNDARY_PROJECTOR_DECOMPOSITION",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_BOUNDARY_PROJECTOR_DECOMPOSITION",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "local constraint, physical-radiation, and gauge projector algebra on the ten-dimensional symmetric spacetime-tensor space",
                "projector ranks 4/2/4, idempotence, completeness, and pairwise annihilation across 26 local face normals",
                "physical projector transversality and trace-free properties on deterministic tensor controls",
            ] if passed else [],
            "equation_or_mapping": {
                "equation_id": "uet.main_theory.curved_3p1.generalized_harmonic_principal_system",
                "source_formula_locators": ["Rinne 2006 Eqs. (27)-(28), (32)-(35)"],
                "incoming_tensor_split": "u1_minus = P_C u1_minus + P_P u1_minus + P_G u1_minus; ranks 4 + 2 + 4",
                "constraint_boundary_class": "differential normal-derivative condition on P_C u1_minus",
                "physical_boundary_class": "differential Weyl/Psi_0 condition on P_P u1_minus",
                "gauge_boundary_class": "algebraic prescription for P_G u1_minus",
                "applicable_incoming_regime": "-alpha < beta_n <= 0; positive beta_n additionally admits incoming u2_A modes",
            },
            "units": "geometric c=1; local orthonormal frame",
            "derivation_class": "imported GH boundary projectors plus deterministic finite-dimensional algebra verification",
            "observable": "projector ranks, algebraic residuals, and tensor transversality/trace residuals",
            "data_role": "internal analytic controls; no physical source data",
            "verification_status": "PASS_GH_BOUNDARY_PROJECTOR_DECOMPOSITION" if passed else "FAIL_GH_BOUNDARY_PROJECTOR_DECOMPOSITION",
            "open_blockers": [
                "differential CPBC residuals are not implemented",
                "physical incoming Weyl data and gauge data are not applied to the periodic solver",
                "positive-normal-shift incoming u2_A constraint boundary system is not implemented",
                "no non-periodic SBP/SAT initial-boundary evolution or boundary-convergence result",
                "no full variable-coefficient nonlinear GH boundary well-posedness proof",
            ],
            "dependency_unlocked": "projector/decomposition design only; curved 3+1 parent remains PARTIAL and Gravity remains blocked",
            "claim_boundary": "This closes only the local 4/2/4 GH boundary-projector algebra. It is not an implemented CPBC, does not prove well-posedness for the repo solver, and does not validate a non-periodic evolution.",
        },
        "scope": {
            "state_variables": ["symmetric u1_minus_ab tensor"],
            "excluded_variables": ["UET C", "UET Phi", "R_gen", "R_obs"],
            "notation_boundary": "GH Phi_iab is a spatial derivative variable, distinct from UET effective-response Phi.",
            "local_frame_signature": "(-,+,+,+)",
            "normal_count": len(cases),
            "symmetric_tensor_dimension": 10,
            "projector_rank_contract": {"constraint": 4, "physical": 2, "gauge": 4},
            "boundary_operator_applied": False,
            "periodic_solver_modified": False,
            "holdout_or_external_data_used": False,
        },
        "case_count": len(cases),
        "random_symmetric_tensor_samples_per_case": 8,
        "residual_tolerance": RESIDUAL_TOLERANCE,
        "maximum_projector_residual": maximum_projector_residual,
        "maximum_reconstruction_residual": maximum_reconstruction_residual,
        "maximum_physical_transversality_residual": maximum_physical_transversality_residual,
        "maximum_physical_trace_residual": maximum_physical_trace_residual,
        "checks": checks,
        "cases": cases,
        "source_hashes": {
            relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            for relative in source_paths
        },
        "literature_basis": [
            {
                "citation": "O. Rinne, Stable radiation-controlling boundary conditions for the generalized harmonic Einstein equations, Class. Quantum Grav. 23, 6275-6300 (2006)",
                "doi": "10.1088/0264-9381/23/22/013",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "role": "source for constraint, physical, and gauge projector decomposition and the distinct differential/algebraic boundary-condition classes",
            },
            {
                "citation": "G. Calabrese and O. Sarbach, Detecting ill posed boundary conditions in General Relativity, J. Math. Phys. 44, 3888-3899 (2003)",
                "doi": "10.1063/1.1599056",
                "url": "https://arxiv.org/abs/gr-qc/0303040",
                "role": "well-posedness caution: constraint-consistent prescriptions alone are insufficient for arbitrary formulation parameters",
            },
        ],
        "claim_boundary": "Local projector algebra only. The source project's boundary-stability analysis is not inherited by this implementation; no CPBC, IBVP, Gravity, or global UET claim is promoted.",
    }


def main() -> int:
    artifact = build_artifact()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "case_count": artifact["case_count"],
                "maximum_projector_residual": artifact["maximum_projector_residual"],
                "checks": artifact["checks"],
                "artifact": OUT.relative_to(ROOT).as_posix(),
            },
            indent=2,
        )
    )
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
