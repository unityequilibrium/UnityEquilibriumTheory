"""24 acceptance cases, executable against the frozen legacy module as well."""
import argparse
import hashlib
import importlib.util
import json
import os
import sqlite3
import sys

import pytest

from docs.knowledge_base import personal_kb as current


@pytest.fixture
def kb(tmp_path, monkeypatch):
    module = current
    legacy = os.environ.get('UET_KB_BASELINE_MODULE')
    if legacy:
        spec = importlib.util.spec_from_file_location('pilot_legacy_kb', legacy)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'REPO_ROOT', tmp_path)
    for name, text in {
        'a/README.md': '# Topic\nInternal benchmark only.\nNo external validation.\n',
        'a/METHOD.md': '# Method\nalpha baseline threshold\n',
        'b/LIMITATIONS.md': '# Limits\nalpha counterevidence unresolved\n',
        'b/ไทย.md': '# นิยาม\r\nหน่วย SI ต้องระบุ\r\nสมมติฐานยังเปิด\r\n',
    }.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode())
    db = tmp_path / 'index.sqlite3'
    module.cmd_ingest(argparse.Namespace(db=db, paths=['a', 'b'], all=False, dry_run=False))
    return module, tmp_path, db


def search(kb, capsys, query='alpha', packet=False):
    module, root, db = kb
    capsys.readouterr()
    module.cmd_search(argparse.Namespace(db=db, query=query, limit=8, snippet_chars=320,
        packet=packet, scope=['a', 'b'], lane='unknown', blocker='unknown'))
    lines = capsys.readouterr().out.splitlines()
    return [json.loads(line) for line in lines if line]


@pytest.mark.parametrize('case', range(8))
def test_retrieval(kb, capsys, case):
    module, root, db = kb
    queries = ['alpha', 'threshold', 'counterevidence', 'benchmark', 'validation', 'SI', 'missingterm', 'alpha']
    rows = search(kb, capsys, queries[case])
    if case == 6:
        assert rows == []
    elif case == 7:
        assert rows == search(kb, capsys, 'alpha')
    else:
        assert rows
        assert all((root / row['source_path']).exists() for row in rows)


@pytest.mark.parametrize('case', range(8))
def test_freshness_scope(kb, capsys, monkeypatch, case):
    module, root, db = kb
    args = argparse.Namespace(db=db, paths=['a'], all=False, dry_run=False)
    if case in (0, 1):
        target = root / 'a/METHOD.md'
        target.unlink() if case == 0 else target.write_text('changed', encoding='utf-8')
        assert not any(r['source_path'] == 'a/METHOD.md' for r in search(kb, capsys))
    elif case == 2:
        module.cmd_ingest(args)
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT status FROM documents WHERE source_path='b/LIMITATIONS.md'").fetchone()[0] == 'active'
    elif case in (3, 4):
        before = db.read_bytes()
        if case == 3:
            search(kb, capsys)
            module.cmd_status(argparse.Namespace(db=db))
        else:
            args.dry_run = True
            module.cmd_ingest(args)
        assert db.read_bytes() == before
    elif case == 5:
        missing = root / 'absent' / 'new.sqlite3'
        with pytest.raises((ValueError, sqlite3.Error, FileNotFoundError)):
            module.cmd_status(argparse.Namespace(db=missing))
        assert not missing.exists()
    elif case == 6:
        before = db.read_bytes()
        original = module.read_source
        def unreadable(path):
            if path.name == 'METHOD.md':
                raise OSError('simulated scan error')
            return original(path)
        monkeypatch.setattr(module, 'read_source', unreadable)
        with pytest.raises((ValueError, OSError)):
            module.cmd_ingest(args)
        assert db.read_bytes() == before
    else:
        old = root / 'old.sqlite3'
        with sqlite3.connect(old) as conn:
            conn.execute('CREATE TABLE legacy(x)')
        before = old.read_bytes()
        with pytest.raises((ValueError, sqlite3.Error)):
            module.cmd_status(argparse.Namespace(db=old))
        assert old.read_bytes() == before


@pytest.mark.parametrize('case', range(8))
def test_citation_boundary(kb, capsys, case):
    module, root, db = kb
    if case == 0:
        rows = search(kb, capsys)
        assert all(r['source_hash'] == hashlib.sha256((root/r['source_path']).read_bytes()).hexdigest() for r in rows)
    elif case == 1:
        rows = search(kb, capsys)
        for row in rows:
            text = '\n'.join((root/row['source_path']).read_text(encoding='utf-8').splitlines()[row['line_start']-1:row['line_end']])
            assert row['chunk_hash'] == hashlib.sha256(text.encode()).hexdigest()
    elif case == 2:
        path = root / 'b/ไทย.md'
        result = module.fetch_source('b/ไทย.md', 2, 3, hashlib.sha256(path.read_bytes()).hexdigest())
        assert result['text'] == 'หน่วย SI ต้องระบุ\nสมมติฐานยังเปิด'
    elif case in (3, 4, 5):
        path = ['../outside.md', 'raw/private.md', '.env'][case-3]
        with pytest.raises((ValueError, FileNotFoundError)):
            module.fetch_source(path, 1, 2, '0'*64)
    elif case == 6:
        with pytest.raises(ValueError, match='stale'):
            module.fetch_source('a/README.md', 1, 2, '0'*64)
    else:
        packet = search(kb, capsys, 'benchmark', packet=True)[0]
        assert packet['lane'] == 'unknown' and packet['controlling_blocker'] == 'unknown'
        assert packet['schema_version'] == 1
        assert 'Internal benchmark only.' in packet['evidence'][0]['text']
        assert 'No external validation.' in packet['evidence'][0]['text']
