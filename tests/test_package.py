"""Portable packaging/IO checks; fixtures are retained under project work/."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'engine'), str(ROOT / 'bridge')]
import native_resources as resources
import runtime_io as io

WORK = ROOT / 'work/package-tests'
WORK.mkdir(parents=True, exist_ok=True)
ENTRY = ROOT / 'skills/yichen-jianying-edit/scripts/headless_draft.py'


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix='case-', dir=WORK))

    def cli(self, entry=ENTRY, **environment):
        env = dict(os.environ)
        env.pop('JIANYING_HEADLESS_ROOT', None)
        env.update(environment)
        return subprocess.run([sys.executable, str(entry), '--help'], env=env,
                              cwd=self.folder, capture_output=True, text=True, timeout=30)

    def test_project_checkout_is_discovered_outside_current_directory(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('verify-build', result.stdout)

    def test_standalone_skill_with_configured_checkout_works(self):
        entry = self.folder / 'standalone.py'
        shutil.copyfile(ENTRY, entry)
        result = self.cli(entry, JIANYING_HEADLESS_ROOT=str(ROOT))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_configured_checkout_fails_before_output(self):
        result = self.cli(JIANYING_HEADLESS_ROOT=str(self.folder / 'missing'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('checkout unavailable', result.stderr)
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_relative_checkout_is_rejected(self):
        result = self.cli(JIANYING_HEADLESS_ROOT='relative-checkout')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('absolute checkout path', result.stderr)

    def test_changed_engine_is_rejected_before_loading(self):
        shutil.copyfile(ROOT / 'project.json', self.folder / 'project.json')
        engine = self.folder / 'engine'
        engine.mkdir()
        (engine / 'jy14_headless.py').write_text('raise AssertionError("must not run")\n')
        result = self.cli(JIANYING_HEADLESS_ROOT=str(self.folder))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Headless component changed', result.stderr)
        self.assertNotIn('AssertionError', result.stderr)

    def test_strict_json_rejects_duplicate_nonfinite_and_nonobject(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'[]', b'{"x":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(io.ApplyError):
                io._parse_strict_json(raw, 'fixture')
        self.assertEqual(io._parse_strict_json(b'{"x":2}', 'fixture'), {'x': 2})

    def test_snapshot_detects_same_length_changed_bytes(self):
        path = self.folder / 'snapshot.json'
        path.write_bytes(b'{"x":1}')
        snapshot = io._snapshot_file(path, 'fixture')
        io._revalidate_snapshot(snapshot, 'unchanged')
        path.write_bytes(b'{"x":2}')
        with self.assertRaises(io.ApplyError):
            io._revalidate_snapshot(snapshot, 'changed')

    def test_snapshot_rejects_symlink(self):
        original = self.folder / 'original'
        original.write_bytes(b'original')
        link = self.folder / 'link'
        link.symlink_to(original)
        with self.assertRaises(io.ApplyError):
            io._snapshot_file(link, 'fixture')

    def test_search_only_directory_traversal_rejects_symlink_component(self):
        real = self.folder / 'real'
        real.mkdir()
        link = self.folder / 'link'
        link.symlink_to(real, target_is_directory=True)
        descriptor = io._open_directory_secure(real, 'real directory')
        os.close(descriptor)
        with self.assertRaises(io.ApplyError):
            io._open_directory_secure(link, 'symlinked directory')
        if sys.platform == 'darwin' and hasattr(os, 'O_SEARCH'):
            self.assertEqual(io._directory_open_flags() & os.O_SEARCH, os.O_SEARCH)

    def test_catalog_relocates_paths_without_changing_resource_identity(self):
        original = json.loads((ROOT / 'engine/native-resource-catalog.json').read_bytes())
        with patch.object(resources.Path, 'home', return_value=self.folder):
            relocated = resources.catalog()
        for key, entry in relocated['resources'].items():
            prior = original['resources'][key]
            self.assertTrue(entry['source'].startswith(str(self.folder) + '/'))
            for field in ('files', 'tree_sha256', 'usage'):
                self.assertEqual(entry.get(field), prior.get(field))

    def test_1142_geometric_mask_manifests_match_captured_identities(self):
        expected = {
            'circle': '755f487494e041e0adceaff3c1a747b1238773c071fe3297d1911112cccd3946',
            'rectangle': 'c8d500f2840e387e372744f6f44e1d2128e29c94df3dc482cf18a8de7d2f0ec6',
            'line': 'e548c277fb2a6e06739855160a985a676221b19e9c4a65b60c8d75df1aea3c29',
            'mirror': '36365677e9ef362fdba0a5a9169cd9427c85f3ebecfc16f98c7d17a21bef3977',
            'star': 'ba3fd7ebd571eba4f3383343eb7b8f6f504dfef8d6477af3bbe49bd8c67f2a8e',
            'heart': 'd72134d8c23f46d9d2ca3b2d7171908285487f2a1cb69cdb57593d427e422936',
        }
        catalog = resources.catalog()
        self.assertEqual(catalog['runtime_profile'], 'jy14-headless-macos-11.4.2')
        for shape, fingerprint in expected.items():
            with self.subTest(shape=shape):
                entry = catalog['resources']['mask/' + shape]
                self.assertIsInstance(entry['files'], dict)
                self.assertEqual(entry['tree_sha256'], fingerprint)
                self.assertEqual(resources.manifest_hash(entry['files']), fingerprint)

    def test_catalog_home_traversal_is_rejected(self):
        bad = self.folder / 'native-resource-catalog.json'
        bad.write_text(json.dumps({'schema': 'jy14-native-resource-catalog/v1', 'source': '@home/../escape'}))
        with patch.object(resources, 'HERE', self.folder), patch.object(resources, 'CATALOG_SHA', hashlib.sha256(bad.read_bytes()).hexdigest()):
            with self.assertRaisesRegex(ValueError, 'Invalid catalog home-relative path'):
                resources.catalog()


if __name__ == '__main__':
    unittest.main()
