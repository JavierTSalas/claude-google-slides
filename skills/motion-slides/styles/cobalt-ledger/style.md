---
spec: slide-style/v1
name: Cobalt Ledger
slug: cobalt-ledger
summary: One electric-cobalt ink on warm paper. Book serif headlines, tiny spaced labels, hairline rules and a stair-stepped bar column.
source:
  kind: deck
  ref: "HTML deck 'Cobalt Grid' (zarazhangrui/beautiful-html-templates, templates/cobalt-grid, MIT)"
  took: palette and CSS variables, font families and roles, rules and bar ornament, 280 ms fade tempo
use_for: [annual reports, research findings, newsletters, editorial reviews, data summaries]
avoid_for: [loud launches, kids, anything that needs more than one color]

canvas: {width_in: 10, height_in: 5.625, margin_in: 0.45}

palette:
  bg: "#F0EBDE"        # paper (CSS --paper)
  ink: "#1F2BE0"       # cobalt (CSS --ink). All text. 7.1:1 on bg
  accent: "#1F2BE0"    # the same ink. One-color style
  surface: "#E6E0CE"   # second paper (CSS --paper-2). Panels
  muted: "#5560E5"     # soft ink (CSS --ink-soft). Secondary text, 4.2:1. Large text only
  tint: "#B4B6E6"      # ink at ~35% on paper. Empty bars, ghost marks
  grid: "#DBD8DE"      # ink at 10% on paper (CSS --grid). Chart gridlines
  accent2: "#1F2BE0"   # one ink: every accent role is cobalt

type:
  display:  {family: Newsreader, weight: 400, case: as-is, size_pt: [60, 76], line: 0.95, color: ink}
  heading:  {family: Newsreader, weight: 400, case: as-is, size_pt: [26, 36], line: 1.05, color: ink}
  emphasis: {family: Newsreader, weight: 700, italic: false, size_pt: [26, 46], color: ink}   # reference uses 500; PPTX carries bold only, so 700
  body:     {family: Hanken Grotesk, weight: 400, size_pt: [10, 12], line: 1.3, color: ink}
  label:    {family: Hanken Grotesk, weight: 600, case: upper, size_pt: [7, 8], tracking_em: 0.18, color: ink}
  meta:     {family: DM Mono, weight: 400, case: lower, size_pt: [7, 8], tracking_em: 0.05, color: ink}
  number:   {family: Newsreader, weight: 400, size_pt: [72, 96], line: 0.9, color: ink}

layout:
  density: medium
  max_words: 40
  align: left
  archetypes: [title, statement, big-number-with-bars, list-2x3, quote, closing]
  ornaments:
    - {name: hairline rule across the top margin, make: native}
    - {name: stair-stepped bar column, make: loop}
    - {name: chart gridlines in grid color, make: native}
    - {name: stair bar chart, make: native}

motion:
  energy: calm
  transition: {kind: fade, speed: fast}
  builds:
    fx: [fade, fly-bottom]
    duration_ms: 300
    trigger: after
    order: headline, then rule-separated details, then the ornament is already moving
  loops:
    - name: stair-scan
      what: A column of thin vertical bars with a stair-stepped edge. The steps scroll up one row every 0.25 s. The last step stays as a pale ghost.
      seconds: 6
      fps: 4
      size_px: [240, 480]
      colors: [bg, ink, tint]
      placement: right third, full height between the rules

rules:
  do:
    - One ink. Hierarchy comes from size and weight, never from a second color.
    - Huge serif against tiny spaced caps. Keep that scale jump.
    - A hairline rule at the top of every slide, inside the margin.
    - Charts as native cobalt rectangles on tint, stepped like the ornament.
  dont:
    - No slide counters, issue numbers or vertical edge text. The reference had them. They are page chrome.
    - No italics for emphasis. Set the closing phrase in bold (the reference used 500).
    - No rounded corners, shadows or fills other than surface.
---

# Cobalt Ledger

## Signature

1. **One ink.** Every mark is cobalt on warm paper. Tints of the same ink for empty states.
2. **Scale jump.** A 70 pt book serif next to 7 pt spaced caps.
3. **Stair-stepped bars.** A column of thin vertical lines with a pixel-step edge. It also drives the charts.

## Slide recipes

Canvas 10 × 5.625 in. Margin 0.45 in. Hairline rule: `ink`, 0.75 pt, from x 0.45 to 9.55 at y 0.3.

**Title.** `display` two lines, left 0.45, top 1.0, width 5.5. `label` line above a `heading` subtitle at y 3.55 and 3.75. Loop `stair-scan` at x 7.1, y 0.45, 1.9 × 3.8 in. Two `label` + `body` credit pairs at y 4.75. Builds: display fade 300, subtitle fade after 300, credits fade after 300.

**Statement.** `heading` at 34 pt, 3 lines max, left 0.45, top 1.4, width 7.6. Set the last phrase in `emphasis` (bold). Hairline at y 4.55, `label` under it. Builds: statement fade 400, label fade after 300.

**Big number with bars.** `heading` title at top 0.45. `number` left 0.45, top 1.3. `label` + `body` under it. Right: 8 bars, x 3.9 to 9.55, bottom 4.9, each 0.55 in wide with 0.16 in gaps. Filled part in `ink`, empty part in `tint`. Heights step up. Builds: number fade 300, bars fly-bottom after, 300 each (first two `after`, rest `with`).

**List 2 × 3.** `heading` title. Six entries in a 2-column grid. Each: `meta` number ("01."), `heading` at 18 pt, one `body` line. Hairline under each row. Builds: rows fade after 300.

**Closing.** `display` right-aligned, right edge 9.55, top 2.4. Loop on the left at x 0.45. Four `label` + `body` columns at y 4.7. Builds: display fade 400.

## Motion

Calm. The reference fades opacity in 280 ms with CSS `ease`. Native fades at 300 ms, chained `after`. Fade transitions, fast. The only constant motion is the stair column. It moves in steps, never smoothly, so it reads as a printed ledger, not a screen.

## Example prompt

> Make a 5-slide year-in-review for a small reading-room library, style cobalt-ledger. One statement, one stat with 8 monthly bars, a 6-item list of what changed, and a closing line.

Caps in `kicker` are typed, not transformed. Write kicker text in capitals.

## Deck theme

Paste into `deck.json` → `"theme"`.

```json
{
  "colors": { "bg": "#F0EBDE", "ink": "#1F2BE0", "accent": "#1F2BE0", "accent2": "#1F2BE0", "surface": "#E6E0CE",
              "muted": "#5560E5", "tint": "#B4B6E6", "grid": "#DBD8DE" },
  "fonts": { "display": "Newsreader", "body": "Hanken Grotesk", "label": "DM Mono" },
  "type": {
    "title":    { "font": "display", "size": 72, "color": "ink", "spacing": 0.95 },
    "hero":     { "font": "display", "size": 54, "color": "ink", "spacing": 0.95 },
    "headline": { "font": "display", "size": 30, "color": "ink", "spacing": 1.05 },
    "number":   { "font": "display", "color": "ink", "spacing": 0.9 },
    "quote":    { "font": "display", "size": 30, "color": "ink", "spacing": 1.05 },
    "kicker":   { "font": "body", "size": 8, "bold": true, "color": "ink" },
    "step":     { "font": "display", "size": 18, "color": "ink" },
    "body":     { "font": "body", "size": 11, "color": "ink", "spacing": 1.3 },
    "label":    { "font": "label", "size": 8, "color": "ink" }
  }
}
```
