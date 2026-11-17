// Web half of probe_reference.py. Usage: node probe_web.mjs <url-or-html> <out_dir> [pages]
// Screenshots each slide or screen, then measures computed fonts, colors and CSS motion.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const { chromium } = createRequire(import.meta.url)("playwright"); // CJS require honors NODE_PATH and global installs

const [src, out, pagesArg] = process.argv.slice(2);
const N = Number(pagesArg || 8);
const url = /^https?:/.test(src) ? src : "file://" + path.resolve(src);
fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(url, { waitUntil: "networkidle", timeout: 45000 }).catch(() => {});
await page.waitForTimeout(1500);

const anims = [];
const grabAnims = () =>
  page.evaluate(() =>
    document.getAnimations().map((a) => {
      const t = a.effect?.getTiming?.() || {};
      return {
        name: a.animationName || a.transitionProperty || a.constructor.name,
        duration_ms: typeof t.duration === "number" ? Math.round(t.duration) : null,
        delay_ms: Math.round(t.delay || 0),
        easing: t.easing,
        iterations: t.iterations === Infinity ? "infinite" : t.iterations,
      };
    })
  );
anims.push(...(await grabAnims()));

// Screens: arrow-key through a deck; fall back to scrolling a page.
const hash = (b) => crypto.createHash("md5").update(b).digest("hex");
let prev = null;
let mode = "keys";
for (let i = 0; i < N; i++) {
  const buf = await page.screenshot();
  const h = hash(buf);
  if (h === prev) {
    if (mode === "keys") {
      mode = "scroll";
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      await page.waitForTimeout(900);
      i--;
      prev = h;
      continue;
    }
    break;
  }
  fs.writeFileSync(path.join(out, `shot-${String(i + 1).padStart(2, "0")}.png`), buf);
  prev = h;
  if (mode === "keys") await page.keyboard.press("ArrowRight");
  else await page.evaluate(() => window.scrollBy(0, window.innerHeight));
  await page.waitForTimeout(120);
  anims.push(...(await grabAnims())); // catches slide-transition animations mid-flight
  await page.waitForTimeout(1100);
}

const facts = await page.evaluate(() => {
  const fam = (s) => s.split(",")[0].replace(/["']/g, "").trim();
  const fonts = {}, textCols = {}, bgCols = {};
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode.textContent.trim();
    const el = walker.currentNode.parentElement;
    if (!t || !el) continue;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const px = parseFloat(cs.fontSize);
    const k = `${fam(cs.fontFamily)}|${cs.fontWeight}|${cs.fontStyle}`;
    const w = t.length * px * px;
    const f = (fonts[k] ||= { family: fam(cs.fontFamily), weight: +cs.fontWeight, style: cs.fontStyle, weight_sum: 0, max_px: 0, min_px: 1e9, transforms: {}, tracking_em: {}, sample: t.slice(0, 40) });
    f.weight_sum += w;
    f.max_px = Math.max(f.max_px, px);
    f.min_px = Math.min(f.min_px, px);
    f.transforms[cs.textTransform] = (f.transforms[cs.textTransform] || 0) + t.length;
    const ls = cs.letterSpacing === "normal" ? 0 : Math.round((parseFloat(cs.letterSpacing) / px) * 100) / 100;
    f.tracking_em[ls] = (f.tracking_em[ls] || 0) + t.length;
    textCols[cs.color] = (textCols[cs.color] || 0) + t.length;
  }
  for (const el of document.querySelectorAll("body, body *")) {
    const cs = getComputedStyle(el);
    const c = cs.backgroundColor;
    if (!c || c === "rgba(0, 0, 0, 0)" || c === "transparent") continue;
    const r = el.getBoundingClientRect();
    bgCols[c] = (bgCols[c] || 0) + r.width * r.height;
  }
  const css = {};
  const keyframes = new Set();
  const visit = (rules) => {
    for (const r of rules) {
      if (r.cssRules && !(r instanceof CSSKeyframesRule)) visit(r.cssRules);
      if (r instanceof CSSKeyframesRule) keyframes.add(r.name);
      const s = r.style;
      if (!s) continue;
      for (const p of ["transition-duration", "transition-timing-function", "animation-duration", "animation-timing-function", "animation-name", "transition-property"]) {
        const v = s.getPropertyValue(p);
        if (v) css[`${p}: ${v}`] = (css[`${p}: ${v}`] || 0) + 1;
      }
    }
  };
  for (const sh of document.styleSheets) {
    try { visit(sh.cssRules); } catch (e) { /* cross-origin sheet */ }
  }
  const rootVars = {};
  const rs = getComputedStyle(document.documentElement);
  for (const sh of document.styleSheets) {
    try {
      for (const r of sh.cssRules) {
        if (r.selectorText === ":root" && r.style) for (const p of r.style) if (p.startsWith("--")) rootVars[p] = rs.getPropertyValue(p).trim();
      }
    } catch (e) {}
  }
  const gfonts = [...document.querySelectorAll('link[href*="fonts.googleapis"]')].flatMap((l) =>
    [...new URL(l.href).searchParams.getAll("family")].map((x) => x.split(":")[0].replace(/\+/g, " ")));
  const faces = [...document.fonts].map((f) => ({ family: f.family.replace(/["']/g, ""), weight: f.weight, style: f.style, status: f.status }));
  return { fonts, textCols, bgCols, css, keyframes: [...keyframes], rootVars, gfonts, faces, title: document.title };
});
await browser.close();

const sortObj = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]);
const tot = Object.values(facts.fonts).reduce((s, f) => s + f.weight_sum, 0) || 1;
const toHex = (c) => {
  const m = c.match(/\d+(\.\d+)?/g);
  if (!m) return c;
  const [r, g, b, a] = m.map(Number);
  return "#" + [r, g, b].map((x) => x.toString(16).padStart(2, "0")).join("").toUpperCase() + (a !== undefined && a < 1 ? ` @${a}` : "");
};
const animSummary = {};
for (const a of anims) {
  const k = `${a.duration_ms}ms ${a.easing}${a.iterations === "infinite" ? " loop" : ""}`;
  animSummary[k] = (animSummary[k] || 0) + 1;
}
const result = {
  title: facts.title,
  fonts: Object.values(facts.fonts)
    .map((f) => ({ ...f, share: Math.round((f.weight_sum / tot) * 1000) / 1000, weight_sum: undefined,
      // a 1920 px wide screen maps to a 10 in (720 pt) slide
      pt_on_slide: [Math.round(f.min_px * 0.375 * 10) / 10, Math.round(f.max_px * 0.375 * 10) / 10] }))
    .sort((a, b) => b.share - a.share)
    .slice(0, 14),
  google_fonts_requested: [...new Set(facts.gfonts)],
  font_faces: facts.faces,
  fonts_not_loaded: [...new Set(facts.gfonts)].filter((g) => !facts.faces.some((f) => f.family === g && f.status === "loaded")),
  text_colors: sortObj(facts.textCols).slice(0, 10).map(([c, n]) => ({ hex: toHex(c), chars: n })),
  background_colors: sortObj(facts.bgCols).slice(0, 10).map(([c, a]) => ({ hex: toHex(c), area_px: Math.round(a) })),
  css_root_vars: facts.rootVars,
  css_motion_decls: sortObj(facts.css).slice(0, 30).map(([k, n]) => ({ decl: k, count: n })),
  keyframes: facts.keyframes,
  live_animations: sortObj(animSummary).slice(0, 20).map(([k, n]) => ({ timing: k, count: n })),
  screens_mode: mode,
  note: "fonts: share is weighted by chars x size^2 (visual area). Screenshots fall back to system fonts when webfonts fail to load; trust the computed families.",
};
fs.writeFileSync(path.join(out, "web.json"), JSON.stringify(result, null, 1));
console.log("ok", Object.keys(result.fonts).length, "font rows");
