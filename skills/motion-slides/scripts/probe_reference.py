#!/usr/bin/env python3
"""Probe a style reference. Measure what can be measured, so the style spec is not guessed.

Usage:
  python3 probe_reference.py <file-or-url> <out_dir> [--frames 16] [--pages 8]

Kinds (by extension or URL):
  video  .mp4 .mov .webm .mkv .gif   cuts, move/hold timing, frames, palette
  image  .png .jpg .jpeg .webp        palette
  pdf    .pdf                         pages, palette, embedded font names
  pptx   .pptx                        theme, fonts, colors, builds, transitions, pages
  web    http(s)://... or .html       screenshots, computed fonts and colors, CSS motion

Writes to out_dir:
  probe.json   measured facts (read this, then write style.md)
  sheet.jpg    contact sheet (look at this)
  palette.png  swatches with hex and share

Deps: Pillow, numpy. ffmpeg for video. LibreOffice + pdftoppm for pptx/pdf pages.
Node + playwright for web (calls probe_web.mjs next to this file).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
VIDEO = {".mp4", ".mov", ".webm", ".mkv", ".gif", ".m4v"}
IMAGE = {".png", ".jpg", ".jpeg", ".webp"}


# ---------------------------------------------------------------- helpers
def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def hexof(rgb):
    return "#%02X%02X%02X" % tuple(int(c) for c in rgb)


def lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def sat(rgb):
    mx, mn = max(rgb) / 255, min(rgb) / 255
    return 0 if mx == 0 else (mx - mn) / mx


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/System/Library/Fonts/Menlo.ttc", "C:/Windows/Fonts/consola.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- palette
def _quant(pixels, k):
    if len(pixels) < k:
        return []
    img = Image.fromarray(pixels.reshape(1, -1, 3).astype(np.uint8))
    q = img.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[: k * 3]).reshape(-1, 3)
    counts = np.bincount(np.array(q).ravel(), minlength=k)
    return [(pal[i], counts[i] / counts.sum()) for i in range(k) if counts[i]]


def _merge(cols, dist=28):
    out = []
    for c, s in sorted(cols, key=lambda x: -x[1]):
        for o in out:
            if np.linalg.norm(o[0].astype(float) - c) < dist:
                o[1] += s
                break
        else:
            out.append([c.astype(float), s])
    return out


def palette(images, k=10):
    """Area palette + accent palette (saturated pixels only, so small accents survive)."""
    px = []
    for im in images:
        im = im.convert("RGB")
        im.thumbnail((360, 360))
        px.append(np.asarray(im).reshape(-1, 3))
    px = np.concatenate(px)
    rng = np.random.default_rng(0)
    if len(px) > 250_000:
        px = px[rng.choice(len(px), 250_000, replace=False)]
    area = _merge(_quant(px, k))
    mx, mn = px.max(1) / 255, px.min(1) / 255
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    vivid = px[(s > 0.35) & (mx > 0.25)]
    vivid_share = len(vivid) / len(px)
    acc = _merge(_quant(vivid, 6), dist=40) if len(vivid) > 200 else []
    cols = [{"hex": hexof(c), "share": round(sh, 4), "src": "area"} for c, sh in area if sh >= 0.004]
    for c, sh in acc:
        if all(np.linalg.norm(np.array(list(bytes.fromhex(x["hex"][1:])), float) - c) > 40 for x in cols):
            cols.append({"hex": hexof(c), "share": round(sh * vivid_share, 4), "src": "accent"})
    # role guesses: bg = largest, ink = best contrast vs bg, accents = vivid by share
    rgb = lambda h: tuple(bytes.fromhex(h[1:]))
    cols.sort(key=lambda x: -x["share"])
    bg = cols[0]
    bg["role_guess"] = "bg"
    rest = [c for c in cols[1:] if c["share"] >= 0.003]
    if rest:
        ink = max(rest, key=lambda c: contrast(rgb(c["hex"]), rgb(bg["hex"])) * (1 + min(c["share"], .1)))
        ink["role_guess"] = "ink"
    for c in cols:
        c["contrast_vs_bg"] = round(contrast(rgb(c["hex"]), rgb(bg["hex"])), 2)
    # flag colors that are a blend of two others (halftone, anti-aliasing, overprint, motion blur)
    arr = {c["hex"]: np.array(rgb(c["hex"]), float) for c in cols}
    for c in cols:
        x = arr[c["hex"]]
        best = None
        for a in cols:
            for b in cols:
                if a is b or c in (a, b) or a["hex"] >= b["hex"]:
                    continue
                d = arr[b["hex"]] - arr[a["hex"]]
                t = float(np.clip(np.dot(x - arr[a["hex"]], d) / max(np.dot(d, d), 1), 0, 1))
                err = np.linalg.norm(arr[a["hex"]] + t * d - x)
                if 0.15 < t < 0.85 and err < 22 and (best is None or err < best[0]):
                    best = (err, a["hex"], b["hex"])
        if best:
            c["maybe_mix_of"] = [best[1], best[2]]
    n = 1
    for c in sorted(cols, key=lambda c: -c["share"] * (0.2 + sat(rgb(c["hex"])))):
        if "role_guess" in c:
            continue
        if "maybe_mix_of" in c:
            c["role_guess"] = "blend"
        elif sat(rgb(c["hex"])) > 0.3:
            c["role_guess"] = "accent" if n == 1 else f"accent{n}"
            n += 1
        else:
            c["role_guess"] = "surface/muted"
    return cols


def palette_png(cols, path):
    cw, h = 150, 120
    im = Image.new("RGB", (cw * len(cols), h + 66), "white")
    d = ImageDraw.Draw(im)
    f = font(14)
    for i, c in enumerate(cols):
        x = i * cw
        d.rectangle([x, 0, x + cw - 4, h], fill=c["hex"])
        d.text((x + 4, h + 6), c["hex"], fill="black", font=f)
        d.text((x + 4, h + 24), f'{c["share"] * 100:.1f}%  {c["contrast_vs_bg"]}:1', fill="black", font=f)
        d.text((x + 4, h + 42), c["role_guess"], fill="black", font=f)
    im.save(path)


# ---------------------------------------------------------------- contact sheet
def sheet(images, labels, path, cols=4, w=480):
    if not images:
        return
    ims = []
    for im in images:
        im = im.convert("RGB")
        r = w / im.width
        ims.append(im.resize((w, max(1, int(im.height * r)))))
    h = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    pad, lab = 6, 20
    out = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + lab + pad) + pad), (24, 24, 24))
    d = ImageDraw.Draw(out)
    f = font(13)
    for i, (im, lb) in enumerate(zip(ims, labels)):
        x = pad + (i % cols) * (w + pad)
        y = pad + (i // cols) * (h + lab + pad)
        out.paste(im, (x, y))
        d.text((x + 2, y + h + 3), lb, fill=(220, 220, 220), font=f)
    out.save(path, quality=88)


# ---------------------------------------------------------------- video
def probe_video(src, out, n_frames):
    meta = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height,r_frame_rate:format=duration", "-of", "json", src]).stdout)
    st, dur = meta["streams"][0], float(meta["format"].get("duration") or 0)
    num, den = (int(x) for x in st["r_frame_rate"].split("/"))
    fps = num / den if den else 0

    # scene cuts
    r = run(["ffmpeg", "-hide_banner", "-i", src, "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"])
    cuts = [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    edges = [0.0] + cuts + [dur]
    shots = [round(b - a, 2) for a, b in zip(edges, edges[1:]) if b - a > 0.05]

    # motion energy at 10 fps on a tiny grayscale copy
    W, S = 96, 10
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={S},scale={W}:-2,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    H = int(round(st["height"] * W / st["width"] / 2) * 2)
    fr = np.frombuffer(raw, np.uint8)[: (len(raw) // (W * H)) * W * H].reshape(-1, H, W).astype(np.float32)
    e = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2)) / 255 if len(fr) > 1 else np.zeros(0)
    thr = max(0.004, float(np.percentile(e, 40)) * 1.5) if len(e) else 0
    moving = e > thr
    runs, cur, val = [], 0, None
    for m in moving:
        if m == val:
            cur += 1
        else:
            if val is not None:
                runs.append((bool(val), cur))
            val, cur = m, 1
    if val is not None:
        runs.append((bool(val), cur))
    ms = lambda xs: [int(x * 1000 / S) for x in xs]
    moves = ms([n for m, n in runs if m])
    holds = ms([n for m, n in runs if not m])
    med = lambda xs: int(np.median(xs)) if xs else None
    motion = {
        "duration_s": round(dur, 2), "fps": round(fps, 2), "size_px": [st["width"], st["height"]],
        "cuts_s": cuts, "cut_count": len(cuts), "shot_s": shots, "median_shot_s": round(float(np.median(shots)), 2) if shots else None,
        "moving_share": round(float(moving.mean()), 2) if len(e) else None,
        "move_ms": {"median": med(moves), "p25": int(np.percentile(moves, 25)) if moves else None,
                    "p75": int(np.percentile(moves, 75)) if moves else None, "count": len(moves)},
        "hold_ms": {"median": med(holds), "p75": int(np.percentile(holds, 75)) if holds else None, "count": len(holds)},
        "energy_curve_10fps": [round(float(x), 4) for x in e[:: max(1, len(e) // 150)]],
        "notes": "move = contiguous frames above motion threshold; hold = still stretches. Use move_ms for build durations, hold_ms for stagger and dwell.",
    }

    # frames: every cut (+0.4 s so the new shot has settled) plus even samples
    times = sorted({round(min(dur - 0.05, c + 0.4), 2) for c in cuts})
    even = [round(dur * (i + 0.5) / n_frames, 2) for i in range(n_frames)]
    for t in even:
        if len(times) >= n_frames:
            break
        if all(abs(t - x) > dur / (n_frames * 2) for x in times):
            times.append(t)
    times = sorted(times)[:n_frames]
    tmp = Path(tempfile.mkdtemp())
    imgs = []
    for i, t in enumerate(times):
        p = tmp / f"f{i:02d}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf", "scale=640:-2", str(p)])
        if p.exists():
            imgs.append(Image.open(p).copy())
    shutil.rmtree(tmp, ignore_errors=True)
    labels = [f"{t:.1f}s" + ("  cut" if any(abs(t - 0.4 - c) < 0.05 for c in cuts) else "") for t in times]
    return {"motion": motion}, imgs, labels


# ---------------------------------------------------------------- pptx
PRESETS = {("entr", 1): "appear", ("entr", 2): "fly", ("entr", 10): "fade", ("entr", 23): "zoom",
           ("entr", 53): "grow-turn", ("entr", 22): "wipe", ("emph", 8): "spin", ("exit", 10): "fade-out",
           ("exit", 2): "fly-out", ("path", 0): "motion-path"}
FLYDIR = {1: "top", 2: "right", 4: "bottom", 8: "left"}
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"


def probe_pptx(src, out, n_pages):
    from lxml import etree
    z = zipfile.ZipFile(src)
    names = z.namelist()
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    sz = pres.find(f"{P}sldSz")
    emu = 914400
    canvas = {"width_in": round(int(sz.get("cx")) / emu, 3), "height_in": round(int(sz.get("cy")) / emu, 3)} if sz is not None else {}
    theme = {}
    for tn in sorted(n for n in names if re.match(r"ppt/theme/theme\d+\.xml", n))[:1]:
        t = etree.fromstring(z.read(tn))
        cs = t.find(f".//{A}clrScheme")
        if cs is not None:
            for el in cs:
                c = el.find(f"{A}srgbClr")
                s = el.find(f"{A}sysClr")
                theme[etree.QName(el).localname] = "#" + (c.get("val") if c is not None else (s.get("lastClr") if s is not None else "?"))
        fs = t.find(f".//{A}fontScheme")
        if fs is not None:
            theme["major_font"] = fs.find(f"{A}majorFont/{A}latin").get("typeface")
            theme["minor_font"] = fs.find(f"{A}minorFont/{A}latin").get("typeface")

    slides = sorted((n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                    key=lambda n: int(re.findall(r"\d+", n)[-1]))
    fonts, fonts_area, sizes, text_cols, fill_cols, bgs = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    per_slide = []
    for sn in slides:
        x = etree.fromstring(z.read(sn))
        for r in x.iter(f"{A}r"):
            t = (r.findtext(f"{A}t") or "")
            rpr = r.find(f"{A}rPr")
            if rpr is None or not t.strip():
                continue
            lat = rpr.find(f"{A}latin")
            fam = lat.get("typeface") if lat is not None else "(theme)"
            key = fam + (" bold" if rpr.get("b") == "1" else "") + (" italic" if rpr.get("i") == "1" else "")
            fonts[key] += len(t)
            fonts_area[key] += len(t) * (int(rpr.get("sz", 1800)) / 100) ** 2
            if rpr.get("sz"):
                sizes[int(rpr.get("sz")) // 100] += len(t)
            c = rpr.find(f"{A}solidFill/{A}srgbClr")
            if c is not None:
                text_cols["#" + c.get("val").upper()] += len(t)
        for sp in x.iter(f"{P}spPr"):
            c = sp.find(f"{A}solidFill/{A}srgbClr")
            if c is not None:
                fill_cols["#" + c.get("val").upper()] += 1
        b = x.find(f".//{P}bg//{A}srgbClr")
        if b is not None:
            bgs["#" + b.get("val").upper()] += 1
        # transition
        tr = x.find(f".//{P}transition")
        trans = None
        if tr is not None:
            kids = [etree.QName(k).localname for k in tr if etree.QName(k).localname not in ("sndAc",)]
            trans = {"kind": kids[0] if kids else "none", "spd": tr.get("spd"), "dur_ms": tr.get("{http://schemas.microsoft.com/office/powerpoint/2010/main}dur")}
        # builds
        builds = []
        for ctn in x.iter(f"{P}cTn"):
            cls = ctn.get("presetClass")
            if not cls:
                continue
            pid, sub = int(ctn.get("presetID", 0)), int(ctn.get("presetSubtype", 0))
            name = PRESETS.get((cls, pid), f"{cls}#{pid}")
            if name == "fly":
                name = "fly-" + FLYDIR.get(sub, str(sub))
            durs = [int(c.get("dur")) for c in ctn.iter(f"{P}cTn") if (c.get("dur") or "").isdigit() and int(c.get("dur")) > 1]
            delay = ctn.find(f"{P}stCondLst/{P}cond")
            builds.append({"fx": name, "trigger": {"clickEffect": "click", "withEffect": "with", "afterEffect": "after"}.get(ctn.get("nodeType"), ctn.get("nodeType")),
                           "dur_ms": max(durs) if durs else None,
                           "delay_ms": int(delay.get("delay")) if delay is not None and (delay.get("delay") or "").isdigit() else 0})
        per_slide.append({"slide": sn.split("/")[-1], "transition": trans, "builds": builds})
    gifs = [n for n in names if n.startswith("ppt/media/") and n.lower().endswith(".gif")]
    tot, tot_a = sum(fonts.values()) or 1, sum(fonts_area.values()) or 1
    facts = {
        "canvas": canvas, "theme": theme,
        "fonts": [{"family": f, "share": round(a / tot_a, 3), "share_chars": round(fonts[f] / tot, 3)}
                  for f, a in fonts_area.most_common(12)],
        "text_sizes_pt": [{"pt": s, "chars": n} for s, n in sorted(sizes.items(), key=lambda x: -x[0])],
        "text_colors": [{"hex": h, "chars": n} for h, n in text_cols.most_common(10)],
        "shape_fills": [{"hex": h, "count": n} for h, n in fill_cols.most_common(10)],
        "slide_backgrounds": [{"hex": h, "count": n} for h, n in bgs.most_common(10)],
        "media": {"gif": len(gifs), "other": len([n for n in names if n.startswith("ppt/media/")]) - len(gifs)},
        "slides": per_slide,
    }
    all_b = [b for s in per_slide for b in s["builds"]]
    if all_b:
        facts["motion_summary"] = {
            "build_fx": dict(Counter(b["fx"] for b in all_b)),
            "build_trigger": dict(Counter(b["trigger"] for b in all_b)),
            "build_dur_ms_median": int(np.median([b["dur_ms"] for b in all_b if b["dur_ms"]])) if any(b["dur_ms"] for b in all_b) else None,
            "transitions": dict(Counter((s["transition"] or {}).get("kind", "none") for s in per_slide)),
        }
    imgs, labels = render_pages(src, n_pages, office=True)
    return facts, imgs, labels


def render_pages(src, n_pages, office=False):
    tmp = Path(tempfile.mkdtemp())
    pdf = src
    if office:
        if not shutil.which("soffice"):
            return [], []
        run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), src], timeout=240)
        pdfs = list(tmp.glob("*.pdf"))
        if not pdfs:
            return [], []
        pdf = str(pdfs[0])
    if not shutil.which("pdftoppm"):
        return [], []
    run(["pdftoppm", "-png", "-r", "60", "-l", str(n_pages), pdf, str(tmp / "p")])
    files = sorted(tmp.glob("p*.png"))
    imgs = [Image.open(f).copy() for f in files]
    shutil.rmtree(tmp, ignore_errors=True)
    return imgs, [f"page {i + 1}" for i in range(len(imgs))]


def probe_pdf(src, out, n_pages):
    facts = {}
    if shutil.which("pdffonts"):
        rows = run(["pdffonts", src]).stdout.splitlines()[2:]
        fams = Counter(re.sub(r"^[A-Z]{6}\+", "", r.split()[0]) for r in rows if r.strip())
        facts["fonts"] = [{"family": f, "objects": n} for f, n in fams.most_common(12)]
    imgs, labels = render_pages(src, n_pages)
    return facts, imgs, labels


def probe_web(src, out, n_pages):
    js = HERE / "probe_web.mjs"
    r = run(["node", str(js), src, str(out), str(n_pages)], timeout=300)
    if r.returncode != 0:
        sys.exit("probe_web.mjs failed:\n" + r.stderr[-2000:])
    facts = json.loads((out / "web.json").read_text())
    shots = sorted(out.glob("shot-*.png"))
    imgs = [Image.open(f).copy() for f in shots]
    return facts, imgs, [f.stem for f in shots]


# ---------------------------------------------------------------- main
def main():
    args, opts, it = [], {}, iter(sys.argv[1:])
    for a in it:
        if a.startswith("--"):
            opts[a] = next(it, None)
        else:
            args.append(a)
    if len(args) < 2:
        sys.exit(__doc__)
    src, out = args[0], Path(args[1])
    out.mkdir(parents=True, exist_ok=True)
    n_frames = int(opts.get("--frames", 16))
    n_pages = int(opts.get("--pages", 8))
    ext = Path(src.split("?")[0]).suffix.lower()
    if src.startswith(("http://", "https://")) and ext not in VIDEO | IMAGE | {".pdf", ".pptx"}:
        kind = "web"
    elif ext in VIDEO:
        kind = "video"
    elif ext in IMAGE:
        kind = "image"
    elif ext == ".pdf":
        kind = "pdf"
    elif ext == ".pptx":
        kind = "pptx"
    elif ext in (".html", ".htm"):
        kind = "web"
    else:
        sys.exit(f"unknown reference type: {src}")

    if kind == "video":
        facts, imgs, labels = probe_video(src, out, n_frames)
    elif kind == "image":
        im = Image.open(src)
        facts, imgs, labels = {"size_px": list(im.size)}, [im.copy()], [Path(src).name]
    elif kind == "pdf":
        facts, imgs, labels = probe_pdf(src, out, n_pages)
    elif kind == "pptx":
        facts, imgs, labels = probe_pptx(src, out, n_pages)
    else:
        facts, imgs, labels = probe_web(src, out, n_pages)

    pal = palette(imgs) if imgs else []
    sheet(imgs, labels, out / "sheet.jpg")
    if pal:
        palette_png(pal, out / "palette.png")
    res = {"kind": kind, "source": src, "measured": {**facts, "palette": pal},
           "files": {"sheet": "sheet.jpg", "palette": "palette.png"}}
    (out / "probe.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res["measured"].items() if k not in ("slides", "energy_curve_10fps")}, indent=1)[:4000])
    print(f"\nwrote {out}/probe.json, sheet.jpg, palette.png")


if __name__ == "__main__":
    main()
