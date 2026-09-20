"""Repair the delegated entropy helper name in the new EOS lane module."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/core/03_lanes/thermal/thermal_collective_response_eos.py"


def main() -> int:
    content = TARGET.read_text(encoding="utf-8")
    old_import = "    entropy_density_J_per_m3_K,\n    validate_inputs as validate_beta_inputs,\n)"
    new_import = "    entropy_density_J_per_m3_K as beta_entropy_density_J_per_m3_K,\n    validate_inputs as validate_beta_inputs,\n)"
    if old_import in content:
        content = content.replace(old_import, new_import, 1)
    old_call = "return entropy_density_J_per_m3_K(phi, inputs.thermal, e0_J_per_m3)"
    new_call = "return beta_entropy_density_J_per_m3_K(phi, inputs.thermal, e0_J_per_m3)"
    if old_call in content:
        content = content.replace(old_call, new_call, 1)
    TARGET.write_text(content, encoding="utf-8")
    print("PASS_REPAIRED_T13_COLLECTIVE_RESPONSE_EOS_ENTROPY_ALIAS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
