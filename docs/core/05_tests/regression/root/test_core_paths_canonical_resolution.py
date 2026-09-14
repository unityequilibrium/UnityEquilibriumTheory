from __future__ import annotations

from pathlib import Path

from docs.core.core_paths import (
    canonical_existing_path,
    canonical_path_for,
    repo_root,
)


def test_o2_legacy_source_resolves_to_canonical_implementation() -> None:
    legacy = "docs/core/uet_o2_finite_density_eos.py"
    expected = repo_root() / "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"

    assert canonical_path_for(legacy) == expected.relative_to(repo_root()).as_posix()
    assert canonical_existing_path(legacy) == expected.resolve()


def test_canonical_source_is_idempotent() -> None:
    canonical = repo_root() / "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"

    assert canonical_existing_path(canonical) == canonical.resolve()


def test_external_path_is_not_rewritten() -> None:
    external = Path("C:/outside/uet_source.py")

    assert canonical_existing_path(external) == external.resolve()
