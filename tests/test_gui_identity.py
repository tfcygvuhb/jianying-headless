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


if __name__ == '__main__':
    unittest.main()
