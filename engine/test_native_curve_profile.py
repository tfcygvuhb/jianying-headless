"""Self-contained tests for the Build 481 named curve data constructor."""
from copy import deepcopy
import unittest
import uuid
from unittest.mock import patch

import native_curve_profile as curve
from runtime_profiles import PROFILE_1140_BUILD481


def uid():
    return str(uuid.uuid4()).upper()


def base_timeline():
    ids = [uid() for _ in range(8)]
    video_id, speed_id, canvas_id, placeholder_id, channel_id, color_id, vocal_id, segment_id = ids
    video = {
        'beauty_face_auto_preset': {}, 'category_name': 'local', 'check_flag': 62978047,
        'crop': {}, 'duration': 24_000_000, 'height': 720, 'id': video_id,
        'is_set_beauty_mode': True, 'local_material_id': uid(), 'material_id': '',
        'material_name': curve.SOURCE_NAME, 'matting': {'path': ''}, 'path': curve.SOURCE_PATH,
        'stable': {'time_range': {}}, 'type': 'video', 'video_algorithm': {
            'path': '', 'story_video_modify_video_config': {}},
        'video_mask_shadow': {'resource_id': '', 'path': ''},
        'video_mask_stroke': {'resource_id': '', 'path': '', 'type': ''}, 'width': 1280,
    }
    extras = [speed_id, canvas_id, placeholder_id, channel_id, color_id, vocal_id]
    segment = {
        'clip': {'scale': {'x': 1.0, 'y': 1.0}, 'transform': {'x': 0.0, 'y': 0.0}, 'flip': {}},
        'enable_adjust_mask': False, 'enable_hsl': False, 'extra_material_refs': extras,
        'hdr_settings': {'mode': 1}, 'id': segment_id, 'material_id': video_id,
        'render_timerange': {}, 'responsive_layout': {}, 'source': 'segmentsourcenormal',
        'source_timerange': {'duration': curve.SOURCE_DURATION_US},
        'target_timerange': {'duration': curve.SOURCE_DURATION_US}, 'uniform_scale': {},
    }
    return {
        'canvas_config': {'width': 1280, 'height': 720}, 'color_space': 0, 'config': {},
        'duration': curve.SOURCE_DURATION_US, 'id': uid(),
        'keyframes': {},
        'last_modified_platform': {},
        'materials': {
            'videos': [video], 'canvases': [{'id': canvas_id, 'type': 'canvas_color'}],
            'placeholder_infos': [{'id': placeholder_id, 'meta_type': 'none', 'type': 'placeholder_info'}],
            'speeds': [{'id': speed_id, 'type': 'speed'}],
            'sound_channel_mappings': [{'id': channel_id, 'type': 'none'}],
            'material_colors': [{'id': color_id}],
            'vocal_separations': [{'id': vocal_id, 'type': 'vocal_separation'}],
        },
        'new_version': '185.0.0', 'path': '',
        'function_assistant_info': {'fps': {}},
        'platform': {'app_id': 3704, 'app_source': 'lv', 'app_version': '11.4.0',
                     'device_id': 'fixture-device', 'hard_disk_id': 'fixture-disk',
                     'mac_address': 'fixture-mac', 'os': 'mac', 'os_version': '26.5.1'},
        'last_modified_platform': {'app_id': 3704, 'app_source': 'lv', 'app_version': '11.4.0',
                                   'device_id': 'fixture-device', 'hard_disk_id': 'fixture-disk',
                                   'mac_address': 'fixture-mac', 'os': 'mac', 'os_version': '26.6.2'},
        'render_index_track_mode_on': True, 'smart_ads_info': {},
        'tracks': [{'id': uid(), 'name': 'Main', 'segments': [segment], 'type': 'video'}],
        'uneven_animation_template_info': {}, 'version': 360000,
    }


class Build481CurveProfileTests(unittest.TestCase):
    def build(self, base=None, **kwargs):
        return curve.build_curve_profile(
            deepcopy(base_timeline() if base is None else base),
            runtime_profile=kwargs.get('runtime_profile', PROFILE_1140_BUILD481),
            source_fps=kwargs.get('source_fps', 30),
            source_sha256=kwargs.get('source_sha256', curve.SOURCE_SHA256),
        )

    def test_builds_exact_named_curve_on_new_graph_without_mutating_base(self):
        base = base_timeline()
        before = deepcopy(base)
        result = self.build(base)
        seg = result['tracks'][0]['segments'][0]
        speed = result['materials']['speeds'][0]
        self.assertEqual(base, before)
        self.assertEqual(result['duration'], curve.TARGET_DURATION_US)
        self.assertEqual(seg['source_timerange'], {'duration': curve.SOURCE_DURATION_US})
        self.assertEqual(seg['target_timerange'], {'duration': curve.TARGET_DURATION_US})
        self.assertEqual(seg['speed'], curve.CURVE_SCALAR)
        self.assertEqual(speed, {
            'id': speed['id'], 'type': 'speed', 'mode': 1, 'speed': curve.CURVE_SCALAR,
            'curve_speed': {'id': curve.CURVE_ID, 'name': curve.CURVE_NAME,
                            'speed_points': curve.CURVE_POINTS},
        })
        self.assertNotEqual(speed['id'], base['materials']['speeds'][0]['id'])
        self.assertEqual(seg['extra_material_refs'].count(speed['id']), 1)
        self.assertNotIn(base['materials']['speeds'][0]['id'], seg['extra_material_refs'])
        self.assertNotAlmostEqual(curve.SOURCE_DURATION_US / curve.CURVE_SCALAR,
                                  curve.TARGET_DURATION_US, delta=1)

    def test_rejects_wrong_runtime_fps_canvas_and_material_identity(self):
        with self.assertRaisesRegex(ValueError, 'Build 481'):
            self.build(runtime_profile='other-runtime')
        with self.assertRaisesRegex(ValueError, '30 fps'):
            self.build(source_fps=25)
        with self.assertRaisesRegex(ValueError, 'Caller-verified source SHA-256'):
            self.build(source_sha256='0' * 64)
        for mutate, message in (
            (lambda x: x['canvas_config'].__setitem__('width', 1920), '1280x720'),
            (lambda x: x['materials']['videos'][0].__setitem__('path', '/wrong.mp4'), 'source SHA'),
            (lambda x: x['materials']['videos'][0].__setitem__('duration', 9_000_000), 'source SHA'),
        ):
            base = base_timeline()
            mutate(base)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.build(base)

    def test_rejects_bad_timing_unknown_fields_and_resource_drift(self):
        for mutate, message in (
            (lambda x: x.__setitem__('duration', x['duration'] - 1), 'duration'),
            (lambda x: x['tracks'][0]['segments'][0]['source_timerange'].__setitem__('duration', 8_000_000), 'untrimmed 9-second'),
            (lambda x: x['tracks'][0]['segments'][0].__setitem__('mystery', 1), 'unsupported fields'),
            (lambda x: x['materials']['speeds'][0].__setitem__('mystery', 1), 'unsupported fields'),
            (lambda x: x['materials'].__setitem__('filters', []), 'unknown material buckets'),
            (lambda x: x['materials']['videos'][0].__setitem__('path', curve.SOURCE_PATH.replace(curve.SOURCE_SHA256, '0' * 64)), 'source SHA'),
        ):
            base = base_timeline()
            mutate(base)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.build(base)

    def test_rejects_ambiguous_or_dangling_speed_references(self):
        base = base_timeline()
        base['tracks'][0]['segments'][0]['extra_material_refs'][0] = uid()
        with self.assertRaisesRegex(ValueError, 'speed reference'):
            self.build(base)
        base = base_timeline()
        base['tracks'][0]['segments'][0]['extra_material_refs'].append(
            base['tracks'][0]['segments'][0]['extra_material_refs'][0])
        with self.assertRaisesRegex(ValueError, 'speed reference|every native'):
            self.build(base)

    def test_rejects_nonidentity_processing_in_captured_base(self):
        for mutate, message in (
            (lambda x: x['tracks'][0]['segments'][0]['clip']['transform'].__setitem__('x', .1),
             'unreviewed visual'),
            (lambda x: x['materials']['videos'][0].__setitem__('is_set_beauty_mode', False),
             'unreviewed processing'),
            (lambda x: x['materials']['canvases'][0].__setitem__('type', 'custom'),
             'unreviewed processing'),
        ):
            base = base_timeline()
            mutate(base)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.build(base)

    def test_builder_and_validator_reject_base_numeric_type_coercions(self):
        mutations = (
            ('color space bool', lambda x: x.__setitem__('color_space', False)),
            ('HDR mode bool', lambda x: x['tracks'][0]['segments'][0]['hdr_settings'].__setitem__('mode', True)),
            ('canvas width float', lambda x: x['canvas_config'].__setitem__('width', 1280.0)),
            ('platform app id bool', lambda x: x['platform'].__setitem__('app_id', True)),
            ('video check flag float', lambda x: x['materials']['videos'][0].__setitem__('check_flag', 62978047.0)),
        )
        for name, mutate in mutations:
            valid_base = base_timeline()
            candidate = self.build(valid_base)
            malformed_base = deepcopy(valid_base)
            mutate(malformed_base)
            with self.subTest(name=name, entrypoint='builder'), self.assertRaises(ValueError):
                self.build(malformed_base)
            with self.subTest(name=name, entrypoint='validator'), self.assertRaises(ValueError):
                curve.validate_curve_candidate(
                    malformed_base, candidate, runtime_profile=PROFILE_1140_BUILD481,
                    source_fps=30, source_sha256=curve.SOURCE_SHA256)

    def test_validator_accepts_builder_candidate_without_calling_builder(self):
        base = base_timeline()
        before = deepcopy(base)
        candidate = self.build(base)
        with patch.object(curve, 'build_curve_profile', side_effect=AssertionError('random builder called')):
            result = curve.validate_curve_candidate(
                base, candidate, runtime_profile=PROFILE_1140_BUILD481,
                source_fps=30, source_sha256=curve.SOURCE_SHA256)
        self.assertEqual(result['profile_id'], 'b481-custom-five-point-v1')
        self.assertEqual(result['speed_material_id'], candidate['materials']['speeds'][0]['id'])
        self.assertEqual(result['source_duration_us'], curve.SOURCE_DURATION_US)
        self.assertEqual(result['target_duration_us'], curve.TARGET_DURATION_US)
        self.assertTrue(curve._strict_graph_equal(base, before))

    def test_validator_rejects_scalar_cold_reopen_and_python_numeric_type_coercions(self):
        mutations = (
            ('speed material bool mode',
             lambda x: x['materials']['speeds'][0].__setitem__('mode', True)),
            ('speed material float mode',
             lambda x: x['materials']['speeds'][0].__setitem__('mode', 1.0)),
            ('speed material bool scalar',
             lambda x: x['materials']['speeds'][0].__setitem__('speed', True)),
            ('speed material int scalar',
             lambda x: x['materials']['speeds'][0].__setitem__('speed', 1)),
            ('speed material float scalar',
             lambda x: x['materials']['speeds'][0].__setitem__('speed', 1.0)),
            ('segment bool scalar',
             lambda x: x['tracks'][0]['segments'][0].__setitem__('speed', True)),
            ('segment int scalar',
             lambda x: x['tracks'][0]['segments'][0].__setitem__('speed', 1)),
            ('segment float scalar',
             lambda x: x['tracks'][0]['segments'][0].__setitem__('speed', 1.0)),
            ('cold reopen scalar',
             lambda x: x['materials']['speeds'][0].__setitem__('speed', 1.4594596172388776)),
            ('cold reopen segment scalar',
             lambda x: x['tracks'][0]['segments'][0].__setitem__('speed', 1.4594596172388776)),
            ('bool point coordinate',
             lambda x: x['materials']['speeds'][0]['curve_speed']['speed_points'][1].__setitem__('y', True)),
        )
        for name, mutate in mutations:
            base = base_timeline()
            before = deepcopy(base)
            candidate = self.build(base)
            mutate(candidate)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'differs from the exact'):
                curve.validate_curve_candidate(
                    base, candidate, runtime_profile=PROFILE_1140_BUILD481,
                    source_fps=30, source_sha256=curve.SOURCE_SHA256)
            self.assertTrue(curve._strict_graph_equal(base, before))

    def test_validator_rejects_graph_identity_reference_duration_and_point_changes(self):
        mutations = (
            ('speed material id', lambda x: x['materials']['speeds'][0].__setitem__('id', uid())),
            ('speed ref', lambda x: x['tracks'][0]['segments'][0]['extra_material_refs'].__setitem__(0, uid())),
            ('timeline duration', lambda x: x.__setitem__('duration', curve.TARGET_DURATION_US + 1)),
            ('segment duration', lambda x: x['tracks'][0]['segments'][0]['target_timerange'].__setitem__('duration', curve.TARGET_DURATION_US + 1)),
            ('curve point', lambda x: x['materials']['speeds'][0]['curve_speed']['speed_points'][2].__setitem__('y', 4.0)),
        )
        for name, mutate in mutations:
            base = base_timeline()
            candidate = self.build(base)
            mutate(candidate)
            with self.subTest(name=name), self.assertRaises(ValueError):
                curve.validate_curve_candidate(
                    base, candidate, runtime_profile=PROFILE_1140_BUILD481,
                    source_fps=30, source_sha256=curve.SOURCE_SHA256)

    def test_validator_rejects_reused_or_noncanonical_speed_id(self):
        for replacement_kind in ('malformed', 'lowercase', 'reused'):
            base = base_timeline()
            candidate = self.build(base)
            old_id = candidate['materials']['speeds'][0]['id']
            replacement = {
                'malformed': 'not-a-uuid',
                'lowercase': str(uuid.uuid4()),
                'reused': base['id'],
            }[replacement_kind]
            candidate['materials']['speeds'][0]['id'] = replacement
            refs = candidate['tracks'][0]['segments'][0]['extra_material_refs']
            refs[refs.index(old_id)] = replacement
            with self.subTest(replacement_kind=replacement_kind), self.assertRaises(ValueError):
                curve.validate_curve_candidate(
                    base, candidate, runtime_profile=PROFILE_1140_BUILD481,
                    source_fps=30, source_sha256=curve.SOURCE_SHA256)


if __name__ == '__main__':
    unittest.main()
