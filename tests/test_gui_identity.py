"""Safety checks for the Build 481 editor identity gate."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
from jianying_identity_verifier import DRAFT_ROOT, evaluate


class EditorIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.name = 'Build481-Identity-Sample'
        self.target = str(Path(DRAFT_ROOT) / self.name)
        self.pid = 12345
        self.screenshot = self.folder / 'editor-window.png'
        self.screenshot.write_bytes(b'isolated editor screenshot fixture')
        self.ocr = self.folder / 'identity-evidence.json'
        self.items = [
            {'text': '草稿名称：', 'confidence': 1.0, 'x': .70, 'y': .80,
             'width': .07, 'height': .02},
            {'text': self.name, 'confidence': 1.0, 'x': .82, 'y': .80,
             'width': .16, 'height': .02},
        ]
        self.write_envelope()
        self.lsof = 'pid=12345\nlsof_exit=0\np12345\n' + '\n'.join([
            'n' + self.target + '/.locked',
            'n' + self.target + '/Resources/headless-media/clip.mp4',
        ]) + '\n'

    def write_envelope(self):
        self.ocr.write_text(json.dumps({
            'schema': 'build481-editor-identity-capture/v1',
            'status': 'captured', 'bundleID': 'com.lemon.lvpro',
            'pid': self.pid, 'cgWindowID': 777,
            'windowTitle': '剪映专业版',
            'screenshot': self.screenshot.name,
            'screenshotSHA256': hashlib.sha256(self.screenshot.read_bytes()).hexdigest(),
            'vision': {'items': self.items},
        }))

    def check(self, name=None, target=None, lsof=None):
        return evaluate(name or self.name, target or self.target, self.pid,
                        lsof or self.lsof, self.screenshot, self.ocr)

    def test_matching_window_and_open_draft_handles(self):
        self.assertEqual(self.check()['status'], 'verified')

    def test_wrong_requested_draft_is_rejected(self):
        other = 'Build481-Another-Draft'
        result = self.check(other, str(Path(DRAFT_ROOT) / other))
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('target-lock-not-unique', {r['code'] for r in result['reasons']})

    def test_foreign_open_draft_handle_is_rejected(self):
        other = Path(DRAFT_ROOT) / 'Build481-Another-Draft' / '.locked'
        result = self.check(lsof=self.lsof + 'n' + str(other) + '\n')
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('foreign-draft-handles', {r['code'] for r in result['reasons']})

    def test_screenshot_mutation_is_rejected(self):
        self.screenshot.write_bytes(b'changed screenshot')
        result = self.check()
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('screenshot-hash-mismatch', {r['code'] for r in result['reasons']})

    def wrapped_name(self):
        self.items = [
            {'text': '草稿名称：', 'confidence': 1.0, 'x': .70, 'y': .80,
             'width': .07, 'height': .02},
            {'text': 'Build481-', 'confidence': 1.0, 'x': .82, 'y': .80,
             'width': .08, 'height': .02},
            {'text': 'Identity-Sample', 'confidence': 1.0, 'x': .82, 'y': .775,
             'width': .14, 'height': .02},
            {'text': '保存位置：', 'confidence': 1.0, 'x': .70, 'y': .70,
             'width': .07, 'height': .02},
        ]
        self.write_envelope()

    def test_wrapped_name_is_exactly_bound_to_the_label(self):
        self.wrapped_name()
        self.assertEqual(self.check()['status'], 'verified')
        self.assertEqual(self.check(lsof=self.lsof + 'n' + str(Path(DRAFT_ROOT) / 'other/.locked') + '\n')['status'],
                         'rejected')

    def test_wrapped_name_rejects_wrong_text_low_confidence_and_wrong_column(self):
        self.wrapped_name()
        for changes in ({'text': 'Identity-SamplE'}, {'confidence': .5}, {'x': .89},
                        {'y': .71}, {'text': 'Identity- Sample'}):
            self.items[2] = dict(self.items[2], **changes)
            self.write_envelope()
            self.assertEqual(self.check()['status'], 'rejected', changes)
            self.wrapped_name()

    def test_wrapped_name_cannot_skip_intervening_text_or_duplicate_label(self):
        self.wrapped_name()
        self.items.insert(2, {'text': 'other', 'confidence': 1.0, 'x': .82, 'y': .781,
                              'width': .08, 'height': .02})
        self.write_envelope()
        self.assertEqual(self.check()['status'], 'rejected')
        self.wrapped_name()
        self.items.append(dict(self.items[0]))
        self.write_envelope()
        self.assertIn('draft-name-label-not-unique', {r['code'] for r in self.check()['reasons']})

    def test_name_elsewhere_cannot_replace_the_labeled_value(self):
        self.wrapped_name()
        self.items[1]['text'] = 'wrong'
        self.items.append({'text': self.name, 'confidence': 1.0, 'x': .45, 'y': .95,
                           'width': .2, 'height': .02})
        self.write_envelope()
        self.assertEqual(self.check()['status'], 'rejected')


if __name__ == '__main__':
    unittest.main()
