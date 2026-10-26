"""Build a JLCPCB *quote and assembly preview* pack, never a signed release.

Keeps the stringent export_jlcpcb_release_rev_b.sh gate intact. An upload to
JLCPCB's quotation/placement preview is NOT approval to submit a fabrication
order. Run in a clean KiCad 10 environment with kicad-cli on PATH.

Usage: python3 engineering_tools/build_rev_b_jlc_quote_preview.py
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
BOARD_BASE = "FT2D_PD20V_12V5_3A_评审原理图"
PROJECT = ROOT / "hardware" / "Rev_B"
BOARD = PROJECT / f"{BOARD_BASE}.kicad_pcb"
SCH = PROJECT / f"{BOARD_BASE}.kicad_sch"
REVIEW = ROOT / "manufacturing" / "Rev_B" / "REVIEW_ONLY_NOT_FOR_FAB"
OUT = ROOT / "manufacturing" / "Rev_B" / "QUOTE_PREVIEW_ONLY_NOT_RELEASED"
PREFLIGHT = ROOT / "manufacturing" / "Rev_B" / "PREFLIGHT"


def run(*args):
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)


def violations(json_path: Path, *categories):
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return {category: len(data.get(category, [])) for category in categories}


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    if not BOARD.is_file() or not SCH.is_file():
        raise SystemExit("Missing official Rev B KiCad project")
    OUT.mkdir(parents=True, exist_ok=True)
    PREFLIGHT.mkdir(parents=True, exist_ok=True)

    erc = PREFLIGHT / "erc.json"
    drc = PREFLIGHT / "drc.json"
    native = PREFLIGHT / "kicad_native_smt_positions.csv"
    run("kicad-cli", "sch", "erc", "--format", "json", "-o", erc, SCH)
    run("kicad-cli", "pcb", "drc", "--schematic-parity", "--refill-zones", "--format", "json", "-o", drc, BOARD)
    errors = {
        "ERC_violations": violations(erc, "violations")["violations"],
        "PCB_DRC_violations": violations(drc, "violations")["violations"],
        "PCB_unconnected": violations(drc, "unconnected_items")["unconnected_items"],
        "schematic_parity": violations(drc, "schematic_parity")["schematic_parity"],
    }
    if any(errors.values()):
        raise SystemExit(f"REFUSE: KiCad ERC/DRC gate not clean: {errors}")

    run("kicad-cli", "pcb", "export", "pos", "--format", "csv", "--units", "mm",
        "--side", "front", "--smd-only", "--exclude-dnp", "-o", native, BOARD)
    original_bom = REVIEW / "JLC_CANDIDATE_BOM_NOT_APPROVED.csv"
    original_cpl = REVIEW / "JLC_CANDIDATE_CPL_NOT_APPROVED.csv"
    run("python3", ROOT / "engineering_tools" / "validate_jlc_smt_release_rev_b.py",
        original_bom, original_cpl, native)

    bom = OUT / "FT2D_RevB_JLC_BOM_QUOTE_ONLY_NOT_APPROVED.csv"
    cpl = OUT / "FT2D_RevB_JLC_CPL_QUOTE_ONLY_NOT_APPROVED.csv"
    shutil.copyfile(original_bom, bom)
    shutil.copyfile(original_cpl, cpl)

    # Both drill files and complete four copper layers need to be inside the
    # same flat archive for an unambiguous JLCPCB Gerber upload.
    archive = OUT / "FT2D_RevB_4L_Gerber_Drill_QUOTE_ONLY.zip"
    with tempfile.TemporaryDirectory(prefix="ft2d-jlc-quote-") as temp:
        raw = Path(temp)
        run("kicad-cli", "pcb", "export", "gerbers", "--layers",
            "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts",
            "--subtract-soldermask", "-o", raw, BOARD)
        run("kicad-cli", "pcb", "export", "drill", "--format", "excellon",
            "--excellon-units", "mm", "--excellon-separate-th", "-o", raw, BOARD)
        parts = sorted(x for x in raw.iterdir() if x.is_file() and x.suffix.lower() in {
            ".gtl", ".g1", ".g2", ".gbl", ".gts", ".gbs",
            ".gto", ".gbo", ".gtp", ".gbp", ".gm1", ".gbrjob", ".drl",
        })
        if len(parts) != 14:
            raise SystemExit(f"REFUSE: expected 14 Gerber + drill files, got {len(parts)}: {[x.name for x in parts]}")
        if len([x for x in parts if x.suffix.lower() in {".gtl", ".g1", ".g2", ".gbl"}]) != 4:
            raise SystemExit("REFUSE: not exactly four Cu layers")
        if len([x for x in parts if x.suffix.lower() == ".drl"]) != 2:
            raise SystemExit("REFUSE: missing PTH/NPTH drill files")
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=True) as zipper:
            for part in parts:
                zipper.write(part, arcname=part.name)

    b_refs = [row["Designator"] for row in rows(bom)]
    c_refs = [row["Designator"] for row in rows(cpl)]
    if len(b_refs) != 53 or len(c_refs) != 53:
        raise SystemExit(f"REFUSE: expected 53 SMT ref placements, got {len(b_refs)}/{len(c_refs)}")
    manifest = {
        "status": "QUOTE_AND_VISUAL_PREVIEW_ONLY__NO_FAB_OR_SMT_APPROVAL",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pcb": str(BOARD.relative_to(ROOT)),
        "schematic": str(SCH.relative_to(ROOT)),
        "ERC_DRC_counts": errors,
        "top_SMT_refs_in_BOM": len(b_refs),
        "top_SMT_refs_in_CPL": len(c_refs),
        "distinct_candidate_LCSC_codes": len({row["JLCPCB Part #"] for row in rows(bom)}),
        "electrical_thermal_SMTPreview_PD_NVM_signoffs": "NOT APPROVED",
        "files_sha256": {path.name: digest(path) for path in (archive, bom, cpl)},
        "source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in (BOARD, SCH)},
    }
    (OUT / "PREVIEW_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    print("NOTE: strictly a quotation and placement-PREVIEW pack; no order has been placed or approved.")


if __name__ == "__main__":
    main()
