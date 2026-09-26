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
LIVE_SPEC = importlib.util.spec_from_file_location(
    'audit_publish_live_staging', ROOT / 'tools/audit_publish_live_staging.py')
LIVE_AUDIT = importlib.util.module_from_spec(LIVE_SPEC)
LIVE_SPEC.loader.exec_module(LIVE_AUDIT)


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
            source = ROOT / 'engine/blueprint-provenance.json'
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

    def test_refuses_symlinked_source_before_resolving_it(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'target.json'
            source = Path(folder) / 'source.json'
            target.write_text('{}', encoding='utf-8')
            source.symlink_to(target)
            result = subprocess.run(
                [sys.executable, str(TOOL), '--source', str(source),
                 '--out', str(ROOT / 'work/publish-metadata-symlink-test')],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('symlinked', result.stderr)

    def test_refuses_unbounded_run_count(self):
        source = ROOT / 'engine/blueprint-provenance.json'
        result = subprocess.run(
            [sys.executable, str(TOOL), '--source', str(source),
             '--out', str(ROOT / 'work/publish-metadata-runs-test'), '--runs', '11'],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--runs', result.stderr)

    def test_live_verdict_accepts_provenance_and_rejects_other_differences(self):
        exact = {'bytes_equal': True, 'mode_equal': True, 'owner_group_equal': True,
                 'acl_equal': True, 'xattrs_equal': True, 'xattr_changed_names': []}
        provenance = dict(exact, xattrs_equal=False,
                          xattr_changed_names=['com.apple.provenance'])
        bad_mode = dict(exact, mode_equal=False)
        bad_acl = dict(exact, acl_equal=False)
        source = {'sha256': 'a'}
        # Provenance-only differences are now acceptable
        self.assertTrue(LIVE_AUDIT.verdict(
            source, [{'comparison': exact}, {'comparison': exact}])['all_exact'])
        result = LIVE_AUDIT.verdict(
            source, [{'comparison': exact}, {'comparison': provenance}])
        self.assertTrue(result['all_exact'])
        self.assertEqual(result['exact_runs'], 2)
        # Non-provenance differences still fail
        for bad in (bad_mode, bad_acl):
            result = LIVE_AUDIT.verdict(
                source, [{'comparison': exact}, {'comparison': bad}])
            self.assertFalse(result['all_exact'])


if __name__ == '__main__':
    unittest.main()
