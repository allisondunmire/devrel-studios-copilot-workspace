"""
Transcript Parser
=================
Parses .vtt (WebVTT) and .srt (SubRip) caption files and outputs clean,
consolidated text with timestamps. Merges overlapping/consecutive captions
and removes duplicate lines to reduce token usage for long transcripts.

Usage:
    python parse-vtt.py <CAPTION_FILE>
    python parse-vtt.py transcript.vtt
    python parse-vtt.py captions.srt
    python parse-vtt.py transcript.vtt --output parsed.txt

Output:
    Prints or saves consolidated transcript with timestamps.
"""

import sys
import os
import re
import argparse


def parse_timestamp(ts_str):
    """Convert VTT/SRT timestamp to total seconds.
    Handles: HH:MM:SS.mmm (VTT), HH:MM:SS,mmm (SRT), MM:SS.mmm"""
    # Normalize SRT comma to dot
    ts_str = ts_str.strip().replace(",", ".")
    parts = ts_str.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return 0.0


def seconds_to_youtube_timestamp(seconds):
    """Convert seconds to YouTube chapter format (M:SS or H:MM:SS)."""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"


def parse_vtt(filepath):
    """Parse a VTT file and return list of (start_seconds, end_seconds, text) tuples."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings before header/NOTE regexes
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Remove WEBVTT header and any metadata
    content = re.sub(r"^WEBVTT.*?\n\n", "", content, flags=re.DOTALL)

    # Remove NOTE blocks
    content = re.sub(r"NOTE\s.*?\n\n", "", content, flags=re.DOTALL)

    return _parse_cue_blocks(content)


def parse_srt(filepath):
    """Parse an SRT file and return list of (start_seconds, end_seconds, text) tuples."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # SRT files sometimes start with a BOM
    content = content.lstrip("\ufeff")

    return _parse_cue_blocks(content)


def _parse_cue_blocks(content):
    """Shared parser for VTT/SRT cue blocks (both use --> arrows)."""
    # Normalize CRLF and CR line endings to LF so block splitting works
    # on Windows-formatted caption files
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\n+", content.strip())

    captions = []
    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue

        # Find the timestamp line
        ts_line = None
        text_lines = []
        for i, line in enumerate(lines):
            if "-->" in line:
                ts_line = line
                text_lines = lines[i + 1:]
                break

        if not ts_line:
            continue

        # Parse timestamps
        match = re.match(
            r"([\d:.,]+)\s*-->\s*([\d:.,]+)",
            ts_line.strip()
        )
        if not match:
            continue

        start = parse_timestamp(match.group(1))
        end = parse_timestamp(match.group(2))

        # Clean text: remove tags, positioning, etc.
        text = " ".join(text_lines)
        text = re.sub(r"<[^>]+>", "", text)  # Remove HTML-like tags
        text = re.sub(r"\{[^}]+\}", "", text)  # Remove style blocks
        text = text.strip()

        if text:
            captions.append((start, end, text))

    return captions


def parse_transcript(filepath):
    """Auto-detect format and parse. Returns list of (start, end, text) tuples."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".srt":
        return parse_srt(filepath)
    elif ext == ".vtt":
        return parse_vtt(filepath)
    else:
        # Try VTT first (more permissive), fall back to SRT-style
        with open(filepath, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        if first_line.startswith("WEBVTT"):
            return parse_vtt(filepath)
        return parse_srt(filepath)


def deduplicate_text(text):
    """Remove repeated phrases within a text block.
    VTT files often triple-repeat lines due to rolling captions."""
    words = text.split()
    if len(words) < 6:
        return text

    # Check for repeated sequences (2x or 3x repeated phrases)
    for repeat_count in [3, 2]:
        cleaned = []
        i = 0
        while i < len(words):
            # Try chunk sizes from large to small
            found_repeat = False
            for chunk_size in range(min(20, (len(words) - i) // repeat_count), 2, -1):
                chunk = words[i:i + chunk_size]
                # Check if the next N copies match
                all_match = True
                for r in range(1, repeat_count):
                    compare = words[i + chunk_size * r:i + chunk_size * (r + 1)]
                    if compare != chunk:
                        all_match = False
                        break
                if all_match:
                    cleaned.extend(chunk)
                    i += chunk_size * repeat_count
                    found_repeat = True
                    break
            if not found_repeat:
                cleaned.append(words[i])
                i += 1
        words = cleaned

    return " ".join(words)


def consolidate_captions(captions, chunk_seconds=30.0):
    """
    Merge captions into chunks of roughly chunk_seconds duration.
    Removes duplicate caption text while preserving chronological flow.
    """
    if not captions:
        return []

    consolidated = []
    current_start, current_end, current_text = captions[0]
    seen_text = {current_text}

    for start, end, text in captions[1:]:
        # Skip duplicate text
        if text in seen_text:
            current_end = max(current_end, end)
            continue

        # Start a new chunk if we've exceeded the chunk duration
        if start - current_start >= chunk_seconds:
            consolidated.append((current_start, current_end, current_text))
            current_start, current_end, current_text = start, end, text
            seen_text = {text}
        else:
            current_text += " " + text
            current_end = end
            seen_text.add(text)

    consolidated.append((current_start, current_end, current_text))
    return consolidated


def format_output(consolidated):
    """Format consolidated captions as readable text with timestamps."""
    lines = []
    for start, end, text in consolidated:
        ts = seconds_to_youtube_timestamp(start)
        clean = deduplicate_text(text)
        lines.append(f"[{ts}] {clean}")
    return "\n\n".join(lines)


def get_stats(captions, consolidated):
    """Return basic stats about the transcript."""
    if not captions:
        return "No captions found."

    duration = captions[-1][1]
    total_words = sum(len(c[2].split()) for c in consolidated)

    return (
        f"Duration: {seconds_to_youtube_timestamp(duration)}\n"
        f"Original captions: {len(captions)}\n"
        f"Consolidated segments: {len(consolidated)}\n"
        f"Total words: {total_words}"
    )


def main():
    parser = argparse.ArgumentParser(description="Parse VTT/SRT transcript files")
    parser.add_argument("caption_file", help="Path to the .vtt or .srt file")
    parser.add_argument("--output", "-o", help="Output file path (default: print to stdout)")
    parser.add_argument("--stats", action="store_true", help="Print stats only")
    args = parser.parse_args()

    if not os.path.isfile(args.caption_file):
        print(f"❌ File not found: {args.caption_file}")
        sys.exit(1)

    ext = os.path.splitext(args.caption_file)[1].lower()
    if ext not in (".vtt", ".srt"):
        print(f"⚠️  Unrecognized extension '{ext}', will attempt auto-detection.")

    captions = parse_transcript(args.caption_file)
    if not captions:
        print("❌ No captions found in file.")
        sys.exit(1)

    consolidated = consolidate_captions(captions)
    stats = get_stats(captions, consolidated)

    if args.stats:
        print(stats)
        return

    output = f"# Transcript\n\n{stats}\n\n---\n\n{format_output(consolidated)}"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ Parsed transcript saved to: {args.output}")
        print(stats)
    else:
        print(output)


if __name__ == "__main__":
    main()
