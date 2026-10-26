"""Reproducible first-pass Rev B electrical-loss screening (NOT 3 A signoff).

Uses the existing KiCad board and its actual U3 pad/track geometry.  The
resistance estimate deliberately assumes *all* 3 A use an entire narrow trace,
without credit for parallel same-net pours.  It does NOT predict temperature
rise, via current sharing, source transient response, or RF interference.

Usage: /usr/bin/python3 engineering_tools/screen_rev_b_power_path.py BOARD [JSON]
"""

from __future__ import annotations

import json
from math import hypot
from pathlib import Path
import sys

import pcbnew as p


def mm(integer):
    return p.ToMM(integer)


def report(path: Path):
    board = p.LoadBoard(str(path))
    u3 = next((fp for fp in board.GetFootprints() if fp.GetReference() == "U3"), None)
    if not u3 or u3.GetValue() != "TPS259474ARPWR":
        raise ValueError("Not the reviewed Rev B TPS259474A footprint")
    pads = {pad.GetNumber(): pad for pad in u3.Pads()}
    if (pads["5"].GetNetname(), pads["6"].GetNetname()) != ("/V12P5", "/VOUT"):
        raise ValueError("U3 input/output pin assignment changed")

    # The internal portion of the elongated 0.3 mm pad is a different
    # thermal/electrical geometry; do not mistake full track length for an
    # independent 0.3 mm *external* neck in the existing wide same-net pour.
    narrow = {}
    for number, net in (("5", "/V12P5"), ("6", "/VOUT")):
        pad = pads[number]
        pad_x, pad_y = mm(pad.GetPosition().x), mm(pad.GetPosition().y)
        traces = []
        for track in board.GetTracks():
            if not isinstance(track, p.PCB_TRACK) or isinstance(track, p.PCB_VIA) or track.GetLayer() != p.F_Cu:
                continue
            if track.GetNetname() != net or mm(track.GetWidth()) > 0.31:
                continue
            a, b = track.GetStart(), track.GetEnd()
            if min(hypot(mm(point.x)-pad_x, mm(point.y)-pad_y) for point in (a,b)) < .01:
                traces.append(track)
        if len(traces) != 1:
            raise ValueError(f"Expected precisely one 0.3 mm escape starting at U3/{number}; got {len(traces)}")
        track = traces[0]
        length = hypot(mm(track.GetStart().x-track.GetEnd().x), mm(track.GetStart().y-track.GetEnd().y))
        width = mm(track.GetWidth())
        # Copper IPC oz conversion approximately 34.8 um; assume 35 um nominal.
        # A copper foil's minimum delivered thickness is NOT guaranteed here.
        resistivity20 = 1.724e-8  # ohm*m for copper at 20 C
        resistance20 = resistivity20*(length/1000)/((width/1000)*35e-6)
        resistance90 = resistance20*(1+.00393*(90-20))
        narrow[net] = {
            "pad": number, "pad_size_mm": [round(mm(pad.GetSize().x), 4), round(mm(pad.GetSize().y), 4)],
            "nominal_track_width_mm": round(width, 4), "entire_track_length_mm": round(length, 4),
            "assume_35um_copper_full_length_R_mohm_at_20C": round(1000*resistance20, 3),
            "assume_35um_copper_full_length_I3A_loss_mW_at_90C": round(1000*9*resistance90, 1),
        }

    # Datasheet nominal current threshold: R_ILM[ohm] = 3334 / I_LIMIT[A].
    # Verify R26 from KiCad and do not silently accept an altered value.
    r26 = next((fp for fp in board.GetFootprints() if fp.GetReference() == "R26"), None)
    if not r26 or r26.GetValue() != "820R":
        raise ValueError("R26 changed; update current-limit analysis")

    return {
        "status": "ENGINEERING_SCREENING_ONLY_NOT_FAB_APPROVAL",
        "board": path.name,
        "conditions": {"Vout_V": 12.5, "Iout_A": 3.0, "requested_PD_V": 20.0, "nominal_FCu_thickness_um": 35},
        "load_power_W": 37.5,
        "PD_input_current_at_85pct_efficiency_A": round(37.5/(.85*20), 3),
        "PD_input_current_at_90pct_efficiency_A": round(37.5/(.90*20), 3),
        "TPS259474A_R26_820ohm_nominal_current_trip_A": round(3334/820, 2),
        "TPS25947_typical_Ron_28p3mohm_at_3A_loss_W": round(3**2*.0283, 3),
        "U3_0p3mm_escapes": narrow,
        "limits": [
            "Track estimates are intentionally conservative by assigning full 3 A to the whole narrow trace, even where its pad and zones are connected.",
            "Copper foil tolerance, zone continuity under soldered parts, via plating, board stackup, thermal dissipation, connector and cable losses are not evaluated.",
            "TPS25947 R_ILM relationship and R_ON are typical, not guaranteed max/min thresholds; check datasheet/current-limit distributions.",
            "Need real 3 A dummy-load test, source-contract check, voltage droop, IR/thermocouple temperature rise, and RF test before connecting FT2D.",
        ],
    }


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("Usage: screen_rev_b_power_path.py BOARD.kicad_pcb [report.json]")
    result = report(Path(sys.argv[1]))
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
