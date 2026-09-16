"""
Transcript Parser (proofreading mode)
=====================================
Parses .vtt (WebVTT) and .srt (SubRip) caption files into a list of cues,
PRESERVING each cue's original index, timestamp line, and text verbatim.

Unlike the vtt-metadata parser, this does NOT consolidate, deduplicate, or
reformat. The goal is loss-less round-tripping: parse -> proofread text ->
write back with identical structure and timestamps.

Usage:
    python parse_transcript.py <CAPTION_FILE>
    python parse_transcript.py transcript.vtt --output cues.json

Output (JSON):
    {
      "format": "vtt" | "srt",
      "header": "<text before the first cue, verbatim>",
      "cues": [
        {"index": 0, "id": "<optional cue id line or null>",
         "timestamp": "00:00:01.000 --> 00:00:04.500",
         "text": "Welcome everyone."}
      ]
    }
"""

import sys
import os
import re
import json
import argparse


def detect_format(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".vtt":
        return "vtt"
    if ext == ".srt":
        return "srt"
    # Fallback: sniff the first line.
    with open(filepath, "r", encoding="utf-8-sig") as f:
        first = f.readline().strip()
    return "vtt" if first.startswith("WEBVTT") else "srt"


def _read(filepath):
    # utf-8-sig transparently strips a BOM if present.
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return f.read()


def parse(filepath):
    """Parse a .vtt/.srt file into structured cues, preserving structure."""
    fmt = detect_format(filepath)
    content = _read(filepath).replace("\r\n", "\n").replace("\r", "\n")

    header = ""
    if fmt == "vtt":
        # Capture the WEBVTT header block (up to the first blank line) verbatim.
        m = re.match(r"(WEBVTT.*?)(?:\n\n|\Z)", content, flags=re.DOTALL)
        if m:
            header = m.group(1)
            content = content[m.end():]

    blocks = re.split(r"\n\s*\n", content.strip("\n"))
    cues = []
    idx = 0
    for block in blocks:
        lines = block.split("\n")
        # Locate the timestamp line (the one containing '-->').
        ts_pos = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if ts_pos is None:
            # No timestamp -> not a cue (e.g. stray NOTE); skip.
            continue

        cue_id = None
        if ts_pos > 0:
            # Any line(s) before the timestamp is the cue id / number.
            cue_id = "\n".join(lines[:ts_pos]).strip() or None

        timestamp = lines[ts_pos].strip()
        text = "\n".join(lines[ts_pos + 1:]).rstrip()

        cues.append({
            "index": idx,
            "id": cue_id,
            "timestamp": timestamp,
            "text": text,
        })
        idx += 1

    return {"format": fmt, "header": header, "cues": cues}


def main():
    ap = argparse.ArgumentParser(description="Parse VTT/SRT into structured cues (loss-less).")
    ap.add_argument("caption_file", help="Path to the .vtt or .srt file")
    ap.add_argument("--output", "-o", help="Write JSON here (default: stdout)")
    args = ap.parse_args()

    if not os.path.isfile(args.caption_file):
        print(f"File not found: {args.caption_file}", file=sys.stderr)
        sys.exit(1)

    result = parse(args.caption_file)
    payload = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"Parsed {len(result['cues'])} cues ({result['format']}) -> {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
