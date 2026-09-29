"""Self-contained structural tests for the Build 481 HSL graph experiment."""
from copy import deepcopy
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import native_adjustments as adjustments
import native_resources
from runtime_profiles import PROFILE_1140_BUILD481


def uid():
    return str(uuid.uuid4()).upper()


def video_material():
    return {
        'beauty_face_auto_preset': {}, 'category_name': 'local', 'check_flag': 62978047,
        'crop': {}, 'duration': 3_000_000, 'height': 720, 'id': uid(),
        'is_set_beauty_mode': True, 'local_material_id': uid(), 'material_id': '',
        'material_name': 'fixture.mp4', 'matting': {'path': ''},
        'path': adjustments.HSL_MEDIA_PATH, 'stable': {'time_range': {}},
        'type': 'video', 'video_algorithm': {'path': '', 'story_video_modify_video_config': {}},
        'video_mask_shadow': {'resource_id': '', 'path': ''},
        'video_mask_stroke': {'resource_id': '', 'path': '', 'type': ''},
        'width': 1280,
    }


def timeline_fixture(*, captured):
    video_node = video_material()
    video_id = video_node['id']
    extras = [uid() for _ in range(6)]
    video_segment = {
        'clip': {'scale': {'x': 1.0, 'y': 1.0}, 'transform': {'x': 0.0, 'y': 0.0}, 'flip': {}},
        'enable_adjust_mask': False, 'enable_hsl': False, 'extra_material_refs': extras,
        'hdr_settings': {'mode': 1}, 'id': uid(), 'material_id': video_id,
        'render_timerange': {}, 'responsive_layout': {}, 'source': 'segmentsourcenormal',
        'source_timerange': {'duration': adjustments.HSL_DURATION_US},
        'target_timerange': {'duration': adjustments.HSL_DURATION_US},
        'uniform_scale': {}, 'volume': 0.0,
    }
    tracks = [{'id': uid(), 'name': 'Main', 'segments': [video_segment], 'type': 'video'}]
    materials = {
        'videos': [video_node], 'canvases': [{'id': extras[1], 'type': 'canvas_color'}],
        'placeholders': [],
        'placeholder_infos': [{'id': extras[0], 'meta_type': 'none', 'type': 'placeholder_info'}],
        'speeds': [{'id': extras[2], 'type': 'speed'}], 'hsl': [],
        'sound_channel_mappings': [{'id': extras[3], 'type': 'none'}],
        'material_colors': [{'id': extras[4]}],
        'vocal_separations': [{'id': extras[5], 'type': 'vocal_separation'}],
    }
    if captured:
        placeholder_id = uid()
        hsl_id = uid()
        materials['placeholders'] = [{'id': placeholder_id, 'name': '调整1', 'type': 'adjust'}]
        materials['hsl'] = [{
            'constant_material_id': uid(), 'custom_color': '#FFE64444', 'hsl_color_type': 1,
            'id': hsl_id, 'interacting': True, 'lumi_hub_path': '/captured/cache/lumi_hub_path',
            'path': '/captured/cache', 'resource_id': adjustments.HSL_RESOURCE_ID,
            'saturation': -50, 'source_platform': 1, 'type': 'hsl', 'version': '1',
        }]
        adjust_segment = {
            'extra_material_refs': [hsl_id], 'id': uid(), 'material_id': placeholder_id,
            'render_timerange': {}, 'responsive_layout': {}, 'source': 'segmentsourcenormal',
            'target_timerange': {'duration': adjustments.HSL_DURATION_US}, 'track_render_index': 1,
        }
        tracks.append({'id': uid(), 'is_default_name': True,
                       'segments': [adjust_segment], 'type': 'adjust'})
    return {
        'canvas_config': {'width': 1280, 'height': 720}, 'color_space': 0, 'config': {},
        'duration': adjustments.HSL_DURATION_US, 'function_assistant_info': {}, 'id': uid(),
        'keyframes': {'videos': [], 'audios': [], 'texts': [], 'stickers': [], 'filters': []},
        'last_modified_platform': {}, 'materials': materials, 'new_version': '185.0.0',
        'path': '', 'platform': {'os': 'mac'}, 'render_index_track_mode_on': False,
        'smart_ads_info': {}, 'tracks': tracks, 'uneven_animation_template_info': {},
        'version': 360000,
    }


class Build481OfflineAdjustmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'draft'
        self.cache = self.root / 'Resources/hsl-cache' / adjustments.HSL_CACHE_DIR
        self.media = self.root / 'Resources/headless-media' / (adjustments.HSL_MEDIA_SHA256 + '.mp4')
        self.cache.mkdir(parents=True)
        (self.cache / 'lumi_hub_path').mkdir()
        self.media.parent.mkdir(parents=True)
        self.media.write_bytes(b'synthetic test source; hash is patched')
        self.base = timeline_fixture(captured=False)
        self.captured = timeline_fixture(captured=True)
        self.media_hash_patch = patch.object(adjustments, '_sha256_file',
                                             return_value=adjustments.HSL_MEDIA_SHA256)
        self.cache_patch = patch.object(adjustments, 'verify_hsl_cache', return_value={
            'resource_id': adjustments.HSL_RESOURCE_ID,
            'tree_sha256': adjustments.HSL_CACHE_TREE_SHA256,
            'file_count': adjustments.HSL_CACHE_FILE_COUNT,
            'path': str(self.cache),
        })

    def tearDown(self):
        self.temp.cleanup()

    def build(self, base=None, template=None, runtime=PROFILE_1140_BUILD481):
        with self.media_hash_patch, self.cache_patch:
            return adjustments.add_hsl_adjustment_layer(
                deepcopy(self.base if base is None else base),
                deepcopy(self.captured if template is None else template),
                draft_root=self.root, cache_root=self.cache, runtime_profile=runtime)

    def test_builds_captured_overlay_and_preserves_both_inputs(self):
        base_before, template_before = deepcopy(self.base), deepcopy(self.captured)
        result = self.build()
        with self.media_hash_patch, self.cache_patch:
            evidence = adjustments.verify_hsl_adjustment_timeline(result, self.cache)
        self.assertEqual(evidence['status'], 'offline-graph-verified-semantic-gate-closed')
        self.assertEqual(evidence['hsl'], 'red.saturation=-50')
        self.assertEqual(evidence['duration_us'], 2_000_000)
        self.assertEqual([track['type'] for track in result['tracks']], ['video', 'adjust'])
        self.assertEqual(self.base, base_before)
        self.assertEqual(self.captured, template_before)
        self.assertNotIn(result['tracks'][1]['id'], adjustments._all_ids(self.captured))

    def test_placeholder_uuid_may_change_when_segment_reference_closes(self):
        result = self.build()
        adjust = result['tracks'][1]['segments'][0]
        placeholder = result['materials']['placeholders'][0]
        placeholder['id'] = uid()
        adjust['material_id'] = placeholder['id']
        with self.media_hash_patch, self.cache_patch:
            evidence = adjustments.verify_hsl_adjustment_timeline(result, self.cache)
        self.assertEqual(evidence['placeholder_id'], placeholder['id'])

    def test_rejects_other_runtime_or_non_two_second_timeline(self):
        with self.assertRaisesRegex(ValueError, 'pinned to Jianying 11.4.0 Build 481'):
            self.build(runtime='jy14-headless-macos-11.4.2')
        result = self.build()
        result['duration'] += 1
        with self.media_hash_patch, self.cache_patch, self.assertRaisesRegex(ValueError, 'timeline duration'):
            adjustments.verify_hsl_adjustment_timeline(result, self.cache)

    def test_rejects_timing_parameter_and_unknown_field_drift(self):
        base = deepcopy(self.base)
        base['tracks'][0]['segments'][0]['target_timerange']['duration'] -= 1
        with self.assertRaisesRegex(ValueError, 'target_timerange'):
            self.build(base=base)
        template = deepcopy(self.captured)
        template['materials']['hsl'][0]['saturation'] = -49
        with self.assertRaisesRegex(ValueError, 'exact red HSL -50'):
            self.build(template=template)
        template = deepcopy(self.captured)
        template['materials']['hsl'][0]['interacting'] = False
        with self.assertRaisesRegex(ValueError, 'exact red HSL -50'):
            self.build(template=template)
        template = deepcopy(self.captured)
        template['materials']['hsl'][0]['opaque_unreviewed_value'] = {'enabled': True}
        with self.assertRaisesRegex(ValueError, 'unsupported fields'):
            self.build(template=template)

    def test_rejects_unknown_nonempty_resource_buckets_and_extra_segments(self):
        base = deepcopy(self.base)
        base['materials']['unknown_resource'] = [{'id': uid()}]
        with self.assertRaisesRegex(ValueError, 'unknown material buckets'):
            self.build(base=base)
        template = deepcopy(self.captured)
        template['tracks'][1]['segments'].append(deepcopy(template['tracks'][1]['segments'][0]))
        with self.assertRaisesRegex(ValueError, 'exactly one segment'):
            self.build(template=template)

    def test_rejects_wrong_video_sha_path_or_bytes(self):
        base = deepcopy(self.base)
        base['materials']['videos'][0]['path'] = '/unrelated/video.mp4'
        with self.assertRaisesRegex(ValueError, 'source SHA-256'):
            self.build(base=base)
        with patch.object(adjustments, '_sha256_file', return_value='0' * 64), self.cache_patch:
            with self.assertRaisesRegex(ValueError, 'source video bytes'):
                adjustments.add_hsl_adjustment_layer(
                    self.base, self.captured, draft_root=self.root, cache_root=self.cache,
                    runtime_profile=PROFILE_1140_BUILD481)

    def test_rejects_nonclosed_placeholder_and_duplicate_constant_id(self):
        result = self.build()
        result['tracks'][1]['segments'][0]['material_id'] = uid()
        with self.media_hash_patch, self.cache_patch, self.assertRaisesRegex(ValueError, 'dangling material reference'):
            adjustments.verify_hsl_adjustment_timeline(result, self.cache)
        result = self.build()
        result['materials']['hsl'][0]['constant_material_id'] = result['materials']['hsl'][0]['id']
        with self.media_hash_patch, self.cache_patch, self.assertRaisesRegex(ValueError, 'aliases|identities are not unique'):
            adjustments.verify_hsl_adjustment_timeline(result, self.cache)

    def test_cache_verifier_accepts_only_pinned_inventory(self):
        inventory = {'file-%03d.bin' % i: {'sha256': 'a' * 64, 'size': i + 1}
                     for i in range(adjustments.HSL_CACHE_FILE_COUNT)}
        with patch.object(native_resources, 'tree_manifest', return_value=inventory), \
                patch.object(native_resources, 'manifest_hash',
                             return_value=adjustments.HSL_CACHE_TREE_SHA256):
            result = adjustments.verify_hsl_cache(self.cache)
        self.assertEqual(result['file_count'], 432)
        with patch.object(native_resources, 'tree_manifest', return_value=inventory), \
                patch.object(native_resources, 'manifest_hash', return_value='0' * 64), \
                self.assertRaisesRegex(ValueError, 'captured 432-file tree'):
            adjustments.verify_hsl_cache(self.cache)


if __name__ == '__main__':
    unittest.main()
