"""Build the gallery deck: gallery/gallery.pptx + gallery/build/out/scenes.js.

Usage: python3 build_gallery.py
Import gallery.pptx into Google Drive. It converts to native Google Slides.
"""
import os
from deckkit import Deck

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
d = Deck(os.path.join(ROOT, "assets"))

# Google Fonts only. Slides renders them natively.
SERIF, SANS, MONO, POSTER = "Instrument Serif", "Instrument Sans", "DM Mono", "Anton"
SWISS, SWISS_BLACK, SOFT = "Archivo", "Archivo Black", "Fraunces"

# ===== 1. Editorial title =====
GREEN, PINK = "2F4B2B", "EBA6BD"
d.slide(GREEN)
d.pic("badge.gif", 7.9, 0.32, w=1.55)
l1 = d.text(0.52, 0.95, 7.0, 1.35, ["Decks"], SERIF, 104, PINK, spacing=0.9)
l2 = d.text(0.52, 2.12, 7.0, 1.35, ["that"], SERIF, 104, PINK, spacing=0.9)
l3 = d.text(0.52, 3.29, 7.0, 1.35, ["move."], SERIF, 104, PINK, italic=True, spacing=0.9)
d.text(6.4, 5.08, 3.0, 0.25, ["NOV 2026"], MONO, 9, PINK, align="r")
d.builds([(l1, "fade", "after", 600), (l2, "fade", "after", 600), (l3, "fly-bottom", "after", 700)])

# ===== 2. Photo-led content =====
CREAM, TERRA, INK, BODY = "F1EBE1", "B5462B", "1E1A16", "4A4038"
d.slide(CREAM, "fade")
d.pic("light.gif", 0.45, 0.31, h=5.0)
d.shape("rect", 4.9, 0.78, 0.55, 0.03, TERRA)
d.text(4.9, 0.9, 4.4, 0.3, ["HOW IT WORKS"], SANS, 10, TERRA, bold=True)
h = d.text(4.9, 1.2, 4.6, 1.4, ["Native slides.", ("Rendered light.", {"italic": True})], SERIF, 40, INK, spacing=0.95)
b = d.text(4.9, 2.65, 4.3, 0.9, ["Layout and text are real Google Slides objects. Motion is built in HTML, "
                                 "rendered to a loop, and placed like any image."], SANS, 12, BODY, spacing=1.15)
steps = []
for i, (n, label, sub) in enumerate([("01", "Structure", "Slides API"), ("02", "Motion", "HTML → GIF"),
                                     ("03", "Builds", "Native fade + fly")]):
    steps.append(d.text(4.9 + i * 1.55, 3.75, 1.45, 1.2, [(n, {"font": SERIF, "size": 30, "color": TERRA}),
                                                         (label, {"font": SANS, "size": 12, "bold": True, "color": INK}),
                                                         (sub, {"font": MONO, "size": 9, "color": BODY})],
                        SANS, 12, INK, spacing=1.05))
d.builds([(h, "fade", "after", 600), (b, "fade", "after", 500)] + [(s, "fly-bottom", "after", 450) for s in steps])

# ===== 3. Kinetic poster =====
YELLOW, HOTPINK, BLUE, BLACK, WHITE = "FFD23F", "FF3D7F", "2B3BFF", "141414", "FFFFFF"
d.slide(YELLOW, "push")
pinkb = d.shape("rect", -0.45, 1.75, 6.4, 4.6, HOTPINK, rot=-5)
blueb = d.shape("rect", 6.05, -0.5, 4.5, 2.95, BLUE, rot=6)
blackb = d.shape("rect", 6.75, 3.3, 3.9, 2.7, BLACK, rot=-4)
decks = d.text(0.3, -0.42, 6.2, 2.3, ["DECKS"], POSTER, 150, BLACK, spacing=0.85)
tm = d.text(0.55, 2.2, 5.4, 3.0, ["THAT", "MOVE"], POSTER, 104, YELLOW, spacing=0.82, rot=-5)
outline = d.pic("outline_noplugins.png", 6.6, 0.18, w=2.25, rot=6)
live = d.text(6.62, 1.8, 3.2, 0.3, ["LIVE IN GOOGLE SLIDES"], SANS, 11, WHITE, bold=True, rot=6)
native = d.text(7.15, 3.72, 3.2, 1.6, ["100%", "NATIVE"], POSTER, 46, HOTPINK, spacing=0.85, rot=-4)
star = d.shape("star", 5.35, 1.55, 1.0, 1.0, BLACK, rot=12)
d.builds([(decks, "fly-top", "after", 450), (pinkb, "fly-left", "after", 450), (tm, "zoom", "after", 450),
          (blueb, "fly-top", "after", 400), (outline, "fade", "after", 400), (live, "fade", "with", 400),
          (blackb, "fly-right", "after", 400), (native, "zoom", "after", 400), (star, "spin", "after", 900)])

# ===== 4. Big number (Swiss data, all native) =====
PAPER, SIGNAL = "F5F5F2", "E63312"
d.slide(PAPER, "fade")
d.text(0.6, 0.55, 5.0, 0.3, ["WEEKLY DECKS SHIPPED"], SWISS, 11, BLACK, bold=True)
weeks = [12, 14, 15, 19, 22, 27, 31, 38]
x0, bw, gap, base, top = 6.25, 0.26, 0.13, 4.75, 3.55
span = len(weeks) * (bw + gap) - gap
bars = []
for i, v in enumerate(weeks):
    hgt = v / max(weeks) * top
    bars.append(d.shape("rect", x0 + i * (bw + gap), base - hgt, bw, hgt, SIGNAL if i == len(weeks) - 1 else BLACK))
# Mask in the ground color hides bars below the baseline, so fly-in reads as bars growing up.
d.shape("rect", x0 - 0.1, base, span + 0.2, 5.625 - base + 0.1, PAPER)
d.shape("rect", x0, base, span, 0.02, BLACK)
d.text(x0, base + 0.1, 0.6, 0.25, ["W1"], SWISS, 9, BLACK)
d.text(x0 + 7 * (bw + gap) - 0.34, base + 0.1, 0.6, 0.25, ["W8"], SWISS, 9, BLACK, align="r")
num = d.text(0.45, 1.25, 5.7, 2.9, ["3.2×"], SWISS_BLACK, 150, BLACK, spacing=0.9, anchor="b")
cap = d.text(0.6, 4.3, 5.0, 0.5, ["more decks in eight weeks."], SWISS, 20, BLACK)
d.builds([(b, "fly-bottom", "after", 260) for b in bars] + [(num, "zoom", "after", 500), (cap, "fade", "after", 400)])

# ===== 5-7. Panorama timeline: one line, three slides, push transitions read as a camera pan =====
CLAY, BONE = "C65D3B", "F6EEE3"
LINE_Y = 3.55
STOPS = [
    ("1987", "PowerPoint 1.0 ships for the Mac.", 0.6),
    ("2007", "Presentations arrive in Google Docs.", 3.4),
    ("2026", "Slides learn to move.", 5.0),
]
for i, (year, line, x) in enumerate(STOPS):
    last = i == len(STOPS) - 1
    d.slide(CLAY, "push" if i else "fade")
    if i == 0:
        d.text(0.6, 0.55, 5.0, 0.3, ["A SHORT HISTORY OF THE SLIDE"], MONO, 10, BONE)
    if last:  # ripple loop sits under the dot; GIF ground == slide ground
        d.pic("ripple.gif", x + 0.17 - 0.8, LINE_Y + 0.015 - 0.8, w=1.6)
    d.shape("rect", -0.2, LINE_Y, (x + 0.17 + 0.2) if last else 10.4, 0.03, BONE)
    dot = d.shape("ellipse", x + 0.06, LINE_Y - 0.095, 0.22, 0.22, BONE)
    yr = d.text(x, 0.9, 5.0, 2.3, [year], SOFT, 120, BONE, spacing=0.9, anchor="b")
    cp = d.text(x + 0.03, LINE_Y + 0.35, 4.6, 0.5, [line], SOFT, 20, BONE, italic=True)
    d.builds([(dot, "zoom", "after", 300), (yr, "fly-bottom", "after", 600), (cp, "fade", "after", 500)])

# ===== 8. Motion hero (rendered full-bleed loop + native text) =====
NIGHT = "141210"
d.slide(NIGHT, "fade")
d.pic("orbits-night.gif", 0.7, 0, w=10, h=5.625)
h1 = d.text(0.55, 1.45, 5.0, 0.95, ["Rendered once."], SERIF, 54, CREAM)
h2 = d.text(0.55, 2.3, 5.0, 0.95, ["Plays forever."], SERIF, 54, PINK, italic=True)
body = d.text(0.6, 3.55, 3.6, 0.6, ["HTML → GIF → Google Slides.", "144 frames. 0.9 MB. Loops on its own."], MONO, 9, CREAM, spacing=1.3)
d.builds([(h1, "fade", "after", 700), (h2, "fade", "after", 700), (body, "fade", "after", 500)])

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
d.save(os.path.join(ROOT, "gallery.pptx"), os.path.join(HERE, "out", "scenes.js"))
print("saved gallery.pptx,", len(d.scenes), "slides")
