"""Shift VBUS_SW inner-layer track segments off the In1.Cu GND plane.

Only modifies two already-via-terminated short traces; KiCad DRC must verify
there is clearance from In2.Cu signal routing after this adjustment.
"""

import sys
import pcbnew as p


def main(path):
    b = p.LoadBoard(path)
    changed = 0
    for item in b.GetTracks():
        if (isinstance(item, p.PCB_TRACK)
                and item.GetNetname() == '/VBUS_SW'
                and item.GetLayer() == p.In1_Cu):
            item.SetLayer(p.In2_Cu)
            changed += 1
    assert changed == 2, 'Expected exactly two inner VBUS_SW traces'
    p.SaveBoard(path, b)
    print('Relocated', changed, 'VBUS_SW segments from In1.Cu GND plane to In2.Cu')


if __name__ == '__main__':
    main(sys.argv[1])
