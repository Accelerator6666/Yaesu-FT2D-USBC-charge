"""Conservative read-only 2D scan for narrow exposed Rev B top-copper links.

This is a diagnostic *heuristic*: it samples F.Cu tracks and same-net filled
zones perpendicular to the track; it DOES NOT model actual DC current
distribution, pads, Joule heating, stackup, vias, or current sharing.
It is intentionally not a manufacturing/3A approval criterion.
"""

from collections import defaultdict
import math
from pathlib import Path
import sys

import pcbnew as p


POWER = ('/USB_VBUS', '/VBUS_RAW', '/VBUS_SW', '/SW', '/V12P5', '/VOUT')


def point_mm(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def main(path):
    board = p.LoadBoard(str(path))
    fill = defaultdict(list)
    for zone in board.Zones():
        if zone.GetLayer() == p.F_Cu and zone.GetNetname() in POWER:
            fill[zone.GetNetname()].append(zone.GetFilledPolysList(p.F_Cu))

    def zone_contains(name, x, y):
        test = point_mm(x, y)
        return any(poly.Contains(test) for poly in fill[name])

    results = defaultdict(list)
    step = 0.05  # mm; sampled cross sections, NOT a fab-accuracy tolerance.
    for tr in board.GetTracks():
        if not isinstance(tr, p.PCB_TRACK) or tr.GetLayer() != p.F_Cu:
            continue
        name = tr.GetNetname()
        if name not in POWER:
            continue
        start, end = tr.GetStart(), tr.GetEnd()
        x0, y0 = p.ToMM(start.x), p.ToMM(start.y)
        x1, y1 = p.ToMM(end.x), p.ToMM(end.y)
        length = math.hypot(x1-x0, y1-y0)
        if length < 1e-3:
            continue
        nx, ny = -(y1-y0)/length, (x1-x0)/length
        drawn = p.ToMM(tr.GetWidth())
        for t in (0.15, 0.35, 0.5, 0.65, 0.85):
            x, y = x0+t*(x1-x0), y0+t*(y1-y0)
            # A filled zone covers the sampled track center; scan perpendicular
            # through continuous same-net copper at 50um increments. Track is
            # counted separately because it can escape the polygon near pads.
            if zone_contains(name, x, y):
                sides = []
                for s in (-1, 1):
                    half = 0.
                    while half + step <= 3.0 and zone_contains(name, x + (half+step)*s*nx, y + (half+step)*s*ny):
                        half += step
                    sides.append(half)
                sampled = max(drawn, sum(sides))
            else:
                sampled = drawn
            results[name].append((sampled, drawn, round(x, 2), round(y, 2), round(length, 2)))

    print('Top-layer approximate 2D cross-sections (50µm grid, ignores pads and thermal).')
    print('Net | samples | narrowest sampled width mm | samples <1.0mm | original track min mm | 3 worst locations [X,Y]')
    for name in POWER:
        samples = sorted(results[name])
        if not samples:
            continue
        minw = min(entry[0] for entry in samples)
        skinny = sum(entry[0]<1.0 for entry in samples)
        trace = min(entry[1] for entry in samples)
        places = ', '.join(f'({v[2]:.2f},{v[3]:.2f})={v[0]:.2f}mm' for v in samples[:3])
        print(f'{name:10} | {len(samples):3d} | {minw:5.2f} | {skinny:3d} | {trace:4.2f} | {places}')
    print('NO-GO: sampling is NOT 3 A current/temperature approval. Inspect worst sites in KiCad.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: audit_power_necks_rev_b.py path.kicad_pcb')
    main(Path(sys.argv[1]))
