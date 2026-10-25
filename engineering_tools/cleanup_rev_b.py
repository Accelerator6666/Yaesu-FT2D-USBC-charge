"""Clean Rev B dangling stubs, two via clearances and local solder-mask DRC.

Use once after postprocessing, then re-run the full project-level DRC. A
successful DRC still would not verify high-current copper or package landpads.
"""

import sys
from pathlib import Path
import pcbnew as p

path = Path(sys.argv[1]).resolve()
b = p.LoadBoard(str(path))


def xy(point):
    return (round(p.ToMM(point.x), 4), round(p.ToMM(point.y), 4))


def vi(point):
    return p.VECTOR2I(p.FromMM(point[0]), p.FromMM(point[1]))


usb_stubs = {((25.0,36.9),(23.2,36.9)), ((25.0,41.15),(23.2,41.15))}
old_vout = (110.1,44.2)
new_vout = (109.9,44.55)

for fp in list(b.GetFootprints()):
    ref=fp.GetReference()
    if ref in ("C11", "R14"):
        # The source schematic marks these optional footprints as DNP, but
        # includes their definitions in the BOM; the PCB must match.
        fp.SetDNP(True)
        fp.SetExcludedFromBOM(False)
    if ref=="C23":
        fp.Reference().SetPosition(vi((102.0,56.0)))
    if ref not in ("U1", "C5", "R1"):
        continue
    pad_num = {"U1":"22", "C5":"2", "R1":"2"}[ref]
    for pad in fp.Pads():
        if pad.GetNumber()==pad_num and pad.GetNetname()=="/GND":
            pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
            print("Changed local GND pad connection",ref,pad_num)


original_items = list(b.GetTracks())
for item in original_items:
    if item.GetNetname()=="/USB_VBUS" and isinstance(item,p.PCB_TRACK):
        segment=(xy(item.GetStart()),xy(item.GetEnd()))
        if segment in usb_stubs or segment[::-1] in usb_stubs:
            b.Remove(item)
            print("Removed VBUS trace stub",segment)
            continue
    if item.GetNetname()=="/VOUT":
        if isinstance(item,p.PCB_VIA) and xy(item.GetPosition())==old_vout:
            item.SetPosition(vi(new_vout))
        elif isinstance(item,p.PCB_TRACK):
            if xy(item.GetStart())==old_vout:
                item.SetStart(vi(new_vout))
            if xy(item.GetEnd())==old_vout:
                item.SetEnd(vi(new_vout))


p.SaveBoard(str(path),b)
