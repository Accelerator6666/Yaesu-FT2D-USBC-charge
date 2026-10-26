"""Fix one-spoke F.Cu thermal reliefs by using local solid GND copper.

This only changes zone-pad connectivity, not whether a separate isolated
F.Cu ground region is properly connected to the In1.Cu plane. Always check
both DRC violation count *and* unconnected count after application.
"""

import sys
import pcbnew as p


PADS = {'U1': {'10', '12', '13', '22', '25'},
        'U2': {'1', '3', '9', '11'},
        'R21': {'2'}, 'R25': {'2'}, 'C26': {'2'}}


def main(path):
    b = p.LoadBoard(path)
    count = 0
    for f in b.GetFootprints():
        if f.GetReference() not in PADS:
            continue
        for pad in f.Pads():
            if pad.GetNumber() in PADS[f.GetReference()]:
                assert pad.GetNetname() == '/GND'
                pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
                count += 1
    p.SaveBoard(path, b)
    print('Solid GND zone connection set on', count, 'verified GND pads')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: ground_pad_connections_rev_b.py board.kicad_pcb')
    main(sys.argv[1])
