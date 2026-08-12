#!/usr/bin/env python3
"""Generate a DevRel Studios production schedule from a shoot/recording date (Day 0).

Every milestone is a fixed calendar-day offset from the recording date, per the studio's
Standard Video Production Formula.

Usage:
    python production_schedule.py <shoot-date> [--title "Name"] [--md] [--skip-weekends]

Examples:
    python production_schedule.py 2026-08-03
    python production_schedule.py "Aug 3 2026" --title "Data Exposed Ep 42" --md
    python production_schedule.py 8/3/2026 --skip-weekends
"""

import argparse
import sys
from datetime import date, timedelta

# Milestone label -> offset in calendar days from the shoot date (Day 0).
MILESTONES = [
    ("Recording / Shoot", 0),
    ("V1 Edit Due", 7),
    ("Internal Comments Due", 12),
    ("V2 Edit Due", 12),
    ("V2 Sent to Guest", 13),
    ("Guest Comments Due", 16),
    ("Final Version Delivered", 19),
    ("Publication Date", 23),
]

# Accepted input date formats.
DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%b %d %Y",
    "%b %d, %Y",
    "%B %d %Y",
    "%B %d, %Y",
    "%d %b %Y",
    "%d %B %Y",
]


def parse_date(text):
    """Parse a date string using several common formats. Returns a date or raises ValueError."""
    from datetime import datetime

    cleaned = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Could not parse date: {text!r}. Try a format like 2026-08-03, Aug 3 2026, or 8/3/2026."
    )


def next_weekday(d):
    """If d is Sat/Sun, roll forward to the next Monday; otherwise return d unchanged."""
    if d.weekday() == 5:  # Saturday
        return d + timedelta(days=2)
    if d.weekday() == 6:  # Sunday
        return d + timedelta(days=1)
    return d


def build_schedule(shoot_date, skip_weekends=False):
    """Return a list of (label, offset, date, is_weekend) rows."""
    rows = []
    for label, offset in MILESTONES:
        d = shoot_date + timedelta(days=offset)
        is_weekend = d.weekday() >= 5
        if skip_weekends:
            d = next_weekday(d)
            is_weekend = False
        rows.append((label, offset, d, is_weekend))
    return rows


def format_plain(rows, title):
    lines = []
    if title:
        lines.append(f"Production Schedule — {title}")
    else:
        lines.append("Production Schedule")
    lines.append("")
    label_w = max(len(r[0]) for r in rows)
    for label, offset, d, is_weekend in rows:
        offset_str = "Day 0" if offset == 0 else f"+{offset}d"
        weekday = d.strftime("%a")
        flag = "  <-- weekend" if is_weekend else ""
        lines.append(
            f"{label.ljust(label_w)}  {d.isoformat()} ({weekday})  {offset_str}{flag}"
        )
    return "\n".join(lines)


def format_markdown(rows, title):
    lines = []
    if title:
        lines.append(f"### Production Schedule — {title}")
    else:
        lines.append("### Production Schedule")
    lines.append("")
    lines.append("| Milestone | Date | Day | Offset |")
    lines.append("|-----------|------|-----|--------|")
    for label, offset, d, is_weekend in rows:
        offset_str = "Day 0" if offset == 0 else f"+{offset} days"
        weekday = d.strftime("%A")
        flag = " ⚠️ weekend" if is_weekend else ""
        lines.append(f"| {label} | {d.isoformat()}{flag} | {weekday} | {offset_str} |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a DevRel Studios production schedule from a shoot date."
    )
    parser.add_argument("shoot_date", help="Recording/shoot date (Day 0), e.g. 2026-08-03.")
    parser.add_argument("--title", default="", help="Optional project/episode name.")
    parser.add_argument("--md", action="store_true", help="Output a Markdown table.")
    parser.add_argument(
        "--skip-weekends",
        action="store_true",
        help="Roll any milestone that lands on Sat/Sun forward to the next Monday.",
    )
    args = parser.parse_args(argv)

    try:
        shoot_date = parse_date(args.shoot_date)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    rows = build_schedule(shoot_date, skip_weekends=args.skip_weekends)
    if args.md:
        print(format_markdown(rows, args.title))
    else:
        print(format_plain(rows, args.title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
