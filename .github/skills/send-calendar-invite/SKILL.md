---
name: send-calendar-invite
description: >
  Use when the user wants to draft a calendar invite email for a Studios recording, live
  event, or tech check, including requests like "send calendar invite", "draft recording
  invite", "calendar email", "session invite email", "send shoot details", or when they
  provide an Episode work item and ask to schedule or notify presenters. Reads metadata
  from the ADO Episode work item, auto-detects the correct template type, builds an HTML
  email body, and opens it for copy-paste into Outlook.
  The email is sent from drstudios@microsoft.com by a human.
---

# Send Calendar Invite Email

Draft a calendar invite email from an Episode work item in the Studios ADO project. The
skill reads all metadata, selects the correct template, and outputs a ready-to-send HTML
email body for the user to copy into Outlook and send from `drstudios@microsoft.com`.

## When to Use

- User asks to send a calendar invite for a recording or event
- User provides an Episode (or Event) work item and wants to notify presenters
- User says "send calendar invite", "draft recording invite", "session invite", "send shoot details"

## Prerequisites

- `@azure-devops/mcp` MCP server configured for the `devrel` org (see `.mcp.json`)
- User has access to the **Studios** project in the `devrel` ADO org
- User has send-as permission on `drstudios@microsoft.com` in Outlook

## Required MCP Tools

| Tool | Purpose |
|------|---------|
| `ado-wit_get_work_item` | Read Episode metadata |

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

Collect email addresses from identity fields:
- `Custom.Host1` → `uniqueName`
- `Custom.Host2` → `uniqueName` (if present)
- `Custom.Additionalpresenters` (parse emails if present)
- `Custom.Additionalinvitees` (parse emails if present)
- `Custom.ContentOwner` → `uniqueName` (if present)
- `Custom.ExecutiveProducer` → `uniqueName` (if present)
- `Custom.Technicaldirector` → `uniqueName` (if present)
- `Custom.AssociateProducer` → `uniqueName` (if present)

Deduplicate the list. Show the user the To line for review.

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
| Setup / Call time | {30 min before start} |
| Executive Producer | {EP name, if set} |
| Technical Director | {TD name, if set} |
| Show Owner/Host | {Content Owner / Host1} |
| Presenter(s) | {All presenters} |
| StreamYard link | {if applicable} |
| Stage | {A, B, or C} |
| Teleprompter | {Yes/No} |
| ADO link | Episode link + ADO entitlement link |

For **host rehearsal:**

| Field | Value |
|-------|-------|
| Event | {Show/event name} |
| Location | DevRel Studios \| Building 25/Room 1332 |
| Hosts | {Host1, Host2} |
| Executive Producer | {EP name} |
| Content Owner | {Content Owner} |
| ADO link | Episode link + ADO entitlement link |

For **on-location recording:**

| Field | Value |
|-------|-------|
| Show title | {Episode title} |
| Shoot date/time | {Start – End, PT} |
| Location | {From description or ask user} |
| Executive Producer | {EP name} |
| Presenter(s) | {All presenters} |
| ADO link | Episode link + ADO entitlement link |

**Footer blocks** (include based on template):
- **In-person templates** → Wardrobe tips + Building 25 directions
- **Remote templates** → Bandwidth/environment tips + platform join instructions
- **All templates** → ADO entitlement link

**ADO access block (always include):**
```
Need access? CoreIdentity Entitlements for ADO access: Studios ADO Entitlement
https://coreidentity.microsoft.com/manage/Entitlement/entitlement/studiosadopr-gyl1
```

### Step 5 — Present for Review

Show the user:

```
From:       drstudios@microsoft.com
To:         {deduplicated recipient list}
Subject:    {formatted subject}
Start:      {start time} PT
End:        {end time} PT
Location:   {location string}
```

Plus a readable preview of the email body. Ask: "How does this look?"

### Step 6 — Output for Copy/Paste

Save the HTML to a temp file and open it in the browser:

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

## Template-Specific Intro Paragraphs

| Template | Intro |
|----------|-------|
| STUDIO_LIVESTREAM_IN_PERSON | This event will be streaming live with presenters in person in the DevRel studio Space. Be sure to arrive at the studio 30 minutes prior to your live session start time. |
| REMOTE_LIVESTREAM_STREAMYARD | This event will be streaming live through StreamYard with remote presenters. This calendar hold encompasses a tech check and the live stream time. |
| REMOTE_LIVESTREAM_TEAMS_NDI | This event will be streaming live through Teams NDI with remote presenters. This calendar hold encompasses a tech check and the live stream time. |
| HOST_REHEARSAL | This invite is for the mandatory host rehearsal for {Event Name}, which will be streaming live with hosts and presenters in person in the DevRel Studios space. We will review the show flow, go over host hand-offs, Q&A with presenters, familiarity with the stages, etc. |
| STUDIO_PRODUCTION_RECORDED | This session will be recorded in person in the DevRel studio Space. Be sure to arrive at the studio 30 minutes prior to your session start time. |
| STUDIO_GREENSCREEN_RECORDED | This session will be recorded in person on the green screen stage in the DevRel studio Space. Be sure to arrive at the studio 30 minutes prior to your session start time. |
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
- ADO datetime fields are stored in **UTC**. Convert to Pacific Time for display
  (UTC-7 during PDT / UTC-8 during PST).
- If the parent Support request has useful context (event name), fetch it using the parent
  relation.
- The skill does **NOT** send the email — it drafts it for human review and send via Outlook
  from `drstudios@microsoft.com`.
