"""Regression checks for the observable support-lane migration."""

from __future__ import annotations

import importlib


def test_observable_root_module_forwards_to_review_lane() -> None:
    legacy = importlib.import_module("docs.core.uet_matter_space_observable")
    canonical_name = "docs.core.03_lanes.review.uet_matter_space_observable"
    canonical = importlib.import_module(canonical_name)

    assert legacy.__canonical_module__ == canonical_name
    for name in (
        "MATTER_SPACE_OBSERVABLE_OPERATOR_MODE",
        "matter_space_observable_contract",
        "normalized_matter_space_observable",
    ):
        assert getattr(legacy, name) is getattr(canonical, name)


def test_observable_path_is_classified_as_review_support() -> None:
    from docs.core.core_paths import canonical_path_for

    assert canonical_path_for("docs/core/uet_matter_space_observable.py") == (
        "docs/core/03_lanes/review/uet_matter_space_observable.py"
    )
