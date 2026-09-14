"""Compatibility helpers shared by migrated UET core modules."""

from __future__ import annotations

import importlib
import runpy
from pathlib import Path
from types import ModuleType
from typing import Any


def load_canonical_module(module_name: str) -> ModuleType:
    """Load a module from a numbered canonical package using ``importlib``."""

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

