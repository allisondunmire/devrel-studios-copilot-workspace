"""
Convert a corrected SRT/VTT transcript into synchronized SRT, VTT, and TTML.

The source caption file remains authoritative. If one requested output path is
the source file itself, it is reused instead of rewritten. Every generated
package is validated for matching cue count, timestamps, and text.
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_transcript import parse  # noqa: E402


TIME_PART = r"(?:(\d{2}):)?(\d{2}):(\d{2}[.,]\d{3})"
TIMESTAMP_RE = re.compile(
    rf"^\s*{TIME_PART}\s*-->\s*{TIME_PART}"
)
TTML_NAMESPACE = "http://www.w3.org/ns/ttml"


def normalize_time(value):
    return value.replace(",", ".")


def normalize_time_parts(hours, minutes, seconds):
    return f"{hours or '00'}:{minutes}:{normalize_time(seconds)}"


def normalized_cues(caption_file):
    result = []
    for cue in parse(caption_file)["cues"]:
        match = TIMESTAMP_RE.match(cue["timestamp"])
        if not match:
            raise ValueError(
                f"Unsupported timestamp in cue {cue['index'] + 1}: "
                f"{cue['timestamp']}"
            )
        result.append(
            {
                "start": normalize_time_parts(*match.groups()[0:3]),
                "end": normalize_time_parts(*match.groups()[3:6]),
                "text": cue["text"],
            }
        )
    return result


def emit_srt(cues):
    blocks = []
    for index, cue in enumerate(cues, start=1):
        start = cue["start"].replace(".", ",")
        end = cue["end"].replace(".", ",")
        blocks.append(f"{index}\n{start} --> {end}\n{cue['text']}")
    return "\n\n".join(blocks) + "\n"


def emit_vtt(cues):
    blocks = ["WEBVTT"]
    for cue in cues:
        blocks.append(
            f"{cue['start']} --> {cue['end']}\n{cue['text']}"
        )
    return "\n\n".join(blocks) + "\n"


def emit_ttml(cues, language):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<tt xmlns="{TTML_NAMESPACE}" '
            f"xml:lang={quoteattr(language)}>"
        ),
        "  <body>",
        "    <div>",
    ]
    for cue in cues:
        text = escape(cue["text"]).replace("\n", "<br/>")
        lines.append(
            f'      <p begin="{cue["start"]}" end="{cue["end"]}">'
            f"{text}</p>"
        )
    lines.extend(["    </div>", "  </body>", "</tt>"])
    return "\n".join(lines) + "\n"


def _ttml_text(element):
    parts = [element.text or ""]
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == "br":
            parts.append("\n")
        else:
            parts.append(child.text or "")
        parts.append(child.tail or "")
    return "".join(parts)


def parse_ttml(ttml_file):
    root = ET.parse(ttml_file).getroot()
    cues = []
    for element in root.findall(f".//{{{TTML_NAMESPACE}}}p"):
        cues.append(
            {
                "start": normalize_time(element.attrib["begin"]),
                "end": normalize_time(element.attrib["end"]),
                "text": _ttml_text(element),
            }
        )
    return cues


def validate_outputs(expected_cues, output_paths):
    for output_path in output_paths:
        extension = os.path.splitext(output_path)[1].lower()
        if extension == ".ttml":
            actual_cues = parse_ttml(output_path)
        else:
            actual_cues = normalized_cues(output_path)
        if actual_cues != expected_cues:
            raise ValueError(
                f"Generated {extension} output does not match the corrected "
                f"source: {output_path}"
            )


def write_outputs(source_file, output_dir, formats, language="en"):
    source_file = os.path.abspath(source_file)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    cues = normalized_cues(source_file)
    if not cues:
        raise ValueError(
            "The corrected source did not contain any parseable caption cues."
        )
    stem = os.path.splitext(os.path.basename(source_file))[0]
    emitters = {
        "srt": emit_srt,
        "vtt": emit_vtt,
        "ttml": lambda items: emit_ttml(items, language),
    }
    output_paths = []

    for output_format in formats:
        if output_format not in emitters:
            raise ValueError(f"Unsupported output format: {output_format}")
        output_path = os.path.join(output_dir, f"{stem}.{output_format}")
        if os.path.normcase(output_path) != os.path.normcase(source_file):
            with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(emitters[output_format](cues))
        output_paths.append(output_path)

    validate_outputs(cues, output_paths)
    return len(cues), output_paths


def main():
    parser = argparse.ArgumentParser(
        description="Generate synchronized SRT, VTT, and TTML caption files."
    )
    parser.add_argument("caption_file", help="Corrected .srt or .vtt file")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: beside the source file)",
    )
    parser.add_argument(
        "--formats",
        default="srt,vtt,ttml",
        help="Comma-separated output formats (default: srt,vtt,ttml)",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="TTML xml:lang value (default: en)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.caption_file):
        print(f"File not found: {args.caption_file}", file=sys.stderr)
        sys.exit(1)

    formats = [
        item.strip().lower()
        for item in args.formats.split(",")
        if item.strip()
    ]
    output_dir = args.output_dir or os.path.dirname(
        os.path.abspath(args.caption_file)
    )

    try:
        cue_count, output_paths = write_outputs(
            args.caption_file,
            output_dir,
            formats,
            args.language,
        )
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"Conversion failed: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Validated {cue_count} synchronized cues:")
    for output_path in output_paths:
        print(f"  {output_path}")


if __name__ == "__main__":
    main()
