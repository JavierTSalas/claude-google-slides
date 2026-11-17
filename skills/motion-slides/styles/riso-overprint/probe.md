# Probe: riso-overprint

Reference: onetake case film "overlap" (15 s, 1920 × 1080, 30 fps), `feitangyuan/onetake` → `cases/overlap-15s/overlap.mp4`. License PolyForm Noncommercial. Only measurements are kept here. No frames are committed.

Command: `python3 scripts/probe_reference.py overlap.mp4 work/overlap-probe`

## Measured

| What | Value | Used as |
|---|---|---|
| Cuts | 0 (one continuous camera move) | `transition: push`, fast |
| Time in motion | 48% | `energy: high` (borderline medium) |
| Move length | median 300 ms, p75 700 ms | `builds.duration_ms: 400` |
| Hold length | median 350 ms | `trigger: after`, short chains. Loop steps every 500 ms |
| Paper | #F0ECE0 (area), #F0EADE (pixel median) | `bg` |
| Pink ink | #F2419B (pixel median, masked) | `accent`, darkened to #EE3D98 for 3:1 |
| Blue ink | #006EA7 (pixel median, masked) | `accent2` |
| Overprint | #00207A (pixel median, masked) | `ink`, `overprint` |
| Wall around the poster | #B6AD9C, 39% of area | Dropped. Camera context, not style |
| #7F639E | flagged blend of blue and pink | Dropped. Halftone average, not an ink |

## Judged (by eye from the contact sheet)

- Display: heavy grotesque, lowercase, tight. Mapped to Archivo Black (single-weight 900 on Google Fonts).
- Labels: bold monospace, lowercase. Mapped to Space Mono Bold.
- Signature: words enter from opposite sides and meet. Halftone dot clouds. Registration marks.
- Dropped: cursors and "you / them" tags. They carry the film's story about two people, not its look.
