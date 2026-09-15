"""Repair the generated Topic 13 calibration sync script after ACL-safe add."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/scripts/audit/sync_topic13_base_phi_independent_calibration_requirement.py"
NEEDLE = 'ACTION_REL = "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json"\n'
INSERT = NEEDLE + 'PROTOCOL_REL = "docs/topics/0.13_Thermodynamic_Bridge/BASE_PHI_INDEPENDENT_CALIBRATION_PROTOCOL.md"\n'


def main() -> int:
    text = TARGET.read_text(encoding="utf-8-sig")
    if "PROTOCOL_REL =" not in text:
        if NEEDLE not in text:
            raise SystemExit("calibration sync constant insertion point not found")
        text = text.replace(NEEDLE, INSERT, 1)
        TARGET.write_text(text, encoding="utf-8")
    print(f"repaired {TARGET.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
