---
name: live-show-calendar
description: >
  Preview, create, and update DRStudios Outlook calendar appointments and invitations from a SharePoint or OneDrive
  Excel run-of-show workbook. Use when the user asks to turn a ROS, run of show, LiveShow table, or Excel schedule into
  calendar blocks; correct session times; add presenters or production attendees; enable Teams links and response
  tracking; apply Outlook categories; or manage tech checks in drstudios@microsoft.com. Routes Teams NDI, In Studio,
  and Hybrid rows to their session-type templates, applies setup buffers, checks for duplicates, and always requires
  explicit approval before calendar writes.
---

# Live Show Calendar Appointments

Create calendar blocks in `drstudios@microsoft.com` from the named Excel table `LiveShow`.
The workflow is preview-first: reading and validation are automatic, but calendar writes are not.

## What the user provides

For each run, require:

- A SharePoint or OneDrive link to the Excel Run of Show workbook.
- Confirmation of the event date if it is not explicit on the `Live Show` worksheet.
- Confirmation of the time zone if it is not explicit in the workbook. Use `Pacific Standard Time`
  when the user says Pacific time; this Outlook identifier handles PST/PDT automatically.

Do not reuse rows, dates, event IDs, presenters, or times from a previous workbook. Always reread
the supplied workbook and create a fresh preview.

If the user identifies a different worksheet or table as authoritative, such as a draft sheet,
inspect that source and explicitly confirm the override in the preview. Do not combine rows from
the default and override sources or silently fall back to a stale sheet. If qualifying rows have
blank Session IDs, keep them blocked unless the user explicitly approves a deterministic ID
assignment. Assign approved IDs chronologically from the next unused ID and report that the
workbook itself remains unchanged.

## Source columns

Read only these columns from the `LiveShow` table on the `Live Show` worksheet:

- `Session Start Time`
- `Session End Time`
- `Session Duration`
- `Session Type`
- `Session ID`
- `Stage Location`
- `Session Name`
- `Presenter(s)`
- `Lower Thirds`
- `Call to Action`
- `Notes`

Ignore scheduling worksheets and tables. Read the event date from the `Live Show` worksheet
header. The workbook filename may corroborate the date, but must not silently override the sheet.

## Qualifying rows and buffers

Match `Session Type` case-insensitively after trimming whitespace:

| Session Type | Appointment start | Appointment end |
|---|---|---|
| `In Studio` | Session Start Time minus 30 minutes | Session End Time |
| `Teams NDI` | Session Start Time minus 20 minutes | Session End Time |
| `Hybrid` | Session Start Time minus 30 minutes | Session End Time |

Skip all other session types, including `Host Transition`. Report skipped row counts in the
preview. Never infer an unknown type's buffer.

## Workflow

### 1. Read the workbook

Use Microsoft 365/Work IQ with the user-provided SharePoint or OneDrive file URL. Inspect the
`Live Show` worksheet and `LiveShow` table without modifying the workbook.

Extract all source columns, the worksheet event date, and the source workbook URL. Preserve
the displayed cell text for names, notes, calls to action, and lower thirds.

### 2. Confirm date and time zone

- If the sheet date is absent, ambiguous, or conflicts with the filename, ask the user.
- If the workbook has no explicit time zone, ask the user. Do not guess from locale or mailbox.
- Use a Windows/Outlook time-zone name such as `Pacific Standard Time` in calendar payloads.
- Apply the same confirmed date and time zone to all rows unless the user explicitly says otherwise.

### 3. Validate

Block creation for a row when any of these are true:

- `Session ID`, `Session Name`, `Session Start Time`, or `Session End Time` is blank.
- Start or end is not a valid time.
- Session End Time is not after Session Start Time.
- Session ID is duplicated among qualifying rows.
- Session Type is unknown.

For `Hybrid`, also block the row unless every presenter in `Presenter(s)` has exactly one
case-insensitive location suffix:

- `(In Studio)` for an in-person presenter.
- `(Teams NDI)` for a remote presenter.

Separate presenters with semicolons, for example:

`Alex Rivera (In Studio); Sam Lee (Teams NDI)`

Require at least one presenter of each type. Strip the suffixes when rendering presenter names.
Do not guess a presenter's location from company, email, notes, or prior events.

Flag, but do not automatically block, overlapping appointment windows caused by setup buffers.
Never add attendees to livestream-session appointments unless the user explicitly requests them.
Tech-check invitations follow the separate attendee preview and approval rules below.

### 4. Render the appointments

Select the template by normalized `Session Type`, then replace every placeholder with workbook
data:

| Session Type | Template |
|---|---|
| `Teams NDI` | [references/teams-ndi-template.md](references/teams-ndi-template.md) |
| `In Studio` | [references/in-studio-template.md](references/in-studio-template.md) |
| `Hybrid` | [references/hybrid-template.md](references/hybrid-template.md) |

Send each rendered body as Graph HTML (`body.contentType: html`). Preserve the templates' inline
styles, table attributes, links, and semantic HTML exactly; do not convert the body to Markdown or
plain text. The inline formatting is intentionally compatible with Outlook desktop's Word HTML
renderer as well as Outlook on the web.

In every livestream-session body, render `Session End Time` in the confirmed event time zone and
render `Session Length` from the displayed `Session Duration` workbook value. If `Session Duration`
is blank, derive it from the validated session start and end times and identify it as derived in the
preview. Never calculate session length from the buffered appointment start time.

`Floor Plan Image URL` is an optional skill-level resource, not required workbook metadata. When a
confirmed HTTPS image URL is available, render it in `In Studio` and `Hybrid` invitations only.
Until then, remove the entire floor-plan image paragraph from the rendered HTML. Never leave the
placeholder in an invitation, invent a URL, or include the floor plan in `Teams NDI` invitations.

### Tech check templates

Tech checks are separate calendar items from livestream-session appointments. Do not apply the
session setup buffers to tech-check times; use the exact tech-check start and end approved by the
user. Route by normalized session type:

| Session Type | Template |
|---|---|
| `In Studio` | [references/tech-check-in-studio-template.md](references/tech-check-in-studio-template.md) |
| `Teams NDI` | [references/tech-check-teams-ndi-template.md](references/tech-check-teams-ndi-template.md) |
| `Hybrid` | [references/tech-check-hybrid-template.md](references/tech-check-hybrid-template.md) |

For a Hybrid tech check, apply the same presenter-location validation used for Hybrid livestream
sessions. Render separate `In-Person Presenter(s)` and `Remote Presenter(s)` values and require at
least one of each.

For a Teams NDI tech check, create an Outlook online meeting with `isOnlineMeeting: true` and
`onlineMeetingProvider: teamsForBusiness`. Never invent or reuse a join URL. After creation, read
the event's generated `onlineMeeting.joinUrl`, then set both `location.displayName` and
`location.locationUri` to that exact URL. Warn in the preview that this two-step process can send
an initial invitation followed by a location update to all attendees. Verify that the Location URL
and `onlineMeeting.joinUrl` match exactly.

For a Hybrid tech check, create an Outlook online meeting with `isOnlineMeeting: true` and
`onlineMeetingProvider: teamsForBusiness`, but preserve the combined Room 1332 and Teams NDI text
from the Hybrid tech-check template in the Location field. The generated Teams join information
remains available in the invitation body and Join button. Verify both the physical Location text
and the generated `onlineMeeting.joinUrl` after creation.

For every tech check, require an explicit date, start time, end time, time zone, and attendee list.
The source workbook may provide them, but do not infer a tech-check schedule from the live-session
times. Preview the subject, date, start, end, location, required attendees, optional attendees, and
conflicts before requesting approval. State that approval will send invitations from
`drstudios@microsoft.com`. Set `responseRequested: true` whenever the attendee list is non-empty.

For Hybrid rows, compute both call times: `Appointment Start Time` is 30 minutes before the
session and `Remote Call Time` is 20 minutes before the session. The calendar appointment starts
at the earlier in-person call time.

Before rendering any appointment, obtain these event-level values from the workbook when
explicitly present, otherwise ask the user once per workbook:

- `Event Name`
- `Show Owner`
- `Executive Producer`
- `Technical Director`
- `ADO Project Label`
- `ADO Project URL`

Apply the same values to all appointment types in that workbook unless the workbook explicitly
defines row-specific overrides. Never carry these values over from a prior workbook or silently
use values from a previously processed event.

Use:

- Calendar owner: `drstudios@microsoft.com`
- Subject and HTML body: the reference template
- Location: `Stage Location`
- Show as: `busy`
- Attendees: empty
- Response requested: `false` only while the event has no attendees
- Reminder: 15 minutes before the computed appointment start
- Transaction ID: `drstudios-live-show-<YYYY-MM-DD>-<Session ID>`

Response tracking is mandatory for every invitation sent from `drstudios@microsoft.com`. Whenever
an event is created with attendees or attendees are added to an existing attendee-free appointment,
explicitly set `responseRequested: true` in the same approved write. Do not rely on the service
default. Include the response-request setting in the preview and verify it by direct event fetch.

### 5. Check existing calendar items

Before showing the final preview, read the DRStudios calendar for the full event date. Mark a row
as a duplicate and exclude it from creation if an existing event has either:

- the same deterministic transaction ID, when available; or
- the same date, Session ID in the subject, and computed start/end times.

Show possible time conflicts separately. A conflict is not permission to overwrite, move, or
delete an existing event.

### 6. Preview and request approval

Show a table with:

| Create? | Session ID | Subject | Start | End | Time zone | Location | Conflict/status |
|---|---|---|---|---|---|---|---|

Then report qualifying, skipped, invalid, duplicate, and ready-to-create counts. State clearly
that appointments have no attendees and no invitations will be sent.

Ask for explicit approval naming the number of appointments, date, calendar, and time zone.
Accept approval for all ready rows or a specific list of Session IDs. A request to inspect,
preview, prepare, or validate is not approval to create.

### 7. Create approved appointments

Create one event at a time in:

`/users/drstudios@microsoft.com/events`

Use the approved preview values and the Work IQ create-entity operation. Never fall back to
`/me/events`; that would write to the user's personal calendar.

If service-mailbox write permission fails, stop immediately. Do not retry against another
calendar. Explain that the user needs delegate write access or the standard Office 365 Outlook
Power Automate connector, which is already known to support this shared calendar.

After each successful create, retain the returned event ID and web link. If a later create fails,
stop the batch and report exactly which Session IDs succeeded, failed, and were not attempted.

### 8. Verify

Re-read the DRStudios calendar for the event date and verify each newly created event's subject,
start, end, time zone, location, attendees, and `responseRequested` value. An attendee-free event
must have `responseRequested: false`; an event with one or more attendees must have
`responseRequested: true`. Return a concise result table with the event links. Do not modify the
source workbook or mark rows as sent.

## Updating existing appointments

When the user supplies revised template language, render a fresh preview for every affected
appointment. Locate existing events by returned event ID first, deterministic transaction ID
second, and exact Session ID/date/time match third. Never identify an event by time alone.

Show the proposed subject and body changes and obtain explicit approval before updating. Patch
only the approved fields; preserve start, end, time zone, location, attendees, `responseRequested`,
reminder, and busy status unless the user explicitly approves changes to them. A subject- or
body-only update must not disable response tracking or reset attendee response statuses. Verify
every updated event, including its `responseRequested` value, by direct event fetch after the write.
Never create a replacement event when the intended existing event cannot be identified uniquely.

When an approved update adds the first attendee to an attendee-free appointment, include
`responseRequested: true` in that update and show it in the preview. When modifying any existing
meeting with attendees, verify that `responseRequested` is true; if it is false, report the issue
and obtain explicit approval before enabling it because that correction can send meeting updates.

### Correcting the schedule

When the user changes event or session timing, preview every affected appointment's current and
proposed start and end in the confirmed time zone. Shift the rendered call times, remote call times,
session start times, and session times in the HTML body by the same amount. Preserve all unrelated
body content and event fields. Warn that changing a meeting that already has attendees can send an
update; attendee-free appointments do not send invitations. Fetch each event immediately before
the approved update, use its latest ETag, patch only `start`, `end`, and `body`, and verify both the
calendar window and all displayed body times.

### Adding attendees to livestream sessions

When the user explicitly asks to send existing livestream appointments, build required and optional
attendee lists by role and session. Resolve identities from the current workbook or event ADO item,
then verify each address with ADO identity data or the Microsoft directory. Never infer an email
alias. The standard role mapping, when requested by the user, is:

| Role | Attendance |
|---|---|
| Presenter(s) for that session | Required |
| Technical Director | Required |
| Executive Producer | Required |
| Show Owner | Optional |
| Associate Producer | Optional |

Add any explicitly requested shared mailbox with the attendance type the user specifies. Read the
Associate Producer from the current event's ADO field when it is not present in the workbook. Show
the resolved name, address, and attendance type in the preview. If a presenter address is missing,
recommend waiting to send the complete invitation; adding that presenter later can send another
meeting update to existing attendees. Do not send a partial invitation unless the user explicitly
approves that tradeoff.

After approval, fetch each event immediately before updating and use its latest ETag. Patch only
`attendees` and `responseRequested: true`, preserving all other fields. Stop on the first failure.
Directly verify the exact recipient set, required/optional types, response tracking, and preserved
event fields. Exchange may canonicalize aliases to primary SMTP addresses; accept this only when
the resolved directory identity is the intended person and report the canonical address.

### Enabling Teams on an existing session

For an approved existing Teams NDI session, set `isOnlineMeeting: true`,
`onlineMeetingProvider: teamsForBusiness`, the complete attendee list, and
`responseRequested: true` in one update whenever Graph supports it. This avoids an initial
invitation followed by a second meeting update. Never invent or reuse a join URL. Preserve the
session's approved Location text unless the user requests a change. Verify that Graph generated a
non-empty `onlineMeeting.joinUrl`, retained the invitation body, and added Teams join information.
If Graph requires a second write, stop and preview the extra attendee notification before proceeding.

### Applying Outlook categories

Treat categories as mailbox-local labels. Reuse the exact name of an existing category on the
shared calendar, preserve any existing categories, and add the requested category at most once.
If the shared mailbox blocks master-category color reads, use an existing correctly categorized
event as the reference and state that the color could not be independently verified through Graph.
Preview the exact session-type scope and exclude other types explicitly. After approval, fetch the
latest ETag, patch only `categories`, retry a change-key conflict with one fresh read, and verify the
target and excluded events. A category-only update should not send a meeting update, but still
requires calendar-write approval.

## Safety rules

- Never create, update, or delete calendar items without explicit approval in the current chat.
- Never write to a personal calendar as a fallback.
- Never add presenters or other attendees to livestream-session appointments unless the user
  explicitly requests and approves them.
- For tech checks, add only the required and optional attendees shown in the approved preview.
- Never send an invitation with attendees unless `responseRequested` is explicitly set to `true`.
- Never create unknown session types.
- Never substitute one session type's template for another.
- A changed workbook requires a fresh preview and fresh approval.
- Do not expose private calendar details while reporting conflict checks.

## Example future request

The user can invoke this skill by saying:

> Create the Teams NDI calendar appointments from this Excel Run of Show in the DRStudios
> calendar: `<SharePoint or OneDrive workbook link>`

First inspect and preview. Do not create appointments until the user approves the exact preview.