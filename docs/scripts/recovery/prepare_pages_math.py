"""Escape Liquid-like math in a disposable copy of the Pages source."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COUNTS = {
    "meta/UET_JOINT_STATE_MEASURE_CONSTRUCTION.md": 1,
    "meta/UET_LATTICE_MECHANICAL_STATE_CONSTRUCTION.md": 2,
    "meta/UET_SPIN_STRAIN_CORRESPONDENCE_AUDIT.md": 4,
}
MATH = re.compile(r"\\\[.*?\\\]", re.DOTALL)


def prepare(directory: Path) -> None:
    directory = directory.resolve()
    if directory == (ROOT / "docs").resolve():
        raise ValueError("Refusing to change canonical research sources")
    for relative, expected in COUNTS.items():
        path = directory / relative
        original = path.read_bytes().decode("utf-8")
        count = 0

        def protect(match: re.Match[str]) -> str:
            nonlocal count
            block = match.group()
            if "{{" not in block:
                return block
            count += 1
            return "<!-- {% raw %} -->\n" + block + "\n<!-- {% endraw %} -->"

        rendered = MATH.sub(protect, original)
        if count != expected:
            raise ValueError(f"{relative}: expected {expected} math blocks, found {count}")
        path.write_bytes(rendered.encode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages_source", type=Path)
    prepare(parser.parse_args().pages_source)
