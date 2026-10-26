"""Generate strictly NON-APPROVED JLC-format BOM/CPL candidate review files.

This intentionally does not produce the release gate's BOM_APPROVED.csv or
CPL_APPROVED.csv. LCSC catalog matches do not establish JLC SMT stock,
footprint suitability, rotation/polarity, or engineering approval.
"""

import csv
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'manufacturing/Rev_B/REVIEW_ONLY_NOT_FOR_FAB'

# (Designators, LCSC code, candidate manufacturer's part number, risk code)
# Catalog search 2026-10-26: no listed selection is approved for purchasing.
PARTS = [
    ('C1 C2', 'C5332007', 'C1608X7R1A105K080AC', 'BIAS'),
    ('C3 C5', 'C1712', 'CL21B105KAFNFNE', 'BIAS'),
    ('C4', 'C380378', 'C1608X7R1H473KT000N', 'NORMAL'),
    ('C10', 'C194115', 'CGA3E1X7R1C105K080AC', 'BIAS'),
    ('C12 C13', 'C2167477', 'C1608X7R1H104K080AE', 'NORMAL'),
    ('C14 C15 C16 C17', 'C77102', 'GRM32ER71H106KA12L', 'DC_BIAS_CRITICAL'),
    ('C18', 'C178639', 'EEHZA1V470P', 'THERMAL_POLARITY'),
    ('C19 C24', 'C85861', 'GCM188R71E104KA57D', 'NORMAL'),
    ('C26', 'C415535', 'GRM188Z71E225KE43D', 'OUT_DECOUPLING_BIAS'),
    ('C20 C21 C22 C25', 'C3848311', '1210X476M250CT', 'DC_BIAS_CRITICAL'),
    ('C23', 'C46550464', 'MA25V220M6X8', 'THERMAL_ESR_POLARITY'),
    ('C27', 'C77036', 'GRM1885C1H332JA01D', 'NORMAL'),
    ('C28', 'C77033', 'GRM1885C1H222JA01D', 'NORMAL'),
    ('D1', 'C1974707', 'ESDA25P35-1U1M', 'TVS_PINOUT'),
    ('D2', 'C2935152', 'ESDA25W', 'TVS_PINOUT'),
    ('F1', 'C41342', '0468003.NRHF', 'FUSE_THERMAL'),
    ('J1', 'C165948', 'TYPE-C-31-M-12', 'MIXED_THT_SMT'),
    ('L1', 'C53463013', 'SRG1260-100-M', 'CURRENT_LAND_PATTERN'),
    ('Q1', 'C457492', 'STL6P3LLH6', 'PINOUT_THERMAL'),
    ('R1 R18 R23', 'C98220', 'RC0603FR-0710KL', 'NORMAL'),
    ('R2 R3', 'C99782', 'RC0603FR-074K7L', 'NORMAL'),
    ('R4', 'C22548', 'RC0603FR-071KL', 'NORMAL'),
    ('R5', 'C5717132', 'RC0603FR-1322KP', 'NORMAL'),
    ('R6', 'C114669', 'RC0603FR-07470RL', 'NORMAL'),
    ('R7 R15 R21 R24', 'C14675', 'RC0603FR-07100KL', 'NORMAL'),
    ('R12', 'C122538', 'RT0603BRD07100KL', 'PRECISION_0P1'),
    ('R13', 'C861591', 'RT0603BRD078K66L', 'PRECISION_0P1'),
    ('R16', 'C227824', 'AC0603FR-0733K2L', 'NORMAL'),
    ('R17', 'C2484234', 'RMCF0603FT133K', 'NORMAL'),
    ('R19', 'C95177', 'RC0603JR-070RL', 'ZERO_OHM'),
    ('R20', 'C103658', 'RTT034703FTP', 'NORMAL'),
    ('R22', 'C861068', 'RT0603BRD07102KL', 'OVLO_102K_SMT_CONFIRMED'),
    ('R25', 'C114659', 'RC0603FR-0712KL', 'NORMAL'),
    ('R26', 'C23253', '0603WAF8200T5E', 'NORMAL'),
    ('U1', 'C2678061', 'STUSB4500QTR', 'NVM_CONFIG_PIN1'),
    ('U2', 'C1855832', 'LM61460AASQRJRRQ1', 'THERMAL_PIN1'),
    ('U3', 'C3662807', 'TPS259474ARPWR', 'CURRENT_LIMIT_PIN1'),
]


def read_csv(path):
    with path.open(newline='', encoding='utf-8-sig') as source:
        return list(csv.DictReader(source))


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    bom = read_csv(REVIEW / 'kicad_bom_unverified.csv')
    native = read_csv(REVIEW / 'kicad_positions_unverified.csv')
    allowed = {row['Refs']: row for row in bom if row['DNP'].strip() != 'DNP' and row['Refs'] not in {'J2', 'J3'}}
    placements = {row['Ref']: row for row in native}
    candidates = {}
    for refs, code, mpn, risk in PARTS:
        if not re.fullmatch(r'C[1-9][0-9]*', code):
            raise ValueError(f'Invalid C-code {code}')
        for ref in refs.split():
            if ref in candidates:
                raise ValueError(f'Duplicate candidate: {ref}')
            candidates[ref] = (code, mpn, risk)
    if set(allowed) != set(placements) or set(allowed) != set(candidates):
        raise ValueError(f'Incomplete candidates: BOM-only={set(allowed)-set(candidates)}; extra={set(candidates)-set(allowed)}; not in CPL={set(allowed)-set(placements)}')

    bom_review = []
    trace = []
    cpl_review = []
    for ref, row in allowed.items():
        code, mpn, risk = candidates[ref]
        # Use the candidate MPN as Comment to avoid claiming the old physical
        # part is being purchased (C18, C23 and F1 are substitutions).
        bom_review.append({'Comment': mpn, 'Designator': ref, 'Footprint': row['Footprint'], 'JLCPCB Part #': code})
        trace.append({'Ref': ref, 'Schematic Value': row['Value'], 'Candidate MPN': mpn,
                      'Candidate LCSC Code': code, 'Review Class': risk,
                      'Source (catalog, not SMT approval)': f'https://www.lcsc.com/product-detail/{code}.html',
                      'Approval': 'NOT APPROVED'})
        p = placements[ref]
        cpl_review.append({'Designator': ref, 'Mid X': p['PosX'], 'Mid Y': p['PosY'],
                           'Rotation': p['Rot'], 'Layer': 'top'})

    write_csv(REVIEW / 'JLC_CANDIDATE_BOM_NOT_APPROVED.csv',
              ['Comment', 'Designator', 'Footprint', 'JLCPCB Part #'], bom_review)
    write_csv(REVIEW / 'JLC_CANDIDATE_CPL_NOT_APPROVED.csv',
              ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'], cpl_review)
    write_csv(REVIEW / 'SMT_CANDIDATE_TRACEABILITY_NOT_APPROVED.csv',
              ['Ref', 'Schematic Value', 'Candidate MPN', 'Candidate LCSC Code',
               'Review Class', 'Source (catalog, not SMT approval)', 'Approval'], trace)
    print(f'{len(candidates)}/{len(placements)} SMT refs mapped to {len(PARTS)} candidate part groups (NOT APPROVED)')


if __name__ == '__main__':
    main()
