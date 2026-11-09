"""Audit local GH characteristic incidence at candidate outer boundaries.

This is a principal-symbol preflight only. It does not impose constraint-
preserving boundary data or integrate a non-periodic initial-boundary problem.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_curved_3p1_generalized_harmonic import (
    GHParameters,
    gh_principal_symbol,
    reconstruct_gh_state,
)


OUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_boundary_characteristic_audit.json"
GH_SOURCE = "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
AUDIT_SOURCE = "docs/scripts/audit/audit_curved_3p1_gh_boundary_characteristics.py"
MODE_LABELS = ("u0", "u1_plus", "u1_minus", "u2_tangent_1", "u2_tangent_2")


def classify_boundary_modes(
    direction: Any,
    parameters: GHParameters,
    *,
    speed_tolerance: float = 1.0e-10,
) -> dict[str, Any]:
    """Classify the implemented five-field GH principal block at one face."""

    tolerance = float(speed_tolerance)
    if not isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("speed_tolerance must be finite and positive")
    symbol = gh_principal_symbol(direction, parameters)
    speeds = tuple(float(value) for value in symbol.characteristic_speeds)
    normal_shift = float(np.asarray(parameters.shift, dtype=float) @ symbol.normal)
    incoming = tuple(
        label for label, speed in zip(MODE_LABELS, speeds) if speed < -tolerance
    )
    outgoing = tuple(
        label for label, speed in zip(MODE_LABELS, speeds) if speed > tolerance
    )
    glancing = tuple(
        label for label, speed in zip(MODE_LABELS, speeds) if abs(speed) <= tolerance
    )
    return {
        "normal": tuple(float(value) for value in symbol.normal),
        "normal_shift": normal_shift,
        "lapse": float(parameters.lapse),
        "characteristic_speeds": speeds,
        "incoming_modes": incoming,
        "outgoing_modes": outgoing,
        "glancing_modes": glancing,
        "reference_shift_domain": (
            "SUBLUMINAL_SHIFT"
            if abs(normal_shift) < float(parameters.lapse) - tolerance
            else "OUTSIDE_SUBLUMINAL_SHIFT_ASSUMPTIONS"
        ),
        "characteristic_rank": symbol.eigenvector_rank,
        "characteristic_residual": symbol.characteristic_residual,
        "symmetrizer_residual": symbol.symmetrizer_residual,
        "minimum_symmetrizer_eigenvalue": symbol.minimum_symmetrizer_eigenvalue,
    }


def principal_energy_flux(
    state: Any,
    direction: Any,
    parameters: GHParameters,
) -> float:
    """Return the frozen-principal outward flux for d_t U + A_n d_n U = 0."""

    block = np.asarray(state, dtype=float)
    if block.shape != (5,) or not np.all(np.isfinite(block)):
        raise ValueError("state must be a finite five-component GH principal block")
    symbol = gh_principal_symbol(direction, parameters)
    return float(0.5 * block @ symbol.symmetrizer @ symbol.matrix @ block)


def _unit_tangent(normal: np.ndarray) -> np.ndarray:
    seed = np.array([0.0, 0.0, 1.0])
    if abs(float(seed @ normal)) > 0.8:
        seed = np.array([1.0, 0.0, 0.0])
    tangent = seed - float(seed @ normal) * normal
    return tangent / np.linalg.norm(tangent)


def _expected_partition(shift_ratio: float) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    if shift_ratio < -1.0:
        return (), ("u1_plus", "u1_minus", "u2_tangent_1", "u2_tangent_2"), ("u0",)
    if shift_ratio == -1.0:
        return (), ("u1_plus", "u2_tangent_1", "u2_tangent_2"), ("u0", "u1_minus")
    if shift_ratio < 0.0:
        return ("u1_minus",), ("u1_plus", "u2_tangent_1", "u2_tangent_2"), ("u0",)
    if shift_ratio == 0.0:
        return ("u1_minus",), ("u1_plus",), ("u0", "u2_tangent_1", "u2_tangent_2")
    if shift_ratio < 1.0:
        return ("u1_minus", "u2_tangent_1", "u2_tangent_2"), ("u1_plus",), ("u0",)
    if shift_ratio == 1.0:
        return ("u1_minus", "u2_tangent_1", "u2_tangent_2"), (), ("u0", "u1_plus")
    return ("u1_plus", "u1_minus", "u2_tangent_1", "u2_tangent_2"), (), ("u0",)


def build_artifact() -> dict[str, Any]:
    directions = (
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([1.0, 2.0, 2.0]) / 3.0,
        np.array([-2.0, 1.0, -2.0]) / 3.0,
    )
    shift_ratios = (-1.25, -1.0, -0.5, 0.0, 0.5, 1.0, 1.25)
    lapse = 0.8
    speed_tolerance = 1.0e-10
    cases: list[dict[str, Any]] = []
    case_index = 0
    for direction in directions:
        tangent = _unit_tangent(direction)
        for ratio in shift_ratios:
            shift = ratio * lapse * direction + 0.25 * tangent
            parameters = GHParameters(
                lapse=lapse,
                shift=tuple(float(value) for value in shift),
                gamma2=0.6,
                symmetrizer_lambda=1.0,
            )
            partition = classify_boundary_modes(
                direction, parameters, speed_tolerance=speed_tolerance
            )
            expected = _expected_partition(ratio)
            partition_matches = (
                partition["incoming_modes"],
                partition["outgoing_modes"],
                partition["glancing_modes"],
            ) == expected
            flux_samples = 0
            minimum_outgoing_flux = None
            maximum_influx_magnitude = 0.0
            if abs(ratio) < 1.0:
                symbol = gh_principal_symbol(direction, parameters)
                mode_index = {label: index for index, label in enumerate(MODE_LABELS)}
                rng = np.random.default_rng(20260925 + case_index)
                fluxes = []
                for _ in range(64):
                    characteristic_state = rng.normal(size=5)
                    for label in partition["incoming_modes"]:
                        characteristic_state[mode_index[label]] = 0.0
                    state = reconstruct_gh_state(
                        characteristic_state, direction, parameters
                    )
                    fluxes.append(principal_energy_flux(state, direction, parameters))
                flux_samples = len(fluxes)
                minimum_outgoing_flux = min(fluxes)
                maximum_influx_magnitude = max(0.0, -minimum_outgoing_flux)
                energy_flux_outward = minimum_outgoing_flux >= -1.0e-12
            else:
                energy_flux_outward = None
            cases.append(
                {
                    "direction": tuple(float(value) for value in direction),
                    "normal_shift_over_lapse": ratio,
                    **partition,
                    "expected_partition_matches": partition_matches,
                    "incoming_free_energy_flux_samples": flux_samples,
                    "minimum_flux_after_zeroing_incoming_modes": minimum_outgoing_flux,
                    "maximum_inward_flux_magnitude": maximum_influx_magnitude,
                    "outgoing_subspace_flux_nonnegative": energy_flux_outward,
                }
            )
            case_index += 1

    subluminal_cases = [case for case in cases if abs(case["normal_shift_over_lapse"]) < 1.0]
    checks = {
        "all_characteristic_partitions_match_analytic_shift_cases": all(
            case["expected_partition_matches"] for case in cases
        ),
        "all_characteristic_bases_have_full_rank": all(
            case["characteristic_rank"] == 5 for case in cases
        ),
        "all_characteristic_residuals_below_1e-12": all(
            case["characteristic_residual"] < 1.0e-12 for case in cases
        ),
        "all_symmetrizers_positive_and_symmetric_compatible": all(
            case["minimum_symmetrizer_eigenvalue"] > 0.0
            and case["symmetrizer_residual"] < 1.0e-12
            for case in cases
        ),
        "all_subluminal_outgoing_subspaces_have_nonnegative_flux": all(
            case["outgoing_subspace_flux_nonnegative"] is True
            for case in subluminal_cases
        ),
        "sonic_and_superluminal_cases_are_flagged_outside_reference_domain": all(
            case["reference_shift_domain"] == "OUTSIDE_SUBLUMINAL_SHIFT_ASSUMPTIONS"
            for case in cases
            if abs(case["normal_shift_over_lapse"]) >= 1.0
        ),
    }
    passed = all(checks.values())
    source_paths = (GH_SOURCE, AUDIT_SOURCE)
    source_hashes = {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        for relative in source_paths
    }
    return {
        "schema_version": "core-curved-3p1-gh-boundary-characteristics-v1",
        "diagnostic_id": "uet.curved_3p1.gh.boundary_characteristics",
        "artifact": "curved_3p1_gh_boundary_characteristic_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION" if passed else "FAIL_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "source-matched incoming, outgoing, and glancing principal-characteristic classification for the implemented GH block",
                "normal-shift sign dependence of the additional incoming u2_A modes",
                "outgoing-principal-subspace energy-flux sign under the implemented symmetrizer for the declared subluminal controls",
            ] if passed else [],
            "equation_or_mapping": {
                "equation_id": "uet.main_theory.curved_3p1.generalized_harmonic_principal_system",
                "formula_ids": [
                    "UET-CURVED3P1-GH-CHARACTERISTICS-012",
                    "UET-CURVED3P1-GH-SYMMETRIZER-011",
                ],
                "characteristics": "u0=psi; u1pm=Pi +/- Phi_n - gamma2*psi; u2_A=Phi_A",
                "speeds": "0; -beta_n +/- alpha; -beta_n",
                "principal_energy_flux": "F_n = 0.5 * U^T S A_n U for d_t U + A_n d_n U = 0",
            },
            "units": "geometric c=1; one local orthonormal GH principal block",
            "derivation_class": "source-matched characteristic algebra plus deterministic principal-symbol verification",
            "observable": "incoming/outgoing/glancing mode sets and normal principal energy flux",
            "data_role": "internal analytic control; no physical source data",
            "verification_status": "PASS_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION" if passed else "FAIL_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION",
            "open_blockers": [
                "constraint-projector differential boundary operator is not implemented",
                "incoming Weyl/radiation and four gauge boundary conditions are not implemented",
                "no non-periodic SBP/SAT evolution, boundary convergence, or discrete Kreiss/robust-stability audit",
                "dimensional observable mapping remains open",
            ],
            "dependency_unlocked": "boundary design preflight only; the curved 3+1 parent remains PARTIAL and Gravity remains blocked",
            "claim_boundary": "This closes only the local principal-characteristic and energy-flux classification lane. It is not a constraint-preserving boundary implementation, a well-posed nonlinear IBVP proof, a production numerical-relativity solver, an Einstein-equation derivation, or Gravity compatibility.",
        },
        "scope": {
            "state_variables": ["psi_ab", "Pi_ab", "Phi_iab_GH"],
            "excluded_variables": ["UET C", "UET Phi", "R_gen", "R_obs"],
            "notation_boundary": "GH Phi_iab is the first-order spatial derivative field; it is distinct from the UET effective response Phi.",
            "forcing_class": "frozen-coefficient principal system; vacuum; no matter evolution",
            "reference_shift_domain": "abs(beta_n) < alpha",
            "boundary_operator_applied": False,
            "xie_2026_accessed": False,
        },
        "case_count": len(cases),
        "subluminal_flux_case_count": len(subluminal_cases),
        "flux_samples_per_subluminal_case": 64,
        "checks": checks,
        "cases": cases,
        "source_hashes": source_hashes,
        "literature_basis": [
            {
                "citation": "O. Rinne, Stable radiation-controlling boundary conditions for the generalized harmonic Einstein equations, Class. Quantum Grav. 23, 6275-6300 (2006)",
                "doi": "10.1088/0264-9381/23/22/013",
                "url": "https://arxiv.org/abs/gr-qc/0606053",
                "role": "source for GH characteristic speeds, projected constraint/physical/gauge boundary decomposition, subluminal normal-shift domain, and frozen-coefficient boundary-stability analysis",
            },
            {
                "citation": "G. Calabrese and O. Sarbach, Detecting ill posed boundary conditions in general relativity, J. Math. Phys. 44, 3888-3899 (2003)",
                "doi": "10.1063/1.1599056",
                "url": "https://eprints.soton.ac.uk/40856/",
                "role": "caution that constraint consistency or setting incoming constraint modes to zero alone does not guarantee well-posedness for arbitrary formulation parameters",
            },
        ],
        "claim_boundary": "Classification and frozen-principal energy-flux controls only. The existing periodic solver and parent gate are unchanged; no physical dependency, Gravity lane, or global UET claim is unlocked.",
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
                "subluminal_flux_case_count": artifact["subluminal_flux_case_count"],
                "checks": artifact["checks"],
                "artifact": OUT.relative_to(ROOT).as_posix(),
            },
            indent=2,
        )
    )
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
