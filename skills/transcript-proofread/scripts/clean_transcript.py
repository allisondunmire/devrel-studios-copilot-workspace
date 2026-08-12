"""
Clean Transcript (upload-ready output)
======================================
Converts a raw caption file into a CLEAN, standard, upload-ready .vtt/.srt.

YouTube auto-generated (ASR) downloads use a "rolling" format: each spoken
line is stored 2-3 times (building up word-by-word) with inline word-timing
tags like <00:00:02.720><c> across</c>. If you hand that file to someone to
re-upload, viewers can see doubled/odd captions.

This script produces the clean version to RETURN to the user:
  - strips inline word-timing tags and cue settings
  - removes rolling duplicate lines
  - keeps one readable cue per spoken line with correct start/end timestamps
  - re-emits valid .vtt or .srt (matches the chosen output format)

It works on already-clean files too (no-op de-duplication), so it is safe to
run on any .vtt/.srt.

Usage:
    python clean_transcript.py <INPUT> --output <OUTPUT.vtt|.srt>
    python clean_transcript.py raw.vtt -o clean.vtt
    python clean_transcript.py raw.vtt -o clean.srt        # convert format
"""

import re
import os
import argparse

TS = re.compile(
    r"(\d\d:\d\d:\d\d[.,]\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d[.,]\d\d\d)"
)


def norm_ts(t, sep="."):
    """Normalize a timestamp to HH:MM:SS<sep>mmm."""
    return t.replace(",", ".").replace(".", sep, 1) if sep == "," else t.replace(",", ".")


def clean_text(t):
    t = re.sub(r"<[^>]+>", "", t)          # strip <00:..> and <c>/</c>
    t = re.sub(r"\{[^}]+\}", "", t)        # strip style blocks
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


def parse_cues(raw):
    """Detect timestamp lines; collect each cue's non-empty text lines."""
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cues, cur = [], None
    for ln in lines:
        m = TS.search(ln.strip())
        if m:
            if cur:
                cues.append(cur)
            cur = {"start": m.group(1), "end": m.group(2), "text_lines": []}
        elif cur is not None and ln.strip():
            cur["text_lines"].append(ln)
    if cur:
        cues.append(cur)
    return cues


def build_clean(cues):
    """One segment per spoken line = last non-empty text line; de-dup rolling."""
    segs = []
    for c in cues:
        if not c["text_lines"]:
            continue
        txt = clean_text(c["text_lines"][-1])
        if txt:
            segs.append([c["start"], c["end"], txt])

    clean = []
    for s, e, txt in segs:
        if clean and txt == clean[-1][2]:
            clean[-1][1] = e               # merge duplicate; extend end
            continue
        clean.append([s, e, txt])

    # keep timestamps monotonic / non-overlapping
    for i in range(len(clean) - 1):
        if clean[i][1].replace(",", ".") > clean[i + 1][0].replace(",", "."):
            clean[i][1] = clean[i + 1][0]
    return clean


def emit(clean, fmt):
    if fmt == "srt":
        out = []
        for i, (s, e, txt) in enumerate(clean, 1):
            out += [str(i), f"{norm_ts(s, ',')} --> {norm_ts(e, ',')}", txt, ""]
        return "\n".join(out).rstrip() + "\n"
    # vtt
    out = ["WEBVTT", "Kind: captions", "Language: en", ""]
    for s, e, txt in clean:
        out += [f"{norm_ts(s)} --> {norm_ts(e)}", txt, ""]
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Produce a clean, upload-ready caption file.")
    ap.add_argument("input", help="Raw .vtt/.srt caption file")
    ap.add_argument("--output", "-o", required=True, help="Output .vtt or .srt")
    args = ap.parse_args()

    raw = open(args.input, encoding="utf-8-sig").read()
    cues = parse_cues(raw)
    clean = build_clean(cues)

    fmt = "srt" if os.path.splitext(args.output)[1].lower() == ".srt" else "vtt"
    open(args.output, "w", encoding="utf-8", newline="\n").write(emit(clean, fmt))
    print(f"Clean cues: {len(clean)} ({fmt}) -> {args.output}")


if __name__ == "__main__":
    main()
