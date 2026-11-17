# Decks that move (sample)

4-slide prototype. Native Google Slides objects plus rendered motion loops.

| Slide | Style | Native | Rendered |
|---|---|---|---|
| 1 Title | #3 editorial serif on green | Text, fade + fly builds | Rotating badge GIF |
| 2 Content | #7 photo-led editorial | Text, steps fly in, fade transition | Window-light arch GIF |
| 3 Poster | #8 kinetic color blocks | Rotated blocks, Anton type, fly/zoom/spin builds, push transition | Outline-text PNG |
| 4 Motion hero | Rendered full-bleed + native text | Text fades, fade transition | Orbits GIF |

## Rebuild

1. Motion: each `motion/<name>/index.html` is a HyperFrames composition. Add `assets/gsap.min.js` (npm `gsap`) and Google Fonts TTFs under `assets/fonts/`, then `npx hyperframes render --fps 25 -o <name>.mp4`.
2. GIF: ffmpeg two-pass palette (`palettegen` + `paletteuse`). Match the slide background color exactly.
3. Deck: `python3 build_deck.py out.pptx assets/`
4. Upload the .pptx to Drive. It converts to Google Slides.

Font families used: Instrument Serif, Instrument Sans, DM Mono, Anton (all Google Fonts).
