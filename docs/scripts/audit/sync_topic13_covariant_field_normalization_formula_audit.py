"""Append the field-normalization formula record before running its audit."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FORMULA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
MARKER = "## Covariant Field-Normalization Identifiability (2026-08-11)"


def main() -> int:
    content = FORMULA.read_text(encoding="utf-8-sig")
    if MARKER not in content:
        content += f"""

{MARKER}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-016` | `delta_phi' = s delta_phi`; `Z'=Z/s^2`; `m_Phi^2'=m_Phi^2/s^2`; `lambda'=lambda/s^4`; `xi'=xi/s^2`; `Phi_scale'=s Phi_scale` | `docs/core/02_equations/covariant/uet_covariant_response.py`; `docs/scripts/audit/audit_topic13_covariant_field_normalization_identifiability.py` | `delta_phi` = natural mass dimension 1; `Phi_normalized=delta_phi/Phi_scale` dimensionless only after a declared scale; `e0` = J m^-3 and `alpha_Phi_K` = K per normalized Phi remain unassigned | algebraic field redefinition of the declared natural-unit scalar action | scoped identifiability no-go; not an SI derivation | prevents a canonical kinetic convention or default coefficient from becoming a fictitious thermal calibration | a source-locked observable amplitude, physical residue, or SI coefficient contract would break the current under-identification and requires a new audit | source-lock a covariant field normalization plus system-specific SI energy-density contract, or an independent non-TTG alpha calibration; then derive base `Phi -> Phi_E` |

The rescaling preserves the scalar action sector and the hypothetical normalized coordinate when both the covariant displacement and `Phi_scale` rescale. It therefore does not identify an absolute field amplitude. This audit does not identify base `Phi` with `Phi_E`, temperature, heat flux, entropy, or `R_gen`.
"""
        FORMULA.write_text(content, encoding="utf-8")
    print("PASS_SYNCED_T13_COVARIANT_FIELD_NORMALIZATION_FORMULA_AUDIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
