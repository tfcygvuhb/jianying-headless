#!/usr/bin/env python3
"""Audit index staging in the real draft root without replacing the index.

This is a pre-publish acceptance fixture, not a publish command.  It requires
the exact Build 481 runtime and a closed editor, creates new hidden files with
exclusive names, records their security metadata, and leaves every file in
place as evidence.  It never creates a draft directory or replaces the home
index and cannot enable a runtime capability.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'engine'))
sys.path.insert(0, str(ROOT / 'tools'))

import audit_publish_metadata as metadata_audit
import headless_runtime as runtime
from runtime_profiles import PROFILE_1140_BUILD481


def verdict(source: dict, candidates: list[dict]) -> dict:
    comparisons = [candidate['comparison'] for candidate in candidates]
    exact = [item['bytes_equal'] and item['mode_equal'] and item['owner_group_equal']
             and item['acl_equal'] and item['xattrs_equal'] for item in comparisons]
    return {
        'all_exact': all(exact),
        'exact_runs': sum(exact),
        'run_count': len(exact),
        'changed_xattrs_by_run': [item['xattr_changed_names'] for item in comparisons],
        'source_sha256': source['sha256'],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--runs', type=int, default=3)
    args = parser.parse_args()
    if args.runs < 1 or args.runs > 10:
        raise SystemExit('--runs must be between 1 and 10')
    out = args.out.expanduser().resolve()
    work = (ROOT / 'work').resolve()
    if out == work or work not in out.parents or out.exists():
        raise SystemExit('--out must be a new child of this checkout work/')

    identity = runtime.doctor()
    if identity['profile_id'] != PROFILE_1140_BUILD481:
        raise SystemExit('live staging audit requires the exact Build 481 profile')
    helper = runtime.helper()
    helper._ensure_editor_closed(True)
    index = runtime.DRAFT_ROOT / 'root_meta_info.json'
    snapshot = helper._snapshot_file(index, 'home index staging audit')
    source = metadata_audit.metadata(index)
    out.mkdir(parents=True, mode=0o700)

    candidates = []
    for number in range(1, args.runs + 1):
        helper._ensure_editor_closed(True)
        helper._revalidate_snapshot(snapshot, 'before live staging audit run')
        name = '.root_meta_info.headless-stage-audit-' + uuid.uuid4().hex + '.tmp'
        candidate = runtime.DRAFT_ROOT / name
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
        descriptor = os.open(candidate, flags, snapshot.mode)
        try:
            offset = 0
            while offset < len(snapshot.content):
                written = os.write(descriptor, snapshot.content[offset:])
                if written <= 0:
                    raise OSError('short write during live staging audit')
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.chmod(candidate, snapshot.mode)
        for key, value in source['xattrs'].items():
            try:
                subprocess.run(['/usr/bin/xattr', '-wx', key, value, str(candidate)],
                               check=True, capture_output=True)
            except (OSError, subprocess.SubprocessError):
                raise ValueError('extended attribute copy failed') from None
        observed = metadata_audit.metadata(candidate)
        observed['run'] = number
        observed['temporary_name'] = name
        observed['comparison'] = metadata_audit.comparison(source, observed)
        candidates.append(observed)
        helper._revalidate_snapshot(snapshot, 'after live staging audit run')

    result = verdict(source, candidates)
    report = {
        'schema': 'jianying-publish-live-staging-audit/v1',
        'profile_id': identity['profile_id'],
        'source': source,
        'candidates': candidates,
        'verdict': result,
        'capability_changed': False,
        'live_index_replaced': False,
        'draft_directory_created': False,
        'temporary_files_retained': True,
    }
    (out / 'report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
