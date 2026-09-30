#!/usr/bin/env python3
"""Generate a reviewed local alias of one exact macOS STIX OTF.

This tool is intentionally restricted to /System/Library/Fonts/Supplemental/
STIXGeneral.otf with the reviewed source SHA-256. It never edits the source and
refuses to overwrite an existing output. It is not a general font converter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import fontTools
from fontTools.ttLib import TTFont

SOURCE = Path('/System/Library/Fonts/Supplemental/STIXGeneral.otf')
SOURCE_SHA256 = '5add3f3f2bd7fd897d2fa5ccbe468607c52111dc44cdfaaf2d851a574f5357a7'
OUTPUT_SHA256 = '154e149bfdd2daf1f9560b8103bc3484c327a4969710339ea9e8b5a1247a0717'
FONTTOOLS_VERSION = '4.60.2'
ALIAS_HEAD_MODIFIED = 3873110399  # Fixed from the GUI-tested byte-identical fixture.
FAMILY = 'Codex STIX Regular Probe'
FULL_NAME = 'Codex STIX Regular Probe Regular'
POSTSCRIPT_NAME = 'CodexSTIXRegularProbe-Regular'
UNIQUE_ID = 'CodexSTIXRegularProbe:1.1.0:Regular'
NAME_VALUES = {1: FAMILY, 3: UNIQUE_ID, 4: FULL_NAME, 6: POSTSCRIPT_NAME}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE,
                        help='must be the reviewed system STIXGeneral.otf')
    parser.add_argument('--output', required=True, type=Path,
                        help='new output path; existing files are never overwritten')
    args = parser.parse_args()

    if fontTools.__version__ != FONTTOOLS_VERSION:
        parser.error(f'fontTools {FONTTOOLS_VERSION} is required for byte-identical output; found {fontTools.__version__}')
    source = args.source.resolve(strict=True)
    if source != SOURCE.resolve(strict=True):
        parser.error(f'unsupported source path: {source}')
    source_hash = sha256(source)
    if source_hash != SOURCE_SHA256:
        parser.error(f'unsupported source SHA-256: {source_hash}')

    output = args.output.expanduser().absolute()
    if output.exists():
        parser.error(f'refusing to overwrite: {output}')
    output.parent.mkdir(parents=True, exist_ok=True)

    font = TTFont(source, recalcBBoxes=False, recalcTimestamp=False)
    for record in font['name'].names:
        if record.nameID in NAME_VALUES:
            encoding = record.getEncoding()
            record.string = NAME_VALUES[record.nameID].encode(encoding)
    cff = font['CFF '].cff
    cff.fontNames[0] = POSTSCRIPT_NAME
    top = cff.topDictIndex[0]
    top.FamilyName = FAMILY
    top.FullName = FULL_NAME
    # Reproduce the already GUI-tested alias exactly. fontTools also updates
    # head.checkSumAdjustment when saving the table directory.
    font['head'].modified = ALIAS_HEAD_MODIFIED
    try:
        with output.open('xb') as stream:
            font.save(stream)
    finally:
        font.close()

    output_hash = sha256(output)
    if output_hash != OUTPUT_SHA256:
        output.unlink(missing_ok=True)
        raise SystemExit(f'generated SHA-256 mismatch: expected {OUTPUT_SHA256}, got {output_hash}')

    result = {
        'status': 'generated',
        'source': str(source),
        'source_sha256': source_hash,
        'output': str(output),
        'output_sha256': output_hash,
        'fonttools_version': fontTools.__version__,
        'name_ids_changed': NAME_VALUES,
        'head_modified_timestamp_fixed_to_match_reviewed_fixture': ALIAS_HEAD_MODIFIED,
        'cff_names_changed': {
            'fontNames[0]': POSTSCRIPT_NAME,
            'FamilyName': FAMILY,
            'FullName': FULL_NAME,
        },
        'overwrote_source': False,
        'overwrote_output': False,
        'scope': 'STIXGeneral Regular source SHA only; reviewed alias, not a general OTF transform',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
