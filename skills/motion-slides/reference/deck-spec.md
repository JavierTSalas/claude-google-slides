# Deck spec (`deck.json`)

`scripts/build_deck.py deck.json out.pptx` turns this file into a `.pptx` that Google Drive converts to native Google Slides.
Page: 10 × 5.625 in (Google Slides 16:9). All positions and sizes are inches. Font sizes are points.

```json
{
  "title": "Q3 kickoff",
  "assets": "assets",
  "max_words": 40,
  "theme": { "colors": {}, "fonts": {}, "type": {} },
  "slides": [ { "bg": "bg", "transition": "fade", "items": [], "build": [], "notes": "" } ]
}
```

| Key | Meaning |
|---|---|
| `assets` | Folder for `image` paths, relative to deck.json. Default: the deck.json folder |
| `max_words` | Per-slide word budget. Build warns above it. Default 40. A slide can set its own |
| `transition` | Deck default transition. A slide's own `transition` wins |
| `theme` | Tokens. Copy the `## Deck theme` block from a style file |

## Theme

```json
"theme": {
  "colors": { "bg": "#2F4B2B", "ink": "#EBA6BD", "accent": "#F1EBE1", "muted": "#C9C2B0" },
  "fonts":  { "display": "Instrument Serif", "body": "Instrument Sans", "label": "DM Mono" },
  "type":   { "title": { "font": "display", "size": 104, "color": "ink", "spacing": 0.9 } }
}
```

- `colors`: any names. Values are hex or another color name. Standard roles: `bg`, `ink`, `accent`, `muted`, `surface`, `accent2`, `accent3`. Recipes use these.
- `fonts`: role → Google Fonts family. Standard roles: `display`, `body`, `label`. Anything not on Google Fonts falls back to Arial in Slides.
- `type`: named presets. An item picks one with `"as"`. Item keys override the preset.

### Type presets

Recipes expect these names. Every built-in style defines all of them.

| Preset | Role |
|---|---|
| `title` | Huge display line (opener, poster) |
| `hero` | Large display line over a loop |
| `headline` | Slide headline |
| `number` | Big numerals (size set by the recipe) |
| `quote` | Pull quote |
| `kicker` | Small label above a headline |
| `step` | Bold short label (numbered steps) |
| `body` | Paragraph text |
| `label` | Meta text: dates, captions, sources |

## Slides

| Key | Meaning |
|---|---|
| `bg` | Color name or hex, or `{"image": "file.png"}` for a full-bleed picture. Default `bg` |
| `transition` | `fade` · `push` · `flip` · `gallery` · `none`, or `{"type": "fade", "speed": "slow"}` (`slow`, `med`, `fast`) |
| `items` | Objects, back to front |
| `build` | Animation sequence (below) |
| `notes` | Speaker notes |
| `recipe` | Label only. Not read by the builder |
| `max_words` | Overrides the deck budget |

## Items

Every item has `at: [x, y, w, h]` and an optional `id` (needed for builds) and `rotate` (degrees, clockwise).

**Text**: `text` (string, `\n` splits paragraphs) or `lines` (list).
A line is a string, an object `{"text": "...", ...run keys}`, or a list of those for mixed styling in one line.

```json
{ "id": "h", "as": "headline", "at": [4.9, 1.2, 4.6, 1.4],
  "lines": ["Native slides.", { "text": "Rendered light.", "italic": true }] }
```

Keys: `as`, `font`, `size`, `color`, `bold`, `italic`, `underline`, `align` (`left`, `center`, `right`, `justify`), `spacing` (line spacing multiple), `anchor` (`top`, `middle`, `bottom`).
Text boxes have zero padding and no autofit (Slides cannot write autofit). The builder warns when text wraps past its box.

**Image**: `image` (path under `assets`). PNG, JPEG or GIF. Animated GIFs keep every frame.
`at` may give only width (`[x, y, w]`) or only height (`[x, y, null, h]`) to keep the aspect ratio. Optional `crop: [l, t, r, b]` as fractions.

**Shape**: `shape` = `rect` · `round-rect` · `ellipse` · `circle` · `arch` · `triangle` · `star` · `star-8` · `star-12` · `diamond` · `chevron` · `arrow` · `half-frame`, or any python-pptx `MSO_SHAPE` name.
Keys: `fill` (color or `none`), `line` (color), `line_width` (pt), `adj` (shape adjustments). Use a thin `rect` as a rule.

**Outline text**: `outline` (string or list of lines). Hollow stroked type. Slides has no text stroke, so the builder renders a transparent PNG from the Google Font.
Keys: `font`, `size`, `color`, `stroke` (pt, default 1.6), `spacing`, `align`, `bold`, `italic`. `at` takes `[x, y]` or `[x, y, w]` (fit to width).

## Builds

A list of strings `"id effect [ms] [mode]"` (or lists with the same parts), in play order.

| Effect | Meaning | Default ms |
|---|---|---|
| `fade` | Fade in | 600 |
| `fly-left` · `fly-right` · `fly-top` · `fly-bottom` | Enter from that side (`rise` = `fly-bottom`, `drop` = `fly-top`) | 600 |
| `zoom` | Grow in from the center | 450 |
| `spin` | One full turn (emphasis; object stays visible) | 900 |

| Mode | Meaning |
|---|---|
| `after` (default) | Starts when the previous step ends |
| `with` | Starts with the previous step |
| `click` | Waits for a click, then starts a new group |

The first group starts by itself when the slide opens. All of these survive Drive's conversion (tested).
Not available in Google Slides: morph, motion paths, wipe (becomes fade), emphasis other than spin, delays.

## Checks the builder runs

- Unknown ids in `build`, unknown colors, missing images: error.
- Word count over budget, text that wraps past its box, a word wider than its box, more than 3 font families, more than 10 build steps: warning.
- Prints deck size and GIF totals. Budget: about 0.5 MB per flat loop, 1.6 MB per photo-like loop.

`--preview DIR` renders a static contact sheet with LibreOffice (first GIF frame, final build state).
The fit check and outline text download Google Fonts once into `~/.cache/motion-slides/fonts`. `--no-fit` skips the check offline.
