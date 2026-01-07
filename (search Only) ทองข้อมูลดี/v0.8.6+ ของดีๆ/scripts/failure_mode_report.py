#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from typing import Dict, Any, List, Tuple

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default="", help="default: <ledger_parent>/failure_mode_report.json")
    ap.add_argument("--top_k", type=int, default=20)
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out = Path(args.out) if args.out else (ledger.parent/"failure_mode_report.json")

    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty ledger")

    fails=[r for r in rows if str(r.get("status","")).upper()!="PASS"]
    grp={}
    for r in fails:
        key=(
            (r.get("band","") or "UNLABELED").strip() or "UNLABELED",
            (r.get("model","") or "").strip(),
            (r.get("integrator","") or "").strip(),
            (r.get("variant","") or "BASE").strip() or "BASE",
            (r.get("fail_code","") or "UNKNOWN").strip() or "UNKNOWN",
        )
        grp[key]=grp.get(key,0)+1

    top = sorted(grp.items(), key=lambda kv: kv[1], reverse=True)[:args.top_k]
    top_list=[{"band":k[0],"model":k[1],"integrator":k[2],"variant":k[3],"fail_code":k[4],"count":v} for k,v in top]

    report={
        "n_total": len(rows),
        "n_fail": len(fails),
        "top_failure_groups": top_list,
    }
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
