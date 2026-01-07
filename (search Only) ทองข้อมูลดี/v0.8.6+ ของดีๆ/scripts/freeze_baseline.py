#!/usr/bin/env python
from __future__ import annotations
import argparse, json, hashlib, os
from pathlib import Path
from typing import Dict, Any, List, Tuple

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_tree(root: Path, include_ext: tuple[str,...] = (".py",".md",".json",".csv")) -> str:
    # Deterministic hash over file paths + their content hashes
    items: List[Tuple[str,str]] = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and (p.suffix in include_ext):
            rel = str(p.relative_to(root)).replace("\\","/")
            items.append((rel, sha256_file(p)))
    h = hashlib.sha256()
    for rel, fh in items:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(fh.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness_root", default=".", help="root of harness repo (contains uet_core/ scripts/)")
    ap.add_argument("--out", default="baseline_lock", help="output folder")
    ap.add_argument("--smoke_ledger", default="", help="path to smoke ledger.csv (optional)")
    ap.add_argument("--golden_ledger", default="", help="path to golden ledger_golden.csv (optional)")
    ap.add_argument("--tier1_ledger", default="", help="path to tier1 ledger_tier1.csv (optional)")
    ap.add_argument("--demo_pack", default="", help="path to demo_pack folder (optional)")
    ap.add_argument("--notes", default="", help="freeform notes")
    args = ap.parse_args()

    harness_root = Path(args.harness_root).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Core hashes
    uet_core = harness_root / "uet_core"
    scripts = harness_root / "scripts"
    if not uet_core.exists() or not scripts.exists():
        raise SystemExit("harness_root must contain uet_core/ and scripts/")

    code_tree_hash = sha256_tree(harness_root, include_ext=(".py",".md",".json",".csv"))
    core_hash = sha256_tree(uet_core, include_ext=(".py",))
    scripts_hash = sha256_tree(scripts, include_ext=(".py",))

    artifacts: Dict[str, Any] = {}
    def add_art(name: str, path_str: str):
        if not path_str:
            return
        p = Path(path_str).resolve()
        if not p.exists():
            artifacts[name] = {"path": str(p), "exists": False}
            return
        if p.is_file():
            artifacts[name] = {"path": str(p), "exists": True, "sha256": sha256_file(p)}
        else:
            artifacts[name] = {"path": str(p), "exists": True, "sha256_tree": sha256_tree(p)}

    add_art("smoke_ledger", args.smoke_ledger)
    add_art("golden_ledger", args.golden_ledger)
    add_art("tier1_ledger", args.tier1_ledger)
    add_art("demo_pack", args.demo_pack)

    manifest = {
        "kind": "UET_BASELINE_LOCK",
        "version": "v0.1",
        "created_utc": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "harness_root": str(harness_root),
        "hashes": {
            "code_tree_hash": code_tree_hash,
            "uet_core_hash": core_hash,
            "scripts_hash": scripts_hash,
        },
        "artifacts": artifacts,
        "notes": args.notes,
    }

    out_manifest = out_dir / "baseline_manifest.json"
    out_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    # Minimal human-readable summary
    lines = []
    lines.append("# Baseline Lock Summary")
    lines.append("")
    lines.append(f"- created_utc: `{manifest['created_utc']}`")
    lines.append(f"- code_tree_hash: `{code_tree_hash}`")
    lines.append(f"- uet_core_hash: `{core_hash}`")
    lines.append(f"- scripts_hash: `{scripts_hash}`")
    lines.append("")
    lines.append("## Artifacts")
    if artifacts:
        for k,v in artifacts.items():
            if v.get("exists"):
                if "sha256" in v:
                    lines.append(f"- {k}: `{v['path']}` sha256=`{v['sha256']}`")
                else:
                    lines.append(f"- {k}: `{v['path']}` sha256_tree=`{v['sha256_tree']}`")
            else:
                lines.append(f"- {k}: `{v['path']}` (MISSING)")
    else:
        lines.append("_No artifacts provided._")
    lines.append("")
    if args.notes:
        lines.append("## Notes")
        lines.append(args.notes)
        lines.append("")

    (out_dir / "BASELINE_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_manifest}")
    print(f"Wrote {out_dir/'BASELINE_SUMMARY.md'}")

if __name__ == "__main__":
    main()
