"""Append the named Topic 13 finite-temperature beta formula record."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FORMULA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
MARKER = "## Named Finite-Temperature beta_T13 Contract (2026-08-11)"


def main() -> int:
    content = FORMULA.read_text(encoding="utf-8-sig")
    if MARKER not in content:
        content += f"""

{MARKER}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-018` | `f_hat_T13=a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2`; `beta_T13=T0*(da_Phi/dT)|T0`; `a_Phi(T)=a_Phi(T0)+beta_T13*(T-T0)/T0`; `s=-e0 Phi^2 beta_T13/(2T0)` | `docs/core/03_lanes/thermal/thermal_response_beta_contract.py`; `docs/scripts/audit/audit_topic13_thermal_response_beta_contract.py` | `C,Phi,a_Phi,b_Phi,g,beta_T13` dimensionless in named normalized lane; `T,T0` = K; `da_Phi/dT` = K^-1; `e0` = J m^-3 external input; `f` = J m^-3 and `s` = J m^-3 K^-1 only after e0 is source-locked | declared finite-temperature response-functional definition, independent of Landauer | formal derivative/unit contract closed for named lane; coefficient provenance and physical correspondence open | makes one auditable meaning for beta_T13 while forbidding aliases to beta_th, beta_core, beta_wave, base covariant Phi, or R_gen | no physical value or SI map follows from declaration; entropy identity is not entropy-production positivity, SK/KMS, EOS, or transport closure | source-lock e0 and coefficient provenance, resolve base Phi correspondence, then test finite-temperature EOS/transport/KMS/entropy contracts |

The contract defines a local first-order temperature expansion only. It does
not set `beta_T13=beta_core`, use `k_B T ln(2)`, identify `Phi` with the legacy
`I` state, or claim a physical entropy-production law.
"""
        FORMULA.write_text(content, encoding="utf-8")
    print("PASS_SYNCED_T13_THERMAL_RESPONSE_BETA_FORMULA_AUDIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
