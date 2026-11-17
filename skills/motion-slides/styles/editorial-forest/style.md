---
spec: slide-style/v1
name: Editorial forest
slug: editorial-forest
summary: Huge dusty-pink serif on deep forest green. Wide margins, mono labels, one small thing turning.
source:
  kind: deck
  ref: Owner picks #2 and #3 from the discovery report (soft editorial, editorial forest HTML templates)
  took: palette, type pairing, margins, label treatment
use_for: [titles, section breaks, closing, hero moments, big numbers, quotes]
avoid_for: [dense data, long lists, paragraphs]

canvas: {width_in: 10, height_in: 5.625, margin_in: 0.55}

palette:
  bg: "#2F4B2B"        # deep forest green
  ink: "#EBA6BD"       # dusty pink. Display type, loop ink
  accent: "#F1EBE1"    # cream. Headlines and hero lines
  muted: "#C9C2B0"     # body on green
  surface: "#24391F"   # darker green panel
  accent2: "#B5462B"   # terracotta, shared with warm-editorial

type:
  display:  {family: Instrument Serif, weight: 400, case: as-is, size_pt: [54, 104], line: 0.9, color: ink}
  emphasis: {family: Instrument Serif, weight: 400, italic: true, case: as-is, size_pt: [54, 104], line: 0.9, color: ink}
  body:     {family: Instrument Sans, weight: 400, size_pt: [12, 14], line: 1.15, color: muted}
  label:    {family: DM Mono, weight: 500, case: upper, size_pt: [9, 10], color: ink}
  number:   {family: Instrument Serif, weight: 400, size_pt: [180, 220], line: 0.85, color: ink}

layout:
  density: low
  align: left
  archetypes: [title, section, motion-hero, big-number, quote]
  ornaments:
    - {name: rotating text badge, make: loop}
    - {name: orbit rings, make: loop}
    - {name: thin rule, make: native}

motion:
  energy: calm
  transition: {kind: fade, speed: slow}
  builds:
    fx: [fade, fly-bottom]
    duration_ms: [600, 700]
    trigger: after
    order: display lines top to bottom, the last line flies up; labels never build
  loops:
    - {name: badge, what: Text ring turns around a still numeral, seconds: 12, fps: 12, size_px: [360, 360], colors: [bg, ink], placement: top right, 1.55 in}
    - {name: orbits, what: Planets orbit still rings, seconds: 12, fps: 15, size_px: [1024, 576], colors: [bg, ink, accent], placement: full bleed, offset right 0.7 in}

rules:
  do:
    - One display line per text box, so each line builds on its own.
    - Italicize the last word or line. It is the turn.
    - Mono caps labels at 9-10 pt on the page edge.
  dont:
    - No paragraphs on green. Move explanation to a warm-editorial slide.
    - No more than one loop per slide.
    - No shadows, gradients or glow.
---

# Editorial forest

## Signature

- A three-line title at 104 pt, the last line italic, flying up last.
- A 1.55 in badge loop turning in the top-right corner. Its ground is the slide green, exactly.
- Mono caps date or section label on the bottom edge. Nothing else on a title.

## Slide recipes

All from [reference/recipes.md](../../reference/recipes.md):

- `title`: as written. 3 to 4 words.
- `motion-hero`: `orbits` loop, cream `hero` line then pink italic line.
- `big-number`: pink numeral, cream unit, one muted sentence.
- `quote`, `section`: as written.
- Content with a picture: switch to `warm-editorial` (`photo-split`). Same fonts, so the deck stays one voice.

## Motion

Slow and sparse. Fade transition (slow). Lines fade in 600 ms each, the last flies up 700 ms. One loop at most: badge on titles, orbits on hero slides.

## Do / Don't

See `rules` above. Pair with `warm-editorial`: forest for beats, warm for explanation.

## Example prompt

> Make a 6-slide kickoff deck. Editorial forest for the title, sections and closing, warm editorial for the two explanation slides.

## Deck theme

Paste into `deck.json` → `"theme"`.

```json
{
  "colors": { "bg": "#2F4B2B", "ink": "#EBA6BD", "accent": "#F1EBE1", "muted": "#C9C2B0", "surface": "#24391F", "accent2": "#B5462B" },
  "fonts": { "display": "Instrument Serif", "body": "Instrument Sans", "label": "DM Mono" },
  "type": {
    "title":    { "font": "display", "size": 104, "color": "ink", "spacing": 0.9 },
    "hero":     { "font": "display", "size": 54, "color": "accent" },
    "headline": { "font": "display", "size": 40, "color": "accent", "spacing": 0.95 },
    "number":   { "font": "display", "color": "ink" },
    "quote":    { "font": "display", "size": 34, "italic": true, "color": "accent", "spacing": 1.0 },
    "kicker":   { "font": "label", "size": 10, "color": "ink" },
    "step":     { "font": "body", "size": 12, "bold": true, "color": "accent" },
    "body":     { "font": "body", "size": 12, "color": "muted", "spacing": 1.15 },
    "label":    { "font": "label", "size": 9, "color": "ink" }
  }
}
```
