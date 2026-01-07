#!/usr/bin/env python
from __future__ import annotations
import argparse
from uet_core.parser import parse_case_params
from uet_core.coercivity import check_C_only, check_CI

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["C_only","C_I"], required=True)
    ap.add_argument("--params", required=True)
    args = ap.parse_args()
    params = parse_case_params(args.model, args.params)
    res = check_C_only(params) if args.model == "C_only" else check_CI(params)
    print(f"STATUS: {res.status}")
    print(f"CODE:   {res.code}")
    print(f"MSG:    {res.message}")
    if res.status == "FAIL":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
