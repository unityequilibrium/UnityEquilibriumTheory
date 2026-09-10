from docs.scripts.audit.audit_topic13_eos_revision_impact import (
    allowed, compare_states, declared_edges,
)


def test_paths_exclude_holdout_and_escape():
    assert allowed("docs/core/artifacts/a.json")
    for path in ("docs/core/../secret.json", "docs/core/artifacts/t13_xie_2026.json",
                 "docs/core/artifacts/holdout.json", "docs/topics/source.json"):
        assert not allowed(path)


def test_edges_and_numeric_comparison():
    assert list(declared_edges({"nested": [{"path": "a", "sha256": "b"}]})) == [("a", "b")]
    rows = compare_states({"x": 2., "zero": 0., "flag": True}, {"x": 3., "zero": 1., "flag": False})
    assert rows["x"]["relative_difference"] == .5
    assert rows["zero"]["relative_difference"] is None
    assert "flag" not in rows
