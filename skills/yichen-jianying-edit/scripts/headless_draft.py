#!/usr/bin/env python3
"""Pinned Skill entrypoint for a separately checked-out Jianying Headless project."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

def project_root():
    configured = os.environ.get('JIANYING_HEADLESS_ROOT')
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise SystemExit('JIANYING_HEADLESS_ROOT must be an absolute checkout path')
        candidates = [path.resolve()]
    else:
        candidates = list(Path(__file__).resolve().parents)
    for path in candidates:
        marker = path / 'project.json'
        if marker.is_file() and not marker.is_symlink():
            try:
                identity = json.loads(marker.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                continue
            if identity.get('id') == 'jianying-headless' and identity.get('schema') == 'jianying-headless-project/v1':
                return path
    raise SystemExit('Jianying Headless checkout unavailable. Clone the project with authorized GitHub access, '
                     'then set JIANYING_HEADLESS_ROOT to its absolute path. The Skill alone does not include the engine.')


PROJECT_ROOT = project_root()
BACKEND = PROJECT_ROOT / 'engine'
PINS = {
    'native_fonts.py': 'ddd7b4c1ecd55890bd645c14930f2c5f6687794691c2280daa32673e048da5e6',
    'runtime_profiles.py': 'c65501e939a049dd33d9be7438b08cbd7d7ef34baa452c7847f691ba7e819586',
    'jy14_headless.py': '3c6c50c9a05a54d2e49042097af90ad641b9562545fdec7a242990faa136fe18',
    'native_motion.py': '5d743caaa38c921779166e5663d36f72a0c3fdb130a690ac3942a7adcf62d6c2',
    'native_effects.py': 'c46b2fc9221dd613f220564b752e532f8f3753dd5595aaffc24f41d5236e4e97',
    'native_resources.py': '693d07072a964701c7fe02c78ce5e06d7d3be615d9a33bb2bf98554cfe78f8d2',
    'native_visual_effects.py': '15df7e56cc7d575a552c180e72ec712f136c618d271b2f3ad2d32dd5929e844c',
    'native-resource-catalog.json': '36e1b8951382f3d755fea268a1ed31e5c178012084e74722346fb79ee8fa641d',
    'native_compound.py': 'eb9e7d5544e1726be291912c47a5cc917b80180a231242ca30b7b5aaf68f5bfc',
    'compound-blueprint.json': '9cba9435053280abf9072d5eaccb8586c841b11dac6854b32daf9cbdba76af8e',
    'native_edit.py': '377c4ff886be5093cc08415e42ebe7d5669c04b30509ffd5a2695e5d1225b5eb',
    'native_export.py': '1a47e5bba1420a02effce49ea50e11fadffab6f65a277608f69481774bf2f219',
    'native_export.cpp': 'a7bd535700cb4ce989d4b40204f407ce6fd74b52a765197344f646c4d3e05aaa',
    'headless_runtime.py': '9925bd53c2cfc40844516aa3242a2cfb455843088d35bff53df5a9b123108443',
    'blueprint.json': '91f7eddad5bff9af23eb88b53713c180e3e3d4054edd469140cfa9aa56bc1dc9',
}

for name, expected in PINS.items():
    path = BACKEND / name
    if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit('Headless component changed or unavailable; reverify before updating the pin: ' + name)

sys.path.insert(0, str(BACKEND))


def require_runtime_capability(capability):
    """Gate wrapper-only operations before loading a mutating engine entrypoint."""
    import headless_runtime
    runtime = headless_runtime.doctor()
    if runtime.get('capabilities', {}).get(capability) is not True:
        raise SystemExit('Runtime profile %s does not enable capability %s' %
                         (runtime.get('runtime_profile', '<unknown>'), capability))


entrypoint = 'jy14_headless.py'
if len(sys.argv) > 1 and sys.argv[1] == 'edit':
    require_runtime_capability('existing_edit')
    entrypoint = 'native_edit.py'
    del sys.argv[1]
elif len(sys.argv) > 1 and sys.argv[1] == 'export':
    require_runtime_capability('native_export')
    entrypoint = 'native_export.py'
    del sys.argv[1]
runpy.run_path(str(BACKEND / entrypoint), run_name='__main__')
