"""Preserve incomplete historical outputs in valid, explicitly invalid envelopes."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "d59d31b3c90388998e48d3149e17e606cf30fa29"
PATHS = {
    "docs/meta/Result/Res_Unification_1774904186.json": "7ff1894a18c1d1c28014a3a1aec71b9ced54afb51b1f5f2b8b0cfbc2ded102c8",
    **{f"docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/data_logs/{x}_Research_Benchmark_Comparison/benchmark_summary.json": "b85d2cae91c58841ce4f95460d308aea42f66608473322705ef8b4a97a089798" for x in ("1769079866", "1769079947", "1769080001")},
}


def envelope(path: str, expected: str) -> str:
    original = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
    if hashlib.sha256(original).hexdigest() != expected:
        raise ValueError(f"Historical input hash mismatch: {path}")
    try:
        json.loads(original)
    except json.JSONDecodeError as exc:
        error = {"message": exc.msg, "line": exc.lineno, "column": exc.colno}
    else:
        raise ValueError(f"Historical input is not invalid JSON: {path}")
    return json.dumps({
        "status": "INVALID_HISTORICAL_OUTPUT",
        "interpretation": "Incomplete historical output; no result or pass can be inferred.",
        "original_commit": BASE,
        "original_path": path,
        "original_sha256": expected,
        "original_bytes_base64": base64.b64encode(original).decode("ascii"),
        "parse_error": error,
    }, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, expected in PATHS.items():
        output = envelope(path, expected)
        dest = ROOT / path
        if args.check:
            if not dest.exists() or dest.read_text(encoding="utf-8") != output:
                return 1
        else:
            if dest.read_bytes() != subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT):
                raise ValueError(f"Working file changed; refusing to replace {path}")
            dest.write_text(output, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
