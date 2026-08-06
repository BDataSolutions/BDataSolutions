#!/usr/bin/env python3
"""Compute beat durations for a BData video.

Two modes:

1. scale  — take the script's [m:ss] timestamps (written at ~150 wpm) and
            stretch them to the real narration length. Fast, no transcript,
            but drifts a few seconds if delivery pace varies by section.

2. align  — transcribe the narration (faster-whisper, preinstalled in the
            Higgsfield sandbox) and find where each beat's opening words are
            actually spoken. Exact; use when the audio has been trimmed and
            the script timestamps no longer correspond to anything.

Usage:
    python3 plan_beats.py scale beats.json narration.mp3 > plan.json
    python3 plan_beats.py align beats.json narration.mp3 > plan.json

beats.json: [{"name": "Hook", "image": "https://...", "start": "0:00",
              "cue": "Here is a pattern I keep running into"}, ...]
`start` drives scale mode; `cue` (first few spoken words) drives align mode.
"""
import json, sys, subprocess


def secs(ts):
    m, s = ts.split(":")
    return int(m) * 60 + float(s)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def scale(beats, total):
    starts = [secs(b["start"]) for b in beats]
    span = starts[-1] + (starts[-1] - starts[-2] if len(starts) > 1 else 60)
    k = total / span
    scaled = [s * k for s in starts] + [total]
    return [scaled[i + 1] - scaled[i] for i in range(len(beats))]


def align(beats, path, total):
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path)
    words = []
    for s in segs:
        words.append((s.start, s.text.strip().lower()))

    def find(cue, after):
        cue = cue.strip().lower()[:40]
        best, key = None, cue.split()[:4]
        for t, text in words:
            if t < after:
                continue
            if all(k in text for k in key[:2]):
                best = t
                break
        return best

    starts, cursor = [], 0.0
    for i, b in enumerate(beats):
        if i == 0:
            starts.append(0.0)
            continue
        t = find(b.get("cue", ""), cursor)
        if t is None:
            raise SystemExit(f"cue not found for beat {i+1}: {b['name']!r} "
                             f"— fall back to scale mode or fix the cue")
        starts.append(t)
        cursor = t
    starts.append(total)
    return [starts[i + 1] - starts[i] for i in range(len(beats))]


if __name__ == "__main__":
    mode, beats_file, audio = sys.argv[1], sys.argv[2], sys.argv[3]
    beats = json.load(open(beats_file))
    total = duration(audio)
    durs = scale(beats, total) if mode == "scale" else align(beats, audio, total)
    for b, d in zip(beats, durs):
        b["duration"] = round(d, 3)
        b.pop("start", None)
        b.pop("cue", None)
    print(json.dumps(beats, indent=2))
    t = 0
    for b in beats:
        print(f"  {int(t//60)}:{int(t%60):02d}  {b['name']}", file=sys.stderr)
        t += b["duration"]
