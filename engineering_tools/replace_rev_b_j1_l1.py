"""One-shot schematic-matched Rev B BOM substitution and buck layout WIP.

Run on a backed-up Rev B working file; existing tracks are *not* retained by
reference when pad positions change and must be fully rerouted and checked.
"""

from pathlib import Path
import sys
import pcbnew as p


def v(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def replace(board, old, ref, folder, name, pos, angle, value, lib_id):
    nets = {pad.GetNumber(): pad.GetNetname() for pad in old.Pads()}
    replacement = p.FootprintLoad(str(folder), name)
    if replacement is None:
        raise RuntimeError(f"Missing footprint {folder}/{name}")
    replacement.SetReference(ref)
    replacement.SetValue(value)
    replacement.SetFPIDAsString(lib_id)
    replacement.SetPath(old.GetPath())
    replacement.SetUuid(old.m_Uuid)
    replacement.SetOrientationDegrees(angle)
    replacement.SetPosition(v(*pos))
    for pad in replacement.Pads():
        net_name = nets.get(pad.GetNumber())
        if net_name:
            net = board.FindNet(net_name)
            if net is None:
                raise RuntimeError(f"Missing net {net_name}")
            pad.SetNet(net)
    assert all(n in {p.GetNumber() for p in replacement.Pads()} for n in nets), (ref, nets)
    board.Remove(old)
    board.Add(replacement)
    print(ref, 'changed to', value, 'at', pos, 'orientation', angle)
    return replacement


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: replace_rev_b_j1_l1.py path-to-Rev-B.kicad_pcb')
    board_path = Path(sys.argv[1]).resolve()
    board = p.LoadBoard(str(board_path))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    old_tracks = list(board.GetTracks())
    for tr in old_tracks:
        board.Remove(tr)
    j1 = replace(board, footprints['J1'], 'J1', '/usr/share/kicad/footprints/Connector_USB.pretty',
            'USB_C_Receptacle_HRO_TYPE-C-31-M-12', (24.15, 42.0), 270,
            'TYPE-C-31-M-12', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12')
    replace(board, footprints['L1'], 'L1', board_path.parent / 'FT2D.pretty',
            'JIERR_SRG1260_100M', (89.0, 43.0), 0,
            'SRG1260-100-M_10uH', 'FT2D:JIERR_SRG1260_100M')

    # Reduce the switch node path between U2 and L1.  Move the high-frequency
    # bypass parts with U2, but leave the bulk input bank as a separate task.
    moves = {'U2': (79.0, 43.0), 'C12': (77.0, 38.0),
             'C13': (73.0, 38.0), 'C19': (79.0, 48.5),
             'R19': (74.0, 48.0)}
    for ref, coords in moves.items():
        footprints[ref].SetPosition(v(*coords))
        print('Moved', ref, coords)

    # Solid top copper connection on the four duplicated connector ground
    # contacts avoids starved one-spoke thermal on this very dense connector.
    for pad in j1.Pads():
        if pad.GetNetname() == '/GND':
            pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)

    # Previous routing, including pad escapes, is invalid after geometry change.
    p.SaveBoard(str(board_path), board)
    print('Removed', len(old_tracks), 'previous routing items; board is unrouted WIP')


if __name__ == '__main__':
    main()
