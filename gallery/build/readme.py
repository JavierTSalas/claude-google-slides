"""Write gallery/README.md from examples.json and the loop GIFs. Usage: python3 readme.py"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
allx = json.load(open(os.path.join(ROOT, "examples.json")))
ex = [e for e in allx if e.get("group") != "reference"]
ref = [e for e in allx if e.get("group") == "reference"]


def loops():
    rows = []
    for f in sorted(os.listdir(os.path.join(ROOT, "assets"))):
        if not f.endswith(".gif"):
            continue
        p = os.path.join(ROOT, "assets", f)
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                              "stream=width,height,nb_read_frames,r_frame_rate", "-of", "csv=p=0", p],
                             capture_output=True, text=True).stdout.strip().split(",")
        w, h, rate, n = out
        fps = int(rate.split("/")[0]) // int(rate.split("/")[1])
        rows.append(f"| `{f}` | {w}×{h} | {fps} | {n} | {os.path.getsize(p) / 1e6:.2f} MB |")
    return "\n".join(rows)


parts = [f"""# Motion gallery

Six prompts. Eight native Google Slides. Real motion.

![All eight slides playing in order](previews/reel.gif)

Every slide is built from native Google Slides objects: text in Google Fonts, shapes, builds and transitions.
Motion that Slides cannot do natively is a small looping GIF, rendered from HTML and placed like any image.
[`gallery.pptx`](gallery.pptx) ({os.path.getsize(os.path.join(ROOT, 'gallery.pptx')) / 1e6:.1f} MB) converts to Google Slides with every build and transition intact.

## Examples
"""]

for e in ex:
    sw = " ".join(f"`#{c}`" for c in e["palette"])
    parts.append(f"""### {e['title']} · {e['role']}

<img src="previews/{e['id']}.gif" width="640" alt="{e['title']} preview">

> {e['prompt']}

**Type** {', '.join(e['fonts'])} · **Palette** {sw}<br>
**Motion** {'. '.join(e['motion'])}.
""")

parts.append("""## From a reference

Point Claude at a video, a deck or a site. It measures the palette, type and motion tempo, writes a reusable style, then builds decks in it.
These two styles come from the motion-slides skill ([PR #3](https://github.com/JavierTSalas/claude-google-slides/pull/3)). The previews replay their specimen decks.
""")
for e in ref:
    sw = " ".join(f"`#{c}`" for c in e["palette"])
    parts.append(f"""### {e['title']} · {e['role']}

<img src="previews/{e['id']}.gif" width="640" alt="{e['title']} preview">

**Reference** {e['reference']}

1. Make the style:
   > {e['stylePrompt']}
2. Use it:
   > {e['prompt']}

**Type** {', '.join(e['fonts'])} · **Palette** {sw}<br>
**Motion** {'. '.join(e['motion'])}. Deck: [`{e['deck']}`]({e['deck']}).
""")

parts.append(f"""## Bring your own style

Fill in the brackets. Keep one idea per slide.

```text
Make a [N]-slide Google Slides deck about [topic].
Style: [2-4 colors]. [display font] for headlines, [text font] for body. Google Fonts only.
Motion: [calm | medium | punchy]. Builds one at a time: [fade | fly-in | zoom].
One rendered loop: [what moves, where, on the slide's exact background color].
Minimal text. No chrome: no page numbers, no corner labels.
```

Or point at a reference:

```text
Match the look of [video, poster, site or deck link].
Take the palette, type, layout and motion tempo. Not the brand, logos or footage.
```

## Tricks worth stealing

- **Pan across slides.** One line sits at the same height on three slides. The push transition reads as a camera pan.
- **Bars that grow.** Bars fly in from below, under a mask in the ground color at the baseline. They rise from the axis.
- **Loops with no edges.** Each GIF is rendered on the slide's exact background color, so it has no visible box.
- **Text over motion.** Headlines stay native text on top of a full-bleed loop. They stay editable.
- **Emphasis last.** The star is already on the slide. It spins after everything else lands.

## What is native, what is rendered

| Native Google Slides | Rendered |
|---|---|
| Text in Google Fonts, shapes, rotation | GIF loops: badge, window light, ripple, orbits |
| Builds: fade, fly-in, zoom, spin. Chained "after previous" | Outline text (PNG). Slides has no text stroke |
| Transitions: fade, push | |

Loop budget:

| Loop | Size | fps | Frames | File |
|---|---|---|---|---|
{loops()}

## Rebuild

Needs Python with `python-pptx`, Node with Playwright (Chromium), and `ffmpeg`.

```bash
cd gallery/build
node render_loop.js loops/ripple.html ../assets/ripple.gif 200 12   # one loop: html -> GIF
python3 build_gallery.py      # ../gallery.pptx and out/scenes.js
python3 gifs_manifest.py      # GIF frames for the preview player
python3 pptx_scenes.py ../reference/riso-overprint.pptx out/ref/riso-overprint   # any .pptx -> preview scenes
node render_preview.js        # ../previews/*.gif and *.mp4
python3 readme.py             # this file
```

Upload `gallery.pptx` to Google Drive and open it with Google Slides.

Previews come from [`build/player.html`](build/player.html). It replays the deck's builds, transitions and loops with the same timing that Slides uses.
Text placement was checked against a Google Slides PDF export of this deck (within about 0.05 in).
""")

open(os.path.join(ROOT, "README.md"), "w").write("\n".join(parts))
print("wrote README.md")
