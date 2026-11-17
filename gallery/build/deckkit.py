"""Tiny deck DSL. One call writes a native .pptx shape AND a preview scene.

The .pptx imports into Google Slides with builds and transitions intact.
The scene JSON drives player.html, which replays the same builds for previews.
"""
import json
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

PNS = "http://schemas.openxmlformats.org/presentationml/2006/main"
EMU_IN = 914400
SHAPES = {"rect": MSO_SHAPE.RECTANGLE, "ellipse": MSO_SHAPE.OVAL, "star": MSO_SHAPE.STAR_5_POINT}
ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


def _in(emu):
    return round(emu / EMU_IN, 4)


class Deck:
    def __init__(self, assets_dir):
        self.assets = assets_dir
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(10), Inches(5.625)
        self.scenes = []

    # ---------- slides ----------
    def slide(self, bg, transition=None):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        f = s.background.fill
        f.solid()
        f.fore_color.rgb = RGBColor.from_string(bg)
        if transition:
            xml = {
                "fade": f'<p:transition xmlns:p="{PNS}" spd="slow"><p:fade/></p:transition>',
                "push": f'<p:transition xmlns:p="{PNS}" spd="med"><p:push dir="l"/></p:transition>',
            }[transition]
            s._element.find(qn("p:clrMapOvr")).addnext(etree.fromstring(xml))
        self.cur = s
        self.scene = {"bg": bg, "transition": transition, "elements": [], "builds": []}
        self.scenes.append(self.scene)
        return s

    def _record(self, shp, kind, rot, **extra):
        el = {"id": shp.shape_id, "type": kind, "x": _in(shp.left), "y": _in(shp.top),
              "w": _in(shp.width), "h": _in(shp.height), "rot": rot, **extra}
        self.scene["elements"].append(el)
        return shp

    # ---------- elements ----------
    def text(self, x, y, w, h, lines, font, size, color, *, bold=False, italic=False,
             align="l", spacing=None, anchor="t", rot=0):
        """lines: list of str or (str, overrides). Overrides: font size color bold italic."""
        tb = self.cur.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = ANCHOR[anchor]
        paras = []
        for i, ln in enumerate(lines):
            s, o = (ln, {}) if isinstance(ln, str) else ln
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = ALIGN[align]
            if spacing:
                p.line_spacing = spacing
            r = p.add_run()
            r.text = s
            run = {"t": s, "font": o.get("font", font), "size": o.get("size", size),
                   "bold": o.get("bold", bold), "italic": o.get("italic", italic),
                   "color": o.get("color", color)}
            f = r.font
            f.name, f.size, f.bold, f.italic = run["font"], Pt(run["size"]), run["bold"], run["italic"]
            f.color.rgb = RGBColor.from_string(run["color"])
            paras.append({"align": align, "spacing": spacing or 1.0, "runs": [run]})
        if rot:
            tb.rotation = rot
        return self._record(tb, "text", rot, paras=paras, anchor=anchor)

    def shape(self, kind, x, y, w, h, color, rot=0):
        s = self.cur.shapes.add_shape(SHAPES[kind], Inches(x), Inches(y), Inches(w), Inches(h))
        st = s._element.find(qn("p:style"))
        if st is not None:  # theme style bakes a drop shadow into Slides
            s._element.remove(st)
        s.fill.solid()
        s.fill.fore_color.rgb = RGBColor.from_string(color)
        s.line.fill.background()
        if rot:
            s.rotation = rot
        return self._record(s, kind, rot, fill=color)

    def pic(self, name, x, y, w=None, h=None, rot=0):
        p = self.cur.shapes.add_picture(f"{self.assets}/{name}", Inches(x), Inches(y),
                                        Inches(w) if w else None, Inches(h) if h else None)
        if rot:
            p.rotation = rot
        return self._record(p, "gif" if name.endswith(".gif") else "image", rot, src=name)

    # ---------- builds ----------
    def builds(self, steps):
        """steps: (shape, effect, mode, ms). effect: fade | fly-left/right/top/bottom | zoom | spin.
        mode: 'after' previous or 'with' previous. The chain auto-starts when the slide opens."""
        self.scene["builds"] = [{"id": s.shape_id, "effect": k, "mode": m, "dur": d} for s, k, m, d in steps]
        self.cur._element.append(etree.fromstring(_timing_xml(steps)))

    def save(self, pptx_path, scenes_path):
        self.prs.save(pptx_path)
        with open(scenes_path, "w") as f:
            f.write("window.SCENES = " + json.dumps(self.scenes, indent=1) + ";\n")


# ---------- OOXML timing ----------
FLY = {"left": (8, "ppt_x", "0-#ppt_w/2", "#ppt_x"), "right": (2, "ppt_x", "1+#ppt_w/2", "#ppt_x"),
       "top": (1, "ppt_y", "0-#ppt_h/2", "#ppt_y"), "bottom": (4, "ppt_y", "1+#ppt_h/2", "#ppt_y")}


def _vis(i, spid):
    return (f'<p:set><p:cBhvr><p:cTn id="{i}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>')


def _anim(i, spid, attr, frm, to, dur):
    return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="{i}" dur="{dur}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:tavLst><p:tav tm="0"><p:val><p:strVal val="{frm}"/></p:val></p:tav>'
            f'<p:tav tm="100000"><p:val><p:strVal val="{to}"/></p:val></p:tav></p:tavLst></p:anim>')


def _effect(ids, spid, kind, node, dur):
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
    else:
        raise ValueError(kind)
    return (f'<p:par><p:cTn id="{a}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold" grpId="0" nodeType="{node}">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{beh}</p:childTnLst></p:cTn></p:par>')


def _timing_xml(steps):
    ids = iter(range(4, 9999))
    groups, end = [], 0
    for shp, kind, mode, dur in steps:
        if mode == "after" or not groups:
            groups.append([end, []])
            node = "afterEffect"
        else:
            node = "withEffect"
        groups[-1][1].append(_effect(ids, shp.shape_id, kind, node, dur))
        end = max(end, groups[-1][0] + dur)
    inner = "".join(
        f'<p:par><p:cTn id="{next(ids)}" fill="hold"><p:stCondLst><p:cond delay="{start}"/></p:stCondLst>'
        f'<p:childTnLst>{"".join(effs)}</p:childTnLst></p:cTn></p:par>' for start, effs in groups)
    bld = "".join(f'<p:bldP spid="{s.shape_id}" grpId="0"/>' for s, *_ in steps if s._element.tag == qn("p:sp"))
    return (f'<p:timing xmlns:p="{PNS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            f'<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>'
            f'<p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn>'
            f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            f'</p:childTnLst></p:cTn></p:par></p:tnLst>' + (f'<p:bldLst>{bld}</p:bldLst>' if bld else '') + '</p:timing>')
