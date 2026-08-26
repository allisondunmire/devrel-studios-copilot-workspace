---
name: wip-onenote-update
description: >
  Refresh the Development & In Planning table on the OneNote page titled
  "Thurs DevRel Bird's Eye / WIP (Work In Progress)" from DevRel Studios Azure
  DevOps projects and categorized recordings in the drstudios@microsoft.com
  calendar. Use when the user asks to update, reconcile, preview, or prepare the
  Thursday WIP agenda, Bird's Eye page, Meeting Agendas OneNote, development
  planning list, or upcoming studio projects. Preserves handwritten notes and
  requires approval before any OneNote change.
---

# Thursday WIP OneNote Update

Prepare a merged refresh of the `DEVELOPMENT & IN PLANNING` table on the recurring
OneNote page `Thurs DevRel Bird's Eye / WIP (Work In Progress) 🦅`.

The workflow is preview-first. Reading source data and preparing a proposed table are
automatic. Never create, replace, or edit OneNote content without explicit approval.

## Destination

- Section: `Meeting Agendas`
- Page: `Thurs DevRel Bird's Eye / WIP (Work In Progress) 🦅`
- Page URL:
  `https://microsoft.sharepoint.com/teams/MicrosoftDeveloperStudiosChannel9/_layouts/Doc.aspx?sourcedoc=%7b57D591DF-8B6A-4725-A47E-4E5A2C9C4A4B%7d&wd=target%28Meeting%20Agendas.one%7C1F5ADB3F-3912-4B04-A797-89513C562A80%2FThurs%20DevRel%20Bird%27s%20Eye%20%5C%2F%20WIP%20%28Work%20In%7C75D89710-D59A-4B6E-B4B8-E3FB2BEC2EB7%2F%29&wdpartid=%7b0C25D5F9-3D89-0FC1-22ED-32DCEB9F17D1%7d%7b1%7d&wdsectionfileid=%7b1F5ADB3F-3912-4B04-A797-89513C562A80%7d&end`
- Calendar: `drstudios@microsoft.com`
- Time zone: `Pacific Standard Time`
- ADO organization/project: `DevRel / Studios`

## Required current-page input

Work IQ does not currently expose OneNote page content. Before each refresh, obtain one
of these from the user:

1. A current screenshot or PDF export that shows the complete `DEVELOPMENT & IN
   PLANNING` table; or
2. Access to an already authenticated browser tab displaying the page.

Do not rely on a screenshot from a prior run. The current page is required to preserve
handwritten notes and detect manual additions. Never ask the user to provide a password,
token, or other sign-in secret through chat.

If current page content is unavailable, continue with a source-only draft when useful,
but label it clearly as unable to preserve or reconcile existing rows.

## Existing table format

Preserve this seven-column structure and column order:

| Projects | EP | Type (Series, show, event) | Relevant dates | Location | State | Notes/Action items/questions |
|---|---|---|---|---|---|---|

Preserve the page's existing visual formatting, links, highlighting, row heights, and
quarter divider rows. Do not alter `TEAM UPDATES` or `IN PRODUCTION`.

Group dated rows by Microsoft fiscal-year quarter:

- Q1: July through September
- Q2: October through December
- Q3: January through March
- Q4: April through June

Render divider labels as `FY<two-digit fiscal year> - Q<n>`. For example, September
2026 is `FY27 - Q1`, and October 2026 is `FY27 - Q2`. Place undated proposals under the
existing `PROPOSALS & other upcoming projects?` divider when present. Do not invent a
quarter for a project with no reliable date.

## ADO project rows

Query only top-level project work item types:

- `Shows`
- `Series`
- `Events`
- `Moments`
- `Support requests`

Include states `New` and `Active`. These are the top-level equivalents of development
and in-planning work. Do not query top-level projects for `Production`; that state exists
on Episodes, not on these project types.

Exclude work under these area paths:

- `Studios\Ops`
- `Studios\Test`
- `Studios\Service account`

Episodes may supply supporting dates or calendar-match evidence, but never render an
Episode as its own project row. Do not include Proposals as project rows unless the user
explicitly asks to include them for that run.

For every ADO candidate, retrieve at least:

- ID and work-item URL
- Title
- Work item type
- State
- Area path
- Executive Producer (`Custom.ExecutiveProducer`) when present
- Assigned To only as fallback evidence, never silently as the EP
- Filming Location (`Custom.FilmingLocation`) when present
- Event start/end (`Custom.Eventstarttime`, `Custom.Eventendtime`) when present
- Livestream date/time (`Custom.Livestreamdateandtime`) when present
- Related Episode publish dates (`Custom.Episodepublishdate`) when useful

Use the ADO work-item URL for the project title hyperlink. If EP is absent, show `TBD`
rather than treating Assigned To as EP. Normalize display types to `Show`, `Series`,
`Event`, `Moment`, or `Support request`.

## Calendar recording data

Read the shared calendar from the current date through December 31 of the current
calendar year. Follow every pagination link until no next page remains. Convert all
dates and times to `Pacific Standard Time`.

Include only non-cancelled events carrying at least one of these exact categories:

- `STUDIO RECORDING`
- `STREAMYARD RECORDING`
- `HYBRID RECORDING (STUDIO + TEAMS)`

Exclude events whose subjects begin with any of these labels, case-insensitively:

- `TECH CHECK`
- `HOST REHEARSAL`
- `REHEARSAL`
- `CREW INVITE`
- `SET UP` or `SETUP`
- `HOLD`

Also exclude ordinary meetings, team syncs, lunches, maintenance blocks, and events
categorized only as `IMPORTANT - DO NOT SCHEDULE OVER`, `HOLD`, or `SET UP TIME`.

Use calendar data to populate or corroborate `Relevant dates` and `Location`. Do not
create a project row solely because a recording exists: match it to one ADO project.

## Matching calendar events to projects

Normalize punctuation, parenthetical production labels, case, and repeated whitespace
before comparing titles. Match in this order:

1. Explicit ADO work-item ID or URL in the calendar subject/body.
2. Exact normalized parent project title in the calendar subject/body.
3. Exact normalized related Episode title with a known parent project.
4. A strong unique title prefix or show/series name match.

Never auto-match on date, EP, or location alone. Mark ambiguous and unmatched events for
review. Show the evidence for every proposed fuzzy match and require the user to approve
it before using the event in a row.

When several recordings match one project, combine their dates compactly in chronological
order. Preserve an existing convention such as `9/1 and ongoing` when the page already
uses it; otherwise use comma-separated `M/d` dates or an `M/d-M/d` range for consecutive
days. Use `TBD` when no reliable date exists.

Normalize obvious locations for display without discarding useful detail:

- StreamYard URL or StreamYard recording -> `StreamYard`
- Building 25 Room 1332/control room -> `Studio - control room`
- Stage A, B, or C -> `Studio - Stage A`, `Studio - Stage B`, or `Studio - Stage C`
- Hybrid/Teams NDI -> retain both studio and virtual context

If ADO and calendar location or date disagree, do not silently choose one. Flag the
conflict in the preview.

## Merge rules

Match an existing row to ADO by hyperlink/ID first and normalized project title second.

For matched rows:

- Refresh the project hyperlink, EP, type, relevant dates, location, and state from
  verified source data.
- Preserve the entire existing `Notes/Action items/questions` cell by default.
- Preserve manual highlighting and formatting.
- Do not overwrite a non-empty manual value with `TBD` or blank source data.
- Flag source/manual conflicts and show both values in the preview.

For new ADO projects, propose a new row in the appropriate quarter with an empty notes
cell unless verified source content supplies a useful note.

Do not automatically remove an existing row. Propose removal only when its ADO item is
Completed, Cancelled, deleted, or no longer qualifies, and require explicit approval.
Keep unmatched manual rows and label them `Manual/unmatched` in the preview.

Map ADO states for page display:

- `New` -> `In planning`
- `Active` -> retain the existing page state when meaningful; otherwise `In planning`

Do not infer `On hold` from a calendar hold. Use an ADO state or preserve the current
manual state.

## Preview

Show these sections before requesting approval:

1. **Proposed table** in the existing seven-column format, grouped by quarter.
2. **Changes** with separate counts and lists for added, refreshed, unchanged, proposed
   removals, unmatched manual rows, ambiguous calendar matches, and conflicts.
3. **Source gaps** for missing EPs, dates, locations, ADO links, or page content.
4. **Excluded calendar items** summarized by reason without exposing private unrelated
   calendar details.

For every changed field, identify its source as `ADO`, `Calendar`, or `Preserved from
OneNote`. A request to inspect, prepare, reconcile, or preview is not approval to edit.

Ask for explicit approval naming the number of rows to add, refresh, and remove. Allow
approval of all proposed changes or a specific list of project IDs/titles.

## Applying an approved update

Use direct OneNote or browser editing only when an authenticated, supported write tool is
available. Re-read or re-inspect the current table immediately before editing. If page
content changed after the preview, stop and prepare a fresh merge.

Update only `DEVELOPMENT & IN PLANNING`. Never replace the full page. Preserve the page
title, objectives, intake instructions, links, `TEAM UPDATES`, `IN PRODUCTION`, and all
other sections.

If no supported OneNote write path is available, provide the approved table in a format
that can be pasted into OneNote and state plainly that it was not written automatically.
Do not claim completion until the updated page has been re-read or visually verified.

## Safety rules

- Never modify OneNote, ADO, or the calendar without explicit approval in the current
  chat.
- This skill reads ADO and calendar data; it never changes either source.
- Never ask for or transmit authentication secrets.
- Never expose unrelated private calendar details in reports.
- Never discard handwritten notes or unmatched rows silently.
- Never guess EP, project identity, dates, location, state, or quarter.
- A new screenshot/export or changed source data requires a fresh preview and approval.

## Example request

> Refresh the Development & In Planning section of the Thursday WIP OneNote page from
> ADO and the DRStudios calendar through the end of this year. Preserve my notes and show
> me a preview before changing anything.