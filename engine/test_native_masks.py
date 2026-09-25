"""Mask integrity and source isolation; no live draft or cache mutations."""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import jy14_headless as j
import native_motion as motion
import native_export
import native_resources as resources
import runtime_profiles as profiles


class NativeMaskTests(unittest.TestCase):
    def setUp(self):
        self.plan = j.read_json(FIXTURE / 'mask-plan.json')

    def test_all_six_masks_accept_and_copy_captured_native_resources(self):
        record = j.verify_build(FIXTURE / 'mask-build-v1')
        self.assertEqual(len(record['native_resources']), 6)
        self.assertEqual(record['duration_us'], 12000000)
        self.assertTrue(all(not r['redistribution_authorized'] for r in record['native_resources']))
        self.assertEqual(len(record['assets']), 1)

    def test_unverified_shape_and_fields_are_rejected(self):
        for shape in ('text', 'custom', '', None):
            spec = deepcopy(self.plan['tracks'][0]['segments'][0])
            spec['mask']['shape'] = shape
            with self.assertRaisesRegex(ValueError, 'Unsupported geometric'):
                motion.validate(spec, 'video')
        self.plan['tracks'][0]['segments'][0]['mask']['url'] = 'https://example.invalid'
        with self.assertRaisesRegex(ValueError, 'Unsupported mask fields'):
            j.validate_plan(self.plan)

    def test_nonfinite_values_and_nonboolean_inversion_are_rejected(self):
        for field, value in [('width', 0), ('feather', float('nan')), ('height', True), ('invert', 1)]:
            spec = deepcopy(self.plan['tracks'][0]['segments'][0])
            spec['mask'][field] = value
            with self.assertRaises(ValueError):
                motion.validate(spec, 'video')

    def test_mask_must_be_visual_and_rounded_corners_rectangular(self):
        spec = self.plan['tracks'][0]['segments'][0]
        with self.assertRaisesRegex(ValueError, 'video track'):
            motion.validate(spec, 'audio')
        spec['mask']['round_corner'] = .2
        with self.assertRaisesRegex(ValueError, 'rectangle'):
            motion.validate(spec, 'video')

    def test_missing_category_or_changed_resource_binding_is_detected(self):
        spec = self.plan['tracks'][0]['segments'][0]
        segment, materials = {}, {}
        motion.apply(segment, materials, spec, 'video', WORK / 'draft')
        node = materials['common_mask'][0]
        index = {node['id']: ('common_mask', node)}
        motion.verify(segment, index, spec, 'video', 0)
        for field in ('category', 'resource_id', 'resource_type'):
            original = node[field]
            node[field] = ''
            with self.assertRaisesRegex(ValueError, 'resource identity'):
                motion.verify(segment, index, spec, 'video', 0)
            node[field] = original
        segment['enable_video_mask'] = False
        with self.assertRaisesRegex(ValueError, 'Mask disabled'):
            motion.verify(segment, index, spec, 'video', 0)

    def test_native_default_omission_preserves_mask_configuration(self):
        spec = self.plan['tracks'][0]['segments'][0]
        segment, materials = {}, {}
        motion.apply(segment, materials, spec, 'video', WORK / 'draft')
        node = materials['common_mask'][0]
        node['config'] = {'width': .28, 'height': .5}
        motion.verify(segment, {node['id']: ('common_mask', node)}, spec, 'video', 0)
        node['config']['width'] = .3
        with self.assertRaisesRegex(ValueError, 'parameter changed'):
            motion.verify(segment, {node['id']: ('common_mask', node)}, spec, 'video', 0)

    def test_wrong_runtime_refused_without_copying(self):
        destination = WORK / 'wrong-runtime'
        with self.assertRaisesRegex(ValueError, '(?i:runtime profile)'):
            resources.prepare(self.plan, destination, {'runtime_profile': 'jy14-headless-macos-11.4.0'})
        self.assertFalse(destination.exists())

    def test_build481_allows_only_captured_geometric_mask_keys(self):
        build481 = profiles.PROFILE_1140_BUILD481
        self.assertFalse(profiles.RUNTIME_IDENTITIES[build481]['capabilities']['native_resources'])
        allowed = ('mask/circle', 'mask/mirror', 'mask/rectangle', 'mask/star', 'mask/heart', 'mask/line')
        for key in allowed:
            with self.subTest(key=key):
                entry = resources.entry_for_runtime(key, resources.definition(key), build481)
                self.assertEqual(entry['source'], str(Path.home() / resources.BUILD481_RESOURCE_IDENTITIES[key]['source']))
                self.assertNotEqual(entry['source'], resources.definition(key)['source'])
                resources.validate_resource_key(build481, resources.catalog()['runtime_profile'], key, entry)
                target = WORK / ('build481-binding-' + key.split('/')[-1])
                resolved = resources.verify_binding(key, str(Path(entry['source'])), target, j.native_media_path,
                                                    allow_native_cache=True, runtime_profile=build481)
                self.assertEqual(resolved['location'], 'native-cache')
                old_path = resources.definition(key)['source']
                with self.assertRaisesRegex(ValueError, 'Build 481 native cache path changed'):
                    resources.verify_binding(key, old_path, target, j.native_media_path,
                                             allow_native_cache=True, runtime_profile=build481)

        with self.assertRaisesRegex(ValueError, 'not verified'):
            resources.validate_resource_key(build481, resources.catalog()['runtime_profile'], 'mask/custom', {})

        for key in allowed:
            fields = [
                    ('resource_id', 'wrong-id'),
                    ('tree_sha256', '0' * 64),
                    ('source', str(WORK / 'unrelated-cache'))]
            if key == 'mask/heart':
                fields.append(('name', 'wrong-name'))
            for field, replacement in fields:
                changed = resources.entry_for_runtime(key, resources.definition(key), build481)
                changed = deepcopy(changed)
                if field in {'resource_id', 'name'}:
                    changed['material'][field] = replacement
                else:
                    changed[field] = replacement
                with self.subTest(key=key, field=field), self.assertRaisesRegex(ValueError, 'identity changed|source changed|material name changed'):
                    resources.validate_resource_key(build481, resources.catalog()['runtime_profile'], key, changed)

    def test_build481_star_serializes_and_verifies_gui_pentagram_type(self):
        build481 = profiles.PROFILE_1140_BUILD481
        target = WORK / 'build481-star-material'
        spec = {'mask': {'shape': 'star'}}
        segment, materials = {}, {}
        motion.apply(segment, materials, spec, 'video', target, build481)
        node = materials['common_mask'][0]
        self.assertEqual(node['resource_type'], 'pentagram')
        motion.verify(segment, {node['id']: ('common_mask', node)}, spec, 'video', 0, build481)
        self.assertEqual(resources.material('mask/star', target)['resource_type'],
                         resources.definition('mask/star')['material']['resource_type'])
        altered = resources.entry_for_runtime('mask/star', resources.definition('mask/star'), build481)
        altered['material']['resource_type'] = 'star'
        with self.assertRaisesRegex(ValueError, 'resource_type changed'):
            resources.validate_resource_key(build481, resources.catalog()['runtime_profile'], 'mask/star', altered)

    def test_build481_supported_masks_prepare_isolated_and_other_shapes_fail_before_copy(self):
        build481 = profiles.PROFILE_1140_BUILD481
        shapes = ('circle', 'mirror', 'rectangle', 'star', 'heart', 'line')
        mask_plan = {'tracks': [{'type': 'video', 'segments': [
            {'mask': {'shape': shape}} for shape in shapes]}]}
        target = WORK / 'build481-approved-masks'
        records = resources.prepare(mask_plan, target, {'runtime_profile': build481})
        self.assertEqual([record['key'] for record in records], ['mask/circle', 'mask/heart', 'mask/line',
                                                                 'mask/mirror', 'mask/rectangle', 'mask/star'])
        expected = {
            'mask/circle': ('7356934080102928946', '755f487494e041e0adceaff3c1a747b1238773c071fe3297d1911112cccd3946', 27),
            'mask/mirror': ('7356933823327638042', '36365677e9ef362fdba0a5a9169cd9427c85f3ebecfc16f98c7d17a21bef3977', 19),
            'mask/rectangle': ('7356934318301647410', 'c8d500f2840e387e372744f6f44e1d2128e29c94df3dc482cf18a8de7d2f0ec6', 19),
            'mask/star': ('7416258989467374091', 'ba3fd7ebd571eba4f3383343eb7b8f6f504dfef8d6477af3bbe49bd8c67f2a8e', 26),
            'mask/heart': ('7416258912162157068', 'd72134d8c23f46d9d2ca3b2d7171908285487f2a1cb69cdb57593d427e422936', 26),
            'mask/line': ('7356933362960831003', 'e548c277fb2a6e06739855160a985a676221b19e9c4a65b60c8d75df1aea3c29', 19),
        }
        for record in records:
            with self.subTest(key=record['key']):
                resource_id, tree_sha256, file_count = expected[record['key']]
                self.assertEqual(record['resource_id'], resource_id)
                self.assertEqual(record['tree_sha256'], tree_sha256)
                self.assertEqual(len(record['files']), file_count)
                self.assertEqual(resources.tree_manifest(target / record['relative']), record['files'])

        key = 'mask/custom'
        plan = {'tracks': [{'type': 'video', 'segments': [{'mask': {'shape': 'custom'}}]}]}
        destination = WORK / 'build481-reject-mask-custom'
        with self.assertRaisesRegex(ValueError, 'not verified|no verified local capture'):
            resources.prepare(plan, destination, {'runtime_profile': build481})
        self.assertFalse(destination.exists())

    def test_build481_dissolve_build_resource_is_exact_but_export_scope_stays_closed(self):
        build481 = profiles.PROFILE_1140_BUILD481
        plan = {'tracks': [{'type': 'video', 'segments': [
            {'transition_out': {'name': 'dissolve'}}]}]}
        target = WORK / 'build481-approved-dissolve'
        records = resources.prepare(plan, target, {'runtime_profile': build481})
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record['key'], 'transition/dissolve')
        self.assertEqual(record['resource_id'], '6724845717472416269')
        self.assertEqual(record['tree_sha256'],
                         'dc006fa499721070ec74f98a2aa01ca7baa85bca5a7145b12acf6c4cdc0243da')
        self.assertEqual(len(record['files']), 14)
        self.assertEqual(resources.tree_manifest(target / record['relative']), record['files'])
        entry = resources.entry_for_runtime('transition/dissolve', resources.definition('transition/dissolve'),
                                             build481)
        self.assertEqual(entry['source'], str(Path.home() / resources.BUILD481_RESOURCE_IDENTITIES[
            'transition/dissolve']['source']))
        with self.assertRaisesRegex(ValueError, 'export-accepted'):
            native_export.require_build481_export_scope(
                build481, {'native_resources': records, 'font_assets': []},
                {'id': 'test', 'materials': {'transitions': [{'id': 'dissolve'}]}, 'tracks': []})

    def test_modified_resource_refused_and_original_cache_untouched(self):
        entry = resources.definition('mask/circle')
        dest = WORK / 'tampered-resource'
        shutil.copytree(entry['source'], dest)
        original = resources.tree_manifest(entry['source'])
        path = dest / next(iter(entry['files']))
        path.write_bytes(path.read_bytes() + b'changed')
        fake = deepcopy(entry)
        fake['source'] = str(dest)
        catalog = deepcopy(resources.catalog())
        catalog['resources']['mask/circle'] = fake
        runtime = {'runtime_profile': catalog['runtime_profile']}
        with patch.object(resources, 'catalog', return_value=catalog):
            with self.assertRaisesRegex(ValueError, 'bytes differ'):
                resources.prepare(self.plan, WORK / 'must-not-copy', runtime)
        self.assertEqual(resources.tree_manifest(entry['source']), original)
        self.assertFalse((WORK / 'must-not-copy').exists())

    def test_missing_resource_and_symlink_fail_closed(self):
        entry = resources.definition('mask/circle')
        entry['source'] = str(WORK / 'missing-source')
        catalog = deepcopy(resources.catalog())
        catalog['resources']['mask/circle'] = entry
        runtime = {'runtime_profile': catalog['runtime_profile']}
        with patch.object(resources, 'catalog', return_value=catalog):
            with self.assertRaises(FileNotFoundError):
                resources.prepare(self.plan, WORK / 'must-not-create', runtime)
        folder = WORK / 'symlink-resource'
        folder.mkdir()
        (folder / 'external').symlink_to(FIXTURE / 'mask-plan.json')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            resources.tree_manifest(folder)

    def test_copied_resources_do_not_need_cache_for_readback(self):
        record = j.read_json(FIXTURE / 'mask-build-v1/build.json')
        original = resources.definition
        def absent_source(key):
            value = original(key)
            value['source'] = str(WORK / 'not-present')
            return value
        with patch.object(resources, 'definition', side_effect=absent_source):
            resources.verify_files(record['native_resources'], FIXTURE / 'mask-build-v1/draft', self.plan)

    def test_native_cache_rebinding_requires_explicit_mode_and_exact_bytes(self):
        entry = resources.definition('mask/circle')
        target = WORK / 'draft'
        with self.assertRaisesRegex(ValueError, 'path changed'):
            resources.verify_binding('mask/circle', entry['source'], target, j.native_media_path)
        got = resources.verify_binding('mask/circle', entry['source'], target, j.native_media_path, True)
        self.assertEqual(got['location'], 'native-cache')
        self.assertTrue(got['bytes_verified'])
        with self.assertRaisesRegex(ValueError, 'path changed'):
            resources.verify_binding('mask/circle', str(WORK / 'other-copy'), target, j.native_media_path, True)
        with patch.object(resources, 'tree_manifest', return_value={}):
            with self.assertRaisesRegex(ValueError, 'bytes changed'):
                resources.verify_binding('mask/circle', entry['source'], target, j.native_media_path, True)

    def test_line_mask_rejects_ineffective_dimension_controls(self):
        spec = self.plan['tracks'][0]['segments'][2]
        for field in ('width', 'height'):
            with self.assertRaisesRegex(ValueError, 'half-plane'):
                motion.validate(dict(spec, mask=dict(spec['mask'], **{field: .5})), 'video')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    FIXTURE, WORK = args.fixture.resolve(), args.work.resolve()
    WORK.mkdir(parents=True, exist_ok=False)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NativeMaskTests))
    j.write(WORK / 'result.json', {'tests': result.testsRun, 'passed': result.wasSuccessful(),
                                 'live_written': False, 'cache_changed': False})
    raise SystemExit(not result.wasSuccessful())
