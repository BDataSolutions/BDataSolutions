#!/usr/bin/env python3
"""BData video assembly — reusable for Videos 9-14.

Runs inside the Higgsfield sandbox (ffmpeg preinstalled, CDN reachable).
Reads a JSON config, downloads narration + scene images, renders the
illustrated-narration cut with Ken Burns motion, music bed and logo
watermark, then PUTs the result to a presigned upload URL.

Usage:  python3 assemble_video.py config.json

Config schema
-------------
{
  "narration_url": "...mp3",            # cleaned narration
  "music_url":     "...mp3",            # optional; omit for no music bed
  "logo_url":      "...png",            # optional; omit for no watermark
  "upload_url":    "https://...",       # optional; presigned PUT target
  "output":        "video9_final.mp4",
  "beats": [                            # in order; durations in seconds
    {"name": "Hook",       "image": "https://...png", "duration": 24.0},
    {"name": "Self-intro", "image": "https://...png", "duration": 35.0}
  ]
}

Beat durations must sum to the narration length; `plan_beats.py` computes
them from the script timestamps (or a transcript) so they always do.
"""
import json, subprocess, sys, os, urllib.request

FPS = 30
FADE = 0.6          # crossfade seconds between beats
ZOOM = 0.10         # Ken Burns travel (10%)
MUSIC_VOL = 0.09    # music bed level under narration
MUSIC_FADE = 4.0    # music fade-out at the end
LOGO_H = 72         # watermark height in px
LOGO_OPACITY = 0.72
LOGO_MARGIN = 24


def fetch(url, dest):
    print(f"  -> {dest}", flush=True)
    urllib.request.urlretrieve(url, dest)
    return dest


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def build(cfg):
    print("Downloading narration and scenes...", flush=True)
    fetch(cfg["narration_url"], "narration.mp3")
    total = probe_duration("narration.mp3")

    beats = cfg["beats"]
    for i, b in enumerate(beats):
        fetch(b["image"], f"s{i+1}.png")

    planned = sum(b["duration"] for b in beats)
    if abs(planned - total) > 0.5:
        print(f"WARNING: beats sum to {planned:.2f}s but narration is "
              f"{total:.2f}s — rescaling beats proportionally.", flush=True)
        k = total / planned
        for b in beats:
            b["duration"] *= k

    # Extend each clip so crossfades straddle the beat boundaries.
    ext = []
    for i, b in enumerate(beats):
        edge = FADE / 2 if i in (0, len(beats) - 1) else FADE
        ext.append(b["duration"] + edge)

    inputs, filters = [], []
    for i, e in enumerate(ext):
        frames = int(round(e * FPS))
        inputs += ["-loop", "1", "-t", f"{e:.3f}", "-i", f"s{i+1}.png"]
        # alternate push-in / pull-out so consecutive scenes don't feel identical
        z = (f"1+{ZOOM}*on/{frames}" if i % 2 == 0
             else f"1+{ZOOM}-{ZOOM}*on/{frames}")
        filters.append(
            f"[{i}:v]scale=2400:1350,zoompan=z='{z}':d={frames}:"
            f"s=1920x1080:fps={FPS},setsar=1[v{i}]")

    prev, off = "v0", 0.0
    for i in range(1, len(ext)):
        off += ext[i - 1] - FADE
        filters.append(f"[{prev}][v{i}]xfade=transition=fade:"
                       f"duration={FADE}:offset={off:.3f}[x{i}]")
        prev = f"x{i}"

    n = len(beats)                    # narration is input index n
    audio_inputs = ["-i", "narration.mp3"]
    if cfg.get("music_url"):
        fetch(cfg["music_url"], "music.mp3")
        audio_inputs += ["-i", "music.mp3"]
        filters.append(f"[{n}:a]anull[an]")
        filters.append(
            f"[{n+1}:a]aloop=loop=-1:size=2e9,atrim=0:{total:.3f},"
            f"volume={MUSIC_VOL},afade=t=out:"
            f"st={total - MUSIC_FADE:.3f}:d={MUSIC_FADE}[am]")
        filters.append("[an][am]amix=inputs=2:duration=first:normalize=0[aout]")
        amap = "[aout]"
    else:
        amap = f"{n}:a"

    if cfg.get("logo_url"):
        fetch(cfg["logo_url"], "logo.png")
        audio_inputs += ["-i", "logo.png"]
        li = len(inputs) // 4 + (2 if cfg.get("music_url") else 1)
        filters.append(
            f"[{li}:v]scale=-1:{LOGO_H},format=rgba,"
            f"colorchannelmixer=aa={LOGO_OPACITY}[wm]")
        filters.append(f"[{prev}][wm]overlay="
                       f"W-w-{LOGO_MARGIN}:H-h-{LOGO_MARGIN}[vout]")
        vmap = "[vout]"
    else:
        vmap = f"[{prev}]"

    out = cfg.get("output", "final.mp4")
    cmd = ["ffmpeg", "-y", *inputs, *audio_inputs,
           "-filter_complex", ";".join(filters),
           "-map", vmap, "-map", amap,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-t", f"{total:.3f}", out]
    print("Rendering...", flush=True)
    subprocess.run(cmd, check=True)

    size = os.path.getsize(out)
    print(f"Rendered {out}: {probe_duration(out):.2f}s, {size/1e6:.1f} MB",
          flush=True)

    if cfg.get("upload_url"):
        print("Uploading...", flush=True)
        code = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-X", "PUT", "-H", "Content-Type: video/mp4",
             "--data-binary", f"@{out}", cfg["upload_url"]],
            capture_output=True, text=True).stdout.strip()
        print(f"UPLOAD_HTTP_{code}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])))
