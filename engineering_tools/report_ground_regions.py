"""Read-only report of Rev B front-copper GND fill polygons and connections."""

import sys
import pcbnew as p

b=p.LoadBoard(sys.argv[1])
z=next(z for z in b.Zones() if z.IsOnLayer(p.F_Cu))
s=z.GetFilledPolysList(p.F_Cu)
gndpads=[(f.GetReference(),pad) for f in b.GetFootprints() for pad in f.Pads() if pad.GetNetname()=="/GND"]
gndvias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=="/GND"]

for i in range(s.OutlineCount()):
    bbox=s.Outline(i).BBox()
    x,y,w,h=map(p.ToMM,(bbox.GetX(),bbox.GetY(),bbox.GetWidth(),bbox.GetHeight()))
    if w<1 and h<1: continue
    pads=[f"{ref}:{pad.GetNumber()}" for ref,pad in gndpads if s.Contains(pad.GetPosition(),i)]
    vias=[(round(p.ToMM(t.GetPosition().x),2),round(p.ToMM(t.GetPosition().y),2)) for t in gndvias if s.Contains(t.GetPosition(),i)]
    print(f"{i:2} ({x:5.1f},{y:5.1f}) {w:5.1f}x{h:5.1f}","GND PADS",pads,"GND VIAS",vias,flush=True)
