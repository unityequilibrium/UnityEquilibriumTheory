"""Append the named Topic 13 collective-response EOS formula record."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FORMULA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
MARKER = "## Named Collective-Response EOS and Stability Contract (2026-08-11)"


def main() -> int:
    content = FORMULA.read_text(encoding="utf-8-sig")
    if MARKER not in content:
        content += f"""

{MARKER}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-019` | `f_hat=a_C C^2/2+b_C C^4/4+a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2`; `mu_C=a_C C+b_C C^3-g C Phi`; `mu_Phi=a_Phi Phi+b_Phi Phi^3-g C^2/2`; `H_CPhi=H_PhiC=-g C` | `docs/core/03_lanes/thermal/thermal_collective_response_eos.py`; `docs/scripts/audit/audit_topic13_collective_response_eos.py` | `C,Phi,a_C,b_C,a_Phi,b_Phi,g` dimensionless in the named lane; `T` = K; `e0` = J m^-3 only for physical density; Hessian is normalized-coordinate curvature | declared candidate response functional extending the named beta_T13 lane | formal EOS, mixed-derivative reciprocity, and local stability contract closed for named lane; physical coefficient provenance open | provides an explicit stability/reciprocity interface without relabeling C as charge/mass or Phi as an information/thermal field | no source coefficient, SI Phi anchor, physical charge EOS, transport, KMS, entropy production, or dissipative balance follows from local Hessian positivity | source-lock coefficients and Phi/e0 mapping, then test physical EOS and nonequilibrium closures |

`C` is deliberately called a collective coordinate, not a charge density. The
formal `mu_C` and `mu_Phi` are normalized derivatives, not measured chemical
potentials. `R_gen` is absent and does not backreact.
"""
        FORMULA.write_text(content, encoding="utf-8")
    print("PASS_SYNCED_T13_COLLECTIVE_RESPONSE_EOS_FORMULA_AUDIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
