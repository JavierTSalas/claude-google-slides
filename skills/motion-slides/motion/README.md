# Motion loops

Each template is a [HyperFrames](https://github.com/heygen-com/hyperframes) composition: HTML + CSS + a paused GSAP timeline.
`scripts/render_loop.py` renders it to a seamless, compressed GIF. Variables (colors, fonts, text) come from `deck.json` → `theme` and `--var`.

| Template | What moves | Variables | Render | Typical size |
|---|---|---|---|---|
| `badge.html` | Text ring turns around a numeral | `bg`, `ink`, `label_font`, `display_font`, `ring_text`, `core_text` | `--fps 12 --width 360` | 0.9 MB |
| `orbits.html` | Planets orbit still rings | `bg`, `ink`, `accent` | `--fps 15 --width 1024` | 0.5 MB |
| `window-light.html` | Blind shadows drift over an arched warm "photo" | `bg`, `light`, `mid`, `deep`, `shadow` | `--photo` | 1.6 MB |
| `marquee.html` | A band of heavy caps slides sideways | `bg`, `ink`, `display_font`, `text`, `sep` | `--fps 12 --width 1280` | 1.1 MB |

```bash
# colors and fonts from the deck theme; text from --var; a --var color may name a theme color
python3 scripts/render_loop.py motion/badge.html assets/badge.gif --theme deck.json \
  --var ring_text="Q3 KICKOFF ✦ PLATFORM TEAM ✦ 2026 ✦" --var core_text=Q3 --fps 12 --width 360
python3 scripts/render_loop.py motion/marquee.html assets/marquee.gif --theme deck.json \
  --var bg=ink --var ink=bg --var text="SHIP IT" --fps 12 --width 1280
```

Theme mapping: a `color` variable takes the theme color of the same name. A `<role>_font` variable takes `theme.fonts.<role>`.

## Size budget

From `docs/research/gif-compression.md` (50 loops ≈ 40 MB per deck):

- Flat graphics: 10–15 fps, about 0.4–0.9 MB. Photo-like: `--photo` (8 fps, ≤ 400 px, 48 colors), about 1.6 MB.
- The moving area drives size. Keep still parts still. Better still, draw them as native shapes on the slide.
- Size the GIF to its on-slide box at a 1280 px wide slide (1 in ≈ 128 px).
- `bg` must equal the slide color behind the GIF. GIF alpha is 1-bit, so a matched ground is the clean edge.

## Write a new loop

Copy the closest template. Keep these rules:

1. Root: `<div id="root" data-composition-id="main" data-start="0" data-duration="N" data-width="W" data-height="H">`.
   Each moving element: `class="clip" data-start="0" data-duration="N" data-track-index="k"`.
2. Declare variables on `<html data-composition-variables='[{"id", "type", "label", "default"}]'>`.
   Types: `color`, `string`, `number`. Name colors after theme roles (`bg`, `ink`, `accent`...) and fonts `<role>_font`.
3. In the script: read `window.__hyperframes.getVariables()`, set them as CSS custom properties, fill text.
   Build `gsap.timeline({ paused: true })` and register it on `window.__timelines["main"]`.
4. Seamless loop: the last frame must lead into the first. Rotate by whole turns. Translate by exactly one pattern period.
   Sway as 0 → +a → 0 → −a → 0 with sine eases. Use `ease: "none"` for constant motion.
5. Load GSAP from `https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js`. The render script swaps in a local copy.
6. Flat color beats gradients: GIFs have 256 colors and gradients band. Soft light is fine at `--photo` settings.
7. Taste: one motion idea per loop, slow and constant. No bounce, no glow, no particles.

Check a loop: open the GIF, then view its first and last frames side by side. They should differ by one step.
