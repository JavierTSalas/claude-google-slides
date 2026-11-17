// Render a loop composition (loops/<name>.html) to a GIF for the deck.
// Contract: the page sets window.LOOP = {w, h, fps, dur} and window.seek(t).
// Usage: node render_loop.js loops/ripple.html ../assets/ripple.gif [outWidth] [colors] [dither]
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

(async () => {
  const [src, out, outW, colors = "32", dither = "none"] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + path.resolve(src));
  await page.evaluate(() => document.fonts.ready);
  const L = await page.evaluate(() => window.LOOP);
  await page.setViewportSize({ width: L.w, height: L.h });
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "loop-"));
  const n = Math.round(L.fps * L.dur); // frame n == frame 0, so stop one short: seamless
  for (let i = 0; i < n; i++) {
    await page.evaluate((t) => window.seek(t), i / L.fps);
    await page.screenshot({ path: path.join(dir, `f${String(i).padStart(4, "0")}.png`) });
  }
  await browser.close();
  const scale = outW ? `scale=${outW}:-1:flags=lanczos,` : "";
  // Flat palettes: few colors, no dither, only changed rectangles stored per frame.
  execFileSync("ffmpeg", ["-y", "-v", "error", "-framerate", String(L.fps), "-i", path.join(dir, "f%04d.png"),
    "-vf", `${scale}split[a][b];[a]palettegen=max_colors=${colors}:stats_mode=full[p];[b][p]paletteuse=dither=${dither}:diff_mode=rectangle`,
    "-loop", "0", out]);
  fs.rmSync(dir, { recursive: true });
  console.log(out, (fs.statSync(out).size / 1e6).toFixed(2), "MB", n, "frames");
})();
