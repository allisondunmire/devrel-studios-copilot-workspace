"""
Transcript Writer (proofreading mode)
=====================================
Applies proofread corrections back into a .vtt/.srt file, preserving the
original format, cue order, timestamps, and cue count.

It re-parses the ORIGINAL file (so structure/timestamps come straight from
the source) and only replaces cue text for cues listed in a corrections file.

Corrections JSON format:
    {
      "0": "Welcome everyone to Microsoft Fabric.",
      "5": "We're using GitHub Copilot today."
    }
Keys are cue indices (as produced by parse_transcript.py); values are the
full corrected text for that cue. Cues not listed are left untouched.

Usage:
    python write_transcript.py <ORIGINAL_FILE> <CORRECTIONS_JSON> --output <OUT_FILE>
"""

import sys
import os
import json
import argparse

# Import the shared parser (same directory).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_transcript import parse  # noqa: E402


def build_cue_block(cue, fmt):
    """Reassemble a single cue block in the correct format."""
    lines = []
    if fmt == "srt":
        # SRT requires a sequential numeric id line.
        lines.append(str(cue["index"] + 1))
        lines.append(cue["timestamp"])
    else:
        # VTT: keep an existing cue id line only if the source had one.
        if cue.get("id"):
            lines.append(cue["id"])
        lines.append(cue["timestamp"])
    lines.append(cue["text"])
    return "\n".join(lines)


def apply_corrections(original_file, corrections, output_file):
    parsed = parse(original_file)
    fmt = parsed["format"]
    cues = parsed["cues"]

    applied = 0
    for cue in cues:
        key = str(cue["index"])
        if key in corrections and corrections[key] is not None:
            new_text = corrections[key]
            if new_text != cue["text"]:
                cue["text"] = new_text
                applied += 1

    blocks = [build_cue_block(c, fmt) for c in cues]

    if fmt == "vtt":
        header = parsed["header"].strip() or "WEBVTT"
        body = "\n\n".join(blocks)
        content = header + "\n\n" + body + "\n"
    else:
        content = "\n\n".join(blocks) + "\n"

    with open(output_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    return applied, len(cues)


def main():
    ap = argparse.ArgumentParser(description="Apply proofread corrections to a VTT/SRT file.")
    ap.add_argument("original_file", help="Path to the original .vtt/.srt file")
    ap.add_argument("corrections_json", help="Path to corrections JSON (index -> corrected text)")
    ap.add_argument("--output", "-o", required=True, help="Output file path")
    args = ap.parse_args()

    for p in (args.original_file, args.corrections_json):
        if not os.path.isfile(p):
            print(f"File not found: {p}", file=sys.stderr)
            sys.exit(1)

    with open(args.corrections_json, "r", encoding="utf-8") as f:
        corrections = json.load(f)

    applied, total = apply_corrections(args.original_file, corrections, args.output)
    print(f"Applied {applied} cue correction(s) across {total} cues -> {args.output}")


if __name__ == "__main__":
    main()
