# claude-google-slides

Make eye-catching, motion-rich Google Slides decks with Claude.

## Set up on a new machine

Paste this into Claude Code:

```text
Install the motion-slides skill from https://github.com/JavierTSalas/claude-google-slides on this machine.
1. Clone the repo (default branch) into ~/code/claude-google-slides. If it exists, git pull.
2. Link ~/code/claude-google-slides/skills/motion-slides to ~/.claude/skills/motion-slides. On Windows, copy it instead. Replace any old copy.
3. Install python-pptx: python3 -m pip install python-pptx
4. For motion loops, make sure Node 22+ and ffmpeg are on PATH. Install them if missing.
5. Optional, for previews: install LibreOffice and poppler (pdftoppm).
6. Test: run python3 ~/.claude/skills/motion-slides/scripts/style_tour.py editorial-forest <temp folder>/motion-tour, then show me <temp folder>/motion-tour/preview/contact-sheet.png. If Node or ffmpeg is missing, add --no-motion.
Tell me what works and what is still missing.
```

Then ask for a deck in any session, for example: *Make a 5-slide Google Slides deck about our Q3 launch in editorial forest.* Or type `/motion-slides`.

## The skill: `motion-slides`

[`skills/motion-slides/`](skills/motion-slides/SKILL.md) is a Claude skill. Prompts, styles and recipes, plus three small scripts.
It writes a `.pptx` with native builds, transitions and looping GIFs. Google Drive converts it to native Google Slides.

**Install**

- Claude Code: use the prompt above, or copy `skills/motion-slides` to `~/.claude/skills/motion-slides` (or `.claude/skills/` in a project).
- Claude apps: zip the `motion-slides` folder and upload it as a custom skill.

**Dependencies**

| What | Needed for |
|---|---|
| `pip install python-pptx` | Every deck |
| Node 22+ and ffmpeg | Motion loops (HyperFrames and gifsicle come through `npx`) |
| LibreOffice and poppler | Optional static preview |

**Try it**

> Make a 5-slide deck for our Q3 kickoff in editorial forest, with a looping badge on the title.

More in [examples/prompts.md](skills/motion-slides/examples/prompts.md).

## Gallery

![Eight native Google Slides with builds, transitions and rendered loops](gallery/previews/reel.gif)

[Motion gallery](gallery/README.md): six example prompts, each with a motion preview and the resulting native Google Slides deck.

## Research

- [Google Slides + Motion: Discovery Report](docs/research/2026-11-17-google-slides-motion-discovery.md)
- [Style Direction](docs/research/style-direction.md)
- [GIF compression budget](docs/research/gif-compression.md)
