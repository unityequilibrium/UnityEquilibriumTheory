"""Compatibility import boundary for the root-level :mod:`core` package.

The directory remains because two protected local-source databases retain
their historical location. Python imports through ``docs.core`` are forwarded
to the exact root package object; equation modules are not copied here.
"""

from __future__ import annotations

import importlib
import sys

_core = importlib.import_module("core")
sys.modules[__name__] = _core
