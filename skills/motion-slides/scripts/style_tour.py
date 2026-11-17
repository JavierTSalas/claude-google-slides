#!/usr/bin/env python3
"""Specimen deck: every recipe in one style. Use it to check a new or edited style.

    python3 style_tour.py STYLE OUTDIR [--no-motion]

STYLE is a slug under ../styles/ or a path to a style.md that has a "## Deck theme" JSON block.
Writes OUTDIR/deck.json, OUTDIR/assets/*.gif, OUTDIR/tour.pptx and OUTDIR/preview/contact-sheet.png.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent

# loop file -> (template, render args, theme var overrides)
LOOPS = {
    "badge.gif": ("badge.html", ["--fps", "12", "--width", "360"], {}),
    "light.gif": ("window-light.html", ["--photo"], {}),
    "orbits.gif": ("orbits.html", ["--fps", "15", "--width", "1024"], {}),
}


def json_blocks(md):
    return [json.loads(b) for b in re.findall(r"```json\s*\n(.*?)\n```", md, re.S)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("style")
    ap.add_argument("outdir")
    ap.add_argument("--no-motion", action="store_true", help="skip loops (no Node/ffmpeg needed)")
    a = ap.parse_args()

    sp = Path(a.style)
    if not sp.is_file():
        sp = SKILL / "styles" / a.style / "style.md"
    md = sp.read_text()
    m = re.search(r"## Deck theme.*?```json\s*\n(.*?)\n```", md, re.S)
    if not m:
        sys.exit(f"{sp}: no '## Deck theme' JSON block")
    theme = json.loads(m.group(1))

    slides = json_blocks((SKILL / "reference" / "recipes.md").read_text())
    out = Path(a.outdir).resolve()
    (out / "assets").mkdir(parents=True, exist_ok=True)
    if a.no_motion:
        for s in slides:
            s["items"] = [i for i in s["items"] if not str(i.get("image", "")).endswith(".gif")]
    deck = {"title": f"Style tour: {sp.parent.name}", "assets": "assets", "theme": theme, "slides": slides}
    (out / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False))

    if not a.no_motion:
        for gif, (tpl, args, _) in LOOPS.items():
            subprocess.run([sys.executable, str(HERE / "render_loop.py"), str(SKILL / "motion" / tpl),
                            str(out / "assets" / gif), "--theme", str(out / "deck.json"), *args], check=True)
    subprocess.run([sys.executable, str(HERE / "build_deck.py"), str(out / "deck.json"), str(out / "tour.pptx"),
                    "--preview", str(out / "preview")], check=True)


if __name__ == "__main__":
    main()
