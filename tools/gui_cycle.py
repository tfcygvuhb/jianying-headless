#!/usr/bin/env python3
"""Verify an isolated Build 481 draft through native GUI save and cold reopen.

This is an acceptance tool, not a general editor. It refuses a running Jianying
session so it cannot replace the user's current project. All output stays in a
fresh work/ directory; failures keep their evidence and leave the app alone.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work'
APP = Path('/Applications/VideoFusion-macOS.app')
MAIN = str(APP / 'Contents/MacOS/VideoFusion-macOS')
BUNDLE = 'com.lemon.lvpro'
AX_SOURCE = Path(__file__).with_name('jianying_ax.swift')
IDENTITY_SOURCE = Path(__file__).with_name('jianying_capture_identity.swift')
IDENTITY_VERIFIER = Path(__file__).with_name('jianying_identity_verifier.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def file_hashes(folder):
    found = {}
    for path in sorted(folder.rglob('*')):
        require(not path.is_symlink(), 'live draft contains a symlink; refusing GUI acceptance')
        if path.is_file():
            found[str(path.relative_to(folder))] = digest(path)
    return found


def manifest_sha256(entries):
    return hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main_pid():
    found = subprocess.run(['pgrep', '-f', '^' + re.escape(MAIN) + '($| )'],
                           capture_output=True, text=True, check=False)
    return [int(value) for value in found.stdout.split()]


def command(argv, timeout=30):
    done = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if done.returncode:
        raise RuntimeError('%s failed (%s): %s' % (argv[0], done.returncode,
                           (done.stderr or done.stdout).strip()[:1200]))
    return done.stdout.strip()


def wait_ax(binary, role, field, value, seconds=25):
    until = time.monotonic() + seconds
    while time.monotonic() < until:
        done = subprocess.run([str(binary), 'check', BUNDLE, role, field, value],
                              cwd=ROOT, capture_output=True, text=True)
        if done.returncode == 0:
            return
        time.sleep(.4)
    raise RuntimeError('AX target was not uniquely visible: %s %s=%s' % (role, field, value))


def verify(build):
    report = json.loads(command([sys.executable, str(ROOT / 'engine/jy14_headless.py'),
                                 'verify', '--build', str(build)], timeout=120))
    require(report.get('status') == 'verified' and report.get('four_mirrors_equal') is True and
            report.get('source_files_unchanged') is True, 'live draft verification failed')
    return report


def open_target(binary, name):
    wait_ax(binary, 'AXWindow', 'title', '剪映专业版')
    pids = main_pid()
    require(len(pids) == 1, 'Jianying main PID is not unique on the home page')
    command(['osascript', '-e',
             'tell application "System Events" to set frontmost of first application process whose unix id is %d to true'
             % pids[0]])
    command([str(binary), 'set', BUNDLE, 'AXTextField', 'description', '', name])
    wait_ax(binary, 'AXStaticText', 'description', 'HomePageDraftTitle:' + name)
    command([str(binary), 'click-card', BUNDLE, name])


def launch_and_open(binary, name):
    command([str(binary), 'session', BUNDLE])
    require(not main_pid(), 'Jianying main process is already running; preserve the current session')
    command(['open', '-b', BUNDLE])
    open_target(binary, name)


def quit_and_confirm(binary):
    command([str(binary), 'quit', BUNDLE], timeout=30)
    require(not main_pid(), 'Jianying main process remained after normal Quit')


def draft_lsof(pid, path):
    done = subprocess.run(['lsof', '-nP', '-Fn', '-p', str(pid)],
                          capture_output=True, text=True, timeout=20)
    draft_root = str(Path.home() / 'Movies/JianyingPro/User Data/Projects/com.lveditor.draft') + '/'
    records = [line for line in done.stdout.splitlines()
               if line == 'p' + str(pid) or line.startswith('n' + draft_root)]
    path.write_text('pid=%d\nlsof_exit=%d\n%s\n' %
                    (pid, done.returncode, '\n'.join(records)))
    require(done.returncode == 0, 'lsof could not inspect the active editor PID')


def editor_identity(ax_binary, capture_binary, name, target, directory):
    """Bind visible editor name and open draft files to one current PID."""
    wait_ax(ax_binary, 'AXStaticText', 'description', 'MainTimeLineRoot')
    pids = main_pid()
    require(len(pids) == 1, 'editor main PID is not unique')
    pid = pids[0]
    directory.mkdir(parents=True, exist_ok=False)
    before_path = directory / 'lsof-before.txt'
    after_path = directory / 'lsof-after.txt'
    draft_lsof(pid, before_path)
    capture_dir = directory / 'capture'
    command([str(capture_binary), '--out-dir', str(capture_dir)], timeout=60)
    require(main_pid() == [pid], 'editor PID changed during identity capture')
    draft_lsof(pid, after_path)
    sys.path.insert(0, str(IDENTITY_VERIFIER.parent))
    from jianying_identity_verifier import evaluate
    screenshot = capture_dir / 'editor-window.png'
    envelope = capture_dir / 'identity-evidence.json'
    results = [evaluate(name, str(target), pid, path.read_text(), screenshot, envelope)
               for path in (before_path, after_path)]
    (directory / 'identity-result.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    require(all(result['status'] == 'verified' for result in results),
            'active editor identity did not match the requested draft')
    require(main_pid() == [pid], 'editor PID changed after identity verification')
    return {'pid': pid, 'capture': str(capture_dir), 'lsof_before': str(before_path),
            'lsof_after': str(after_path), 'checks': results}


def run(args):
    build = Path(args.build).resolve(strict=True)
    out = Path(args.out).resolve()
    require(WORK.resolve() in build.parents, 'build must be an isolated work/ build')
    require(WORK.resolve() in out.parents and not out.exists(), 'output must be a fresh work/ directory')
    require(not main_pid(), 'Jianying main process is already running; preserve the current session')
    require(1 <= args.rounds <= 3, 'rounds must be 1..3')
    record = json.loads((build / 'build.json').read_text())
    name = record['name']
    require(name.startswith(('Build481-', 'Codex-', 'MediaCoverage-')),
            'this acceptance tool only operates named isolated drafts')
    target = Path(record['target']).resolve(strict=True)
    live_root = Path.home() / 'Movies/JianyingPro/User Data/Projects/com.lveditor.draft'
    require(target.parent == live_root.resolve() and target.name == name,
            'build target is not the matching local draft')
    sys.path.insert(0, str(ROOT / 'engine'))
    import headless_runtime as runtime
    identity = runtime.validate_runtime()
    require(identity['runtime_profile'] == 'jy14-headless-macos-11.4.0-build481' and
            record['runtime_profile'] == identity['runtime_profile'] and
            record['runtime']['libvideoeditor_sha256'] == identity['libvideoeditor_sha256'] and
            record['runtime']['codec_sha256'] == identity['codec_sha256'],
            'Build 481 runtime fingerprint changed')
    assets = record.get('assets', [])
    source_before = {asset['source']: digest(asset['source']) for asset in assets}
    require(all(source_before[asset['source']] == asset['sha256'] for asset in assets),
            'source asset changed before GUI acceptance')
    preflight = verify(build)
    require(preflight['name'] == name, 'live draft changed before GUI acceptance')
    out.mkdir(mode=0o700)
    binary = out / 'jianying_ax'
    command(['swiftc', str(AX_SOURCE), '-o', str(binary)], timeout=120)
    capture_binary = out / 'jianying_capture_identity'
    command(['swiftc', str(IDENTITY_SOURCE), '-o', str(capture_binary)], timeout=120)
    summary = {'schema': 'build481-gui-cycle/v1', 'status': 'running', 'name': name,
               'build': str(build), 'target': str(target), 'runtime': identity,
               'ax_source_sha256': digest(AX_SOURCE), 'source_sha256_before': source_before,
               'identity_source_sha256': digest(IDENTITY_SOURCE),
               'identity_verifier_sha256': digest(IDENTITY_VERIFIER),
               'rounds': []}
    report_path = out / 'result.json'
    try:
        for number in range(1, args.rounds + 1):
            preflight = verify(build)
            require(preflight['name'] == name, 'live draft changed before GUI acceptance')
            before = file_hashes(target)
            launch_and_open(binary, name)
            first = verify(build)
            require(first['name'] == name, 'opened draft name does not match the requested build')
            opened_identity = editor_identity(binary, capture_binary, name, target,
                                              out / ('round-%d-open' % number))
            command([str(binary), 'save', BUNDLE, str(target)])
            saved_identity = editor_identity(binary, capture_binary, name, target,
                                             out / ('round-%d-saved' % number))
            saved = verify(build)
            require(saved['name'] == name, 'saved draft name changed')
            quit_and_confirm(binary)
            launch_and_open(binary, name)
            cold_identity = editor_identity(binary, capture_binary, name, target,
                                            out / ('round-%d-cold' % number))
            cold = verify(build)
            require(cold['name'] == name and cold['duration_us'] == first['duration_us'] and
                    cold['tracks'] == first['tracks'], 'cold reopen changed the planned timeline')
            quit_and_confirm(binary)
            source_after = {asset['source']: digest(asset['source']) for asset in assets}
            require(source_after == source_before, 'source asset changed during GUI acceptance')
            after = file_hashes(target)
            summary['rounds'].append({'round': number, 'preflight': preflight,
                                      'before': first, 'saved': saved,
                                      'cold_reopen': cold, 'editor_identity': {
                                          'opened': opened_identity, 'saved': saved_identity,
                                          'cold_reopen': cold_identity},
                                      'source_sha256_after': source_after,
                                      'draft_manifest_sha256_before': manifest_sha256(before),
                                      'draft_manifest_sha256_after': manifest_sha256(after),
                                      'draft_files_before': len(before), 'draft_files_after': len(after),
                                      'draft_files_added': sorted(after.keys() - before.keys()),
                                      'draft_files_removed': sorted(before.keys() - after.keys()),
                                      'draft_files_changed': sorted(k for k in before.keys() & after.keys()
                                                                    if before[k] != after[k])})
            report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
        summary['status'] = 'verified'
    except Exception as error:
        summary['status'] = 'failed'
        summary['error'] = str(error)
        report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
        raise
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'rounds': len(summary['rounds']),
                      'name': name, 'result': str(report_path)}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--rounds', type=int, default=1)
    run(parser.parse_args())
