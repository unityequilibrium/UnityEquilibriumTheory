"""Regression coverage for ledger separation; uses temporary source fixtures only."""

import contextlib
import io
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "work_ledger_index_under_test", Path(__file__).with_name("build_work_ledger_index.py")
)
ledger_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger_index)


class ClassificationTests(unittest.TestCase):
    def test_book_research_is_not_topic_research(self):
        record = ledger_index.classify('- Area: book-writing (secondary: research-standards)\n'
                                      '- Workspace: uet_history/3_publish/books/biology\n')
        self.assertEqual(record['stream'], 'book-history')
        self.assertIn('research', record['related_streams'])

    def test_unrelated_prose_does_not_change_domain(self):
        record = ledger_index.classify('- Area: research-core\n'
                                      '- Next: unrelated book-writing work is not included\n')
        self.assertEqual(record['stream'], 'research')
        self.assertEqual(record['areas'], ['research-core'])

    def test_secondary_books_do_not_turn_ops_into_book_work(self):
        record = ledger_index.classify('- Area: repo-ops; secondary: theory-history, book-writing\n')
        self.assertEqual(record['stream'], 'operations')

    def test_mixed_primary_is_not_silently_research(self):
        self.assertEqual(ledger_index.classify('Area: research-core / book-writing')['stream'], 'mixed')

    def test_path_fallback_stays_flagged(self):
        record = ledger_index.classify('Workspace: docs/topics/0.13_Thermodynamic_Bridge')
        self.assertEqual(record['stream'], 'research')
        self.assertIn('missing_primary_area', record['flags'])

    def test_legacy_area_and_explicit_heading_area(self):
        self.assertEqual(ledger_index.classify('- Area `research-core`; formal audit')['stream'], 'research')
        self.assertEqual(ledger_index.classify('- **Area:** `book-writing`')['stream'], 'book-history')
        self.assertEqual(ledger_index.classify('Workspace: Core', 'research-standards / audit')['stream'], 'research')

    def test_conflicting_explicit_stream_needs_review(self):
        record = ledger_index.classify('Stream: research\nArea: book-writing')
        self.assertEqual(record['stream'], 'review')
        self.assertIn('stream_area_conflict', record['flags'])

    def test_unknown_and_multiple_area_fields_are_visible(self):
        self.assertEqual(ledger_index.classify('Area: unknown')['stream'], 'review')
        self.assertIn('multiple_area_fields', ledger_index.classify('Area: research-core\nArea: repo-ops')['flags'])

    def test_fenced_example_metadata_is_not_work(self):
        self.assertEqual(ledger_index.classify('```md\nArea: book-writing\n```\nArea: research-core')['stream'], 'research')

    def test_legacy_wave_requires_all_structured_fields(self):
        body = '\n'.join(f'{f}: recorded' for f in ['MAJOR_RESULT_CLOSURE', 'CONTROLLING_BLOCKER', 'CLAIM_BOUNDARY', 'EVIDENCE_HASHES'])
        self.assertEqual(ledger_index.classify(body)['stream'], 'research')
        self.assertEqual(ledger_index.classify('MAJOR_RESULT_CLOSURE: recorded')['stream'], 'review')
        self.assertEqual(ledger_index.classify('```text\n' + body + '\n```')['stream'], 'review')

    def test_embedded_wave_area_is_metadata_not_narrative(self):
        self.assertEqual(ledger_index.classify('MAJOR_RESULT_CLOSURE: named lane. Area research-core; secondary result-artifacts.')['stream'], 'research')
        self.assertEqual(ledger_index.classify('MAJOR_RESULT_CLOSURE: planning. Area repo-ops; secondary research-standards.')['stream'], 'operations')
        self.assertEqual(ledger_index.classify('Next: go to Area research-core')['stream'], 'review')
        self.assertEqual(ledger_index.classify('Area research-core; secondary result-artifacts.')['stream'], 'research')
        self.assertEqual(ledger_index.classify('MAJOR_RESULT_CLOSURE: one lane\nCLOSED_FOR_LANE. Area research-core; secondary result-artifacts.\n\nNext action: review')['stream'], 'research')
        self.assertEqual(ledger_index.classify('```text\nMAJOR_RESULT_CLOSURE: example. Area book-writing\n```')['stream'], 'review')


class SourceTests(unittest.TestCase):
    def test_empty_coverage_is_not_success(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder)
            with self.assertRaises(ValueError):
                ledger_index.build(root)
            (root / '2026-11-03.md').write_bytes(b'')
            with self.assertRaises(ValueError):
                ledger_index.build(root)

    def test_crlf_source_entry_hash_preserves_original_bytes(self):
        raw = b'# Day\r\n## One\r\nArea: research-core\r\n'
        record = ledger_index.parse_source('2026/2026-11-03.md', raw)[0]
        self.assertEqual(record['entry_sha256'], ledger_index.digest(raw.split(b'\r\n', 1)[1]))

    def test_nested_sections_fences_duplicate_headings_and_lines(self):
        raw = ('# Day\n\n## Repeat\nArea: research-core\n```md\n## Not a section\n```\n'
               '### Nested\nArea: book-writing\n## Repeat\nArea: repo-ops\n').encode()
        records = ledger_index.parse_source('2026/2026-11-03.md', raw)
        self.assertEqual([r['stream'] for r in records], ['research', 'book-history', 'operations'])
        self.assertEqual([r['start_line'] for r in records], [3, 8, 10])
        self.assertEqual([r['anchor'] for r in records], ['repeat', 'nested', 'repeat-1'])
        self.assertEqual(records[0]['end_line'], 7)

    def test_unsectioned_source_is_not_dropped(self):
        self.assertEqual(len(ledger_index.parse_source('2026-11-03.md', b'Area: research-core\n')), 1)

    def test_build_preserves_sources_and_marks_exact_duplicates(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder)
            (root / '2026').mkdir()
            raw = b'# Day\n## One\nArea: research-core\n'
            (root / '2026/2026-11-03.md').write_bytes(raw)
            (root / '2026-11-03.md').write_bytes(raw)
            (root / 'TEMPLATE.md').write_text('## Not work\nArea: book-writing\n')
            index = ledger_index.build(root)
            self.assertEqual(index['summary']['sources'], 2)
            self.assertEqual(index['summary']['exact_duplicates'], 1)
            self.assertIn('duplicate_of', index['records'][1])
            self.assertEqual(index['sources'][0]['sha256'], ledger_index.digest(raw))
            self.assertIn('2026-11-03', index['duplicate_dates'])
            self.assertEqual((root / '2026-11-03.md').read_bytes(), raw)
            self.assertEqual(ledger_index.outputs(index), ledger_index.outputs(ledger_index.build(root)))

    def test_check_is_read_only_and_fails_on_stale_output(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder)
            (root / '2026-11-03.md').write_text('# Day\n## One\nArea: research-core\n')
            with patch.object(sys, 'argv', ['index', '--ledger', folder]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ledger_index.main(), 0)
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            with patch.object(sys, 'argv', ['index', '--ledger', folder, '--check']), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ledger_index.main(), 0)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})
            (root / 'RESEARCH.md').write_text('stale')
            with patch.object(sys, 'argv', ['index', '--ledger', folder, '--check']), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ledger_index.main(), 1)
            self.assertEqual((root / 'RESEARCH.md').read_text(), 'stale')
            (root / '2026-11-04.md').write_text('# Day\n## New\nArea: book-writing\n')
            with patch.object(sys, 'argv', ['index', '--ledger', folder, '--check']), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ledger_index.main(), 1)

    def test_override_rejects_changed_source_and_duplicate_decisions(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            root = Path(folder)
            source = root / '2026-11-03.md'
            source.write_text('# Day\n## One\nUnknown historical entry\n')
            record = ledger_index.build(root)['records'][0]
            override = {'id': record['id'], 'entry_sha256': record['entry_sha256'],
                        'stream': 'operations', 'reason': 'Reviewed source metadata'}
            path = root / 'CLASSIFICATION_OVERRIDES.json'
            path.write_text(json.dumps({'schema_version': 1, 'records': [override]}))
            self.assertEqual(ledger_index.build(root)['records'][0]['stream'], 'operations')
            source.write_text('# Day\n## One\nChanged source\n')
            record = ledger_index.build(root)['records'][0]
            self.assertEqual(record['stream'], 'review')
            self.assertIn('stale_classification_override', record['flags'])
            override['additional_reviewed_sha256'] = [record['entry_sha256']]
            path.write_text(json.dumps({'schema_version': 1, 'records': [override]}))
            self.assertEqual(ledger_index.build(root)['records'][0]['stream'], 'operations')
            source.write_text('# Day\n## One\nAnother unreviewed change\n')
            self.assertEqual(ledger_index.build(root)['records'][0]['stream'], 'review')
            path.write_text(json.dumps({'schema_version': 1, 'records': [override, override]}))
            with self.assertRaises(ValueError):
                ledger_index.build(root)


if __name__ == '__main__':
    unittest.main()
