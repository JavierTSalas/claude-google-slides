#!/usr/bin/env python3
"""Render a HyperFrames motion template to a small, seamless GIF loop for Google Slides.

    python3 render_loop.py TEMPLATE.html OUT.gif [--theme deck.json] [--var id=value ...]
                           [--fps 12] [--width 360] [--colors 256] [--lossy 30] [--photo]

Variables: the template declares them in data-composition-variables. Values come from, in order:
template defaults < deck.json theme (color ids match theme.colors; '<role>_font' ids match theme.fonts) < --var.
A --var value may name a theme color, e.g. --var ink=accent.

Pipeline (sizes from docs/research/gif-compression.md):
  HyperFrames -> lossless PNG frames -> ffmpeg palettegen(stats_mode=full) + paletteuse(no dither,
  diff_mode=rectangle) -> gifsicle -O3 --lossy=30 (if available).

Needs: Node 22+ (npx), ffmpeg. gifsicle comes from PATH or npx gifsicle@7. Fonts download from Google Fonts.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfonts  # noqa: E402

HYPERFRAMES = os.environ.get("HYPERFRAMES", "hyperframes@0.9.59")
GSAP_CDN = re.compile(r'https://cdn\.jsdelivr\.net/npm/gsap@([0-9.]+)/dist/gsap\.min\.js')
CACHE = Path(os.environ.get("MOTION_SLIDES_CACHE", Path.home() / ".cache" / "motion-slides"))


def local_gsap(version):
    """Fetch gsap.min.js from the npm registry once (the render browser may not reach CDNs)."""
    import io
    import tarfile
    import urllib.request

    out = CACHE / f"gsap-{version}.min.js"
    if not out.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        url = f"https://registry.npmjs.org/gsap/-/gsap-{version}.tgz"
        with urllib.request.urlopen(url, timeout=60) as r:
            tgz = tarfile.open(fileobj=io.BytesIO(r.read()), mode="r:gz")
        out.write_bytes(tgz.extractfile("package/dist/gsap.min.js").read())
    return out


def die(msg):
    sys.exit(f"error: {msg}")


def declared_vars(src):
    m = re.search(r"data-composition-variables='(.*?)'", src, re.S)
    if not m:
        return []
    return json.loads(html.unescape(m.group(1)))


def resolve(v, colors):
    seen = 0
    while isinstance(v, str) and v in colors and seen < 4:
        v, seen = colors[v], seen + 1
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("template")
    ap.add_argument("out")
    ap.add_argument("--theme", help="deck.json whose theme supplies colors and fonts")
    ap.add_argument("--var", action="append", default=[], metavar="ID=VALUE")
    ap.add_argument("--fps", type=int, default=12, help="10-15 for flat graphics, 8 for photo-like")
    ap.add_argument("--width", type=int, help="output width px; size to the on-slide box at 1280 px slide width")
    ap.add_argument("--colors", type=int, default=256, help="palette size; 48 for photo-like loops")
    ap.add_argument("--lossy", type=int, default=30, help="gifsicle lossy level; 0 disables")
    ap.add_argument("--photo", action="store_true", help="photo-like preset: 8 fps, <=400 px, 48 colors")
    a = ap.parse_args()

    if a.photo:
        a.fps, a.colors = min(a.fps, 8), min(a.colors, 48)
        a.width = min(a.width or 400, 400)
    for tool in ("npx", "ffmpeg"):
        if not shutil.which(tool):
            die(f"'{tool}' not found. Install Node 22+ and ffmpeg, or skip motion (native builds still work)")

    tpl = Path(a.template).resolve()
    src = tpl.read_text()
    decl = declared_vars(src)
    ids = {d["id"]: d for d in decl}

    colors, fonts = {}, {}
    if a.theme:
        th = json.loads(Path(a.theme).read_text()).get("theme", {})
        colors, fonts = th.get("colors", {}), th.get("fonts", {})
    vals = {}
    for vid, d in ids.items():
        if d.get("type") == "color" and vid in colors:
            vals[vid] = resolve(vid, colors)
        elif vid.endswith("_font") and vid[:-5] in fonts:
            vals[vid] = fonts[vid[:-5]]
    for kv in a.var:
        k, _, v = kv.partition("=")
        if k not in ids:
            die(f"--var {k}: template declares {sorted(ids)}")
        vals[k] = resolve(v, colors) if ids[k].get("type") == "color" else v

    merged = {vid: vals.get(vid, d.get("default")) for vid, d in ids.items()}
    families = sorted({v for k, v in merged.items() if k.endswith("_font") and v})

    work = Path(tempfile.mkdtemp(prefix="motion-loop-"))
    try:
        css, files = gfonts.font_face_css(families, "fonts")
        missing = [f for f in families if not any(p.name.startswith(f.replace(" ", "")) for p in files)]
        if missing:
            print("warn: not on Google Fonts, will fall back:", ", ".join(missing))
        (work / "fonts").mkdir()
        for p in files:
            shutil.copy(p, work / "fonts" / p.name)
        page = src.replace("</head>", f"<style>\n{css}\n</style>\n</head>", 1) if css else src
        m = GSAP_CDN.search(page)
        if m:
            shutil.copy(local_gsap(m.group(1)), work / "gsap.min.js")
            page = GSAP_CDN.sub("gsap.min.js", page)
        (work / "index.html").write_text(page)

        frames = work / "frames"
        cmd = ["npx", "-y", HYPERFRAMES, "render", str(work), "--format", "png-sequence", "-o", str(frames),
               "--fps", str(a.fps), "--variables", json.dumps(vals), "--quiet"]
        print("render:", tpl.name, json.dumps(vals))
        r = subprocess.run(cmd, capture_output=True, text=True)
        pngs = sorted(frames.rglob("*.png")) if frames.exists() else []
        if r.returncode != 0 or not pngs:
            sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
            die("HyperFrames render failed (run 'npx hyperframes doctor' to check Chrome and ffmpeg)")

        seq = work / "seq"
        seq.mkdir()
        for i, p in enumerate(pngs):
            os.link(p, seq / f"f{i:05d}.png") if p.stat().st_dev == seq.stat().st_dev else shutil.copy(p, seq / f"f{i:05d}.png")
        scale = f",scale={a.width}:-1:flags=lanczos" if a.width else ""
        inp = ["-framerate", str(a.fps), "-i", str(seq / "f%05d.png")]
        pal = work / "palette.png"
        raw = work / "raw.gif"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-vf",
                        f"format=rgb24{scale},palettegen=max_colors={a.colors}:stats_mode=full", str(pal)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-i", str(pal), "-lavfi",
                        f"format=rgb24{scale}[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle",
                        "-loop", "0", str(raw)], check=True)

        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        gifsicle = [shutil.which("gifsicle")] if shutil.which("gifsicle") else ["npx", "-y", "-p", "gifsicle@7", "gifsicle"]
        ok = a.lossy and subprocess.run([*gifsicle, "--version"], capture_output=True).returncode == 0
        if ok:
            subprocess.run([*gifsicle, "-O3", f"--lossy={a.lossy}", str(raw), "-o", str(out)], check=True)
        else:
            shutil.copy(raw, out)
            if a.lossy:
                print("note: gifsicle unavailable; GIF is about 2x larger. Install gifsicle 1.92+ to halve it")

        from PIL import Image  # bundled with python-pptx

        with Image.open(out) as im:
            n, (w, h) = getattr(im, "n_frames", 1), im.size
            px = im.convert("RGB").getpixel((0, 0))
        ground = "#%02X%02X%02X" % px
        print(f"saved {out}: {w}x{h}, {n} frames @ {a.fps} fps, {out.stat().st_size / 1e6:.2f} MB")
        print(f"corner pixel {ground}: set the slide/box behind the GIF to exactly this color")
        want = str(merged.get("bg") or "").upper()
        if want.startswith("#") and len(want) == 7 and want != ground:
            print(f"warn: corner is {ground} but bg is {want}. Give #root (or a full-bleed child) "
                  f"'background: var(--bg)'; without it frames render on black")
        if out.stat().st_size > 1.6e6:
            print("warn: over the 1.6 MB budget. Shrink the moving area, lower --fps or --width, or use --photo")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
