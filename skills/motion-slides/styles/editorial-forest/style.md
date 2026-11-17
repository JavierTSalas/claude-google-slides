---
spec: slide-style/v1
name: Editorial forest
slug: editorial-forest
source: { kind: deck, ref: "zarazhangrui/beautiful-html-templates 'editorial forest' + owner picks #2, #3" }
use_for: [title, section, motion-hero, big-number, quote]
avoid_for: [dense data, long lists]
canvas: { width_in: 10, height_in: 5.625, margin_in: 0.55 }
palette:
  bg: "#2F4B2B"       # deep forest green
  ink: "#EBA6BD"      # dusty pink
  accent: "#F1EBE1"   # cream
  muted: "#C9C2B0"
  surface: "#24391F"
type:
  display: { family: Instrument Serif, weight: 400, italic: false, case: sentence, tracking_em: 0, size_pt: 104 }
  emphasis: { family: Instrument Serif, weight: 400, italic: true, case: sentence, tracking_em: 0, size_pt: 104 }
  body: { family: Instrument Sans, weight: 400, italic: false, case: sentence, tracking_em: 0, size_pt: 12 }
  label: { family: DM Mono, weight: 500, italic: false, case: upper, tracking_em: 0, size_pt: 9 }
layout:
  density: sparse
  max_words: 12
  align: left
  archetypes: [title, motion-hero, big-number, quote, section]
  ornaments: [one small rotating badge, thin rules, nothing else]
motion:
  energy: calm
  transition: { kind: fade, speed: slow }
  builds: { kinds: [fade, fly-bottom], order: top-to-bottom, duration_ms: 600, stagger_ms: 0, mode: after }
  loops:
    - { name: badge, what: "text ring turns around a numeral", seconds: 12, fps: 12, size_px: 360, colors: [bg, ink], placement: "top right, 1.55 in" }
    - { name: orbits, what: "planets orbit still rings", seconds: 12, fps: 15, size_px: 1024, colors: [bg, ink, accent], placement: "full bleed, offset right 0.7 in" }
rules:
  do:
    - Set one huge serif line per text box so each line can build on its own.
    - Italicize the last word or line for the turn.
    - Keep labels in mono caps at 9-10 pt, at the page edges.
  dont:
    - No paragraph on a dark slide. Move it to a warm-editorial slide.
    - No more than one loop per slide.
    - No drop shadows, gradients or glow.
---

# Editorial forest

Quiet, confident, magazine-cover energy. Huge display serif in dusty pink on deep green. Wide margins. One small thing moves.

## Signature moves

- A title set at 104 pt over three lines, the last one italic, flying up last.
- A 1.55 in badge loop turning in a corner. Its ground equals the slide green exactly.
- Mono caps labels (date, section) at the bottom edge.

## Pairs with

`warm-editorial` for content slides. Same fonts, cream ground. Alternate them: forest for beats, warm for explanation.

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
