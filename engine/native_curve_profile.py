"""Offline constructor for the single captured Build 481 curve profile.

This is deliberately not a plan, build, publish, or export entry point. It
accepts one exact 9-second 1x base timeline and returns a copied in-memory
timeline carrying the one cold-reopened GUI curve sample.
"""
from copy import deepcopy
import uuid

from runtime_profiles import PROFILE_1140_BUILD481


SOURCE_SHA256 = '5e6d2dbed08aa8d193ce983243284ab0014f7f4de3cb90a3d86de7199cfa9032'
SOURCE_PATH = ('##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/'
               'Resources/headless-media/' + SOURCE_SHA256 + '.mp4')
SOURCE_NAME = 'timecode-24s.mp4'
SOURCE_DURATION_US = 9_000_000
TARGET_DURATION_US = 6_166_666
SOURCE_FPS = 30
CURVE_SCALAR = 1.4576270189136267
CURVE_ID = '6768730851543880206'
CURVE_NAME = '自定义'
CURVE_POINTS = [
    {'x': 0.0, 'y': 1.0},
    {'x': 0.25, 'y': 1.0},
    {'x': 0.5, 'y': 4.375},
    {'x': 0.75, 'y': 1.0},
    {'x': 1.0, 'y': 1.0},
]

TIMELINE_FIELDS = {
    'canvas_config', 'color_space', 'config', 'duration', 'function_assistant_info',
    'id', 'keyframes', 'last_modified_platform', 'materials', 'new_version', 'path',
    'platform', 'render_index_track_mode_on', 'smart_ads_info', 'tracks',
    'uneven_animation_template_info', 'version',
}
VIDEO_TRACK_FIELDS = {'id', 'name', 'segments', 'type'}
VIDEO_SEGMENT_FIELDS = {
    'clip', 'enable_adjust_mask', 'enable_hsl', 'extra_material_refs', 'hdr_settings',
    'id', 'material_id', 'render_timerange', 'responsive_layout', 'source',
    'source_timerange', 'target_timerange', 'uniform_scale',
}
MATERIAL_FIELDS = {
    'videos': {'beauty_face_auto_preset', 'category_name', 'check_flag', 'crop',
               'duration', 'height', 'id', 'is_set_beauty_mode', 'local_material_id',
               'material_id', 'material_name', 'matting', 'path', 'stable', 'type',
               'video_algorithm', 'video_mask_shadow', 'video_mask_stroke', 'width'},
    'canvases': {'id', 'type'},
    'placeholder_infos': {'id', 'meta_type', 'type'},
    'speeds': {'id', 'type'},
    'sound_channel_mappings': {'id', 'type'},
    'material_colors': {'id'},
    'vocal_separations': {'id', 'type'},
}
MATERIAL_BUCKET_COUNTS = {
    'videos': 1, 'canvases': 1, 'placeholder_infos': 1, 'speeds': 1,
    'sound_channel_mappings': 1, 'material_colors': 1, 'vocal_separations': 1,
}


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def _exact_keys(value, expected, message):
    _require(isinstance(value, dict) and set(value) == expected, message)


def _check_nested_schema(timeline, video, segment):
    _exact_keys(timeline['config'], set(), 'Timeline config contains unsupported fields')
    _exact_keys(timeline['function_assistant_info'], {'fps'},
                'Timeline assistant info contains unsupported fields')
    _exact_keys(timeline['function_assistant_info']['fps'], set(),
                'Timeline assistant fps contains unsupported fields')
    platform_fields = {'app_id', 'app_source', 'app_version', 'device_id', 'hard_disk_id',
                       'mac_address', 'os', 'os_version'}
    for field in ('last_modified_platform', 'platform'):
        _exact_keys(timeline[field], platform_fields,
                    'Timeline %s contains unsupported fields' % field)
        platform = timeline[field]
        _require(platform['app_id'] == 3704 and platform['app_source'] == 'lv'
                 and platform['app_version'] == '11.4.0' and platform['os'] == 'mac'
                 and all(isinstance(platform[key], str) and platform[key]
                         for key in ('device_id', 'hard_disk_id', 'mac_address', 'os_version')),
                 'Timeline platform identity does not match the captured Build 481 app')
    _exact_keys(timeline['smart_ads_info'], set(), 'Timeline ads info contains unsupported fields')
    _exact_keys(timeline['uneven_animation_template_info'], set(),
                'Timeline animation info contains unsupported fields')
    _exact_keys(timeline['keyframes'], set(), 'Timeline keyframes contain unsupported fields')
    _require(timeline['keyframes'] == {},
             'Curve profile does not accept timeline keyframes')
    _exact_keys(video['crop'], set(), 'Video crop contains unsupported fields')
    _exact_keys(video['stable'], {'time_range'}, 'Video stable metadata contains unsupported fields')
    _exact_keys(video['stable']['time_range'], set(),
                'Video stable time range contains unsupported fields')
    _exact_keys(video['matting'], {'path'}, 'Video matting contains unsupported fields')
    _exact_keys(video['video_algorithm'], {'path', 'story_video_modify_video_config'},
                'Video algorithm contains unsupported fields')
    _exact_keys(video['video_algorithm']['story_video_modify_video_config'], set(),
                'Video algorithm config contains unsupported fields')
    _exact_keys(video['video_mask_shadow'], {'resource_id', 'path'},
                'Video shadow resource contains unsupported fields')
    _exact_keys(video['video_mask_stroke'], {'resource_id', 'path', 'type'},
                'Video stroke resource contains unsupported fields')
    _exact_keys(segment['clip'], {'scale', 'transform', 'flip'},
                'Video clip contains unsupported fields')
    _exact_keys(segment['clip']['scale'], {'x', 'y'}, 'Video scale contains unsupported fields')
    _exact_keys(segment['clip']['transform'], {'x', 'y'},
                'Video transform contains unsupported fields')
    _exact_keys(segment['clip']['flip'], set(), 'Video flip contains unsupported fields')
    for field in ('render_timerange', 'responsive_layout', 'uniform_scale'):
        _exact_keys(segment[field], set(), 'Video %s contains unsupported fields' % field)
    _exact_keys(segment['hdr_settings'], {'mode'}, 'Video HDR settings contain unsupported fields')
    _require(segment['clip'] == {
        'flip': {}, 'scale': {'x': 1.0, 'y': 1.0},
        'transform': {'x': 0.0, 'y': 0.0},
    } and segment['enable_adjust_mask'] is False
             and segment['enable_hsl'] is False
             and segment['hdr_settings'] == {'mode': 1}
             and segment['source'] == 'segmentsourcenormal',
             'Base video segment has unreviewed visual or source state')
    _require(video['beauty_face_auto_preset'] == {}
             and video['category_name'] == 'local'
             and video['check_flag'] == 62978047
             and video['crop'] == {}
             and video['is_set_beauty_mode'] is True
             and video['material_id'] == ''
             and video['matting'] == {'path': ''}
             and video['stable'] == {'time_range': {}}
             and video['type'] == 'video'
             and video['video_algorithm'] == {
                 'path': '', 'story_video_modify_video_config': {}}
             and video['video_mask_shadow'] == {'path': '', 'resource_id': ''}
             and video['video_mask_stroke'] == {
                 'path': '', 'resource_id': '', 'type': ''},
             'Base video material has unreviewed processing state')


def _material_index(timeline):
    result = {}
    materials = timeline.get('materials')
    _require(isinstance(materials, dict), 'Timeline materials are malformed')
    for bucket, nodes in materials.items():
        _require(isinstance(nodes, list), 'Material bucket must be a list')
        for node in nodes:
            _require(isinstance(node, dict) and isinstance(node.get('id'), str) and node['id'],
                     'Malformed material identity')
            _require(node['id'] not in result, 'Duplicate material ID')
            result[node['id']] = (bucket, node)
    return result


def _validate_base(timeline, source_fps, source_sha256):
    _exact_keys(timeline, TIMELINE_FIELDS, 'Timeline contains unsupported fields')
    _require(timeline.get('new_version') == '185.0.0' and timeline.get('version') == 360000,
             'Curve profile is pinned to the Build 481 timeline schema')
    _require(type(source_fps) is int and source_fps == SOURCE_FPS,
             'Curve profile requires the captured 30 fps source')
    _require(source_sha256 == SOURCE_SHA256,
             'Caller-verified source SHA-256 does not match the captured media')
    _require(timeline.get('canvas_config') == {'width': 1280, 'height': 720},
             'Curve profile requires a 1280x720 canvas')
    _require(type(timeline.get('duration')) is int and timeline['duration'] == SOURCE_DURATION_US,
             'Base timeline duration must be exactly 9 seconds')
    _require(timeline.get('color_space') == 0
             and timeline.get('render_index_track_mode_on') is True
             and timeline.get('path') == '',
             'Base timeline has unreviewed render state')
    tracks = timeline.get('tracks')
    _require(isinstance(tracks, list) and len(tracks) == 1 and tracks[0].get('type') == 'video',
             'Base timeline must contain exactly one video track')
    track = tracks[0]
    _exact_keys(track, VIDEO_TRACK_FIELDS, 'Video track contains unsupported fields')
    _require(isinstance(track.get('segments'), list) and len(track['segments']) == 1,
             'Base video track must contain exactly one segment')
    segment = track['segments'][0]
    _exact_keys(segment, VIDEO_SEGMENT_FIELDS, 'Video segment contains unsupported fields')
    _require(segment.get('source_timerange') == {'duration': SOURCE_DURATION_US}
             and segment.get('target_timerange') == {'duration': SOURCE_DURATION_US},
             'Base segment must be the untrimmed 9-second source at 1x')

    materials = timeline.get('materials')
    _require(isinstance(materials, dict) and set(materials) == set(MATERIAL_BUCKET_COUNTS),
             'Timeline contains unknown material buckets')
    _require({key: len(value) if isinstance(value, list) else -1
              for key, value in materials.items()} == MATERIAL_BUCKET_COUNTS,
             'Timeline contains unsupported or extra materials')
    for bucket, nodes in materials.items():
        for node in nodes:
            _exact_keys(node, MATERIAL_FIELDS[bucket],
                        'Material in %s contains unsupported fields' % bucket)
    _require(materials['canvases'][0]['type'] == 'canvas_color'
             and materials['placeholder_infos'][0]['type'] == 'placeholder_info'
             and materials['placeholder_infos'][0]['meta_type'] == 'none'
             and materials['sound_channel_mappings'][0]['type'] == 'none'
             and materials['vocal_separations'][0]['type'] == 'vocal_separation',
             'Base companion materials have unreviewed processing state')
    index = _material_index(timeline)
    video_ref = index.get(segment.get('material_id'))
    _require(video_ref is not None and video_ref[0] == 'videos',
             'Video segment material reference is invalid')
    video = video_ref[1]
    _check_nested_schema(timeline, video, segment)
    _require(video.get('path') == SOURCE_PATH and video.get('material_name') == SOURCE_NAME
             and video.get('width') == 1280 and video.get('height') == 720
             and video.get('duration') == 24_000_000,
             'Video material does not match the pinned source SHA and media properties')
    _require(len(segment.get('extra_material_refs', [])) == 6
             and sum(1 for ref in segment['extra_material_refs']
                    if ref in index and index[ref][0] == 'speeds') == 1,
             'Video segment must have exactly one speed reference among its native refs')
    _require(len(set(segment['extra_material_refs'])) == 6
             and set(segment['extra_material_refs']) == set(index) - {video['id']},
             'Video segment must reference every native companion material exactly once')
    speed_id = next(ref for ref in segment['extra_material_refs'] if index[ref][0] == 'speeds')
    speed_ref = index[speed_id]
    _exact_keys(speed_ref[1], {'id', 'type'},
                'Base speed material does not match the exact cold-reopened default 1x shape')
    _require(speed_ref[1].get('type') == 'speed', 'Base speed material must be 1x')
    for ref in [segment['material_id']] + segment['extra_material_refs']:
        _require(ref in index, 'Timeline contains a dangling material reference')
    identifiers = [timeline.get('id'), track.get('id'), segment.get('id')]
    identifiers.extend(index)
    identifiers.extend(node.get('local_material_id') for node in materials['videos'])
    _require(all(isinstance(item, str) and item for item in identifiers)
             and len(identifiers) == len(set(identifiers)),
             'Timeline graph contains malformed or duplicate identities')
    return track, segment, speed_id


def build_curve_profile(base_timeline, *, runtime_profile, source_fps, source_sha256):
    """Return the exact cold-reopened five-point curve on a copied base graph.

    ``source_sha256`` must come from a caller-side byte hash; this pure graph
    constructor checks the supplied digest and the timeline's pinned media path
    but does not open or hash media files.
    The observed scalar and target duration are preserved independently. Their
    arithmetic discrepancy is intentional evidence from the GUI snapshot.
    """
    _require(runtime_profile == PROFILE_1140_BUILD481,
             'Curve profile is pinned to Jianying 11.4.0 Build 481')
    _require(isinstance(base_timeline, dict), 'Base timeline must be an object')
    track, segment, old_speed_id = _validate_base(base_timeline, source_fps, source_sha256)
    result = deepcopy(base_timeline)
    result_track = result['tracks'][0]
    result_segment = result_track['segments'][0]
    used = {result['id'], result_track['id'], result_segment['id']}
    used.update(_material_index(result))
    used.update(node['local_material_id'] for node in result['materials']['videos'])
    new_speed_id = str(uuid.uuid4()).upper()
    while new_speed_id in used:
        new_speed_id = str(uuid.uuid4()).upper()
    speed_material = {
        'id': new_speed_id,
        'type': 'speed',
        'mode': 1,
        'speed': CURVE_SCALAR,
        'curve_speed': {
            'id': CURVE_ID,
            'name': CURVE_NAME,
            'speed_points': deepcopy(CURVE_POINTS),
        },
    }
    result['materials']['speeds'] = [speed_material]
    result_segment['extra_material_refs'] = [
        new_speed_id if ref == old_speed_id else ref
        for ref in result_segment['extra_material_refs']
    ]
    result_segment['speed'] = CURVE_SCALAR
    result_segment['source_timerange'] = {'duration': SOURCE_DURATION_US}
    result_segment['target_timerange'] = {'duration': TARGET_DURATION_US}
    result['duration'] = TARGET_DURATION_US
    _require(sum(ref == new_speed_id for ref in result_segment['extra_material_refs']) == 1,
             'Generated speed material reference did not close')
    return result
