"""Narrow Build 481 HSL graph experiment for one captured adjustment layer.

This structural experiment only adds a captured adjustment graph to an
in-memory timeline. It is not a formal plan/build/publish interface, does not
write a draft, register it, launch Jianying, or authorize export. The caller
must already have copied the pinned media and HSL cache into an isolated draft.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import uuid

import native_resources as resources
from runtime_profiles import PROFILE_1140_BUILD481


HSL_RESOURCE_ID = '7416258989467374091'
HSL_CACHE_DIR = '2a5048e9c3ab6d08ecd65fd781d276d5'
HSL_CACHE_TREE_SHA256 = '863935506f672590ce8ab8fe0ef413ede8b95e67dfc4c33d055bc7689736cb55'
HSL_CACHE_FILE_COUNT = 432
HSL_DURATION_US = 2_000_000
HSL_MEDIA_SHA256 = 'd2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16'
HSL_MEDIA_PATH = ('##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/'
                  'Resources/headless-media/' + HSL_MEDIA_SHA256 + '.mp4')
TIMELINE_FIELDS = {
    'canvas_config', 'color_space', 'config', 'duration', 'function_assistant_info',
    'id', 'keyframes', 'last_modified_platform', 'materials', 'new_version', 'path',
    'platform', 'render_index_track_mode_on', 'smart_ads_info', 'tracks', 'uneven_animation_template_info', 'version',
}
VIDEO_TRACK_FIELDS = {'id', 'name', 'segments', 'type'}
ADJUST_TRACK_FIELDS = {'id', 'is_default_name', 'segments', 'type'}
VIDEO_SEGMENT_FIELDS = {
    'clip', 'enable_adjust_mask', 'enable_hsl', 'extra_material_refs', 'hdr_settings',
    'id', 'material_id', 'render_timerange', 'responsive_layout', 'source',
    'source_timerange', 'target_timerange', 'uniform_scale', 'volume',
}
ADJUST_SEGMENT_FIELDS = {
    'extra_material_refs', 'id', 'material_id', 'render_timerange',
    'responsive_layout', 'source', 'target_timerange', 'track_render_index',
}
PLACEHOLDER_FIELDS = {'id', 'name', 'type'}
HSL_MATERIAL_FIELDS = {
    'constant_material_id', 'custom_color', 'hsl_color_type', 'id', 'interacting',
    'lumi_hub_path', 'path', 'resource_id', 'saturation', 'source_platform', 'type', 'version',
}
MATERIAL_FIELDS = {
    'videos': {'beauty_face_auto_preset', 'category_name', 'check_flag', 'crop', 'duration',
               'height', 'id', 'is_set_beauty_mode', 'local_material_id', 'material_id',
               'material_name', 'matting', 'path', 'stable', 'type', 'video_algorithm',
               'video_mask_shadow', 'video_mask_stroke', 'width'},
    'canvases': {'id', 'type'},
    'placeholders': PLACEHOLDER_FIELDS,
    'placeholder_infos': {'id', 'meta_type', 'type'},
    'speeds': {'id', 'type'},
    'hsl': HSL_MATERIAL_FIELDS,
    'sound_channel_mappings': {'id', 'type'},
    'material_colors': {'id'},
    'vocal_separations': {'id', 'type'},
}
MATERIAL_BUCKET_COUNTS_BASE = {
    'videos': 1, 'canvases': 1, 'placeholders': 0, 'placeholder_infos': 1,
    'speeds': 1, 'hsl': 0, 'sound_channel_mappings': 1, 'material_colors': 1,
    'vocal_separations': 1,
}
MATERIAL_BUCKET_COUNTS_CAPTURE = {**MATERIAL_BUCKET_COUNTS_BASE, 'placeholders': 1, 'hsl': 1}
HSL_EXPECTED_FIELDS = {
    'type': 'hsl',
    'resource_id': HSL_RESOURCE_ID,
    'hsl_color_type': 1,
    'custom_color': '#FFE64444',
    'saturation': -50,
    'source_platform': 1,
    'interacting': True,
    'version': '1',
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _exact_keys(value, expected, message):
    _require(isinstance(value, dict) and set(value) == expected, message)


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _verify_source_media(video_material, draft_root):
    _require(video_material.get('path') == HSL_MEDIA_PATH,
             'Video material path does not identify the captured source SHA-256')
    media = Path(draft_root) / 'Resources/headless-media' / (HSL_MEDIA_SHA256 + '.mp4')
    _require(media.is_file() and not media.is_symlink(), 'Pinned source video is missing or unsafe')
    _require(_sha256_file(media) == HSL_MEDIA_SHA256,
             'Pinned source video bytes do not match the captured SHA-256')


def _validate_graph_shape(timeline, *, captured):
    _exact_keys(timeline, TIMELINE_FIELDS, 'Timeline contains unsupported fields')
    _require(type(timeline.get('duration')) is int and timeline['duration'] == HSL_DURATION_US,
             'Build 481 HSL timeline duration must be exactly 2 seconds')
    tracks = timeline.get('tracks', [])
    wanted_types = ['video', 'adjust'] if captured else ['video']
    _require([track.get('type') for track in tracks] == wanted_types,
             'Timeline contains unsupported tracks')
    video_track = _one_track(timeline, 'video')
    _exact_keys(video_track, VIDEO_TRACK_FIELDS, 'Video track contains unsupported fields')
    _exact_keys(video_track['segments'][0], VIDEO_SEGMENT_FIELDS,
                'Video segment contains unsupported fields')
    materials = timeline.get('materials')
    _require(isinstance(materials, dict) and set(materials) == set(MATERIAL_BUCKET_COUNTS_BASE),
             'Timeline contains unknown material buckets')
    expected_counts = MATERIAL_BUCKET_COUNTS_CAPTURE if captured else MATERIAL_BUCKET_COUNTS_BASE
    _require({key: len(value) if isinstance(value, list) else -1 for key, value in materials.items()}
             == expected_counts, 'Timeline contains unsupported resource materials')
    for bucket, nodes in materials.items():
        for node in nodes:
            _exact_keys(node, MATERIAL_FIELDS[bucket],
                        'Material in %s contains unsupported fields' % bucket)
    index = _material_index(timeline)
    for track in tracks:
        for segment in track.get('segments', []):
            refs = [segment.get('material_id')] + segment.get('extra_material_refs', [])
            _require(all(ref in index for ref in refs), 'Timeline contains a dangling material reference')
    if captured:
        adjust_track = _one_track(timeline, 'adjust')
        _exact_keys(adjust_track, ADJUST_TRACK_FIELDS, 'Adjust track contains unsupported fields')
        _exact_keys(adjust_track['segments'][0], ADJUST_SEGMENT_FIELDS,
                    'Adjust segment contains unsupported fields')
        _exact_keys(materials['placeholders'][0], PLACEHOLDER_FIELDS,
                    'Adjustment placeholder contains unsupported fields')
        _exact_keys(materials['hsl'][0], HSL_MATERIAL_FIELDS,
                    'Captured HSL material contains unsupported fields')


def _material_index(timeline):
    result = {}
    for bucket, nodes in timeline.get('materials', {}).items():
        _require(isinstance(nodes, list), 'Unexpected native materials container')
        for node in nodes:
            _require(isinstance(node, dict) and isinstance(node.get('id'), str) and node['id'],
                     'Malformed native material')
            _require(node['id'] not in result, 'Duplicate native material identity')
            result[node['id']] = (bucket, node)
    return result


def _all_ids(timeline):
    found = []
    timeline_id = timeline.get('id')
    _require(isinstance(timeline_id, str) and timeline_id, 'Malformed timeline identity')
    found.append(timeline_id)
    index = _material_index(timeline)
    found.extend(index)
    for bucket, node in index.values():
        if bucket == 'videos' and node.get('local_material_id'):
            _require(isinstance(node['local_material_id'], str), 'Malformed media-library identity')
            found.append(node['local_material_id'])
        if bucket == 'hsl' and node.get('constant_material_id'):
            _require(isinstance(node['constant_material_id'], str), 'Malformed HSL constant identity')
            found.append(node['constant_material_id'])
    for track in timeline.get('tracks', []):
        _require(isinstance(track.get('id'), str) and track['id'], 'Malformed track identity')
        _require(track.get('id') not in found, 'Duplicate track identity')
        found.append(track['id'])
        for segment in track.get('segments', []):
            _require(isinstance(segment.get('id'), str) and segment['id'], 'Malformed segment identity')
            _require(segment.get('id') not in found, 'Duplicate segment identity')
            found.append(segment['id'])
    return found


def _new_id(used):
    while True:
        value = str(uuid.uuid4()).upper()
        if value not in used:
            used.add(value)
            return value


def _one_track(timeline, kind):
    tracks = [track for track in timeline.get('tracks', []) if track.get('type') == kind]
    _require(len(tracks) == 1, 'Expected exactly one %s track' % kind)
    _require(len(tracks[0].get('segments', [])) == 1,
             'Expected exactly one segment on %s track' % kind)
    return tracks[0]


def _range(segment, field, start, duration):
    value = segment.get(field)
    actual_start = value.get('start', 0) if isinstance(value, dict) else None
    actual_duration = value.get('duration') if isinstance(value, dict) else None
    _require(isinstance(value, dict) and type(actual_start) is int and actual_start == start
             and type(actual_duration) is int and actual_duration == duration,
             'Unsupported HSL %s range' % field)


def verify_hsl_cache(cache_root):
    """Require the complete captured Build 481 cache tree, including no extras."""
    root = Path(cache_root)
    _require(root.name == HSL_CACHE_DIR, 'Unexpected Build 481 HSL cache identity')
    _require(not root.is_symlink(), 'Build 481 HSL cache root must not be a symlink')
    actual = resources.tree_manifest(root)
    _require(len(actual) == HSL_CACHE_FILE_COUNT
             and resources.manifest_hash(actual) == HSL_CACHE_TREE_SHA256,
             'Build 481 HSL cache differs from the captured 432-file tree')
    return {'resource_id': HSL_RESOURCE_ID, 'tree_sha256': HSL_CACHE_TREE_SHA256,
            'file_count': HSL_CACHE_FILE_COUNT, 'path': str(root.resolve())}


def verify_hsl_adjustment_timeline(timeline, cache_root):
    """Validate the single supported composition, including closed UUID rebinding."""
    _require(isinstance(timeline, dict), 'Timeline must be an object')
    _validate_graph_shape(timeline, captured=True)
    _require(type(timeline.get('duration')) is int and timeline['duration'] == HSL_DURATION_US,
             'Build 481 HSL timeline duration must be exactly 2 seconds')
    tracks = timeline.get('tracks', [])
    _require([track.get('type') for track in tracks] == ['video', 'adjust'],
             'Build 481 HSL composition must contain one video and one adjust track')
    video_track = _one_track(timeline, 'video')
    adjust_track = _one_track(timeline, 'adjust')
    video = video_track['segments'][0]
    adjust = adjust_track['segments'][0]
    _require(adjust_track.get('is_default_name') is True
             and adjust.get('track_render_index') == 1
             and adjust.get('render_timerange') == {}
             and adjust.get('responsive_layout') == {}
             and adjust.get('source') == 'segmentsourcenormal',
             'Captured adjustment track fields changed')
    _range(video, 'source_timerange', 0, HSL_DURATION_US)
    _range(video, 'target_timerange', 0, HSL_DURATION_US)
    _range(adjust, 'target_timerange', 0, HSL_DURATION_US)
    index = _material_index(timeline)
    _require(len(timeline.get('materials', {}).get('placeholders', [])) == 1
             and len(timeline.get('materials', {}).get('hsl', [])) == 1,
             'Build 481 HSL composition must contain one placeholder and one HSL material')
    _require(len(timeline.get('materials', {}).get('videos', [])) == 1,
             'Build 481 HSL composition must contain exactly one video material')
    for track in tracks:
        for segment in track.get('segments', []):
            references = [segment.get('material_id')] + segment.get('extra_material_refs', [])
            _require(all(reference in index for reference in references),
                     'Timeline segment contains a dangling material reference')
    _require(video.get('material_id') in index and index[video['material_id']][0] == 'videos',
             'Video segment material reference is invalid')
    source_duration = index[video['material_id']][1].get('duration')
    _require(type(source_duration) is int and source_duration == 3_000_000,
             'Only the captured 3-second source video is accepted')
    cache_input = Path(cache_root)
    _require(not cache_input.is_symlink(), 'Build 481 HSL cache root must not be a symlink')
    cache = cache_input.resolve(strict=True)
    draft_root = cache.parents[2]
    _verify_source_media(index[video['material_id']][1], draft_root)
    _require(len(adjust.get('extra_material_refs', [])) == 1,
             'Adjust segment must reference one HSL material')
    placeholder = index.get(adjust.get('material_id'))
    hsl = index.get(adjust['extra_material_refs'][0])
    _require(placeholder is not None and placeholder[0] == 'placeholders'
             and placeholder[1].get('type') == 'adjust'
             and placeholder[1].get('name') == '调整1',
             'Adjust placeholder reference is invalid')
    _require(hsl is not None and hsl[0] == 'hsl', 'Adjust HSL reference is invalid')
    node = hsl[1]
    _require(all(node.get(key) == value for key, value in HSL_EXPECTED_FIELDS.items()),
             'Unsupported Build 481 HSL parameter or resource identity')
    constant_id = node.get('constant_material_id')
    _require(isinstance(constant_id, str) and constant_id and constant_id != node['id'],
             'HSL constant material identity is missing or aliases its material ID')
    try:
        uuid.UUID(constant_id)
    except (ValueError, AttributeError, TypeError) as error:
        raise ValueError('HSL constant material identity is not a UUID') from error
    _require(node.get('path') == str(cache)
             and node.get('lumi_hub_path') == str(cache / 'lumi_hub_path')
             and (cache / 'lumi_hub_path').is_dir(),
             'HSL resource paths do not resolve to the staged draft cache')
    ids = _all_ids(timeline)
    _require(len(ids) == len(set(ids)), 'Native graph identities are not unique')
    verify_hsl_cache(cache)
    return {'status': 'offline-graph-verified-semantic-gate-closed',
            'profile': PROFILE_1140_BUILD481, 'hsl': 'red.saturation=-50',
            'duration_us': HSL_DURATION_US, 'placeholder_id': adjust['material_id'],
            'hsl_material_id': node['id'],
            'hsl_constant_material_id': node['constant_material_id'],
            'cache_tree_sha256': HSL_CACHE_TREE_SHA256}


def add_hsl_adjustment_layer(base_timeline, captured_template, *, draft_root,
                             cache_root, runtime_profile):
    """Build the one evidence-backed HSL layer on a single captured video.

    This is a data-only constructor. It accepts only the exact Build 481
    composition evidenced by the isolated GUI capture. It does not enable any
    runtime capability and never mutates its inputs.
    """
    _require(runtime_profile == PROFILE_1140_BUILD481,
             'HSL adjustment constructor is pinned to Jianying 11.4.0 Build 481')
    _require(isinstance(base_timeline, dict) and isinstance(captured_template, dict),
             'Base and captured template timelines are required')
    _require(base_timeline.get('new_version') == '185.0.0'
             and base_timeline.get('version') == 360000
             and captured_template.get('new_version') == '185.0.0'
             and captured_template.get('version') == 360000,
             'Unsupported Build 481 timeline schema')
    _validate_graph_shape(base_timeline, captured=False)
    _validate_graph_shape(captured_template, captured=True)
    _require([track.get('type') for track in base_timeline.get('tracks', [])] == ['video'],
             'Base timeline must contain exactly one video track')
    _require(not base_timeline.get('materials', {}).get('hsl')
             and not base_timeline.get('materials', {}).get('placeholders'),
             'Base timeline already contains a resource-backed adjustment graph')
    base_video = _one_track(base_timeline, 'video')['segments'][0]
    _range(base_video, 'source_timerange', 0, HSL_DURATION_US)
    _range(base_video, 'target_timerange', 0, HSL_DURATION_US)
    _require([track.get('type') for track in captured_template.get('tracks', [])] == ['video', 'adjust'],
             'Captured template must contain one video and one adjust track')
    template_adjust = _one_track(captured_template, 'adjust')
    template_segment = template_adjust['segments'][0]
    template_video = _one_track(captured_template, 'video')['segments'][0]
    _range(template_video, 'source_timerange', 0, HSL_DURATION_US)
    _range(template_video, 'target_timerange', 0, HSL_DURATION_US)
    _range(template_segment, 'target_timerange', 0, HSL_DURATION_US)
    template_index = _material_index(captured_template)
    _require(len(template_segment.get('extra_material_refs', [])) == 1,
             'Captured adjust segment must have exactly one extra reference')
    old_hsl = template_index.get(template_segment['extra_material_refs'][0])
    old_placeholder = template_index.get(template_segment.get('material_id'))
    _require(len(captured_template.get('materials', {}).get('hsl', [])) == 1
             and len(captured_template.get('materials', {}).get('placeholders', [])) == 1,
             'Captured template must contain one HSL node and one adjustment placeholder')
    _require(old_hsl is not None and old_hsl[0] == 'hsl'
             and old_placeholder is not None and old_placeholder[0] == 'placeholders',
             'Captured adjust graph references are incomplete')
    _require(all(old_hsl[1].get(key) == value for key, value in HSL_EXPECTED_FIELDS.items()),
             'Captured template does not contain the exact red HSL -50 resource')
    cache_input = Path(cache_root)
    root_input = Path(draft_root)
    _require(not cache_input.is_symlink() and not root_input.is_symlink(),
             'Draft and HSL cache roots must not be symlinks')
    cache = cache_input.resolve(strict=True)
    root = root_input.resolve(strict=True)
    _require(cache == root / 'Resources' / 'hsl-cache' / HSL_CACHE_DIR,
             'HSL cache must be the pinned draft-local cache path')
    base_index = _material_index(base_timeline)
    _verify_source_media(base_index[base_video['material_id']][1], root)
    _verify_source_media(template_index[template_video['material_id']][1], root)
    verify_hsl_cache(cache)

    result = deepcopy(base_timeline)
    used = set(_all_ids(result)) | set(_all_ids(captured_template))
    adjust_track = deepcopy(template_adjust)
    segment = adjust_track['segments'][0]
    placeholder = deepcopy(old_placeholder[1])
    hsl = deepcopy(old_hsl[1])
    adjust_track['id'] = _new_id(used)
    segment['id'] = _new_id(used)
    placeholder['id'] = _new_id(used)
    hsl['id'] = _new_id(used)
    # GUI saves can regenerate this placeholder UUID. Its owning segment must
    # follow the generated identity; the HSL resource/constant IDs stay distinct.
    segment['material_id'] = placeholder['id']
    segment['extra_material_refs'] = [hsl['id']]
    hsl['constant_material_id'] = _new_id(used)
    hsl['path'] = str(cache)
    hsl['lumi_hub_path'] = str(cache / 'lumi_hub_path')
    result.setdefault('materials', {}).setdefault('placeholders', []).append(placeholder)
    result['materials'].setdefault('hsl', []).append(hsl)
    result['tracks'].append(adjust_track)
    verify_hsl_adjustment_timeline(result, cache)
    return result
