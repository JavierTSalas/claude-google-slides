---
spec: slide-style/v1
name: Riso Overprint
slug: riso-overprint
summary: Two riso inks on cream paper. Heavy lowercase words meet from opposite sides. Where the inks cross, they print a third color.
source:
  kind: video
  ref: "onetake case film 'overlap' (feitangyuan/onetake, cases/overlap-15s). PolyForm Noncommercial: frames not committed."
  took: palette, type classes, motion tempo, entry directions, ornaments
use_for: [workshops, community events, creative briefs, launches, zines]
avoid_for: [financial results, legal, anything that needs long body text]

canvas: {width_in: 10, height_in: 5.625, margin_in: 0.5}

palette:
  bg: "#F0EADE"         # cream paper (measured)
  ink: "#00207A"        # overprint navy: pink x blue (measured). Body text, 11.8:1 on bg
  accent: "#EE3D98"     # fluorescent pink ink. Measured #F2419B, darkened 2% to reach 3:1 on bg. Display only
  accent2: "#006EA7"    # blue ink (measured). Display and labels, 4.6:1 on bg
  overprint: "#00207A"  # same as ink. Where accent and accent2 cross
  paper: "#FFFFFF"      # text on ink pills

type:
  display: {family: Archivo Black, weight: 900, case: lower, size_pt: [110, 180], line: 0.82, color: accent}
  heading: {family: Archivo Black, weight: 900, case: lower, size_pt: [28, 44], line: 0.9, color: accent2}
  body:    {family: Archivo, weight: 400, size_pt: [13, 16], line: 1.2, color: ink}
  label:   {family: Space Mono, weight: 700, case: lower, size_pt: [10, 12], line: 1.3, color: accent2}
  number:  {family: Archivo Black, weight: 900, size_pt: [180, 240], line: 0.8, color: accent}

layout:
  density: low
  align: mixed          # first word hugs the left margin, second word hugs the right
  archetypes: [title, statement, big-number, list-3, closing]
  ornaments:
    - {name: registration marks in the 4 corners, make: png}
    - {name: halftone dot cloud, make: loop}
    - {name: ink pill tags, make: native}

motion:
  energy: high
  transition: {kind: push, speed: fast}
  builds:
    fx: [fly-left, fly-right, zoom, fly-bottom]
    duration_ms: 400
    trigger: after
    order: pink word from the left, blue word from the right (with), then labels
  loops:
    - name: ink-pass
      what: Two halftone clouds, one per ink, drift apart and back on the dot grid. Overprint grows and shrinks.
      seconds: 6
      fps: 2
      size_px: [720, 720]
      colors: [bg, accent, accent2, overprint]
      placement: centered between the two display words, behind them

rules:
  do:
    - Two inks per slide, plus their overprint. Nothing else.
    - Split a phrase across the two inks. First half pink, second half blue.
    - Let display words touch or nearly touch in the middle.
    - Labels in lowercase mono, one line each.
  dont:
    - No gradients, shadows, photos in full color, or a third ink.
    - No pink body text. Pink is for display only (3:1 on bg).
    - No centered stacks of small text.
    - No cursors or "you / them" tags. They were the reference film's story, not its style.
---

# Riso Overprint

## Signature

1. **Two inks meet.** A phrase splits into a pink half and a blue half. They enter from opposite sides and land touching.
2. **Halftone overprint.** Dot clouds in both inks. Where they cross, deep navy.
3. **Print furniture.** Registration marks in the corners. Lowercase bold mono labels.

## Slide recipes

Canvas 10 × 5.625 in. Margin 0.5 in.

**Title.** Loop `ink-pass` at x 2.9, y 0.55, 4.2 × 4.2 in, behind everything. Word 1 in `display` pink, left 0.5, top 1.1, right-aligned to x 5.2. Word 2 in `display` `accent2`, left 4.9, top 1.1. Labels in `label` at y 4.85: left one pink, right one blue, right-aligned to 9.5. Registration marks at the 4 corners, 0.45 in square, 0.2 in inset. Builds: word 1 fly-left 400, word 2 fly-right with, labels fade after 300.

**Statement.** Two lines, max 8 words. Line 1 in `heading` at 54 pt pink, line 2 at 54 pt blue, both left at 0.5, tops 1.5 and 2.4. One `label` line under it at y 3.6. Builds: line 1 fly-left 400, line 2 fly-right after 400.

**Big number.** Number in `number` pink, left 0.5, top 0.7. A blue ink pill (rounded rectangle, `accent2` fill, `paper` text in `label`) under it. One `body` sentence, max 14 words, width 4 in. Loop on the right half, x 5.4, y 0.75, 4.1 in square. Builds: number zoom 450, pill fly-left after 350, body fade after 300.

**List of 3.** Three columns at x 0.5, 3.6, 6.7, width 2.8. Each: an ink pill (pink, blue, navy) with a mono number, a `heading` at 30 pt, a `body` line. Builds: columns fly-bottom after, 400 each.

**Closing.** One word in `display` at 260 pt, bleeding off the left edge (left -0.6). Split its letters across the two inks (two text boxes). One `label` line at y 4.9. Builds: pink part fly-left 450, blue part fly-right with.

## Motion

Fast and physical. The reference is one continuous camera move with ~300 ms moves and ~350 ms holds. Native builds chain `after` at 400 ms. Transitions push, fast, like a camera pan along a wall. The loop steps on the dot grid twice a second, so it reads as print, not video.

## Example prompt

> Make a 5-slide deck for a Thursday-night printmaking club, style riso-overprint. Title "print club". One stat, one 3-step list, close with "see you there".
