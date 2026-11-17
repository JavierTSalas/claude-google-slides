#!/usr/bin/env python3
"""Build a Google-Slides-ready .pptx from a motion-slides deck spec (JSON).

    python3 build_deck.py deck.json out.pptx [--preview DIR]

Native output: text, shapes, images (animated GIFs keep every frame),
builds (fade, fly, zoom, spin) and slide transitions (fade, push, flip, gallery).
Google Drive converts the .pptx to Google Slides on import and keeps all of these.

Needs: python-pptx (tested 1.0.2; brings lxml and Pillow). Other versions usually work
Optional for --preview: LibreOffice (soffice) and poppler (pdftoppm).
Spec: ../reference/deck-spec.md
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from itertools import count
from pathlib import Path

import pptx
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfonts  # noqa: E402

W_IN, H_IN = 10.0, 5.625  # Google Slides default 16:9 page
PPTX_TESTED = "1.0.2"  # known-good python-pptx; other versions usually work
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
NS_P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"

WARN = []


def die(msg):
    sys.exit(f"error: {msg}")


def warn(msg):
    WARN.append(msg)


# ---------------------------------------------------------------- theme tokens
class Theme:
    def __init__(self, spec):
        t = spec.get("theme", {})
        self.colors = {k: v for k, v in t.get("colors", {}).items()}
        self.fonts = dict(t.get("fonts", {}))
        self.type = dict(t.get("type", {}))
        self.used_fonts = set()

    def color(self, v, where):
        seen = 0
        while isinstance(v, str) and v in self.colors and seen < 4:
            v, seen = self.colors[v], seen + 1
        h = str(v).lstrip("#")
        if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
            die(f"{where}: color '{v}' is not a theme color or 6-digit hex")
        return RGBColor.from_string(h.upper())

    def font(self, v):
        fam = self.fonts.get(v, v)
        self.used_fonts.add(fam)
        return fam


# ---------------------------------------------------------------- helpers
def box(item, where, need_wh=True):
    at = item.get("at")
    if not isinstance(at, list) or len(at) < 2:
        die(f"{where}: 'at' must be [x, y, w, h] in inches (page is 10 x 5.625)")
    at = list(at) + [None] * (4 - len(at))
    x, y, w, h = at[:4]
    if need_wh and (w is None or h is None):
        die(f"{where}: text and shapes need w and h in 'at'")
    if x > W_IN or y > H_IN or (w and x + w < 0) or (h and y + h < 0):
        warn(f"{where}: sits fully off the page")
    return x, y, w, h


ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT, "justify": PP_ALIGN.JUSTIFY}
ANCHOR = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}
RUN_KEYS = ("font", "size", "color", "bold", "italic", "underline")

SHAPES = {
    "rect": MSO_SHAPE.RECTANGLE,
    "round-rect": MSO_SHAPE.ROUNDED_RECTANGLE,
    "ellipse": MSO_SHAPE.OVAL,
    "circle": MSO_SHAPE.OVAL,
    "arch": MSO_SHAPE.ROUND_2_SAME_RECTANGLE,  # top corners fully round
    "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
    "star": MSO_SHAPE.STAR_5_POINT,
    "star-8": MSO_SHAPE.STAR_8_POINT,
    "star-12": MSO_SHAPE.STAR_12_POINT,
    "diamond": MSO_SHAPE.DIAMOND,
    "chevron": MSO_SHAPE.CHEVRON,
    "arrow": MSO_SHAPE.RIGHT_ARROW,
    "half-frame": MSO_SHAPE.HALF_FRAME,
}


def resolve_style(item, theme, where):
    """Merge: type preset ('as') <- item keys."""
    st = {}
    preset = item.get("as")
    if preset:
        if preset not in theme.type:
            die(f"{where}: type preset '{preset}' not in theme.type")
        st.update(theme.type[preset])
    st.update({k: v for k, v in item.items() if k in RUN_KEYS + ("align", "spacing", "anchor")})
    st.setdefault("font", "body")
    st.setdefault("size", 14)
    st.setdefault("color", "ink")
    return st


def norm_lines(item):
    """-> list of paragraphs; each paragraph = list of run dicts."""
    if "text" in item:
        raw = str(item["text"]).split("\n")
    else:
        raw = item["lines"]
    paras = []
    for ln in raw:
        runs = ln if isinstance(ln, list) else [ln]
        paras.append([{"text": r} if isinstance(r, str) else dict(r) for r in runs])
    return paras


def add_text(slide, item, theme, where):
    x, y, w, h = box(item, where)
    st = resolve_style(item, theme, where)
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE  # Slides only honours NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ANCHOR[st.get("anchor", "top")]
    words, measured = 0, []
    for i, runs in enumerate(norm_lines(item)):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[st.get("align", "left")]
        if st.get("spacing"):
            p.line_spacing = float(st["spacing"])
        measured.append([])
        for rd in runs:
            rs = dict(st)
            if rd.get("as"):
                rs.update(theme.type[rd["as"]])
            rs.update({k: v for k, v in rd.items() if k in RUN_KEYS})
            measured[-1].append((rd["text"], theme.font(rs["font"]), rs["size"], bool(rs.get("bold")),
                                 bool(rs.get("italic"))))
            r = p.add_run()
            r.text = rd["text"]
            words += len(rd["text"].split())
            f = r.font
            f.name = theme.font(rs["font"])
            f.size = Pt(rs["size"])
            f.bold = bool(rs.get("bold", False))
            f.italic = bool(rs.get("italic", False))
            if rs.get("underline"):
                f.underline = True
            f.color.rgb = theme.color(rs["color"], where)
    if item.get("rotate"):
        tb.rotation = item["rotate"]
    fit_check(measured, w, h, float(st.get("spacing") or 1.0), where)
    return tb, words


_FONTS = {}


def _font(fam, size, bold, italic):
    from PIL import ImageFont

    key = (fam, size, bold, italic)
    if key not in _FONTS:
        path = gfonts.fetch(fam, 700 if bold else 400, italic) if not FIT_OFF else None
        _FONTS[key] = ImageFont.truetype(str(path), int(size * 4)) if path else None
    return _FONTS[key]


FIT_OFF = False


def fit_check(paras, w, h, spacing, where):
    """Warn when text wraps past its box. Measures with the real Google Font (cached download)."""
    global FIT_OFF
    if FIT_OFF:
        return
    total = unwrapped = 0.0
    for runs in paras:
        tokens, lh = [], 0.0
        for text, fam, size, bold, italic in runs:
            try:
                f = _font(fam, size, bold, italic)
            except OSError:
                f = None
            if f is None:
                if not any("fit check" in x for x in WARN):
                    warn(f"fit check skipped for '{fam}': font not downloadable (offline or not a Google Font)")
                return
            asc, desc = f.getmetrics()
            lh = max(lh, (asc + desc) / 4 / 72 * spacing)
            for word in re.split(r"(\s+)", text):
                if word:
                    tokens.append((word, f.getlength(word) / 4 / 72))
        lines, cur = 1, 0.0
        for word, wd in tokens:
            if word.isspace():
                cur += wd
                continue
            if wd > w + 0.02:
                warn(f"{where}: '{word}' is {wd:.2f} in wide, box is {w:.2f} in. It will break mid-word")
            if cur > 0 and cur + wd > w + 0.02:
                lines, cur = lines + 1, wd
            else:
                cur += wd
        total += lines * (lh or 0.2)
        unwrapped += lh or 0.2
    if total > unwrapped + 0.01 and total > h + 0.15:  # only overflow caused by wrapping
        warn(f"{where}: text wraps to about {total:.2f} in of height, box is {h:.2f} in. "
             f"Shorten, shrink the size, or widen the box")


def strip_theme_style(shape):
    st = shape._element.find(qn("p:style"))
    if st is not None:  # python-pptx default style bakes a drop shadow into Slides
        shape._element.remove(st)


def add_shape(slide, item, theme, where):
    x, y, w, h = box(item, where)
    kind = item["shape"]
    mso = SHAPES.get(kind) or getattr(MSO_SHAPE, str(kind).upper().replace("-", "_"), None)
    if mso is None:
        die(f"{where}: unknown shape '{kind}'. Use one of {sorted(SHAPES)} or an MSO_SHAPE name")
    s = slide.shapes.add_shape(mso, Inches(x), Inches(y), Inches(w), Inches(h))
    strip_theme_style(s)
    if kind == "arch":
        s.adjustments[0] = 0.5
    for i, a in enumerate(item.get("adj", [])):
        s.adjustments[i] = a
    if item.get("fill", "ink") in (None, "none"):
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = theme.color(item.get("fill", "ink"), where)
    if item.get("line"):
        s.line.color.rgb = theme.color(item["line"], where)
        s.line.width = Pt(item.get("line_width", 1.5))
    else:
        s.line.fill.background()
    if item.get("rotate"):
        s.rotation = item["rotate"]
    return s


def add_image(slide, item, base, where):
    x, y, w, h = box(item, where, need_wh=False)
    path = (base / item["image"]).resolve()
    if not path.is_file():
        die(f"{where}: image not found: {path}")
    p = slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                 Inches(w) if w else None, Inches(h) if h else None)
    crop = item.get("crop")
    if crop:
        p.crop_left, p.crop_top, p.crop_right, p.crop_bottom = crop
    if item.get("rotate"):
        p.rotation = item["rotate"]
    return p, path


def add_outline(slide, item, theme, work, where):
    """Outlined (stroked, hollow) text. Slides has no text stroke, so render a transparent PNG."""
    from PIL import Image, ImageDraw, ImageFont

    x, y, w, h = box(item, where, need_wh=False)
    st = resolve_style(item, theme, where)
    fam = theme.font(st["font"])
    ttf = gfonts.fetch(fam, 700 if st.get("bold") else 400, bool(st.get("italic")))
    if not ttf:
        die(f"{where}: could not download Google Font '{fam}' for outline text")
    dpi = 220
    px = int(st["size"] * dpi / 72)
    font = ImageFont.truetype(str(ttf), px)
    stroke = max(1, int(item.get("stroke", 1.6) * dpi / 72))
    text = item["outline"] if isinstance(item["outline"], str) else "\n".join(item["outline"])
    gap = int(px * (float(st.get("spacing", 1.0)) - 1.0))
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = probe.multiline_textbbox((0, 0), text, font=font, stroke_width=stroke, spacing=gap,
                                          align=st.get("align", "left"))
    img = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    rgb = theme.color(st["color"], where)
    col = (rgb[0], rgb[1], rgb[2], 255)
    ImageDraw.Draw(img).multiline_text((2 - l, 2 - t), text, font=font, fill=(0, 0, 0, 0), stroke_width=stroke,
                                       stroke_fill=col, spacing=gap, align=st.get("align", "left"))
    out = work / f"outline_{abs(hash((text, fam, px, str(col)))) % 10**8}.png"
    img.save(out)
    win = img.width / dpi
    if w:  # fit width if given
        win = w
    p = slide.shapes.add_picture(str(out), Inches(x), Inches(y), Inches(win))
    if item.get("rotate"):
        p.rotation = item["rotate"]
    return p


# ---------------------------------------------------------------- transitions
def add_transition(slide, spec):
    if not spec or spec in ("none", "cut"):
        return
    if isinstance(spec, str):
        spec = {"type": spec}
    kind, speed = spec["type"], spec.get("speed", "slow" if spec["type"] == "fade" else "med")
    if speed not in ("slow", "med", "fast"):
        die(f"transition speed must be slow|med|fast, got {speed}")
    if kind == "fade":
        xml = f'<p:transition xmlns:p="{NS_P}" spd="{speed}"><p:fade/></p:transition>'
    elif kind == "push":
        xml = f'<p:transition xmlns:p="{NS_P}" spd="{speed}"><p:push dir="l"/></p:transition>'
    elif kind == "dissolve":  # Slides imports this as a fade through black
        xml = f'<p:transition xmlns:p="{NS_P}" spd="{speed}"><p:dissolve/></p:transition>'
    elif kind in ("flip", "gallery"):
        inner = {"flip": '<p14:flip dir="r"/>', "gallery": '<p14:gallery dir="l"/>'}[kind]
        xml = (f'<mc:AlternateContent xmlns:mc="{NS_MC}"><mc:Choice xmlns:p14="{NS_P14}" Requires="p14">'
               f'<p:transition xmlns:p="{NS_P}" spd="{speed}" p14:dur="1000">{inner}</p:transition></mc:Choice>'
               f'<mc:Fallback><p:transition xmlns:p="{NS_P}" spd="{speed}"><p:fade/></p:transition></mc:Fallback>'
               f'</mc:AlternateContent>')
    else:
        die(f"transition '{kind}' not supported. Use fade | push | flip | gallery | dissolve | none")
    sld = slide._element
    anchor = sld.find(qn("p:clrMapOvr"))
    if anchor is None:
        anchor = sld.find(qn("p:cSld"))
    anchor.addnext(etree.fromstring(xml))


# ---------------------------------------------------------------- builds (OOXML timing)
FX_DEFAULT_MS = {"fade": 600, "fly": 600, "zoom": 450, "spin": 900, "appear": 1}
FX_ALIAS = {"rise": "fly-bottom", "drop": "fly-top", "fly-up": "fly-bottom", "fly-down": "fly-top"}
FLY = {"left": (8, "ppt_x", "0-#ppt_w/2", "#ppt_x"), "right": (2, "ppt_x", "1+#ppt_w/2", "#ppt_x"),
       "top": (1, "ppt_y", "0-#ppt_h/2", "#ppt_y"), "bottom": (4, "ppt_y", "1+#ppt_h/2", "#ppt_y")}


def parse_build(entry, where):
    parts = entry.split() if isinstance(entry, str) else [str(p) for p in entry]
    if len(parts) < 2:
        die(f"{where}: build '{entry}' needs at least 'id effect'")
    sid, fx = parts[0], FX_ALIAS.get(parts[1], parts[1])
    if fx not in ("fade", "zoom", "spin", "appear") and not (fx.startswith("fly-") and fx[4:] in FLY):
        die(f"{where}: effect '{parts[1]}' not supported. Use fade | fly-left|right|top|bottom | zoom | spin | appear")
    ms, mode = FX_DEFAULT_MS[fx.split("-")[0]], "after"
    for p in parts[2:]:
        if p.isdigit():
            ms = int(p)
        elif p in ("after", "with", "click"):
            mode = p
        else:
            die(f"{where}: build '{entry}': unknown token '{p}'")
    return sid, fx, ms, mode


def _vis(i, spid):
    return (f'<p:set><p:cBhvr><p:cTn id="{i}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName>'
            f'</p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>')


def _anim(i, spid, attr, frm, to, dur):
    return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{i}" dur="{dur}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="{frm}"/></p:val></p:tav>'
            f'<p:tav tm="100000"><p:val><p:strVal val="{to}"/></p:val></p:tav></p:tavLst></p:anim>')


def _effect(ids, spid, fx, node, dur):
    a = next(ids)
    if fx == "fade":
        beh = _vis(next(ids), spid) + (
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
        pid, cls, sub = 10, "entr", 0
    elif fx.startswith("fly-"):
        sub, attr, frm, to = FLY[fx[4:]]
        beh = _vis(next(ids), spid) + _anim(next(ids), spid, attr, frm, to, dur)
        pid, cls = 2, "entr"
    elif fx == "appear":
        beh = _vis(next(ids), spid)
        pid, cls, sub = 1, "entr", 0
    elif fx == "zoom":
        beh = (_vis(next(ids), spid) + _anim(next(ids), spid, "ppt_w", "0", "#ppt_w", dur)
               + _anim(next(ids), spid, "ppt_h", "0", "#ppt_h", dur))
        pid, cls, sub = 23, "entr", 16
    else:  # spin
        beh = (f'<p:animRot by="21600000"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}" fill="hold"/>'
               f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>r</p:attrName>'
               f'</p:attrNameLst></p:cBhvr></p:animRot>')
        pid, cls, sub = 8, "emph", 0
    return (f'<p:par><p:cTn id="{a}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold" '
            f'grpId="0" nodeType="{node}"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'<p:childTnLst>{beh}</p:childTnLst></p:cTn></p:par>')


def add_builds(slide, steps):
    """steps: [(shape, fx, ms, mode)]. First group auto-starts on slide open unless its first step is 'click'."""
    groups = []  # {click, pars: [[start_ms, [(spid, fx, node, ms)]]], end}
    for shp, fx, ms, mode in steps:
        if not groups or mode == "click":
            groups.append({"click": mode == "click", "pars": [[0, []]], "end": 0})
            node = "clickEffect" if mode == "click" else "afterEffect"
        elif mode == "with":
            node = "withEffect"
        else:
            g = groups[-1]
            g["pars"].append([g["end"], []])
            node = "afterEffect"
        g = groups[-1]
        g["pars"][-1][1].append((shp.shape_id, fx, node, ms))
        g["end"] = max(g["end"], g["pars"][-1][0] + ms)

    ids = count(3)
    body = []
    for gi, g in enumerate(groups):
        gid = next(ids)
        if gi == 0 and not g["click"]:
            cond = '<p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
        else:
            cond = '<p:cond delay="indefinite"/>'
        pars = []
        for start, effs in g["pars"]:
            pid = next(ids)
            inner = "".join(_effect(ids, spid, fx, node, ms) for spid, fx, node, ms in effs)
            pars.append(f'<p:par><p:cTn id="{pid}" fill="hold"><p:stCondLst><p:cond delay="{start}"/></p:stCondLst>'
                        f'<p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>')
        body.append(f'<p:par><p:cTn id="{gid}" fill="hold"><p:stCondLst>{cond}</p:stCondLst>'
                    f'<p:childTnLst>{"".join(pars)}</p:childTnLst></p:cTn></p:par>')
    seen, bld = set(), []
    for shp, *_ in steps:
        if shp._element.tag == qn("p:sp") and shp.shape_id not in seen:
            seen.add(shp.shape_id)
            bld.append(f'<p:bldP spid="{shp.shape_id}" grpId="0"/>')
    xml = (f'<p:timing xmlns:p="{NS_P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" '
           f'nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" '
           f'nodeType="mainSeq"><p:childTnLst>{"".join(body)}</p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
           + (f'<p:bldLst>{"".join(bld)}</p:bldLst>' if bld else "") + '</p:timing>')
    slide._element.append(etree.fromstring(xml))


# ---------------------------------------------------------------- deck
def build(spec_path, out_path):
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    base = (spec_path.parent / spec.get("assets", ".")).resolve()
    theme = Theme(spec)
    work = Path(tempfile.mkdtemp(prefix="motion-slides-"))

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W_IN), Inches(H_IN)
    blank = prs.slide_layouts[6]
    budget = spec.get("max_words", 40)
    gifs = []

    for si, sd in enumerate(spec["slides"], 1):
        where = f"slide {si}"
        slide = prs.slides.add_slide(blank)
        bg = sd.get("bg", "bg")
        if isinstance(bg, dict) and bg.get("image"):
            p, path = add_image(slide, {"image": bg["image"], "at": [0, 0, W_IN, H_IN]}, base, where + " bg")
            slide.shapes._spTree.remove(p._element)
            slide.shapes._spTree.insert(2, p._element)  # send to back
        else:
            f = slide.background.fill
            f.solid()
            f.fore_color.rgb = theme.color(bg, where + " bg")
        add_transition(slide, sd.get("transition", spec.get("transition")))

        shapes, words = {}, 0
        for ii, item in enumerate(sd.get("items", []), 1):
            iw = f"{where} item {item.get('id', ii)}"
            if "text" in item or "lines" in item:
                shp, n = add_text(slide, item, theme, iw)
                words += n
            elif "image" in item:
                shp, path = add_image(slide, item, base, iw)
                if path.suffix.lower() == ".gif":
                    gifs.append(path)
            elif "shape" in item:
                shp = add_shape(slide, item, theme, iw)
            elif "outline" in item:
                shp = add_outline(slide, item, theme, work, iw)
                words += len(str(item["outline"]).split())
            else:
                die(f"{iw}: item needs one of text | lines | image | shape | outline")
            if item.get("id"):
                if item["id"] in shapes:
                    die(f"{iw}: duplicate id '{item['id']}'")
                shapes[item["id"]] = shp

        steps = []
        for b in sd.get("build", []):
            sid, fx, ms, mode = parse_build(b, where)
            if sid not in shapes:
                die(f"{where}: build '{b}' targets unknown id '{sid}'")
            steps.append((shapes[sid], fx, ms, mode))
        if steps:
            add_builds(slide, steps)
        if sd.get("notes"):
            slide.notes_slide.notes_text_frame.text = sd["notes"]

        cap = sd.get("max_words", budget)
        if words > cap:
            warn(f"{where}: {words} words on the slide (budget {cap}). Cut text: one idea per slide")
        if len(steps) > 10:
            warn(f"{where}: {len(steps)} build steps. Keep the sequence under ~3 s total")

    if len(theme.used_fonts) > 3:
        warn(f"deck uses {len(theme.used_fonts)} font families {sorted(theme.used_fonts)}. Aim for 2-3")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    shutil.rmtree(work, ignore_errors=True)

    size = os.path.getsize(out_path) / 1e6
    gif_mb = sum(os.path.getsize(g) for g in set(gifs)) / 1e6
    print(f"saved {out_path}: {len(spec['slides'])} slides, {size:.1f} MB "
          f"({len(gifs)} GIF placements, {len(set(gifs))} unique, {gif_mb:.1f} MB)")
    print("fonts:", ", ".join(sorted(theme.used_fonts)))
    for w in WARN:
        print("warn:", w)
    if pptx.__version__ != PPTX_TESTED:
        print(f"note: python-pptx {pptx.__version__}; tested with {PPTX_TESTED}. "
              f"If something looks off: python3 -m pip install python-pptx=={PPTX_TESTED}")
    return theme


# ---------------------------------------------------------------- preview
def preview(pptx, outdir, fonts):
    """Static contact sheet: first frame of each GIF, final state of each build."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice or not shutil.which("pdftoppm"):
        print("preview skipped: needs soffice (LibreOffice) and pdftoppm (poppler)")
        return
    from PIL import Image

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    gfonts.install(fonts)
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(pptx)],
                   check=True, capture_output=True)
    pdf = outdir / (Path(pptx).stem + ".pdf")
    for old in outdir.glob("slide-*.png"):
        old.unlink()
    subprocess.run(["pdftoppm", "-r", "96", "-png", str(pdf), str(outdir / "slide")], check=True)
    pages = sorted(outdir.glob("slide-*.png"))
    ims = [Image.open(p).convert("RGB") for p in pages]
    if not ims:
        return
    w, h = ims[0].size
    cols = 2 if len(ims) > 1 else 1
    rows = (len(ims) + cols - 1) // cols
    pad = 16
    sheet = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), (255, 255, 255))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        sheet.paste(im, (pad + c * (w + pad), pad + r * (h + pad)))
    sheet.save(outdir / "contact-sheet.png")
    print(f"preview: {outdir / 'contact-sheet.png'} ({len(ims)} slides)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--preview", metavar="DIR", help="also render a static contact sheet (LibreOffice)")
    ap.add_argument("--no-fit", action="store_true", help="skip the text-fit check (no font downloads)")
    a = ap.parse_args()
    FIT_OFF = a.no_fit
    th = build(a.spec, a.out)
    if a.preview:
        preview(a.out, a.preview, th.used_fonts)
