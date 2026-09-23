#!/usr/bin/env python3
"""Create a non-live macOS metadata fixture for the Jianying home index.

The source is opened read-only and never replaced.  Every candidate file is
created below a fresh ``work/`` directory so this tool cannot publish a draft
or mutate Jianying's live index.  The report is evidence only: it never changes
runtime capabilities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def xattrs(path: Path) -> dict[str, str]:
    names = subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines()
    return {name: subprocess.check_output(
        ['/usr/bin/xattr', '-px', name, str(path)], text=True).replace('\n', '').lower()
            for name in names}


def acl(path: Path) -> list[str]:
    result = subprocess.run(['/bin/ls', '-lde', str(path)], check=True,
                            capture_output=True, text=True,
                            env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
    lines = result.stdout.splitlines()
    return [line.strip() for line in lines[1:]]


def metadata(path: Path) -> dict:
    value = path.lstat()
    if not stat.S_ISREG(value.st_mode) or path.is_symlink():
        raise ValueError('fixture input must be a non-symlink regular file')
    return {
        'sha256': digest(path), 'size': value.st_size,
        'mode': oct(stat.S_IMODE(value.st_mode)), 'uid': value.st_uid, 'gid': value.st_gid,
        'xattrs': xattrs(path), 'acl': acl(path),
    }


def comparison(source: dict, candidate: dict) -> dict:
    source_attrs = source['xattrs']
    candidate_attrs = candidate['xattrs']
    changed = sorted(name for name in set(source_attrs) | set(candidate_attrs)
                     if source_attrs.get(name) != candidate_attrs.get(name))
    return {
        'bytes_equal': source['sha256'] == candidate['sha256'],
        'mode_equal': source['mode'] == candidate['mode'],
        'owner_group_equal': (source['uid'], source['gid']) == (candidate['uid'], candidate['gid']),
        'acl_equal': source['acl'] == candidate['acl'],
        'xattrs_equal': not changed,
        'xattr_changed_names': changed,
        'source_xattrs_preserved': all(candidate_attrs.get(name) == value
                                       for name, value in source_attrs.items()),
        'added_xattrs': sorted(set(candidate_attrs) - set(source_attrs)),
    }


def copy_attrs(source: Path, destination: Path) -> None:
    for name, value in xattrs(source).items():
        subprocess.run(['/usr/bin/xattr', '-wx', name, value, str(destination)],
                       check=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.expanduser().resolve(strict=True)
    out = args.out.expanduser().resolve()
    project = Path(__file__).resolve().parent.parent
    work = (project / 'work').resolve()
    if out == work or work not in out.parents or out.exists():
        raise SystemExit('--out must be a new child of this checkout work/')
    before = metadata(source)
    payload = source.read_bytes()
    out.mkdir(parents=True, mode=0o700)

    candidates = {}
    direct = out / 'direct-write.index'
    direct.write_bytes(payload)
    os.chmod(direct, int(before['mode'], 8))
    copy_attrs(source, direct)
    candidates['direct_write'] = metadata(direct)
    candidates['direct_write']['comparison'] = comparison(before, candidates['direct_write'])

    copied = out / 'copy2-rewrite.index'
    shutil.copy2(source, copied)
    copied.write_bytes(payload)
    candidates['copy2_rewrite'] = metadata(copied)
    candidates['copy2_rewrite']['comparison'] = comparison(before, candidates['copy2_rewrite'])

    cloned = out / 'clone-rewrite.index'
    clone = subprocess.run(['/bin/cp', '-c', '-p', str(source), str(cloned)],
                           capture_output=True, text=True)
    if clone.returncode == 0:
        cloned.write_bytes(payload)
        candidates['clone_rewrite'] = metadata(cloned)
        candidates['clone_rewrite']['comparison'] = comparison(before, candidates['clone_rewrite'])
    else:
        candidates['clone_rewrite'] = {'status': 'unavailable', 'stderr': clone.stderr.strip()}

    after = metadata(source)
    report = {
        'schema': 'jianying-publish-metadata-audit/v1',
        'source_unchanged': before == after,
        'source': before,
        'candidates': candidates,
        'capability_changed': False,
        'live_index_written': False,
    }
    (out / 'report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if before != after:
        raise SystemExit('source metadata changed during read-only audit')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
