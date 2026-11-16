"""Locator translation checks only; no scientific calculation or artifact writes."""

from pathlib import Path
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[3]
CODE = ROOT / "topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research"


@pytest.fixture(params=["Flow_Hessian", "Infrared_Trials"])
def source(request):
    script = CODE / ("Research_Fluid_Core_O2_" + request.param + ".py")
    return runpy.run_path(str(script)), script.relative_to(ROOT).as_posix()


@pytest.mark.parametrize("layout", ["current", "legacy", "windows"])
def test_unique_recorded_locator_preserves_digest(source, layout):
    ns, current = source
    key = current if layout == "current" else "docs/" + current
    if layout == "windows":
        key = key.replace("/", "\\")
    record = {key: "a" * 64, "unrelated/file.py": "b" * 64}
    original = dict(record)
    assert ns["_archived_source_hash"](record) == "a" * 64
    assert record == original


@pytest.mark.parametrize("kind", ["empty", "wrong_directory", "other_script"])
def test_missing_source_locator_fails_closed(source, kind):
    ns, current = source
    records = {
        "empty": {},
        "wrong_directory": {"elsewhere/" + Path(current).name: "a" * 64},
        "other_script": {current + ".other": "a" * 64},
    }
    with pytest.raises(ValueError, match="exactly one source locator"):
        ns["_archived_source_hash"](records[kind])


@pytest.mark.parametrize("second", ["a" * 64, "b" * 64])
def test_duplicate_current_and_legacy_locators_are_ambiguous(source, second):
    ns, current = source
    with pytest.raises(ValueError, match="exactly one source locator"):
        ns["_archived_source_hash"]({current: "a" * 64, "docs/" + current: second})


def test_translating_locator_cannot_repair_a_tampered_digest(source):
    ns, current = source
    expected = "a" * 64
    tampered = "b" * 64
    assert ns["_archived_source_hash"]({"docs/" + current: tampered}) == tampered
    assert ns["_archived_source_hash"]({"docs/" + current: tampered}) != expected


def test_locator_lookup_does_not_read_or_write_evidence(source, monkeypatch):
    ns, current = source
    def forbidden(*args, **kwargs):
        raise AssertionError("locator translation must not read or write evidence")
    for name in ("read_text", "read_bytes", "write_text", "write_bytes"):
        monkeypatch.setattr(Path, name, forbidden)
    assert ns["_archived_source_hash"]({"docs/" + current: "a" * 64}) == "a" * 64
