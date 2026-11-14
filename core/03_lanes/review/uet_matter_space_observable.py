"""Normalized measurement operator for the characteristic matter-space lane.

The operator maps a physical-state result to diagnostic observables.  It does not
turn C into mass, does not create a new state variable, and does not feed any
observer record back into the dynamics.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from docs.core.uet_trace import UETStepResult


MATTER_SPACE_OBSERVABLE_OPERATOR_MODE = "matter_space_normalized_observable_v1"


def _safe_scale(value: float) -> float:
    scale = float(value)
    if not np.isfinite(scale) or scale <= 0.0:
        raise ValueError("reference_scale must be finite and positive")
    return scale


def normalized_matter_space_observable(
    result: UETStepResult,
    *,
    dx: float,
    reference_scale: float = 1.0,
    center_index: int | None = None,
    threshold: float = 1.0e-12,
) -> dict[str, Any]:
    """Return a normalized, detector-independent diagnostic record.

    ``C_profile`` and ``Phi_profile`` are dimensionless sampled profiles.  The
    arrival radius is measured in grid cells and is therefore a numerical
    support diagnostic, not a physical length until a dimensional map exists.
    """

    spacing = float(dx)
    if not np.isfinite(spacing) or spacing <= 0.0:
        raise ValueError("dx must be finite and positive")
    scale = _safe_scale(reference_scale)
    if not np.isfinite(threshold) or threshold < 0.0:
        raise ValueError("threshold must be finite and non-negative")
    C = np.asarray(result.C, dtype=float)
    Phi = np.asarray(result.space_response, dtype=float)
    if C.ndim != 1 or Phi.ndim != 1 or C.shape != Phi.shape:
        raise ValueError("result C and space_response must be matching one-dimensional fields")
    if not np.all(np.isfinite(C)) or not np.all(np.isfinite(Phi)):
        raise ValueError("physical state contains non-finite values")

    C_profile = C / scale
    Phi_profile = Phi / scale
    active = np.flatnonzero(np.maximum(np.abs(C_profile), np.abs(Phi_profile)) > threshold)
    if center_index is None:
        center = int(np.argmax(np.maximum(np.abs(C_profile), np.abs(Phi_profile)))) if active.size else 0
    else:
        center = int(center_index)
    if center < 0 or center >= C.size:
        raise ValueError("center_index must lie inside the field")
    radius = int(max(abs(int(active.min()) - center), abs(int(active.max()) - center))) if active.size else 0
    ledger = result.energy_ledger if isinstance(result.energy_ledger, dict) else {}
    return {
        "operator_mode": MATTER_SPACE_OBSERVABLE_OPERATOR_MODE,
        "unit_lane": "normalized",
        "C_profile": C_profile.copy(),
        "Phi_profile": Phi_profile.copy(),
        "C_rms": float(np.sqrt(np.mean(C_profile**2))),
        "Phi_rms": float(np.sqrt(np.mean(Phi_profile**2))),
        "C_peak": float(np.max(np.abs(C_profile))) if C_profile.size else 0.0,
        "Phi_peak": float(np.max(np.abs(Phi_profile))) if Phi_profile.size else 0.0,
        "arrival_radius_cells": radius,
        "arrival_radius_normalized_length": radius * spacing,
        "center_index": center,
        "threshold": float(threshold),
        "trace_backreaction": False,
        "mass_density_mapping": "NOT_DEFINED",
        "physical_energy_mapping": "NOT_DEFINED",
        "ledger_summary": {
            key: ledger[key]
            for key in ("actual_delta", "closure_relative", "dissipation", "input_power", "ledger_gate")
            if key in ledger
        },
        "claim_boundary": "normalized sampled diagnostic; no SI, mass, detector, or empirical identity",
    }


def matter_space_observable_contract() -> dict[str, Any]:
    return {
        "operator_mode": MATTER_SPACE_OBSERVABLE_OPERATOR_MODE,
        "mapping": "O[C,Phi,Pi] -> normalized sampled profiles, support radius and ledger summary",
        "inputs": ["UETStepResult.C", "UETStepResult.space_response", "dx", "reference_scale"],
        "outputs": ["C_profile", "Phi_profile", "arrival_radius_cells", "ledger_summary"],
        "unit_lane": "normalized_only_v1",
        "observer_record": "derived diagnostic; does not alter physical state",
        "mass_density_mapping": "NOT_DEFINED",
        "SI_status": "BLOCKED",
        "uncertainty_status": "numerical_refinement_only",
        "evidence_status": "INTERNAL_CANDIDATE",
    }


__all__ = [
    "MATTER_SPACE_OBSERVABLE_OPERATOR_MODE",
    "matter_space_observable_contract",
    "normalized_matter_space_observable",
]
