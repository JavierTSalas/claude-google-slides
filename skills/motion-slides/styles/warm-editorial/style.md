---
spec: slide-style/v1
name: Warm editorial
slug: warm-editorial
source: { kind: pptx, ref: "addsumtech/slides_maker editorial + owner pick #7" }
use_for: [photo-split, quote, big-number, explanation]
avoid_for: [openers that need energy]
canvas: { width_in: 10, height_in: 5.625, margin_in: 0.5 }
palette:
  bg: "#F1EBE1"       # cream paper
  ink: "#1E1A16"      # warm black
  accent: "#B5462B"   # terracotta
  muted: "#4A4038"
  surface: "#E2B07F"  # sunlit tan
  accent2: "#2F4B2B"  # forest, for pairing
type:
  display: { family: Instrument Serif, weight: 400, italic: false, case: sentence, tracking_em: 0, size_pt: 40 }
  emphasis: { family: Instrument Serif, weight: 400, italic: true, case: sentence, tracking_em: 0, size_pt: 40 }
  body: { family: Instrument Sans, weight: 400, italic: false, case: sentence, tracking_em: 0, size_pt: 12 }
  label: { family: DM Mono, weight: 400, italic: false, case: sentence, tracking_em: 0, size_pt: 9 }
layout:
  density: medium
  max_words: 40
  align: left
  archetypes: [photo-split, quote, big-number]
  ornaments: [short terracotta rule above the kicker, arched photo, numbered steps]
motion:
  energy: gentle
  transition: { kind: fade, speed: slow }
  builds: { kinds: [fade, fly-bottom], order: headline-body-steps, duration_ms: 500, stagger_ms: 0, mode: after }
  loops:
    - { name: window-light, what: "blind shadows drift over an arched warm photo", seconds: 10, fps: 8, size_px: 400, colors: [bg], placement: "left, 5.0 in tall" }
rules:
  do:
    - Lead with a real or rendered image. Text sits in one right column.
    - Headline in two short lines, the second italic.
    - Numbers in terracotta serif; labels under them in small mono.
  dont:
    - No bullet lists. Use up to three numbered steps.
    - No stock-photo people. Prefer light, texture, objects.
    - No card grids.
---

# Warm editorial

Photo-led and calm. Cream paper, warm black serif, terracotta details. Reads like a printed feature spread.

## Signature moves

- An arched image on the left with slow window light moving across it.
- A 0.55 in terracotta rule above a small bold kicker.
- Three numbered steps that rise in one after another.

## Deck theme

Paste into `deck.json` → `"theme"`.

```json
{
  "colors": { "bg": "#F1EBE1", "ink": "#1E1A16", "accent": "#B5462B", "muted": "#4A4038", "surface": "#E2B07F", "accent2": "#2F4B2B" },
  "fonts": { "display": "Instrument Serif", "body": "Instrument Sans", "label": "DM Mono" },
  "type": {
    "title":    { "font": "display", "size": 96, "color": "ink", "spacing": 0.9 },
    "hero":     { "font": "display", "size": 54, "color": "ink" },
    "headline": { "font": "display", "size": 40, "color": "ink", "spacing": 0.95 },
    "number":   { "font": "display", "color": "accent" },
    "quote":    { "font": "display", "size": 34, "italic": true, "color": "ink", "spacing": 1.0 },
    "kicker":   { "font": "body", "size": 10, "bold": true, "color": "accent" },
    "step":     { "font": "body", "size": 12, "bold": true, "color": "ink" },
    "body":     { "font": "body", "size": 12, "color": "muted", "spacing": 1.15 },
    "label":    { "font": "label", "size": 9, "color": "muted" }
  }
}
```
