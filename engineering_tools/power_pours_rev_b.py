"""Proposed top-copper distribution for Rev B's ~3 A power paths.

Preliminary polygons are clipped by all foreign-net copper by KiCad refill.
This is a manufacturing *review* artifact, not proof of 3 A ampacity:
report narrow physical necks, current return, and copper temperature first.
"""

import sys
import math
import pcbnew as p


def vec(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


POUR_WIDTHS_MM = {
    'USB_VBUS': 1.8,
    'VBUS_RAW': 1.8,
    'VBUS_SW': 1.8,
    'SW': 1.6,
    'V12P5': 2.0,
    'VOUT': 2.0,
}


def rectangle_around_track(track, desired_width):
    a, b = track.GetStart(), track.GetEnd()
    x0, y0 = p.ToMM(a.x), p.ToMM(a.y)
    x1, y1 = p.ToMM(b.x), p.ToMM(b.y)
    distance = math.hypot(x1-x0, y1-y0)
    if distance < 0.45:
        return None
    # Square caps overlap neighboring segment corridors at elbows. Segment
    # width is a *target* only: KiCad clips copper for foreign nets.
    ex, ey = (x1-x0)/distance, (y1-y0)/distance
    nx, ny = -ey, ex
    half = desired_width/2
    cap = min(0.30, distance/3)
    return [(x0-ex*cap+nx*half,y0-ey*cap+ny*half),
            (x1+ex*cap+nx*half,y1+ey*cap+ny*half),
            (x1+ex*cap-nx*half,y1+ey*cap-ny*half),
            (x0-ex*cap-nx*half,y0-ey*cap-ny*half)]


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: power_pours_rev_b.py board.kicad_pcb')
    path = sys.argv[1]
    board = p.LoadBoard(path)
    already = [z for z in board.Zones() if z.GetNetname() != '/GND']
    if already:
        raise RuntimeError('Board already contains power fills; refusing duplicates')

    region_count = {name: 0 for name in POUR_WIDTHS_MM}
    unioned = {name: p.SHAPE_POLY_SET() for name in POUR_WIDTHS_MM}
    for track in list(board.GetTracks()):
        suffix = track.GetNetname().removeprefix('/')
        if suffix not in POUR_WIDTHS_MM or not isinstance(track, p.PCB_TRACK):
            continue
        if track.GetLayer() != p.F_Cu:
            continue
        vertices = rectangle_around_track(track, POUR_WIDTHS_MM[suffix])
        if not vertices:
            continue
        region_count[suffix] += 1
        polygon = p.SHAPE_POLY_SET()
        polygon.NewOutline()
        for x, y in vertices:
            polygon.Append(vec(x, y))
        unioned[suffix].BooleanAdd(polygon)

    for suffix, polygon in unioned.items():
        if polygon.OutlineCount() == 0:
            continue
        net_name = '/' + suffix
        net = board.FindNet(net_name)
        if not net:
            raise RuntimeError('Net missing: ' + net_name)
        zone = p.ZONE(board)
        zone.SetLayer(p.F_Cu)
        zone.SetNet(net)
        zone.SetZoneName(f'REVIEW_3A_{suffix}')
        zone.SetAssignedPriority(1)
        zone.SetPadConnection(p.ZONE_CONNECTION_FULL)
        zone.SetLocalClearance(p.FromMM(.25))
        zone.SetMinThickness(p.FromMM(.25))
        zone.SetOutline(polygon)
        board.Add(zone)
    print('Merged trace-following corridors per power net:', region_count)
    p.SaveBoard(path, board)


if __name__ == '__main__':
    main()
