"""Load derived core modules by file path (their folders start with digits, so they are not importable names)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]


def load(relative: str):
    """Load core/<relative> once and return the module (registered in sys.modules for dataclasses)."""
    path = CORE / relative
    name = "uet_engine_dep_" + path.stem
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
