"""Cross-check a proposed JLCPCB BOM/CPL against KiCad's native SMT placement.

Fail closed on missing/extra/duplicate/unsourced designators or impossible
coordinates. This is not a substitute for online JLCPCB assembly preview,
manual polarity/rotation check, material compatibility, or power signoff.
"""

import csv
import math
from pathlib import Path
import re
import sys


LCSC_CODE = re.compile(r'C[1-9][0-9]*\Z')
REF = re.compile(r'[A-Z][A-Z0-9]*[0-9]+\Z')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f'{path}: empty CSV or missing header')
        return reader.fieldnames, list(reader)


def require_columns(found, required, origin):
    missing = set(required) - set(found)
    if missing:
        raise ValueError(f'{origin}: missing columns {sorted(missing)}')


def single_reference(text):
    value = text.strip().upper()
    if not REF.fullmatch(value):
        raise ValueError(f'Invalid/unsupported designator {text!r}; use comma-separated explicit refs')
    return value


def parse_bom_references(text):
    # A BOM may group same-part designators in one row: "R2, R3".
    result = [single_reference(x) for x in text.replace(';', ',').split(',')]
    if len(set(result)) != len(result):
        raise ValueError(f'Duplicate refs within BOM cell: {text!r}')
    return result


def main(bom_file: Path, cpl_file: Path, native_pos_file: Path):
    native_columns, native_rows = read_csv(native_pos_file)
    require_columns(native_columns, ('Ref', 'PosX', 'PosY', 'Rot', 'Side'), native_pos_file)
    native = {single_reference(row['Ref']): row for row in native_rows}
    if len(native) != len(native_rows) or not native:
        raise ValueError('KiCad reference placement list empty or duplicated')

    bom_columns, bom_rows = read_csv(bom_file)
    required_bom = ('Comment', 'Designator', 'Footprint')
    require_columns(bom_columns, required_bom, bom_file)
    part_column = next((n for n in ('JLCPCB Part #', 'LCSC Part #') if n in bom_columns), None)
    if not part_column:
        raise ValueError('BOM needs JLCPCB Part # or LCSC Part # column')
    mapped = {}
    for i, row in enumerate(bom_rows, start=2):
        if not row.get('Comment', '').strip() or not row.get('Footprint', '').strip():
            raise ValueError(f'BOM row {i}: missing comment or footprint')
        code = (row.get(part_column) or '').strip().upper()
        if not LCSC_CODE.fullmatch(code):
            raise ValueError(f'BOM row {i}: missing/invalid JLC C-code {code!r}')
        for ref in parse_bom_references(row.get('Designator', '')):
            if ref in mapped:
                raise ValueError(f'BOM duplicate {ref}: rows {mapped[ref][0]} and {i}')
            mapped[ref] = (i, code)

    if set(mapped) != set(native):
        raise ValueError(f'BOM membership difference: missing {sorted(set(native)-set(mapped))}; extra {sorted(set(mapped)-set(native))}')

    cpl_columns, cpl_rows = read_csv(cpl_file)
    require_columns(cpl_columns, ('Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'), cpl_file)
    placed = set()
    orientations_changed = []
    y_sign = set()
    for i, row in enumerate(cpl_rows, start=2):
        ref = single_reference(row['Designator'])
        if ref not in native:
            raise ValueError(f'CPL row {i}: unknown/non-SMT/DNP ref {ref}')
        if ref in placed:
            raise ValueError(f'CPL row {i}: duplicate {ref}')
        placed.add(ref)
        native_row = native[ref]
        x, y, angle = [float(row[col]) for col in ('Mid X', 'Mid Y', 'Rotation')]
        nx, ny, na = [float(native_row[col]) for col in ('PosX', 'PosY', 'Rot')]
        if not all(math.isfinite(n) for n in (x, y, angle)):
            raise ValueError(f'CPL row {i}: non-finite coordinate or angle')
        if abs(x - nx) > .05 or abs(abs(y) - abs(ny)) > .05:
            raise ValueError(f'CPL {ref}: does not match KiCad pad-center X / |Y| within 0.05 mm')
        sign = 'positive' if y >= 0 else 'negative'
        y_sign.add(sign)
        if row['Layer'].strip().lower() not in {'top', 'front'}:
            raise ValueError(f'CPL {ref}: Rev B currently requires front-only SMT; got {row["Layer"]!r}')
        if abs(((angle-na+180)%360)-180)>.05:
            orientations_changed.append(ref)
    if placed != set(native):
        raise ValueError(f'CPL missing SMT refs: {sorted(set(native)-placed)}')
    if len(y_sign) != 1:
        raise ValueError(f'Mixed CPL Y axis signs {sorted(y_sign)}')
    print(f'SMT gate PASS: {len(mapped)} BOM refs, {len(placed)} CPL refs, every BOM line has a JLC C-code')
    print('CPL Y convention:', next(iter(y_sign)), '(still requires JLC online visual preview)')
    print('CPL rotations changed from KiCad:', ','.join(orientations_changed) or 'none')
    print('NOT APPROVED: component MPN compatibility, polarities/rotations, thermal/current and JLC preview')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('Usage: validate_jlc_smt_release_rev_b.py BOM_APPROVED.csv CPL_APPROVED.csv native_positions.csv')
    try:
        main(*(Path(v) for v in sys.argv[1:]))
    except (ValueError, KeyError) as exc:
        raise SystemExit(f'NO-GO: SMT verification failed: {exc}') from exc
