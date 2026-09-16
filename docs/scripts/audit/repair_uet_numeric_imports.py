"""Repair Python imports accidentally rewritten to numeric package syntax."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs"
ALIASES = ROOT / "docs" / "core" / "00_governance" / "uet_core_legacy_module_aliases.json"
TEXT_SUFFIX = ".py"


def write_retry(path: Path, text: str) -> None:
    for attempt in range(5):
        try:
            path.write_text(text, encoding="utf-8")
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.5)


def main() -> int:
    payload = json.loads(ALIASES.read_text(encoding="utf-8"))
    replacements = sorted(
        (
            (str(item["canonical_module"]), str(item["legacy_module"]))
            for item in payload.get("aliases", [])
            if str(item.get("canonical_module", "")).startswith("docs.core.0")
        ),
        key=lambda pair: len(pair[0]),
        reverse=True,
    )
    changed: list[dict[str, str]] = []
    for path in sorted(DOCS.rglob("*.py")):
        if any(part in {".git", "__pycache__", "07_artifacts", "08_history"} for part in path.parts):
            continue
        before = path.read_text(encoding="utf-8")
        after = before
        for canonical, legacy in replacements:
            after = re.sub(
                rf"(?<![A-Za-z0-9_.]){re.escape(canonical)}(?![A-Za-z0-9_])",
                legacy,
                after,
            )
        if after != before:
            write_retry(path, after)
            changed.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256_before": hashlib.sha256(before.encode()).hexdigest(),
                    "sha256_after": hashlib.sha256(after.encode()).hexdigest(),
                }
            )
    print(json.dumps({"status": "PASS", "files_changed": len(changed)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
