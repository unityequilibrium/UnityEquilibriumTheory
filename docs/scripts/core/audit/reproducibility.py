"""
Utilities for reproducible UET experiments.

This module intentionally stays lightweight so it can be imported by topic-level
verification scripts without requiring extra infrastructure.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DEFAULT_SEED = 42


def lock_all_seeds(seed: int = DEFAULT_SEED) -> int:
    """Lock common pseudo-random sources used in experiments."""
    random.seed(seed)

    try:
        import numpy as np  # type: ignore

        np.random.seed(seed)
    except ImportError:
        pass

    try:
        import torch  # type: ignore

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

    try:
        import tensorflow as tf  # type: ignore

        tf.random.set_seed(seed)
    except ImportError:
        pass

    os.environ["PYTHONHASHSEED"] = str(seed)
    return seed


def get_environment_info() -> Dict[str, Any]:
    """Return a serializable summary of the current runtime environment."""
    info: Dict[str, Any] = {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
    }

    for package_name in ("numpy", "scipy", "pandas", "matplotlib", "torch", "tensorflow"):
        try:
            module = __import__(package_name)
            info[f"{package_name}_version"] = getattr(module, "__version__", "unknown")
        except ImportError:
            info[f"{package_name}_version"] = None

    return info


def _normalize_for_hash(value: Any) -> Any:
    """Convert common data structures into a stable, JSON-serializable shape."""
    if isinstance(value, dict):
        return {str(key): _normalize_for_hash(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_normalize_for_hash(item) for item in value]
    if isinstance(value, Path):
        return str(value)

    try:
        import numpy as np  # type: ignore

        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
    except ImportError:
        pass

    return value


def hash_dataset(data: Any) -> str:
    """Hash in-memory data using a stable JSON representation."""
    payload = json.dumps(
        _normalize_for_hash(data),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def hash_file(path: str | Path) -> str:
    """Hash a file from disk."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_artifact(
    *,
    topic: str,
    results: Dict[str, Any],
    dataset_hash: str,
    config: Dict[str, Any] | None = None,
    metrics: Dict[str, Any] | None = None,
    thresholds: Dict[str, Any] | None = None,
    notes: str | None = None,
    seed: int = DEFAULT_SEED,
    uet_version: str = "0.9.0",
) -> Dict[str, Any]:
    """Create a normalized verification artifact."""
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "uet_version": uet_version,
        "seed": seed,
        "dataset_hash": dataset_hash,
        "results": results,
        "config": config or {},
        "metrics": metrics or {},
        "thresholds": thresholds or {},
        "notes": notes,
        "environment": get_environment_info(),
    }


def save_artifact(artifact: Dict[str, Any], path: str | Path) -> Path:
    """Persist a verification artifact as JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return target
