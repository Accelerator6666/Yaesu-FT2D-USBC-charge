"""Targeted repairs after importing a Specctra autoroute session.

Do not treat this as release approval: the autorouter's 0.15-0.2 mm power
traces are not adequate for the 3 A path, even if connectivity DRC passes.
"""
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parent
PATH = ROOT / "FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb"
board = p.LoadBoard(str(PATH))


def mm(v):
    return p.FromMM(v)


def at(x, y):
    return p.VECTOR2I(mm(x), mm(y))


board.GetDesignSettings().m_TrackMinWidth = mm(0.15)
board.GetDesignSettings().m_MinClearance = mm(0.14)
board.GetDesignSettings().m_NetSettings.GetDefaultNetclass().SetClearance(mm(0.14))

solid_ground = {
    ("D2", "3"), ("U1", "10"), ("C10", "2"), ("C24", "2"),
    ("U2", "3"), ("U2", "9"), ("U2", "11"), ("U3", "8"),
}
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if (fp.GetReference(), pad.GetNumber()) in solid_ground:
            pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)

remove_vias = {
    ("/VBUS_SW", 74.7469, 42.9141),
    ("/DVDT_U3", 106.5775, 45.5322),
    ("/BUCK_RT", 71.3987, 48.0537),
}
for item in list(board.GetTracks()):
    if not isinstance(item, p.PCB_VIA):
        continue
    x, y = p.ToMM(item.GetPosition().x), p.ToMM(item.GetPosition().y)
    if any(item.GetNetname() == net and abs(x - px) < 0.001
           and abs(y - py) < 0.001 for net, px, py in remove_vias):
        board.Remove(item)

net = board.FindNet("/OVLO_U3")
assert net is not None


def trace(a, b, layer, width=0.15):
    item = p.PCB_TRACK(board)
    item.SetStart(at(*a))
    item.SetEnd(at(*b))
    item.SetLayer(layer)
    item.SetWidth(mm(width))
    item.SetNet(net)
    board.Add(item)


def via(point):
    item = p.PCB_VIA(board)
    item.SetPosition(at(*point))
    item.SetWidth(mm(0.6))
    item.SetDrill(mm(0.3))
    item.SetViaType(p.VIATYPE_THROUGH)
    item.SetLayerPair(p.F_Cu, p.B_Cu)
    item.SetNet(net)
    board.Add(item)


trace((107.1, 42.775), (105.3, 42.775), p.F_Cu)
via((105.3, 42.775))
trace((105.3, 42.775), (105.3, 54.5), p.In2_Cu)
trace((105.3, 54.5), (106.3, 55.1), p.In2_Cu)
via((106.3, 55.1))
trace((106.3, 55.1), (107.225, 56.0), p.F_Cu)

p.ZONE_FILLER(board).Fill(board.Zones())
p.SaveBoard(str(PATH), board)
print(f"Postprocessed {PATH}")
