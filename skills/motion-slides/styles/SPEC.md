# Style spec: `slide-style/v1`

A style is one file: `styles/<slug>/style.md`.

- **Front matter (YAML):** tokens. Claude copies them into a deck's `theme`. No script parses this file.
- **Body (Markdown):** what tokens cannot hold. Signature moves, slide recipes, motion, do and don't.

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
  # Keys per token: family, weight (100-900), italic (bool), case (as-is|upper|lower|title),
  # size_pt (number or [min, max]), line (multiplier), tracking_em (advisory), color (palette role).

layout:
  density: low                       # low <= 15 words per slide | medium <= 40 | high <= 80
  align: left                        # left | center | mixed
  archetypes: [title, statement, big-number, list-3, split, quote, closing]
  ornaments:                         # every ornament says how it is made
    - {name: registration marks, make: native}   # native = Slides shapes and lines
    - {name: halftone dot cloud, make: loop}     # loop = rendered GIF; png = rendered still

motion:
  energy: high                       # calm | medium | high
  transition: {kind: push, speed: fast}           # fade | push | flip | gallery | none
  builds:
    fx: [fly-left, fly-right, zoom]  # from: appear fade fly-left fly-right fly-top fly-bottom zoom spin
    duration_ms: 400                 # one value or [min, max]
    trigger: after                   # after | with | click. Slides has no delay control.
    order: display first, then ornament, then label   # prose
  loops:
    - name: ink-pass
      what: Two dot clouds slide in from opposite sides and overprint in the middle.
      seconds: 6
      fps: 15
      size_px: [720, 720]
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

## Native limits the spec must respect

| Want | Native Google Slides | Do instead |
|---|---|---|
| Font | Google Fonts only | Map with the table in [FROM-REFERENCE.md](FROM-REFERENCE.md) |
| Weight 800-900 | PPTX import carries bold on or off only | A single-weight heavy family (Archivo Black, Anton, Alfa Slab One, Dela Gothic One) |
| Letter spacing | Not settable by the Slides API. PPTX import unverified | Pick a font whose spacing fits. Keep `tracking_em` as advisory |
| Gradient, texture, glow, blur | Gradient survives PPTX import. Others do not | Pre-render a PNG, or move it into a loop |
| Easing curves, delays, motion paths, morph | None | Chain `after` builds. Put choreography in a loop |
| Builds | fade, fly (4 sides), zoom, spin, appear | Map wipes to fly or fade. Map scale-ins to zoom |
| Transitions | fade, push (slide), flip, gallery, cube, dissolve | Hard cut = none. Camera pan = push |
| Loops | GIF plays from slide open, not on its build | Time loops so frame 0 looks complete |

## Mapping to the deck builder

`deck.json` `theme` takes tokens straight from the front matter:

- `theme.colors` = `palette` (same role names).
- `theme.fonts` = `{display, body, label, emphasis}` → each role's `family`.
- `theme.type.<preset>` = `{font, size, color, italic, bold}` from each type role. `bold` = weight >= 600. `size` = the low end of `size_pt` unless the recipe says otherwise.
