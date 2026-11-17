# claude-google-slides

Make eye-catching, motion-rich Google Slides decks with Claude.

## The skill: `motion-slides`

[`skills/motion-slides/`](skills/motion-slides/SKILL.md) is a Claude skill. Prompts, styles and recipes, plus three small scripts.
It writes a `.pptx` with native builds, transitions and looping GIFs. Google Drive converts it to native Google Slides.

**Install**

- Claude Code: copy `skills/motion-slides` to `~/.claude/skills/motion-slides` (or `.claude/skills/` in a project).
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

## Research

- [Google Slides + Motion: Discovery Report](docs/research/2026-11-17-google-slides-motion-discovery.md)
- [Style Direction](docs/research/style-direction.md)
- [GIF compression budget](docs/research/gif-compression.md)
