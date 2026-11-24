"""Source regression for the topic 0.18 Lean lane (Code/06_Lean/uet_formal).

These checks do not run Lean (CI has no Lean toolchain). They guard the proof sources against the
edits that would silently weaken them: a `sorry` or `admit`, a new `axiom`, a module left out of the
root import, or a theorem named in a module header that no longer exists. Whether the proofs check is
established by `lake build` and `#print axioms` (see the lane README), not by these tests.
"""

from pathlib import Path
import re

import pytest

LANE = Path(__file__).resolve().parents[1] / "Code" / "06_Lean" / "uet_formal"
MODULES = sorted((LANE / "UetFormal").glob("*.lean"))
BLOCK_COMMENT = re.compile(r"/-.*?-/", re.S)
LINE_COMMENT = re.compile(r"--[^\n]*")


def _code(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return LINE_COMMENT.sub("", BLOCK_COMMENT.sub("", text))


def _header_theorems(path: Path) -> list[str]:
    match = re.match(r"\s*/-(.*?)-/", path.read_text(encoding="utf-8"), re.S)
    assert match, f"{path.name}: missing module header"
    return re.findall(r"\*\s+`([A-Za-z_][A-Za-z0-9_']*)`", match.group(1))


def test_lane_has_the_seven_modules():
    assert [p.stem for p in MODULES] == [
        "Boost", "EnergyMomentum", "Isotropic", "NoetherO2", "Selection", "Threshold", "TraceFeedback"]


def test_root_imports_every_module():
    root = (LANE / "UetFormal.lean").read_text(encoding="utf-8")
    imported = set(re.findall(r"^import UetFormal\.(\w+)\s*$", root, re.M))
    assert imported == {p.stem for p in MODULES}


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.stem)
def test_no_sorry_admit_or_new_axiom(path):
    code = _code(path)
    assert not re.search(r"\bsorry\b", code), f"{path.name} contains sorry"
    assert not re.search(r"\badmit\b", code), f"{path.name} contains admit"
    assert not re.search(r"^\s*(?:private\s+)?axiom\s", code, re.M), f"{path.name} declares an axiom"


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.stem)
def test_header_theorems_exist(path):
    names = _header_theorems(path)
    assert names, f"{path.name}: header lists no theorems"
    code = _code(path)
    for name in names:
        assert re.search(rf"^theorem\s+{re.escape(name)}\b", code, re.M), f"{path.name}: {name} not found"


def test_toolchain_is_pinned():
    assert (LANE / "lean-toolchain").read_text(encoding="utf-8").strip().startswith("leanprover/lean4:v")
    assert "mathlib" in (LANE / "lake-manifest.json").read_text(encoding="utf-8").lower()
