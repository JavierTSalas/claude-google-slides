# Slide recipes

Proven layouts on the 10 × 5.625 in page. Copy a recipe's JSON into `slides`, then change words, ids and sizes.
Every recipe uses theme roles only (`bg`, `ink`, `accent`, `muted`, `surface`, `accent2`; fonts `display`, `body`, `label`),
so it works in any style. Type presets (`"as"`) are listed in [deck-spec.md](deck-spec.md#type-presets).

Rules for all recipes:

- One idea per slide. Respect each recipe's word budget.
- Fit text by arithmetic, not hope: line width (in) ≈ characters × size_pt / 72 × k, with k ≈ 0.48 for display serifs, 0.40 for condensed caps (Anton), 0.62 for mono, 0.52 for sans. Keep 0.1 in spare.
- Positions are tuned for the built-in fonts. A wide display face (Archivo Black, for example) needs smaller sizes in the style's `type` presets. Run `scripts/style_tour.py` on the style and fix every fit warning.
- Margins: 0.5–0.6 in. Bleed only on purpose (poster blocks, hero loops).
- Builds: total sequence under about 3 s. First group auto-plays on slide open. Use `click` only for a reveal the speaker controls.
- A GIF starts playing when the slide opens, not when it builds in. Do not give loops an entrance build.

---

## title

Huge display type, one small loop, one date. Nothing else. Use for: opener, closer. Budget: 4 words + date.
Motion: lines fade in one by one, last line flies up. Loop: `badge` (top right, 1.55 in).

```json
{
  "recipe": "title",
  "bg": "bg",
  "items": [
    { "id": "badge", "image": "badge.gif", "at": [7.9, 0.32, 1.55] },
    { "id": "l1", "text": "Decks", "as": "title", "at": [0.52, 0.95, 7.0, 1.35] },
    { "id": "l2", "text": "that", "as": "title", "at": [0.52, 2.12, 7.0, 1.35] },
    { "id": "l3", "text": "move.", "as": "title", "italic": true, "at": [0.52, 3.29, 7.0, 1.35] },
    { "id": "date", "text": "NOV 2026", "as": "label", "align": "right", "at": [6.4, 5.08, 3.0, 0.25] }
  ],
  "build": ["l1 fade 600", "l2 fade 600", "l3 fly-bottom 700"]
}
```

Variations: two lines instead of three (y 1.5 and 2.67). No loop: shift nothing, leave the space empty.

## photo-split

Image or loop left, text column right. Use for: explaining one thing with a picture. Budget: 40 words.
Motion: fade transition in. Headline, then body, then the three steps rise in turn. Loop: `window-light` (arch, 5.0 in tall), or a still photo.

```json
{
  "recipe": "photo-split",
  "bg": "bg",
  "transition": "fade",
  "items": [
    { "id": "pic", "image": "light.gif", "at": [0.45, 0.31, null, 5.0] },
    { "id": "rule", "shape": "rect", "fill": "accent", "at": [4.9, 0.78, 0.55, 0.03] },
    { "id": "kicker", "text": "HOW IT WORKS", "as": "kicker", "at": [4.9, 0.9, 4.4, 0.3] },
    { "id": "h", "as": "headline", "at": [4.9, 1.2, 4.6, 1.4],
      "lines": ["Native slides.", { "text": "Rendered light.", "italic": true }] },
    { "id": "b", "as": "body", "at": [4.9, 2.65, 4.3, 0.9],
      "text": "Layout and text are real Google Slides objects. Motion is rendered to a loop." },
    { "id": "s1", "at": [4.9, 3.75, 1.45, 1.2], "spacing": 1.05, "lines": [
      { "text": "01", "as": "number", "size": 30 }, { "text": "Structure", "as": "step" }, { "text": "Slides API", "as": "label", "color": "muted" } ] },
    { "id": "s2", "at": [6.45, 3.75, 1.45, 1.2], "spacing": 1.05, "lines": [
      { "text": "02", "as": "number", "size": 30 }, { "text": "Motion", "as": "step" }, { "text": "HTML → GIF", "as": "label", "color": "muted" } ] },
    { "id": "s3", "at": [8.0, 3.75, 1.45, 1.2], "spacing": 1.05, "lines": [
      { "text": "03", "as": "number", "size": 30 }, { "text": "Builds", "as": "step" }, { "text": "Fade + fly", "as": "label", "color": "muted" } ] }
  ],
  "build": ["h fade 600", "b fade 500", "s1 fly-bottom 450", "s2 fly-bottom 450", "s3 fly-bottom 450"]
}
```

Variations: drop the steps and give the body 2 lines. Photo on the right: mirror x (`pic` at 5.4, text at 0.6).
An arch-shaped still photo: crop it to an arch PNG before placing (the Slides API cannot mask images).

## poster

Rotated color blocks, giant condensed caps, one outline word, a spinning star. Use for: openers, section breaks, one bold claim.
Budget: 8 words. Motion: push transition, then nine fast builds (fly, zoom, spin). Best in `kinetic-poster`.

```json
{
  "recipe": "poster",
  "bg": "bg",
  "transition": "push",
  "items": [
    { "id": "blockA", "shape": "rect", "fill": "accent", "rotate": -5, "at": [-0.45, 1.75, 6.4, 4.6] },
    { "id": "blockB", "shape": "rect", "fill": "accent2", "rotate": 6, "at": [6.05, -0.5, 4.5, 2.95] },
    { "id": "blockC", "shape": "rect", "fill": "ink", "rotate": -4, "at": [6.75, 3.3, 3.9, 2.7] },
    { "id": "big", "text": "DECKS", "as": "title", "size": 150, "color": "ink", "spacing": 0.85, "at": [0.3, -0.42, 6.2, 2.3] },
    { "id": "pair", "lines": ["THAT", "MOVE"], "as": "title", "color": "bg", "spacing": 0.82, "rotate": -5, "at": [0.55, 2.2, 5.4, 3.0] },
    { "id": "hollow", "outline": ["NO", "PLUG-INS"], "font": "display", "size": 48, "color": "surface",
      "spacing": 0.9, "stroke": 1.4, "rotate": 6, "at": [6.6, 0.18, 2.25] },
    { "id": "tag", "text": "LIVE IN GOOGLE SLIDES", "as": "kicker", "color": "surface", "rotate": 6, "at": [6.62, 1.8, 3.2, 0.3] },
    { "id": "claim", "lines": ["100%", "NATIVE"], "as": "title", "size": 46, "color": "accent", "spacing": 0.85,
      "rotate": -4, "at": [7.15, 3.72, 3.2, 1.6] },
    { "id": "star", "shape": "star", "fill": "ink", "rotate": 12, "at": [5.35, 1.55, 1.0, 1.0] }
  ],
  "build": ["big fly-top 450", "blockA fly-left 450", "pair zoom 450", "blockB fly-top 400",
            "hollow fade 400", "tag fade 400 with", "blockC fly-right 400", "claim zoom 400", "star spin 900"]
}
```

Variations: replace `blockC` and `claim` with a `marquee` loop band (`image`, at `[-0.3, 4.55, 10.6]`, `rotate` -3).
Keep blocks to 3 colors. Never more than one outline word.

## motion-hero

A full-bleed loop with two lines of native type over the quiet side. Use for: a turn in the story, a closing thought.
Budget: 6 words + label. Motion: fade transition, lines fade in. Loop: `orbits` (offset right so the left stays calm).

```json
{
  "recipe": "motion-hero",
  "bg": "bg",
  "transition": "fade",
  "items": [
    { "id": "loop", "image": "orbits.gif", "at": [0.7, 0, 10, 5.625] },
    { "id": "k", "text": "RENDERED MOTION", "as": "label", "size": 10, "at": [0.6, 0.6, 4.0, 0.3] },
    { "id": "h1", "text": "Rendered once.", "as": "hero", "at": [0.55, 1.45, 5.0, 0.95] },
    { "id": "h2", "text": "Plays forever.", "as": "hero", "color": "ink", "italic": true, "at": [0.55, 2.3, 5.0, 0.95] }
  ],
  "build": ["h1 fade 700", "h2 fade 700"]
}
```

## big-number

One number carries the slide. Use for: a result, a metric, a date. Budget: 1 number + 12 words.
Motion: the number zooms in, then the line fades.

```json
{
  "recipe": "big-number",
  "bg": "bg",
  "transition": "fade",
  "items": [
    { "id": "k", "text": "SIZE PER LOOP", "as": "label", "at": [0.6, 0.45, 4.0, 0.3] },
    { "id": "n", "text": "0.5", "as": "number", "size": 210, "spacing": 0.85, "at": [0.45, 1.0, 6.2, 3.1] },
    { "id": "u", "text": "MB", "as": "headline", "color": "accent", "at": [5.0, 1.65, 2.0, 0.9] },
    { "id": "line", "as": "body", "size": 16, "color": "ink", "at": [0.6, 4.25, 5.6, 0.8],
      "text": "A flat loop after compression. Fifty fit in one deck." }
  ],
  "build": ["n zoom 500", "u fade 400 with", "line fade 500"]
}
```

Fit: at 210 pt a display numeral is about 1.4 in wide per digit. Keep to 4 characters.

## quote

A pull quote in italic display type, one attribution. Use for: customer voice, a principle. Budget: 20 words.
Motion: fade transition, quote fades, attribution rises.

```json
{
  "recipe": "quote",
  "bg": "bg",
  "transition": "fade",
  "items": [
    { "id": "mark", "text": "“", "as": "title", "size": 140, "color": "accent", "at": [0.5, 0.35, 1.2, 1.6] },
    { "id": "q", "as": "quote", "at": [1.2, 1.25, 7.6, 2.4],
      "text": "I didn't think you could do something like this in Google Slides." },
    { "id": "rule", "shape": "rect", "fill": "accent", "at": [1.25, 4.05, 0.55, 0.03] },
    { "id": "who", "text": "PROJECT OWNER · FIRST REVIEW", "as": "label", "at": [1.25, 4.2, 6.0, 0.3] }
  ],
  "build": ["q fade 800", "rule fly-left 300", "who fly-bottom 400 with"]
}
```

## section

A divider: big index, short title. Use for: chapter breaks in decks over 8 slides. Budget: 4 words.
Motion: gallery transition, index flies in from the left, title fades.

```json
{
  "recipe": "section",
  "bg": "bg",
  "transition": "gallery",
  "items": [
    { "id": "idx", "text": "02", "as": "number", "size": 180, "spacing": 0.85, "at": [0.5, 0.7, 4.5, 2.8] },
    { "id": "t", "lines": ["How it", { "text": "works", "italic": true }], "as": "headline", "size": 64, "color": "ink",
      "spacing": 0.9, "at": [4.6, 1.35, 5.0, 2.4] },
    { "id": "k", "text": "SECTION TWO", "as": "label", "at": [0.6, 5.0, 4.0, 0.25] }
  ],
  "build": ["idx fly-left 500", "t fade 600"]
}
```
