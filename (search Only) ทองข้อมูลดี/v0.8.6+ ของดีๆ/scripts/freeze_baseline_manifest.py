#!/usr/bin/env python
from __future__ import annotations
import argparse, json, hashlib, datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

def parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def add_evidence(evidence: Dict[str, Any], key_prefix: str, path: Optional[str]) -> Optional[Path]:
    if not path:
        return None
    p = Path(path)
    evidence[f"{key_prefix}_path"] = str(p)
    if p.exists() and p.is_file():
        evidence[f"{key_prefix}_sha256"] = sha256_file(p)
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="baseline/baseline_manifest.json")
    ap.add_argument("--dt_presets", default="", help="dt presets json to embed + hash")
    ap.add_argument("--band_dt_presets", default="", help="band dt presets json to embed + hash")
    ap.add_argument("--band_stability", default="", help="band stability report to hash")
    ap.add_argument("--metric_thresholds", default="", help="metric thresholds json to hash")
    ap.add_argument("--stress_spec", default="", help="stress_spec.json to hash")
    ap.add_argument("--extra_files", default="", help="semicolon-separated extra files to hash")
    ap.add_argument("--note", default="", help="optional note")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, Any] = {
        "created_at_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "note": args.note,
        "dt_presets": None,
        "band_dt_presets": None,
        "evidence": {},
    }
    evidence: Dict[str, Any] = {}

    # Embed presets (if provided)
    p = add_evidence(evidence, "dt_presets", args.dt_presets)
    if p and p.exists():
        manifest["dt_presets"] = json.loads(p.read_text(encoding="utf-8"))

    p = add_evidence(evidence, "band_dt_presets", args.band_dt_presets)
    if p and p.exists():
        manifest["band_dt_presets"] = json.loads(p.read_text(encoding="utf-8"))

    # Hash other key files
    add_evidence(evidence, "band_stability", args.band_stability)
    add_evidence(evidence, "metric_thresholds", args.metric_thresholds)
    add_evidence(evidence, "stress_spec", args.stress_spec)

    evidence["extra_files"] = []
    for s in parse_list(args.extra_files):
        p = Path(s)
        rec = {"path": str(p)}
        if p.exists() and p.is_file():
            rec["sha256"] = sha256_file(p)
        evidence["extra_files"].append(rec)

    manifest["evidence"] = evidence
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Wrote", out)

if __name__ == "__main__":
    main()
