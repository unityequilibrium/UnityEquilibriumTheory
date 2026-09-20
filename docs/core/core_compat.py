"""Compatibility and legacy-import helpers for the UET core.

Canonical implementations live below the numbered core packages. The legacy
root modules were useful during migration, but one wrapper file per module
made the tree look unmigrated. This module provides one explicit, lazy import
boundary: old dotted names resolve through the generated alias registry
without duplicating implementation files.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[2]
_ALIAS_REGISTRY = (
    _REPO_ROOT
    / "docs"
    / "core"
    / "00_governance"
    / "uet_core_legacy_module_aliases.json"
)


def load_canonical_module(module_name: str) -> ModuleType:
    """Load a module from a numbered canonical package using importlib."""

    return importlib.import_module(module_name)


def forward_public_symbols(namespace: dict[str, Any], module_name: str) -> ModuleType:
    """Populate a legacy shim namespace from one canonical implementation."""

    implementation = load_canonical_module(module_name)
    public = list(getattr(implementation, "__all__", ()))
    if not public:
        public = [name for name in vars(implementation) if not name.startswith("_")]
    namespace["__canonical_module__"] = module_name
    namespace["__all__"] = public
    for name in public:
        namespace[name] = getattr(implementation, name)
    namespace["__getattr__"] = lambda name: getattr(implementation, name)
    namespace["__dir__"] = lambda: sorted(set(public) | set(vars(implementation)))
    return implementation


def run_canonical_as_script(module_name: str) -> None:
    """Preserve direct-script execution for a migrated module when requested."""

    implementation = load_canonical_module(module_name)
    implementation_path = getattr(implementation, "__file__", None)
    if implementation_path is None:
        raise RuntimeError(f"canonical module has no executable file: {module_name}")
    runpy.run_path(str(Path(implementation_path).resolve()), run_name="__main__")


def _load_aliases() -> dict[str, str]:
    """Read the one source of truth for removed root-module aliases."""

    if not _ALIAS_REGISTRY.exists():
        return {}
    try:
        payload = json.loads(_ALIAS_REGISTRY.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    aliases: dict[str, str] = {}
    for record in payload.get("aliases", []):
        legacy = record.get("legacy_module")
        canonical = record.get("canonical_module")
        if isinstance(legacy, str) and isinstance(canonical, str):
            aliases[legacy] = canonical
    return aliases


class _LegacyAliasLoader(importlib.abc.Loader):
    """Load the canonical module object for a legacy dotted name."""

    def __init__(self, canonical_module: str) -> None:
        self.canonical_module = canonical_module

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        return importlib.import_module(self.canonical_module)

    def exec_module(self, module: ModuleType) -> None:
        # create_module already executed the canonical implementation.
        # Keep the same provenance marker that the former one-file root shims
        # exposed. The module object is shared with the canonical import, so
        # this does not create a second implementation or alter its API.
        setattr(module, "__canonical_module__", self.canonical_module)
        return None


class _LegacyAliasFinder(importlib.abc.MetaPathFinder):
    """Resolve only the aliases recorded by the migration registry."""

    def __init__(self, aliases: dict[str, str]) -> None:
        self.aliases = aliases
        self._uet_legacy_alias_finder = True

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None = None,
        target: ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        canonical = self.aliases.get(fullname)
        if canonical is None or fullname in sys.modules:
            return None
        loader = _LegacyAliasLoader(canonical)
        return importlib.util.spec_from_loader(
            fullname,
            loader,
            origin=str(_ALIAS_REGISTRY),
        )


def install_legacy_module_aliases() -> int:
    """Install the lazy legacy import boundary once and return alias count."""

    for finder in sys.meta_path:
        if getattr(finder, "_uet_legacy_alias_finder", False):
            return len(getattr(finder, "aliases", {}))
    aliases = _load_aliases()
    if not aliases:
        return 0
    sys.meta_path.insert(0, _LegacyAliasFinder(aliases))
    return len(aliases)
