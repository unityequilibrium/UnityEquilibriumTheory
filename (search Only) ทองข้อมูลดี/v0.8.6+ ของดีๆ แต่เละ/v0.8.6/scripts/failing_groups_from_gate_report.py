#!/usr/bin/env python
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import List, Dict, Any

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate_report", required=True, help="stress_gate_report.json")
    ap.add_argument("--out", default="failing_groups.json")
    ap.add_argument("--key_mode", choices=["band_model_integrator","band_model"], default="band_model_integrator",
                    help="expected fields in failed_groups depend on summary grouping")
    args = ap.parse_args()

    rep = json.loads(Path(args.gate_report).read_text(encoding="utf-8"))
    failed = rep.get("failed_groups", []) or []
    out_list = []
    for r in failed:
        band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        if args.key_mode == "band_model":
            out_list.append(f"{band}|{model}")
        else:
            integ = (r.get("integrator","") or "").strip()
            out_list.append(f"{band}|{model}|{integ}")
    out_list = sorted(set(out_list))

    payload = {"meta": {"n_failed_groups": len(out_list), "key_mode": args.key_mode},
               "groups": out_list}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Wrote", out, "n=", len(out_list))

if __name__ == "__main__":
    main()
