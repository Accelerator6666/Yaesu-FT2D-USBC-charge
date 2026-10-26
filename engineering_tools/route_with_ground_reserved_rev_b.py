"""Experimental complete Rev B reroute with reserved GND fanouts.

The earlier autorouter chose signal traces right through possible GND-via
placements. This variant reserves ordinary 0.6/0.3 mm GND through-vias and
local traces BEFORE routing; all other nets must route around the reserved
clearances. This is a DRC-gated *trial* and not manufacturing signoff.

Usage (after backing up the current board):
  /usr/bin/python3 route_with_ground_reserved_rev_b.py prepare PCB DSN
  java -jar freerouting-2.2.4.jar -de DSN -do SES
  /usr/bin/python3 route_with_ground_reserved_rev_b.py finish PCB SES
  /usr/bin/python3 power_pours_rev_b.py PCB
  kicad-cli pcb drc --refill-zones --schematic-parity PCB
"""

import sys
from pathlib import Path
import pcbnew as p


def vec(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


# Seven previously DRC-checked isolated-island stitch locations, plus new
# candidate fanouts selected to keep vias physically outside solder pads.
GROUND_VIAS = [
    (42.400, 49.458), (72.900, 44.651), (41.681, 42.967),
    (102.555, 55.425), (110.867, 47.003), (113.650, 47.128),
    (100.163, 43.306),
    (46.000, 36.650),  # U1: pin-22 route heads north, outside the QFN
    (80.550, 45.250),  # U2: pad 9 PGND; GND routing retained under SW
    (105.550, 58.150), # R25: PGTH resistor GND
    (110.100, 58.050), # R26: ILM resistor GND
    (52.623, 42.182),  # C3: isolated local GND at PD-to-FET interface
    (75.600, 41.150),  # U2: pad 1 PGND escaped to west of buck
    (110.000, 43.225), # U3: GND pin 8 escaped between signal pads
]


PRE_ROUTES = [
    # U1 GND pin 22: escape up between 0.5 mm pitch pins and then north.
    ('/GND', .18, (44.750, 38.038), (44.750, 36.650)),
    ('/GND', .18, (44.750, 36.650), (46.000, 36.650)),
    # U2 PGND2, R25/R26 resistor ends: solder pad to normal through via.
    ('/GND', .25, (80.750, 44.300), (80.550, 45.250)),
    ('/GND', .28, (105.825, 59.000), (105.550, 58.150)),
    ('/GND', .28, (108.825, 59.000), (110.100, 58.050)),
    ('/GND', .25, (77.250, 41.700), (76.200, 41.150)),
    ('/GND', .25, (76.200, 41.150), (75.600, 41.150)),
    ('/GND', .16, (108.900, 43.225), (110.000, 43.225)),
]


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in {'prepare', 'finish'}:
        raise SystemExit('Usage: script.py prepare|finish PCB.dsn PCB.ses')
    phase, path, interchange_path = sys.argv[1:]
    path = str(Path(path).resolve())
    interchange_path = str(Path(interchange_path).resolve())
    b = p.LoadBoard(path)

    if phase == 'prepare':
        ground_net = b.FindNet('/GND')
        assert ground_net is not None
        old_items = list(b.GetTracks())
        old_power_zones = [z for z in b.Zones() if z.GetNetname() != '/GND']
        for item in old_items:
            b.Remove(item)
        for zone in old_power_zones:
            b.Remove(zone)

        for x, y in GROUND_VIAS:
            via = p.PCB_VIA(b)
            via.SetNet(ground_net)
            via.SetWidth(p.FromMM(.6))
            via.SetDrill(p.FromMM(.3))
            via.SetViaType(p.VIATYPE_THROUGH)
            via.SetLayerPair(p.F_Cu, p.B_Cu)
            via.SetPosition(vec(x, y))
            b.Add(via)
        for net, width, xy0, xy1 in PRE_ROUTES:
            track = p.PCB_TRACK(b)
            track.SetLayer(p.F_Cu)
            track.SetNet(ground_net)
            track.SetWidth(p.FromMM(width))
            track.SetStart(vec(*xy0))
            track.SetEnd(vec(*xy1))
            b.Add(track)

        p.SaveBoard(path, b)
        ok = p.ExportSpecctraDSN(b, interchange_path)
        print('Reserve', len(GROUND_VIAS), 'GND vias +', len(PRE_ROUTES),
              'local GND tracks; removed', len(old_items), 'prior route items;',
              len(old_power_zones), 'power zones; DSN export', ok, flush=True)
        if not ok:
            raise RuntimeError('KiCad DSN export failed')
    else:
        ok = p.ImportSpecctraSES(b, interchange_path)
        if not ok:
            raise RuntimeError('KiCad SES import failed')
        p.SaveBoard(path, b)
        print('Imported SES; track/via count', len(b.GetTracks()), flush=True)


if __name__ == '__main__':
    main()
