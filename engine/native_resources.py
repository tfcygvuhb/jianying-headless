"""Pinned, locally acquired native effect resources; never fetch or license them.

The catalog describes resources selected in the real application during testing.
Copying them into a private local draft does not grant redistribution rights.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

import headless_runtime as rt
from runtime_profiles import PROFILE_1140_BUILD481, RESOURCE_CAPTURE_PROFILE, validate_resource_profile

HERE = Path(__file__).resolve().parent
CATALOG_SHA = '45882abc24887a2dc65e64135dff829ca95e52ad2e8a57a7c0467fe6d03c0757'
SHAPES = ('circle', 'rectangle', 'line', 'mirror', 'star', 'heart')

# Build 481 has a resource-key exception, not the general native_resources
# capability. The official GUI selection and cold-reopen capture confirmed
# only the individually listed resources; each has an exact GUI-selected
# identity and cache path, with files cross-checked against its pinned capture.
BUILD481_RESOURCE_IDENTITIES = {
    'effect/light-shake': {
        'resource_id': '7399493554147527951',
        'name': '轻微抖动',
        'tree_sha256': '109b61dbbfb2f09a69e01e56197d840f7199f6ad51201b0b62a1bc2341929555',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/7399493554147527951/f443ba63a627600bf408d3ed98fe788e'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/7399493554147527951/'
                          'f443ba63a627600bf408d3ed98fe788e'),
    },
    'mask/circle': {
        'resource_id': '7356934080102928946',
        'tree_sha256': '755f487494e041e0adceaff3c1a747b1238773c071fe3297d1911112cccd3946',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/82432977/3ab1c47350d987c8ad415497e020a38b'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/82432977/'
                          '3ab1c47350d987c8ad415497e020a38b'),
    },
    'mask/mirror': {
        'resource_id': '7356933823327638042',
        'tree_sha256': '36365677e9ef362fdba0a5a9169cd9427c85f3ebecfc16f98c7d17a21bef3977',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/82432979/95ac211c99063c41b86b9b63742f4a6d'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/82432979/'
                          '95ac211c99063c41b86b9b63742f4a6d'),
    },
    'mask/rectangle': {
        'resource_id': '7356934318301647410',
        'tree_sha256': 'c8d500f2840e387e372744f6f44e1d2128e29c94df3dc482cf18a8de7d2f0ec6',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/82432980/02b8999168d121538a98ea59127483ef'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/82432980/'
                          '02b8999168d121538a98ea59127483ef'),
    },
    'mask/star': {
        'resource_id': '7416258989467374091',
        'tree_sha256': 'ba3fd7ebd571eba4f3383343eb7b8f6f504dfef8d6477af3bbe49bd8c67f2a8e',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/83244852/7ff81ba985da9aae07b69c5b77ea7e9a'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/83244852/'
                          '7ff81ba985da9aae07b69c5b77ea7e9a'),
        'resource_type': 'pentagram',
    },
    'mask/heart': {
        'resource_id': '7416258912162157068',
        'resource_type': 'heart',
        'name': '爱心',
        'tree_sha256': 'd72134d8c23f46d9d2ca3b2d7171908285487f2a1cb69cdb57593d427e422936',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/83244815/27ae3c55bb97e470a75f61a8d34832bf'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/83244815/'
                          '27ae3c55bb97e470a75f61a8d34832bf'),
    },
    'mask/line': {
        'resource_id': '7356933362960831003',
        'resource_type': 'line',
        'tree_sha256': 'e548c277fb2a6e06739855160a985a676221b19e9c4a65b60c8d75df1aea3c29',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/82432976/4c6a0ef5de6a844342d40330e00c59eb'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/82432976/'
                          '4c6a0ef5de6a844342d40330e00c59eb'),
    },
    # Individually captured from the official Build 481 transition picker.
    # This exact identity permits a local draft build only; export scope stays
    # independently gated by the runtime profile and its evidence record.
    'transition/dissolve': {
        'resource_id': '6724845717472416269',
        'tree_sha256': 'dc006fa499721070ec74f98a2aa01ca7baa85bca5a7145b12acf6c4cdc0243da',
        'source': ('Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/'
                   'effect/6724845717472416269/33d3a1ad16e89a4e2c9b6d45e3ec7aa1'),
        'legacy_source': ('Movies/JianyingPro/User Data/Cache/effect/6724845717472416269/'
                          '33d3a1ad16e89a4e2c9b6d45e3ec7aa1'),
    },
}


def require(value, message):
    if not value:
        raise ValueError(message)


def tree_manifest(folder):
    folder = Path(folder)
    require(folder.is_dir() and not folder.is_symlink(), 'Native resource directory missing or symlinked')
    result = {}
    for path in sorted(folder.rglob('*')):
        info = path.lstat()
        require(not path.is_symlink(), 'Native resource symlinks are not allowed')
        if stat.S_ISDIR(info.st_mode):
            continue
        require(stat.S_ISREG(info.st_mode), 'Native resource contains a nonregular file')
        result[path.relative_to(folder).as_posix()] = {'sha256': rt.digest(path), 'size': info.st_size}
    require(result, 'Native resource is empty')
    return result


def manifest_hash(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify_cached_manifest(entry, actual, message):
    """Only exact captured compiler outputs may supplement unchanged sources."""
    original = entry['files']
    require(all(actual.get(name) == info for name, info in original.items()), message)
    extra = {name: info for name, info in actual.items() if name not in original}
    allowed = entry.get('native_generated_cache_files', {})
    require(all(allowed.get(name) == info for name, info in extra.items()), message)
    return sorted(extra)


def catalog():
    path = HERE / 'native-resource-catalog.json'
    require(rt.digest(path) == CATALOG_SHA, 'Native resource catalog changed; review capture provenance')
    value = json.loads(path.read_bytes())
    require(value['schema'] == 'jy14-native-resource-catalog/v1', 'Unsupported native resource catalog')
    # Only relocate the captured user's home prefix. Relative cache locations,
    # resource IDs, permissions and every resource byte hash remain unchanged.
    def expand_home(item):
        if isinstance(item, dict):
            return {key: expand_home(child) for key, child in item.items()}
        if isinstance(item, list):
            return [expand_home(child) for child in item]
        if isinstance(item, str) and item.startswith('@home/'):
            relative = Path(item[len('@home/'):])
            require(not relative.is_absolute() and '..' not in relative.parts, 'Invalid catalog home-relative path')
            return str(Path.home() / relative)
        return item
    return expand_home(value)


def definition(key):
    data = catalog()
    require(key in data['resources'], 'Native resource has no verified local capture: ' + key)
    return deepcopy(data['resources'][key])


def validate_resource_key(runtime_profile, capture_profile, key, entry):
    """Gate a resource by exact runtime, key, and captured identity."""
    if runtime_profile != PROFILE_1140_BUILD481:
        validate_resource_profile(runtime_profile, capture_profile)
        return
    require(capture_profile == RESOURCE_CAPTURE_PROFILE,
            'Build 481 resource needs the reviewed 11.4.2 capture profile')
    expected = BUILD481_RESOURCE_IDENTITIES.get(key)
    require(expected is not None, 'Build 481 native resource is not verified: ' + key)
    require(entry.get('material', {}).get('resource_id') == expected['resource_id']
            and entry.get('tree_sha256') == expected['tree_sha256'],
            'Build 481 resource identity changed: ' + key)
    for field in ('resource_type', 'name'):
        if field in expected:
            require(entry.get('material', {}).get(field) == expected[field],
                    'Build 481 resource material ' + field + ' changed: ' + key)
    require(entry.get('source') == str(Path.home() / expected['source']),
            'Build 481 resource source changed: ' + key)
    source = Path(entry['source'])
    legacy_source = Path.home() / expected['legacy_source']
    require(source.resolve(strict=True) == legacy_source.resolve(strict=True),
            'Build 481 resource source no longer matches the reviewed cache bytes: ' + key)


def entry_for_runtime(key, entry, runtime_profile):
    value = deepcopy(entry)
    if runtime_profile == PROFILE_1140_BUILD481:
        expected = BUILD481_RESOURCE_IDENTITIES.get(key)
        require(expected is not None, 'Build 481 native resource is not verified: ' + key)
        value['source'] = str(Path.home() / expected['source'])
        if 'resource_type' in expected:
            value['material']['resource_type'] = expected['resource_type']
    return value


def relative_path(entry):
    fingerprint = entry['tree_sha256']
    require(len(fingerprint) == 64 and set(fingerprint) <= set('0123456789abcdef'), 'Invalid resource identity')
    return 'Resources/headless-native/' + fingerprint


def wanted_keys(plan):
    result = {'mask/' + s['mask']['shape'] for t in plan['tracks'] for s in t['segments'] if 'mask' in s}
    result.update('transition/' + s['transition_out']['name'] for t in plan['tracks'] for s in t['segments']
                  if 'transition_out' in s)
    result.update(t['type'] + '/' + s['name'] for t in plan['tracks'] if t['type'] in {'filter', 'effect'}
                  for s in t['segments'])
    result.update('text-effect/' + s['text_effect']['name'] for t in plan['tracks'] for s in t['segments']
                  if 'text_effect' in s)
    return sorted(result)


def prepare(plan, folder, runtime):
    keys = wanted_keys(plan)
    if not keys:
        return []
    data = catalog()
    entries = {}
    for key in keys:
        require(key in data['resources'], 'Native resource has no verified local capture: ' + key)
        entries[key] = entry_for_runtime(key, data['resources'][key], runtime['runtime_profile'])
        validate_resource_key(runtime['runtime_profile'], data['runtime_profile'], key, entries[key])
    records = []
    for key in keys:
        entry = deepcopy(entries[key])
        source = Path(entry['source'])
        require(source.is_absolute(), 'Native resource source must be absolute')
        if runtime['runtime_profile'] != PROFILE_1140_BUILD481:
            require(source.resolve(strict=True) == source,
                    'Native resource source must be the captured canonical directory')
        generated = verify_cached_manifest(entry, tree_manifest(source), 'Native resource bytes differ from captured identity')
        relative = relative_path(entry)
        dest = Path(folder) / relative
        if not dest.exists():
            dest.mkdir(parents=True, exist_ok=False, mode=0o700)
            # Ship only the original effect package, never this machine's
            # optional GPU compiler cache. All names come from the pinned catalog.
            for name in entry['files']:
                copied = dest / name
                copied.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                shutil.copyfile(source / name, copied, follow_symlinks=False)
        require(tree_manifest(dest) == entry['files'], 'Native resource changed during copy')
        verify_cached_manifest(entry, tree_manifest(source), 'Native resource changed during copy')
        # Preserve resource contents and metadata; files remain local to the draft.
        for path in [dest] + list(dest.rglob('*')):
            os.chmod(path, 0o700 if path.is_dir() else 0o600)
        records.append({'key': key, 'relative': relative, 'tree_sha256': entry['tree_sha256'],
                        'files': entry['files'], 'resource_id': entry['material']['resource_id'],
                        'origin': 'native-application-selection', 'redistribution_authorized': False})
        if 'usage' in entry:
            records[-1]['usage'] = deepcopy(entry['usage'])
        if generated:
            records[-1]['source_generated_cache_files_not_copied'] = generated
    return records


def material(key, target, runtime_profile=None):
    data = catalog()
    active_profile = runtime_profile or data['runtime_profile']
    require(key in data['resources'], 'Native resource has no verified local capture: ' + key)
    entry = entry_for_runtime(key, data['resources'][key], active_profile)
    validate_resource_key(active_profile, data['runtime_profile'], key, entry)
    value = deepcopy(entry['material'])
    value['path'] = str(Path(target) / relative_path(entry))
    return value


def verify_files(records, folder, plan, runtime_profile=None):
    require([r['key'] for r in records] == wanted_keys(plan), 'Native resource inventory differs from plan')
    data = catalog()
    active_profile = runtime_profile or data['runtime_profile']
    for record in records:
        require(record['key'] in data['resources'],
                'Native resource has no verified local capture: ' + str(record['key']))
        entry = entry_for_runtime(record['key'], data['resources'][record['key']], active_profile)
        validate_resource_key(active_profile, data['runtime_profile'], record['key'], entry)
        require(record['relative'] == relative_path(entry) and record['files'] == entry['files']
                and record['tree_sha256'] == entry['tree_sha256'], 'Native resource record changed')
        require(record.get('usage') == entry.get('usage'), 'Native resource usage boundary changed')
        require(tree_manifest(Path(folder) / record['relative']) == entry['files'], 'Draft-owned native resource bytes changed')


def verify_binding(key, value, target, resolve_native_path, allow_native_cache=False, runtime_profile=None):
    data = catalog()
    active_profile = runtime_profile or data['runtime_profile']
    entry = entry_for_runtime(key, data['resources'][key], active_profile)
    validate_resource_key(active_profile, data['runtime_profile'], key, entry)
    actual = resolve_native_path(value, Path(target))
    if actual == (Path(target) / relative_path(entry)).resolve():
        return {'key': key, 'location': 'draft-owned'}
    # Native save may rebind known IDs back to the captured cache. Keep the
    # legacy path and Build 481's GUI-selected container path profile-specific;
    # accept only that exact source AND its captured contents.
    expected_cache = Path(entry['source'])
    if active_profile == PROFILE_1140_BUILD481:
        require(Path(value) == expected_cache, 'Build 481 native cache path changed')
        expected_cache = expected_cache.resolve(strict=True)
    require(allow_native_cache and actual == expected_cache, 'Native resource path changed')
    generated = verify_cached_manifest(entry, tree_manifest(actual), 'Native cache resource bytes changed')
    result = {'key': key, 'location': 'native-cache', 'bytes_verified': True}
    if generated:
        result['native_generated_cache_files_verified'] = generated
    return result
