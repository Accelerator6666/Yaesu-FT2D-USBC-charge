"""Experimentally reroute a Rev B working copy with KiCad 10 / Freerouting.

This is NOT a release step. The resulting board must pass full KiCad DRC,
have power-net copper reviewed, and have all assembly parts sourced before
manufacturing files can be released.

Example:
  /usr/bin/python3 autoroute_rev_b.py prepare board.kicad_pcb board.dsn
  java -jar freerouting.jar -de board.dsn -do board.ses
  /usr/bin/python3 autoroute_rev_b.py finish board.kicad_pcb board.ses
"""

import sys
from pathlib import Path

import pcbnew as p


def vec(x_mm, y_mm):
    return p.VECTOR2I(p.FromMM(x_mm), p.FromMM(y_mm))


def escape_track(board, net_name, a, b, width=0.15):
    trace = p.PCB_TRACK(board)
    trace.SetStart(vec(*a))
    trace.SetEnd(vec(*b))
    trace.SetWidth(p.FromMM(width))
    trace.SetLayer(p.F_Cu)
    trace.SetNet(board.FindNet(net_name))
    board.Add(trace)


def escape_via(board, net_name, xy):
    via = p.PCB_VIA(board)
    via.SetPosition(vec(*xy))
    via.SetWidth(p.FromMM(0.6))
    via.SetDrill(p.FromMM(0.3))
    via.SetViaType(p.VIATYPE_THROUGH)
    via.SetLayerPair(p.F_Cu, p.B_Cu)
    via.SetNet(board.FindNet(net_name))
    board.Add(via)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in {"prepare", "finish"}:
        raise SystemExit("Usage: autoroute_rev_b.py prepare|finish board.kicad_pcb input.dsn|input.ses")

    step, pcb_filename, routing_filename = sys.argv[1:]
    pcb_filename = str(Path(pcb_filename).resolve())
    routing_filename = str(Path(routing_filename).resolve())
    board = p.LoadBoard(pcb_filename)

    if step == "prepare":
        # Shorten the two impossible fan-outs of the legacy layout; no changes
        # to component rotation, pad numbering, or connected nets.
        moves = {"D2": (36.0, 37.0), "R22": (100.0, 46.0)}
        for footprint in board.GetFootprints():
            ref = footprint.GetReference()
            if ref in moves:
                footprint.SetPosition(vec(*moves[ref]))
                print("Moved", ref, "to", moves[ref], flush=True)

        previous_tracks = list(board.GetTracks())
        for track in previous_tracks:
            board.Remove(track)
        # Two fine-pitch pads have no usable outward fanout in the original
        # autorouted topology. Give them short, explicitly necked escapes.
        escape_track(board, "/CC1", (25.0, 40.3), (23.25, 40.3))
        escape_via(board, "/CC1", (23.25, 40.3))
        escape_track(board, "/OVLO_U3", (107.1, 42.775), (105.8, 42.775))
        escape_via(board, "/OVLO_U3", (105.8, 42.775))
        # USB-C connector has four VBUS through-hole contacts surrounded by
        # a 0.85 mm pitch pad field. Fan out away from the tightly packed row.
        usb_vbus_escapes = [
            ((25.0, 36.9), (23.2, 36.9)),  # A9
            ((26.35, 36.9), (28.4, 36.9)), # B4
            ((25.0, 41.15), (23.2, 41.15)),# A4
            ((26.35, 41.15), (28.4, 41.15)), # B9
        ]
        for a, b in usb_vbus_escapes:
            escape_track(board, "/USB_VBUS", a, b)
            escape_via(board, "/USB_VBUS", b)

        # The eFuse IN/OUT lands are 0.3 mm wide. Route outside the package
        # via these narrow necks instead of forcing a 0.6 mm trace over both.
        escape_track(board, "/V12P5", (107.75, 41.8), (106.3, 41.5))
        escape_via(board, "/V12P5", (106.3, 41.5))
        escape_track(board, "/VOUT", (108.25, 44.2), (110.1, 44.2))
        escape_via(board, "/VOUT", (110.1, 44.2))
        # Removing tracks invalidates the saved polygon fill. Specctra uses
        # unfilled zone outlines; KiCad's own DRC refills after SES import.
        p.SaveBoard(pcb_filename, board)
        success = p.ExportSpecctraDSN(board, routing_filename)
        print("Export DSN:", success, "removed tracks:", len(previous_tracks), flush=True)
        if not success:
            raise RuntimeError("KiCad could not export Specctra DSN")
    else:
        success = p.ImportSpecctraSES(board, routing_filename)
        print("Import SES:", success, "new routing items:", len(board.GetTracks()), flush=True)
        if not success:
            raise RuntimeError("KiCad could not import Specctra SES")
        p.SaveBoard(pcb_filename, board)


if __name__ == "__main__":
    main()
