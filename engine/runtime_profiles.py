"""Exact Jianying application identities and fail-closed capabilities.

Compatibility is selected by the complete application identity, never by a
version prefix.  The 11.4.0 Build 481 profile is intentionally draft-only:
its codec and native ABI must be reviewed independently before any native
export, resource, or existing-draft operation is enabled.
"""

PRIMARY_VERSION = '11.5.0'
PROFILE_PREFIX = 'jy14-headless-macos-'
BUNDLE_ID = 'com.lemon.lvpro'
TEAM_IDENTIFIER = 'X2JNK7LY8J'

CAPABILITY_NAMES = (
    'draft_create', 'publish', 'verify', 'existing_edit',
    'native_export', 'native_resources',
)

RESOURCE_CAPABILITY_NAMES = (
    'fonts', 'subtitles', 'transitions', 'filters', 'effects', 'stickers',
    'masks', 'keyframes', 'compound_clips', 'adjustment_layers',
    'member_online_resources',
)

EVIDENCE_LAYERS = ('offline_build', 'native_reopen', 'native_export')

PROFILE_1140_BUILD481 = PROFILE_PREFIX + '11.4.0-build481'

# The old version keys are retained as a compatibility surface for code that
# only needs a historical library fingerprint.  New runtime selection must
# use RUNTIME_IDENTITIES so that 11.4.0 can distinguish Build 481 from the
# historical 11.4.0 capture.
PROFILES = {
    '11.5.0': '2041482a1aaeffa4d8bd69b836f8cf38807aaad8021bca410d567c59af3bccfa',
    '11.4.2': '632c8ddd09ff4a54f876cd8142eb505055ee26d944199506b230949b7e106bd1',
    '11.4.0': 'a1693070036a6678bb5db35f71d2105812ad24a2370e7e91c78712cc0d6455f3',
}

_FULL_DRAFT_CAPABILITIES = {
    'draft_create': True, 'publish': True, 'verify': True,
    'existing_edit': True,
    'existing_edit': True, 'native_export': True, 'native_resources': True,
}
_BUILD481_CAPABILITIES = {
    'draft_create': True, 'publish': True, 'verify': True,
    'existing_edit': True, 'native_export': False, 'native_resources': False,
}
_LEGACY_DISABLED_CAPABILITIES = {name: False for name in CAPABILITY_NAMES}

# Evidence is deliberately more granular than the coarse runtime switch.  It
# records what has actually been observed for Build 481 without turning a
# partial result into permission to use native resources.  Values are limited
# to ``verified``, ``partial``, ``blocked`` and ``unverified`` so reports and
# tests cannot silently reinterpret prose as a capability grant.
_BUILD481_RESOURCE_EVIDENCE = {
    'fonts': {'offline_build': 'unverified', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'subtitles': {'offline_build': 'verified', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'transitions': {'offline_build': 'blocked', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'filters': {'offline_build': 'blocked', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'effects': {'offline_build': 'blocked', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'stickers': {'offline_build': 'unverified', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'masks': {'offline_build': 'blocked', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'keyframes': {'offline_build': 'unverified', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'compound_clips': {'offline_build': 'unverified', 'native_reopen': 'blocked', 'native_export': 'blocked'},
    'adjustment_layers': {'offline_build': 'unverified', 'native_reopen': 'unverified', 'native_export': 'blocked'},
    'member_online_resources': {'offline_build': 'blocked', 'native_reopen': 'unverified', 'native_export': 'blocked'},
}

# Codec SHA256 values are source-pinned.  A profile may carry None while it is
# awaiting an isolated rebuild; None means "not reviewed" and is a hard stop,
# never an invitation to reuse an older binary.
RUNTIME_IDENTITIES = {
    PROFILE_PREFIX + '11.5.0': {
        'profile_id': PROFILE_PREFIX + '11.5.0',
        'app_version': '11.5.0', 'app_build': '11.5.0',
        'bundle_id': BUNDLE_ID, 'team_identifier': TEAM_IDENTIFIER,
        'library_sha256': PROFILES['11.5.0'],
        'codec_name': 'jy14_codec_hardened_11_4',
        'codec_sha256': 'b6533eb5eb1eea58dfa74fb1d16d3bb580970fe881f587605d358af1745f971d',
        'capabilities': dict(_FULL_DRAFT_CAPABILITIES),
    },
    PROFILE_PREFIX + '11.4.2': {
        'profile_id': PROFILE_PREFIX + '11.4.2',
        'app_version': '11.4.2', 'app_build': '11.4.2',
        'bundle_id': BUNDLE_ID, 'team_identifier': TEAM_IDENTIFIER,
        'library_sha256': PROFILES['11.4.2'],
        'codec_name': 'jy14_codec_hardened_11_4',
        'codec_sha256': 'b6533eb5eb1eea58dfa74fb1d16d3bb580970fe881f587605d358af1745f971d',
        'capabilities': dict(_FULL_DRAFT_CAPABILITIES),
    },
    # Historical 11.4.0 is kept identifiable but is not promoted to any
    # live-writing capability.  It cannot alias the current Build 481.
    PROFILE_PREFIX + '11.4.0': {
        'profile_id': PROFILE_PREFIX + '11.4.0',
        'app_version': '11.4.0', 'app_build': '11.4.0',
        'bundle_id': BUNDLE_ID, 'team_identifier': TEAM_IDENTIFIER,
        'library_sha256': PROFILES['11.4.0'],
        'codec_name': 'jy14_codec_hardened_11_4',
        'codec_sha256': 'b6533eb5eb1eea58dfa74fb1d16d3bb580970fe881f587605d358af1745f971d',
        'capabilities': dict(_LEGACY_DISABLED_CAPABILITIES),
    },
    PROFILE_1140_BUILD481: {
        'profile_id': PROFILE_1140_BUILD481,
        'app_version': '11.4.0', 'app_build': '481',
        'bundle_id': BUNDLE_ID, 'team_identifier': TEAM_IDENTIFIER,
        'library_sha256': 'aea79715de6097394c2f38153e11565f02a823678801cd1eafe90bcccb20c086',
        'codec_name': 'jy14_codec_hardened_11_4_0_build481',
        'codec_sha256': 'f6f49c718c740dae77fe1525b2762fc1801951ec6bf5eb223156842529123947',
        'capabilities': dict(_BUILD481_CAPABILITIES),
        'resource_evidence': {name: dict(layers)
                              for name, layers in _BUILD481_RESOURCE_EVIDENCE.items()},
    },
}

CAPABILITY_MATRIX = {
    profile_id: dict(profile['capabilities'])
    for profile_id, profile in RUNTIME_IDENTITIES.items()
}
EXPORT_PROFILES = frozenset(
    profile_id for profile_id, capabilities in CAPABILITY_MATRIX.items()
    if capabilities['native_export']
)
RESOURCE_CAPTURE_PROFILE = PROFILE_PREFIX + '11.4.2'
TIMELINE_SCHEMAS = frozenset((('185.0.0', 360000), ('187.0.0', 360000)))


def _copy_profile(profile):
    value = dict(profile)
    value['capabilities'] = dict(profile['capabilities'])
    if 'resource_evidence' in profile:
        value['resource_evidence'] = {
            name: dict(layers) for name, layers in profile['resource_evidence'].items()
        }
    return value


def resource_evidence_for(profile_id):
    profile = profile_for_id(profile_id)
    evidence = profile.get('resource_evidence', {})
    if set(evidence) != set(RESOURCE_CAPABILITY_NAMES):
        return {}
    allowed = {'verified', 'partial', 'blocked', 'unverified'}
    for name, layers in evidence.items():
        if set(layers) != set(EVIDENCE_LAYERS) or not set(layers.values()) <= allowed:
            raise ValueError('Malformed resource evidence matrix for ' + name)
    return {name: dict(layers) for name, layers in evidence.items()}


def profile_for_id(profile_id):
    try:
        return _copy_profile(RUNTIME_IDENTITIES[profile_id])
    except KeyError as error:
        raise ValueError('Unknown Jianying runtime profile: ' + str(profile_id)) from error


def codec_for_profile(profile_id):
    profile = profile_for_id(profile_id)
    if not profile['codec_sha256']:
        raise ValueError('No reviewed codec is pinned for runtime profile ' + profile_id)
    return profile['codec_name'], profile['codec_sha256']


def capabilities_for(profile_id):
    return dict(profile_for_id(profile_id)['capabilities'])


def require_capability(profile_id, capability):
    if capability not in CAPABILITY_NAMES:
        raise ValueError('Unknown runtime capability: ' + str(capability))
    if not capabilities_for(profile_id)[capability]:
        raise ValueError('Runtime profile %s does not enable capability %s' %
                         (profile_id, capability))


def resolve_identity(info, fingerprint, team_identifier):
    """Return the one exact profile matching plist identity and library hash."""
    if (not isinstance(info, dict) or not isinstance(fingerprint, str)
            or not isinstance(team_identifier, str)):
        raise ValueError('Malformed Jianying application identity; stop native writes')
    version = info.get('CFBundleShortVersionString')
    build = info.get('CFBundleVersion')
    bundle_id = info.get('CFBundleIdentifier')
    matches = [profile for profile in RUNTIME_IDENTITIES.values()
               if profile['app_version'] == version and profile['app_build'] == build
               and profile['bundle_id'] == bundle_id
               and profile['team_identifier'] == team_identifier
               and profile['library_sha256'] == fingerprint]
    if len(matches) != 1:
        expected = [profile['profile_id'] for profile in RUNTIME_IDENTITIES.values()
                    if profile['app_version'] == version and profile['app_build'] == build]
        raise ValueError(
            'Unsupported Jianying version/build/identity; stop native writes; '
            'version=%s; build=%s; bundle=%s; matching_profiles=%s' %
            (version, build, bundle_id, expected))
    return _copy_profile(matches[0])


def validate_identity(info, fingerprint):
    """Backward-compatible historical helper; live callers use resolve_identity."""
    team = info.get('TeamIdentifier') or info.get('team_identifier') or TEAM_IDENTIFIER
    return resolve_identity(info, fingerprint, team)['app_version']


def validate_timeline_schema(timeline, runtime_profile=None):
    schema = (timeline.get('new_version'), timeline.get('version'))
    if type(schema[1]) is not int or schema not in TIMELINE_SCHEMAS:
        raise ValueError('Unexpected native timeline version')
    if runtime_profile is not None:
        profile = profile_for_id(runtime_profile)
        # Build 481 has only a reviewed legacy 185 schema.  Do not infer that
        # its future native save migration is equivalent to 11.5.0.
        if schema[0] == '187.0.0' and runtime_profile != PROFILE_PREFIX + '11.5.0':
            raise ValueError('Native timeline schema is incompatible with this runtime profile')
        if not profile['capabilities']['draft_create'] and runtime_profile == PROFILE_1140_BUILD481:
            raise ValueError('Runtime profile is not enabled for draft timelines')
    return schema


def saved_schema_upgrade(expected, actual, runtime_profile):
    """Recognize only the exact observed UI upgrade; never normalize other fields."""
    before = validate_timeline_schema(expected, runtime_profile)
    after = validate_timeline_schema(actual, runtime_profile)
    if before == after:
        return None
    if (runtime_profile == PROFILE_PREFIX + '11.5.0' and before == ('185.0.0', 360000)
            and after == ('187.0.0', 360000)
            and actual.get('last_modified_platform', {}).get('app_version') == '11.5.0'):
        return {'timeline_id': actual['id'], 'before': before[0], 'after': after[0]}
    raise ValueError('Unreviewed native schema migration')


def validate_export_profiles(build_profile, runtime_profile):
    require_capability(build_profile, 'native_export')
    require_capability(runtime_profile, 'native_export')
    if build_profile != runtime_profile:
        raise ValueError('Build runtime differs from the installed editor; rebuild or edit a copy on the current runtime')


def validate_resource_profile(runtime_profile, capture_profile):
    if capture_profile != RESOURCE_CAPTURE_PROFILE:
        raise ValueError('Native resources need the reviewed 11.4.2 capture profile')
    require_capability(runtime_profile, 'native_resources')
