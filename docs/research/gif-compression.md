# GIF budget for motion decks (up to 50 loops)

Date: 2026-11-17. Masters: `prototypes/decks-that-move/motion/*` rendered with HyperFrames to MP4, then converted to GIF.

## Result

- 50 flat-graphic loops fit in about 40 MB. Budget: 0.4–0.9 MB per flat loop, about 1.6 MB per photo-like loop.
- `gifsicle -O3 --lossy=30` halves size. Quality loss is not visible on flat graphics.
- A small moving area cuts size 2.5–4x. This is the biggest lever.
- The Drive connector in a cloud session caps uploads at about 3 MB per call. That cap is the blocker, not GIF size.

## Pipeline

```bash
# 1. palette from the master
ffmpeg -i loop.mp4 -vf "fps=$FPS,scale=$W:-1:flags=lanczos,palettegen=max_colors=$C:stats_mode=full" p.png
# 2. map frames (no dither or sierra2_4a; bayer breaks flat backgrounds)
ffmpeg -i loop.mp4 -i p.png -lavfi "fps=$FPS,scale=$W:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle" -loop 0 raw.gif
# 3. lossy optimize (gifsicle 1.92; npm: gifsicle@7)
gifsicle -O3 --lossy=30 raw.gif -o loop.gif
```

## Matrix (bytes)

| Loop | Size, fps | ffmpeg | -O3 | -O3 lossy=30 | -O3 lossy=80 | SSIM vs master |
|---|---|---|---|---|---|---|
| badge (text ring) | 360 px, 15 | 1,511,963 | 1,316,083 | 830,272 | 755,200 | 0.956 → 0.953 |
| badge | 360 px, 10 | 1,016,672 | 879,158 | 548,580 | 497,697 | |
| orbits | 1024 px, 15 | 1,610,527 | 1,423,354 | 911,850 | 889,673 | 0.990 → 0.986 |
| orbits | 1024 px, 10 | 1,009,439 | 903,440 | 609,276 | 595,899 | |
| orbits, dashed ring static | 1024 px, 15 | 615,535 | 560,404 | **415,929** | 403,779 | |
| light (photo-like) | 400 px, 8, 48 colors, no dither | 3,029,184 | 2,856,691 | 1,584,295 | 1,241,794 | 0.975 → 0.906 (reads as grain) |
| light | 400 px, 8, 64 colors, sierra | 4,360,263 | 4,208,365 | 1,809,841 | 1,363,760 | |

## Design rules for loops

1. Keep the moving area small. Static rings, rules and text go in native shapes, not in the GIF.
2. Flat graphics: 10–15 fps, lossy=30. Photo-like light: 8 fps, ≤ 400 px, 48 colors, lossy=30.
3. Match the GIF ground to the slide background exactly (sample the GIF pixel, set the slide to it).
4. Size the GIF to its on-slide box at about 1x of a 1280 px wide slide. Larger costs bytes for nothing.

## Upload routes tested

| Route | Result |
|---|---|
| Drive connector (cloud session) | Fails above about 3 MB of file per call (4.2 MB request cap, 10 MB file cap). |
| PPTX with externally linked GIFs (`r:link`, `TargetMode="External"`) | Google conversion does not fetch them. Link-only pictures drop; link + embed keeps the embedded copy only. |
| User uploads the .pptx to Drive, opens as Slides | Works. Drive conversion limit is 100 MB per presentation (Google Help, not verified at 100 MB). |
| Drive API resumable upload with the user's own OAuth | Not tested. Google API hosts answer from the container; needs an OAuth client and a one-time consent. No 3 MB cap. |
| MP4 via Drive + Slides API `createVideo` | About 10x smaller than GIF. Plays in present mode only, needs a click or autoplay, no native loop. Not a GIF replacement. |

Recommendation: the skill uploads with the Drive API under the user's own OAuth (local Claude Code, or a stored refresh token). Fallback: the user drags the .pptx into Drive.
