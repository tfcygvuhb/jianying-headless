"""Behavioral guard tests; keep all generated fixtures under the requested work path."""
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import native_export as e

WORK = Path(os.environ['JY_NATIVE_EXPORT_TEST_WORK']).resolve()
WORK.mkdir(parents=True, exist_ok=True)


class ExportGuards(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='case-', dir=WORK))
        self.folder = self.root / 'build/draft'
        self.folder.mkdir(parents=True)
        self.target = self.root / 'planned-live-draft'
        self.relative = Path('Resources/headless-media/asset.mp4')
        self.source = self.folder / self.relative
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b'owned test bytes')
        self.settings = dict(width=1280, height=720, fps=25, bitrate=4_000_000, timeout_seconds=60)
        self.probe = {'format': {'duration': '6.0', 'tags': {'major_brand': 'isom'}},
                      'streams': [{'codec_type': 'video', 'codec_name': 'h264', 'width': 1280, 'height': 720,
                                   'r_frame_rate': '25/1', 'nb_frames': '150'},
                                  {'codec_type': 'audio', 'codec_name': 'aac'}]}

    def test_native_placeholder_resolves_to_build_not_live(self):
        source, relative = e.source_in_build(e.j.DRAFT_PATH_TOKEN + str(self.relative), self.target, self.folder)
        self.assertEqual(source, self.source)
        self.assertEqual(relative, self.relative)
        self.assertFalse(self.target.exists())

    def test_external_or_traversal_dependency_rejected(self):
        for path in ('/outside/asset.mp4', '../asset.mp4', e.j.DRAFT_PATH_TOKEN + '../asset.mp4'):
            with self.assertRaises(ValueError):
                e.source_in_build(path, self.target, self.folder)

    def test_symlink_dependency_rejected(self):
        link = self.folder / 'Resources/link.mp4'
        link.symlink_to(self.source)
        with self.assertRaises(ValueError):
            e.source_in_build(str(self.target / 'Resources/link.mp4'), self.target, self.folder)

    def test_changed_dependency_is_not_staged(self):
        out = self.root / 'output'; out.mkdir()
        raw = str(self.target / self.relative)
        timeline = {'materials': {'videos': [{'path': raw}]}}
        record = {'target': str(self.target), 'files': {str(self.relative): {'size': 16, 'sha256': '0' * 64}}}
        with self.assertRaisesRegex(ValueError, 'manifest'):
            e.stage_timeline(timeline, record, self.folder, out)
        self.assertFalse((out / self.relative).exists())

    def test_stage_copies_and_rewrites_dependency_without_mutating_input(self):
        out = self.root / 'output'; out.mkdir()
        raw = str(self.target / self.relative)
        timeline = {'materials': {'videos': [{'path': raw}]}}
        record = {'target': str(self.target), 'files': {str(self.relative): {
            'size': self.source.stat().st_size, 'sha256': e.j.nd.digest(self.source)}}}
        value, files = e.stage_timeline(timeline, record, self.folder, out)
        self.assertEqual(value['materials']['videos'][0]['path'], str(out / self.relative))
        self.assertEqual(timeline['materials']['videos'][0]['path'], raw)
        self.assertEqual((out / self.relative).read_bytes(), self.source.read_bytes())
        self.assertEqual(files, record['files'])

    def test_unknown_resource_and_online_dependency_rejected(self):
        for node in ({'mystery_path': '/outside/file'}, {'resource_url': 'https://example.test/private'}):
            with self.assertRaises(ValueError):
                e.stage_timeline(node, {'target': str(self.target)}, self.folder, self.root)

    def test_serialized_text_style_path_staged_but_literal_text_unchanged(self):
        out = self.root / 'text-output'; out.mkdir()
        raw = str(self.target / self.relative)
        content = {'text': raw, 'styles': [{'effectStyle': {'id': 'test-style', 'path': raw}}]}
        timeline = {'materials': {'videos': [{'path': raw}],
                                 'texts': [{'type': 'text', 'content': json.dumps(content)}]}}
        original = deepcopy(timeline)
        record = {'target': str(self.target), 'files': {str(self.relative): {
            'size': self.source.stat().st_size, 'sha256': e.j.nd.digest(self.source)}}}
        staged, files = e.stage_timeline(timeline, record, self.folder, out)
        actual = json.loads(staged['materials']['texts'][0]['content'])
        self.assertEqual(actual['styles'][0]['effectStyle']['path'], str(out / self.relative))
        self.assertEqual(actual['text'], raw)
        self.assertEqual(timeline, original)
        self.assertEqual(files, record['files'])

    def test_serialized_text_cannot_hide_external_or_ambiguous_style_paths(self):
        contents = [
            json.dumps({'text': 'https://example.test is literal subtitle text', 'styles': [
                {'effectStyle': {'id': 'not-staged', 'path': '/outside/style'}}]}),
            json.dumps({'text': 'font', 'styles': [{'font': {'path': '/outside/font.ttf'}}]}),
            '{"text":"duplicate","styles":[],"styles":[{"effectStyle":{"path":"/outside/style"}}]}',
            'not valid native text JSON',
        ]
        for content in contents:
            with self.subTest(content=content), self.assertRaises((ValueError, RuntimeError)):
                e.stage_timeline({'materials': {'texts': [{'type': 'text', 'content': content}]}},
                                 {'target': str(self.target)}, self.folder, self.root)

    def test_quicktime_mislabeled_mp4_rejected(self):
        self.probe['format']['tags']['major_brand'] = 'qt  '
        with self.assertRaisesRegex(ValueError, 'MP4 container'):
            e.validate_probe(self.probe, self.settings, 6_000_000, True)

    def test_duplicate_identical_mp4_brand_accepted_but_mixed_rejected(self):
        self.probe['format']['tags']['major_brand'] = 'isom;isom'
        self.assertEqual(e.validate_probe(self.probe, self.settings, 6_000_000, True)['major_brand'], 'isom')
        self.probe['format']['tags']['major_brand'] = 'isom;qt  '
        with self.assertRaisesRegex(ValueError, 'MP4 container'):
            e.validate_probe(self.probe, self.settings, 6_000_000, True)

    def test_real_ftyp_header_checked_independently_of_tags(self):
        output = self.root / 'output.mp4'
        for header, accepted in ((b'\x00\x00\x00\x20ftypisom\x00\x00\x02\x00', True),
                                 (b'\x00\x00\x00\x20ftypqt  \x00\x00\x02\x00', False),
                                 (b'\x00\x00\x00\x20freeisom\x00\x00\x02\x00', False)):
            output.write_bytes(header)
            if accepted:
                self.assertEqual(e.validate_ftyp(output), 'isom')
            else:
                with self.assertRaisesRegex(ValueError, 'MP4 container'):
                    e.validate_ftyp(output)

    def test_truncated_video_rejected(self):
        self.probe['streams'][0]['nb_frames'] = '75'
        with self.assertRaisesRegex(ValueError, 'frame count'):
            e.validate_probe(self.probe, self.settings, 6_000_000, True)

    def test_missing_audio_rejected(self):
        self.probe['streams'].pop()
        with self.assertRaisesRegex(ValueError, 'audio stream'):
            e.validate_probe(self.probe, self.settings, 6_000_000, True)

    def test_wrong_canvas_and_fps_rejected(self):
        for field, value in (('width', 1920), ('r_frame_rate', '30/1')):
            bad = deepcopy(self.probe)
            bad['streams'][0][field] = value
            with self.assertRaises(ValueError):
                e.validate_probe(bad, self.settings, 6_000_000, True)

    def test_matching_mp4_accepted(self):
        value = e.validate_probe(self.probe, self.settings, 6_000_000, True)
        self.assertEqual(value['frames'], 150)
        self.assertEqual(value['audio_codec'], 'aac')
        self.assertEqual(value['frame_delta'], 0)

    def test_aligned_timeline_missing_or_extra_frame_rejected(self):
        for count in ('149', '151'):
            with self.subTest(count=count):
                self.probe['streams'][0]['nb_frames'] = count
                with self.assertRaisesRegex(ValueError, 'frame count'):
                    e.validate_probe(self.probe, self.settings, 6_000_000, True)

    def test_microsecond_precision_does_not_admit_a_missing_frame(self):
        self.settings['fps'] = 30
        self.probe['streams'][0]['r_frame_rate'] = '30/1'
        self.probe['format']['duration'] = '1.233333'
        self.probe['streams'][0]['nb_frames'] = '37'
        value = e.validate_probe(self.probe, self.settings, 1_233_333, True)
        self.assertEqual(value['frame_count_policy'], 'exact-aligned')
        self.probe['streams'][0]['nb_frames'] = '36'
        with self.assertRaisesRegex(ValueError, 'frame count'):
            e.validate_probe(self.probe, self.settings, 1_233_333, True)

    def test_fractional_timeline_allows_only_adjacent_frame_counts(self):
        for count in (150, 151):
            self.probe['streams'][0]['nb_frames'] = str(count)
            value = e.validate_probe(self.probe, self.settings, 6_020_000, True)
            self.assertEqual(value['accepted_frame_range'], [150, 151])
            self.assertEqual(value['frame_count_policy'], 'adjacent-fractional')
        for count in (149, 152):
            self.probe['streams'][0]['nb_frames'] = str(count)
            with self.assertRaisesRegex(ValueError, 'frame count'):
                e.validate_probe(self.probe, self.settings, 6_020_000, True)

    def test_unknown_mask_identity_is_rejected(self):
        for node in ({'id': 'circle'}, {'resource_type': 'text'},
                     {'resource_type': 'circle', 'resource_id': 'uncaptured'}):
            with self.assertRaisesRegex(ValueError, 'mask'):
                e.supported_features({'materials': {'common_mask': [node]}})

    def test_captured_static_mask_parameters_are_accepted(self):
        for shape in e.resources.SHAPES:
            node = e.motion.mask_material({'shape': shape}, self.target)
            value = e.supported_features({'materials': {'common_mask': [node]}})
            self.assertIn('six captured shapes', value['mask_export'])

    def test_mask_custom_parameters_and_invalid_values_rejected(self):
        for override in ({'text': 'not supported'}, {'feather': float('nan')}, {'invert': 1},
                         {'aspectRatio': True}, {'roundCorner': .5}):
            node = e.motion.mask_material({'shape': 'circle'}, self.target)
            node['config'].update(override)
            with self.assertRaises(ValueError):
                e.supported_features({'materials': {'common_mask': [node]}})

    def test_forged_mask_directory_is_not_staged(self):
        out = self.root / 'output'; out.mkdir()
        relative = Path('Resources/headless-native/forged')
        folder = self.folder / relative; folder.mkdir(parents=True)
        (folder / 'config.json').write_bytes(b'{}')
        node = e.motion.mask_material({'shape': 'circle'}, self.target)
        node['path'] = str(self.target / relative)
        record = {'target': str(self.target), 'files': {
            str(relative / 'config.json'): {'size': 2, 'sha256': e.j.nd.digest(folder / 'config.json')}}}
        with self.assertRaisesRegex(ValueError, 'captured native resource'):
            e.stage_timeline({'materials': {'common_mask': [node]}}, record, self.folder, out)
        self.assertFalse((out / relative).exists())

    def test_unverified_effects_and_animations_rejected(self):
        for materials in ({'video_effects': [{'id': 'effect'}]},
                          {'material_animations': [{'animations': [{'name': 'pop'}]}]},
                          {'speeds': [{'curve_speed': {'points': [1, 2]}}]},
                          {'transitions': [{'effect_id': 'uncaptured'}]}):
            with self.assertRaises(ValueError):
                e.supported_features({'materials': materials})

    def test_captured_light_shake_and_native_parameters_accepted(self):
        node = deepcopy(e.resources.definition('effect/light-shake')['material'])
        node['id'] = 'captured-effect'
        node['adjust_params'][0]['value'] = 0
        node['adjust_params'][1]['value'] = 1
        value = e.supported_features({'materials': {'video_effects': [node]},
            'tracks': [{'type': 'effect', 'segments': [{'material_id': node['id']}]}]})
        self.assertEqual([w['code'] for w in value['warnings']], ['native-resource-use-limits'])

    def test_effect_identity_parameters_and_binding_cannot_be_forged(self):
        original = deepcopy(e.resources.definition('effect/light-shake')['material'])
        original['id'] = 'captured-effect'
        for change in ({'effect_id': 'uncaptured'}, {'resource_id': 'uncaptured'}, {'apply_target_type': 0},
                       {'value': .5}, {'value': True}, {'adjust_params': []},
                       {'adjust_params': [{'name': 'effects_adjust_range', 'value': float('nan')},
                                          {'name': 'effects_adjust_speed', 'value': .5}]}):
            with self.assertRaises(ValueError):
                e.supported_features({'materials': {'video_effects': [{**original, **change}]}})
        for segment in ({'material_id': 'different'},
                        {'material_id': original['id'], 'common_keyframes': [{'id': 'unexpected-animation'}]}):
            with self.assertRaises(ValueError):
                e.supported_features({'materials': {'video_effects': [original]},
                                      'tracks': [{'type': 'effect', 'segments': [segment]}]})
        with self.assertRaises(ValueError):
            e.supported_features({'materials': {'video_effects': [original]},
                                  'tracks': [{'type': 'video', 'segments': [{'material_id': original['id']}]}]})

    def test_retired_filter_and_flower_rejected(self):
        for kind in ('filter', 'text_effect'):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'support has been removed'):
                e.supported_features({'materials': {'effects': [{'type': kind, 'id': 'retired'}]}})

    def test_orphan_flower_style_still_rejected(self):
        text = {'id': 'text', 'content': json.dumps({'styles': [{'effectStyle': {'id': 'retired'}}]})}
        with self.assertRaisesRegex(ValueError, 'no captured material binding'):
            e.supported_features({'materials': {'texts': [text]},
                                  'tracks': [{'type': 'text', 'segments': [{'material_id': 'text'}]}]})

    def test_retired_effects_fail_before_export_job_creation(self):
        out = self.root / 'must-not-export'
        timeline = {'materials': {'effects': [{'type': 'filter', 'id': 'retired'}]}}
        record = {'runtime_profile': 'jy14-headless-macos-11.5.0'}
        with patch.object(e, 'verified_build', return_value=(self.folder, record, timeline)):
            with self.assertRaisesRegex(ValueError, 'support has been removed'):
                e.run(self.folder, out)
        self.assertFalse(out.exists())

    def test_build481_native_export_abi_passed(self):
        e.require_verified_native_abi('jy14-headless-macos-11.4.0-build481')
        with self.assertRaisesRegex(ValueError, 'ABI evidence is incomplete'):
            e.require_verified_native_abi('jy14-headless-macos-future')

    def test_build481_advanced_export_scope_stays_closed(self):
        profile = 'jy14-headless-macos-11.4.0-build481'
        base = {'id': 'test-timeline', 'materials': {'speeds': [{'speed': 1}]},
                'tracks': [{'segments': [{'speed': 1}]}]}
        e.require_build481_export_scope(profile, {'native_resources': [], 'font_assets': []}, base)
        for bucket in ('transitions', 'video_effects', 'effects'):
            value = deepcopy(base)
            value['materials'][bucket] = [{'id': 'pending'}]
            with self.subTest(bucket=bucket), self.assertRaises(ValueError):
                e.require_build481_export_scope(profile, {}, value)
        for key, bucket in (('transition/dissolve', 'transitions'),
                            ('effect/light-shake', 'video_effects')):
            value = deepcopy(base)
            value['materials'][bucket] = [deepcopy(e.resources.definition(key)['material'])]
            e.require_build481_export_scope(profile, {'native_resources': [{'key': key}]}, value)
            with self.assertRaisesRegex(ValueError, 'inventory does not match'):
                e.require_build481_export_scope(profile, {}, value)
            value['materials'][bucket][0]['resource_id'] = 'wrong'
            with self.assertRaisesRegex(ValueError, 'identity is not export-accepted'):
                e.require_build481_export_scope(profile, {'native_resources': [{'key': key}]}, value)
        value = deepcopy(base)
        value['materials']['common_mask'] = [{'resource_type': 'circle'}]
        e.require_build481_export_scope(profile, {'native_resources': [{'key': 'mask/circle'}]}, value)
        value['materials']['common_mask'] = [{'resource_type': 'mirror'}]
        e.require_build481_export_scope(profile, {'native_resources': [{'key': 'mask/mirror'}]}, value)
        for key, resource_type in (('mask/rectangle', 'rectangle'), ('mask/star', 'pentagram'),
                                   ('mask/heart', 'heart'), ('mask/line', 'line')):
            value['materials']['common_mask'] = [{'resource_type': resource_type}]
            e.require_build481_export_scope(profile, {'native_resources': [{'key': key}]}, value)
        with self.assertRaisesRegex(ValueError, 'inventory does not match'):
            e.require_build481_export_scope(profile, {}, value)
        value['materials']['common_mask'][0]['resource_type'] = 'custom'
        with self.assertRaisesRegex(ValueError, 'native resource'):
            e.require_build481_export_scope(profile, {'native_resources': [{'key': 'mask/custom'}]}, value)
        value = deepcopy(base)
        for speed in (1,):
            value['materials']['speeds'][0]['speed'] = speed
            e.require_build481_export_scope(profile, {}, value)
        for speed in (0.1, 0.5, 0.75, 1.5, 8):
            value['materials']['speeds'][0]['speed'] = speed
            with self.assertRaisesRegex(ValueError, 'unreviewed constant speeds'):
                e.require_build481_export_scope(profile, {}, value)
        value['materials']['speeds'][0]['speed'] = 2
        with self.assertRaisesRegex(ValueError, 'unreviewed constant speeds'):
            e.require_build481_export_scope(profile, {}, value)
        value['materials']['speeds'][0]['speed'] = 0.1001
        with self.assertRaisesRegex(ValueError, 'unreviewed constant speeds'):
            e.require_build481_export_scope(profile, {}, value)
        value['materials']['speeds'][0]['speed'] = True
        with self.assertRaisesRegex(ValueError, 'unreviewed constant speeds'):
            e.require_build481_export_scope(profile, {}, value)
        value['materials']['speeds'][0]['speed'] = 1.5
        value['materials']['speeds'][0]['curve_speed'] = {'points': []}
        with self.assertRaisesRegex(ValueError, 'await export acceptance'):
            e.require_build481_export_scope(profile, {}, value)
        value['materials']['speeds'][0]['curve_speed'] = {}
        with self.assertRaisesRegex(ValueError, 'await export acceptance'):
            e.require_build481_export_scope(profile, {}, value)
        value = deepcopy(base)
        value['tracks'][0]['segments'][0]['common_keyframes'] = [{'id': 'pending'}]
        with self.assertRaisesRegex(ValueError, 'keyframes are not verified'):
            e.require_build481_export_scope(profile, {}, value)
        with self.assertRaisesRegex(ValueError, 'font SHA-256'):
            e.require_build481_export_scope(profile, {'font_assets': [{'relative': 'font.ttf',
                'sha256': '0' * 64, 'size': 1}]}, base)

    @staticmethod
    def build481_keyframe_group(channel='y', points=None):
        prop, low, high = e.motion.KEYFRAMES[channel]
        if points is None:
            points = [0, 1_000_000]
        return {'id': 'group-' + channel, 'material_id': '', 'property_type': prop,
                'keyframe_list': [
                    {'id': 'node-%s-%s' % (channel, at), 'curveType': 'Line', 'graphID': '',
                     'left_control': {'x': 0.0, 'y': 0.0}, 'right_control': {'x': 0.0, 'y': 0.0},
                     'time_offset': at, 'values': [low if at == 0 else high]}
                    for at in points]}

    def test_build481_verified_keyframe_channel_matrix_is_accepted(self):
        profile = 'jy14-headless-macos-11.4.0-build481'
        matrix = {'video': ('x', 'y', 'scale', 'rotation', 'opacity', 'volume'),
                  'text': ('x', 'y', 'scale', 'rotation'), 'audio': ('volume',)}
        for track_type, channels in matrix.items():
            for channel in channels:
                with self.subTest(track_type=track_type, channel=channel):
                    segment = {'target_timerange': {'start': 0, 'duration': 1_000_000},
                               'common_keyframes': [self.build481_keyframe_group(channel)]}
                    if track_type == 'video':
                        segment.update(speed=1.0, source_timerange={'start': 0, 'duration': 1_000_000})
                    timeline = {'id': 'test-timeline', 'materials': {},
                                'tracks': [{'type': track_type, 'segments': [segment]}]}
                    e.require_build481_export_scope(profile, {'font_assets': []}, timeline)

    def test_build481_allows_only_pinned_custom_fonts(self):
        profile = 'jy14-headless-macos-11.4.0-build481'
        timeline = {'id': 'test-timeline', 'materials': {}, 'tracks': []}
        asset = {'relative': 'Resources/headless-fonts/monaco.ttf',
                 'sha256': 'e110b2fb6248c654878dee87e9805ac0b2afc8fab19099cf92bfe12ea085c028', 'size': 12345}
        for digest in e.BUILD481_FONT_SHA256:
            e.require_build481_export_scope(profile, {'font_assets': [dict(asset, sha256=digest)]}, timeline)
        for digest in ('0' * 64,
                       '5add3f3f2bd7fd897d2fa5ccbe468607c52111dc44cdfaaf2d851a574f5357a7'):
            with self.subTest(digest=digest), self.assertRaisesRegex(ValueError, 'font SHA-256'):
                e.require_build481_export_scope(profile, {'font_assets': [dict(asset, sha256=digest)]}, timeline)

    def test_build481_keyframes_reject_unverified_shapes_channels_and_mapping(self):
        profile = 'jy14-headless-macos-11.4.0-build481'
        def timeline(track_type='text', channel='y', **segment_changes):
            segment = {'target_timerange': {'start': 0, 'duration': 1_000_000},
                       'common_keyframes': [self.build481_keyframe_group(channel)]}
            segment.update(segment_changes)
            return {'id': 'test-timeline', 'materials': {},
                    'tracks': [{'type': track_type, 'segments': [segment]}]}

        rejected = [
            timeline('text', 'opacity'),
            timeline('filter', 'y'),
            timeline('video', 'x', speed=1.5),
            timeline('video', 'x', speed=1.0,
                     source_timerange={'start': 100, 'duration': 1_000_000}),
            timeline('video', 'x', speed=1.0,
                     source_timerange={'start': 0, 'duration': 900_000}),
        ]
        for node_change in ({'curveType': 'Sine'}, {'curveType': 'Line', 'graphID': 'graph'},
                            {'curveType': 'Line', 'values': [0.0, .5]},
                            {'curveType': 'Line', 'values': [float('nan')]}):
            value = timeline()
            value['tracks'][0]['segments'][0]['common_keyframes'][0]['keyframe_list'][0].update(node_change)
            rejected.append(value)
        value = timeline()
        value['tracks'][0]['segments'][0]['common_keyframes'][0]['keyframe_list'].pop()
        rejected.append(value)
        value = timeline()
        value['tracks'][0]['segments'][0]['common_keyframes'][0]['keyframe_list'][1]['time_offset'] = 0
        rejected.append(value)
        value = timeline()
        value['tracks'][0]['segments'][0]['common_keyframes'].append(self.build481_keyframe_group('y'))
        rejected.append(value)
        for candidate in rejected:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                e.require_build481_export_scope(profile, {'font_assets': []}, candidate)

    def test_previously_verified_native_export_profiles_remain_enabled(self):
        # Build 481's fail-closed ABI gate must not accidentally disable the
        # exact 11.5.0 and 11.4.2 profiles that already passed native export.
        for version in ('11.5.0', '11.4.2'):
            with self.subTest(version=version):
                profile_id = 'jy14-headless-macos-' + version
                self.assertIn(profile_id, e.VERIFIED_NATIVE_ABI_PROFILES)
                e.require_verified_native_abi(profile_id)

    def test_native_helper_preserves_profile_specific_restore_dispatch(self):
        source = (Path(__file__).with_name('native_export.cpp')).read_text()
        self.assertRegex(source, re.compile(
            r'"11\.5\.0".*?0x21b86dc, 0x274b018, 0x3d8, 0x7e8, false, true', re.S))
        self.assertRegex(source, re.compile(
            r'"11\.4\.2".*?0x21234d0, 0x2681f98, 0x3d8, 0x7e8, false, true', re.S))
        self.assertRegex(source, re.compile(
            r'"11\.4\.0-build481".*?0x2041b80, 0x2681f98, 0x3d8, 0x7e8, true, true', re.S))
        self.assertIn('if (active_abi->invoke_restore_via_server)', source)
        self.assertIn('reinterpret_cast<void (*)(long, bool, long)>(base + active_abi->restore_draft)', source)
        self.assertIn('checkResponse(server.invoke(restoreReq, sid)', source)
        self.assertIn('exportcallback compile_error_callback', source)

    def test_changed_light_shake_resource_is_not_staged(self):
        out = self.root / 'output'; out.mkdir()
        relative = Path('Resources/headless-native/forged-effect')
        folder = self.folder / relative; folder.mkdir(parents=True)
        (folder / 'config.json').write_bytes(b'{}')
        node = deepcopy(e.resources.definition('effect/light-shake')['material'])
        node['path'] = str(self.target / relative)
        record = {'target': str(self.target), 'files': {
            str(relative / 'config.json'): {'size': 2, 'sha256': e.j.nd.digest(folder / 'config.json')}}}
        with self.assertRaisesRegex(ValueError, 'captured native resource'):
            e.stage_timeline({'materials': {'video_effects': [node]}}, record, self.folder, out)
        self.assertFalse((out / relative).exists())

    def test_known_dissolve_and_empty_native_defaults_accepted(self):
        value = e.supported_features({'materials': {
            'common_mask': [], 'video_effects': [], 'material_animations': [{'animations': []}],
            'transitions': [{'effect_id': '6724845717472416269'}]}, 'tracks': [{'type': 'video'}]})
        self.assertIn('requires viewing', value['visual_acceptance'])
        self.assertEqual([w['code'] for w in value['warnings']], ['native-dissolve-audio-overlap'])
        self.assertEqual(e.supported_features({'materials': {}, 'tracks': []})['warnings'], [])

    def test_invalid_settings_rejected(self):
        timeline = {'canvas_config': {'width': 1280, 'height': 721}, 'fps': 25}
        with self.assertRaises(ValueError):
            e.settings_for(timeline, 4_000_000, 60)
        timeline['canvas_config']['height'] = 720
        for bitrate, timeout in ((True, 60), (0, 60), (4_000_000, 0)):
            with self.assertRaises(ValueError):
                e.settings_for(timeline, bitrate, timeout)

    def test_sandbox_allows_only_owned_user_data_and_no_external_writes(self):
        job = self.root / 'job'; job.mkdir()
        profile = job / 'test.sb'; profile.write_bytes(e.sandbox_profile(job))
        allowed = job / 'allowed.txt'; allowed.write_text('fixture')
        denied = self.root / 'denied.txt'; denied.write_text('fixture')
        permitted = subprocess.run(['/usr/bin/sandbox-exec', '-f', str(profile), '/bin/cat', str(allowed)], capture_output=True)
        forbidden = subprocess.run(['/usr/bin/sandbox-exec', '-f', str(profile), '/bin/cat', str(denied)], capture_output=True)
        write = subprocess.run(['/usr/bin/sandbox-exec', '-f', str(profile), '/usr/bin/touch', str(self.root / 'forbidden-write')], capture_output=True)
        self.assertEqual(permitted.returncode, 0)
        self.assertNotEqual(forbidden.returncode, 0)
        self.assertNotEqual(write.returncode, 0)
        self.assertFalse((self.root / 'forbidden-write').exists())


if __name__ == '__main__':
    result = unittest.main(exit=False).result
    e.j.write(WORK / 'result.json', {'tests': result.testsRun, 'passed': result.wasSuccessful(),
                                   'failures': len(result.failures), 'errors': len(result.errors),
                                   'live_written': False, 'export_renderer_started': False})
    raise SystemExit(not result.wasSuccessful())
