# Decks that move (sample)

The 4-slide sample deck, as a `deck.json`. It mixes all three built-in styles on purpose, so the builder warns about 4 font families.

| Slide | Recipe | Style | Loop |
|---|---|---|---|
| 1 | title | editorial-forest | badge |
| 2 | photo-split | warm-editorial | window-light |
| 3 | poster | kinetic-poster | none (all native) |
| 4 | motion-hero | editorial-forest | orbits |

Rebuild from the skill folder:

```bash
cd skills/motion-slides
D=examples/decks-that-move
python3 scripts/render_loop.py motion/badge.html        $D/assets/badge.gif  --theme $D/deck.json --fps 12 --width 360
python3 scripts/render_loop.py motion/window-light.html $D/assets/light.gif  --theme $D/deck.json --var bg=paper --photo
python3 scripts/render_loop.py motion/orbits.html       $D/assets/orbits.gif --theme $D/deck.json --var accent=cream --fps 15 --width 1024
python3 scripts/build_deck.py $D/deck.json $D/out/decks-that-move.pptx --preview $D/out/preview
```

Result: about 3 MB, 3 loops. Upload the .pptx to Google Drive and open it with Google Slides.
