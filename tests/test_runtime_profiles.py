"""Version selection and fail-closed guards, without changing the installed app."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'engine'))
import runtime_profiles as profiles


class RuntimeProfiles(unittest.TestCase):
    def info(self, version):
        return {'CFBundleShortVersionString': version, 'CFBundleVersion': version,
                'CFBundleIdentifier': 'com.lemon.lvpro'}

    def test_primary_and_legacy_identities(self):
        self.assertEqual(profiles.PRIMARY_VERSION, '11.5.0')
        for v,h in profiles.PROFILES.items():
            self.assertEqual(profiles.validate_identity(self.info(v),h),v)

    def test_exact_1142_fingerprint_is_preserved(self):
        self.assertEqual(profiles.PROFILES['11.4.2'],
                         '632c8ddd09ff4a54f876cd8142eb505055ee26d944199506b230949b7e106bd1')

    def test_build481_is_a_distinct_exact_basic_export_profile(self):
        profile = profiles.RUNTIME_IDENTITIES[profiles.PROFILE_1140_BUILD481]
        info = {'CFBundleShortVersionString': '11.4.0', 'CFBundleVersion': '481',
                'CFBundleIdentifier': 'com.lemon.lvpro'}
        self.assertEqual(profiles.resolve_identity(
            info, profile['library_sha256'], 'X2JNK7LY8J')['app_version'], '11.4.0')
        self.assertEqual(profile['profile_id'], 'jy14-headless-macos-11.4.0-build481')
        self.assertEqual(profile['capabilities'], {
            'draft_create': True, 'publish': True, 'verify': True,
            'existing_edit': True, 'native_export': True, 'native_resources': False,
        })
        self.assertIn(profiles.PROFILE_1140_BUILD481, profiles.EXPORT_PROFILES)
        evidence = profiles.resource_evidence_for(profiles.PROFILE_1140_BUILD481)
        self.assertEqual(set(evidence), set(profiles.RESOURCE_CAPABILITY_NAMES))
        self.assertEqual(evidence['subtitles'], {
            'offline_build': 'verified', 'native_reopen': 'partial',
            'native_export': 'partial',
        })
        self.assertEqual(evidence['fonts'], {
            'offline_build': 'verified', 'native_reopen': 'partial',
            'native_export': 'partial',
        })
        self.assertEqual(evidence['keyframes'], {
            'offline_build': 'verified', 'native_reopen': 'verified',
            'native_export': 'verified',
        })
        self.assertEqual(evidence['masks'], {
            'offline_build': 'verified', 'native_reopen': 'verified',
            'native_export': 'verified',
        })
        for kind in ('transitions', 'effects'):
            self.assertEqual(evidence[kind], {
                'offline_build': 'verified', 'native_reopen': 'verified',
                'native_export': 'verified',
            })
        self.assertFalse(profile['capabilities']['native_resources'])
        self.assertTrue(profile['capabilities']['native_export'])
        self.assertTrue(all(set(layers) == set(profiles.EVIDENCE_LAYERS)
                            for layers in evidence.values()))
        self.assertEqual(profiles.resource_evidence_for(
            profiles.PROFILE_PREFIX + '11.5.0'), {})
        with self.assertRaises(ValueError):
            profiles.resolve_identity(
                dict(info, CFBundleVersion='482'), profile['library_sha256'], 'X2JNK7LY8J')
        with self.assertRaises(ValueError):
            profiles.resolve_identity(info, profiles.PROFILES['11.4.0'], 'X2JNK7LY8J')
        with self.assertRaises(ValueError):
            profiles.resolve_identity(info, profile['library_sha256'], 'com.other')
        self.assertEqual(
            profiles.codec_for_profile(profiles.PROFILE_1140_BUILD481),
            ('jy14_codec_hardened_11_4_0_build481',
             'a473977dabb7652b7f111cd5d279c697ae71afc94c64a137d85fc8af8d06203f'))

    def test_mismatched_hash_build_bundle_and_unknown_version_rejected(self):
        for version in ('11.5.0','11.4.2'):
            h=profiles.PROFILES[version]
            bad=[(self.info(version),'0'*64)]
            for key,val in [('CFBundleVersion','unexpected'),('CFBundleIdentifier','com.other')]:
                info=self.info(version);info[key]=val;bad.append((info,h))
            for info,sha in bad:
                with self.subTest(version=version,info=info),self.assertRaises(ValueError):
                    profiles.validate_identity(info,sha)
        with self.assertRaises(ValueError):
            profiles.validate_identity(self.info('11.5.1'),profiles.PROFILES['11.5.0'])

    def test_export_only_allows_same_reviewed_runtime(self):
        for v in ('11.5.0','11.4.2'):
            p=profiles.PROFILE_PREFIX+v
            profiles.validate_export_profiles(p,p)
        profiles.validate_export_profiles(profiles.PROFILE_1140_BUILD481,
                                          profiles.PROFILE_1140_BUILD481)
        for a,b in [('11.4.2','11.5.0'),('11.5.0','11.4.2'),('11.4.0','11.4.0'),('11.5.1','11.5.1')]:
            with self.subTest(a=a,b=b),self.assertRaises(ValueError):
                profiles.validate_export_profiles(profiles.PROFILE_PREFIX+a,profiles.PROFILE_PREFIX+b)
        with self.assertRaisesRegex(ValueError, 'differs'):
            profiles.validate_export_profiles(profiles.PROFILE_1140_BUILD481,
                                              profiles.PROFILE_PREFIX+'11.4.2')

    def test_resource_pairing_keeps_capture_provenance(self):
        for p in profiles.EXPORT_PROFILES:
            if p == profiles.PROFILE_1140_BUILD481:
                with self.assertRaisesRegex(ValueError, 'native_resources'):
                    profiles.validate_resource_profile(p, profiles.RESOURCE_CAPTURE_PROFILE)
                continue
            profiles.validate_resource_profile(p,profiles.RESOURCE_CAPTURE_PROFILE)
        with self.assertRaises(ValueError):
            profiles.validate_resource_profile(profiles.PROFILE_PREFIX+'11.4.0',profiles.RESOURCE_CAPTURE_PROFILE)
        with self.assertRaises(ValueError):
            profiles.validate_resource_profile(profiles.PROFILE_PREFIX+'11.5.0',profiles.PROFILE_PREFIX+'11.5.0')

    def test_timeline_schema_is_version_scoped(self):
        old = {'new_version':'185.0.0','version':360000}
        new = {'new_version':'187.0.0','version':360000}
        for version in ('11.4.0','11.4.2','11.5.0'):
            profiles.validate_timeline_schema(old,profiles.PROFILE_PREFIX+version)
        profiles.validate_timeline_schema(old, profiles.PROFILE_1140_BUILD481)
        profiles.validate_timeline_schema(new,profiles.PROFILE_PREFIX+'11.5.0')
        for version in ('11.4.0','11.4.2','11.5.1', '11.4.0-build481'):
            with self.assertRaises(ValueError):
                profiles.validate_timeline_schema(new,profiles.PROFILE_PREFIX+version)
        for bad in [dict(new,new_version='188.0.0'),dict(new,version=360001),dict(new,version=360000.0)]:
            with self.assertRaises(ValueError): profiles.validate_timeline_schema(bad)

    def test_ui_upgrade_is_reported_without_mutating_evidence(self):
        old={'id':'sample','new_version':'185.0.0','version':360000}
        new=dict(old,new_version='187.0.0',last_modified_platform={'app_version':'11.5.0'})
        runtime=profiles.PROFILE_PREFIX+'11.5.0'
        change=profiles.saved_schema_upgrade(old,new,runtime)
        self.assertEqual(change,{'timeline_id':'sample','before':'185.0.0','after':'187.0.0'})
        self.assertEqual(new['new_version'],'187.0.0')
        self.assertIsNone(profiles.saved_schema_upgrade(new,new,runtime))
        with self.assertRaises(ValueError): profiles.saved_schema_upgrade(new,old,runtime)
        with self.assertRaises(ValueError):
            profiles.saved_schema_upgrade(old,dict(new,last_modified_platform={}),runtime)


if __name__=='__main__':
    unittest.main()
