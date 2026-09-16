---
name: create-event-episodes
description: >
  Use when the user wants to ingest a session list and create matching Episode work items
  under an ADO Event, including requests like "create episodes under this event", "add
  episodes to event <ID>", "set up the sessions for this event", "spin up episodes from
  this table/ROS", or when they paste a list of topics and speakers for an event or show.
  Ingests a pasted Topic/Speaker table, Loop or Excel export, or run-of-show, populates
  metadata, lets child-task automation fire, verifies cascading children, and notifies the
  scheduling owner. Falls back to
  manually replicating the child-task template if the automation doesn't fire.
---

# Create Event Episodes

Turn an ingested session list into fully-formed ADO Episodes under an **Event**,
then let the studio's automation build each Episode's child-task tree. The skill:
**ingests** flexible input → **normalizes** it to a confirmed episode table →
**creates** Episodes under `Studios\Events` (which triggers the child-task flow) →
**verifies** the cascading children landed → **falls back** to the embedded child
templates if they didn't → **assigns** triage owners → **notifies** scheduling.

## The Core Insight (why this skill exists)

The studio runs a **Power Automate flow** (it acts as the **Tracy Myles** service
account, `v-tmyles@microsoft.com`) that auto-creates an Episode's child tasks
~30–60s after the Episode is created. Verified behavior:

- The flow **only fires when the Episode is created with area path
  `Studios\Events`**. Creating under the root `Studios` area and *moving* it to
  `Studios\Events` afterward does **not** fire it (the create-time trigger filter
  never matches, and create-event hooks don't replay on existing items).
- When it fires it creates child tasks **Scheduling, Editing, Uploading,
  Publishing**, inherits the parent's area + iteration path, and **auto-assigns
  Scheduling → Allison Dunmire**. The other tasks are left unassigned.
- **Thumbnails** is inconsistent — some episodes get one, the verified test run
  did not. Treat its presence as optional.
- Verified 2026-05-29: test Episode 231939 (area `Studios\Events`) → children
  231940–231943 created by Tracy Myles ~52s later; Scheduling auto-assigned to
  Allison.

⚠️ If the flow doesn't fire (wrong area path, flow disabled), use the **manual
child templates** in the Fallback section — don't leave Episodes childless.

## Input / Ingestion Contract

This skill **revolves around ingested data**. Accept whatever the user pastes and
normalize it to the canonical episode record below. **Never fabricate** a value —
if it isn't in the input (or an invite, or something the user said), leave it
blank / `TBD` and ask.

### Accepted input formats
- **2-column table** (the common Loop/Teams paste): `Topic | Speaker(s)`.
- **Wider table**: any of `Topic, Speaker(s), Host, Recording date/time, Publish
  date, StreamYard link, Notes` as columns (map by header name).
- **Run-of-show doc**: extract one episode per session row; ignore transitions,
  breaks, and intros unless the user says otherwise.
- **Plain list**: lines like `Topic — Speaker` or `Topic: Speaker`.

### Canonical episode record (what each row normalizes to)
| Field | Required | Maps to (ADO) | Notes |
|---|---|---|---|
| `topic` | ✅ | `System.Title` | The Episode title |
| `speakers` | ✅ | `Custom.Remotepresenters` (text) or `Custom.Host1/2` (identity) | Remote presenters by default; in-studio hosts go to Host1/Host2 |
| `recording_start` / `recording_end` | — | `Custom.Recordingstartdateandtime` / `…enddateandtime` | From invite or ROS if present |
| `publish_date` | — | `Custom.Episodepublishdate` | |
| `streamyard_link` | — | `Custom.StreamyardLink` | Usually filled from Work IQ (Step 3), not the paste |
| `notes` | — | `Custom.Notes` | |

> **Always echo the normalized table back to the user for confirmation before
> creating anything.** Flag any spelling corrections (against an invite) and any
> blanks you're leaving for them to fill.

## Event-Level Inputs (apply to all episodes)

| Field | Description | Example |
|---|---|---|
| **Parent Event ID** | The ADO `Events` work item | `222161` |
| **Iteration path** | Quarter bucket for episodes + children | `Studios\FY26\H2\Q4` |
| **EP** | `Custom.ExecutiveProducer` (identity email) | `catomiss@microsoft.com` |
| **Content Owner** | `Custom.ContentOwner` (identity email) | `jefritz@microsoft.com` |
| **Filming location** | `Custom.FilmingLocation` (picklist) | `Streamyard (with producer assigned by DevRel Studios)` |
| **Editor-task owner** | Who triages Editing/Uploading/Publishing (+Thumbnails) | `v-jolynndeal@microsoft.com` (Jo Lynn Deal) |

Confirm these once; they're usually identical across an event.

## Workflow

### Step 1: Ingest & normalize
Parse the user's input into the canonical episode table. Echo it back and get a
thumbs-up. Do **not** invent speakers, times, or links — leave gaps visible.

### Step 2: Fetch & validate the parent Event
`ado-wit_get_work_item` on the parent ID. Confirm it's an `Events` type in project
`Studios`; note the livestream/event date. If episodes already exist under it,
list them and ask before adding more.

### Step 3: Enrich with StreamYard links (Work IQ)
If there are pre-records, ask Work IQ for the scheduling owner's invites:

```
work-iq-ask_work_iq:
  "Find the pre-record calendar invites Allison Dunmire sent for <event>. For
   each: session topic, presenter(s), date/time, and the StreamYard link."
```

Map links to episodes by topic/presenter. The studio often reuses **one**
StreamYard link for a recording block — apply it only to episodes with a matching
invite; leave the rest blank. Surface any extra presenter found in an invite and
confirm before adding.

### Step 4: Create Episodes (area path = `Studios\Events`!)
Create all episodes in one `ado-wit_add_child_work_items` call:
- `parentId` = Event ID, `workItemType` = `Episode`, `project` = `Studios`
- per item: `title` = topic, `description` = speaker(s),
  `areaPath` = `Studios\\Events`  ← **required to trigger the flow**,
  `iterationPath` = the iteration path

Capture the returned Episode IDs. Then batch-populate metadata via
`ado-wit_update_work_items_batch` (`op:"Add"`, `path:"/fields/<ref>"`): EP,
Content Owner, Filming Location, Remote presenters, StreamYard link (where it
exists), Host1/Host2, recording times / publish date if known. (Boolean required
fields default to `0` — no need to set them.)

### Step 5: VERIFY the cascading children (do not skip)
The whole point is the children. Verify, don't assume:

1. Wait ~60s after creation.
2. For each Episode, `ado-wit_get_work_item` (`expand:"relations"`) and count
   `System.LinkTypes.Hierarchy-Forward` (Child) links.
3. Batch-read the children with `ado-wit_get_work_items_batch_by_ids`
   (fields: `System.WorkItemType`, `System.CreatedBy`, `System.AssignedTo`,
   `System.AreaPath`, `System.IterationPath`) and check:
   - Created by `v-tmyles@microsoft.com` (confirms it was the automation).
   - Types present include **Scheduling, Editing, Uploading, Publishing**
     (Thumbnails optional).
   - **Scheduling is assigned to Allison.**
   - Area = `Studios\Events`, Iteration = the event's iteration.
4. If an Episode has **0 children after ~2 min**, retry once (wait another 60s).
   Still nothing → go to **Fallback (Step 6)** for that Episode only.
5. Report a per-episode verification table (✅ auto / ⚠️ manual / ❌ missing).

### Step 6: Fallback — manually replicate the child template
Only for Episodes where the flow didn't fire. For each, create the child set —
**one `ado-wit_add_child_work_items` call per type** (the tool takes a single
`workItemType` per call), each with `areaPath:"Studios\\Events"` +
`iterationPath` + `title` = the type name:

`Scheduling`, `Editing`, `Uploading`, `Publishing` (and `Thumbnails` if the user
wants it). See **Child Task Templates** for fields. Then do Step 7 assignments
(including Scheduling → Allison, which the flow would normally have done).

### Step 7: Assign editor-role tasks (triage)
The flow assigns Scheduling automatically; if you created it manually, assign it
to Allison. For **Editing / Uploading / Publishing (+Thumbnails)** there is **no
fixed per-type default** — historically they follow whoever's editing the event.
Ask the user who owns them and batch-assign via `ado-wit_update_work_items_batch`
(`/fields/System.AssignedTo`). Common answer: route all to a triage owner
(e.g., Jo Lynn Deal).

### Step 8: Notify the scheduling owner
Offer to comment on the parent Event tagging scheduling. Get the GUID with
`ado-core_get_identity_ids`, then `ado-wit_add_work_item_comment` (`format:Html`):

```
<a href="#" data-vss-mention="version:2.0,{GUID}">@Name</a> the N episodes for
this event have been created … <ul><li>{id} — {topic} ({speakers})</li>…</ul>
```

### Step 9: Confirm
Show the final table (below).

## Output Format

```
## 🎬 Episodes created under Event {parentId} — {event title}
| Topic | Episode ID | Children | Source | Scheduling | Editor tasks |
|---|---|---|---|---|---|
| WinForms | 231899 | 4 ✅ | auto (Tracy Myles) | Allison | Jo Lynn |
| Foundry  | 231903 | 5 ⚠️ | manual fallback   | Allison | Jo Lynn |

Area path: Studios\Events · Iteration: Studios\FY26\H2\Q4
Notified: @Allison Dunmire on {parentId} (comment {commentId})
Gaps left for you: {episode} StreamYard link (no invite found), …
```

## Field Reference (from the live ADO process)

### Episode (`Studios.Episode`)
- **States:** New → Pre Production → Production → Post Production → Publication →
  EP action required → Hold → Completed → Cancelled
- **Hard-required:** `System.Title`, `System.State` (default `New`),
  `System.AreaPath`, `System.IterationPath`, and booleans
  `Custom.YouTubeshorts`, `Custom.Thumbnails`, `Custom.Upwork`,
  `Custom.Teleprompter` (all default `0` — auto-satisfied on create).
- **Key fields to populate:**

| Field | Ref | Type |
|---|---|---|
| Host 1 / Host 2 | `Custom.Host1` / `Custom.Host2` | identity |
| Remote presenters | `Custom.Remotepresenters` | text (`Name; Name`) |
| Additional presenters | `Custom.Additionalpresenters` | text |
| Filming Location | `Custom.FilmingLocation` | picklist |
| Executive Producer | `Custom.ExecutiveProducer` | identity |
| Content Owner | `Custom.ContentOwner` | identity |
| Associate Producer | `Custom.AssociateProducer` | identity |
| Technical director | `Custom.Technicaldirector` | identity |
| Streamyard Link | `Custom.StreamyardLink` | URL/text |
| Recording start / end | `Custom.Recordingstartdateandtime` / `…enddateandtime` | datetime |
| Episode publish date | `Custom.Episodepublishdate` | datetime |
| YouTube Channel / playlist | `Custom.YouTubeChannel` / `Custom.YouTubeplaylist` | picklist / text |
| Notes | `Custom.Notes` | text |

> Picklist options (FilmingLocation, YouTubeChannel, Publishingplatform) aren't
> returned inline by the type API. Known good FilmingLocation value:
> `Streamyard (with producer assigned by DevRel Studios)`. If unsure of an
> option, read a recent Episode or check the field in ADO.

## Child Task Templates (for manual fallback)

All five share: `System.Title` = the type name, `System.State` = `New`,
`System.AreaPath` = `Studios\Events`, `System.IterationPath` = event iteration.
Optional `Custom.Notes` and `Custom.Episodepublishdate` on every type.

| Type (`ref`) | Default assignee | Extra required (defaulted) | Useful optional fields | States |
|---|---|---|---|---|
| **Scheduling** (`Studios.Scheduling`) | **Allison Dunmire** `v-adunmire@microsoft.com` | — | `Custom.Recordingstartdateandtime`, `…enddateandtime` | New → In progress → Hold → Completed → Cancelled |
| **Editing** (`Studios.Editing`) | editor / triage owner | `Custom.YouTubeshorts`=0, `Custom.Needsreviewprocessed`=0 | `Custom.EditNotes`, `Custom.ShowId`, `Custom.ExecutiveProducer`, `Custom.ContentOwner`, `Custom.Total#ofvideos` | New → In progress → Needs review → Hold → Completed → Cancelled |
| **Thumbnails** (`Studios.Thumbnails`) | editor / triage owner | — | `Custom.Total#ofvideos` | New → In progress → In review → Hold → Completed → Cancelled |
| **Uploading** (`Studios.Uploading`) | editor / triage owner | `Custom.YouTubeshorts`=0 | `Custom.YouTubeChannel`, `Custom.ShowId`, `Custom.Publishingplatform`, `Custom.Total#ofvideos` | New → In progress → Hold → Completed → Cancelled |
| **Publishing** (`Studios.Publishing`) | editor / triage owner | `Custom.YouTubeshorts`=0 | `Custom.YouTubeChannel`, `Custom.Publishingplatform`, `Custom.Total#ofvideos` | New → In progress → Hold → Completed → Cancelled |

Manual creation per type (repeat for each Episode that needs it):
```
ado-wit_add_child_work_items
  parentId: <episodeId>
  workItemType: "Scheduling"   # one type per call
  project: "Studios"
  items: [{ title: "Scheduling",
            areaPath: "Studios\\Events",
            iterationPath: "Studios\\FY26\\H2\\Q4" }]
```

## Requirements

- **Azure DevOps MCP** (`ado-*`): `ado-wit_get_work_item`,
  `ado-wit_get_work_item_type`, `ado-wit_add_child_work_items`,
  `ado-wit_update_work_items_batch`, `ado-wit_get_work_items_batch_by_ids`,
  `ado-wit_add_work_item_comment`, `ado-core_get_identity_ids`. Org `devrel`,
  project `Studios`.
- **Work IQ MCP** (`work-iq-ask_work_iq`) — StreamYard links / invite enrichment.
- Access to the Studios ADO project + the scheduling owner's invite history.

If the ADO MCP is unavailable, output the normalized episode table + planned
field values for manual entry.

## Edge Cases

- **Episode created under root `Studios`** — flow won't fire; moving later won't
  help. Recreate under `Studios\Events`, or use the manual fallback.
- **Children missing / partial** — Step 5 retries once, then falls back per
  episode. Thumbnails is inconsistent; add it manually only if the user wants it.
- **No invite for an episode** — leave StreamYard blank; don't reuse another
  session's link unless the user confirms it's the shared block link.
- **Extra presenter in an invite** — surface and confirm before adding.
- **Identity not found** by `ado-core_get_identity_ids` — try the full
  `v-…@microsoft.com` UPN; if still unresolved, ask Work IQ for the alias (vendor
  accounts use the `v-` prefix).
- **Messy/partial ingest** — if a required field (topic or speaker) is missing
  for a row, show it as `TBD` and ask; never guess.
- **Duplicate run** — episodes already under the event → list and confirm first.

## Reference

| Item | Detail |
|---|---|
| Org / Project | `devrel` / `Studios` |
| Episode type | `Episode` (ref `Studios.Episode`) |
| Child types | `Thumbnails`, `Scheduling`, `Editing`, `Uploading`, `Publishing` |
| Automation account | Tracy Myles `v-tmyles@microsoft.com` (Power Automate flow) |
| Trigger condition | Episode **created** with area path `Studios\Events` |
| Auto-assignment | Scheduling → Allison Dunmire `v-adunmire@microsoft.com` |
| Editor-task triage (example) | Jo Lynn Deal `v-jolynndeal@microsoft.com` |
| Identity field input | accepts `…@microsoft.com` email / UPN |
| Comment mention | `<a href="#" data-vss-mention="version:2.0,{GUID}">@Name</a>` (GUID from `ado-core_get_identity_ids`) |
| Verified test | Episode 231939 → children 231940–231943 by Tracy Myles ~52s later |
