"""
Bulk-ingest research documentation into the UET Semantic Engine.

Usage:
    python -m uet_agents.ingest_docs          # via running api_server
    python uet_agents/ingest_docs.py --direct # direct (no server needed)
"""

import argparse
import json
import sys
from pathlib import Path

# Docs directories to ingest (relative to repo root)
DOCS_DIRS = [
    "docs/Docs",
    "docs/Doc",
]

EXTENSIONS = {".md", ".txt", ".rst"}


def collect_docs(repo_root: Path) -> list[dict]:
    """Walk doc directories and collect all text files."""
    docs = []
    for docs_dir in DOCS_DIRS:
        base = repo_root / docs_dir
        if not base.exists():
            print(f"  Skipping {docs_dir} (not found)")
            continue
        for fpath in sorted(base.rglob("*")):
            if fpath.suffix.lower() in EXTENSIONS and fpath.stat().st_size > 100:
                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                    doc_id = str(fpath.relative_to(repo_root)).replace("\\", "/")
                    docs.append({
                        "doc_id": doc_id,
                        "text": text,
                        "source_type": "documentation",
                        "tags": [fpath.parent.name, fpath.suffix.lstrip(".")],
                    })
                except Exception as e:
                    print(f"  Error reading {fpath}: {e}")
    return docs


def ingest_via_api(docs: list[dict], base_url: str = "http://localhost:8001"):
    """Ingest docs by calling the running API server."""
    import requests

    for i, doc in enumerate(docs, 1):
        try:
            r = requests.post(
                f"{base_url}/ingest",
                json={
                    "doc_id": doc["doc_id"],
                    "text": doc["text"],
                    "source_type": doc["source_type"],
                    "tags": doc["tags"],
                    "ingest_mode": "bulk",
                },
                timeout=30,
            )
            r.raise_for_status()
            print(f"  [{i}/{len(docs)}] {doc['doc_id']} ({len(doc['text'])} chars)")
        except Exception as e:
            print(f"  [{i}/{len(docs)}] FAILED {doc['doc_id']}: {e}")


def ingest_direct(docs: list[dict]):
    """Ingest docs directly into semantic engine (no server needed)."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from uet_agents.semantic_engine import UETSemanticEngine

    engine = UETSemanticEngine()
    print(f"  Before: {len(engine.knowledge_chunks)} chunks, {len(engine.vocab)} vocab")

    for i, doc in enumerate(docs, 1):
        chunks_added = engine.ingest_document(
            doc_id=doc["doc_id"],
            text=doc["text"],
            source_type=doc["source_type"],
            tags=doc["tags"],
            ingest_mode="bulk",
        )
        print(f"  [{i}/{len(docs)}] {doc['doc_id']} → +{chunks_added} chunks")

    print(f"  After: {len(engine.knowledge_chunks)} chunks, {len(engine.vocab)} vocab")
    print(f"  State saved to {engine.state_file}")


def main():
    parser = argparse.ArgumentParser(description="Ingest UET docs into Semantic Engine")
    parser.add_argument("--direct", action="store_true", help="Ingest directly (no API server)")
    parser.add_argument("--url", default="http://localhost:8001", help="API server URL")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    print(f"Collecting docs from {repo_root}...")
    docs = collect_docs(repo_root)
    print(f"Found {len(docs)} documents ({sum(len(d['text']) for d in docs):,} chars total)")

    if not docs:
        print("No documents found. Check DOCS_DIRS paths.")
        return

    if args.direct:
        print("Ingesting directly into semantic engine...")
        ingest_direct(docs)
    else:
        print(f"Ingesting via API at {args.url}...")
        ingest_via_api(docs, args.url)

    print("Done!")


if __name__ == "__main__":
    main()
