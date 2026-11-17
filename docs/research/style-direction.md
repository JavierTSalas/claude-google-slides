# Style Direction

Source: owner's picks from the discovery screenshots (2026-11-17).

| Role | Reference | Traits to carry over |
|---|---|---|
| Title slide | [#2 Soft editorial](img/02-beautiful-html-templates-soft-editorial.jpg), [#3 Editorial forest](img/03-beautiful-html-templates-editorial-forest.jpg) | Huge display serif. Two-color palettes (deep green + pink, cream + pastels). Small mono caps labels. Wide margins. No chrome. |
| Content slide | [#7 slides_maker editorial](img/07-slides-maker-editorial-pptx.jpg) | Photo-led split layouts. Warm photography. Serif headline, small sans body. Pull quote. Single big number. Arched image mask. |
| Supported alt style | [#8 bang-motion kinetic colorblock](img/08-bang-motion-kinetic-colorblock.jpg) | Rotated color blocks. Heavy condensed caps. Bright primaries (yellow, pink, blue, black). Outline type. Poster energy. |

## Native Slides feasibility

- Display serifs, mono labels, condensed caps: Google Fonts (e.g. Fraunces, Instrument Serif, DM Mono, Anton). ✅
- Rounded cards, rotated blocks, split layouts, image crops: Slides API shapes, transforms, images. ✅
- Arched image mask: crop-to-shape is UI-only. Pre-mask the image (PNG) or use a template placeholder. ⚠️
- Outline (stroked) text: no native text stroke. Render as image or GIF. ⚠️

## Motion mapping

- Title (#2, #3): quiet. Native Fade / Fly-in builds. Optional slow GIF texture.
- Content (#7): slow push-in on photos via Drive MP4 or native Zoom. Fade builds for text.
- Poster (#8): kinetic. Blocks slam in and rotate. Render as GIF/MP4 with HyperFrames; keep headline text native on top where possible.
