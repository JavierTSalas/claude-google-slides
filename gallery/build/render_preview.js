// Render motion previews from player.html.
//   node render_preview.js                -> every example in ../examples.json + the full reel
//   node render_preview.js panorama       -> one example
//   node render_preview.js --stills DIR   -> final state of every slide as PNG (for checks)
// Output: ../previews/<id>.mp4 (1280x720, 30 fps) and ../previews/<id>.gif (640x360, 15 fps).
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const PLAYER = "file://" + path.join(__dirname, "player.html");
const FPS = 30;

async function open(browser, query) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto(`${PLAYER}?${query}`);
  await page.evaluate(() => window.READY);
  return page;
}

async function render(browser, id, query) {
  const page = await open(browser, query);
  const dur = await page.evaluate(() => window.DURATION);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "pv-"));
  const n = Math.ceil((dur / 1000) * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate((ms) => window.seek(ms), (i * 1000) / FPS);
    await page.screenshot({ path: path.join(dir, `f${String(i).padStart(5, "0")}.png`) });
  }
  await page.close();
  const src = ["-framerate", String(FPS), "-i", path.join(dir, "f%05d.png")];
  const mp4 = path.join(ROOT, "previews", `${id}.mp4`), gif = path.join(ROOT, "previews", `${id}.gif`);
  execFileSync("ffmpeg", ["-y", "-v", "error", ...src, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
    "-preset", "slow", "-movflags", "+faststart", mp4]);
  execFileSync("ffmpeg", ["-y", "-v", "error", ...src, "-vf",
    "fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
    "-loop", "0", gif]);
  fs.rmSync(dir, { recursive: true });
  const mb = (f) => (fs.statSync(f).size / 1e6).toFixed(2);
  console.log(`${id}: ${(dur / 1000).toFixed(1)} s, mp4 ${mb(mp4)} MB, gif ${mb(gif)} MB`);
}

(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch();
  const examples = JSON.parse(fs.readFileSync(path.join(ROOT, "examples.json")));
  if (args[0] === "--stills") {
    const out = args[1];
    fs.mkdirSync(out, { recursive: true });
    const count = await (await open(browser, "slides=1")).evaluate(() => window.SCENES.length);
    for (let s = 1; s <= count; s++) {
      const page = await open(browser, `slides=${s}&hold=0`);
      await page.evaluate(() => window.seek(window.DURATION - 1));
      await page.screenshot({ path: path.join(out, `s${s}.png`) });
      await page.close();
    }
  } else {
    fs.mkdirSync(path.join(ROOT, "previews"), { recursive: true });
    const only = args[0];
    for (const ex of examples) {
      if (only && only !== ex.id) continue;
      await render(browser, ex.id, `slides=${ex.slides.join(",")}&hold=${ex.hold}&lastHold=${ex.lastHold || ex.hold}&lead=${ex.lead ? 1 : 0}`);
    }
    if (!only || only === "reel") {
      const all = examples.flatMap((e) => e.slides);
      await render(browser, "reel", `slides=${all.join(",")}&hold=1500&lastHold=3000`);
    }
  }
  await browser.close();
})();
