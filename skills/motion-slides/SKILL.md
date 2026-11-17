---
name: motion-slides
description: Build designed, motion-rich Google Slides decks (native builds and transitions plus looping GIF motion) as a .pptx that Google Drive converts to native Slides. Use when asked for a deck, slides or a presentation for Google Slides that should look designed or move, or for a slide style taken from a reference.
---

# Motion slides

Output: a native Google Slides deck. Text and shapes stay editable. Motion comes from three native layers:

1. **Builds**: fade, fly, zoom, spin. Auto-play on slide open or on click.
2. **Transitions**: fade, push, flip, gallery.
3. **Loops**: animated GIFs rendered from HTML (HyperFrames). They play forever in Slides.

Path: `deck.json` → `scripts/build_deck.py` → `.pptx` → Google Drive converts it to Slides.
The Slides API cannot set animations or transitions. A `.pptx` import can, so the skill writes `.pptx`.

`<skill>` below means the folder that holds this file.

## Setup (once)

| Need | For | Install |
|---|---|---|
| Python 3.9+ and `python-pptx` | Every deck | `pip install python-pptx` |
| Node 22+ and `ffmpeg` | Motion loops only | `npx` fetches HyperFrames and gifsicle on first use |
| LibreOffice and poppler | `--preview` contact sheet only | `soffice`, `pdftoppm` |

No Google Cloud project and no API keys. Fonts download from Google Fonts on first use.

## Workflow

### 1. Brief

Get: audience, goal, slide count, content, style. Infer what you can. Ask one short question only when the content is missing.
Default style: `editorial-forest` for beats, `warm-editorial` for explanation (one theme, see the pairing note in each file).

### 2. Style

Read the whole style file before you write a slide.

| Style | Look | Use for |
|---|---|---|
| [`editorial-forest`](styles/editorial-forest/style.md) | Huge pink serif on deep green, mono labels, one small loop | Titles, sections, hero moments |
| [`warm-editorial`](styles/warm-editorial/style.md) | Cream paper, arched photo, terracotta details | Content, explanation, quotes |
| [`kinetic-poster`](styles/kinetic-poster/style.md) | Rotated yellow/pink/blue/black blocks, Anton caps | Openers, bold claims, breaks |

- **User style**: they point at a `style.md`. Format: [styles/SPEC.md](styles/SPEC.md).
- **From a reference** (image, video, deck, website): follow [styles/FROM-REFERENCE.md](styles/FROM-REFERENCE.md) first. It ends with a new `style.md`.
- Check a new or edited style: `python3 <skill>/scripts/style_tour.py <slug or style.md> out/tour` builds every recipe in it.

Copy the style's `## Deck theme` JSON into `deck.json` → `theme`. Two styles in one deck: merge their colors under distinct names.

### 3. Outline

- One idea per slide. Pick a recipe for each from [reference/recipes.md](reference/recipes.md): `title`, `photo-split`, `poster`, `motion-hero`, `big-number`, `quote`, `section`.
- Do not repeat a recipe on adjacent slides.
- Write to each recipe's word budget. Cut, do not shrink type.
- A title slide holds the title, at most one loop, and a date. Nothing else.

### 4. Motion plan

- Per slide: one build sequence under about 3 s, the style's transition, at most one loop.
- Choose a loop from [motion/README.md](motion/README.md) or write a new HyperFrames template there. New loops make a deck unique. Reuse is fine within a deck.
- Builds that play by themselves feel cinematic. Use `click` only for reveals the speaker controls.

### 5. Render loops

```bash
python3 <skill>/scripts/render_loop.py <skill>/motion/badge.html assets/badge.gif --theme deck.json --fps 12 --width 360
```

- The loop's `bg` must equal the color behind it on the slide. The script prints the corner pixel. Match it.
- Budget: about 0.5 MB per flat loop, 1.6 MB per photo-like loop (`--photo`). 50 loops fit in one deck.
- Size the GIF to its box on a 1280 px wide slide. Keep the moving area small.

### 6. Build and review

```bash
python3 <skill>/scripts/build_deck.py deck.json out/deck.pptx --preview out/preview
```

Fix every `warn:` line. Open `out/preview/contact-sheet.png` and check it against the taste rules below. Rebuild until clean.
The preview is static: first GIF frame, final build state. LibreOffice fakes missing italics; Slides does too.

### 7. Deliver

- **Deck under 3 MB and a Google Drive connector is available**: upload with `create_file`, `contentMimeType` `application/vnd.openxmlformats-officedocument.presentationml.presentation`, conversion on (the default). The result is a Google Slides file. Share its link.
- **Otherwise**: hand over the `.pptx`. The user drags it into Google Drive, opens it with Google Slides, then **File → Save as Google Slides**. Drive converts decks up to 100 MB.
- Never link images by URL inside the `.pptx`. Google's converter does not fetch them.

### 8. Polish (optional)

Only the Slides UI can do some things: Drive video autoplay, image masks, replacing a GIF with a Drive MP4.
If Claude in Chrome is available, do them there after import.

## Taste rules

- One idea per slide. Type can be the picture.
- No page chrome: no "02 / 05" counters, corner brackets, logos on every slide, progress bars.
- No "headline left, card grid right" on every slide. Vary recipes.
- No glow, lens flare, purple gradients, glassmorphism, soft drop shadows, bouncy motion.
- Not every object fades. Mix fly, zoom and cuts. Big things first, details last.
- Fonts come from the style, at most 3 families per deck. Google Fonts only.
- Loop grounds match the slide exactly. A visible GIF rectangle is a bug.
- Words: title 4, poster 8, hero 6, content 40. The builder warns above budget.
- Before delivery, look at the contact sheet as a stranger would. Remove anything that does not earn its place.

## What Google Slides can and cannot do

| Works (tested through Drive import) | Does not |
|---|---|
| Fade, fly (4 sides), zoom, spin builds; auto or on click | Morph, motion paths, wipe (becomes fade), delays |
| Fade, push, flip, gallery transitions | Glow, soft edge, 3D, text stroke (use `outline` items) |
| Animated GIF, all frames, loops forever | Letter spacing, text autofit |
| Rotation, solid fills, any Google Font | Embedded video or audio inside the `.pptx` |

A GIF starts when the slide opens, not when it builds in. Never give a loop an entrance build.
Details and the full feature map: `docs/research/` in the source repository.

## Files

```
SKILL.md                 this workflow
reference/deck-spec.md   deck.json format: theme, items, builds, transitions
reference/recipes.md     7 slide layouts as JSON
styles/<slug>/style.md   built-in and user styles (slide-style/v1)
styles/SPEC.md           style format; styles/FROM-REFERENCE.md builds one from a reference
motion/*.html            loop templates (HyperFrames) + README
scripts/build_deck.py    deck.json -> .pptx (+ --preview)
scripts/render_loop.py   template -> compressed GIF
scripts/style_tour.py    every recipe in one style, for checking
examples/                sample deck + example prompts
```
