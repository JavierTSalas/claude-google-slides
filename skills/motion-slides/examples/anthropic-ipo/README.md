# Anthropic heads to Nasdaq (example)

An 8-slide news deck on Anthropic's IPO filing and recent news, as of Nov 17, 2026. Style: `cobalt-ledger`, with inverted cobalt slides for the beats. Sources are in each slide's speaker notes.

| Slide | Recipe | Loop |
|---|---|---|
| 1 | title | stair-scan (paper) |
| 2 | statement | none |
| 3 | big number with bars | none |
| 4 | big number, inverted | stair-scan (cobalt) |
| 5 | list 2 × 3 | none |
| 6 | statement, inverted | none |
| 7 | dated list | none |
| 8 | closing, inverted | ticker band (marquee in DM Mono) |

Rebuild from the skill folder:

```bash
cd skills/motion-slides
D=examples/anthropic-ipo
python3 scripts/render_loop.py styles/cobalt-ledger/loops/stair-scan.html $D/assets/stair-paper.gif --theme $D/deck.json --fps 4 --width 240 --colors 8
python3 scripts/render_loop.py styles/cobalt-ledger/loops/stair-scan.html $D/assets/stair-cobalt.gif --theme $D/deck.json \
  --var bg=cobalt --var ink=paper --var tint=ghost --fps 4 --width 240 --colors 16 --lossy 0
python3 scripts/render_loop.py motion/marquee.html $D/assets/ticker.gif --theme $D/deck.json \
  --var bg=cobalt --var ink=paper --var "display_font=DM Mono" --var "text=NASDAQ · ANT" --var "sep=✦" --fps 12 --width 1280
python3 scripts/build_deck.py $D/deck.json $D/out/anthropic-ipo.pptx --preview $D/out/preview
```

Result: about 0.9 MB, 3 loops. The inverted stair loop needs 16 colors, or its corner drifts one shade off the slide.
