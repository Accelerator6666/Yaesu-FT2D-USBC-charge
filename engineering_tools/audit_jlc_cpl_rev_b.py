"""Compare preview CPL against all BOM-relevant, populated board SMT parts.

Does not certify manufacturer's pick-place center or rotation conventions.
"""

import csv
import sys
import pcbnew as p


def main(board_path, cpl_path):
    b = p.LoadBoard(board_path)
    expected = {
        fp.GetReference(): fp for fp in b.GetFootprints()
        if fp.GetAttributes() & p.FP_SMD
        and not fp.GetAttributes() & p.FP_DNP
        and not fp.GetAttributes() & p.FP_EXCLUDE_FROM_POS_FILES
    }
    with open(cpl_path, encoding='utf-8-sig', newline='') as f:
        positions = list(csv.DictReader(f))
    refs = [row['Ref'] for row in positions]
    assert len(refs) == len(set(refs)), 'Duplicate references in CPL'
    assert set(refs) == set(expected), (
        'CPL missing', sorted(set(expected)-set(refs)),
        'CPL extras', sorted(set(refs)-set(expected)))
    for row in positions:
        fp = expected[row['Ref']]
        assert abs(float(row['PosX']) - p.ToMM(fp.GetPosition().x)) < .002
        assert abs(float(row['PosY']) + p.ToMM(fp.GetPosition().y)) < .002
    print('CPL geometry membership PASS:', len(refs), 'all non-DNP SMT devices')
    print('J1 angle', next(r['Rot'] for r in positions if r['Ref'] == 'J1'))
    print('L1 package', next(r['Package'] for r in positions if r['Ref'] == 'L1'))
    print('NOT verified: JLC preview orientation, component center, feeder acceptance')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: audit_jlc_cpl_rev_b.py PCB.kicad_pcb CPL.csv')
    main(*sys.argv[1:])
