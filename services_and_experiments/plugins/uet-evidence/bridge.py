"""Private subprocess bridge to the repository's canonical read-only KB functions."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ALLOWED_INDEX_PATHS = {
    "docs/knowledge_base/personal_index.sqlite3",
    "tmp/research-foundation-pilot/after-corpus.sqlite3",
}


def emit(value, root=None, ok=True):
    if root and isinstance(value, str):
        value = value.replace(str(root), "[repository]")
    envelope = {"ok": True, "value": value} if ok else {"ok": False, "error": str(value)}
    print(json.dumps(envelope, ensure_ascii=False, separators=(",", ":")))


def main():
    root = None
    try:
        request = json.loads(sys.stdin.read())
        # strict=True raises WinError 5 in some sandboxed desktop environments;
        # the Node host already checked that the configured repository exists.
        root = Path(request["repository_root"]).resolve()
        kb_dir = root / "docs" / "knowledge_base"
        sys.path.insert(0, str(kb_dir))
        import personal_kb  # loaded from the configured repository, not from the plugin package

        index_path = request.get("index_path", "docs/knowledge_base/personal_index.sqlite3")
        if index_path not in ALLOWED_INDEX_PATHS:
            raise ValueError("Unsupported local evidence index path")
        db_path = root / Path(index_path)
        operation = request.get("operation")
        if operation == "probe":
            db = personal_kb.connect(db_path)
            try:
                backend = db.execute("SELECT value FROM schema_meta WHERE key='search_backend'").fetchone()[0]
                if backend == "fts5":
                    db.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH ?", ("uet_plugin_probe_no_match",)).fetchone()
                elif backend != "like":
                    raise ValueError("Evidence index has an unknown search backend")
            finally:
                db.close()
            emit({"index_schema": personal_kb.SCHEMA_VERSION, "search_backend": backend})
            return 0

        if operation == "search":
            query = request["query"]
            limit = request.get("limit", 6)
            snippet_chars = request.get("snippet_chars", 360)
            scope = request.get("scope", [])
            db = personal_kb.connect(db_path)
            try:
                backend = db.execute("SELECT value FROM schema_meta WHERE key='search_backend'").fetchone()[0]
            finally:
                db.close()
            rows, diagnostics = personal_kb.search_evidence(db_path, query, limit, snippet_chars, scope)
            evidence = []
            for row in rows:
                evidence.append({
                    "source_path": row["source_path"],
                    "source_hash": row["source_hash"],
                    "chunk_hash": row["chunk_hash"],
                    "heading_path": row["heading_path"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "locator": f"{row['source_path']}#L{row['line_start']}-L{row['line_end']}",
                    "snippet": row["snippet"],
                    "search_method": "bm25_fts5" if row["search_method"] == "fts5" else "literal_like",
                })
            emit({
                "schema_version": 1,
                "question": query,
                "scope": scope,
                "lane": "unknown",
                "controlling_blocker": "unknown",
                "search_method": "bm25_fts5" if backend == "fts5" else "literal_like",
                "evidence": evidence,
                "diagnostics": diagnostics,
                "next_step": "Use fetch_source on selected locators before relying on a claim." if evidence else "No current evidence matched this query.",
            })
            return 0

        if operation == "fetch":
            line_start = request["line_start"]
            line_end = request["line_end"]
            if not isinstance(line_start, int) or not isinstance(line_end, int):
                raise ValueError("Line numbers must be integers")
            if line_end < line_start or line_end - line_start + 1 > 250:
                raise ValueError("Fetch at most 250 lines at a time to keep evidence packets focused")
            result = personal_kb.fetch_source(
                request["source_path"], line_start, line_end, request["expected_hash"]
            )
            if len(result["text"].encode("utf-8")) > 18000:
                raise ValueError("Fetched text exceeds 18000 bytes. Request a smaller line range")
            expected_chunk_hash = request.get("expected_chunk_hash")
            if expected_chunk_hash:
                actual = hashlib.sha256(result["text"].encode("utf-8")).hexdigest()
                if actual != expected_chunk_hash:
                    raise ValueError("stale chunk: hash mismatch; rerun search and fetch its exact line range")
            result["locator"] = f"{result['source_path']}#L{line_start}-L{line_end}"
            emit(result)
            return 0

        raise ValueError("Unknown bridge operation")
    except Exception as exc:
        message = str(exc)
        emit(message[:1000], root=root, ok=False)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
