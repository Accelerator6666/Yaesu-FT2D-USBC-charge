"""Find conservative GND stitching-via locations in Rev B isolated fills.

Uses only coarse rectangular clearance guards. It is a layout proposal, not
an electrical sign-off. Running without --apply is read-only. Run DRC after
applying and inspect every via across all four copper layers.
"""

import math
import sys
from pathlib import Path
import pcbnew as p


board_path = Path(sys.argv[1]).resolve()
apply = len(sys.argv) > 2 and sys.argv[2] == "--apply"
board = p.LoadBoard(str(board_path))
fills = next(z for z in board.Zones() if z.IsOnLayer(p.F_Cu)).GetFilledPolysList(p.F_Cu)
targets = (0, 1, 2, 3, 4, 5, 6, 14)
mm = p.ToMM


def point(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def segment_distance(x, y, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = min(1., max(0., ((x - ax)*dx + (y - ay)*dy)/(dx*dx + dy*dy))) if dx*dx + dy*dy else 0.
    return math.hypot(x-(ax+t*dx), y-(ay+t*dy))


def clearance_score(x, y):
    safety = 100.
    for track in board.GetTracks():
        if track.GetNetname() == "/GND":
            continue
        if isinstance(track, p.PCB_VIA):
            score = math.hypot(x-mm(track.GetPosition().x), y-mm(track.GetPosition().y)) - mm(track.GetWidth(p.F_Cu))/2 - 0.3
        else:
            a, b = track.GetStart(), track.GetEnd()
            score = segment_distance(x, y, mm(a.x), mm(a.y), mm(b.x), mm(b.y)) - mm(track.GetWidth())/2 - 0.3
        safety = min(safety, score)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            delta = math.hypot(x-mm(pad.GetPosition().x), y-mm(pad.GetPosition().y))
            radius = max(mm(pad.GetSize().x), mm(pad.GetSize().y))/2
            # Avoid via-in-pad, including for GND pads.
            score = delta - radius - 0.3 - (0.25 if pad.GetNetname() != "/GND" else 0.15)
            safety = min(safety, score)
    return safety


for i in targets:
    bbox = fills.Outline(i).BBox()
    x0, y0 = mm(bbox.GetX()), mm(bbox.GetY())
    w, h = mm(bbox.GetWidth()), mm(bbox.GetHeight())
    found = []
    step = 0.5
    nx, ny = int(w/step), int(h/step)
    for ix in range(nx):
        for iy in range(ny):
            x, y = x0+step*(ix+0.5), y0+step*(iy+0.5)
            if not all(fills.Contains(point(x+dx,y+dy),i) for dx,dy in ((0,0),(.4,0),(-.4,0),(0,.4),(0,-.4))):
                continue
            score = clearance_score(x,y)
            if score > 0.28:
                found.append((score,x,y))
    if not found:
        print("No safe coarse via candidate for region",i,"bbox",(x0,y0,w,h),flush=True)
        continue
    score,x,y = max(found)
    print("GND region",i,"candidate",(round(x,3),round(y,3)),"margin",round(score,3),flush=True)
    if apply:
        via = p.PCB_VIA(board)
        via.SetPosition(point(x,y))
        via.SetNet(board.FindNet("/GND"))
        via.SetWidth(p.FromMM(0.6))
        via.SetDrill(p.FromMM(0.3))
        via.SetViaType(p.VIATYPE_THROUGH)
        via.SetLayerPair(p.F_Cu,p.B_Cu)
        board.Add(via)

if apply:
    p.SaveBoard(str(board_path),board)
