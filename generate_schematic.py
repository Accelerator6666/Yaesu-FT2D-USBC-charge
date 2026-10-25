"""Generate a review-only KiCad schematic from the FT2D Rev A pin table.

This intentionally does not generate a PCB or claim verified manufacturer footprints.
"""

from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
import csv
import json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "FT2D_PD20V_12V5_3A_评审原理图.kicad_sch"
SYM_OUT = ROOT / "FT2D.kicad_sym"
SYM_TABLE = ROOT / "sym-lib-table"
FP_TABLE = ROOT / "fp-lib-table"
PRO_OUT = OUT.with_suffix(".kicad_pro")
PROJECT = OUT.stem
_uuid_index = 0


def next_uuid():
    """Keep schematic IDs stable when footprints or values are refined."""
    global _uuid_index
    _uuid_index += 1
    return str(uuid5(NAMESPACE_URL, f"ft2d-pd-rev-a/{_uuid_index}"))


ROOT_UUID = next_uuid()


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


parts = []


def part(ref, value, pins, footprint="", x=None, y=None, dnp=False):
    parts.append(dict(ref=ref, value=value, pins=pins, footprint=footprint,
                      x=x, y=y, dnp=dnp))


R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"

part("J1", "USB4085-GF-A", [
    ("A1", "GND", "GND"), ("A4", "VBUS", "USB_VBUS"),
    ("A5", "CC1", "CC1"), ("A6", "D+", None), ("A7", "D-", None),
    ("A8", "SBU1", None), ("A9", "VBUS", "USB_VBUS"),
    ("A12", "GND", "GND"), ("B1", "GND", "GND"),
    ("B4", "VBUS", "USB_VBUS"), ("B5", "CC2", "CC2"),
    ("B6", "D+", None), ("B7", "D-", None), ("B8", "SBU2", None),
    ("B9", "VBUS", "USB_VBUS"), ("B12", "GND", "GND"),
    ("SH", "Shield", "GND")],
    "Connector_USB:USB_C_Receptacle_GCT_USB4085", 50.8, 60.96)

part("U1", "STUSB4500QTR", [
    ("1", "CC1DB", "CC1"), ("2", "CC1", "CC1"), ("3", "NC", None),
    ("4", "CC2", "CC2"), ("5", "CC2DB", "CC2"),
    ("6", "RESET", "PD_RESET"), ("7", "SCL", "SCL"),
    ("8", "SDA", "SDA"), ("9", "DISCH", "PD_DISCH"),
    ("10", "GND", "GND"), ("11", "ATTACH", None),
    ("12", "ADDR0", "GND"), ("13", "ADDR1", "GND"),
    ("14", "POWER_OK3", None), ("15", "GPIO", None),
    ("16", "VBUS_EN_SNK", "VBUS_EN_SNK"),
    ("17", "A_B_SIDE", None), ("18", "VBUS_VS_DISCH", "PD_VBUS_SENSE"),
    ("19", "ALERT", None), ("20", "POWER_OK2", None),
    ("21", "VREG_1V2", "PD_1V2"), ("22", "VSYS", "GND"),
    ("23", "VREG_2V7", "PD_2V7"), ("24", "VDD", "VBUS_RAW"),
    ("25", "EP", "GND")],
    "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm", 121.92, 60.96)

part("Q1", "STL6P3LLH6", [
    ("1", "S", "VBUS_RAW"), ("2", "S", "VBUS_RAW"),
    ("3", "S", "VBUS_RAW"), ("4", "G", "PD_GATE"),
    ("5", "D", "VBUS_SW"), ("6", "D", "VBUS_SW"),
    ("7", "D", "VBUS_SW"), ("8", "D", "VBUS_SW")],
    "FT2D:ST_PowerFLAT_3p3_TypeF", 193.04, 60.96)

part("U2", "LM61460AASQRJRRQ1", [
    ("1", "BIAS", "GND"), ("2", "VCC", "BUCK_VCC"),
    ("3", "AGND", "GND"), ("4", "FB", "FB_U2"),
    ("5", "PGOOD", "BUCK_PGOOD"), ("6", "RT", "BUCK_RT"),
    ("7", "EN/SYNC", "EN_U2"), ("8", "VIN1", "VBUS_SW"),
    ("9", "PGND1", "GND"), ("10", "SW", "SW"),
    ("11", "PGND2", "GND"), ("12", "VIN2", "VBUS_SW"),
    ("13", "RBOOT", "RBOOT_U2"), ("14", "CBOOT", "CBOOT_U2")],
    "FT2D:TI_RJR0014A", 264.16, 60.96)

part("U3", "TPS259474ARPWR", [
    ("1", "EN/UVLO", "UVLO_U3"), ("2", "OVLO", "OVLO_U3"),
    ("3", "PG", "PG_U3"), ("4", "PGTH", "PGTH_U3"),
    ("5", "IN", "V12P5"), ("6", "OUT", "VOUT"),
    ("7", "DVDT", "DVDT_U3"), ("8", "GND", "GND"),
    ("9", "ILM", "ILM_U3"), ("10", "ITIMER", "ITIMER_U3")],
    "FT2D:TI_RPW0010A", 335.28, 60.96)

part("J2", "PD_PROGRAM_TEST", [
    ("1", "GND", "GND"), ("2", "SCL", "SCL"),
    ("3", "SDA", "SDA"), ("4", "2V7_TEST", "PD_2V7"),
    ("5", "VBUS_TEST", "VBUS_RAW"), ("6", "RESET", "PD_RESET")],
    "FT2D:PD_Programming_Pads_1x06_P2p54", 406.4, 60.96)

part("J3", "E-DC-6_PIGTAIL", [("1", "+12.5V", "VOUT"),
                                  ("2", "GND", "GND")], "FT2D:Wire_Pads_2x_P3mm", 477.52, 60.96)


def two(ref, value, a, b, footprint="", dnp=False):
    part(ref, value, [("1", "1", a), ("2", "2", b)], footprint, dnp=dnp)


two("F1", "1206SFS300F/32", "USB_VBUS", "VBUS_RAW", "Fuse:Fuse_1206_3216Metric")
two("D1", "ESDA25P35-1U1M", "USB_VBUS", "GND", "FT2D:ST_ESDA25P35_1U1M")
part("D2", "ESDA25W", [("1", "CC1", "CC1"),
                         ("2", "CC2", "CC2"), ("3", "GND", "GND")],
     "Package_TO_SOT_SMD:SOT-323_SC-70")
part("TP1", "PG_U3_TEST", [("1", "PG_U3", "PG_U3")],
     "TestPoint:TestPoint_Pad_1.0x1.0mm", 548.64, 60.96)
two("L1", "SRP1238A-100M_10uH", "SW", "V12P5", "FT2D:Bourns_SRP1238A")

resistors = [
    ("R1", "10k", "PD_RESET", "GND"),
    ("R2", "4k7", "SCL", "PD_2V7"),
    ("R3", "4k7", "SDA", "PD_2V7"),
    ("R4", "1k", "PD_DISCH", "VBUS_SW"),
    ("R5", "22k", "VBUS_EN_SNK", "PD_GATE"),
    ("R6", "470R", "PD_VBUS_SENSE", "VBUS_RAW"),
    ("R7", "100k", "PD_GATE", "VBUS_RAW"),
    ("R12", "100k_0.1%", "V12P5", "FB_U2"),
    ("R13", "8k66_0.1%", "FB_U2", "GND"),
    ("R14", "1k_DNP", "V12P5", "CFF_SERIES"),
    ("R15", "100k", "BUCK_PGOOD", "BUCK_VCC"),
    ("R16", "33k2", "BUCK_RT", "GND"),
    ("R17", "133k", "VBUS_SW", "EN_U2"),
    ("R18", "10k", "EN_U2", "GND"),
    ("R19", "0R", "RBOOT_U2", "CBOOT_U2"),
    ("R20", "470k", "V12P5", "UVLO_U3"),
    ("R21", "100k", "UVLO_U3", "GND"),
    ("R22", "101k", "V12P5", "OVLO_U3"),
    ("R23", "10k", "OVLO_U3", "GND"),
    ("R24", "100k", "V12P5", "PGTH_U3"),
    ("R25", "12k", "PGTH_U3", "GND"),
    ("R26", "820R", "ILM_U3", "GND"),
]
for row in resistors:
    two(*row, R0603, dnp=row[0] == "R14")

caps = [
    ("C1", "1u_6V3", "PD_1V2", "GND", C0603),
    ("C2", "1u_6V3", "PD_2V7", "GND", C0603),
    ("C3", "1u_25V", "VBUS_RAW", "GND", C0805),
    ("C4", "47n_50V", "PD_GATE", "VBUS_RAW", C0603),
    ("C5", "1u_25V", "PD_VBUS_SENSE", "GND", C0805),
    ("C10", "1u_16V", "BUCK_VCC", "GND", C0603),
    ("C11", "10p_DNP", "CFF_SERIES", "FB_U2", C0603),
    ("C12", "100n_50V", "VBUS_SW", "GND", C0603),
    ("C13", "100n_50V", "VBUS_SW", "GND", C0603),
    ("C14", "10u_50V", "VBUS_SW", "GND", C1210),
    ("C15", "10u_50V", "VBUS_SW", "GND", C1210),
    ("C16", "10u_50V", "VBUS_SW", "GND", C1210),
    ("C17", "10u_50V", "VBUS_SW", "GND", C1210),
    ("C18", "EEHZL1V470R_47u", "VBUS_SW", "GND", "Capacitor_SMD:CP_Elec_5x5.8"),
    ("C19", "100n_16V", "CBOOT_U2", "SW", C0603),
    ("C20", "47u_25V", "V12P5", "GND", C1210),
    ("C21", "47u_25V", "V12P5", "GND", C1210),
    ("C22", "47u_25V", "V12P5", "GND", C1210),
    ("C23", "250AVHT221M0608_220u", "V12P5", "GND", "Capacitor_SMD:CP_Elec_6.3x7.7"),
    ("C24", "100n_25V", "V12P5", "GND", C0603),
    ("C25", "47u_25V", "VOUT", "GND", C1210),
    ("C26", "100n_25V", "VOUT", "GND", C0603),
    ("C27", "3n3_25V", "DVDT_U3", "GND", C0603),
    ("C28", "2n2_10V", "ITIMER_U3", "GND", C0603),
]
for ref, value, a, b, fp in caps:
    two(ref, value, a, b, fp, dnp=ref == "C11")

# A2 landscape: main function blocks occupy the upper band, passives in a grid.
small = [p for p in parts if p["x"] is None]
for idx, p in enumerate(small):
    p["x"] = 50.8 + (idx % 10) * 53.34
    p["y"] = 137.16 + (idx // 10) * 38.1


def fmt(n):
    return f"{n:.4f}".rstrip("0").rstrip(".")


def pin_layout(pins):
    nleft = (len(pins) + 1) // 2
    nright = len(pins) - nleft
    rows = []
    for i, (num, name, net) in enumerate(pins):
        if i < nleft:
            row = i
            x = -10.16
            y = (nleft - 1) * 1.27 - row * 2.54
            angle = 0
        else:
            row = i - nleft
            x = 10.16
            y = (nright - 1) * 1.27 - row * 2.54
            angle = 180
        rows.append((num, name, net, x, y, angle))
    halfheight = max(nleft, nright, 2) * 1.27 + 1.27
    return rows, halfheight


lines = ["(kicad_sch", "  (version 20250114)", "  (generator \"eeschema\")",
         f"  (uuid {q(ROOT_UUID)})", "  (paper \"A2\")",
         "  (title_block (title \"FT2D PD20V to 12.5V/3A - ELECTRICAL REVIEW ONLY\")",
         "    (rev \"A\") (comment 1 \"Not a PCB. Footprints and performance unverified.\"))",
         "  (lib_symbols"]
lib_start = len(lines)

for p in parts:
    ref = p["ref"]
    rows, hh = pin_layout(p["pins"])
    prefix = "".join(c for c in ref if c.isalpha())
    lines += [f"    (symbol {q('FT2D:' + ref)}",
              "      (pin_names (offset 0.508))",
              "      (exclude_from_sim no) (in_bom yes) (on_board yes)",
              f"      (property \"Reference\" {q(prefix)} (at 0 {fmt(hh + 2.54)} 0) (effects (font (size 1 1))))",
              f"      (property \"Value\" {q(p['value'])} (at 0 {fmt(-hh - 2.54)} 0) (effects (font (size 1 1))))",
              f"      (property \"Footprint\" {q(p['footprint'])} (at 0 0 0) (effects (font (size 1 1)) (hide yes)))",
              "      (property \"Datasheet\" \"\" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))",
              f"      (symbol {q(ref + '_0_1')}",
              f"        (rectangle (start -7.62 {fmt(-hh)}) (end 7.62 {fmt(hh)}) (stroke (width 0.254) (type default)) (fill (type background)))",
              "      )",
              f"      (symbol {q(ref + '_1_1')}"]
    for num, name, net, x, y, angle in rows:
        lines.append(f"        (pin passive line (at {fmt(x)} {fmt(y)} {angle}) (length 2.54) (name {q(name)} (effects (font (size 0.8 0.8)))) (number {q(num)} (effects (font (size 0.8 0.8)))))")
    lines += ["      )", "    )"]
lines += ["  )"]
lib_end = len(lines) - 1

for p in parts:
    x, y = p["x"], p["y"]
    ref = p["ref"]
    rows, hh = pin_layout(p["pins"])
    uid = next_uuid()
    lines += ["  (symbol", f"    (lib_id {q('FT2D:' + ref)})",
              f"    (at {fmt(x)} {fmt(y)} 0) (unit 1)",
              "    (exclude_from_sim no) (in_bom yes) (on_board yes)",
              f"    (dnp {'yes' if p['dnp'] else 'no'}) (uuid {q(uid)})",
              f"    (property \"Reference\" {q(ref)} (at {fmt(x)} {fmt(y-hh-2.54)} 0) (effects (font (size 1 1))))",
              f"    (property \"Value\" {q(p['value'])} (at {fmt(x)} {fmt(y+hh+2.54)} 0) (effects (font (size 1 1))))",
              f"    (property \"Footprint\" {q(p['footprint'])} (at {fmt(x)} {fmt(y)} 0) (effects (font (size 1 1)) (hide yes)))",
              "    (property \"Datasheet\" \"\" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))"]
    for num, name, net, px, py, angle in rows:
        lines.append(f"    (pin {q(num)} (uuid {q(next_uuid())}))")
    lines += ["    (instances", f"      (project {q(PROJECT)} (path {q('/' + ROOT_UUID)} (reference {q(ref)}) (unit 1)))",
              "    )", "  )"]
    for num, name, net, px, py, angle in rows:
        ax, ay = x + px, y - py
        if net is None:
            lines.append(f"  (no_connect (at {fmt(ax)} {fmt(ay)}) (uuid {q(next_uuid())}))")
        else:
            label_angle = 180 if px < 0 else 0
            justify = "right bottom" if px < 0 else "left bottom"
            lines.append(f"  (label {q(net)} (at {fmt(ax)} {fmt(ay)} {label_angle}) (effects (font (size 0.8 0.8)) (justify {justify})) (uuid {q(next_uuid())}))")

lines.append("  (embedded_fonts no)")
lines.append(")")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
library_lines = ["(kicad_symbol_lib", "  (version 20250114)",
                 '  (generator "kicad_symbol_editor")']
for item in lines[lib_start:lib_end]:
    if item.lstrip().startswith('(symbol "FT2D:'):
        item = item.replace('(symbol "FT2D:', '(symbol "', 1)
    library_lines.append(item)
library_lines.append(")")
SYM_OUT.write_text("\n".join(library_lines) + "\n", encoding="utf-8")
SYM_TABLE.write_text('(sym_lib_table (lib (name "FT2D") (type "KiCad") (uri "${KIPRJMOD}/FT2D.kicad_sym") (options "") (descr "FT2D review symbols")))\n', encoding="utf-8")
FP_TABLE.write_text('(fp_lib_table\n' + '\n'.join(
    f'  (lib (name "{name}") (type "KiCad") (uri "${{KICAD10_FOOTPRINT_DIR}}/{name}.pretty") (options "") (descr ""))'
    for name in ["Connector_USB", "Fuse", "Resistor_SMD", "Capacitor_SMD", "TestPoint", "Package_DFN_QFN", "Package_TO_SOT_SMD"]
) + '  (lib (name "FT2D") (type "KiCad") (uri "${KIPRJMOD}/FT2D.pretty") (options "") (descr "FT2D power-board custom footprints"))\n)\n', encoding="utf-8")
if not PRO_OUT.exists():
    PRO_OUT.write_text(json.dumps({"meta": {"version": 1}}) + "\n", encoding="utf-8")
print(OUT)
print(f"parts={len(parts)} pins={sum(len(p['pins']) for p in parts)}")
