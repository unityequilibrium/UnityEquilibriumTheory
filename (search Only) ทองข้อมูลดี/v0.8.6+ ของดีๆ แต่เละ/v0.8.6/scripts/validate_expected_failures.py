#!/usr/bin/env python
"""
Validate that an "expected FAIL" matrix actually fails.

Usage:
  python scripts/validate_expected_failures.py --matrix matrices/UET_v0_8_5_pre_Tier3_FAIL_HARD_matrix.csv --ledger runs_tier3_fail/ledger.csv

It prints a small summary and exits with code 0 if all expectations satisfied, else 1.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--ledger", required=True)
    args = ap.parse_args()

    m = pd.read_csv(args.matrix)
    l = pd.read_csv(args.ledger)

    # merge by case_id
    df = m.merge(l[["case_id","status","fail_code","fail_reasons","backtracks_total","max_energy_increase"]], on="case_id", how="left", indicator=True)

    missing = df[df["_merge"]!="both"]
    if len(missing):
        print("ERROR: some case_id not found in ledger:")
        print(missing[["case_id","_merge"]])
        return 1

    # expectation is encoded in notes starting with "EXPECT:FAIL"
    expect_fail = df["notes"].astype(str).str.contains("EXPECT:FAIL", na=False)
    got_fail = df["status"].astype(str).str.upper().eq("FAIL")

    bad = df[expect_fail & ~got_fail]
    if len(bad):
        print("FAILED: these were expected to FAIL but did not:")
        print(bad[["case_id","status","fail_code","backtracks_total","max_energy_increase","notes"]].to_string(index=False))
        return 1

    print("OK: all EXPECT:FAIL cases failed as expected.")
    print(df[expect_fail][["case_id","status","fail_code","backtracks_total","max_energy_increase"]].to_string(index=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
