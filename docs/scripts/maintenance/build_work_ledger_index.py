"""Build source-linked ledger views without rewriting historical work records."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata


REPO = Path(__file__).resolve().parents[3]
STREAMS = {
    "research": ("RESEARCH.md", "Research Work"),
    "book-history": ("BOOK_HISTORY.md", "Historical Book And Theory Work"),
    "operations": ("OPERATIONS.md", "Repository, Policy And Tooling Work"),
    "mixed": ("MIXED.md", "Mixed Research And Book Records"),
    "review": ("REVIEW.md", "Classification Review"),
}
AREA_STREAM = {
    "research-core": "research",
    "research-standards": "research",
    "data-provenance": "research",
    "book-writing": "book-history",
    "theory-history": "book-history",
    "repo-ops": "operations",
    "documentation-system": "operations",
    "thai-policy": "operations",
    "services-tools": "operations",
    "raw-private": "operations",
    "result-artifacts": "operations",
}
DATE_FILE = re.compile(r"\d{4}-\d{2}-\d{2}\.md\Z")
FIELD = re.compile(
    r"^\s*(?:[-*]\s+)?(?:\*\*)?(area(?:\s+id)?|stream|workspace|paths?|files(?:\s+or\s+artifacts)?)"
    r"(?:\*\*)?\s*:\s*(.*)$", re.I
)
AREA_PATTERN = re.compile(r"(?<![\w-])(" + "|".join(AREA_STREAM) + r")(?![\w-])", re.I)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def slug(title: str) -> str:
    title = title.lower().strip()
    return "".join(
        c for c in title
        if c in "-_ " or unicodedata.category(c)[0] in {"L", "N", "M"}
    ).replace(" ", "-")


def classify(body: str, title: str = "") -> dict:
    fields: dict[str, list[str]] = {}
    fenced = False
    for line in body.splitlines():
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            fenced = not fenced
            continue
        if fenced:
            continue
        line = line.replace("**", "")
        line = re.sub(r"^(\s*[-*]?\s*Area(?: id)?)\s+(?=`)", r"\1: ", line, flags=re.I)
        match = FIELD.match(line)
        if match:
            fields.setdefault(match[1].lower(), []).append(match[2])
    area_fields = fields.get("area", []) + fields.get("area id", [])
    heading_area = re.match(r"^([a-z-]+)\s*/", title.lower())
    if not area_fields and heading_area and heading_area[1] in AREA_STREAM:
        area_fields = [heading_area[1]]
    areas = list(dict.fromkeys(AREA_PATTERN.findall(" ".join(area_fields).lower())))
    first = area_fields[0] if area_fields else ""
    primary_text = re.split(r"[;(]\s*secondary\b", first, maxsplit=1, flags=re.I)[0]
    primary = AREA_PATTERN.findall(primary_text.lower())
    related = sorted({AREA_STREAM[a] for a in areas})
    flags = []
    if len(area_fields) > 1:
        flags.append("multiple_area_fields")
    paths = " ".join(v for k, values in fields.items() if k not in {"area", "area id", "stream"} for v in values)
    has_book_path = bool(re.search(r"(?:^|[\s`(,])uet_history[/\\]", paths))
    has_research_path = bool(re.search(r"docs[/\\](?:core|topics|meta|scripts)[/\\]", paths))
    basis = "explicit_primary_area"
    if {AREA_STREAM[a] for a in primary} >= {"research", "book-history"}:
        stream = "mixed"
        flags.append("multiple_primary_domains")
    elif primary:
        stream = AREA_STREAM[primary[0]]
        if primary[0] == "result-artifacts" and has_research_path and not has_book_path:
            stream, basis = "research", "artifact_area_and_research_workspace"
    elif has_book_path and has_research_path:
        stream, basis = "mixed", "workspace_paths_without_primary_area"
        flags.append("missing_primary_area")
    elif has_book_path or has_research_path:
        stream = "book-history" if has_book_path else "research"
        basis = "workspace_path_without_primary_area"
        flags.append("missing_primary_area")
    else:
        stream, basis = "review", "insufficient_structured_metadata"
        flags.append("missing_or_unknown_primary_area")
    if stream == "review" and not areas and all(
        re.search(rf"^{field}:\s*\S", body, re.M)
        for field in ("MAJOR_RESULT_CLOSURE", "CONTROLLING_BLOCKER", "CLAIM_BOUNDARY", "EVIDENCE_HASHES")
    ):
        stream, basis = "research", "legacy_research_wave_fields"
        flags.clear()
    declarations = fields.get("stream", [])
    if declarations:
        declared = declarations[0].strip().strip("` ").lower()
        if len(declarations) != 1 or declared not in STREAMS or declared == "review":
            stream, basis = "review", "invalid_stream_declaration"
            flags.append("invalid_stream")
        elif declared != stream and not (stream == "review" and not areas):
            stream, basis = "review", "stream_area_conflict"
            flags.append("stream_area_conflict")
        else:
            stream, basis = declared, "explicit_stream_and_area" if areas else "explicit_stream"
    return {"stream": stream, "areas": areas, "related_streams": related,
            "basis": basis, "flags": flags}


def parse_source(path: str, raw: bytes) -> list[dict]:
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    headings = []
    fence = None
    anchors: Counter = Counter()
    for number, line in enumerate(lines, 1):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token[0]
            elif token[0] == fence:
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            title = match[2]
            base = slug(title)
            anchor = base + (f"-{anchors[base]}" if anchors[base] else "")
            anchors[base] += 1
            headings.append((number, len(match[1]), title, anchor))
    records = []
    for i, (start, level, title, anchor) in enumerate(headings):
        if level == 1:
            continue
        end = headings[i + 1][0] - 1 if i + 1 < len(headings) else len(lines)
        body = "".join(lines[start:end])
        if not body.strip():
            continue
        content = "".join(lines[start - 1:end])
        record = {"id": f"{path}#{anchor}", "source": path, "anchor": anchor,
                  "start_line": start, "end_line": end, "title": title,
                  "entry_sha256": digest(content.encode("utf-8")),
                  **classify(body, title)}
        record["date"] = Path(path).stem
        record["legacy_root_path"] = len(Path(path).parts) == 1
        records.append(record)
    if not records and raw.strip():
        title = headings[0][2] if headings else Path(path).stem
        records.append({"id": f"{path}#unsectioned-record", "source": path,
                        "anchor": "", "start_line": 1, "end_line": len(lines),
                        "title": title, "entry_sha256": digest(raw),
                        **classify("".join(lines)), "date": Path(path).stem,
                        "legacy_root_path": len(Path(path).parts) == 1})
        records[-1]["flags"].append("unsectioned_source")
    return records


def build(ledger: Path) -> dict:
    sources, records = [], []
    paths = sorted(
        (p for p in ledger.rglob("*.md") if DATE_FILE.fullmatch(p.name)),
        key=lambda p: (len(p.relative_to(ledger).parts) == 1, p.as_posix()),
    )
    if not paths:
        raise ValueError("No dated ledger sources found; refusing an empty coverage report")
    for path in paths:
        if not path.resolve().is_relative_to(ledger.resolve()):
            raise ValueError(f"Ledger source escapes workspace: {path.name}")
        relative = path.relative_to(ledger).as_posix()
        raw = path.read_bytes()
        if not raw.strip():
            raise ValueError(f"Empty dated ledger source: {relative}")
        entries = parse_source(relative, raw)
        sources.append({"path": relative, "sha256": digest(raw), "entries": len(entries)})
        records.extend(entries)
    # Identical entry payloads are retained, but never counted as separate work.
    seen = {}
    for record in records:
        fingerprint = record["entry_sha256"]
        if fingerprint in seen:
            record["duplicate_of"] = seen[fingerprint]
        else:
            seen[fingerprint] = record["id"]
    override_file = ledger / "CLASSIFICATION_OVERRIDES.json"
    overrides = json.loads(override_file.read_text(encoding="utf-8")) if override_file.exists() else {"schema_version": 1, "records": []}
    if overrides.get("schema_version") != 1:
        raise ValueError("Unsupported ledger override schema")
    by_id = {r["id"]: r for r in records}
    override_ids = set()
    for override in overrides["records"]:
        key = override["id"]
        if key in override_ids or override["stream"] not in STREAMS or not override.get("reason"):
            raise ValueError(f"Invalid or duplicate override: {key}")
        override_ids.add(key)
        record = by_id.get(key)
        if record is None:
            continue  # A historical override may refer to another source revision.
        if override["entry_sha256"] != record["entry_sha256"]:
            record["stream"] = "review"
            record["flags"].append("stale_classification_override")
            continue
        record["original_flags"] = record["flags"]
        record.update(stream=override["stream"], basis="hash_locked_metadata_review", flags=[],
                      classification_review=override["reason"])
    counts = Counter(r["stream"] for r in records)
    return {"schema_version": 1, "boundary_date": "2026-11-03",
            "scope": "daily ledger metadata only; not scientific validation or verified publication status",
            "summary": {"sources": len(sources), "entries": len(records),
                        "by_stream": dict(sorted(counts.items())),
                        "exact_duplicates": sum("duplicate_of" in r for r in records),
                        "review_entries": sum(bool(r["flags"]) for r in records)},
            "duplicate_dates": {day: [s["path"] for s in sources if Path(s["path"]).stem == day]
                                for day, count in Counter(Path(s["path"]).stem for s in sources).items()
                                if count > 1},
            "override_sha256": digest(override_file.read_bytes()) if override_file.exists() else None,
            "sources": sources, "records": records}


def outputs(index: dict) -> dict[str, str]:
    result = {"INDEX.json": json.dumps(index, ensure_ascii=False, indent=2) + "\n"}
    for stream, (filename, title) in STREAMS.items():
        selected = [r for r in index["records"] if r["stream"] == stream]
        if stream == "review":
            selected = [r for r in index["records"] if r["flags"]]
        selected.sort(key=lambda r: (r["date"], r["source"], r["start_line"]), reverse=True)
        lines = [f"# {title}", "", "<!-- Generated by build_work_ledger_index.py; do not edit. -->", "",
                 "[Ledger guide](README.md) | [Research](RESEARCH.md) | [Book history](BOOK_HISTORY.md) | "
                 "[Operations](OPERATIONS.md) | [Mixed](MIXED.md) | [Review](REVIEW.md)", "",
                 "These are source-linked historical records, not proof of completed research, "
                 "successful publication, or current scientific readiness.", ""]
        if stream == "book-history":
            lines += ["Book/theory work is historical here. The owner relocated that workspace out of "
                      "Harness. Do not access its destination, start new manuscript work, or count "
                      "these entries as research progress.", ""]
        if stream == "mixed":
            lines += ["Both domains occur in the primary metadata or workspace paths. These entries "
                      "are not silently included in either single-domain progress count.", ""]
        if stream == "review":
            lines += ["Review all flagged entries, including provisional path-based classifications. "
                      "Historical source text is not rewritten automatically.", ""]
            for day, paths in index["duplicate_dates"].items():
                lines += [f"Multiple source files for {day}: " + ", ".join(f"[{p}]({p})" for p in paths)
                          + ". Preserved separately; do not assume equal or delete either.", ""]
        lines += [f"Indexed entries: {len(selected)}. Counts describe records, not accomplishments.", "",
                  "| Date | Record | Area | Notes |", "| --- | --- | --- | --- |"]
        for record in selected:
            title_text = record["title"].replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
            link = record["source"] + (f"#{record['anchor']}" if record["anchor"] else "")
            notes = list(record["flags"])
            if record["legacy_root_path"]:
                notes.append("legacy root location")
            if "duplicate_of" in record:
                notes.append("exact duplicate; do not double-count")
            lines.append(f"| {record['date']} | [{title_text}]({link}) "
                         f"(L{record['start_line']}) | {', '.join(record['areas']) or 'unspecified'} | "
                         f"{'; '.join(notes) or record['basis']} |")
        result[filename] = "\n".join(lines) + "\n"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=REPO / "WORK_LEDGER")
    parser.add_argument("--check", action="store_true", help="Compare without writing any files")
    args = parser.parse_args()
    index = build(args.ledger)
    expected = outputs(index)
    mismatched = []
    for filename, content in expected.items():
        path = args.ledger / filename
        if args.check:
            if not path.exists() or path.read_bytes() != content.encode("utf-8"):
                mismatched.append(filename)
        else:
            path.write_bytes(content.encode("utf-8"))
    if mismatched:
        print("STALE ledger views: " + ", ".join(mismatched))
        return 1
    print(json.dumps(index["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
