# Style spec: `slide-style/v1`

A style is one file: `styles/<slug>/style.md`.

- **Front matter (YAML):** tokens, for people and Claude. No script parses it.
- **Body (Markdown):** what tokens cannot hold. Signature moves, slide recipes, motion, do and don't.
- **`## Deck theme` (JSON block in the body):** the same tokens in `deck.json` form. `style_tour.py` and decks read this block.

Optional files in the same folder:

| File | What |
|---|---|
| `loops/<name>.html` | HyperFrames composition for a rendered loop. Colors come from palette roles. |
| `specimen.json` | A 4-slide deck in deck-spec format that shows the style. |
| `preview.jpg` | Contact sheet of the specimen. |
| `probe.md` | Reference-derived styles only. The measured numbers and where they came from. Never commit third-party frames. |

## Front matter

```yaml
---
spec: slide-style/v1
name: Riso Overprint                 # display name. Describe the look, never the source brand.
slug: riso-overprint                 # folder name
summary: Two riso inks on cream paper. Where they cross, they print a third color.
source:                              # omit for hand-made styles
  kind: video                        # video | deck | site | image | pptx | pdf
  ref: https://example.com/clip.mp4  # URL or a description. Never commit the media.
  took: palette, type classes, motion tempo, ornaments   # the look only
use_for: [workshops, launches, creative briefs]
avoid_for: [financial results, legal]

canvas: {width_in: 10, height_in: 5.625, margin_in: 0.5}

palette:                             # role: hex. Decks use roles, never raw hex.
  bg: "#F0EADE"                      # required. Slide background.
  ink: "#00207A"                     # required. Body text. Needs 4.5:1 on bg.
  accent: "#F2419B"                  # required. Display, highlights. Needs 3:1 on bg for display text.
  accent2: "#006EA7"                 # optional
  accent3: ...                       # optional
  surface: "#B6AD9C"                 # optional. Second background, cards, panels.
  muted: ...                         # optional. Captions, rules.
  # Extra roles are allowed. Name them by job (overprint, grid, wall).

type:                                # role: font token. Google Fonts family names only.
  display:  {family: Archivo Black, weight: 900, case: lower, size_pt: [96, 170], line: 0.85, color: accent}
  heading:  {...}                    # optional
  body:     {family: Archivo, weight: 400, size_pt: [12, 16], line: 1.2, color: ink}
  label:    {family: Space Mono, weight: 700, case: lower, size_pt: [9, 11], color: accent2}
  emphasis: {...}                    # optional. One-word italic or script.
  number:   {...}                    # optional. Big stat numerals.
  # Keys per token: family, weight (100-900), italic (bool), case (as-is|sentence|upper|lower|title),
  # size_pt (number or [min, max]), line (multiplier), tracking_em (advisory), color (palette role).

layout:
  density: low                       # low | medium | high
  max_words: 15                      # per slide. Low ~15, medium ~40, high ~80
  align: left                        # left | center | mixed
  archetypes: [title, statement, big-number, list-3, split, quote, closing]
  ornaments:                         # a string, or {name, make} to say how it is made
    - {name: registration marks, make: png}      # native = Slides shapes; png = rendered still
    - {name: halftone dot cloud, make: loop}     # loop = rendered GIF

motion:
  energy: high                       # calm | medium | high
  transition: {kind: push, speed: fast}           # fade | dissolve | push | flip | gallery | none
  builds:
    fx: [fly-left, fly-right, zoom]  # from: appear fade fly-left fly-right fly-top fly-bottom zoom spin
    duration_ms: 400                 # one value or [min, max]
    trigger: after                   # after | with | click. Slides has no delays: stagger comes from `after` chains
    order: display first, then ornament, then label   # prose
  loops:
    - name: ink-pass                 # loops/ink-pass.html, rendered to assets/ink-pass.gif
      what: Two dot clouds slide in from opposite sides and overprint in the middle.
      seconds: 6
      fps: 2
      size_px: [540, 540]            # width, height. A single number means square
      colors: [bg, accent, accent2, overprint]    # palette roles. Flat colors keep GIFs small.
      placement: right half, behind display type

rules:
  do:   [Two inks per slide at most, plus their overprint.]
  dont: [No gradients. No drop shadows. No third ink.]
---
```

## Body sections, in this order

1. **Signature.** The 2 or 3 moves a person would recognize in a thumbnail.
2. **Slide recipes.** One block per archetype: positions in inches on the 10 × 5.625 canvas, type roles, builds.
3. **Motion.** What enters, from where, in what order. What loops. Tempo in ms.
4. **Do / Don't.** Specific to this style. The global anti-slop rules still apply.
5. **Example prompt.** One line a user could paste.
6. **Deck theme.** A `json` code block under the heading `## Deck theme`. See below.

## Native limits the spec must respect

| Want | Native Google Slides | Do instead |
|---|---|---|
| Font | Google Fonts only | Map with the table in [FROM-REFERENCE.md](FROM-REFERENCE.md) |
| Weight 800-900 | PPTX import carries bold on or off only | A single-weight heavy family (Archivo Black, Anton, Alfa Slab One, Dela Gothic One) |
| Letter spacing | Not settable by the Slides API. PPTX import unverified | Pick a font whose spacing fits. Keep `tracking_em` as advisory |
| Gradient, texture, glow, blur | Gradient survives PPTX import. Others do not | Pre-render a PNG, or move it into a loop |
| Easing curves, delays, motion paths, morph | None | Chain `after` builds. Put choreography in a loop |
| Builds | appear, fade, fly (4 sides), zoom, spin | Map wipes to fly or fade. Map scale-ins to zoom |
| Transitions | fade, push (slide), flip, gallery, cube, dissolve | Hard cut = none. Camera pan = push |
| Loops | GIF plays from slide open, not on its build | Time loops so frame 0 looks complete |

## Deck theme block

The last section of the body. `deck.json` and `scripts/style_tour.py` read it as is. Derive it from the front matter:

- `colors` = `palette`, same role names.
- `fonts` = type role → `family`. At least `display`, `body`, `label`.
- `type` = named presets. Define all nine, because the shared recipes use them: `title`, `hero`, `headline`, `number`, `quote`, `kicker`, `step`, `body`, `label`. Each is `{font, size, color, italic, bold, spacing}`. `font` and `color` name a role. `bold` = weight >= 600.

```json
{
  "colors": { "bg": "#F0EADE", "ink": "#00207A", "accent": "#EE3D98", "accent2": "#006EA7" },
  "fonts":  { "display": "Archivo Black", "body": "Archivo", "label": "Space Mono" },
  "type": {
    "title":    { "font": "display", "size": 150, "color": "accent", "spacing": 0.82 },
    "hero":     { "font": "display", "size": 72, "color": "accent2", "spacing": 0.85 },
    "headline": { "font": "display", "size": 40, "color": "accent2", "spacing": 0.9 },
    "number":   { "font": "display", "color": "accent", "spacing": 0.8 },
    "quote":    { "font": "display", "size": 34, "color": "ink", "spacing": 0.95 },
    "kicker":   { "font": "label", "size": 11, "bold": true, "color": "accent" },
    "step":     { "font": "display", "size": 22, "color": "ink" },
    "body":     { "font": "body", "size": 14, "color": "ink", "spacing": 1.2 },
    "label":    { "font": "label", "size": 10, "bold": true, "color": "accent2" }
  }
}
```
