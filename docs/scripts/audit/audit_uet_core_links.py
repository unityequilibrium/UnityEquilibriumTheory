"""Audit local Markdown links in the active UET core tree."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
AUDIT = CORE / "00_governance" / "uet_core_links_audit.json"
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
SKIP_PREFIXES = ("#", "http://", "https://", "mailto:", "data:", "codex:", "plugin:")
PATH_SUFFIXES = {".md", ".json", ".py", ".png", ".jpg", ".jpeg", ".svg", ".html", ".csv", ".npz"}


def resolve_target(source: Path, target: str) -> Path | None:
    value = unquote(target.strip().split("#", 1)[0].split("?", 1)[0])
    if not value or value.startswith(SKIP_PREFIXES):
        return None
    # Square-bracket math also contains `](...)`; only path-shaped targets
    # belong to this audit.
    if not value.startswith(("./", "../", "/", "docs/")) and Path(value).suffix.lower() not in PATH_SUFFIXES:
        return None
    if value.startswith("/"):
        return ROOT / value.lstrip("/")
    if value.startswith("docs/"):
        return ROOT / value
    return source.parent / value


def build() -> dict[str, object]:
    checked: list[dict[str, str]] = []
    broken: list[dict[str, str]] = []
    for source in sorted(CORE.rglob("*.md")):
        relative_source = source.relative_to(ROOT).as_posix()
        if "/08_history/" in relative_source or "/99_review/" in relative_source:
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for raw_target in LINK_PATTERN.findall(text):
            target = resolve_target(source, raw_target)
            if target is None:
                continue
            record = {"source": source.relative_to(ROOT).as_posix(), "target": raw_target}
            checked.append(record)
            if not target.exists():
                broken.append({**record, "resolved": target.relative_to(ROOT).as_posix() if target.is_relative_to(ROOT) else str(target)})
    checks = [
        {
            "check_id": "active_core_markdown_links",
            "status": "PASS" if not broken else "FAIL",
            "observed": len(broken),
        }
    ]
    status = "PASS" if not broken else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_links_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_links.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "active_core_markdown_links_need_repair",
        "checks": checks,
        "links_checked": len(checked),
        "broken_links": broken,
        "claim_boundary": "Markdown path audit only; no physics-status promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "links_checked": result["links_checked"], "broken": len(result["broken_links"])}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
