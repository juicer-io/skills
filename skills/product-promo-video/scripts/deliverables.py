"""Subtitles (.srt + .vtt) and a thumbnail for a finished video.

Usage: python3 deliverables.py cues.json <out-base> <thumbnail-frame.png>

cues.json is a list of [start_s, end_s, "text"], times copied from the video's timeline, one
cue per piece of on-screen text a viewer reads (no voiceover, so the subtitles are the
on-screen text). Writes <out-base>.srt, <out-base>.vtt and <out-base>-thumbnail.jpg (1280x720 for
landscape frames, 720x1280 for vertical, 1080x1080 for square, 1080x1350 for 4:5).
Needs: pillow.
"""
import json
import sys
from PIL import Image

MAX_LINES, MAX_CHARS = 2, 42


def ts(t, sep):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def check(cues):
    prev = 0.0
    for a, b, text in cues:
        assert b > a >= prev, f"cue {a}-{b} overlaps the previous one or ends before it starts"
        lines = text.split("\n")
        assert len(lines) <= MAX_LINES and all(len(l) <= MAX_CHARS for l in lines), (
            f"cue at {a}s needs at most {MAX_LINES} lines of {MAX_CHARS} characters: {text!r}")
        if b - a < 1.5:
            print(f"WARNING: cue at {a}s is on screen for {b - a:.2f}s, under 1.5s to read it")
        prev = b


def main(cues_path, base, frame):
    cues = json.load(open(cues_path))
    check(cues)
    with open(base + ".srt", "w") as f:
        f.write("\n".join(f"{i}\n{ts(a, ',')} --> {ts(b, ',')}\n{x}\n" for i, (a, b, x) in enumerate(cues, 1)))
    with open(base + ".vtt", "w") as f:
        f.write("WEBVTT\n\n" + "\n".join(f"{ts(a, '.')} --> {ts(b, '.')}\n{x}\n" for a, b, x in cues))
    img = Image.open(frame).convert("RGB")
    w, h = img.size
    size = (1280, 720) if w > h else (720, 1280) if h >= 1.7 * w else (1080, round(1080 * h / w))
    img.resize(size, Image.LANCZOS).save(base + "-thumbnail.jpg", quality=90)
    print(f"wrote {base}.srt, {base}.vtt, {base}-thumbnail.jpg ({len(cues)} cues)")


if __name__ == "__main__":
    main(*sys.argv[1:4])
