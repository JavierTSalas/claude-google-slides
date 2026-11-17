---
spec: slide-style/v1
name: Kinetic poster
slug: kinetic-poster
summary: Loud, flat, fast. Rotated yellow, pink, blue and black blocks, heavy condensed caps, one hollow word. Everything slams in.
source:
  kind: video
  ref: Owner pick #8 from the discovery report (kinetic color-block motion graphics)
  took: palette, condensed caps, rotated blocks, outline type, build tempo
use_for: [openers, bold claims, section breaks, hackathons, launches]
avoid_for: [explanations, quotes over 8 words, dense data]

canvas: {width_in: 10, height_in: 5.625, margin_in: 0.3}

palette:
  bg: "#FFD23F"        # signal yellow
  ink: "#141414"       # black
  accent: "#FF3D7F"    # hot pink
  accent2: "#2B3BFF"   # ultramarine
  surface: "#FFFFFF"   # white, for outline type and tags
  muted: "#141414"

type:
  display:  {family: Anton, weight: 400, case: upper, size_pt: [44, 150], line: 0.82, color: ink}
  body:     {family: Instrument Sans, weight: 700, case: as-is, size_pt: [11, 12], line: 1.1, color: ink}
  label:    {family: Instrument Sans, weight: 700, case: upper, size_pt: [9, 11], color: ink}
  number:   {family: Anton, weight: 400, size_pt: [180, 210], line: 0.85, color: ink}

layout:
  density: low
  align: mixed
  archetypes: [poster, big-number, section, title]
  ornaments:
    - {name: rotated color blocks, make: native}
    - {name: outline word, make: png}
    - {name: star, make: native}
    - {name: marquee band, make: loop}

motion:
  energy: high
  transition: {kind: push, speed: med}
  builds:
    fx: [fly-top, fly-left, fly-right, zoom, spin, fade]
    duration_ms: [400, 450]
    trigger: after
    order: biggest word, then blocks from three sides, then small text, then the star spins
  loops:
    - {name: marquee, what: Heavy caps slide sideways in a band, seconds: 8, fps: 12, size_px: [1280, 128], colors: [ink, bg], placement: full-width band low on the slide, rotated -3 deg}

rules:
  do:
    - Let type bleed off the page edge. Cropped letters read as energy.
    - Rotate every block a few degrees, alternating direction.
    - Build big to small, fast, and finish with a spin.
  dont:
    - No more than 3 block colors on one slide.
    - No paragraphs. No sentence case in display type.
    - No gradients, glows or soft shadows.
    - No italics. Anton has none, so Slides fakes a slant. Switch the color to accent instead.
---

# Kinetic poster

## Signature

- One word at 150 pt bleeding off the top edge.
- Blocks fly in from three sides, then a star spins.
- One hollow (outline) word in white on the blue block. Rendered as PNG, since Slides has no text stroke.

## Slide recipes

From [reference/recipes.md](../../reference/recipes.md):

- `poster`: the core layout, as written. 8 words.
- `big-number`, `section`: Anton numerals. Use the accent color, not italic, for the turn.
- `title`: works, with tighter line spacing (0.82).
- Avoid `photo-split` and `quote` beyond 8 words.

## Motion

Fast. Push transition. Builds of 400 to 450 ms, all `after`, nine steps max, then a 900 ms star spin. Optional marquee band loop in black with yellow caps.

## Do / Don't

See `rules` above.

## Example prompt

> Make a 3-slide kinetic poster opener for a hackathon: "BUILD WEIRD THINGS", Nov 21-23, prizes.

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
