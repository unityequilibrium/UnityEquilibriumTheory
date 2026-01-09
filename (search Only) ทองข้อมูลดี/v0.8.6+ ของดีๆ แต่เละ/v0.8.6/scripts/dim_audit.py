#!/usr/bin/env python
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Dict, Any
import math

def _load(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def _need(scales: Dict[str, Any], k: str):
    if k not in scales:
        raise SystemExit(f"Missing units.scales['{k}'] for physical mode")
    return float(scales[k])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="path to config.json (run artifact)")
    args = ap.parse_args()
    cfg = _load(Path(args.config))

    units = cfg.get("units", {"mode":"dimensionless"})
    mode = units.get("mode","dimensionless")
    print("units.mode =", mode)

    if mode == "dimensionless":
        print("OK: model is declared dimensionless. No further action.")
        return

    if mode != "physical":
        raise SystemExit("units.mode must be 'dimensionless' or 'physical'")

    scales = units.get("scales", {})
    L0 = _need(scales, "L0")
    e0 = _need(scales, "e0")
    C0 = float(scales.get("C0", 1.0))
    I0 = float(scales.get("I0", 1.0))
    t0 = float(scales.get("t0", 1.0))

    model = cfg.get("model","")
    params = cfg.get("params", {})
    print(f"scales: L0={L0}  e0={e0}  C0={C0}  I0={I0}  t0={t0}")

    def tilde_kappa(kappa, field_scale):
        return (kappa * field_scale*field_scale) / (e0 * L0*L0)

    def tilde_beta(beta):
        return (beta * C0 * I0) / e0

    def tilde_poly(a=None, delta=None, s=None, field_scale=1.0):
        out = {}
        if a is not None:
            out["a_tilde"] = (a * field_scale*field_scale) / e0
        if delta is not None:
            out["delta_tilde"] = (delta * field_scale**4) / e0
        if s is not None:
            out["s_tilde"] = (s * field_scale) / e0
        return out

    def tilde_M(M, field_scale):
        return (t0 * M * e0) / (field_scale*field_scale)

    print("\n--- Dimensionless parameter report ---")
    if model == "C_only":
        kappa = float(params.get("kappa", math.nan))
        M = float(params.get("M", math.nan))
        pot = params.get("pot", {})
        a = pot.get("a", None); delta = pot.get("delta", None); s = pot.get("s", None)
        print(f"kappa_tilde = {tilde_kappa(kappa, C0):.6g}")
        print(f"M_tilde     = {tilde_M(M, C0):.6g}")
        for k,v in tilde_poly(a=a, delta=delta, s=s, field_scale=C0).items():
            print(f"{k:10s}= {float(v):.6g}")
    elif model == "C_I":
        kC = float(params.get("kC", math.nan))
        kI = float(params.get("kI", math.nan))
        MC = float(params.get("MC", math.nan))
        MI = float(params.get("MI", math.nan))
        beta = float(params.get("beta", math.nan))
        potC = params.get("potC", {})
        potI = params.get("potI", {})
        print(f"kC_tilde    = {tilde_kappa(kC, C0):.6g}")
        print(f"kI_tilde    = {tilde_kappa(kI, I0):.6g}")
        print(f"beta_tilde  = {tilde_beta(beta):.6g}")
        print(f"MC_tilde    = {tilde_M(MC, C0):.6g}")
        print(f"MI_tilde    = {tilde_M(MI, I0):.6g}")
        for k,v in tilde_poly(a=potC.get("a",None), delta=potC.get("delta",None), s=potC.get("s",None), field_scale=C0).items():
            print(f"C_{k:8s}= {float(v):.6g}")
        for k,v in tilde_poly(a=potI.get("a",None), delta=potI.get("delta",None), s=potI.get("s",None), field_scale=I0).items():
            print(f"I_{k:8s}= {float(v):.6g}")
    else:
        print(f"Unknown model {model}. No report.")

    print("\nInterpretation hint:")
    print("- Good dimensionless parameters are typically O(1) after proper scaling.")
    print("- Huge/small values indicate stiffness or poor scaling; mark as boundary/unsafe in atlas.")

if __name__ == "__main__":
    main()
