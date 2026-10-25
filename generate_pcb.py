"""Populate a KiCad 4-layer prototype board from the schematic XML netlist.

The board is an in-progress layout: this script deliberately does not produce
Gerbers. Do not submit the output to a fab until routing, DRC, and land-pattern
review are complete.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT = Path(__file__).resolve().parent
NETLIST = ROOT / "tmp" / "FT2D.net.xml"
OUT = ROOT / "FT2D_PD20V_12V5_3A_评审原理图.kicad_pcb"
KICAD = Path(__file__).resolve().parents[0]
STOCK = Path(r"C:\Users\jasonz\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints")


def mm(v):
    return p.FromMM(v)


def at(x, y):
    return p.VECTOR2I(mm(x), mm(y))


placement = {
    "J1": (25, 42, 90), "D1": (31, 46, 0), "D2": (36, 37, 0),
    "F1": (38, 43, 0), "U1": (45, 40, 0), "Q1": (56, 42, 0),
    "U2": (72, 43, 0), "L1": (89, 43, 0), "U3": (108, 43, 0),
    "J2": (45, 75, 0), "J3": (117, 73, 0), "TP1": (116, 38, 0),
    "C1": (41, 35, 0), "C2": (47, 35, 0), "C3": (50, 41, 0),
    "C4": (60, 56, 0), "C5": (41, 46, 0),
    "C10": (69, 47, 0), "C11": (83, 58, 0),
    "C12": (69, 38, 0), "C13": (75, 38, 0),
    "C14": (62, 33, 0), "C15": (67, 33, 0),
    "C16": (72, 33, 0), "C17": (77, 33, 0),
    "C18": (62, 48, 0), "C19": (77, 45, 0),
    "C20": (98, 34, 0), "C21": (103, 34, 0), "C22": (108, 34, 0),
    "C23": (102, 51, 0), "C24": (104, 41, 0),
    "C25": (117, 51, 0), "C26": (113, 43, 0),
    "C27": (110, 49, 0), "C28": (113, 49, 0),
    "R1": (40, 51, 0), "R2": (44, 51, 0), "R3": (48, 51, 0),
    "R4": (51, 47, 0), "R5": (52, 52, 0),
    "R6": (37, 50, 0), "R7": (57, 52, 0),
    "R12": (78, 52, 0), "R13": (78, 55, 0),
    "R14": (80, 58, 0), "R15": (68, 51, 0),
    "R16": (71, 51, 0), "R17": (63, 55, 0),
    "R18": (66, 55, 0), "R19": (77, 48, 0),
    "R20": (114, 60, 0), "R21": (117, 60, 0),
    "R22": (108, 56, 0), "R23": (111, 56, 0),
    "R24": (102, 59, 0), "R25": (105, 59, 0),
    "R26": (108, 59, 0),
}

tree = ET.parse(NETLIST)
root = tree.getroot()
components = root.find("components")
assert components is not None
refs = {c.attrib["ref"] for c in components.findall("comp")}
assert refs == set(placement), (sorted(refs - set(placement)), sorted(set(placement) - refs))

board = p.BOARD()
board.SetCopperLayerCount(4)
board.GetDesignSettings().m_MinClearance = mm(0.14)
board.GetDesignSettings().m_NetSettings.GetDefaultNetclass().SetClearance(mm(0.14))
board.SetFileName(str(OUT))
net_map = {}
for net in root.findall("./nets/net"):
    name = net.attrib["name"]
    obj = p.NETINFO_ITEM(board, name)
    board.Add(obj)
    net_map[name] = obj

parts = {}
for comp in components.findall("comp"):
    ref = comp.attrib["ref"]
    footprint_id = comp.findtext("footprint")
    if not footprint_id or ":" not in footprint_id:
        raise ValueError(f"Missing footprint: {ref}")
    library, name = footprint_id.split(":", 1)
    path = ROOT / "FT2D.pretty" if library == "FT2D" else STOCK / f"{library}.pretty"
    footprint = p.FootprintLoad(str(path), name)
    if footprint is None:
        raise ValueError(f"Cannot load footprint {footprint_id} for {ref}")
    footprint.SetFPIDAsString(footprint_id)
    footprint.SetReference(ref)
    footprint.SetValue(comp.findtext("value") or "")
    x, y, rotation = placement[ref]
    footprint.SetPosition(at(x, y))
    footprint.SetOrientationDegrees(rotation)
    if ref in ("R14", "C11"):
        footprint.SetExcludedFromBOM(True)
    board.Add(footprint)
    parts[ref] = footprint

for net in root.findall("./nets/net"):
    obj = net_map[net.attrib["name"]]
    for node in net.findall("node"):
        ref, pin = node.attrib["ref"], node.attrib["pin"]
        pads = [pad for pad in parts[ref].Pads() if pad.GetNumber() == pin]
        if not pads:
            raise ValueError(f"{ref} has no footprint pad {pin}")
        for pad in pads:
            pad.SetNet(obj)

# U3's narrow ground terminal cannot form two reliable thermal spokes.
for pad in parts["U3"].Pads():
    if pad.GetNumber() == "8":
        pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)

for a, b in [((20, 20), (125, 20)), ((125, 20), (125, 85)),
             ((125, 85), (20, 85)), ((20, 85), (20, 20))]:
    edge = p.PCB_SHAPE(board)
    edge.SetShape(p.SHAPE_T_SEGMENT)
    edge.SetStart(at(*a))
    edge.SetEnd(at(*b))
    edge.SetLayer(p.Edge_Cuts)
    edge.SetWidth(mm(0.05))
    board.Add(edge)

for layer in (p.F_Cu, p.In1_Cu, p.B_Cu):
    zone = p.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(net_map["/GND"])
    zone.SetLocalClearance(mm(0.2))
    zone.SetThermalReliefGap(mm(0.3))
    zone.SetThermalReliefSpokeWidth(mm(0.35))
    zone.SetPadConnection(
        p.ZONE_CONNECTION_FULL if layer == p.In1_Cu else p.ZONE_CONNECTION_THERMAL
    )
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((20.5, 20.5), (124.5, 20.5),
                 (124.5, 84.5), (20.5, 84.5)):
        outline.Append(mm(x), mm(y))
    board.Add(zone)

p.ZONE_FILLER(board).Fill(board.Zones())
p.SaveBoard(str(OUT), board)
print(f"{OUT}: {len(parts)} components, {len(net_map)} nets, 4 layers")
