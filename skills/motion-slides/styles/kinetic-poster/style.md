---
spec: slide-style/v1
name: Kinetic poster
slug: kinetic-poster
source: { kind: video, ref: "bangtutorial/bang-motion kinetic colorblock + owner pick #8" }
use_for: [poster, title, section, big-number]
avoid_for: [explanations, quotes longer than 8 words]
canvas: { width_in: 10, height_in: 5.625, margin_in: 0.3 }
palette:
  bg: "#FFD23F"       # signal yellow
  ink: "#141414"      # black
  accent: "#FF3D7F"   # hot pink
  accent2: "#2B3BFF"  # ultramarine
  surface: "#FFFFFF"
  muted: "#141414"
type:
  display: { family: Anton, weight: 400, italic: false, case: upper, tracking_em: 0, size_pt: 104 }
  body: { family: Instrument Sans, weight: 700, italic: false, case: upper, tracking_em: 0, size_pt: 11 }
  label: { family: Instrument Sans, weight: 700, italic: false, case: upper, tracking_em: 0, size_pt: 9 }
layout:
  density: sparse
  max_words: 8
  align: free
  archetypes: [poster, big-number, section]
  ornaments: [rotated blocks (-6..6 deg), one outline word, a star, a marquee band]
motion:
  energy: loud
  transition: { kind: push, speed: med }
  builds: { kinds: [fly-top, fly-left, fly-right, zoom, spin, fade], order: big-to-small, duration_ms: 420, stagger_ms: 0, mode: after }
  loops:
    - { name: marquee, what: "heavy caps slide sideways in a band", seconds: 8, fps: 12, size_px: 1280, colors: [ink, bg], placement: "full width band, rotated -3 deg, low on the slide" }
rules:
  do:
    - Let type bleed off the page edge. Cropped letters read as energy.
    - Rotate every block a few degrees, alternating direction.
    - Build big to small, fast (400-450 ms), finish with a spin.
  dont:
    - No more than 3 block colors on one slide.
    - No body paragraphs. No sentence case.
    - No gradients, glows or soft shadows.
    - No italics. Anton has none, so Slides fakes a slant. Switch the color to accent instead.
---

# Kinetic poster

Loud, flat, fast. Rotated color blocks, heavy condensed caps, one hollow word. Every object slams in.

## Signature moves

- One word at 150 pt bleeding off the top edge.
- Blocks fly in from three sides, then a star spins.
- Outline text rendered as PNG (Slides has no text stroke), white on the blue block.

## Deck theme

Paste into `deck.json` → `"theme"`.

```json
{
  "colors": { "bg": "#FFD23F", "ink": "#141414", "accent": "#FF3D7F", "accent2": "#2B3BFF", "surface": "#FFFFFF", "muted": "#141414" },
  "fonts": { "display": "Anton", "body": "Instrument Sans", "label": "Instrument Sans" },
  "type": {
    "title":    { "font": "display", "size": 104, "color": "ink", "spacing": 0.82 },
    "hero":     { "font": "display", "size": 46, "color": "ink", "spacing": 0.85 },
    "headline": { "font": "display", "size": 44, "color": "ink", "spacing": 0.85 },
    "number":   { "font": "display", "color": "ink" },
    "quote":    { "font": "display", "size": 40, "color": "ink", "spacing": 0.9 },
    "kicker":   { "font": "body", "size": 11, "bold": true, "color": "ink" },
    "step":     { "font": "body", "size": 12, "bold": true, "color": "ink" },
    "body":     { "font": "body", "size": 12, "bold": true, "color": "ink", "spacing": 1.1 },
    "label":    { "font": "label", "size": 9, "bold": true, "color": "ink" }
  }
}
```
