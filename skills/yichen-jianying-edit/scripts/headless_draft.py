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
    'runtime_profiles.py': 'f7f5320ccb3ce06693cebff578b7ce5d6aa7b7fad1d918e21b1e18ee1406c844',
    'jy14_headless.py': '037c5cb0836d6dc67a42e01bb4e470673688ba92b63b6e1097ab7fc1bc0ee88f',
    'native_motion.py': '3660f876b7f8b1c95c5c0ae7dc4e7b56a990a6fffd7730263a978dc84b653143',
    'native_effects.py': 'c46b2fc9221dd613f220564b752e532f8f3753dd5595aaffc24f41d5236e4e97',
    'native_resources.py': '7cf0b2bcc626305fee0b68c28f0d41e1a770e31022adb67b4d68b31f0c8b60ae',
    'native_visual_effects.py': '15df7e56cc7d575a552c180e72ec712f136c618d271b2f3ad2d32dd5929e844c',
    'native-resource-catalog.json': '45882abc24887a2dc65e64135dff829ca95e52ad2e8a57a7c0467fe6d03c0757',
    'native_compound.py': 'eb9e7d5544e1726be291912c47a5cc917b80180a231242ca30b7b5aaf68f5bfc',
    'compound-blueprint.json': '9cba9435053280abf9072d5eaccb8586c841b11dac6854b32daf9cbdba76af8e',
    'native_edit.py': 'eaecade21b8a5fa7d123e08f85be3a17efe9ac1b6a3f2e6104d053957082f748',
    'native_export.py': 'a0e2d91bcbe92c333df609ef6a11e6ce161a0951682a05647096bf7b1fae3060',
    'native_export.cpp': '33cb7bdb206deba3804648b9b279e4d91073af91219eab124819657834f674c2',
    'headless_runtime.py': 'e294ea135cd1a416c8e0b854eeabc126d94189c23d22831ea3add9c94ca375a3',
    'blueprint.json': '91f7eddad5bff9af23eb88b53713c180e3e3d4054edd469140cfa9aa56bc1dc9',
}
TOOL_PINS = {
    'gui_cycle.py': 'c472af26af1a07770c92aad71df3be503ca32c6af5e348ee7760668c41354153',
    'jianying_ax.swift': '07ef2e000886b95c074d0295a041b728e800b97700c4c5837b5c1da1323c7bb2',
    'jianying_capture_identity.swift': 'd6c4af04ceea142cafb9d5fa75d94fd0fd2c0ef3d5c467a352a5131bad5a8b03',
    'jianying_identity_verifier.py': 'f50856afd089450333702aab6f3e0efd7e28b150203ebc382aa35fc54af68d74',
}

for name, expected in PINS.items():
    path = BACKEND / name
    if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit('Headless component changed or unavailable; reverify before updating the pin: ' + name)
for name, expected in TOOL_PINS.items():
    path = PROJECT_ROOT / 'tools' / name
    if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit('GUI component changed or unavailable; reverify before updating the pin: ' + name)

sys.path.insert(0, str(BACKEND))


def require_runtime_capability(capability):
    """Gate wrapper-only operations before loading a mutating engine entrypoint."""
    import headless_runtime
    runtime = headless_runtime.doctor()
    if runtime.get('capabilities', {}).get(capability) is not True:
        raise SystemExit('Runtime profile %s does not enable capability %s' %
                         (runtime.get('runtime_profile', '<unknown>'), capability))


entrypoint = BACKEND / 'jy14_headless.py'
if len(sys.argv) > 1 and sys.argv[1] == 'edit':
    require_runtime_capability('existing_edit')
    entrypoint = BACKEND / 'native_edit.py'
    del sys.argv[1]
elif len(sys.argv) > 1 and sys.argv[1] == 'export':
    require_runtime_capability('native_export')
    entrypoint = BACKEND / 'native_export.py'
    del sys.argv[1]
elif len(sys.argv) > 1 and sys.argv[1] == 'gui-cycle':
    require_runtime_capability('publish')
    require_runtime_capability('verify')
    entrypoint = PROJECT_ROOT / 'tools/gui_cycle.py'
    del sys.argv[1]
runpy.run_path(str(entrypoint), run_name='__main__')
