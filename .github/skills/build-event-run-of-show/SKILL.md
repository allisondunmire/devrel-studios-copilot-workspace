---
name: build-event-run-of-show
description: >
  Use when the user wants to build or populate a DevRel Studios Run of Show
  workbook from an event website, including requests like "build the Run of
  Show", "fill this ROS spreadsheet from the event site", or "copy the agenda
  into our production workbook". Extracts the public schedule and presenters,
  confirms production-only mappings such as session type and stage, then updates
  the existing Excel workbook while preserving its formulas and data validation.
---

# Build Event Run of Show

Turn a published event agenda into a production-ready DevRel Studios Run of
Show (ROS) in an existing Excel workbook. Treat the event site as the source for
public program facts and the workbook as the source of truth for production
schema, formulas, formatting, and allowed dropdown values.

## Context resolution

Parameters this skill needs:

- `event_source` - the event website, agenda page, or supplied agenda document.
  Resolve from an explicit URL or file in the user's request.
- `workbook_target` - the existing `.xlsx` or `.xlsm` ROS workbook to update.
  Resolve from an explicit local path, attachment, OneDrive URL, or SharePoint
  URL in the user's request.
- `agenda_scope` - which public agenda blocks belong in the production ROS.
  Resolve from the user's request or confirm after presenting the available
  choices.
- `production_mappings` - workbook-specific values for fields the public source
  does not authoritatively provide, especially session type and stage location.
  Resolve from the workbook's allowed values plus explicit user confirmation.
- `event_timezone` - the timezone used by agenda times. Use a timezone stated by
  the event source or user; otherwise ask.

Resolution rules:

1. Prefer values explicitly supplied by the user.
2. For a bare workbook filename or relative path, resolve it through the active
   workspace or attachment context before checking the process working
   directory.
3. If either `event_source` or `workbook_target` is missing, ask for it.
4. If more than one worksheet or table could be the ROS target, show their names
   and headers and ask the user to choose.
5. Never guess a production mapping that is not supported by the source or
   workbook. Recommend a mapping and get confirmation.
6. Stop if the workbook cannot be read or updated with the user's existing
   permissions. Do not create a replacement workbook unless the user asks.

## Required capabilities

- Web or browser access to read the event source
- Spreadsheet tooling that can inspect and preserve Excel formulas, tables,
  styles, comments, and data validation
- Authenticated Microsoft 365 access when the workbook is hosted in OneDrive or
  SharePoint

Prefer coauthoring-safe Microsoft 365 file APIs for cloud-hosted workbooks. Use
browser editing only when the file API is unavailable, and verify that the
cloud save completes.

## Workflow

### 1. Read the event source

Extract every agenda block in source order:

| Field | Rule |
|---|---|
| Start time | Preserve the published time |
| End time | Preserve the published time |
| Session name | Preserve the published title |
| Presenter(s) | Preserve published names and order |
| Public category | Capture labels such as Keynote, Deep Dive, Panel, Break, or Lunch |
| Venue | Capture the published venue separately from stage |
| Source | Keep the source URL or document reference for provenance |

Also capture the event date and timezone if stated. Do not infer a timezone from
the user's current timezone.

### 2. Inspect the workbook before editing

Identify:

- The ROS worksheet and table by semantic headers such as `Session Start Time`,
  `Session End Time`, `Session Type`, `Stage Location`, `Session Name`, and
  `Presenter(s)`
- Existing populated rows
- Table bounds and available blank rows
- Formula columns and their source formulas
- Data-validation ranges and exact allowed dropdown values
- Date and time number formats
- Protected sheets, external links, macros, and named ranges

For `.xlsm`, preserve VBA. If the workbook contains external links, do not use a
save path that strips cached values or link metadata.

### 3. Normalize and preview the agenda

Create a proposed table containing:

`Start | End | Public category | Proposed session type | Proposed stage |
Session name | Presenter(s) | Notes`

Before writing, show the user:

1. The number and time range of extracted blocks.
2. The available scope choices when the source contains non-broadcast items:
   - **Broadcast program only** - sessions plus on-air breaks and meals
   - **Full public agenda** - also includes check-in, networking, and reception
3. Every unresolved or inferred production mapping.

Ask one concise grouped clarification when possible rather than asking about
each row separately.

### 4. Map public facts to production fields

Public event metadata and production metadata are different. Apply these rules:

- Use a public category directly only when it exactly matches an allowed
  workbook value.
- If the event explicitly supports both in-person and virtual attendance,
  `Hybrid` may be recommended for live program sessions, but still confirm the
  mapping.
- Map an AMA or audience-question segment to `Q&A` only when that option is
  allowed.
- Map breaks and meals to `Slate` only after confirming that the production
  wants those blocks represented on air.
- A venue such as "Microsoft Campus - Redmond, Washington" is not a stage.
  When no stage is published, ask the user to choose an allowed stage value. If
  they choose `Other`, put the venue in Notes.
- Never invent lower thirds, calls to action, session IDs, speaker titles, or
  internal production assignments.

Use the workbook's exact dropdown spelling and capitalization.

### 5. Update the workbook

Write only to the confirmed ROS table and only for the selected agenda scope.

1. Store start and end times as Excel time values, not display strings.
2. Preserve formulas in calculated columns. Translate the nearest valid table
   formula to each populated row instead of hardcoding its displayed result.
3. Preserve existing data validation, styles, number formats, conditional
   formatting, comments, and table definitions.
4. If more rows are needed, extend the table and validation ranges using the
   workbook's existing conventions.
5. Do not overwrite unrelated sheets such as video details, scheduling,
   speakers, or promos unless the user explicitly includes them.
6. Record material assumptions and the public venue in the existing Notes or
   comments convention. Include the source URL when doing so does not conflict
   with the template.

### 6. Validate before saving

Confirm all of the following:

- Workbook row count equals the approved agenda block count.
- First and last rows match the approved scope and published schedule.
- Session names and presenters match the source.
- Every dropdown-backed value is in the workbook's allowed list.
- Start times precede end times and adjacent blocks have no unexpected overlap
  or gap.
- Formula cells remain formulas and calculate to the expected durations and
  session IDs.
- No formula cell evaluates to an Excel error.
- Workbook sheets, tables, validations, and formulas outside the target range
  are unchanged.

Use the workbook's native calculation engine when available. If formulas cannot
be recalculated, state that limitation rather than claiming full validation.

### 7. Save and verify persistence

For a cloud workbook, replace or update the same target only after the preview
is confirmed. Reopen or reread the saved workbook and verify a representative
first, middle, and last row. Confirm the cloud UI or API reports the file as
saved before reporting completion.

Remove temporary local copies after successful persistence.

## Output

Return:

- Workbook link or path
- Worksheet and table updated
- Number of agenda blocks written
- Included time range
- Confirmed session-type and stage mappings
- Any intentionally blank production fields
- Any validation limitation or remaining user action

## Stop conditions

Pause and ask rather than guessing when:

- The event source has conflicting schedules or no authoritative times.
- The event timezone is unknown.
- The user has not chosen between broadcast-only and full-agenda scope.
- A production field has multiple plausible dropdown values.
- Existing workbook rows contain data that would be overwritten.
- The workbook is protected, checked out, locked, or cannot be safely saved.

## Routing guardrails

- If the user wants ADO Episode work items created from an existing ROS, use
  `create-event-episodes`.
- If the user wants a new generic spreadsheet rather than an existing Studios
  ROS populated, use the available spreadsheet-creation workflow.
- If the user only wants event data summarized and no workbook update, perform a
  read-only extraction instead of invoking this side-effecting workflow.
