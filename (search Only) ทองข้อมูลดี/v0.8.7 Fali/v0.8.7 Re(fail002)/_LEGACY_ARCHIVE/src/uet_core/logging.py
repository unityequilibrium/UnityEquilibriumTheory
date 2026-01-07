"""
Run artifact writing for UET harness.
Implements the run folder contract from R0-C1.1.
"""
from __future__ import annotations
import json, hashlib, time, platform, sys
from pathlib import Path
import numpy as np

def stable_json_dumps(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def config_hash(config: dict) -> str:
    # Exclude any non-deterministic keys if present
    cfg = dict(config)
    cfg.pop("run_id", None)
    cfg.pop("timestamp_utc", None)
    s = stable_json_dumps(cfg).encode("utf-8")
    return hashlib.sha256(s).hexdigest()[:12]

def make_run_id(cfg_hash: str) -> str:
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "_" + cfg_hash

def write_meta(run_dir: Path, code_hash: str = "unknown") -> dict:
    meta = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "code_hash": code_hash,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta

def init_run_folder(out_root: Path, model: str, case_id: str, config: dict) -> tuple[Path,str,str]:
    out_root = Path(out_root)
    cfg_hash = config_hash(config)
    run_id = make_run_id(cfg_hash)
    run_dir = out_root / model / case_id / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    config2 = dict(config)
    config2["config_hash"] = cfg_hash
    config2["run_id"] = run_id
    (run_dir / "config.json").write_text(json.dumps(config2, indent=2), encoding="utf-8")
    return run_dir, run_id, cfg_hash

def write_timeseries(run_dir: Path, rows: list[dict]) -> None:
    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(run_dir / "timeseries.csv", index=False)

def write_summary(run_dir: Path, summary: dict) -> None:
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
