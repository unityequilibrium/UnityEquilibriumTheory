from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

def load_config_for_run(runs_root: Path, run_id: str) -> dict:
    p = runs_root / run_id / "config.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))

def extract_quartic_params(cfg: dict) -> dict:
    out={}
    try:
        # Try params.pot first (new format), then top-level pot
        pot = cfg.get("params", {}).get("pot") or cfg.get("pot")
        if isinstance(pot, dict) and pot.get("type")=="quartic":
            out["a"]=float(pot.get("a",0.0))
            out["delta"]=float(pot.get("delta") if pot.get("delta") is not None else 0.0)
            out["s"]=float(pot.get("s",0.0))
        elif isinstance(cfg.get("potC"), dict):
            out["a"]=float(cfg["potC"].get("a",0.0))
            out["delta"]=float(cfg["potC"].get("delta"))
            out["s"]=float(cfg["potC"].get("s",0.0))
    except Exception:
        pass
    # Handle nested params
    params = cfg.get("params", cfg)
    if "kappa" in params: out["kappa"]=float(params["kappa"])
    if "kC" in params: out["kappa"]=float(params["kC"])
    
    # Handle domain.L and domain.dim
    domain = cfg.get("domain", cfg)
    if "L" in domain: out["L"]=float(domain["L"])
    if "dim" in domain: out["dim"]=int(domain["dim"])
    
    # Handle grid.N (can be dict or int)
    grid = cfg.get("grid")
    if isinstance(grid, dict):
        out["grid"]=int(grid.get("N", 64))
    elif isinstance(grid, (int, float)):
        out["grid"]=int(grid)
    return out

def add_density_columns(df: pd.DataFrame) -> pd.DataFrame:
    out=df.copy()
    L = out["L"].fillna(1.0).astype(float) if "L" in out.columns else 1.0
    D = out["dim"].fillna(2).astype(int) if "dim" in out.columns else 2
    vol = (L ** D)
    if "Omega0" in out.columns: out["Omega0_density"]=out["Omega0"]/vol
    if "OmegaT" in out.columns: out["OmegaT_density"]=out["OmegaT"]/vol
    return out
