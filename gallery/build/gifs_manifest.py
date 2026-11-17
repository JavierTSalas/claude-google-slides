"""Extract GIF frames for the preview player and write out/gifs.js."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(HERE, "..", "assets")
out = {}
for f in sorted(os.listdir(assets)):
    if not f.endswith(".gif"):
        continue
    name = f[:-4]
    d = os.path.join(HERE, "out", "frames", name)
    os.makedirs(d, exist_ok=True)
    for old in os.listdir(d):
        os.remove(os.path.join(d, old))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(assets, f), os.path.join(d, "%04d.png")], check=True)
    rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                           "-of", "csv=p=0", os.path.join(assets, f)], capture_output=True, text=True).stdout.strip()
    num, den = rate.split("/")
    out[name] = {"fps": int(num) / int(den), "n": len(os.listdir(d))}
with open(os.path.join(HERE, "out", "gifs.js"), "w") as fh:
    fh.write("window.GIFS = " + json.dumps(out) + ";\n")
print(out)
