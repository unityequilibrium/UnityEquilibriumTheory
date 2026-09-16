"""Build the single lazy-import registry used after root shim removal."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
OUTPUT = CORE / "00_governance" / "uet_core_legacy_module_aliases.json"
GENERATOR = "docs/scripts/audit/build_uet_core_legacy_module_aliases.py"
PROTECTED = {"__init__.py", "core_paths.py", "core_compat.py"}
MODULE_PATTERN = re.compile(r'"(docs\.(?:core|scripts)\.[^"]+)"')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_path(module_name: str) -> str:
    return module_name.replace(".", "/") + ".py"


def build() -> dict[str, object]:
    aliases: list[dict[str, object]] = []
    failures: list[str] = []
    for source in sorted(CORE.glob("*.py")):
        if source.name in PROTECTED:
            continue
        text = source.read_text(encoding="utf-8")
        matches = MODULE_PATTERN.findall(text)
        if not matches:
            failures.append(source.relative_to(ROOT).as_posix())
            continue
        canonical_module = matches[-1]
        canonical = canonical_path(canonical_module)
        target = ROOT / canonical
        if not target.exists():
            failures.append(f"{source.relative_to(ROOT).as_posix()} -> {canonical}")
            continue
        legacy_path = source.relative_to(ROOT).as_posix()
        aliases.append(
            {
                "alias_id": "UET-LEGACY-MODULE-" + hashlib.sha1(legacy_path.encode()).hexdigest()[:12].upper(),
                "legacy_module": "docs.core." + source.stem,
                "legacy_path": legacy_path,
                "canonical_module": canonical_module,
                "canonical_path": canonical,
                "legacy_sha256": sha256(source),
                "canonical_sha256": sha256(target),
                "status": "REMOVED_ROOT_SHIM",
                "compatibility_mode": "lazy_meta_path_alias",
                "claim_boundary": "import compatibility only; no physics or evidence promotion",
            }
        )
    # After the physical cleanup, the old root files are intentionally absent.
    # Keep the previously generated alias table as the compatibility source of
    # truth instead of rebuilding an empty table from the cleaned root.
    if not aliases and OUTPUT.exists():
        try:
            prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            prior = {}
        prior_aliases = prior.get("aliases", [])
        if isinstance(prior_aliases, list):
            aliases = [item for item in prior_aliases if isinstance(item, dict)]
    aliases.sort(key=lambda item: str(item["legacy_module"]))
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_legacy_module_aliases",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "status": "PASS" if not failures else "BLOCKED",
        "source_root": "docs/core root compatibility Python modules",
        "compatibility_mode": "lazy_meta_path_alias",
        "alias_count": len(aliases),
        "aliases": aliases,
        "unresolved_sources": failures,
        "claim_boundary": "organization and import compatibility only; no physics-status promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args()
    payload = build()
    if not args.check:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "alias_count": payload["alias_count"],
                "unresolved": len(payload["unresolved_sources"]),
            },
            ensure_ascii=False,
        )
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
