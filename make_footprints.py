"""Generate the non-standard PCB lands used by the FT2D prototype.

Dimensions below are millimetres, transcribed from the manufacturer land
patterns. Keep this source with the KiCad project so the custom footprints
remain auditable. A fabrication release still needs independent pad review.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "FT2D.pretty"
OUT.mkdir(exist_ok=True)


def pad(n, x, y, w, h):
    return (f'  (pad "{n}" smd rect (at {x:g} {y:g}) '
            f'(size {w:g} {h:g}) (layers "F.Cu" "F.Paste" "F.Mask"))')


def fp(name, description, body_w, body_h, pads):
    lines = [
        f'(footprint "{name}"',
        '  (version 20240108) (generator "pcbnew") (layer "F.Cu")',
        f'  (descr "{description}")',
        f'  (property "Reference" "REF**" (at 0 {-body_h/2-1.3:g}) '
        '(layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'  (property "Value" "{name}" (at 0 {body_h/2+1.3:g}) '
        '(layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'  (fp_rect (start {-body_w/2:g} {-body_h/2:g}) '
        f'(end {body_w/2:g} {body_h/2:g}) '
        '(stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))',
        f'  (fp_rect (start {-body_w/2-0.25:g} {-body_h/2-0.25:g}) '
        f'(end {body_w/2+0.25:g} {body_h/2+0.25:g}) '
        '(stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
        *[pad(*p) for p in pads],
        ')'
    ]
    (OUT / f"{name}.kicad_mod").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ST DS9257 Rev 4, Fig. 16: 3.3 x 3.3 PowerFLAT type F.
# Pad numbers 1-3 source, 4 gate, 5-8 common drain.
# Segmented common drain land retains each schematic pad number.
q1 = [(n, x, 1.55, 0.4, 0.75)
      for n, x in [(1, -0.975), (2, -0.325), (3, 0.325), (4, 0.975)]]
q1 += [(n, x, -0.5, 0.61, 2.4)
       for n, x in [(5, -0.915), (6, -0.305), (7, 0.305), (8, 0.915)]]
fp("ST_PowerFLAT_3p3_TypeF",
   "ST STL6P3LLH6; DS9257 Rev4 Figure 16", 3.3, 3.3, q1)

# TI RJR0014A, LM61460-Q1 data sheet example board layout. The edge
# terminals are represented by rectangular lands within the given extents.
# Fine-pitch placement and paste stencil need independent vendor check.
u2 = [
    (1, -1.75, -1.3, 0.8, 0.9),
    (2, -1.8, -0.525, 0.7, 0.25),
    (3, -1.8, 0, 0.7, 0.25),
    (4, -1.8, 0.525, 0.7, 0.25),
    (5, -1.75, 1.3, 0.8, 0.9),
    (6, -1.0, 1.5, 0.25, 0.7),
    (7, -0.55, 1.5, 0.25, 0.7),
    (8, 0.55, 1.5, 0.45, 0.7),
    (9, 1.75, 1.3, 0.8, 0.9),
    (10, 0.8, 0, 2.4, 0.4),
    (11, 1.75, -1.3, 0.8, 0.9),
    (12, 0.55, -1.5, 0.45, 0.7),
    (13, -0.55, -1.5, 0.25, 0.7),
    (14, -1.0, -1.5, 0.25, 0.7),
]
fp("TI_RJR0014A",
   "TI LM61460-Q1 RJR0014A; 4.0x3.5 mm VQFN-HR", 4.0, 3.5, u2)

# TI RPW0010A, TPS25947 data sheet package drawing. Pins 5/6 are the
# two long central power terminals; 1/4 and 7/10 have bent edge lands.
u3 = [
    (1, -0.9, -0.725, 0.6, 0.3),
    (2, -0.9, -0.225, 0.6, 0.25),
    (3, -0.9, 0.225, 0.6, 0.25),
    (4, -0.9, 0.725, 0.6, 0.3),
    (5, -0.25, 0, 0.3, 2.4),
    (6, 0.25, 0, 0.3, 2.4),
    (7, 0.9, 0.725, 0.6, 0.3),
    (8, 0.9, 0.225, 0.6, 0.25),
    (9, 0.9, -0.225, 0.6, 0.25),
    (10, 0.9, -0.725, 0.6, 0.3),
]
fp("TI_RPW0010A",
   "TI TPS25947 RPW0010A; 2.0x2.0 mm VQFN-HR", 2.0, 2.0, u3)

# Bourns SRP1238A Rev current data sheet: 14.2 overall, 8.0 gap,
# 5.0 pad height => 3.1 mm pad width.
fp("Bourns_SRP1238A",
   "Bourns SRP1238A; 14.2 mm overall land span, 8.0 mm gap",
   13.5, 12.5,
   [(1, -5.55, 0, 3.1, 5.0), (2, 5.55, 0, 3.1, 5.0)])

# ST DS14419 Rev 4, Fig. 14: 1.8 overall, 0.7 gap, 0.8 height.
fp("ST_ESDA25P35_1U1M",
   "ST ESDA25P35-1U1M; 1.6x1.0 mm QFN-2L", 1.6, 1.0,
   [(1, -0.625, 0, 0.55, 0.8), (2, 0.625, 0, 0.55, 0.8)])

# 2.54 mm pitch test pads are for a powered, 2.7 V-safe I2C jig only.
fp("PD_Programming_Pads_1x06_P2p54",
   "Six 1.5 mm test pads at 2.54 mm pitch", 15.0, 2.0,
   [(i, (i-3.5)*2.54, 0, 1.5, 1.5) for i in range(1, 7)])

# Solder pads for the verified E-DC-6 pigtail, not a barrel-jack footprint.
fp("Wire_Pads_2x_P3mm",
   "Two pigtail solder lands with external cable strain relief", 8.0, 4.0,
   [(1, -2.5, 0, 3.0, 3.0), (2, 2.5, 0, 3.0, 3.0)])

print(f"Generated {len(list(OUT.glob('*.kicad_mod')))} custom footprints in {OUT}")
