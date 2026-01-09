#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Drop-in helper: make scripts runnable from ANY working directory by injecting repo-root on sys.path.
Use at top of scripts that import uet_core.
"""
from __future__ import annotations
from pathlib import Path
import sys

def ensure_repo_on_path(anchor: str = "uet_core") -> Path:
    """
    Walk up from this file until we find a folder containing `anchor` (e.g. uet_core),
    then add that folder to sys.path.
    Returns the repo root path.
    """
    here = Path(__file__).resolve()
    for p in [here.parent] + list(here.parents):
        if (p / anchor).exists():
            root = p
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            return root
    raise RuntimeError(f"Could not locate repo root containing '{anchor}' from {here}")
