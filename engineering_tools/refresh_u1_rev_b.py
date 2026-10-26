"""Refresh U1's embedded KiCad official footprint with identical land pattern.

Valid only after confirming all 29 pad numbers, position, size, shape and
layers match the packaged STUSB4500QTR device and existing board footprint.
"""

import sys
import pcbnew as p


def main(path):
    b = p.LoadBoard(path)
    old = next(fp for fp in b.GetFootprints() if fp.GetReference() == 'U1')
    replacement = p.FootprintLoad('/usr/share/kicad/footprints/Package_DFN_QFN.pretty',
                                  'QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm')
    if replacement is None:
        raise RuntimeError('KiCad official U1 footprint missing')
    source = [(x.GetNumber(), x.GetPosition(), x.GetSize(), x.GetShape(),
               x.GetLayerSet().FmtBin()) for x in old.Pads()]
    old_nets = {x.GetNumber(): x.GetNetname() for x in old.Pads()}
    replacement.SetPosition(old.GetPosition())
    replacement.SetOrientationDegrees(old.GetOrientationDegrees())
    replacement.SetReference('U1')
    replacement.SetValue(old.GetValue())
    replacement.SetPath(old.GetPath())
    replacement.SetUuid(old.m_Uuid)
    replacement.SetFPIDAsString('Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm')
    check = [(x.GetNumber(), x.GetPosition(), x.GetSize(), x.GetShape(),
              x.GetLayerSet().FmtBin()) for x in replacement.Pads()]
    # Pad order is not semantically relevant, but all physical pads must match.
    assert sorted(map(str, source)) == sorted(map(str, check)), 'U1 land pattern changed'
    for pad in replacement.Pads():
        net_name = old_nets.get(pad.GetNumber())
        if net_name:
            pad.SetNet(b.FindNet(net_name))
        if pad.GetNetname() == '/GND' and pad.GetNumber() == '12':
            pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    b.Remove(old)
    b.Add(replacement)
    p.SaveBoard(path, b)
    print('U1 updated to KiCad official embedded footprint; 29 pads validated')


if __name__ == '__main__':
    main(sys.argv[1])
