---
name: send-calendar-invite
description: >
  Use when the user wants to draft a calendar invite email for a Studios recording, live
  event, or tech check, including requests like "send calendar invite", "draft recording
  invite", "calendar email", "session invite email", "send shoot details", or when they
  provide an Episode work item and ask to schedule or notify presenters. Reads metadata
  from the ADO Episode work item, auto-detects the correct template type, builds an HTML
  email body, sends or prepares the invite from drstudios@microsoft.com, and updates the
  Episode, Scheduling task, and tagged ADO comment after a verified successful send.
---

# Send Calendar Invite Email

Create a calendar invite from an Episode work item in the Studios ADO project. The skill
reads all metadata, selects the correct template, sends or prepares a ready-to-send HTML
invite from `drstudios@microsoft.com`, then updates ADO after the send is verified.

## When to Use

- User asks to send a calendar invite for a recording or event
- User provides an Episode (or Event) work item and wants to notify presenters
- User says "send calendar invite", "draft recording invite", "session invite", "send shoot details"

## Prerequisites

- `@azure-devops/mcp` MCP server configured for the `devrel` org (see `.mcp.json`)
- User has access to the **Studios** project in the `devrel` ADO org
- User has send-as permission on `drstudios@microsoft.com` in Outlook
- Microsoft 365 calendar write access, or user confirmation after a manual Outlook send

## Required MCP Tools

| Tool | Purpose |
|------|---------|
| `ado-wit_get_work_item` | Read Episode metadata, children, and verification state |
| ADO work-item write | Update Episode and Scheduling states |
| ADO comment write | Add the tagged post-send comment |
| Microsoft 365 calendar read/write | Check duplicates, send, and verify the invite |

## Input

- **ADO work item** (required) — URL or ID number
- Accepted types: **Episode** (primary) or **Event** (parent-level)
- If an **Event** is provided, fetch it and check for required metadata. Events typically
  lack episode-level details (presenter, stage, time). If key fields are missing, push back
  and ask the user to provide the Episode ID or supply the missing details manually.

## Workflow

### Step 1 — Fetch the Episode

Use `ado-wit_get_work_item` with:
- `organization`: `devrel`
- `project`: `Studios`
- `id`: extracted from the URL or provided directly

Extract these fields:

| Detail | ADO Field | Notes |
|--------|-----------|-------|
| Title | `System.Title` | Session/show title |
| Host / Presenter 1 | `Custom.Host1` | Identity — extract `displayName` + `uniqueName` |
| Host 2 | `Custom.Host2` | Identity (optional) |
| Additional presenters | `Custom.Additionalpresenters` | Text (optional) |
| Remote presenters | `Custom.Remotepresenters` | Text (optional) |
| Additional invitees | `Custom.Additionalinvitees` | Text (optional) |
| Content Owner | `Custom.ContentOwner` | Identity (optional) |
| Executive Producer | `Custom.ExecutiveProducer` | Identity (optional) |
| Technical Director | `Custom.Technicaldirector` | Identity (optional) |
| Associate Producer | `Custom.AssociateProducer` | Identity (optional) |
| Filming Location | `Custom.FilmingLocation` | "Studio", "Studio (Self Service)", "Remote", or "On Location" |
| Stage | `Custom.Stage` | A, B, or C |
| Recording Start | `Custom.Recordingstartdateandtime` | UTC — convert to PT |
| Recording End | `Custom.Recordingenddateandtime` | UTC — convert to PT (optional) |
| StreamYard link | `Custom.StreamyardLink` | URL (optional) |
| Teleprompter | `Custom.Teleprompter` | Boolean |
| # presenters on camera | `Custom.#ofpresentersoncameraatthesametime` | Number |
| Description | `System.Description` | HTML — may contain additional notes |
| Show / Series Title | Parent `System.Title` | Fetch the parent work item and use its audience-facing title |
| ADO link | Constructed | `https://dev.azure.com/devrel/Studios/_workitems/edit/{id}` |

**Time conversion:** ADO datetime fields are stored in UTC. Convert to Pacific Time
(UTC-7 during PDT / UTC-8 during PST) for display.

**Technical Director is required:** Before building or sending an invite, verify that
`Custom.Technicaldirector` contains an assigned person. If it is blank, stop and ask the
user who should be assigned as Technical Director. Prompt the user to add that person to
the Episode in ADO, or, when the user authorizes the change and ADO write access is
available, update the field for them. Re-fetch the Episode to verify the assignment before
sending. Never send an invite with a blank or omitted Technical Director.

For calendar categorization, these people are DevRel-assigned Technical Directors:
- Matt Scholz
- Cameron Tomisser
- Kaitlin McKinnon
- Sara Finkelstein
- Aurea Astro
- Golnaz Alibeigi

An assigned TD outside this list is a third-party TD, even when that person is also the
Show Owner. A third-party TD still satisfies the requirement that every invite have an
assigned Technical Director.

### Step 2 — Determine the Template Type

Use this decision tree:

```
Is this a Host Rehearsal?
  → User indicates rehearsal (ask if ambiguous)
  → Template: HOST_REHEARSAL

Is FilmingLocation == "On Location"?
  → Template: ON_LOCATION_RECORDING

Is FilmingLocation == "Studio" or "Studio (Self Service)"?
  ├── Is this a live event? (ask user)
  │   ├── Yes → Template: STUDIO_LIVESTREAM_IN_PERSON
  │   └── No → Has green screen? (ask user)
  │       ├── Yes → Template: STUDIO_GREENSCREEN_RECORDED
  │       └── No → Template: STUDIO_PRODUCTION_RECORDED
  └──

Is FilmingLocation == "Remote" or not set?
  ├── Is this a live event? (ask user if not obvious)
  │   ├── Yes + StreamYard link → Template: REMOTE_LIVESTREAM_STREAMYARD
  │   ├── Yes + no StreamYard  → Template: REMOTE_LIVESTREAM_TEAMS_NDI
  │   └── No
  │       ├── StreamYard link present       → Template: REMOTE_PRODUCTION_STREAMYARD
  │       ├── Remote + in-person presenters → Template: HYBRID_STUDIO_TEAMS_NDI
  │       └── Default                       → Template: REMOTE_PRODUCTION_TEAMS_NDI
```

If the template cannot be auto-detected, ask the user to pick from:
1. Studio livestream session (in-person)
2. Remote livestream session – StreamYard
3. Remote livestream session – Teams NDI
4. Host rehearsal
5. Studio production (recorded, in-person)
6. Studio production – green screen (recorded, in-person)
7. Remote production – StreamYard
8. Remote production – Teams NDI
9. Hybrid production: in-studio and Teams NDI
10. On-location recording

### Step 3 — Determine Recipients

Add these as **required attendees**:
- `Custom.Host1` → `uniqueName`
- `Custom.Host2` → `uniqueName` (if present)
- `Custom.Additionalpresenters` (parse emails if present)
- `Custom.Additionalinvitees` (parse emails if present)
- `Custom.ContentOwner` → `uniqueName` (if present)
- `Custom.Technicaldirector` → `uniqueName`
- `Custom.AssociateProducer` → `uniqueName` (if present)

Add `Custom.ExecutiveProducer` as an **optional attendee**. If the Executive Producer is
also the Technical Director, include that person only once as a required attendee in the
Technical Director role.

Deduplicate attendees by email address. When one person appears in both required and
optional roles, required takes precedence. Show the user the required and optional
attendee lines for review.

### Step 4 — Build the Email

#### Subject line format

For **recorded StreamYard productions** (`REMOTE_PRODUCTION_STREAMYARD`):

`{Show/Series Title} | {Episode Title} (remote recording - StreamYard)`

Use audience-facing titles in the subject:
- Remove administrative fiscal-year suffixes from the parent title, such as `FY27`.
- Remove trailing audience or routing tags from the Episode title, such as `| SMB`.
- Do not change the titles stored in ADO.

Example for Episode 237854:

`Fabric Tech Talk Fridays | How Azure Pricing Works (remote recording - StreamYard)`

For **recorded in-studio productions** (`STUDIO_PRODUCTION_RECORDED` and
`STUDIO_GREENSCREEN_RECORDED`):

`{Show/Series Title} | {Episode Title} (Studio recording - in person)`

Apply the same audience-facing title cleanup rules described above.

For all other templates, use:

`[DevRel Studios] {Title} — {Date} {Time} PT`

Example: `[DevRel Studios] Steph Rogers - Studio C Recording — June 12, 2026 1:00 PM PT`

#### Email body structure

**Header block:**
```
IMPORTANT SHOOT INFORMATION – PLEASE READ THOROUGHLY:
{Template-specific intro paragraph}
For rescheduling or questions, please email drstudios@microsoft.com
```

**Details table** (HTML `<table>`). Fields vary by template:

For **live events** (studio or remote):

| Field | Value |
|-------|-------|
| Event | {parent event title or show name} |
| Session title | {Episode title} |
| Session number | {Episode ID} |
| Presenter(s) | {Host1, Host2, Additional presenters} |
| Presenter(s) Call time | {20-30 min before start} |
| Session time | {Start – End, PT} |
| Location | {Studio + stage, or StreamYard link, or Teams NDI} |
| Show Owner | {Content Owner} |
| Executive Producer | {EP name} |
| Technical Director | {TD name} |
| ADO project | Episode link + ADO entitlement link |

For **standard recordings** (studio or remote):

| Field | Value |
|-------|-------|
| Show title | {Episode title} |
| Shoot date/time | {Start – End, PT} |
| Executive Producer | {EP name, if set} |
| Technical Director | {TD name, if set} |
| Show Owner/Host | {Content Owner / Host1} |
| Presenter(s) | {All presenters} |
| StreamYard link | {if applicable} |
| Stage | {A, B, or C} |
| Teleprompter | {Yes/No} |
| ADO link | Episode link + ADO entitlement link |

The `Technical Director` row is mandatory. Never omit it from a standard recording body.
Standard-recording invites cover only the ADO recording start and end times. Do not add
a setup/call-time row, extend the event for setup, or instruct attendees to arrive before
the recording time. This does not change the explicit call-time rules for live events.

For **host rehearsal:**

| Field | Value |
|-------|-------|
| Event | {Show/event name} |
| Location | DevRel Studios \| Building 25/Room 1332 |
| Hosts | {Host1, Host2} |
| Executive Producer | {EP name} |
| Technical Director | {TD name} |
| Content Owner | {Content Owner} |
| ADO link | Episode link + ADO entitlement link |

For **on-location recording:**

| Field | Value |
|-------|-------|
| Show title | {Episode title} |
| Shoot date/time | {Start – End, PT} |
| Location | {From description or ask user} |
| Executive Producer | {EP name} |
| Technical Director | {TD name} |
| Presenter(s) | {All presenters} |
| ADO link | Episode link + ADO entitlement link |

The `Technical Director` row is mandatory in every invite body, including live events,
standard recordings, host rehearsals, and on-location recordings.

**Footer blocks** (include based on template):
- **In-person templates** → Wardrobe tips + Building 25 directions
- **Remote templates** → Bandwidth/environment tips + platform join instructions
- **All templates** → ADO entitlement link

**ADO access block (always include):**
```
Need access? CoreIdentity Entitlements for ADO access: Studios ADO Entitlement
https://coreidentity.microsoft.com/manage/Entitlement/entitlement/studiosadopr-gyl1
```

#### Calendar category

Apply Outlook categories according to the [Studio calendar color-coding wiki](https://dev.azure.com/devrel/Studios/_wiki/wikis/Studios.wiki/11411/Studio-calendar-color-coding):

| Condition | Outlook category | Wiki color |
|-----------|------------------|------------|
| Unconfirmed calendar hold | `HOLD` | Yellow |
| Studio recording or studio live session with a DevRel TD | `STUDIO RECORDING` | Dark green |
| StreamYard recording or live session with a DevRel TD | `STREAMYARD RECORDING` | Light green |
| Teams NDI or hybrid recording/live session with a DevRel TD | `HYBRID RECORDING (STUDIO + TEAMS)` | Light blue |
| Assigned TD is not in the DevRel TD list above | `3RD PARTY PRODUCER (NOT DEVREL)` | Purple |
| Stage is B or C | Add `STAGE c` | Pink |

`3RD PARTY PRODUCER (NOT DEVREL)` replaces the platform category; do not also apply
`STUDIO RECORDING`, `STREAMYARD RECORDING`, or `HYBRID RECORDING (STUDIO + TEAMS)`.
`STAGE c` is additive for Stage B/C and may appear with either a platform category or the
third-party category. The literal category name is `STAGE c` for both Stage B and Stage C.

`SET UP TIME` (grey) and `IMPORTANT - DO NOT SCHEDULE OVER` (red) apply only to separate
setup/prep and block events; do not add them to a recording invite. If the filming format
does not map to this table, such as an on-location recording, ask the user which category
to apply before sending.

### Step 5 — Present for Review

Show the user:

```
From:       drstudios@microsoft.com
Required:   {deduplicated required attendee list}
Optional:   {Executive Producer, unless also Technical Director}
Subject:    {formatted subject}
Start:      {start time} PT
End:        {end time} PT
Location:   {location string}
Categories: {exact Outlook category list}
```

Plus a readable preview of the email body. Ask: "How does this look?"

### Step 6 — Send the Invite

Create or update the calendar event on `drstudios@microsoft.com`. Before creating a new
event, query the shared calendar for the recording window and do not create a duplicate.
If a matching HOLD exists, convert it into the final invite instead.

When updating or converting an existing event, replace its managed production categories
with the categories selected above. Remove stale or incompatible values including `HOLD`,
`STUDIO RECORDING`, `STREAMYARD RECORDING`,
`HYBRID RECORDING (STUDIO + TEAMS)`, `3RD PARTY PRODUCER (NOT DEVREL)`, and `STAGE c`
before applying the new set. Preserve unrelated categories only when they are still valid;
ask the user when their purpose is unclear.

After the calendar write, re-fetch the event and verify:
- The event is not cancelled and no longer has a HOLD subject prefix or category
- Organizer is `drstudios@microsoft.com`
- Subject, start/end time, location, and attendees match the Episode
- Categories exactly match the category rules and contain no stale managed category
- The Technical Director is required and appears in the body
- `responseRequested` is `true`

Only treat the invite as successfully sent after this verification passes.

If direct calendar creation is unavailable, save the HTML to a temp file and open it in
the browser for manual Outlook entry:

```powershell
$file = Join-Path $env:TEMP "studio-invite-body.html"
$htmlBody | Out-File -FilePath $file -Encoding utf8
Start-Process $file
```

**User action:**
1. Browser opens with rendered email body
2. Ctrl+A → Ctrl+C in the browser tab
3. Create new calendar invite in Outlook from `drstudios@microsoft.com`
4. Set Subject, Start/End time, Location, and Recipients from the metadata summary
5. Ctrl+V in the description/body field
6. Review and Send

After the user confirms the manual invite was sent, continue to Step 7.

### Step 7 — Update ADO After Successful Send

Run this step after every logical invite send or update, but only after Step 6 verifies a
direct calendar write or the user confirms a manual send. Do not change ADO when invite
creation or update fails or remains unverified. A logical send/update may require multiple
calendar API writes to finish validation; run this ADO step once after the complete invite
is verified.

For an Episode work item:

1. Set the Episode `System.State` to `Production`.
2. Fetch the Episode's direct children and identify the child whose
  `System.WorkItemType` is `Scheduling`. Set only that child's `System.State` to
  `Completed`. Do not infer the Scheduling child from relation order or update Editing,
  Uploading, Publishing, Graphics, or Thumbnail children.
3. Add a new HTML comment to the Episode for every verified invite send or update. Do not
  skip the comment because the Episode is already in `Production` or Scheduling is already
  `Completed`. Use `data-vss-mention` links so ADO registers real person mentions:

  ```text
  {EP mention} {Show Owner mention, if present} {TD mention} Calendar invite has been sent for {filming configuration} recording on {M/D/YY} from {start-end time} PT; {TD display name} is the assigned TD.
  ```

  Example:

  ```text
  Calendar invite has been sent for StreamYard recording on 10/2/26 from 1-2 PM PT; Matt Scholz is the assigned TD.
  ```

  - Use `Custom.ExecutiveProducer` for the EP.
  - Use `Custom.ContentOwner` for the Show Owner when populated.
  - Use `Custom.Technicaldirector` for the TD mention and display name.
  - Tag the EP, Show Owner, and TD. If one person fills multiple roles, mention that person
    only once.
  - Use the audience-facing filming configuration, such as `Studio`, `remote
    StreamYard`, `remote Teams NDI`, `hybrid Studio/Teams NDI`, or `on-location`.
  - Format the date as `M/D/YY` and use the full recording start-end window in Pacific
    Time, for example `1-2 PM PT` or `10-11:30 AM PT`.
  - Mention the assigned `Custom.Technicaldirector` and also use the TD's display name in
    the closing clause. Do not substitute an untagged plain-text name for the TD mention.
4. Re-fetch the Episode, Scheduling child, and latest comment. Verify the Episode is
  `Production`, Scheduling is `Completed`, and the comment's `mentions` collection
  contains the expected EP, Show Owner (when distinct), and Technical Director identity
  IDs.

If no Scheduling child exists, complete the Episode state/comment updates and report that
Scheduling could not be updated. If one ADO update fails, retry or report that individual
failure rather than claiming the full workflow completed.

## Template-Specific Intro Paragraphs

| Template | Intro |
|----------|-------|
| STUDIO_LIVESTREAM_IN_PERSON | This event will be streaming live with presenters in person in the DevRel studio Space. Be sure to arrive at the studio 30 minutes prior to your live session start time. |
| REMOTE_LIVESTREAM_STREAMYARD | This event will be streaming live through StreamYard with remote presenters. This calendar hold encompasses a tech check and the live stream time. |
| REMOTE_LIVESTREAM_TEAMS_NDI | This event will be streaming live through Teams NDI with remote presenters. This calendar hold encompasses a tech check and the live stream time. |
| HOST_REHEARSAL | This invite is for the mandatory host rehearsal for {Event Name}, which will be streaming live with hosts and presenters in person in the DevRel Studios space. We will review the show flow, go over host hand-offs, Q&A with presenters, familiarity with the stages, etc. |
| STUDIO_PRODUCTION_RECORDED | This session will be recorded in person in the DevRel studio Space. |
| STUDIO_GREENSCREEN_RECORDED | This session will be recorded in person on the green screen stage in the DevRel studio Space. |
| REMOTE_PRODUCTION_STREAMYARD | This virtual session will be recorded using StreamYard (a web-based platform - no download necessary). Remote presenters should join the StreamYard link at the meeting start time. |
| REMOTE_PRODUCTION_TEAMS_NDI | This virtual session will be recorded using Teams NDI. Remote presenters should join the Teams meeting link at the meeting start time. |
| HYBRID_STUDIO_TEAMS_NDI | This session is a hybrid production with some presenters in the DevRel studio Space and others joining remotely via Teams NDI. |
| ON_LOCATION_RECORDING | This session will be recorded on location. See details below for venue information and arrival instructions. |

## Standard Footer Content

### Wardrobe Tips (in-person templates only)

```
Don't:
- Wear large logo shirts, or non-Microsoft logos unless it's related to your technology topic.
- Wear shirts that have a busy print, or a tight pattern.
- Wear solid black, or solid white.
- Wear hats, unless worn for religious observance.

Do:
- Wear color, they can be muted, color is always good on camera.
- Ensure your clothes are wrinkle free – HD catches everything.
- Wear simple jewelry, or none. Large jewelry can be distracting and create additional noise.
```

### Building 25 Directions (in-person templates only)

```
Microsoft Building 25: 15700 NE 39th St, Redmond, WA 98052
DevRel Studios (formerly the Ch9 Studio) is located in Building 25, Room 1332.
- Building 25 has a north and south wing. DevRel Studios is in the south wing, toward the
  left as you are facing the front of Bldg 25.
- If you are not a vendor or FTE, you will need to allow time for check in at reception.
- Sponsor for reception to contact by email upon your arrival will be Matt Scholz – he will
  meet you in the lobby after you are checked in.
- FTE and vendors can register their vehicles for on-site parking in advance here:
  https://parking.microsoft.com/
```

### Remote Tips (remote templates only)

```
Tips for remote presenters:
- Remote video production utilizes a large amount of internet bandwidth. Please close any
  unnecessary applications and browser tabs.
- Use a wired ethernet connection if possible.
- Use headphones or earbuds to prevent echo.
- Choose a quiet, well-lit location with a clean background.
- Position your camera at eye level.
```

## Important Notes

- Identity fields in ADO (Host1, Host2, EP, TD, etc.) return objects with `displayName`
  and `uniqueName` (email) — always extract both.
- Some fields may be null/missing — skip them gracefully in the output table.
- The Technical Director is the exception to optional missing fields: it must be assigned,
  included as a required attendee, and shown in the body before an invite is sent.
- The Executive Producer is always optional unless that person is also the Technical
  Director, in which case include them once as required.
- ADO datetime fields are stored in **UTC**. Convert to Pacific Time for display
  (UTC-7 during PDT / UTC-8 during PST).
- If the parent Support request has useful context (event name), fetch it using the parent
  relation.
- After a verified direct send, or after the user confirms a manual send, update the
  Episode state, Scheduling child, and tagged ADO comment as described in Step 7.
