"""Build the 4-slide sample deck as .pptx for Google Slides import.

Native: text, shapes, rotation, fonts, builds (OOXML timing), transitions.
Rendered: GIF loops from HyperFrames (badge, window light, orbits), outline-text PNG.
"""
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

OUT, ASSETS = sys.argv[1], sys.argv[2]
PNS = "http://schemas.openxmlformats.org/presentationml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"

# palette
GREEN = "2F4B2B"   # matches rendered GIF ground exactly
PINK = "EBA6BD"
CREAM = "F1EBE1"
TERRA = "B5462B"
INK = "1E1A16"
BODY = "4A4038"
YELLOW = "FFD23F"
HOTPINK = "FF3D7F"
BLUE = "2B3BFF"
BLACK = "141414"
WHITE = "FFFFFF"

SERIF, MONO, SANS, POSTER = "Instrument Serif", "DM Mono", "Instrument Sans", "Anton"

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)
BLANK = prs.slide_layouts[6]


def rgb(h):
    return RGBColor.from_string(h)


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(color)


def text(slide, x, y, w, h, lines, font, size, color, *, bold=False, italic=False,
         align=PP_ALIGN.LEFT, spacing=None, anchor=MSO_ANCHOR.TOP, rot=0):
    """lines: list of str, or list of (str, dict overrides)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, ln in enumerate(lines):
        s, o = (ln, {}) if isinstance(ln, str) else ln
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing:
            p.line_spacing = spacing
        r = p.add_run()
        r.text = s
        f = r.font
        f.name = o.get("font", font)
        f.size = Pt(o.get("size", size))
        f.bold = o.get("bold", bold)
        f.italic = o.get("italic", italic)
        f.color.rgb = rgb(o.get("color", color))
    if rot:
        tb.rotation = rot
    return tb


def block(slide, kind, x, y, w, h, color, rot=0):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    st = s._element.find(qn("p:style"))
    if st is not None:  # drop theme style: it bakes a drop shadow into Slides
        s._element.remove(st)
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(color)
    s.line.fill.background()
    if rot:
        s.rotation = rot
    return s


def pic(slide, path, x, y, w=None, h=None, rot=0):
    p = slide.shapes.add_picture(path, Inches(x), Inches(y),
                                 Inches(w) if w else None, Inches(h) if h else None)
    if rot:
        p.rotation = rot
    return p


# ---------- transitions ----------
def transition(slide, kind):
    xml = {
        "fade": f'<p:transition xmlns:p="{PNS}" spd="slow"><p:fade/></p:transition>',
        "push": f'<p:transition xmlns:p="{PNS}" spd="med"><p:push dir="l"/></p:transition>',
    }[kind]
    sld = slide._element
    sld.find(qn("p:clrMapOvr")).addnext(etree.fromstring(xml))


# ---------- builds (auto-start chain, "after previous" / "with previous") ----------
def _vis(i, spid):
    return (f'<p:set><p:cBhvr><p:cTn id="{i}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>')


def _anim(i, spid, attr, frm, to, dur):
    return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{i}" dur="{dur}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:tavLst><p:tav tm="0"><p:val><p:strVal val="{frm}"/></p:val></p:tav>'
            f'<p:tav tm="100000"><p:val><p:strVal val="{to}"/></p:val></p:tav></p:tavLst></p:anim>')


FLY = {"left": (8, "ppt_x", "0-#ppt_w/2", "#ppt_x"), "right": (2, "ppt_x", "1+#ppt_w/2", "#ppt_x"),
       "top": (1, "ppt_y", "0-#ppt_h/2", "#ppt_y"), "bottom": (4, "ppt_y", "1+#ppt_h/2", "#ppt_y")}


def effect(ids, spid, kind, node, dur):
    a = next(ids)
    if kind == "fade":
        b, c = next(ids), next(ids)
        beh = _vis(b, spid) + (f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{c}" dur="{dur}"/>'
                               f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
        pid, cls, sub = 10, "entr", 0
    elif kind.startswith("fly-"):
        sub, attr, frm, to = FLY[kind[4:]]
        b, c = next(ids), next(ids)
        beh = _vis(b, spid) + _anim(c, spid, attr, frm, to, dur)
        pid, cls = 2, "entr"
    elif kind == "zoom":
        b, c, d = next(ids), next(ids), next(ids)
        beh = _vis(b, spid) + _anim(c, spid, "ppt_w", "0", "#ppt_w", dur) + _anim(d, spid, "ppt_h", "0", "#ppt_h", dur)
        pid, cls, sub = 23, "entr", 16
    elif kind == "spin":
        b = next(ids)
        beh = (f'<p:animRot by="21600000"><p:cBhvr><p:cTn id="{b}" dur="{dur}" fill="hold"/>'
               f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')
        pid, cls, sub = 8, "emph", 0
    return (f'<p:par><p:cTn id="{a}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold" grpId="0" nodeType="{node}">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{beh}</p:childTnLst></p:cTn></p:par>')


def builds(slide, steps):
    """steps: list of (shape, kind, mode, dur_ms); mode = 'after' | 'with'. Auto-starts on slide open."""
    ids = iter(range(4, 9999))
    groups, end = [], 0
    for shp, kind, mode, dur in steps:
        if mode == "after" or not groups:
            groups.append([end, []])
            node = "afterEffect"
        else:
            node = "withEffect"
        groups[-1][1].append(effect(ids, shp.shape_id, kind, node, dur))
        end = max(end, groups[-1][0] + dur)
    inner = "".join(
        f'<p:par><p:cTn id="{next(ids)}" fill="hold"><p:stCondLst><p:cond delay="{start}"/></p:stCondLst>'
        f'<p:childTnLst>{"".join(effs)}</p:childTnLst></p:cTn></p:par>' for start, effs in groups)
    bld = "".join(f'<p:bldP spid="{s.shape_id}" grpId="0"/>' for s, *_ in steps if s._element.tag == qn("p:sp"))
    xml = (f'<p:timing xmlns:p="{PNS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
           f'<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>'
           f'<p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>'
           f'</p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           f'</p:childTnLst></p:cTn></p:par></p:tnLst>' + (f'<p:bldLst>{bld}</p:bldLst>' if bld else '') + '</p:timing>')
    slide._element.append(etree.fromstring(xml))


A = lambda n: f"{ASSETS}/{n}"

# ===== Slide 1: title (style #3) =====
s = prs.slides.add_slide(BLANK)
bg(s, GREEN)
pic(s, A("badge.gif"), 7.9, 0.32, w=1.55)
l1 = text(s, 0.52, 0.95, 7.0, 1.35, ["Decks"], SERIF, 104, PINK, spacing=0.9)
l2 = text(s, 0.52, 2.12, 7.0, 1.35, ["that"], SERIF, 104, PINK, spacing=0.9)
l3 = text(s, 0.52, 3.29, 7.0, 1.35, ["move."], SERIF, 104, PINK, italic=True, spacing=0.9)
text(s, 6.4, 5.08, 3.0, 0.25, ["NOV 2026"], MONO, 9, PINK, align=PP_ALIGN.RIGHT)
builds(s, [(l1, "fade", "after", 600), (l2, "fade", "after", 600), (l3, "fly-bottom", "after", 700)])

# ===== Slide 2: content (style #7) =====
s = prs.slides.add_slide(BLANK)
bg(s, CREAM)
transition(s, "fade")
pic(s, A("light.gif"), 0.45, 0.31, h=5.0)
block(s, MSO_SHAPE.RECTANGLE, 4.9, 0.78, 0.55, 0.03, TERRA)
text(s, 4.9, 0.9, 4.4, 0.3, ["HOW IT WORKS"], SANS, 10, TERRA, bold=True)
h = text(s, 4.9, 1.2, 4.6, 1.4, ["Native slides.", ("Rendered light.", {"italic": True})], SERIF, 40, INK, spacing=0.95)
b = text(s, 4.9, 2.65, 4.3, 0.9, ["Layout and text are real Google Slides objects. Motion is built in HTML, "
                                  "rendered to a loop, and placed like any image."], SANS, 12, BODY, spacing=1.15)
steps = []
for i, (n, label, sub) in enumerate([("01", "Structure", "Slides API"), ("02", "Motion", "HyperFrames → GIF"), ("03", "Builds", "Native fade + fly")]):
    x = 4.9 + i * 1.55
    steps.append(text(s, x, 3.75, 1.45, 1.2, [(n, {"font": SERIF, "size": 30, "color": TERRA}),
                                              (label, {"font": SANS, "size": 12, "bold": True, "color": INK}),
                                              (sub, {"font": MONO, "size": 9, "color": BODY})], SANS, 12, INK, spacing=1.05))
builds(s, [(h, "fade", "after", 600), (b, "fade", "after", 500)] + [(st, "fly-bottom", "after", 450) for st in steps])

# ===== Slide 3: kinetic poster (style #8) =====
s = prs.slides.add_slide(BLANK)
bg(s, YELLOW)
transition(s, "push")
pinkb = block(s, MSO_SHAPE.RECTANGLE, -0.45, 1.75, 6.4, 4.6, HOTPINK, rot=-5)
blueb = block(s, MSO_SHAPE.RECTANGLE, 6.05, -0.5, 4.5, 2.95, BLUE, rot=6)
blackb = block(s, MSO_SHAPE.RECTANGLE, 6.75, 3.3, 3.9, 2.7, BLACK, rot=-4)
decks = text(s, 0.3, -0.42, 6.2, 2.3, ["DECKS"], POSTER, 150, BLACK, spacing=0.85)
tm = text(s, 0.55, 2.2, 5.4, 3.0, ["THAT", "MOVE"], POSTER, 104, YELLOW, spacing=0.82, rot=-5)
outline = pic(s, A("outline_noplugins.png"), 6.6, 0.18, w=2.25, rot=6)
live = text(s, 6.62, 1.8, 3.2, 0.3, ["LIVE IN GOOGLE SLIDES"], SANS, 11, WHITE, bold=True, rot=6)
native = text(s, 7.15, 3.72, 3.2, 1.6, ["100%", "NATIVE"], POSTER, 46, HOTPINK, spacing=0.85, rot=-4)
star = block(s, MSO_SHAPE.STAR_5_POINT, 5.35, 1.55, 1.0, 1.0, BLACK, rot=12)
text(s, 0.6, 5.12, 4.5, 0.25, ["OPENER STYLE  ·  KINETIC POSTER"], SANS, 9, WHITE, bold=True, rot=-5)
builds(s, [(decks, "fly-top", "after", 450), (pinkb, "fly-left", "after", 450), (tm, "zoom", "after", 450),
           (blueb, "fly-top", "after", 400), (outline, "fade", "after", 400), (live, "fade", "with", 400),
           (blackb, "fly-right", "after", 400), (native, "zoom", "after", 400), (star, "spin", "after", 900)])

# ===== Slide 4: rendered motion hero =====
s = prs.slides.add_slide(BLANK)
bg(s, GREEN)
transition(s, "fade")
pic(s, A("orbits.gif"), 0.7, 0, w=10, h=5.625)
text(s, 0.6, 0.6, 4.0, 0.3, ["RENDERED MOTION"], MONO, 10, PINK)
h1 = text(s, 0.55, 1.45, 5.0, 0.95, ["Rendered once."], SERIF, 54, CREAM)
h2 = text(s, 0.55, 2.3, 5.0, 0.95, ["Plays forever."], SERIF, 54, PINK, italic=True)
body = text(s, 0.6, 3.55, 3.6, 0.9, ["HyperFrames → GIF → Google Slides.", "240 frames. 3 MB. Loops on its own."], MONO, 9, CREAM, spacing=1.3)
builds(s, [(h1, "fade", "after", 700), (h2, "fade", "after", 700), (body, "fade", "after", 500)])

prs.save(OUT)
print("saved", OUT)
