"""Correct the fluctuation record to distinguish curvature from mixed-mode gap."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/core/02_equations/o2/uet_o2_condensate_fluctuations.py"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8-sig")
    text = text.replace(
        "    radial_gap_sq: float\n",
        "    radial_curvature_sq: float\n    zero_momentum_high_mode_sq: float\n",
        1,
    )
    text = text.replace(
        "    radial_gap_sq = 2.0 * q / float(config.matter.matter_kinetic)\n    values = (mass_sq, q, amplitude_sq, radial_gap_sq)\n",
        "    radial_curvature_sq = 2.0 * q / float(config.matter.matter_kinetic)\n    zero_momentum_high_mode_sq = 2.0 * (q / float(config.matter.matter_kinetic) + 2.0 * mu**2)\n    values = (mass_sq, q, amplitude_sq, radial_curvature_sq, zero_momentum_high_mode_sq)\n",
        1,
    )
    text = text.replace(
        "        radial_gap_sq=radial_gap_sq,\n",
        "        radial_curvature_sq=radial_curvature_sq,\n        zero_momentum_high_mode_sq=zero_momentum_high_mode_sq,\n",
        1,
    )
    text = text.replace(
        "    \"radial_gap_sq\": \"2.0 * q / float(config.matter.matter_kinetic)\",\n",
        "    \"radial_curvature_sq\": \"2*q/Z\",\n    \"zero_momentum_high_mode_sq\": \"2*(q/Z+2*mu^2)\",\n",
        1,
    )
    TARGET.write_text(text, encoding="utf-8")
    print("REPAIRED_TOPIC13_UET_O2_CONDENSATE_FLUCTUATION_GAP_CONTRACT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
