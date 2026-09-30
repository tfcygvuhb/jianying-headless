"""A rejected Build 481 speed must not reach the draft home index."""
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
import jy14_headless as j


class Build481SpeedPublishGateTests(unittest.TestCase):
    def test_rejected_speed_stops_before_audit_and_home_write(self):
        timeline = {'materials': {'speeds': [{'speed': 8}]},
                    'tracks': [{'segments': [{'speed': 8}]}]}
        helper = SimpleNamespace(_decrypt_metadata_in_memory=lambda _: timeline)
        with tempfile.TemporaryDirectory() as root:
            build = Path(root) / 'build'
            build.mkdir()
            audit = Path(root) / 'audit'
            with patch.object(j.nd, 'helper', return_value=helper):
                with self.assertRaisesRegex(ValueError, 'publish rejects unqualified speed'):
                    j.publish(build, audit, verify_build_fn=lambda _: {
                        'runtime_profile': 'jy14-headless-macos-11.4.0-build481'})
            self.assertFalse(audit.exists())

    def test_speed_gate_checks_material_and_segment(self):
        timeline = {'materials': {'speeds': [{'speed': 1}]},
                    'tracks': [{'segments': [{'speed': 1}]}]}
        j.require_build481_publish_speed_scope(timeline)
        timeline['materials']['speeds'][0]['curve_speed'] = {'points': []}
        with self.assertRaises(ValueError):
            j.require_build481_publish_speed_scope(timeline)
        del timeline['materials']['speeds'][0]['curve_speed']
        timeline['tracks'][0]['segments'][0]['speed'] = 0.5
        with self.assertRaises(ValueError):
            j.require_build481_publish_speed_scope(timeline)


if __name__ == '__main__':
    unittest.main()
