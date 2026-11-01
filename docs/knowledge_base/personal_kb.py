"""Local research index. Only explicit ingest writes; evidence queries are read-only."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = REPO_ROOT / 'docs/knowledge_base/personal_index.sqlite3'
DEFAULT_PATHS = ('docs/UET_Documentation_Details', 'docs/topics/For Work',
                 'docs/topics/README.md', 'docs/meta', 'docs/core')
TEXT_EXTENSIONS = {'.md', '.txt', '.py', '.json', '.toml', '.yaml', '.yml'}
SKIP_PARTS = {'.git', '.venv', '__pycache__', 'node_modules', 'vectors', 'media',
              'target', 'dist', 'build', 'raw', '1_raw', 'ch_drafts', 'private', 'secrets',
              '.codex', '.agents', '.aws', '.ssh', '.publish-core-handoff'}
SCHEMA_VERSION = '3'

@dataclass(frozen=True)
class SourceFile:
    path: Path
    rel_path: str
    content: str
    file_hash: str

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def normalize_rel(path: Path):
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()

def safe_source(path: Path):
    rel = path.resolve().relative_to(REPO_ROOT.resolve())
    lowered = {p.lower() for p in rel.parts}
    name = path.name.lower()
    if lowered & SKIP_PARTS or name.startswith('.env') or name in {'config.toml', 'credentials.json'}:
        raise ValueError('Source is outside public research scope')
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError('Unsupported source type')
    return path.resolve()

def should_skip(path):
    try:
        safe_source(path)
        return False
    except ValueError:
        return True

def connect(db_path: Path, *, writable=False):
    db_path = Path(db_path).resolve()
    if writable:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
    else:
        if not db_path.is_file():
            raise FileNotFoundError('Index missing; use explicit ingest --rebuild on a new database')
        conn = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True)
        conn.execute('PRAGMA query_only=ON')
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
        if not row or row['value'] != SCHEMA_VERSION:
            raise ValueError('Legacy index: rebuild explicitly using ingest --rebuild; queries never migrate')
    except (sqlite3.Error, ValueError) as exc:
        conn.close()
        raise ValueError('Legacy index: rebuild explicitly using ingest --rebuild') from exc
    return conn

def init_db(conn):
    conn.executescript('''
        CREATE TABLE schema_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE documents(source_path TEXT PRIMARY KEY,file_hash TEXT NOT NULL,
            status TEXT NOT NULL,indexed_at TEXT NOT NULL,chunk_count INTEGER NOT NULL);
        CREATE TABLE chunks(source_path TEXT NOT NULL,chunk_index INTEGER NOT NULL,
            heading_path TEXT,text TEXT NOT NULL,chunk_hash TEXT NOT NULL,
            line_start INTEGER NOT NULL,line_end INTEGER NOT NULL,
            PRIMARY KEY(source_path,chunk_index));
        CREATE TABLE ingest_runs(id INTEGER PRIMARY KEY,mode TEXT,started_at TEXT,
            finished_at TEXT,scanned_files INTEGER,changed_files INTEGER,
            skipped_files INTEGER,deleted_files INTEGER,chunks_written INTEGER,dry_run INTEGER);
    ''')
    backend = 'fts5'
    try:
        conn.execute('CREATE VIRTUAL TABLE chunks_fts USING fts5(source_path UNINDEXED, chunk_index UNINDEXED, heading_path, text)')
    except sqlite3.OperationalError:
        backend = 'like'
        conn.execute('CREATE TABLE chunks_fts(source_path TEXT,chunk_index INTEGER,heading_path TEXT,text TEXT)')
    conn.executemany('INSERT INTO schema_meta VALUES (?,?)', [('schema_version', SCHEMA_VERSION), ('search_backend', backend)])
    conn.commit()

def iter_files(paths: Iterable[str]):
    seen = set()
    for item in paths:
        root = (REPO_ROOT / item).resolve()
        root.relative_to(REPO_ROOT.resolve())
        if not root.exists():
            continue
        if root.is_file():
            files = [root]
        else:
            files = []
            def scan_error(error):
                raise error
            for directory, dirs, names in os.walk(root, onerror=scan_error):
                dirs[:] = sorted(d for d in dirs if d.lower() not in SKIP_PARTS)
                files.extend(Path(directory) / name for name in sorted(names))
        for path in files:
            if path.is_file() and not should_skip(path) and path.resolve() not in seen:
                seen.add(path.resolve())
                yield path

def read_source(path):
    path = safe_source(path)
    raw = path.read_bytes()
    if b'\x00' in raw:
        raise ValueError('Binary source in text scope')
    return SourceFile(path, normalize_rel(path), raw.decode('utf-8'), hashlib.sha256(raw).hexdigest())

def chunk_records(text):
    lines = text.splitlines()
    if not lines:
        return []
    # Preserve the full line range; avoid splitting inside a fenced code block.
    records, stack, start, heading, fenced = [], [], 0, '', False
    def emit(end):
        body = '\n'.join(lines[start:end])
        if body.strip():
            records.append((heading, body, start + 1, end))
    for i, line in enumerate(lines):
        match = re.match(r'^(#{1,6})\s+(.+?)\s*$', line) if not fenced else None
        if match:
            if i > start:
                emit(i)
            start = i
            level = len(match[1])
            stack = stack[:level-1] + [match[2]]
            heading = ' > '.join(stack)
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
    emit(len(lines))
    return records

def chunk_markdownish(text):
    return [(h, t) for h, t, _, _ in chunk_records(text)]

def existing_hashes(conn):
    return {r['source_path']: r['file_hash'] for r in conn.execute("SELECT source_path,file_hash FROM documents WHERE status='active'")}

def clear_document(conn, rel_path):
    conn.execute('DELETE FROM chunks WHERE source_path=?', (rel_path,))
    conn.execute('DELETE FROM chunks_fts WHERE source_path=?', (rel_path,))

def upsert_source(conn, source):
    records = chunk_records(source.content)
    clear_document(conn, source.rel_path)
    for index, (heading, text, start, end) in enumerate(records):
        digest = hashlib.sha256(text.encode()).hexdigest()
        conn.execute('INSERT INTO chunks VALUES (?,?,?,?,?,?,?)', (source.rel_path,index,heading,text,digest,start,end))
        conn.execute('INSERT INTO chunks_fts VALUES (?,?,?,?)', (source.rel_path,index,heading,text))
    conn.execute('''INSERT INTO documents VALUES (?,?,'active',?,?)
        ON CONFLICT(source_path) DO UPDATE SET file_hash=excluded.file_hash,status='active',
        indexed_at=excluded.indexed_at,chunk_count=excluded.chunk_count''',
        (source.rel_path,source.file_hash,now_iso(),len(records)))
    return len(records)

def in_scope(rel_path, paths):
    source = (REPO_ROOT / rel_path).resolve()
    for item in paths:
        scope = (REPO_ROOT / item).resolve()
        scope.relative_to(REPO_ROOT.resolve())
        if source == scope or source.is_relative_to(scope):
            return True
    return False

def cmd_ingest(args):
    started = now_iso()
    # Complete the scan before opening a writer; any read error aborts the pass.
    sources = [read_source(path) for path in iter_files(args.paths)]
    if any(source is None for source in sources):
        raise ValueError('Scan error: unreadable source; index unchanged')
    rebuild = getattr(args, 'rebuild', False)
    if rebuild and args.db.exists():
        raise ValueError('Rebuild requires a NEW database path; preserve the existing index')
    conn = None
    try:
        if args.db.exists():
            conn = connect(args.db, writable=not args.dry_run)
            known = existing_hashes(conn)
        else:
            known = {}
        seen = {s.rel_path for s in sources}
        deleted = sorted(p for p in known if in_scope(p, args.paths) and p not in seen)
        changed = [s for s in sources if args.all or known.get(s.rel_path) != s.file_hash]
        written = 0
        if not args.dry_run:
            if conn is None:
                args.db.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(args.db)
                conn.row_factory = sqlite3.Row
                init_db(conn)
            with conn:
                for source in changed:
                    written += upsert_source(conn, source)
                for path in deleted:
                    conn.execute("UPDATE documents SET status='deleted',indexed_at=? WHERE source_path=?", (now_iso(), path))
                    clear_document(conn, path)
                conn.execute('INSERT INTO ingest_runs VALUES (NULL,?,?,?,?,?,?,?,?,?)',
                    ('all' if args.all else 'changed',started,now_iso(),len(sources),len(changed),
                     len(sources)-len(changed),len(deleted),written,0))
        print(json.dumps({'mode':'all' if args.all else 'changed','dry_run':args.dry_run,
            'scanned_files':len(sources),'changed_files':len(changed),'skipped_files':len(sources)-len(changed),
            'deleted_files':len(deleted),'chunks_written':written,'db':str(args.db)}, ensure_ascii=False))
    finally:
        if conn:
            conn.close()
    return 0

def cmd_status(args):
    conn = connect(args.db)
    try:
        counts = {r['status']:r['n'] for r in conn.execute('SELECT status,COUNT(*) n FROM documents GROUP BY status ORDER BY status')}
        last = conn.execute('SELECT * FROM ingest_runs ORDER BY id DESC LIMIT 1').fetchone()
        print(json.dumps({'db':str(args.db),'documents':counts,
            'chunks':conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0],
            'last_ingest_run':dict(last) if last else None}, ensure_ascii=False))
    finally:
        conn.close()
    return 0

def fetch_source(source_path, line_start, line_end, expected_hash):
    if not expected_hash or not re.fullmatch('[0-9a-f]{64}', expected_hash):
        raise ValueError('Expected SHA256 required')
    source = read_source(REPO_ROOT / source_path)
    if source.file_hash != expected_hash:
        raise ValueError('stale source: hash mismatch')
    lines = source.content.splitlines()
    if line_start < 1 or line_end < line_start or line_end > len(lines):
        raise ValueError('Invalid line range')
    return {'source_path':source.rel_path,'source_hash':source.file_hash,
            'line_start':line_start,'line_end':line_end,'text':'\n'.join(lines[line_start-1:line_end])}

def search_evidence(db, query, limit=8, snippet_chars=320, scope=()):
    if not query.strip() or limit < 1 or snippet_chars < 1:
        raise ValueError('Nonempty query and positive limits required')
    for item in scope:
        (REPO_ROOT / item).resolve().relative_to(REPO_ROOT.resolve())
    conn = connect(db)
    try:
        backend = conn.execute("SELECT value FROM schema_meta WHERE key='search_backend'").fetchone()[0]
        columns = 'c.*,d.file_hash AS source_hash'
        if backend == 'fts5':
            # MATCH errors are explicit: malformed syntax must not silently change semantics.
            rows = conn.execute(f'''SELECT {columns} FROM chunks_fts
                JOIN chunks c ON c.source_path=chunks_fts.source_path AND c.chunk_index=chunks_fts.chunk_index
                JOIN documents d ON d.source_path=c.source_path
                WHERE chunks_fts MATCH ? AND d.status='active'
                ORDER BY bm25(chunks_fts),c.source_path,c.chunk_index''', (query,))
        else:
            literal = query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            rows = conn.execute(f'''SELECT {columns} FROM chunks c JOIN documents d ON d.source_path=c.source_path
                WHERE c.text LIKE ? ESCAPE '\\' AND d.status='active'
                ORDER BY c.source_path,c.chunk_index''', ('%'+literal+'%',))
        evidence, diagnostics = [], []
        for row in rows:
            if scope and not in_scope(row['source_path'], scope):
                continue
            try:
                item = fetch_source(row['source_path'],row['line_start'],row['line_end'],row['source_hash'])
                if hashlib.sha256(item['text'].encode()).hexdigest() != row['chunk_hash']:
                    raise ValueError('stale chunk: hash mismatch')
            except (ValueError,OSError,UnicodeError):
                diagnostics.append({'source_path':row['source_path'],'status':'stale_or_unavailable'})
                continue
            item.update(heading_path=row['heading_path'],chunk_hash=row['chunk_hash'],
                snippet=' '.join(item['text'].split())[:snippet_chars],search_method=backend)
            evidence.append(item)
            if len(evidence) == limit:
                break
        return evidence, diagnostics
    finally:
        conn.close()

def cmd_search(args):
    rows, diagnostics = search_evidence(args.db,args.query,args.limit,args.snippet_chars,getattr(args,'scope',()))
    if getattr(args, 'packet', False):
        print(json.dumps({'schema_version':1,'question':args.query,'scope':list(getattr(args,'scope',())),
            'lane':getattr(args,'lane','unknown'),'controlling_blocker':getattr(args,'blocker','unknown'),
            'evidence':rows,'diagnostics':diagnostics},ensure_ascii=False))
    else:
        for row in rows:
            print(json.dumps(row,ensure_ascii=False))
        for diagnostic in diagnostics:
            print(json.dumps(diagnostic),file=sys.stderr)
    return 0

def cmd_fetch(args):
    print(json.dumps(fetch_source(args.source_path,args.line_start,args.line_end,args.expected_hash),ensure_ascii=False))
    return 0

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=DEFAULT_DB)
    sub = parser.add_subparsers(dest='command',required=True)
    ingest = sub.add_parser('ingest')
    ingest.add_argument('--all',action='store_true')
    ingest.add_argument('--dry-run',action='store_true')
    ingest.add_argument('--rebuild',action='store_true',help='Build schema 3 at a NEW database path')
    ingest.add_argument('paths',nargs='*',default=list(DEFAULT_PATHS))
    ingest.set_defaults(func=cmd_ingest)
    status = sub.add_parser('status'); status.set_defaults(func=cmd_status)
    search = sub.add_parser('search')
    search.add_argument('query'); search.add_argument('--limit',type=int,default=8)
    search.add_argument('--snippet-chars',type=int,default=320)
    search.add_argument('--packet',action='store_true'); search.add_argument('--scope',action='append',default=[])
    search.add_argument('--lane',default='unknown'); search.add_argument('--blocker',default='unknown')
    search.set_defaults(func=cmd_search)
    fetch = sub.add_parser('fetch')
    fetch.add_argument('source_path'); fetch.add_argument('--line-start',type=int,required=True)
    fetch.add_argument('--line-end',type=int,required=True); fetch.add_argument('--expected-hash',required=True)
    fetch.set_defaults(func=cmd_fetch)
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    args.db = args.db.resolve()
    try:
        return args.func(args)
    except (ValueError,OSError,sqlite3.Error,UnicodeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
