"""Link C5 local ground to pre-existing standard ground via north of C5.

Routing kept between the PD_RESET/SCL lines to the east and VBUS_RAW to
the west; DRC + copper neck review required after refill.
"""

import sys
import pcbnew as p


def pos(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


SEGMENTS = [
    ((41.950, 46.000), (41.950, 43.350)),
    ((41.950, 43.350), (41.681, 42.967)),
]


def main(path):
    b = p.LoadBoard(path)
    net = b.FindNet('/GND')
    for a, z in SEGMENTS:
        tr = p.PCB_TRACK(b)
        tr.SetStart(pos(*a))
        tr.SetEnd(pos(*z))
        tr.SetLayer(p.F_Cu)
        tr.SetWidth(p.FromMM(.25))
        tr.SetNet(net)
        b.Add(tr)
    p.SaveBoard(path, b)
    print('Linked C5 GND to existing via at 41.681,42.967 via two .25mm traces')


if __name__ == '__main__':
    main(sys.argv[1])
