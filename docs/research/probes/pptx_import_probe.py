"""Build a probe .pptx: one feature per slide, to test Google Slides import fidelity.

Slide map (transition / animation / effect):
 1 fade transition      + Fade entrance (on click)
 2 dissolve transition  + Fly In from left (on click)
 3 push transition      + Zoom entrance (after previous)
 4 p14 flip transition  + Spin emphasis (on click)
 5 p14 gallery trans.   + Wipe entrance (on click)
 6 morph (fade fallback)+ Bounce entrance + motion path
 7 no transition        + gradient fill, outer shadow, glow, soft edge, fonts
 8 no transition        + animated GIF + native bar chart
"""
import copy
import sys
from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

OUT = sys.argv[1]
GIF = sys.argv[2]

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
    "p159": "http://schemas.microsoft.com/office/powerpoint/2015/09/main",
}
P = "{%s}" % NS["p"]

# ---- animated GIF (24 frames, rotating bar) ----
frames = []
for i in range(24):
    im = Image.new("RGB", (320, 180), (12, 12, 20))
    d = ImageDraw.Draw(im)
    x = int(20 + i * 11.5)
    d.rectangle([x, 70, x + 40, 110], fill=(255, 90, 60))
    d.text((10, 10), f"frame {i}", fill=(255, 255, 255))
    frames.append(im)
frames[0].save(GIF, save_all=True, append_images=frames[1:], duration=60, loop=0)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def add_box(slide, text, left, top, w=4, h=1.2, font="Arial", color=(40, 40, 60)):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(*color)
    tf = shp.text_frame
    tf.text = text
    r = tf.paragraphs[0].runs[0]
    r.font.size = Pt(24)
    r.font.name = font
    r.font.color.rgb = RGBColor(255, 255, 255)
    return shp


def set_transition(slide, xml):
    sld = slide._element
    # transition must come after clrMapOvr / cSld and before timing
    frag = etree.fromstring(xml)
    csld = sld.find(P + "cSld")
    clr = sld.find(P + "clrMapOvr")
    anchor = clr if clr is not None else csld
    anchor.addnext(frag)


def effect_par(ctn_id, spid, preset_id, preset_class, subtype, node_type, delay, behaviors):
    return f"""
<p:par xmlns:p="{NS['p']}">
  <p:cTn id="{ctn_id}" presetID="{preset_id}" presetClass="{preset_class}" presetSubtype="{subtype}" fill="hold" grpId="0" nodeType="{node_type}">
    <p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>
    <p:childTnLst>{behaviors}</p:childTnLst>
  </p:cTn>
</p:par>"""


def vis(i, spid):
    return f"""<p:set><p:cBhvr><p:cTn id="{i}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>
<p:to><p:strVal val="visible"/></p:to></p:set>"""


def set_timing(slide, steps):
    """steps: list of (click_group: bool, effect_xml_par, spid). Each click group wraps its effects."""
    ids = iter(range(3, 999))
    click_pars = []
    for eff in steps:
        outer = next(ids)
        inner = next(ids)
        click_pars.append(f"""<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>
<p:childTnLst><p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>
<p:childTnLst>{eff(ids)}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>""")
    bld = "".join(f'<p:bldP spid="{s}" grpId="0" animBg="1"/>' for s in slide._probe_spids)
    xml = f"""<p:timing xmlns:p="{NS['p']}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>
<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{''.join(click_pars)}</p:childTnLst></p:cTn>
<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>
</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>{bld}</p:bldLst></p:timing>"""
    slide._element.append(etree.fromstring(xml))


def fade_in(spid, node="clickEffect", delay=0):
    def f(ids):
        a, b, c = next(ids), next(ids), next(ids)
        beh = vis(b, spid) + f"""<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{c}" dur="500"/>
<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>"""
        return effect_par(a, spid, 10, "entr", 0, node, delay, beh)
    return f


def fly_in_left(spid, node="clickEffect"):
    def f(ids):
        a, b, c, d = next(ids), next(ids), next(ids), next(ids)
        beh = vis(b, spid) + f"""
<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{c}" dur="500" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
<p:attrNameLst><p:attrName>ppt_x</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="0-#ppt_w/2"/></p:val></p:tav>
<p:tav tm="100000"><p:val><p:strVal val="#ppt_x"/></p:val></p:tav></p:tavLst></p:anim>
<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{d}" dur="500" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
<p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav>
<p:tav tm="100000"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav></p:tavLst></p:anim>"""
        return effect_par(a, spid, 2, "entr", 8, node, 0, beh)
    return f


def zoom_in(spid, node="afterEffect"):
    def f(ids):
        a, b, c, d = next(ids), next(ids), next(ids), next(ids)
        beh = vis(b, spid) + f"""
<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{c}" dur="500" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
<p:attrNameLst><p:attrName>ppt_w</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:fltVal val="0"/></p:val></p:tav>
<p:tav tm="100000"><p:val><p:strVal val="#ppt_w"/></p:val></p:tav></p:tavLst></p:anim>
<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{d}" dur="500" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
<p:attrNameLst><p:attrName>ppt_h</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:fltVal val="0"/></p:val></p:tav>
<p:tav tm="100000"><p:val><p:strVal val="#ppt_h"/></p:val></p:tav></p:tavLst></p:anim>"""
        return effect_par(a, spid, 53, "entr", 16, node, 0, beh)
    return f


def spin(spid):
    def f(ids):
        a, b = next(ids), next(ids)
        beh = f"""<p:animRot by="21600000"><p:cBhvr><p:cTn id="{b}" dur="2000" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>"""
        return effect_par(a, spid, 8, "emph", 0, "clickEffect", 0, beh)
    return f


def wipe(spid):
    def f(ids):
        a, b, c = next(ids), next(ids), next(ids)
        beh = vis(b, spid) + f"""<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn id="{c}" dur="500"/>
<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>"""
        return effect_par(a, spid, 22, "entr", 8, "clickEffect", 0, beh)
    return f


def motion_path(spid):
    def f(ids):
        a, b = next(ids), next(ids)
        beh = f"""<p:animMotion origin="layout" path="M 0 0 L 0.25 0.1 E" pathEditMode="relative" ptsTypes="">
<p:cBhvr><p:cTn id="{b}" dur="2000" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>"""
        return effect_par(a, spid, 42, "path", 0, "clickEffect", 0, beh)
    return f


def alt_transition(choice_ns, requires, inner, dur):
    return f"""<mc:AlternateContent xmlns:mc="{NS['mc']}">
<mc:Choice xmlns:p14="{NS['p14']}" xmlns:p159="{NS['p159']}" Requires="{requires}">
<p:transition xmlns:p="{NS['p']}" spd="slow" p14:dur="{dur}">{inner}</p:transition></mc:Choice>
<mc:Fallback><p:transition xmlns:p="{NS['p']}" spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>"""


specs = [
    ("1 Fade transition + Fade-in", f'<p:transition xmlns:p="{NS["p"]}" spd="med"><p:fade/></p:transition>', lambda s: [fade_in(s)]),
    ("2 Dissolve transition + Fly-in-left", f'<p:transition xmlns:p="{NS["p"]}" spd="med"><p:dissolve/></p:transition>', lambda s: [fly_in_left(s)]),
    ("3 Push transition + Zoom (after prev)", f'<p:transition xmlns:p="{NS["p"]}" spd="med"><p:push dir="u"/></p:transition>', lambda s: [zoom_in(s)]),
    ("4 Flip transition + Spin emphasis", alt_transition("p14", "p14", "<p14:flip dir=\"r\"/>", 1000), lambda s: [spin(s)]),
    ("5 Gallery transition + Wipe entrance", alt_transition("p14", "p14", "<p14:gallery dir=\"l\"/>", 1000), lambda s: [wipe(s)]),
    ("6 Morph transition + motion path", alt_transition("p159", "p159", "<p159:morph option=\"byObject\"/>", 2000), lambda s: [fade_in(s), motion_path(s)]),
]

for title, trans, anims in specs:
    s = prs.slides.add_slide(blank)
    shp = add_box(s, title, 1, 1, w=9, h=1.5, color=(30, 30, 80))
    s._probe_spids = [shp.shape_id]
    set_transition(s, trans)
    set_timing(s, anims(shp.shape_id))

# slide 7: effects + fonts
s = prs.slides.add_slide(blank)
g = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.5), Inches(4), Inches(3))
g.fill.gradient()
g.fill.gradient_angle = 45
stops = g.fill.gradient_stops
stops[0].color.rgb = RGBColor(255, 80, 60)
stops[1].color.rgb = RGBColor(60, 40, 200)
g.text_frame.text = "gradient fill"
sh = add_box(s, "outer shadow", 5, 0.5, color=(20, 120, 90))
glow = add_box(s, "glow", 5, 2.2, color=(120, 20, 90))
soft = add_box(s, "soft edges", 5, 3.9, color=(90, 90, 20))
A = "{%s}" % NS["a"]
for shape, eff in [
    (sh, '<a:outerShdw xmlns:a="%s" blurRad="190500" dist="76200" dir="2700000" algn="tl" rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="60000"/></a:srgbClr></a:outerShdw>' % NS["a"]),
    (glow, '<a:glow xmlns:a="%s" rad="228600"><a:srgbClr val="FF00FF"><a:alpha val="60000"/></a:srgbClr></a:glow>' % NS["a"]),
    (soft, '<a:softEdge xmlns:a="%s" rad="127000"/>' % NS["a"]),
]:
    spPr = shape._element.spPr
    el = etree.SubElement(spPr, A + "effectLst")
    el.append(etree.fromstring(eff))
add_box(s, "Playfair Display (Google font)", 0.5, 4.2, w=4.2, font="Playfair Display")
add_box(s, "Helvetica Neue (not Google)", 0.5, 5.6, w=4.2, font="Helvetica Neue")
add_box(s, "Space Grotesk (Google font)", 9.3, 0.5, w=3.8, font="Space Grotesk")

# slide 8: animated gif + native chart
s = prs.slides.add_slide(blank)
s.shapes.add_picture(GIF, Inches(0.5), Inches(0.5), Inches(5.33), Inches(3))
cd = CategoryChartData()
cd.categories = ["Q1", "Q2", "Q3", "Q4"]
cd.add_series("Revenue", (12, 18, 26, 40))
s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.5), Inches(0.5), Inches(6), Inches(4.5), cd)

prs.save(OUT)
print("saved", OUT)
