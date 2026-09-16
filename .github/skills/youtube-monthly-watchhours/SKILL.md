---
name: youtube-monthly-watchhours
description: >
  Use when the user wants to analyze a month of YouTube Studio analytics data and produce
  an executive-ready report, including requests like "analyze YouTube watch hours",
  "monthly YouTube report", "YouTube watch hours summary", "channel performance
  breakdown", or "generate YouTube monthly update". Returns top videos per channel by
  watch hours, channel share breakdown, key watch-hour drivers with editorial insight,
  a narrative monthly summary, and can optionally generate a formatted .docx document.
---

# YouTube Monthly Watch Hours Summary

Analyze a month of YouTube Studio analytics data and produce an executive-ready report.

## What it does

- Top 3 videos per channel ranked by watch hours
- Channel share breakdown (hours + percentage)
- Key watch-hour drivers with editorial insight
- Narrative monthly summary (5–7 sentences, leadership-ready)
- *(Optional)* Formatted `.docx` Word document saved to Downloads

## When to use it

End of each month when you have a YouTube analytics export covering one or more channels and need a quick summary for stakeholders.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Analytics file | ✅ | `.xlsx` or `.csv` export from YouTube Studio containing columns: **Channel**, **Content** (video ID or `Total`), **Video title**, **Watch time (hours)**, **Views**. If the file has a `Table data` sheet, use that. |
| Month label | Optional | e.g. "April 2026". If omitted, infer from the data or file name. |
| Word doc | Optional | If the user asks, generate a `.docx` and save it to `~/Downloads`. |

## Instructions

### Data loading

1. Open the provided file. For `.xlsx`, prefer a sheet named **Table data**; fall back to the first sheet.
2. Identify the header row. Required columns (case-insensitive): **Channel**, **Video title** (or **Video Title**), **Watch time (hours)** (or **Watch Hours**), **Views**. A **Content** column distinguishes per-video rows from channel `Total` rows.
3. Skip any repeated header rows (where the Channel cell equals the literal text "Channel").
4. Convert watch-hours and views to numbers; treat blanks or non-numeric values as 0.
5. **Do not fabricate or infer missing data.**

### Analysis

6. Group rows by **Channel**.
7. For each channel, capture the `Total` row (if present) for aggregate numbers; otherwise sum the individual video rows.
8. Rank each channel's videos by watch hours descending; select the **top 3**.
9. Compute each channel's **share** of grand-total watch hours (percentage).
10. Identify overall watch-hour drivers:
    - Which channels contributed the largest share
    - Any repeated formats, series, or themes obvious from video titles
    - Any single videos that disproportionately drove the totals
11. Write a concise narrative summary (5–7 sentences) in clear, neutral, reporting language suitable for a leadership update.

### Output (in chat)

Display the results using the format in the **Output Format** section below.

### Word document (only if requested)

12. Install `python-docx` if not already available.
13. Build a `.docx` containing:
    - Title: "YouTube Monthly Watch Hours Summary"
    - Subtitle: the month label
    - Overview section (total watch hours, total views, channel count)
    - Top Videos by Channel (heading per channel, numbered list)
    - Biggest Watch Hour Drivers (bullet list)
    - Monthly Summary (paragraph)
    - Channel Share table (Channel | Watch Hours | Share %)
14. Save to `~/Downloads/YouTube Watch Hours Summary - {Month Year}.docx`.

## Output Format

```
## Top Videos by Channel

**Channel Name** — X watch hours (Y% of total)
1. Video title — X watch hours
2. Video title — X watch hours
3. Video title — X watch hours

(repeat for each channel, ordered by total watch hours descending)

---

## Biggest Watch Hour Drivers
- Bullet insight about the dominant channel or video
- Bullet about secondary contributors
- Bullet about recurring themes or formats

---

## Monthly Summary
Short paragraph (5–7 sentences) in clear, neutral, reporting language.
```

## Edge cases

- If a channel has fewer than 3 videos, report all available videos.
- If watch-hours or views columns use different header names, attempt case-insensitive matching before failing.
- If the file contains multiple sheets, prefer "Table data"; otherwise use the first sheet with recognizable column headers.
- Empty or malformed rows should be skipped with a warning, not cause a failure.
