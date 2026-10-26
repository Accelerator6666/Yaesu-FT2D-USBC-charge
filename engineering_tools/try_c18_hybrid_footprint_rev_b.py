"""Replace ORIGINAL Rev B C18 with a 6.3 mm Panasonic hybrid candidate.

One-shot script: guards against reruns or unintentional position drift.
Does not certify component equivalence or the 105 C thermal downgrade.
Use a disposable destination for trials or the canonical PCB for application.
"""

from pathlib import Path
import sys

import pcbnew as pcb


def main(source: Path, destination: Path):
    board = pcb.LoadBoard(str(source))
    old = next(fp for fp in board.GetFootprints() if fp.GetReference() == 'C18')
    if old.GetValue() != 'EEHZL1V470R_47u' or abs(pcb.ToMM(old.GetPosition().x)-62.)>.01:
        raise RuntimeError('This one-shot migration requires the original 5 mm C18 at x=62 mm')
    replacement = pcb.FootprintLoad(
        '/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'CP_Elec_6.3x5.8'
    )
    if replacement is None:
        raise RuntimeError('KiCad 10 CP_Elec_6.3x5.8 missing')
    replacement.SetFPIDAsString('Capacitor_SMD:CP_Elec_6.3x5.8')
    replacement.SetReference(old.GetReference())
    replacement.SetValue('EEHZA1V470P_47u')
    # The wider terminal needs clearance from the neighbouring BUCK_VCC track.
    # A half-millimetre movement toward Q1 keeps the capacitor on VBUS_SW.
    replacement.SetPosition(pcb.VECTOR2I(old.GetPosition().x - pcb.FromMM(.5), old.GetPosition().y))
    replacement.SetOrientation(old.GetOrientation())
    replacement.SetPath(old.GetPath())
    replacement.SetAttributes(old.GetAttributes())
    old_pads = {pad.GetNumber(): pad for pad in old.Pads()}
    board.Add(replacement)
    for pad in replacement.Pads():
        original = old_pads[pad.GetNumber()]
        pad.SetNet(original.GetNet())
        print('C18', pad.GetNumber(), 'net', pad.GetNetname(), 'position', pcb.ToMM(pad.GetPosition().x))
    board.Remove(old)
    filler = pcb.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcb.SaveBoard(str(destination), board)
    print('Saved hybrid candidate PCB:', destination)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: try_c18_hybrid_footprint_rev_b.py input.kicad_pcb output.kicad_pcb')
    main(Path(sys.argv[1]), Path(sys.argv[2]))
