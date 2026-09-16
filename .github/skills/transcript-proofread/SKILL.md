---
name: transcript-proofread
description: >
  Use when the user wants to proofread or deliver a .vtt/.srt caption file, including requests
  like "proofread this transcript", "create all caption formats", "make SRT, VTT, and TTML",
  or "attach the corrected captions to the ADO episode". Corrects wording and brand names,
  produces clean synchronized caption files, and can optionally attach them to an Azure DevOps
  Episode or upload a corrected track to YouTube. It does not generate titles, descriptions,
  or chapter metadata.
---

# Transcript Proofreader

Proofread an AI-generated `.vtt` or `.srt` transcript and return a **clean, upload-ready
corrected caption file** plus a **summary of changes**. Focus especially on tech/brand names
that speech-to-text engines get wrong.

Works with transcripts from **any** source — YouTube auto-captions, Frame.io, or other tools.
Frame.io transcript export is a manual input when the account does not provide API access.

> **The deliverable is a clean, standard caption file.** These files are handed to someone who
> re-uploads them to YouTube, so the returned `.vtt`/`.srt` must be a normal, upload-ready
> subtitle file: **one readable cue per line, no rolling/duplicate lines, and no inline
> word-timing tags.** Never return the raw YouTube-ASR format as the final deliverable.

## What this skill fixes

Do a **full proofread**, in priority order:

1. **Tech & brand terms** — the top priority. Correct product, company, and framework names
   (e.g. `Fabriq` → `Fabric`, `Co-pilot` → `Copilot`, `Asure` → `Azure`, `dot net` → `.NET`).
2. **Common-word misspellings** — ordinary typos and phonetic errors.
3. **Capitalization** — especially brand casing (`.NET`, `GitHub`, `PostgreSQL`, `Copilot`).
4. **Basic punctuation & grammar** — light touch only.

**Do NOT** rewrite meaning, restyle sentences, or remove filler words ("uh", "um"). Only
correct the wording. (Cleaning duplicate rolling lines / word-timing tags from raw YouTube-ASR
files is expected — see the cleaning step below — but do not otherwise re-time or merge the
actual spoken lines.)

## Confidence gating (important)

- **Auto-apply** high-confidence tech/brand corrections — any cue text that matches a glossary
  `variant`, or an obvious, unambiguous brand-casing fix.
- **Ask the user to confirm** anything ambiguous: an unknown proper noun, a possible homophone,
  a term not in the glossary, or anything where the intended word is genuinely unclear.
- When in doubt, **ask** rather than silently changing — but don't pester the user about
  clearly-correct fixes.

## Files in this skill

| Path | Purpose |
|------|---------|
| `scripts/parse_transcript.py` | Loss-lessly parse `.vtt`/`.srt` into cues (index, timestamp, text). |
| `scripts/clean_transcript.py` | Produce the **clean, upload-ready** output: strip word-timing tags, remove rolling duplicate lines, re-emit standard `.vtt`/`.srt`. |
| `scripts/write_transcript.py` | Apply index-keyed corrections back into a file, preserving format/timestamps/cue count. |
| `scripts/convert_transcript.py` | Generate and validate synchronized `.srt`, `.vtt`, and `.ttml` files from the corrected source. |
| `scripts/ado_attach_files.py` | Optionally attach generated caption files to an ADO work item using Azure CLI authentication. |
| `scripts/captions.js` | (Optional) Upload the corrected track to YouTube via the Data API. See the YouTube upload section. |
| `references/glossary.json` | Known-correct tech/brand terms + common mistranscriptions. Grows over time. |

## Routing guardrails

- Use this skill for caption correction, caption-file conversion, and delivery of corrected
  caption files.
- Use `vtt-metadata` when the user wants titles, a YouTube description, chapters, or metadata
  written into ADO fields. Do not run both skills unless the user asks for both deliverables.
- Use `video-staging` when the user provides a video and wants the full YouTube staging and ADO
  creation workflow, rather than caption-only delivery.

## Workflow

### Step 1 — Parse & detect format

Run the parser to get a loss-less, structured view of every cue:

```
python <PLUGIN_ROOT>/skills/transcript-proofread/scripts/parse_transcript.py <FILE> --output cues.json
```

> **Path note:** `<PLUGIN_ROOT>` is `plugins/devrel-studios` when running from the source repo,
> or `.github/plugins/devrel-studios` after workspace installation.

Each cue has an `index`, `timestamp`, and `text`.

**Detect raw YouTube-ASR files:** if cue text contains inline word-timing tags (e.g.
`<00:00:02.720><c> across</c>`) or the same lines repeat 2–3× (rolling captions), this is a raw
YouTube auto-caption download. It must be **cleaned** into a standard, upload-ready file (Step 5)
before returning it. Read the transcript's actual words (ignore the tags/duplication) when
proofreading.

### Step 2 — Load the glossary

Read `references/glossary.json`. For each entry, `canonical` is the correct form and `variants`
are common wrong spellings that should be auto-corrected to it (case-insensitive, whole-word).

### Step 3 — Proofread every cue

Read the **full** transcript for context (a term's correct spelling often depends on
surrounding words). For each cue text:

- Apply glossary variant → canonical replacements (auto).
- Fix obvious misspellings, brand casing, and light punctuation/grammar (auto for
  high-confidence, otherwise queue for confirmation).
- Use your own up-to-date knowledge of tech products and news to catch brand names not yet in
  the glossary — you should know that "Fabriq" in a data/analytics context means Microsoft
  "Fabric". Queue these as **ambiguous** for confirmation if they're not already glossary
  entries.

Build a list of proposed changes: `{cue index, timestamp, before → after, reason,
auto|confirm}`.

### Step 4 — Confirm ambiguous items

Present **auto-applied** changes and **needs-confirmation** changes separately:

```
## ✅ Auto-applied (high-confidence tech/brand & spelling)
| Cue | Time | Before → After | Reason |
|-----|------|----------------|--------|
| 4 | 0:32 | Fabriq → Fabric | brand name (glossary) |
| 9 | 1:15 | Co-pilot → Copilot | brand name (glossary) |

## ❓ Please confirm (ambiguous)
| # | Cue | Time | Proposed | Reason |
|---|-----|------|----------|--------|
| 1 | 12 | 2:03 | Delta → Databricks Delta? | unclear proper noun |
```

Ask the user to confirm, reject, or edit each ambiguous item. Accept batch answers
(e.g. "1 and 3 yes, 2 no").

### Step 5 — Produce the clean, upload-ready corrected file

The returned file must be a **clean, standard caption file** (one cue per spoken line, no
rolling duplicates, no word-timing tags) — it will be handed to someone who re-uploads it to
YouTube.

**For raw YouTube-ASR input** (recommended path): apply your confirmed corrections to the raw
text, then run the cleaner to emit the standard file:

```
python <PLUGIN_ROOT>/skills/transcript-proofread/scripts/clean_transcript.py <CORRECTED_FILE> --output <NAME>.corrected.vtt
```

`clean_transcript.py` strips word-timing tags, removes rolling duplicate lines, keeps correct
start/end timestamps, and re-emits a valid `.vtt` (or `.srt` if the output ends in `.srt`). It
is also safe to run on already-clean files.

**For already-clean input:** apply corrections with `write_transcript.py` (index-keyed) — it
preserves format, timestamps, and cue count:

```
python <PLUGIN_ROOT>/skills/transcript-proofread/scripts/write_transcript.py <ORIGINAL_FILE> corrections.json --output <NAME>.corrected.<ext>
```

Save the output **next to the original** as `<name>.corrected.vtt` / `.srt`. This clean file is
the deliverable to return to the user.

### Step 6 — (Optional) Produce SRT, VTT, and TTML

When the user asks for a caption package or multiple output formats, generate all requested
formats from the corrected file:

```
python <PLUGIN_ROOT>/skills/transcript-proofread/scripts/convert_transcript.py <CORRECTED_FILE> --formats srt,vtt,ttml
```

The converter keeps the corrected source file unchanged, writes the other formats beside it by
default, and validates that every output has the same cue count, timestamps, and text. Use
`--output-dir <DIR>` when the deliverables belong elsewhere and `--language <CODE>` for a TTML
language other than English.

### Step 7 — (Optional) Attach caption files to an ADO Episode

Only run this step when the user asks to attach the files to Azure DevOps.

1. Resolve the work item from an explicit ID or search by episode title, topic, or speaker.
2. If multiple plausible work items match, ask the user which one to use.
3. Confirm the exact work item ID and project before attaching files.
4. Verify Azure CLI is installed and authenticated with `az login`.
5. Attach the files:

```
python <PLUGIN_ROOT>/skills/transcript-proofread/scripts/ado_attach_files.py --organization devrel --project <PROJECT> --work-item-id <ID> <FILE.srt> <FILE.vtt> <FILE.ttml>
```

The script requests an Azure DevOps access token from the caller's Azure CLI session. It does
not require or persist a personal access token. Before uploading, it verifies that the target
exists and is an Episode, then skips filenames that are already attached so a retry does not
duplicate completed work. Use `--expected-work-item-type <TYPE>` only when the caller explicitly
needs a different work item type. Report authentication or API errors directly; do not claim the
files were attached unless every requested attachment succeeds.

### Step 8 — Show the change summary

Report: total cues, number of lines changed, count of auto vs confirmed changes, and the output
file path. Include the final change table. Tell the user the returned file is clean and
upload-ready.

### Step 9 — Update the glossary (learning)

When the user **confirms** a correct spelling for a term that isn't already in
`references/glossary.json`, append it:

- Add a new entry `{ "canonical": "<correct>", "variants": ["<what was in the transcript>"] }`,
  or add the observed variant to an existing entry's `variants` list.
- Only add terms the user **explicitly confirmed** — never store unconfirmed guesses.
- Keep the JSON valid; bump nothing else. This makes future runs auto-handle the term.

### Step 10 — (Optional) Upload the corrected captions to YouTube

Only if the user explicitly asks to update the video on YouTube. This modifies **live,
public-facing** captions — always confirm first.

Auth reuses the token store at `~/.copilot/youtube-tokens/<channel>.json` (shared with the
`youtube-description` skill; requires the `youtube.force-ssl` scope).

```
# See existing tracks (read-only). ASR = auto-generated (cannot be edited).
node <PLUGIN_ROOT>/skills/transcript-proofread/scripts/captions.js <channel> list <videoId>

# Add the corrected file as a new standard English track (takes precedence over ASR).
node <PLUGIN_ROOT>/skills/transcript-proofread/scripts/captions.js <channel> insert <videoId> en "English" <clean.vtt>
```

Notes:
- YouTube **auto-generated (ASR)** tracks can't be updated — insert a **new** standard track.
- Upload the **clean** file (Step 5), not the raw format.
- If tokens are expired (`invalid_grant`), tell the user to run
  `node ~/.copilot/youtube-tokens/auth.js <channel>` and retry.
- After `insert`/`update`, `captions.js` **automatically re-lists the tracks and warns** if the
  corrected track is missing, still a draft, or if YouTube still only has an auto-generated
  (ASR) track for the language (viewers may still be seeing the auto-captions). Propagation can
  take a few minutes — re-run `captions.js <channel> list <videoId>` to re-check.

## Edge cases

- **Raw YouTube-ASR format:** rolling duplicate lines + inline word-timing tags. Always clean
  it (Step 5) before returning; never hand back the raw format.
- **`[inaudible]` / garbled audio:** flag it, do not invent words.
- **`.srt` vs `.vtt` timestamps:** `.srt` uses commas (`00:00:01,000`), `.vtt` uses dots. The
  scripts handle both; the cleaner can also convert between them via the output extension.
- **Multi-line cues:** preserve line breaks within a cue; only fix the words.
- **Multi-format delivery:** generate every format from the same corrected source, then rely on
  `convert_transcript.py` validation before returning or attaching the files.
- **ADO authentication unavailable:** stop and tell the user to run `az login`; never fall back
  to embedding or requesting a PAT in the skill.
- **No changes needed:** if nothing is wrong, say so. Still return a cleaned file if the input
  was raw ASR (the cleanup itself is valuable).
- **Very long transcripts:** still read the whole thing for context; process cue-by-cue.
- **Unknown extension:** the parser sniffs for a `WEBVTT` header and falls back to `.srt`.

## Requirements

- Python 3.8+ (standard library only — no third-party packages).
- Azure CLI — only for optional ADO attachment delivery.
- Node.js — only for the optional YouTube caption upload (`scripts/captions.js`).
