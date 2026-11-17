---
spec: slide-style/v1
name: Warm editorial
slug: warm-editorial
summary: Cream paper, warm black serif, terracotta details and an arched sunlit picture. A printed feature spread.
source:
  kind: pptx
  ref: Owner pick #7 from the discovery report (photo-led editorial PPTX)
  took: photo-led split layout, serif headline with italic turn, numbered steps, rule above kicker
use_for: [explanation, how it works, process, quotes, single metrics]
avoid_for: [openers that need energy]

canvas: {width_in: 10, height_in: 5.625, margin_in: 0.5}

palette:
  bg: "#F1EBE1"        # cream paper
  ink: "#1E1A16"       # warm black
  accent: "#B5462B"    # terracotta
  muted: "#4A4038"     # body brown
  surface: "#E2B07F"   # sunlit tan
  accent2: "#2F4B2B"   # forest, shared with editorial-forest

type:
  display:  {family: Instrument Serif, weight: 400, case: as-is, size_pt: [34, 96], line: 0.95, color: ink}
  emphasis: {family: Instrument Serif, weight: 400, italic: true, case: as-is, size_pt: [34, 96], line: 0.95, color: ink}
  body:     {family: Instrument Sans, weight: 400, size_pt: [12, 14], line: 1.15, color: muted}
  label:    {family: DM Mono, weight: 400, case: as-is, size_pt: [9, 10], color: muted}
  number:   {family: Instrument Serif, weight: 400, size_pt: [30, 210], line: 0.85, color: accent}

layout:
  density: medium
  align: left
  archetypes: [photo-split, quote, big-number]
  ornaments:
    - {name: arched picture with drifting window light, make: loop}
    - {name: short terracotta rule above the kicker, make: native}
    - {name: numbered steps, make: native}

motion:
  energy: calm
  transition: {kind: fade, speed: slow}
  builds:
    fx: [fade, fly-bottom]
    duration_ms: [450, 600]
    trigger: after
    order: headline, body, then steps rise one by one
  loops:
    - {name: window-light, what: Blind shadows drift and a leaf sways across an arched warm picture, seconds: 10, fps: 8, size_px: [400, 511], colors: [bg], placement: left, 5.0 in tall}

rules:
  do:
    - Lead with a picture or the light loop. Text sits in one right-hand column.
    - Headline in two short lines, the second italic.
    - Numbers in terracotta serif, small mono labels under them.
  dont:
    - No bullet lists. Use up to three numbered steps.
    - No stock photos of people. Prefer light, texture, objects.
    - No card grids.
---

# Warm editorial

## Signature

- An arched picture on the left with slow window light moving across it.
- A 0.55 in terracotta rule above a small bold kicker.
- Three numbered steps that rise in one after another.

## Slide recipes

From [reference/recipes.md](../../reference/recipes.md):

- `photo-split`: the core layout. Up to 40 words.
- `quote`: italic warm-black quote, terracotta rule.
- `big-number`: terracotta numeral on cream.
- Titles and section breaks: switch to `editorial-forest`.

## Motion

Gentle. Fade transition (slow). Headline 600 ms, body 500 ms, then each step flies up from the bottom in 450 ms. The light loop runs from slide open.

## Do / Don't

See `rules` above. The arch is a pre-rendered loop or a pre-cropped PNG; the Slides API cannot mask images.

## Example prompt

> Explain our three-step onboarding on one warm editorial slide, with the window-light loop on the left.

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
