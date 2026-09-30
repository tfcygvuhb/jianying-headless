#!/usr/bin/env python3
"""Fail-closed check for a Build 481 editor identity evidence bundle.

This program never interacts with Jianying. It validates supplied lsof -Fn text,
Vision OCR JSON, and screenshot bytes against a requested draft identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any

DRAFT_ROOT = str(Path.home() / "Movies/JianyingPro/User Data/Projects/com.lveditor.draft")
DEFAULT_MIN_CONFIDENCE = 0.85


def reject(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def normalized_absolute(raw: str) -> str | None:
    if not raw.startswith("/") or "\x00" in raw:
        return None
    normalized = os.path.normpath(raw)
    if normalized != raw:
        return None
    return normalized


def is_under(path: str, parent: str) -> bool:
    return path == parent or path.startswith(parent.rstrip("/") + "/")


def parse_lsof(text: str) -> tuple[set[int], list[int], list[str]]:
    pids: set[int] = set()
    exits: list[int] = []
    paths: list[str] = []
    for line in text.splitlines():
        if line.startswith("pid="):
            raw = line[4:]
            if raw.isdigit():
                pids.add(int(raw))
        elif line.startswith("p") and line[1:].isdigit():
            pids.add(int(line[1:]))
        elif line.startswith("lsof_exit="):
            raw = line[len("lsof_exit="):]
            if raw.lstrip("-").isdigit():
                exits.append(int(raw))
        elif line.startswith("n/"):
            # -Fn encodes a path as one 'n' record. Do not split on spaces.
            paths.append(line[1:])
    return pids, exits, paths


def normalize_label(text: str) -> str:
    return text.strip().removesuffix(":").removesuffix("：").strip()


def ocr_box(item: dict[str, Any]) -> tuple[float, float, float, float] | None:
    try:
        box = tuple(float(item[key]) for key in ('x', 'y', 'width', 'height'))
    except (KeyError, TypeError, ValueError):
        return None
    x, y, width, height = box
    if not all(math.isfinite(value) for value in box) or not (0 <= x < 1 and 0 <= y < 1 and
            0 < width <= 1 - x and 0 < height <= 1 - y):
        return None
    return box


def ocr_center_y(item: dict[str, Any]) -> float:
    box = ocr_box(item)
    return box[1] + box[3] / 2 if box is not None else float('nan')


def beside_label(label: dict[str, Any], value: dict[str, Any]) -> bool:
    left, right = ocr_box(label), ocr_box(value)
    if left is None or right is None:
        return False
    lx, ly, lw, lh = left
    vx, vy, _, vh = right
    return vx >= lx + lw - 0.01 and abs((ly + lh / 2) - (vy + vh / 2)) <= max(0.025, 1.5 * max(lh, vh))


def name_sequences(items: list[dict[str, Any]], label: dict[str, Any], name: str) -> list[list[dict[str, Any]]]:
    """Read only an exact OCR value beside 草稿名称, including bounded line wraps."""
    save_labels = [item for item in items if isinstance(item.get('text'), str)
                   and normalize_label(item['text']) == '保存位置' and ocr_box(item) is not None]
    save_boundary = ocr_center_y(save_labels[0]) if len(save_labels) == 1 else None
    sequences = []
    for first in items:
        part = first.get('text')
        if not isinstance(part, str):
            continue
        part = part.strip()
        if not part or not name.startswith(part) or not beside_label(label, first):
            continue
        sequence = [first]
        assembled = part
        while assembled != name and len(sequence) < 4 and save_boundary is not None:
            previous = sequence[-1]
            px, py, _, ph = ocr_box(previous)
            previous_center = py + ph / 2
            possible = []
            for item in items:
                if item in sequence or not isinstance(item.get('text'), str) or not item['text'].strip():
                    continue
                box = ocr_box(item)
                if box is None:
                    continue
                x, y, _, height = box
                center = y + height / 2
                gap = py - (y + height)
                if (abs(x - px) <= max(.004, .25 * max(ph, height)) and
                        center < previous_center - .5 * min(ph, height) and
                        center > save_boundary + .005 and
                        -.003 <= gap <= 1.25 * max(ph, height)):
                    possible.append((center, item))
            if not possible:
                break
            nearest = max(center for center, _ in possible)
            next_line = [item for center, item in possible if abs(center - nearest) <= .005]
            if len(next_line) != 1:
                break
            next_item = next_line[0]
            next_part = next_item['text'].strip()
            if not name.startswith(assembled + next_part):
                break
            sequence.append(next_item)
            assembled += next_part
        if assembled == name:
            sequences.append(sequence)
    return sequences


def load_evidence(screenshot: Path, ocr_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]], str]:
    problems: list[dict[str, str]] = []
    screenshot_sha = hashlib.sha256(screenshot.read_bytes()).hexdigest()
    payload = json.loads(ocr_path.read_text())
    if not isinstance(payload, dict) or payload.get('status') != 'captured' or \
            payload.get('schema') != 'build481-editor-identity-capture/v1' or \
            not isinstance(payload.get('vision'), dict) or \
            not isinstance(payload['vision'].get('items'), list):
        return [], [reject("ocr-envelope-invalid", "capture must contain a successful Vision evidence envelope")], screenshot_sha
    if payload.get("screenshotSHA256") != screenshot_sha:
        problems.append(reject("screenshot-hash-mismatch", "OCR envelope is not bound to the supplied screenshot bytes"))
    if payload.get('bundleID') != 'com.lemon.lvpro' or \
            not isinstance(payload.get('pid'), int) or \
            not isinstance(payload.get('cgWindowID'), int) or \
            payload.get('windowTitle') != '剪映专业版' or \
            payload.get('screenshot') != screenshot.name:
        problems.append(reject('capture-binding-invalid', 'capture PID/window metadata is missing or unexpected'))
    items = payload['vision']['items']
    if not all(isinstance(item, dict) for item in items):
        problems.append(reject("ocr-items-invalid", "OCR items must be JSON objects"))
        return [], problems, screenshot_sha
    return items, problems, screenshot_sha


def evaluate(name: str, target: str, pid: int, lsof_text: str,
             screenshot: Path, ocr_path: Path,
             min_confidence: float = DEFAULT_MIN_CONFIDENCE) -> dict[str, Any]:
    reasons: list[dict[str, str]] = []
    expected_target = normalized_absolute(target)
    if expected_target is None:
        reasons.append(reject("target-not-canonical-absolute", "target must be an absolute normalized path"))
    elif Path(expected_target).name != name:
        reasons.append(reject("name-target-mismatch", "target basename must equal expected name"))
    elif not is_under(expected_target, DRAFT_ROOT) or expected_target == DRAFT_ROOT:
        reasons.append(reject("target-outside-draft-root", "target must be a child of the configured local draft root"))
    if not name or name in (".", "..") or "/" in name:
        reasons.append(reject("invalid-name", "expected name must be one path component"))
    if not math.isfinite(min_confidence) or not 0.0 <= min_confidence <= 1.0:
        reasons.append(reject("invalid-confidence-threshold", "min_confidence must be finite and in [0,1]"))
    if pid <= 0:
        reasons.append(reject("invalid-pid", "PID must be a positive integer"))

    pids, exits, paths = parse_lsof(lsof_text)
    if len(pids) != 1:
        reasons.append(reject("lsof-pid-not-unique", f"expected one PID declaration, found {sorted(pids)}"))
    elif pid not in pids:
        reasons.append(reject("lsof-pid-mismatch", f"lsof PID {next(iter(pids))} does not match current PID {pid}"))
    if len(exits) != 1 or exits[0] != 0:
        reasons.append(reject("lsof-not-successful", f"expected one lsof_exit=0 record, found {exits}"))

    if expected_target is not None:
        root = DRAFT_ROOT
        normalized_paths: list[str] = []
        malformed_paths: list[str] = []
        for path in paths:
            if not path.startswith('/'):
                continue  # sockets, pipes and device names cannot identify a draft
            normalized = normalized_absolute(path)
            if normalized is None:
                malformed_paths.append(path)
            else:
                normalized_paths.append(normalized)
        if malformed_paths:
            reasons.append(reject("lsof-path-invalid", f"noncanonical path records: {malformed_paths}"))
        draft_paths = [p for p in normalized_paths if is_under(p, root)]
        if not draft_paths:
            reasons.append(reject("no-draft-handles", "lsof contains no handle under the configured draft root"))
        foreign = sorted({p for p in draft_paths if not is_under(p, expected_target)})
        if foreign:
            reasons.append(reject("foreign-draft-handles", f"draft-root handles outside target: {foreign}"))
        locked = [p for p in normalized_paths if PurePosixPath(p).name == ".locked" and is_under(p, root)]
        expected_lock = expected_target.rstrip("/") + "/.locked"
        if len(locked) != 1 or locked[0] != expected_lock:
            reasons.append(reject("target-lock-not-unique", f"expected exactly one {expected_lock}; found {locked}"))

    try:
        items, evidence_problems, screenshot_sha = load_evidence(screenshot, ocr_path)
        reasons.extend(evidence_problems)
        envelope = json.loads(ocr_path.read_text())
        if isinstance(envelope, dict) and envelope.get('pid') != pid:
            reasons.append(reject('capture-pid-mismatch', 'captured PID differs from the lsof/current editor PID'))
    except (OSError, json.JSONDecodeError) as error:
        items, screenshot_sha = [], ""
        reasons.append(reject("evidence-unreadable", str(error)))

    labels = [item for item in items
              if isinstance(item.get("text"), str) and normalize_label(item["text"]) == "草稿名称"]
    if len(labels) != 1:
        reasons.append(reject("draft-name-label-not-unique", f"expected one 草稿名称 label, found {len(labels)}"))
    sequences = name_sequences(items, labels[0], name) if len(labels) == 1 else []
    if len(sequences) != 1:
        reasons.append(reject("exact-name-not-unique", f"expected one exact name beside 草稿名称, found {len(sequences)}"))
    if len(labels) == 1 and len(sequences) == 1:
        label, value = labels[0], sequences[0][0]
        try:
            label_conf = float(label["confidence"])
            value_conf = min(float(item['confidence']) for item in sequences[0])
        except (KeyError, TypeError, ValueError):
            reasons.append(reject("ocr-geometry-invalid", "name label/value lacks numeric confidence or bounding box"))
        else:
            if (not math.isfinite(label_conf) or not math.isfinite(value_conf) or
                    not 0.0 <= label_conf <= 1.0 or not 0.0 <= value_conf <= 1.0 or
                    min(label_conf, value_conf) < min_confidence):
                reasons.append(reject("name-confidence-low", f"label={label_conf:.3f}, value={value_conf:.3f}, threshold={min_confidence:.3f}"))
            if ocr_box(label) is None or any(ocr_box(item) is None for item in sequences[0]):
                reasons.append(reject("ocr-geometry-invalid", "OCR boxes must be finite normalized coordinates in [0,1]"))
            elif not beside_label(label, value):
                reasons.append(reject("name-not-adjacent-to-label", "exact name OCR is not to the right of and aligned with 草稿名称"))

    if expected_target is not None:
        target_resources = expected_target.rstrip('/') + '/Resources/'
        if not any(path.startswith(target_resources) for path in paths):
            reasons.append(reject('target-resource-handle-missing',
                                  'current editor PID has no open resource under the expected draft'))

    return {
        "status": "verified" if not reasons else "rejected",
        "expected_name": name,
        "expected_target": target,
        "pid": pid,
        "screenshot_sha256": screenshot_sha,
        "lsof_path_record_count": len(paths),
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--lsof", required=True, type=Path, help="saved lsof -Fn text, with PID/exit metadata")
    parser.add_argument("--screenshot", required=True, type=Path)
    parser.add_argument("--ocr", required=True, type=Path, help="Vision evidence envelope bound to screenshot SHA-256")
    parser.add_argument("--min-confidence", type=float, default=DEFAULT_MIN_CONFIDENCE)
    args = parser.parse_args()
    try:
        result = evaluate(args.name, args.target, args.pid, args.lsof.read_text(),
                          args.screenshot, args.ocr, args.min_confidence)
    except OSError as error:
        result = {"status": "rejected", "reasons": [reject("input-unreadable", str(error))]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
