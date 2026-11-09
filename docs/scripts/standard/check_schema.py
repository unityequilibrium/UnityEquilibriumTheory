"""Validate Research Standard v2 records and their cross-references.

Checks (docs/STANDARD.md sections 1, 3, 4, 5, 7):
- every record validates against docs/standard/schema.json
- ids are unique; results point to existing claims and Test Cards
- L2/L3 results point to an APPROVED or CLOSED Test Card
- a claim's level is backed by at least one result of that level (FAILED needs
  a FAILED result); L0 claims need no evidence
- Test Card data sources exist in the data manifest
- PUBLIC data manifest files exist and match their sha256 (raw-data hash lock)
- every referenced data file, Test Card script and Result producer exists and
  is tracked by git (catches files hidden by .gitignore)

Usage: python docs/scripts/standard/check_schema.py [--root PATH]
Exit status 0 when clean, 1 when any error is found.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CLAIMS_PATH,
    DATA_MANIFEST_PATH,
    LEVEL_ORDER,
    REPO_ROOT,
    RESULTS_DIR,
    SCHEMA_PATH,
    TESTS_DIR,
    THEORY_CARD_PATH,
    load_json,
    record_files,
)


class SchemaChecker:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        schema = load_json(root / SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        self.schema_id = schema["$id"]
        self.registry = Registry().with_resource(
            self.schema_id, Resource.from_contents(schema)
        )

    def validate(self, kind: str, record: Any, label: str) -> bool:
        validator = Draft202012Validator(
            {"$ref": f"{self.schema_id}#/$defs/{kind}"}, registry=self.registry
        )
        problems = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        for problem in problems:
            where = "/".join(str(p) for p in problem.path) or "<root>"
            self.errors.append(f"{label}: {where}: {problem.message}")
        return not problems

    def load(self, path: Path, kind: str) -> Any | None:
        label = path.relative_to(self.root).as_posix()
        try:
            record = load_json(path)
        except (OSError, ValueError) as exc:
            self.errors.append(f"{label}: cannot read JSON: {exc}")
            return None
        return record if self.validate(kind, record, label) else None

    def run(self) -> list[str]:
        root = self.root
        claims_reg = self.load(root / CLAIMS_PATH, "claims_registry") if (root / CLAIMS_PATH).exists() else {"claims": []}
        manifest = self.load(root / DATA_MANIFEST_PATH, "data_manifest") if (root / DATA_MANIFEST_PATH).exists() else {"entries": []}
        claims_reg = claims_reg or {"claims": []}
        manifest = manifest or {"entries": []}

        theory_versions: set[tuple[str, int]] = set()
        if (root / THEORY_CARD_PATH).exists():
            card = self.load(root / THEORY_CARD_PATH, "theory_card")
            if card:
                theory_versions.add((card["card_id"], card["version"]))

        tests: dict[str, dict] = {}
        for path in record_files(root, TESTS_DIR):
            card = self.load(path, "test_card")
            if card is None:
                continue
            label = path.relative_to(root).as_posix()
            if card["test_id"] in tests:
                self.errors.append(f"{label}: duplicate test_id {card['test_id']}")
            if path.stem != card["test_id"]:
                self.errors.append(f"{label}: file name must equal test_id {card['test_id']}")
            tests[card["test_id"]] = card

        results: dict[str, dict] = {}
        for path in record_files(root, RESULTS_DIR):
            result = self.load(path, "result")
            if result is None:
                continue
            label = path.relative_to(root).as_posix()
            if result["result_id"] in results:
                self.errors.append(f"{label}: duplicate result_id {result['result_id']}")
            if path.stem != result["result_id"]:
                self.errors.append(f"{label}: file name must equal result_id {result['result_id']}")
            results[result["result_id"]] = result

        claims: dict[str, dict] = {}
        for claim in claims_reg["claims"]:
            if claim["claim_id"] in claims:
                self.errors.append(f"claims.json: duplicate claim_id {claim['claim_id']}")
            claims[claim["claim_id"]] = claim

        data_ids = {entry["data_id"] for entry in manifest["entries"]}

        for test_id, card in tests.items():
            if card["claim_id"] not in claims:
                self.errors.append(f"test {test_id}: unknown claim_id {card['claim_id']}")
            ref = (card["theory_card"]["card_id"], card["theory_card"]["version"])
            if ref not in theory_versions:
                self.errors.append(f"test {test_id}: theory card {ref[0]} v{ref[1]} not found in {THEORY_CARD_PATH.as_posix()}")
            for source in card["data_sources"]:
                if source["data_id"] not in data_ids:
                    self.errors.append(f"test {test_id}: data_id {source['data_id']} not in data manifest")
            approval = card.get("approval")
            if approval and approval["approved_by"].strip().lower() == card["drafted_by"].strip().lower():
                self.errors.append(f"test {test_id}: a card cannot be approved by its drafter")

        for result_id, result in results.items():
            if result["claim_id"] not in claims:
                self.errors.append(f"result {result_id}: unknown claim_id {result['claim_id']}")
            test_id = result.get("test_card_id")
            if test_id is not None:
                card = tests.get(test_id)
                if card is None:
                    self.errors.append(f"result {result_id}: unknown test_card_id {test_id}")
                elif result["level"] in ("L2_CONFRONTED", "L3_REPLICATED") and card["status"] == "DRAFT":
                    self.errors.append(f"result {result_id}: Test Card {test_id} is not APPROVED")

        for claim_id, claim in claims.items():
            level = claim["level"]
            evidence = [results[r] for r in claim["evidence"] if r in results]
            for missing in (r for r in claim["evidence"] if r not in results):
                self.errors.append(f"claim {claim_id}: evidence {missing} has no result record")
            if level == "L0_SPECULATIVE":
                continue
            if level == "FAILED":
                if not any(r["level"] == "FAILED" for r in evidence):
                    self.errors.append(f"claim {claim_id}: FAILED claim needs a FAILED result")
                continue
            needed = LEVEL_ORDER[level]
            if not any(LEVEL_ORDER.get(r["level"], -1) >= needed for r in evidence):
                self.errors.append(f"claim {claim_id}: level {level} is not backed by a result of that level")

        for entry in manifest["entries"]:
            if entry["visibility"] != "PUBLIC":
                continue
            path = root / entry["path"]
            if not path.is_file():
                self.errors.append(f"data {entry['data_id']}: file {entry['path']} missing")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != entry["sha256"]:
                self.errors.append(f"data {entry['data_id']}: sha256 mismatch for {entry['path']}")
            self.require_tracked(entry["path"], f"data {entry['data_id']}")

        for test_id, card in tests.items():
            self.require_tracked(script_path(card["prediction_method"]["script"]), f"test {test_id} script")
        for result_id, result in results.items():
            self.require_tracked(script_path(result["producer"]["script"]), f"result {result_id} producer")

        return self.errors

    def require_tracked(self, rel: str, label: str) -> None:
        """A referenced file must exist and be in git (staged or committed).

        Guards against files hidden by .gitignore (e.g. the global *.csv rule),
        which pass every local check but are absent from the repository.
        Skipped when the root is not a git work tree (unit-test fixtures).
        """
        if not (self.root / rel).is_file():
            self.errors.append(f"{label}: file {rel} missing")
            return
        if not self.in_git:
            return
        proc = subprocess.run(["git", "-C", str(self.root), "ls-files", "--error-unmatch", "--", rel],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            self.errors.append(f"{label}: {rel} is not tracked by git (ignored or never added; use git add -f if it is public)")

    @property
    def in_git(self) -> bool:
        if not hasattr(self, "_in_git"):
            proc = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True)
            self._in_git = proc.returncode == 0 and Path(proc.stdout.strip()).resolve() == self.root.resolve()
        return self._in_git


def script_path(text: str) -> str:
    """Strip run notes and pytest node ids: 'a/b.py::test_x (run as ...)' -> 'a/b.py'."""
    return text.split(" (", 1)[0].split("::", 1)[0].strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors = SchemaChecker(args.root.resolve()).run()
    for error in errors:
        print(f"ERROR {error}")
    print(f"check_schema: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
