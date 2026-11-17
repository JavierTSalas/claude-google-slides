"""Fetch Google Fonts TTFs (stdlib only). Used for outline text, previews and motion renders.

Cache: $MOTION_SLIDES_FONTS or ~/.cache/motion-slides/fonts
"""
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CACHE = Path(os.environ.get("MOTION_SLIDES_FONTS", Path.home() / ".cache" / "motion-slides" / "fonts"))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"  # this UA gets TrueType URLs from the css2 API


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch(family, weight=400, italic=False, exact=False):
    """Local .ttf path for one face, or None. exact=False falls back to the family's default face."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{family.replace(' ', '')}-{weight}{'i' if italic else ''}.ttf"
    if out.exists():
        return out
    queries = [f"{family}:ital,wght@{int(italic)},{weight}"]
    if weight == 400:
        queries.append(f"{family}:ital@{int(italic)}")
    if not italic and weight == 400:
        queries.append(family)
    for q in queries:
        url = "https://fonts.googleapis.com/css2?family=" + urllib.parse.quote(q, safe=":,@;")
        try:
            css = _get(url).decode()
        except (urllib.error.HTTPError, urllib.error.URLError):
            continue
        m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)
        if m:
            out.write_bytes(_get(m.group(1)))
            return out
    if not exact and (weight, italic) != (400, False):
        return fetch(family, 400, False, exact=True)
    return None


def faces(family):
    """Common faces for a family: regular, medium, bold, italic. Returns {(weight, italic): path}."""
    got = {}
    for w, i in ((400, False), (500, False), (700, False), (400, True)):
        p = fetch(family, w, i, exact=True)
        if p:
            got[(w, i)] = p
    return got


def install(families):
    """Copy faces into ~/.local/share/fonts so LibreOffice previews use the real fonts."""
    dest = Path.home() / ".local" / "share" / "fonts" / "motion-slides"
    dest.mkdir(parents=True, exist_ok=True)
    missing = []
    for fam in families:
        fs = faces(fam)
        if not fs:
            missing.append(fam)
        for p in fs.values():
            shutil.copy(p, dest / p.name)
    if shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(dest)], capture_output=True)
    if missing:
        print("fonts not on Google Fonts (Slides will fall back to Arial):", ", ".join(missing))
    return missing


def font_face_css(families, rel_dir="fonts"):
    """@font-face CSS for HTML renders. Copies TTFs next to the HTML under rel_dir by the caller."""
    rules, files = [], []
    for fam in families:
        for (w, i), p in faces(fam).items():
            files.append(p)
            rules.append(f'@font-face {{ font-family: "{fam}"; src: url("{rel_dir}/{p.name}"); '
                         f'font-weight: {w}; font-style: {"italic" if i else "normal"}; }}')
    return "\n".join(rules), files
