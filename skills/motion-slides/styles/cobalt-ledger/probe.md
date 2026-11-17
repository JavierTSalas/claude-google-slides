# Probe: cobalt-ledger

Reference: HTML deck "Cobalt Grid", `zarazhangrui/beautiful-html-templates` → `templates/cobalt-grid/template.html` (MIT). 8 screens.

Command: `python3 scripts/probe_reference.py template.html work/cobalt-probe --pages 10`

## Measured

| What | Value | Used as |
|---|---|---|
| CSS variables | --paper #F0EBDE, --paper-2 #E6E0CE, --ink #1F2BE0, --ink-soft #5560E5, --grid ink at 10% | `bg`, `surface`, `ink`, `muted`, `grid` |
| Text colors | 100% of characters in #1F2BE0 | One-ink rule |
| Screenshot palette | Paper 87%, ink 5%, rest flagged as tints of ink on paper | `tint` |
| Newsreader 400 | 83% of visual text area, up to 73 pt on a 10 in slide | `display`, `heading` |
| Newsreader 500 | 6%, 45 pt | `emphasis` |
| Hanken Grotesk 400 | 8%, 6-7 pt | `body`, raised to 10-12 pt for Slides |
| Hanken Grotesk 600 uppercase | tracking 0.16-0.22 em, 4.5-6 pt | `label`, raised to 7-8 pt |
| DM Mono 400 | tracking 0.04-0.08 em | `meta` |
| CSS motion | one `transition: opacity 280ms ease`, no keyframes | `energy: calm`, fade 300 ms |

## Judged

- Signature: one ink, huge serif against tiny spaced caps, stair-stepped bar column.
- Dropped: slide counters ("01 / 08"), issue numbers, vertical edge text. Page chrome under the anti-slop rules.
