"""Inventory an existing recovery checkpoint against an immutable public commit."""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHECKPOINT = "4890ab874c0e20cbd3ce744091089a3d97aeb5b1"
BASE = "d59d31b3c90388998e48d3149e17e606cf30fa29"
OUTPUT = ROOT / "docs/meta/workspace_recovery_20261031.json"
RELOCATED = {
    "docs/core/07_artifacts/causal_influence_formula_audit.json": "docs/core/07_artifacts/correspondence/causal_influence_formula_audit.json",
    "docs/core/07_artifacts/causal_nonclosed_contract.json": "docs/core/07_artifacts/archive/causal_nonclosed_contract.json",
    "docs/core/07_artifacts/causal_nonclosed_kernel_verification.json": "docs/core/07_artifacts/verification/causal_nonclosed_kernel_verification.json",
    "docs/core/07_artifacts/uet_gr_research_program_gate.json": "docs/core/07_artifacts/gates/uet_gr_research_program_gate.json",
}


def git(*args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT,
        input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout


def tree(ref: str) -> dict[str, str]:
    result = {}
    for line in filter(None, git("ls-tree", "-r", "-z", ref).split(b"\0")):
        metadata, path = line.split(b"\t", 1)
        result[path.decode("utf-8")] = metadata.split()[2].decode("ascii")
    return result


def read_blobs(ids: set[str]) -> dict[str, bytes]:
    stream = git("cat-file", "--batch", input_bytes=("\n".join(sorted(ids)) + "\n").encode())
    result = {}
    cursor = 0
    while cursor < len(stream):
        end = stream.index(b"\n", cursor)
        sha, kind, size = stream[cursor:end].split()
        if kind != b"blob":
            raise ValueError(f"Expected blob, got {kind!r}")
        size = int(size)
        result[sha.decode()] = stream[end + 1:end + 1 + size]
        cursor = end + 2 + size
    return result


def same(left: bytes | None, right: bytes | None, path: str) -> bool:
    if left is None or right is None:
        return left is right
    if left.replace(b"\r\n", b"\n") == right.replace(b"\r\n", b"\n"):
        return True
    if path.endswith(".json"):
        try:
            # Compare JSON structurally without conflating booleans and numbers.
            return json.dumps(json.loads(left), sort_keys=True, separators=(",", ":")) == json.dumps(
                json.loads(right), sort_keys=True, separators=(",", ":")
            )
        except (ValueError, UnicodeDecodeError):
            pass
    return False


def inventory() -> dict:
    paths = [p.decode("utf-8") for p in git("diff-tree", "--no-commit-id", "--name-only", "-r", "-z", CHECKPOINT).split(b"\0") if p]
    refs = (CHECKPOINT + "^", CHECKPOINT, BASE)
    trees = [tree(ref) for ref in refs]
    ids = {t[p] for t in trees for p in paths if p in t}
    ids.update(trees[2][p] for p in RELOCATED.values() if p in trees[2])
    blobs = read_blobs(ids)
    original = git("show", "-s", "--format=%an%x00%aI", CHECKPOINT).decode("utf-8").strip().split("\0")
    rows = []
    for path in paths:
        ids = [t.get(path) for t in trees]
        parent, local, main = [blobs.get(sha) for sha in ids]
        if same(local, main, path):
            classification, disposition = "already_on_main", "already_published"
            blocker, action = None, "None; content matches baseline under declared comparison."
        elif main is None:
            classification, disposition = "missing_on_main", "blocked"
            blocker = "canonical_path_and_dependency_review"
            action = "Resolve canonical path, dependencies, provenance and validation before integration."
            if path in RELOCATED:
                blocker = "relocated_artifact_content_and_provenance_review"
                action = "Compare checkpoint content, generator and inputs with the recorded relocated artifact before integration."
                canonical = blobs.get(trees[2].get(RELOCATED[path]))
                try:
                    local_obj, canonical_obj = json.loads(local), json.loads(canonical)
                    if isinstance(local_obj, dict) and isinstance(canonical_obj, dict):
                        local_obj.pop("generated_at", None)
                        canonical_obj.pop("generated_at", None)
                        if json.dumps(local_obj, sort_keys=True) == json.dumps(canonical_obj, sort_keys=True):
                            disposition, blocker = "superseded", None
                            action = "Use relocated baseline artifact; JSON matches except generated_at."
                        elif local_obj.get("source_hashes") != canonical_obj.get("source_hashes"):
                            blocker = "relocated_artifact_source_identity_mismatch"
                            action = ("Review canonical docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md "
                                      "and docs/scripts/audit/audit_uet_gr_causal_nonclosed.py, then regenerate "
                                      "in isolation and verify input hashes and downstream gates.")
                except (TypeError, ValueError, UnicodeDecodeError):
                    pass
        elif same(parent, main, path):
            classification, disposition = "main_unchanged", "blocked"
            blocker = "local_delta_and_dependency_review"
            action = "Review checkpoint delta and validate its dependencies on the main baseline."
        else:
            classification, disposition = "both_sides_changed", "blocked"
            blocker = "two_sided_source_or_provenance_conflict"
            action = "Compare source, producer and inputs; reconcile without overwriting public evidence."
        if disposition == "blocked" and main is not None and path.endswith(".json"):
            try:
                local_obj, main_obj = json.loads(local), json.loads(main)
                if isinstance(local_obj, dict) and isinstance(main_obj, dict):
                    local_obj.pop("generated_at", None)
                    main_obj.pop("generated_at", None)
                    if json.dumps(local_obj, sort_keys=True) == json.dumps(main_obj, sort_keys=True):
                        disposition, blocker = "superseded", None
                        action = "Use baseline artifact; JSON matches except generated_at."
            except (TypeError, ValueError, UnicodeDecodeError):
                pass
        rows.append({
            "checkpoint_path": path, "canonical_path": RELOCATED.get(path, path),
            "source_commit": CHECKPOINT, "source_blob": ids[1], "parent_blob": ids[0],
            "main_blob": ids[2], "canonical_baseline_blob": trees[2].get(RELOCATED.get(path, path)),
            "author": original[0],
            "author_date": original[1], "classification": classification,
            "disposition": disposition,
            "verification": "baseline JSON structurally equal except generated_at" if disposition == "superseded" else "structural comparison only",
            "blocker": blocker, "next_action": action,
        })
    return {
        "schema_version": 1, "checkpoint": CHECKPOINT, "baseline_main": BASE,
        "comparison": "CRLF normalized; JSON structurally compared; no scientific equivalence inferred",
        "summary": dict(sorted(collections.Counter(row["classification"] for row in rows).items())),
        "records": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check and subprocess.run(
        ["git", "cat-file", "-e", CHECKPOINT + "^{commit}"], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode:
        # Public checkouts do not contain the unpublished checkpoint object.
        # Validate the manifest structure without claiming to verify its blobs.
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        rows = data.get("records", [])
        if (data.get("checkpoint") != CHECKPOINT or data.get("baseline_main") != BASE
                or len(rows) != 467 or len({r.get("checkpoint_path") for r in rows}) != 467
                or any(r.get("source_commit") != CHECKPOINT or not r.get("source_blob") for r in rows)):
            return 1
        print("Manifest structure checked; local checkpoint blobs are unavailable and were not reverified.")
        return 0
    result = inventory()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered else 1
    OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
