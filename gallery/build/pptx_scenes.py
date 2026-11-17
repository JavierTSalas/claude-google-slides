"""Read a .pptx into preview scenes, so player.html can replay any deck built for Google Slides.

Usage: python3 pptx_scenes.py deck.pptx out/ref/<name>
Writes <out>/scenes.js (window.SCENES, window.GIFS) and <out>/media/ (images, GIF frames).

Covers what the decks here use: solid backgrounds, text boxes, rect/roundRect/ellipse/star5 shapes,
pictures (PNG, JPEG, animated GIF), fade/push transitions, and auto-chained fade/fly/zoom/spin builds.
"""
import json, os, re, subprocess, sys, zipfile
from lxml import etree

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
EMU = 914400
FLY = {"8": "fly-left", "2": "fly-right", "1": "fly-top", "4": "fly-bottom"}


def q(el, path):
    return el.find(path, NS)


def color(el):
    c = el.find(".//a:srgbClr", NS) if el is not None else None
    return c.get("val").upper() if c is not None else None


def xfrm(sp):
    x = q(sp, ".//a:xfrm")
    off, ext = q(x, "a:off"), q(x, "a:ext")
    return {"x": int(off.get("x")) / EMU, "y": int(off.get("y")) / EMU, "w": int(ext.get("cx")) / EMU,
            "h": int(ext.get("cy")) / EMU, "rot": int(x.get("rot", 0)) / 60000}


def paras(tx):
    out = []
    for p in tx.findall("a:p", NS):
        ppr = q(p, "a:pPr")
        algn = {"ctr": "c", "r": "r"}.get(ppr.get("algn") if ppr is not None else None, "l")
        sp = q(p, "a:pPr/a:lnSpc/a:spcPct")
        runs = []
        for r in p.findall("a:r", NS):
            rpr = q(r, "a:rPr")
            g = (lambda k, d=None: rpr.get(k, d)) if rpr is not None else (lambda k, d=None: d)
            lat = q(rpr, "a:latin") if rpr is not None else None
            runs.append({"t": q(r, "a:t").text or "", "font": lat.get("typeface") if lat is not None else "Arial",
                         "size": int(g("sz", 1800)) / 100, "bold": g("b") == "1", "italic": g("i") == "1",
                         "color": color(q(rpr, "a:solidFill")) if rpr is not None else "000000",
                         "spc": int(g("spc", 0)) / 100})
        if not runs:  # empty line keeps its height
            end = q(p, "a:endParaRPr")
            runs = [{"t": " ", "font": "Arial", "size": int(end.get("sz", 1800)) / 100 if end is not None else 18,
                     "bold": False, "italic": False, "color": "000000", "spc": 0}]
        out.append({"align": algn, "spacing": int(sp.get("val")) / 100000 if sp is not None else 1.0, "runs": runs})
    return out


def builds(sld):
    root = sld.find(".//p:timing//p:cTn[@nodeType='mainSeq']", NS)
    if root is None:
        return []
    out = []
    for grp in root.iterfind("p:childTnLst/p:par/p:cTn/p:childTnLst/p:par/p:cTn", NS):
        start = int(q(grp, "p:stCondLst/p:cond").get("delay", 0))
        for eff in grp.iterfind("p:childTnLst/p:par/p:cTn", NS):
            pid, cls, sub = eff.get("presetID"), eff.get("presetClass"), eff.get("presetSubtype")
            kind = ("fade" if pid == "10" else FLY.get(sub, "fly-bottom") if pid == "2" else "zoom" if pid == "23"
                    else "spin" if pid == "8" and cls == "emph" else "appear")
            durs = [int(c.get("dur")) for c in eff.iterfind(".//p:cBhvr/p:cTn", NS) if c.get("dur", "").isdigit()]
            spid = q(eff, ".//p:spTgt").get("spid")
            out.append({"id": int(spid), "effect": kind, "start": start, "dur": max(durs or [1])})
    return out


def main(pptx, out):
    media = os.path.join(out, "media")
    os.makedirs(media, exist_ok=True)
    z = zipfile.ZipFile(pptx)
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    sz = q(pres, "p:sldSz")
    scale = 10 / (int(sz.get("cx")) / EMU)  # player stage is 10 in wide
    prels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in prels}
    scenes, gifs = [], {}
    for sid in pres.iterfind("p:sldIdLst/p:sldId", NS):
        path = "ppt/" + target[sid.get(f"{{{NS['r']}}}id")]
        sld = etree.fromstring(z.read(path))
        rels_path = re.sub(r"slides/(slide\d+\.xml)", r"slides/_rels/\1.rels", path)
        rels = {r.get("Id"): os.path.normpath(os.path.join(os.path.dirname(path), r.get("Target")))
                for r in etree.fromstring(z.read(rels_path))}
        tr = q(sld, "p:transition")
        kind = None
        if tr is not None and len(tr):
            kind = {"fade": "fade", "push": "push"}.get(etree.QName(tr[0]).localname, "fade")
        scene = {"bg": color(q(sld, "p:cSld/p:bg")) or "FFFFFF", "transition": kind, "elements": [],
                 "builds": builds(sld)}
        for el in q(sld, "p:cSld/p:spTree"):
            tag = etree.QName(el).localname
            if tag not in ("sp", "pic", "cxnSp"):
                continue
            cnv = q(el, ".//p:cNvPr")
            g = {k: round(v * scale, 4) if k != "rot" else v for k, v in xfrm(el).items()}
            e = {"id": int(cnv.get("id")), **g}
            if tag == "pic":
                name = rels[q(el, ".//a:blip").get(f"{{{NS['r']}}}embed")]
                fn = os.path.basename(name)
                data = z.read(name)
                open(os.path.join(media, fn), "wb").write(data)
                if fn.lower().endswith(".gif"):
                    key = os.path.splitext(fn)[0]
                    fdir = os.path.join(media, key)
                    if key not in gifs:
                        os.makedirs(fdir, exist_ok=True)
                        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(media, fn),
                                        os.path.join(fdir, "%04d.png")], check=True)
                        rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                               "stream=r_frame_rate", "-of", "csv=p=0", os.path.join(media, fn)],
                                              capture_output=True, text=True).stdout.strip().split("/")
                        gifs[key] = {"fps": int(rate[0]) / int(rate[1]), "n": len(os.listdir(fdir)), "dir": os.path.relpath(fdir, os.path.dirname(os.path.abspath(__file__)))}
                    e.update(type="gif", gif=key)
                else:
                    e.update(type="image", src=os.path.relpath(os.path.join(media, fn), os.path.dirname(os.path.abspath(__file__))))
            else:
                spr = q(el, "p:spPr")
                geom = q(spr, "a:prstGeom")
                prst = geom.get("prst") if geom is not None else "rect"
                e["type"] = {"ellipse": "ellipse", "star5": "star"}.get(prst, "rect")
                fill = q(spr, "a:solidFill")
                e["fill"] = color(fill) if fill is not None else None
                if prst == "roundRect":
                    gd = q(geom, "a:avLst/a:gd")
                    adj = int(gd.get("fmla").split()[-1]) if gd is not None else 16667
                    e["radius"] = round(adj / 100000 * min(g["w"], g["h"]), 4)
                ln = q(spr, "a:ln")
                if ln is not None and q(ln, "a:solidFill") is not None:
                    e["line"] = {"color": color(q(ln, "a:solidFill")), "w": int(ln.get("w", 12700)) / EMU * scale}
                if tag == "cxnSp":  # a straight line: draw it as a thin bar
                    w = e.get("line", {}).get("w", 1 / 72)
                    e.update(type="rect", fill=e.get("line", {}).get("color", "000000"), h=max(e["h"], w), line=None)
                tx = q(el, "p:txBody")
                if tx is not None and "".join(tx.itertext()).strip():
                    bp = q(tx, "a:bodyPr")
                    ins = [int(bp.get(k, d)) / EMU * scale for k, d in (("lIns", 91440), ("tIns", 45720), ("rIns", 91440), ("bIns", 45720))]
                    e.update(paras=paras(tx), anchor={"ctr": "m", "b": "b"}.get(bp.get("anchor"), "t"), inset=ins)
                    for p in e["paras"]:
                        for r in p["runs"]:
                            r["size"] *= scale
                            r["spc"] *= scale
                    if not e["fill"] and not e.get("line"):
                        e["type"] = "text"
            scene["elements"].append(e)
        scenes.append(scene)
    with open(os.path.join(out, "scenes.js"), "w") as f:
        f.write("window.SCENES = " + json.dumps(scenes) + ";\nwindow.GIFS = " + json.dumps(gifs) + ";\n")
    print(pptx, "->", out, len(scenes), "slides,", len(gifs), "gif loops")


if __name__ == "__main__":
    main(*sys.argv[1:3])
