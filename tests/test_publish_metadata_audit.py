"""Safety tests for the non-live publish metadata fixture."""

from pathlib import Path
import importlib.util
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / 'tools/audit_publish_metadata.py'
SPEC = importlib.util.spec_from_file_location('audit_publish_metadata', TOOL)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class PublishMetadataAudit(unittest.TestCase):
    def test_comparison_reports_additions_without_calling_them_preserved(self):
        source = {'sha256': 'a', 'mode': '0o644', 'uid': 1, 'gid': 2,
                  'acl': [], 'xattrs': {'com.apple.quarantine': 'aa'}}
        candidate = dict(source, xattrs={
            'com.apple.quarantine': 'aa', 'com.apple.provenance': 'bb'})
        result = AUDIT.comparison(source, candidate)
        self.assertTrue(result['source_xattrs_preserved'])
        self.assertFalse(result['xattrs_equal'])
        self.assertEqual(result['added_xattrs'], ['com.apple.provenance'])

    def test_refuses_output_outside_work(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'index.json'
            source.write_text('{}', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(TOOL), '--source', str(source),
                 '--out', str(Path(folder) / 'audit')],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('work/', result.stderr)

    def test_refuses_existing_output(self):
        source = ROOT / 'engine/blueprint-provenance.json'
        out = ROOT / 'work/publish-metadata-existing-test'
        out.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [sys.executable, str(TOOL), '--source', str(source), '--out', str(out)],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
