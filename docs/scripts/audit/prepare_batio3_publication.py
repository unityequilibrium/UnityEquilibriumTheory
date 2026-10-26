"""Metadata-only BaTiO3 dependency packaging; never executes research producers.

--rebind changes only declared provenance; one legacy context snapshot is embedded
byte-for-byte in the existing manifest, not supplied by private Git history at check time.
--check is offline and read-only, and does not require the local research commit.
Full Git history is required for the already-public historical input pins.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import (
    artifact_metadata, contract_hash, identity_hash, load_json, TEXT,
)

T = "docs/topics/0.13_Thermodynamic_Bridge"
MANIFEST = f"{T}/Data/03_Research/batio3_publication_manifest.json"
CONTRACT = f"{T}/calculation_contracts/batio3_static_correspondence_audit.json"
SCRIPT = "docs/scripts/audit/prepare_batio3_publication.py"
TESTS = "docs/scripts/audit/tests/test_batio3_publication_package.py"
META = frozenset({"contract_id", "contract_sha256", "contract_review_status", "identities"})
JOINT = f"{T}/calculation_contracts/joint_thermodynamic_completion.json"
PLATFORM = f"{T}/Result/artifacts/t13_physical_platform_correspondence_screen.json"
INHERITED = ("parent_static_reference_audit", "phi_variance_static_admissibility")


def digest(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def normalized_hash(path, data):
    if Path(path).suffix.lower() in TEXT:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def payload(value, path=None):
    result = deepcopy({k: v for k, v in value.items() if k not in META})
    if path == PLATFORM:
        for stem in INHERITED:
            result["inherited_evidence"][stem]["contract_sha256"] = "PROVENANCE_REFERENCE_ONLY"
    return result


def semantics(value):
    result = deepcopy({k: v for k, v in value.items() if k != "identities"})
    change = result.get("observation", {}).get("system_partition", {}).get("boundary_change")
    if change:
        # Only the referenced contract's digest is provenance. IDs, partition,
        # outcome and explanation remain part of the immutable scientific scope.
        change["baseline_contract_sha256"] = "PROVENANCE_REFERENCE_ONLY"
    return result


def git(root, *args):
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false",
                                    "-C", str(root), *args], stderr=subprocess.PIPE)


def target(root, relative):
    p = (root / relative).resolve()
    if not p.is_relative_to(root.resolve()) or Path(relative).is_absolute():
        raise ValueError("publication path escapes review workspace")
    return p


def records(manifest, kind):
    return [r for r in manifest["files"] if r["kind"] == kind]


def verify_snapshot(manifest):
    snapshot = manifest["historical_local_snapshots"][0]
    text = snapshot["normalized_text"]
    if normalized_hash(snapshot["path"], text.encode()) != snapshot["sha256"]:
        raise ValueError("embedded historical snapshot hash mismatch")
    if json.loads(text)["contract_id"] != snapshot["contract_id"]:
        raise ValueError("embedded historical contract ID mismatch")
    return snapshot


def capture_snapshot(root, manifest):
    """One-time local packaging input; never called by read-only check."""
    snapshot = manifest["historical_local_snapshots"][0]
    if "normalized_text" not in snapshot:
        raw = git(root, "show", snapshot["commit"] + ":" + snapshot["path"])
        if normalized_hash(snapshot["path"], raw) != snapshot["sha256"]:
            raise ValueError("legacy source snapshot differs from declared identity")
        snapshot["normalized_text"] = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    verify_snapshot(manifest)
    row = next(r for r in manifest["files"] if r["path"] == PLATFORM)
    if "nested_provenance" not in row:
        old = load_json(target(root, PLATFORM))
        if digest(payload(old)) != row["payload_sha256"]:
            raise ValueError("legacy platform payload changed before provenance classification")
        row["original_payload_with_provenance_sha256"] = row["payload_sha256"]
        row["original_nested_metadata"] = {
            stem: old["inherited_evidence"][stem]["contract_sha256"] for stem in INHERITED}
        row["nested_provenance"] = ["inherited_evidence." + stem + ".contract_sha256" for stem in INHERITED]
        row["payload_sha256"] = digest(payload(old, PLATFORM))
    _write_json(target(root, MANIFEST), manifest)


def verify_preservation(root, manifest):
    """Verify source snapshots, not a substitute for physical acceptance."""
    if manifest["approval"] != "LOCAL_REVIEW_ONLY; no push or merge authorized until file-list review":
        raise ValueError("publication approval boundary changed")
    verify_snapshot(manifest)
    if len({r["path"] for r in manifest["files"]}) != len(manifest["files"]):
        raise ValueError("duplicate publication file")
    for r in manifest["files"]:
        p = target(root, r["path"])
        if r["kind"] == "immutable":
            if normalized_hash(r["path"], p.read_bytes()) != r["source_sha256"]:
                raise ValueError("immutable source changed: " + r["path"])
        elif r["kind"] == "contract":
            if digest(semantics(load_json(p))) != r["semantic_sha256"]:
                raise ValueError("contract physics/scope changed: " + r["path"])
        elif r["kind"] == "artifact":
            if digest(payload(load_json(p), r["path"])) != r["payload_sha256"]:
                raise ValueError("scientific artifact payload changed: " + r["path"])
        else:
            raise ValueError("unclassified publication file")
    for r in manifest["public_matched_inputs"]:
        if normalized_hash(r["path"], target(root, r["path"]).read_bytes()) != r["sha256"]:
            raise ValueError("current main input changed: " + r["path"])
    for r in manifest["historical_pins"]:
        git(root, "merge-base", "--is-ancestor", r["commit"], manifest["public_base"])
        b = git(root, "show", r["commit"] + ":" + r["path"])
        if normalized_hash(r["path"], b) != r["sha256"]:
            raise ValueError("public historical input hash mismatch")
        current_base = git(root, "show", manifest["public_base"] + ":" + r["path"])
        if normalized_hash(r["path"], target(root, r["path"]).read_bytes()) != normalized_hash(r["path"], current_base):
            raise ValueError("current Core/Topic11 artifact overwritten: " + r["path"])


def _write_json(path, data):
    """Explicit bulk mechanical provenance rewrite, never scientific values."""
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True,
                         indent=2, allow_nan=False) + "\n"
    if path.read_text(encoding="utf-8") != encoded:
        path.write_text(encoded, encoding="utf-8", newline="\n")
        return True
    return False


def rebind(root, manifest):
    capture_snapshot(root, manifest)
    verify_preservation(root, manifest)
    snapshot = verify_snapshot(manifest)
    pins = {x["path"]: x for x in manifest["historical_pins"]}
    contract_paths = [r["path"] for r in records(manifest, "contract")]
    artifacts = records(manifest, "artifact")
    touched = set()
    for _ in range(2 * (len(contract_paths) + len(artifacts)) + 1):
        changed = False
        for p in contract_paths:
            c = load_json(target(root, p))
            if p == CONTRACT:
                for extra, role in ((MANIFEST, "input"), (SCRIPT, "code"), (TESTS, "code")):
                    if not any(i["path"] == extra for i in c["identities"]):
                        c["identities"].append({"path": extra, "kind": "working_file",
                                                "role": role, "sha256": "0" * 64})
            for item in c["identities"]:
                if (p == JOINT and item.get("commit") == snapshot["commit"]
                        and item["path"] == snapshot["path"]):
                    # Same REQUIRED historical bytes, now embedded in an admitted
                    # data input instead of an unavailable local-only Git object.
                    item["path"] = MANIFEST
                    item["kind"] = "working_file"
                    item.pop("commit")
                if item["path"] in pins:
                    pin = pins[item["path"]]
                    item["kind"] = "git_blob"
                    item["commit"] = pin["commit"]
                    item["sha256"] = pin["sha256"]
                else:
                    item["sha256"] = identity_hash(root, item)
            change = c.get("observation", {}).get("system_partition", {}).get("boundary_change")
            if change:
                baseline = load_json(target(root, change["baseline_identity"]))
                if baseline["contract_id"] != change["baseline_contract_id"]:
                    raise ValueError("boundary baseline ID changed")
                change["baseline_contract_sha256"] = contract_hash(baseline)
            if _write_json(target(root, p), c):
                changed = True
                touched.add(p)
        contracts = {load_json(target(root, p))["contract_id"]: load_json(target(root, p))
                     for p in contract_paths}
        for row in artifacts:
            p = row["path"]
            a = load_json(target(root, p))
            c = contracts[a["contract_id"]]
            a["contract_sha256"] = contract_hash(c)
            a["identities"] = deepcopy(c["identities"])
            if p == PLATFORM:
                for stem in INHERITED:
                    upstream = load_json(target(root, f"{T}/calculation_contracts/{stem}.json"))
                    a["inherited_evidence"][stem]["contract_sha256"] = contract_hash(upstream)
            # Existing review disposition is preserved, not promoted by packaging.
            if _write_json(target(root, p), a):
                changed = True
                touched.add(p)
        if not changed:
            break
    else:
        raise ValueError("provenance graph failed to reach a fixed point")
    result = check(root, manifest)
    result["provenance_files_rewritten"] = len(touched)
    return result


def check(root, manifest):
    verify_preservation(root, manifest)
    contracts = {}
    for row in records(manifest, "contract"):
        c = load_json(target(root, row["path"]))
        for item in c["identities"]:
            if item["kind"] == "git_blob":
                git(root, "merge-base", "--is-ancestor", item["commit"], manifest["public_base"])
        if row["path"] == JOINT:
            binding = [i for i in c["identities"] if i["path"] == MANIFEST]
            if len(binding) != 1 or binding[0].get("availability") != "REQUIRED":
                raise ValueError("historical snapshot remains a REQUIRED supplied input")
        meta = artifact_metadata(c, root)
        if c["review"]["status"] != row["review_status"]:
            raise ValueError("review disposition changed during packaging")
        contracts[c["contract_id"]] = meta
    for row in records(manifest, "artifact"):
        a = load_json(target(root, row["path"]))
        expected = contracts[a["contract_id"]]
        if any(a.get(k) != expected[k] for k in META):
            raise ValueError("stale artifact provenance: " + row["path"])
        if a.get("contract_review_status") != row["review_status"]:
            raise ValueError("artifact review disposition changed")
        if row["path"] == PLATFORM:
            for stem in INHERITED:
                upstream = load_json(target(root, f"{T}/calculation_contracts/{stem}.json"))
                if a["inherited_evidence"][stem]["contract_sha256"] != contract_hash(upstream):
                    raise ValueError("stale nested inherited-evidence provenance")
        serialized = json.dumps(a, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if target(root, row["path"]).read_bytes() != serialized.encode():
            raise ValueError("artifact serialization differs from its producer")
    return {"kind": "PUBLICATION_PACKAGING_NOT_PHYSICAL_VALIDATION",
            "imported_files": len(manifest["files"]), "contracts": len(contracts),
            "preserved_artifact_payloads": len(records(manifest, "artifact")),
            "unchanged_current_inputs": len(manifest["public_matched_inputs"]),
            "public_historical_pins": len(manifest["historical_pins"]),
            "embedded_historical_snapshots": len(manifest["historical_local_snapshots"]),
            "old_scientific_producers_executed": False, "push_performed": False,
            "approval": manifest["approval"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--rebind", action="store_true")
    args = parser.parse_args(argv)
    manifest = load_json(ROOT / MANIFEST)
    result = rebind(ROOT, manifest) if args.rebind else check(ROOT, manifest)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
