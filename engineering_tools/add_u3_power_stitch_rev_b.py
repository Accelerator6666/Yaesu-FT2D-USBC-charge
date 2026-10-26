"""Add reviewed local In2 power spreading and through-via stitching near U3.

Targets a specific Rev B placement only. Fails rather than duplicating pours or
stitches. The added copper is an engineering *improvement*, NOT 3 A/thermal
approval; a DRC-clean PCB still needs physical power path and EMI signoff.

Usage: /usr/bin/python3 engineering_tools/add_u3_power_stitch_rev_b.py board.kicad_pcb
"""

from pathlib import Path
import sys

import pcbnew as p


def vec(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


ISLANDS = {
    '/V12P5': [(102.0, 39.0), (108.1, 39.0), (108.1, 48.2), (102.0, 48.2)],
    '/VOUT': [(109.2, 39.0), (116.0, 39.0), (116.0, 48.2), (109.2, 48.2)],
}
VIAS = {
    '/V12P5': [(104.0, 44.1), (104.0, 45.0)],
    '/VOUT': [(111.0, 45.0), (115.0, 44.0)],
}


def main(board_path: Path):
    board = p.LoadBoard(str(board_path))
    if not board:
        raise RuntimeError(f'Cannot load board: {board_path}')
    if any(z.GetZoneName().startswith('REV_B_U3_IN2_') for z in board.Zones()):
        raise RuntimeError('U3 power stitch already present; refusing duplicate application')

    u3 = next((f for f in board.GetFootprints() if f.GetReference() == 'U3'), None)
    if not u3 or abs(p.ToMM(u3.GetPosition().x) - 108) > .01 or abs(p.ToMM(u3.GetPosition().y) - 43) > .01:
        raise RuntimeError('Expected U3 at (108,43)mm; do not apply to a moved footprint')
    u3_pins = {pad.GetNumber(): pad.GetNetname() for pad in u3.Pads()}
    if (u3_pins.get('5'), u3_pins.get('6')) != ('/V12P5', '/VOUT'):
        raise RuntimeError(f'Unexpected U3 5/6 net mapping {u3_pins}')

    # Keep SWIG objects alive through fill/save: pcbnew uses borrowed wrappers.
    retained = []
    for name, vertices in ISLANDS.items():
        net = board.FindNet(name)
        if net is None:
            raise RuntimeError(f'Power net missing: {name}')
        zone = p.ZONE(board)
        zone.SetLayer(p.In2_Cu)
        zone.SetNet(net)
        zone.SetZoneName('REV_B_U3_IN2_' + name.lstrip('/'))
        zone.SetAssignedPriority(2)
        zone.SetPadConnection(p.ZONE_CONNECTION_FULL)
        zone.SetLocalClearance(p.FromMM(.30))
        zone.SetMinThickness(p.FromMM(.25))
        polygon = p.SHAPE_POLY_SET()
        polygon.NewOutline()
        for x, y in vertices:
            polygon.Append(vec(x, y))
        zone.SetOutline(polygon)
        board.Add(zone)
        retained.append((zone, polygon))

        for x, y in VIAS[name]:
            via = p.PCB_VIA(board)
            via.SetPosition(vec(x, y))
            via.SetWidth(p.FromMM(.6))
            via.SetDrill(p.FromMM(.3))
            via.SetViaType(p.VIATYPE_THROUGH)
            via.SetLayerPair(p.F_Cu, p.B_Cu)
            via.SetNet(net)
            board.Add(via)
            retained.append(via)

    # Filled copper is saved along with zone geometry for visual Gerber review.
    p.ZONE_FILLER(board).Fill(board.Zones())
    for zone, polygon in [obj for obj in retained if isinstance(obj, tuple)]:
        if zone.GetFilledPolysList(p.In2_Cu).OutlineCount() != 1:
            raise RuntimeError(f'Expected exactly one filled {zone.GetNetname()} In2 island')
    p.SaveBoard(str(board_path), board)
    print('Added 2 continuous In2.Cu power islands and 4 ordinary 0.6/0.3 mm vias near U3.')
    print('Required next step: KiCad 10 schematic-parity + refill DRC, copper and EMI review.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: add_u3_power_stitch_rev_b.py board.kicad_pcb')
    main(Path(sys.argv[1]))
