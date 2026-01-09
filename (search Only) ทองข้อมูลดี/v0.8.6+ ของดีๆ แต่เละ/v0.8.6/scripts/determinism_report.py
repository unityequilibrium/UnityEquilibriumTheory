#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from typing import Dict, Any, Tuple, List

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default="determinism_report.json")
    ap.add_argument("--min_repeats", type=int, default=3)
    args = ap.parse_args()

    rows=[]
    with Path(args.ledger).open("r", encoding="utf-8") as f:
        rdr=csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty ledger")

    g: Dict[Tuple[str,str,str,str,str], List[Dict[str,Any]]] = {}
    for r in rows:
        key=(r.get("base_case_id",""), r.get("model",""), r.get("integrator",""), r.get("dt",""), r.get("seed",""))
        g.setdefault(key, []).append(r)

    unstable=[]
    stable=0
    total=0
    for key, rs in g.items():
        if len(rs) < args.min_repeats:
            continue
        total += 1
        pass_set=set(str(r.get("pass","")) for r in rs)
        code_set=set(str(r.get("fail_code","")) for r in rs)
        status_set=set(str(r.get("status","")) for r in rs)
        if len(pass_set)>1 or len(code_set)>1 or len(status_set)>1:
            unstable.append({
                "base_case_id": key[0], "model": key[1], "integrator": key[2], "dt": key[3], "seed": key[4],
                "n": len(rs),
                "pass_values": sorted(pass_set),
                "fail_codes": sorted(code_set),
                "statuses": sorted(status_set),
            })
        else:
            stable += 1

    report={
        "meta": {
            "min_repeats": args.min_repeats,
            "n_groups": total,
            "n_stable": stable,
            "n_unstable": len(unstable),
            "unstable_rate": (len(unstable)/total) if total else 0.0,
        },
        "unstable_examples": unstable[:2000],
        "status": "OK" if len(unstable)==0 else "UNSTABLE"
    }
    out=Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["meta"], indent=2))
    print("Wrote", out)

if __name__ == "__main__":
    main()
