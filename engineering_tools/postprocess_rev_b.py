"""Apply reviewed connectivity and ground-pour post-processing to Rev B.

Must be followed by zone refill, *full* KiCad DRC, and visual engineering
review. Intentional signal routing on In2.Cu crosses the GND pour, so a
complete continuous ground return must be rechecked before fabrication.
"""

import sys
from pathlib import Path
import pcbnew as p


board_path = Path(sys.argv[1]).resolve()
board = p.LoadBoard(str(board_path))


def v(xy):
    return p.VECTOR2I(p.FromMM(xy[0]), p.FromMM(xy[1]))


def track(netname, layer, start, end, width=0.2):
    t = p.PCB_TRACK(board)
    t.SetNet(board.FindNet(netname))
    t.SetLayer(layer)
    t.SetStart(v(start))
    t.SetEnd(v(end))
    t.SetWidth(p.FromMM(width))
    board.Add(t)


def via(netname, at):
    t = p.PCB_VIA(board)
    t.SetNet(board.FindNet(netname))
    t.SetPosition(v(at))
    t.SetViaType(p.VIATYPE_THROUGH)
    t.SetLayerPair(p.F_Cu, p.B_Cu)
    t.SetWidth(p.FromMM(0.6))
    t.SetDrill(p.FromMM(0.3))
    board.Add(t)


# The USB-C CC1 input escaped onto the unused board-edge corridor. Carry it
# outside the connector footprint and approach the D2 CC1 pin from above.
cc1_route = [
    ((23.25, 40.3), (22.0, 40.3)),
    ((22.0, 40.3), (22.0, 32.5)),
    ((22.0, 32.5), (33.8, 32.5)),
    ((33.8, 32.5), (33.8, 36.35)),
]
for start, end in cc1_route:
    track("/CC1", p.In2_Cu, start, end)
via("/CC1", (33.8, 36.35))
track("/CC1", p.F_Cu, (33.8, 36.35), (35.1125, 36.35))


# Eliminate one-sided via stubs reported by the last KiCad run. They are
# connected through other traces on F.Cu; if DRC later reports unconnected
# items, the removal must be revisited.
unused_vias = {(106.3, 41.5), (23.2, 41.15), (23.2, 36.9)}
for item in list(board.GetTracks()):
    if not isinstance(item, p.PCB_VIA):
        continue
    point = (round(p.ToMM(item.GetPosition().x), 3), round(p.ToMM(item.GetPosition().y), 3))
    if point in unused_vias:
        print("Removing one-sided via", item.GetNetname(), point, flush=True)
        board.Remove(item)


for zone in board.Zones():
    # Do not keep floating ground copper islands that can receive and emit RF.
    zone.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    if zone.IsOnLayer(p.F_Cu) or zone.IsOnLayer(p.B_Cu):
        zone.SetThermalReliefGap(p.FromMM(0.20))
        zone.SetThermalReliefSpokeWidth(p.FromMM(0.25))


p.SaveBoard(str(board_path), board)
print("Postprocessed", board_path, flush=True)
