"""Offline contract checks for the GUI acceptance tool's schema adapter."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import gui_cycle as cycle


class GuiCycleSchemaTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.build = self.root / 'build'
        self.build.mkdir()
        self.target = self.root / 'Codex-Isolated-Edit'
        self.target.mkdir()
        self.record = {'schema': cycle.EDIT_SCHEMA, 'name': self.target.name,
                       'target': str(self.target), 'duration_us': 5_000_000}
        (self.build / 'expected-timeline.json').write_text(json.dumps({
            'tracks': [{'type': 'video'}, {'type': 'text'}, {'type': 'audio'}]}))
        self.report = {'status': 'verified', 'draft': str(self.target),
                       'duration_us': 5_000_000, 'tracks': 3,
                       'four_mirrors_equal': True, 'source_files_unchanged': True}

    def verify(self, report, record=None):
        with patch.object(cycle, 'command', return_value=json.dumps(report)) as called:
            result = cycle.verify(self.build, record or self.record)
        self.assertEqual(Path(called.call_args.args[0][1]).name, 'native_edit.py')
        return result

    def test_edit_report_is_bound_to_target_and_expected_track_count(self):
        self.assertEqual(self.verify(self.report)['name'], self.target.name)

    def test_edit_report_rejects_wrong_target(self):
        with self.assertRaisesRegex(ValueError, 'path differs'):
            self.verify(dict(self.report, draft=str(self.build)))

    def test_edit_report_rejects_wrong_track_count(self):
        with self.assertRaisesRegex(ValueError, 'track count differs'):
            self.verify(dict(self.report, tracks=2))

    def test_edit_report_rejects_changed_duration(self):
        with self.assertRaisesRegex(ValueError, 'duration differs'):
            self.verify(dict(self.report, duration_us=4_999_999))

    def test_headless_verifier_keeps_its_name_and_tracks(self):
        record = dict(self.record, schema=cycle.HEADLESS_SCHEMA)
        report = dict(self.report, name=self.target.name,
                      tracks=[{'type': 'video', 'segments': 1}])
        with patch.object(cycle, 'command', return_value=json.dumps(report)) as called:
            result = cycle.verify(self.build, record)
        self.assertEqual(Path(called.call_args.args[0][1]).name, 'jy14_headless.py')
        self.assertEqual(result['tracks'], report['tracks'])
        with patch.object(cycle, 'command', return_value=json.dumps(dict(report, name='wrong'))):
            with self.assertRaisesRegex(ValueError, 'name differs'):
                cycle.verify(self.build, record)

    def test_edit_source_manifest_detects_changes_and_symlinks(self):
        source = self.root / 'source'
        source.mkdir()
        (source / 'draft_info.json').write_text('original')
        media = self.target / 'media.mp4'
        media.write_bytes(b'media')
        record = dict(self.record, source=str(source),
                      source_files=cycle.source_manifest(source),
                      media_dependencies=[{'path': str(media), 'sha256': cycle.digest(media)}])
        before = cycle.source_snapshot(record, self.target)
        self.assertEqual(before['source_files'], record['source_files'])
        (source / 'draft_info.json').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source draft changed'):
            cycle.source_snapshot(record, self.target)
        (source / 'draft_info.json').write_text('original')
        (source / 'link').symlink_to(media)
        with self.assertRaisesRegex(ValueError, 'contains a symlink'):
            cycle.source_snapshot(record, self.target)

    def test_home_card_click_retries_once_only_after_exact_title_remains(self):
        clicked = []

        def command(argv, timeout=30):
            if argv[1] == 'click-card':
                clicked.append(argv)
                if len(clicked) == 1:
                    raise RuntimeError('editor state did not appear after exact associated card click')
            return ''

        with patch.object(cycle, 'command', side_effect=command), \
                patch.object(cycle, 'wait_ax') as wait, patch.object(cycle, 'main_pid', return_value=[123]):
            self.assertEqual(cycle.open_target(self.root / 'ax', self.target.name), 2)
        self.assertEqual(len(clicked), 2)
        self.assertEqual(wait.call_count, 3)
        self.assertEqual(wait.call_args.kwargs['seconds'], 5)

    def test_home_card_click_does_not_retry_unrelated_failure(self):
        clicked = []

        def command(argv, timeout=30):
            if argv[1] == 'click-card':
                clicked.append(argv)
                raise RuntimeError('unique title is not contained in the unique draft card AX frame')
            return ''

        with patch.object(cycle, 'command', side_effect=command), \
                patch.object(cycle, 'wait_ax'), patch.object(cycle, 'main_pid', return_value=[123]):
            with self.assertRaisesRegex(ValueError, 'exact associated card click failed'):
                cycle.open_target(self.root / 'ax', self.target.name)
        self.assertEqual(len(clicked), 1)


if __name__ == '__main__':
    unittest.main()
