"""Read-only physical-copper inventory; DRC and area do not certify 3 A load.

Run with KiCad 10's /usr/bin/python3 pcbnew interpreter. The minimum width
counts original fine-neck track geometry, while zone area counts *filled*
top-layer polygons. Current paths and local thermal rise require separate
physical/electrical analysis before any manufacture signoff.
"""

from collections import defaultdict
from pathlib import Path
import sys

import pcbnew as p


def main(board_path: Path):
    board = p.LoadBoard(str(board_path))
    groups = defaultdict(lambda: dict(n=0, length=0., minimum=1e9, vias=0, area=0.))
    for item in board.GetTracks():
        name = item.GetNetname()
        if name not in {'/USB_VBUS', '/VBUS_RAW', '/VBUS_SW', '/SW', '/V12P5', '/VOUT'}:
            continue
        g = groups[name]
        if isinstance(item, p.PCB_VIA):
            g['vias'] += 1
        elif isinstance(item, p.PCB_TRACK) and item.GetLayer() == p.F_Cu:
            g['n'] += 1
            g['length'] += p.ToMM(item.GetLength())
            g['minimum'] = min(g['minimum'], p.ToMM(item.GetWidth()))
    for zone in board.Zones():
        name = zone.GetNetname()
        if zone.GetLayer() == p.F_Cu and name in groups:
            g = groups[name]
            g['area'] += zone.GetFilledPolysList(p.F_Cu).Area() / (10**12)
    print('Net | F.Cu filled zone area mm² | F.Cu tracks | track length mm | narrowest original track mm | full-through vias')
    for name in ('/USB_VBUS', '/VBUS_RAW', '/VBUS_SW', '/SW', '/V12P5', '/VOUT'):
        g = groups[name]
        print(f"{name:10} | {g['area']:8.1f} | {g['n']:3d} | {g['length']:7.1f} | {g['minimum']:4.2f} | {g['vias']:2d}")
    print('NOTICE: Poured zones overlap these original traces but can neck down near pads/foreign nets.')
    print('NOTICE: 3 A steady-state temperature rise, current density and VDROP NOT verified.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: audit_power_copper_rev_b.py input.kicad_pcb')
    main(Path(sys.argv[1]))
