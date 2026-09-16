"""Append the Topic 13 beta-symbol separation record before its audit."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FORMULA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
MARKER = "## Beta Symbol Separation and Non-Circularity (2026-08-11)"


def main() -> int:
    content = FORMULA.read_text(encoding="utf-8-sig")
    if MARKER not in content:
        content += f"""

{MARKER}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-017` | `beta_th = 1/(k_B T)` and `E_L = k_B T ln(2) = ln(2)/beta_th`; `beta_core != beta_th` unless a separately declared mapping is derived | `docs/core/01_contracts/units/uet_parameters.py`; `docs/core/02_equations/matter_space/uet_hyperbolic_phase_field.py`; `docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Thermodynamic_Bridge.py`; `docs/scripts/audit/audit_topic13_beta_symbol_separation.py` | `beta_th` = J^-1 after externally supplied `T` in K; `E_L` = J; `beta_core` = dimensionless normalized coupling; `beta_wave` = comparator coefficient with no SI bridge declared | standard inverse-temperature/Landauer identity plus repository source audit | scoped symbol-identification no-go; not a UET beta derivation | prevents the standard Landauer identity, a normalized core coupling, or an auxiliary comparator coefficient from being silently substituted for a finite-temperature UET bridge coefficient | the legacy research print label calls a Landauer value a UET beta prediction although the current core helper explicitly rejects that derivation; neither current beta has a declared UET action/temperature/SI mapping | declare one `beta_UET` with an action term, units, finite-temperature coefficient provenance, and an observable/SI contract independent of Landauer; then audit the derivation |

This record distinguishes a standard thermodynamic inverse energy `beta_th` from
the legacy normalized core coupling `beta_core` and the hyperbolic-comparator
`beta_wave`. The standard identity can constrain a lower bound only after a
temperature is supplied; it cannot identify an independent UET coefficient.
No `Phi`, `R_gen`, temperature, heat flux, entropy, or calibration is relabeled
by this audit.
"""
        FORMULA.write_text(content, encoding="utf-8")
    print("PASS_SYNCED_T13_BETA_SYMBOL_SEPARATION_FORMULA_AUDIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
