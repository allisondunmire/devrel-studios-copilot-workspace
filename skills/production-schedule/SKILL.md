---
name: production-schedule
description: >
  Generate a DevRel Studios video production schedule from a given shoot/recording date. Use
  whenever the user provides a shoot day (record day, filming date, "we shot on...", "recording
  is...") and wants the downstream milestone dates: V1 edit, internal comments, V2 edit, V2 sent
  to guest, guest comments, final version, and publication date. Trigger phrases include
  "production schedule", "build a schedule for this shoot", "when is publication if we record
  on...", "generate milestones for a shoot day", "post-production timeline", "edit due dates".
  Always use this skill for shoot-day-driven scheduling even if the user doesn't say the word
  "schedule".
---

# Production Schedule Generator

Generate a full DevRel Studios production schedule from a single input: the **shoot/recording
date (Day 0)**. Every downstream milestone is a fixed offset from that date, per the **Standard
Video Production Formula** below.

## Standard Video Production Formula

| Milestone | Offset from Recording |
|-----------|----------------------|
| Recording / Shoot | Day 0 |
| V1 Edit Due | +7 days |
| Internal Comments Due | +12 days |
| V2 Edit Due | +12 days (same day as comments) |
| V2 Sent to Guest | +13 days |
| Guest Comments Due | +16 days |
| Final Version Delivered | +19 days |
| Publication Date | +23 days |

## How to use it

1. Get the **shoot date** from the user. Accept common formats (e.g. `2026-08-03`,
   `Aug 3 2026`, `8/3/2026`). If the date is ambiguous or missing, ask before proceeding.
2. Run the script to compute all milestone dates:

   ```bash
   python scripts/production_schedule.py <shoot-date> [--title "Project Name"] [--md]
   ```

   - `<shoot-date>` — the Day 0 recording date, any common format.
   - `--title` — optional project/episode name to label the schedule.
   - `--md` — output a Markdown table (default is a plain aligned table). Use `--md` when the
     user wants something to paste into a doc, ADO, or project file.

3. Return the computed schedule to the user. Each milestone shows its **date** and the
   **weekday** so the user can spot weekend deadlines.

## Weekend handling

By default the script reports the raw offset dates (it does **not** shift weekends). It flags any
milestone that lands on a Saturday or Sunday so the user can decide whether to adjust. If the
user asks to avoid weekend deadlines, re-run with `--skip-weekends` to roll those milestones
forward to the next Monday.

## Files in this skill

| Path | Purpose |
|------|---------|
| `scripts/production_schedule.py` | Compute all milestone dates from a shoot date. Supports Markdown output and weekend flagging/skipping. |

## Notes

- The offsets are calendar days, not business days.
- V2 Edit Due intentionally shares the same date as Internal Comments Due (+12).
- If a project uses a non-standard timeline, tell the user these are the studio's standard
  offsets and adjust only the specific milestones they call out.
