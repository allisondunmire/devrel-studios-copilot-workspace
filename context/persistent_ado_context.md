# Azure DevOps Agent Context - DevRel Studios Project

This file provides persistent context for GitHub Copilot agent mode when working with the DevRel Studios Azure DevOps project.

## Project Overview

- **Organization**: DevRel
- **Project**: Studios
- **Project ID**: d583c19b-5f23-4bed-a650-1cc43436e5c9
- **URL**: https://dev.azure.com/devrel/Studios
- **Purpose**: Video production workflow management from pre-production through publication
- **Teams**:
  - **Studios Team** (ID: `f75f8afd-097e-46bc-aa33-b74f1d01d648`) — Video production (Shows, Series, Events, etc.)
  - **Studios Ops** (ID: `11551163-628b-4fe4-ae15-e8a92753bf3b`) — Operational work (ADO platform, automation, documentation, security, AI innovation, studio infrastructure). Area path: `Studios\Ops`
  - **Service accounts** (ID: `ea6d963c-560f-44d9-8f2f-b13f25780013`) — Azure Logic App Standard automation flows

## Project Structure

### Process Template
- **Type**: Custom process template (loosely based on Agile)
- **Focus**: Content publishing and video production workflows
- **Custom work item types**: Uses custom work item types that are more intuitive to video production
- **No sprints**: Uses half and quarterly iterations (FY## H1, H2 - Q1, Q2, Q3, Q4) for reporting and analytics

### Work Item Hierarchy

#### Top-level Work Items (Studios Project)
1. **Shows** - Ongoing video series (remain Active throughout entire FY)
2. **Series** - Structured content series
3. **Events** - Event-based video content
4. **Moments** - For impactful stand-alone videos
   - **API work item type name is `Moments` (plural).** Use exactly `Moments` when creating via the API — the singular `Moment` will fail.
5. **Support requests** - For support requests

#### Organization-Adjacent Work Items (NOT Studios Project)
- **Content** - Organization-level content tracking (tracked by org, not owned by Studios)

**Valid children of top-level work items:**
- **Episode** - Primary child work item for Shows, Series, Events, Moments, and Support requests
- **General** - General purpose work items (organizational, pre-event, post-event work) - *Universal child (can be child of any work item type)*
- **Scheduling** - Scheduling work items - *Universal child (can be child of any work item type)*
- **Graphics** - Graphics and design work (show/series/event branding)
- **Thumbnails** - Thumbnail creation (top-level branding)
- **Postmortem** - Post-project analysis / comments
- **Proposal** - Staging/planning area
- **Upwork** - External Upwork contractor support

#### Mid-level work Items
- **Episode** - Primary child work item for Shows, Series, Events, Moments, and Support requests
  - **Valid children:** Scheduling, Editing, Shorts, Uploading, Publishing, Thumbnails, Graphics, Upwork, Proposal, General
  - **Note:** Scheduling and General are universal children (allowed under any work item type)

- **General** - General purpose work items
  - **Valid children:** Scheduling, General (nested organization)
  - **Note:** General items under Events are typically "Pre Event" or "Post Event" organizational containers
  - **Note:** Scheduling and General are universal children (allowed under any work item type)

- **Proposal** - Planning and staging work items
  - **Valid children:** Scheduling, General
  - **Note:** Some Proposals (e.g., MVP Creator Proposals) may become Episodes
  - **Note:** Scheduling and General are universal children (allowed under any work item type)

#### Low-level Work Items (Workflow Steps)
- **Scheduling** - For scheduling (child of Episode or General)
- **Editing** - For editing (child of Episode)
  - **Multiple Editing siblings per Episode:** Automation creates a default Editing WI and, when applicable, additional Editing WIs for distinct deliverable types (e.g., "Editing - Shorts" for YouTube Shorts). EPs may also create additional Editing WIs for other deliverable types as needed. Each Editing WI tracks its own `Custom.Total#ofvideos` count.
  - **Nesting allowed:** Editing can have Editing children (for complex multi-stage editing workflows)
- **Shorts** - YouTube Shorts editing work items (child of Episode)
  - Created automatically by automation when Episode's `Custom.YouTubeshorts` toggle is true
  - Titled "Editing - Shorts" or "Editing: Shorts"
  - Tracks its own `Custom.Total#ofvideos` count
- **Uploading** - For uploading (child of Episode)
- **Publishing** - For publishing (child of Episode)
- **Thumbnails** - For video thumbnails (child of Episode or top-level items)
  - **Nesting allowed:** Thumbnails can have Thumbnails children (for revision tracking)
- **Graphics** - Graphics and design work (child of Episode or top-level items)
  - **Nesting allowed:** Graphics can have Graphics children (for revision tracking or complex designs)
- **Upwork** - For external Upwork support (child of Episode or top-level items)
- **Postmortem** - Post-project analysis / comments (child of top-level items)

#### Multiple Editing Siblings Pattern
**An Episode can have multiple Editing work items as direct children, each representing a distinct deliverable type:**
- **Editing** (default) — The standard video edit, created automatically by automation flows
- **Editing - Shorts** — YouTube Shorts edits, created automatically when the Episode's `Custom.YouTubeshorts` toggle is true (replaces the previous boolean trickle-down behavior)
- **Editing - [Other]** — EPs may manually create additional Editing WIs for other deliverable types (clips, trailers, alternate cuts, etc.)

Each Editing WI carries a `Custom.Total#ofvideos` field (integer) indicating how many videos that edit job produces. Uploading and Publishing work items remain singular per Episode and cover all deliverable types.

#### Nesting Guidelines
**Same-type nesting is allowed for specific work item types, but should be used sparingly:**
- **Graphics → Graphics** - For tracking revisions or breaking down complex design work
- **Thumbnails → Thumbnails** - For tracking thumbnail revisions or A/B testing variants
- **Editing → Editing** - For multi-stage editing workflows (rough cut → fine cut → final)

**Note:** While nesting is technically allowed for these types, it is NOT ideal and should be tracked/monitored. Excessive nesting can make the hierarchy difficult to manage. Use queries to monitor nested work items and keep nesting to a minimum when possible.
**Note:** Multiple Editing *siblings* under an Episode (the pattern above) is distinct from nested Editing *children* under an Editing WI. Both are valid but serve different purposes.

#### Ops Work Items (Studios\Ops area path — managed by Studios Ops team)
**Ownership boundary is area path, not work item type.** Any work item type (Action, Issue, Documentation, Task, Epic) under `Studios\Ops` belongs to the Studios Ops team.

##### Epic Hierarchy (Ops top-level organizers)
Epics serve as the top-level organizational containers for all Ops work:
| Epic | ID | Purpose |
|---|---|---|
| ADO Platform & Infrastructure | #218946 | Board configuration, process template, permissions, area paths |
| Automation & Integration | #218947 | Power Automate Flows, Logic Apps, MCP server, scripts |
| Queries/Dashboards/Analytics | #218948 | Shared queries, dashboards, reporting |
| Documentation & Wiki | #218949 | Wiki pages, context files, README updates |
| AI Innovation & Experiments | #218950 | Copilot experiments, AI-assisted workflows, prototyping |
| Studio Operations | #218951 | Physical studio, equipment, facilities, vendor management |
| Communications & Outreach | #218952 | Team announcements, cross-org communications, newsletters |

##### Ops work item types (all MUST be under `Studios\Ops` area path)
- **Epic** - Top-level organizer for Ops work (see table above)
  - **Valid children:** Task, Action, Documentation, General
- **Action** - Action items
  - **Valid children:** Task, Issue, Documentation
- **Issue** - Issue items (Area path: `Studios\Ops\Issue`)
  - **Valid children:** Task
- **Documentation** - Documentation items
  - **Valid children:** Task
- **Task** - Task items

**Note:** Task, Action, Documentation, Issue, and General are universal children — they can appear as children of any work item type across both video production and Ops hierarchies.

### Team Structure & Area Path Ownership

#### Studios Team (ID: `f75f8afd-097e-46bc-aa33-b74f1d01d648`)
- **Description**: Primary video production team
- **Permissions**: Member-of 'contributors' for inheritance
- **Backlog area paths**: All `Studios\*` paths **EXCEPT** `Studios\Ops` (and its children)
- **Backlog levels**: Shows, Series, Events, Moments, Support requests → Episode → low-level workflow items

#### Studios Ops (ID: `11551163-628b-4fe4-ae15-e8a92753bf3b`)
- **Description**: Operational work — ADO platform, automation, documentation, AI innovation, studio infrastructure
- **Permissions**: Member-of 'contributors' for inheritance
- **Backlog area paths**: `Studios\Ops` (including children: `Studios\Ops\Action`, `Studios\Ops\Documentation`, `Studios\Ops\Issue`)
- **Backlog levels**: Epic → Action/Issue/Documentation → Task
- **Iteration paths**: `Studios\FY26\H1\Q1` through `Studios\FY26\H2\Q4` (quarterly cadence)

#### Service accounts (ID: `ea6d963c-560f-44d9-8f2f-b13f25780013`)
- **Description**: Azure Logic App Standard automation flows
- **Backlog area paths**: `Studios\Service account`

**Cross-team parenting prohibition**: Ops work items (`Studios\Ops`) MUST NOT be parented under video production items (Shows/Series/Events/Episodes), and vice versa. Each team's hierarchy is independent.

### Permissions
- **Admin/Contributor/Reader roles**:
  - **Admins**: Admin perms
  - **Contributors**: Non-team members with write access for their video projects
  - **Readers**: Read-only access to wiki documentation

## Misc repository Information
- **No code repositories** in this ADO project (other than Wiki)
- **Wiki**: Used as primary documentation site

## Integration Points
We have two workflows in our ADO Project: (We currently utilize both Power Automate Flows and Azure Logic Apps to provide some automation in our ADO project.)
1: Manual process = manual work is done, leverages Power Automate Flows / Azure Logic Apps for automation assistance
2: Automated process = leverages MCP Server and the VS Code Agent to perform work. Must operate in a way that does not interfere with existing Power Automate Flows / Azure Logic Apps automation

### Automation Flow Documentation
Detailed documentation for all automation flows is maintained in `ADO/Flows/`. Each markdown file describes trigger conditions, decision logic, processing steps, and hierarchy diagrams for a specific flow. Refer to these docs for the authoritative specification of each automation's behavior.

### Power Automate Flows
- **Current Power Automate Flows are used to reduce repetitive creation of children work items, and to update children work item fields when parent item is updated**
    - **Automated work item creation**: "When an episode is created" → create children work items with specific fields and values. If the Episode's `Custom.YouTubeshorts` field is true, an additional 'Editing - Shorts' work item is created as a child of the Episode (instead of trickling a boolean value to a single Editing WI)
    - **Automated updates**: "When an episode work item is updated" → update children items with specific fields and values
- **Proposal to parent work item creation**
    - **Proposal work item to parent work item**: DevRel Studios Submission Form creates a 'Proposal' work item, Flow is triggered when the Proposal work item state = 'ready for automation', Flow creates the parent Shows/Series/Events/Moments/Support requests parent work item and established the link
- **Iteration path automation**
    - **Episode iteration path**: When Episode work item is updated, calculates correct iteration path (FY/H/Q) from Episode Publish Date field and updates if needed
    - **Parent iteration path on completion**: When Shows/Series/Events/Moments/Support requests state changes to 'Completed', finds latest Episode publish date and updates parent iteration path to match. Uses tag 'auto-iteration-updated' to prevent loops

### Azure Logic Apps
- **Current Azure Logic App Flows are used to reduce repetitive creation of children work items, and to update children work item fields when parent item is updated**
    - **Automated work item creation**: When an episode is created then create children work items with specific fields and values. If the Episode's `Custom.YouTubeshorts` field is true, an additional 'Editing - Shorts' work item is created as a child of the Episode (instead of trickling a boolean value to a single Editing WI)
    - **Automated updates**: When an episode work item is updated then update children items with specific fields and values
    - **Edit needs review alert**: When an 'Editing' work item is moved to state 'Needs review' then send email notification to EP

## Common Agent Tasks

### Primary Operations
1. **Work Item Creation**:
   - Create multiple episode work items under parent Shows/Series/Events
       - Example: "Create 10 'Episode' work items under this parent 'Shows/Series/Event' work item: [work item id]"
       - Example: "Create episodes based off of this Run of Show spreadsheet (RoS) under this parent 'Shows/Series/Event' work item: [work item id]"
   - Bulk creation of related work items
   - **Important**: Always retrieve parent work item details first to inherit area path and iteration path for child work items (sans Episode work items with the 'Studios\Full course video' area path)

2. **Work Item Modification**:
   - Update states/fields of work items
   - Bulk updates across related items

3. **Data Import** (Using a .csv file of a Run of Show (RoS) spreadsheet):
   - Ingest Excel spreadsheets to create multiple work items with specific field data
   - Map spreadsheet data to work item fields

4. **Misc**:
   - Return list of work items assigned to prompter

### Workitem States

#### Proposal work items
- **Proposal**: New, Pending EP assignment, Pending data validation, Pending client action, Ready for project automation, Ingested, Cancelled, Rejected

#### Top level (Shows, Series, Events, Moments, Support requests)
- **Series/Shows/Events/Moments/Support requests**: New, Active, Hold, Completed, Cancelled

#### Mid-level (Episodes)
- **Episodes**: New, Pre production, Production, Post production, Publication, EP action required, Hold, Completed, Cancelled

#### Low-level (Scheduling, Editing, Uploading, Publishing, Thumbnails, Graphics, Upwork, General)
- **Scheduling/Editing/Uploading/Publishing/Thumbnails/Graphics/Upwork/General**: New, In progress, Completed
    - ***Editing***: Note: The 'Editing' work item type also has the state 'Needs review'

### Work item state descriptions

#### Proposal
- **New** - The proposal was created
- **Pending EP assignment** - The proposal is pending EP assignment
- **Pending data validation** - The proposal is pending EP communication with the content owner to verify submitted info
- **Pending client action** - The proposal is pending action from the content owner
- **Ready for project automation** - _This state kicks off the parent work item flow logic_
- **Ingested** - The proposal was ingested and linked to its parent item
- **Cancelled** - The proposal was cancelled
- **Rejected** - The proposal was rejected

#### Proposal work item tags for automation
- **Show** = `show`
- **Series** = `series`
- **Event** = `event`
- **Moment** = `moment`
- **Production support** = `production`
- **Post-production support** = `post`
- **Publication support** = `publication`

#### Top level (Shows, Series, Events, Moments, Support requests)
- **New** - The project was created
- **Active** - The project is active and/or on-going
- **Hold** - The project is on hold
- **Completed** - The project was completed
- **Cancelled** - The project was cancelled

#### Mid-level (Episodes)
- **New** - The episode was created
- **Pre production** - The episode is in pre-production (planning, scheduling, pending 'metadata')
- **Production** - The episode is waiting for the shoot, being shot or was just shot
- **Post production** - The episode is in post production (editing, uploading, staging for publication)
- **Publication** - The episode is pending publication on the publication date on its designated publishing platform
- **EP action required** - Something is missing or needed, EP needs to address something that's a blocker
- **Hold** - The episode is on hold for `X` reason
- **Completed** - The episode was delivered as intended and is completed
- **Cancelled** - The episode was cancelled for `X` reason

#### Low-level (Scheduling, Editing, Uploading, Publishing, Thumbnails, Graphics, Upwork, General)
- **New** - The work item was created
- **In progress** - The work item is currently in progress
- **Completed** - The work item is completed
  - `Editing work item only` **Needs review** - Used for when a video edit needs a review

## Area Paths Structure
**Area Paths:**
- `Studios\Shows` - For show content (parent path)
  - `Studios\Shows\Fabric Tech Talk Fridays` - Fabric Tech Talk Fridays show
  - `Studios\Shows\Azure Friday` - Azure Friday show
  - `Studios\Shows\Data Exposed` - Data Exposed show
  - `Studios\Shows\The Low Code Revolution` - The Low Code Revolution show
  - `Studios\Shows\One Dev Question` - One Dev Question show
  - `Studios\Shows\Open at Microsoft` - Open at Microsoft show
  - `Studios\Shows\Cozy AI Kitchen` - Cozy AI Kitchen show
  - `Studios\Shows\Sip and Sync with Azure` - Sip and Sync with Azure show
  - `Studios\Shows\Microsoft MVP Unplugged` - Microsoft MVP Unplugged show
- `Studios\Series\Beginner series` - For beginner-focused content
- `Studios\Series\Limited series` - For limited content
- `Studios\Events` - For event-based content and video projects
- `Studios\Initiatives\Moments` - For single impactful stand-alone videos
- `Studios\Initiatives\Production support` - For production support requests
- `Studios\Initiatives\Post-production support` - For post-production support requests
- `Studios\Initiatives\Publication support` - For publication support requests
- `Studios\Proposals` - For proposal items
- `Studios\Full course video` - For full course video items
- `Studios\Ops\Action` - **Ops team only** For operational actions
- `Studios\Ops\Documentation` - **Ops team only** For documentation creation or updating
- `Studios\Ops\Issue` - **Ops team only** For issues that need addressed
- `Studios\Test` - **Excluded from hygiene** Test work items
- `Studios\Service account` - **Excluded from hygiene** Service account items

**Area Path Hierarchy Structure:**
- **Level 1**: Studios (Project root)
- **Level 2**: Primary content and organizational categories
  - `Series` - For structured content series organization
  - `Shows` - For ongoing show content (has child paths for specific shows)
  - `Events` - For event-based video content
  - `Initiatives` - For larger initiatives and specialized workflows **(Moments and Support requests)**
  - `Proposals` - For content proposals and planning
  - `Full course video` - For full course video items
  - `Ops` - For operational work (managed by Studios Ops team, Epic hierarchy)
  - `Test` - **Excluded from hygiene** Test work items
  - `Service account` - **Excluded from hygiene** Service account items
- **Level 3**: Specific subcategories (where applicable)
  - `Beginner series` - Under Series for beginner-focused content
  - `Limited series` - Under Series for limited-run content
  - `Action` - Under Ops for operational action items
  - `Documentation` - Under Ops for documentation work
  - `Issue` - Under Ops for issues that need addressing
  - `Moments` - Under `/Initiatives` for impactful stand-alone videos
  - `Production support` - Under `/Initiatives` for production support requests
  - `Post production support` - Under `/Initiatives` for post-production requests
  - `Publication support` - Under `/Initiatives` for publishing support requests
  - *Shows child paths* - Under `/Shows` for show-specific area paths (Azure Friday, Data Exposed, etc.)

**Complete Area Path Structure [tree view]**
```
Studios\
├── Shows\
│   ├── Fabric Tech Talk Fridays
│   ├── Azure Friday
│   ├── Data Exposed
│   ├── The Low Code Revolution
│   ├── One Dev Question
│   ├── Open at Microsoft
│   ├── Cozy AI Kitchen
│   ├── Sip and Sync with Azure
│   └── Microsoft MVP Unplugged
├── Series\
│   ├── Beginner series
│   └── Limited series
├── Events\
├── Initiatives\
│   ├── Moments
│   ├── Production support
│   ├── Post production support
│   └── Publication support
├── Proposals\
├── Full course video\
├── Ops\
│   ├── Action
│   ├── Documentation
│   └── Issue
├── Test\               (excluded from hygiene)
└── Service account\    (excluded from hygiene)
```

**Usage Guidelines**
- **Studios\Shows** - Use for ongoing episodic show content
  - Show-specific child paths available (Azure Friday, Data Exposed, etc.)
- **Studios\Series** - Use for structured educational content series
  - **Studios\Series\Beginner series** - For beginner-focused educational content
  - **Studios\Series\Limited series** - For limited-run content series
- **Studios\Events** - Use for event-specific video content
- **Studios\Initiatives\[Category]** - Use for larger initiatives and specialized workflows
  - **Studios\Initiatives\Moments** - For impactful stand-alone videos
  - **Studios\Initiatives\Production support** - For production support requests
  - **Studios\Initiatives\Post-production support** - For post-production support requests
  - **Studios\Initiatives\Publication support** - For publication support requests
- **Studios\Proposals** - Use for content proposals and planning
- **Studios\Full course video** - For full course video items
- **Studios\Ops\[Category]** - Use for operational tasks and administrative work
  - **Studios\Ops\Action** - For operational action items
  - **Studios\Ops\Documentation** - For documentation creation or updating
  - **Studios\Ops\Issue** - For issues that need addressing
- **Studios\Test** - For test work items (excluded from hygiene)
- **Studios\Service account** - For service account items (excluded from hygiene)

## Iteration Structure
**Iteration for metrics/analytics + tracking/measuring**

### Iteration
- **Path Format**: `Studios\FY##\H#\Q#`
- **Example**: `Studios\FY26\H1\Q1`
- **Levels**:
  - Level 1: Studios (Project)
  - Level 2: FY## (Fiscal Year)
  - Level 3: H# (Half - H1/H2)
  - Level 4: Q# (Quarter - Q1/Q2/Q3/Q4)
- **Purpose**: Reporting and analytics rather than sprint planning
- **Usage**: Track work completion and production metrics by quarter

### Fiscal Year Calendar (Microsoft FY)
**Fiscal year runs July 1 - June 30**

#### FY26 Date Ranges
- **FY26 H1 Q1**: July 1, 2025 - September 30, 2025
- **FY26 H1 Q2**: October 1, 2025 - December 31, 2025
- **FY26 H2 Q3**: January 1, 2026 - March 31, 2026
- **FY26 H2 Q4**: April 1, 2026 - June 30, 2026

#### FY27 Date Ranges
- **FY27 H1 Q1**: July 1, 2026 - September 30, 2026
- **FY27 H1 Q2**: October 1, 2026 - December 31, 2026
- **FY27 H2 Q3**: January 1, 2027 - March 31, 2027
- **FY27 H2 Q4**: April 1, 2027 - June 30, 2027

### Special Iteration Paths
- **Studios\Archival** - **Excluded from hygiene** Early migration work items (used during initial ADO setup)

## Standard and custom fields
**Standard and custom work item fields for mapping**

### Shows (Top-level)
- `state` - Current state of the work item
- `assignedto` - The person assigned to the work item
- `Custom.ExecutiveProducer` - Identity field for executive producer
- `Custom.ContentOwner` - Identity field for content owner
- `Custom.AdditionalStakeholders` - Optional identity field for additional stakeholders
- `Custom.FilmingLocation` - Location where content will be produced
- `Custom.SharePoint` - Url to SharePoint
- `Custom.Figma` - Url to Figma
- `Custom.FrameIO` - Url to FrameIO (Asset management link)
- `Custom.Runofshow` - Url to Run of Show spreadsheet
- `Custom.Graphics` - Boolean flag for Azure Logic App Flow, if 'true', creates a 'Graphics' work item as a child work item for the entire show
- `Custom.Upwork` - Boolean flag for Azure Logic App Flow, if 'true', creates an 'Upwork' work item as a child work item for the entire show
- `Custom.Longformseries` - Boolean flag for Azure Logic App Flow, if 'true', creates a 'Episode' work item as a child work item with the 'Studios\Full course video' area path

### Series (Top-level)
- `state` - Current state of the work item
- `assignedto` - The person assigned to the work item
- `Custom.ExecutiveProducer` - Identity field for executive producer
- `Custom.ContentOwner` - Identity field for content owner
- `Custom.AdditionalStakeholders` - Optional identity field for additional stakeholders
- `Custom.FilmingLocation` - Location where content will be produced
- `Custom.SharePoint` - Url to SharePoint
- `Custom.Figma` - Url to Figma
- `Custom.FrameIO` - Url to FrameIO (Asset management link)
- `Custom.Runofshow` - Url to Run of Show spreadsheet
- `Custom.Graphics` - Boolean flag for Azure Logic App Flow, if 'true', creates a 'Graphics' work item as a child work item for the entire series
- `Custom.Upwork` - Boolean flag for Azure Logic App Flow, if 'true', creates an 'Upwork' work item as a child work item for the entire series
- `Custom.Longformseries` - Boolean flag for Azure Logic App Flow, if 'true', creates a 'Episode' work item as a child work item with the 'Studios\Full course video' area path

### Moments (Top-level)
*API work item type name: `Moments` (plural). Fields mirror Shows/Series/Events (state, assignedto, ExecutiveProducer, ContentOwner, AdditionalStakeholders, FilmingLocation, SharePoint, Figma, FrameIO, Runofshow, Graphics, Upwork, Longformseries).*

### Events (Top-level)
- `state` - Current state of the work item
- `assignedto` - The person assigned to the work item
- `Custom.ExecutiveProducer` - Identity field for executive producer
- `Custom.ContentOwner` - Identity field for content owner
- `Custom.AdditionalStakeholders` - Optional identity field for additional stakeholders
- `Custom.FilmingLocation` - Location where content will be produced
- `Custom.Eventstarttime` - Event start date and time
- `Custom.Eventendtime` - Event end date and time
- `Custom.SharePoint` - Url to SharePoint
- `Custom.Figma` - Url to Figma
- `Custom.FrameIO` - Url to FrameIO (Asset management link)
- `Custom.Runofshow` - Url to Run of Show spreadsheet
- `Custom.Graphics` - Boolean flag for Azure Logic App Flow, if 'true', creates a 'Graphics' work item as a child work item for the entire event
- `Custom.Upwork` - Boolean flag for Azure Logic App Flow, if 'true', creates an 'Upwork' work item as a child work item for the entire event
- `Custom.Longformseries` - Boolean flag for Azure Logic App Flow, if 'true', creates a 'Episode' work item as a child work item with the 'Studios\Full course video' area path

### Episode (Mid-level)
- `state` - Current state of the work item
- `assignedto` - The person assigned to the work item
- `Custom.ExecutiveProducer` - Identity field for the executive producer
- `Custom.Host1` - Primary presenter (Internal)
- `Custom.Host2` - Secondary presenter (Internal)
- `Custom.AdditionalPresenters` - Additional presenters (Internal and External)
- `Custom.Episodepublishdate` - Publication scheduling
- `Custom.FilmingLocation` - Location where content will be produced
- `Custom.Recordingstartdateandtime` - Episode recording start time (local time zone)
- `Custom.Recordingenddateandtime` - Episode recording end time (local time zone)
- `Custom.YouTubeshorts` - Indicates if a YouTube shorts video file is required
- `Custom.Thumbnails` - Indicates if a custom thumbnail is needed
- `Custom.Rawfile` - Link to raw video file
- `Custom.Finalfile` - Link to final video file
- `Custom.Learnvideoid` - Video ID from the Learn Video Service
- `Custom.Learnvideoembedurl` - Learn video embed URL
- `Custom.YouTubeChannel` - YouTube channel where the video will be published
- `Custom.YouTubeplaylist` - URL to the YouTube playlist
- `Custom.Videotitleext` - External video title
- `Custom.Videodescriptionexternal` - External video description
- `Custom.Chaptermarkersexternal` - External chapter markers
- `Custom.Resourcelinksexternal` - External resource links
- `Custom.Speakersociallinksexternal` - External speaker social links

### Scheduling/Editing/Uploading/Publishing/Thumbnails/Graphics/Upwork/Full course video/General (Low-level)
- `state` - Current state of the work item
- `assignedto` - The person assigned to the work item
- `Custom.ExecutiveProducer` - Identity field for the executive producer
- `Custom.Episodepublishdate` - Delivery deadline alignment
- `Custom.Recordingstartdateandtime` - Episode recording start time (local time zone)
- `Custom.Recordingenddateandtime` - Episode recording end time (local time zone)
- `Custom.YouTubeshorts` - Indicates if a YouTube shorts video file is required
- `Custom.YouTubeChannel` - YouTube channel where the video will be published
- `Custom.Total#ofvideos` - Integer field on Editing work items indicating the total number of video deliverables produced by that edit job (default: 1 if null/0 for historical items)
- `Custom.Total#ofgraphics` - Integer field on Graphics work items indicating the total number of graphics deliverables produced by that graphics job (default: 1 if null/0 for historical items)

### Action/Issue/Documentation/Task (Ops work items)
- `state` - Current state of the work item
- `assignedto` - The person assigned to the work item

### Custom Field Data Types
- `Identity Fields` - ExecutiveProducer, ContentOwner, AdditionalStakeholders, Host1, Host2
- `DateTime Fields` - Episodepublishdate, Recordingstartdateandtime, Recordingenddateandtime
- `Boolean Fields` - Graphics, Thumbnails, Upwork, longformseries, Youtubeshorts
- `String Fields` - FilmingLocation, SharePoint, Figma, FrameIO, Runofshow, BoardColumn
- `Integer Fields` - StackRank, Priority, Total#ofvideos, Total#ofgraphics

### Field Validation Notes
- `Person fields` - require valid Azure AD identities
- `DateTime fields` - should use ISO format (YYYY-MM-DDTHH:mm:ssZ)
- `Boolean fields` - accept true/false values
- `URL fields` - (SharePoint, Figma, FrameIO) should be valid HTTP/HTTPS URLs

## Run of show (RoS) mapping
**When creating episode work items from a run of show spreadsheet (RoS), the user should prompt something to the extent of: 'create episode work items based on this run of show, under this parent work item: [work item name or id]**
**ONLY use the 'Video Details' sheet in the run of show (RoS) for ADO use**
**ado field mapping - excel spreadsheet column headers**
**Episode information starts on row 4, column A**

#### Fields required for initial creation (bulk):
- `System.Title` - 'Video/Session Title' | value in cell
- Parent link (Series/Shows/Events/Moments work item ID)

#### Fields best set during update (after creation):
- `state` - 'New' (default)
- `assignedto` - the person prompting (must be valid Azure AD identity)
- `Custom.ExecutiveProducer` - the person prompting (must be valid Azure AD identity)
- `Custom.Videotitleext` - 'Video/Session Title' | value in cell
- `Custom.Videodescriptionexternal` - 'Video/Session Description' | value in cell
- `Custom.Speakersociallinksexternal` - 'Social Handle(s)' | value in cell
- `Custom.Resourcelinksexternal` - 'CTA Links' | value in cell
- `Custom.Chaptermarkersexternal` - 'Chapter Markers' | value in cell
- `Custom.Rawfile` - 'Link to RAW files' | value in cell
- `Custom.Finalfile` - 'Link to Final Files' | value in cell
- `Custom.Host1` - 'Speaker(s)' | 1st speaker (identity field, use corresponding email from 'Speaker(s) Email'). See **Speaker/Email Parsing Rules** below.
- `Custom.Host2` - 'Speaker(s)' | 2nd speaker (identity field, use corresponding email from 'Speaker(s) Email'). See **Speaker/Email Parsing Rules** below.
- `Custom.AdditionalPresenters` - 'Speaker(s)' | 3rd+ speakers as plain text, semicolon-delimited. See **Speaker/Email Parsing Rules** below.
- `System.AreaPath` - inherited from parent work item (automatic)
- `System.IterationPath` - inherited from parent work item (automatic)

#### Speaker/Email Parsing Rules:
The 'Speaker(s)' and 'Speaker(s) Email' columns may contain multiple values. The following rules ensure deterministic parsing:

1. **Delimiter**: Split values by semicolon (`;`). Trim leading/trailing whitespace from each resulting value.
2. **Positional matching**: The Nth name in 'Speaker(s)' corresponds to the Nth email in 'Speaker(s) Email'. Both columns must have the same number of values; if counts differ, match positionally up to the shorter list and treat unmatched names as having no email.
3. **Field assignment by position**:
   - **Position 1** → `Custom.Host1` (identity field, use email for ADO resolution)
   - **Position 2** → `Custom.Host2` (identity field, use email for ADO resolution)
   - **Position 3+** → Append to `Custom.AdditionalPresenters` as plain text, semicolon-delimited (format: `DisplayName <email>` per entry, e.g. `Greg Mattox <gregmatt@microsoft.com>;Jeff Petty <jepett@microsoft.com>`)
4. **Single speaker**: If only one name/email is present, populate `Custom.Host1` only. Leave `Custom.Host2` and `Custom.AdditionalPresenters` blank.
5. **Identity fallback**: If an identity field (`Host1` or `Host2`) fails ADO identity resolution (e.g., external email), move that speaker to `Custom.AdditionalPresenters` using the same `DisplayName <email>` format and leave the identity field blank.

**Example**:
- Speaker(s): `Aria Hanson;Diego Baca;Greg Mattox;Jeff Petty`
- Speaker(s) Email: `arcarley@microsoft.com;diebaca@microsoft.com;gregmatt@microsoft.com;jepett@microsoft.com`
- Result:
  - `Custom.Host1` → `arcarley@microsoft.com` (ADO resolves to Aria Hanson)
  - `Custom.Host2` → `diebaca@microsoft.com` (ADO resolves to Diego Baca)
  - `Custom.AdditionalPresenters` → `Greg Mattox <gregmatt@microsoft.com>;Jeff Petty <jepett@microsoft.com>`

#### Notes:
- Identity fields (`assignedto`, `Custom.ExecutiveProducer`, `Custom.Host1`, `Custom.Host2`) require valid Azure AD identities. If not found, use `Custom.AdditionalPresenters`.
- Spreadsheet columns should match ADO field names as closely as possible. Unmapped columns will be ignored.
- All metadata fields should be set during the update phase for complete and accurate episode records.

#### Identity Field Assignment Process:
When populating identity fields like "Host 1" (Primary presenter):

##### Primary Approach: ADO Identity Fields
1. **RoS Preparation**: Include email addresses directly in the "Speaker email" column (e.g., `Eleanor Boyd <eleanorboyd@microsoft.com>`)
2. **Email Extraction**: Extract the email address from angle brackets in the Speaker email field during processing
3. **Automated Processing**: During ADO population, use the extracted email address from the RoS Speaker email field
4. **ADO Identity Resolution**: Use `mcp_ado_wit_update_work_item` with the email address as the value:

   ```json
   {"op": "add", "path": "/fields/Custom.Host1", "value": "eleanorboyd@microsoft.com"}
   ```
5. **Automatic Display Name Resolution**: ADO automatically resolves the email to the full user identity profile including:
   - Display name (e.g., "Eleanor Boyd")
   - User ID and descriptor
   - Profile picture and links
6. **Verification**: The system returns the complete identity object with display name and profile information

##### Fallback Approach: Non-ADO Email Addresses

When ADO identity fields fail with error "unknown identity" (e.g., external speakers, non-Microsoft emails):

1. **Error Detection**: ADO returns error like `The identity value 't******n@g*****.**m' for field 'Host 1' is an unknown identity.`
2. **Fallback Process**:

   - Skip the identity field (`Custom.Host1`, `Custom.Host2`, etc.)
   - Use the "Additional presenters" field instead: `Custom.Additionalpresenters`
3. **Implementation**:

   ```json
   {"op": "add", "path": "/fields/Custom.Additionalpresenters", "value": "timspann@github.com"}
   ```
4. **Field Characteristics**:

   - `Custom.Additionalpresenters` accepts any text/email without identity validation
   - Stores email addresses for external speakers, contractors, or non-ADO users
   - Allows manual lookup and contact information retention

### Processing Workflow

1. **First**: Always try identity fields (`Custom.Host1`, `Custom.Host2`) for Microsoft/internal emails
2. **Fallback**: If identity field fails, populate `Custom.Additionalpresenters` with the email address
3. **Documentation**: Log which emails were moved to fallback field for manual review if needed

**Example Scenarios**:

- **Microsoft Employee**: `eleanorboyd@microsoft.com` → `Custom.Host1` (works)
- **External Speaker**: `timspann@github.com` → `Custom.Additionalpresenters` (fallback)
- **Contractor**: `contractor@external.com` → `Custom.Additionalpresenters` (fallback)

**Example Implementation**:

- RoS Speaker email: `Eleanor Boyd <eleanorboyd@microsoft.com>`
- ADO processing: Extract "eleanorboyd@microsoft.com" from RoS and populate Host 1 field
- ADO Host 1 field result: Full identity profile with "Eleanor Boyd" display name automatically resolved

### Best Practice: Bulk Episode Creation from RoS
**Recommended workflow to reduce API limitations and ensure consistency**
1. Retrieve the parent work item to get area path and iteration path values.
2. Bulk create episode work items from the RoS spreadsheet with only these fields (ado work item title, internal notes/description, parent link), AND the parent work items area path / iteration path.
3. Immediately update each created episode work item to set:
   - All additional metadata fields (speakers, social handles, CTA links, chapter markers, file URLs, etc.)
   - Assignment and executive producer
4. This ensures all episode work items are fully populated, correctly tracked, and maintain consistency with their parent work item's organizational structure.

### Run of show (RoS) error handling
1. If a identity field value cannot be found for a host, revert to `Custom.AdditionalPresenters` field
2. If a cell is missing any value, skip mapping, leave ADO field blank

## Video URL Mapping to Episodes
Establishes a consistent, safe workflow to map YouTube video URLs to `Episode` work items using standardized fields.

### Scope
- Parent types: `Shows`, `Series`, `Events`, `Moments`, `Support requests`
- Child type: `Episode`
- Default behavior: Update only Episodes missing a video URL ("missing-only").
- Overwrite mode: Allowed only with explicit user approval.

### Fields Used
- `Custom.Videotitleext` – External video title used for matching (may contain HTML).
- `Custom.YouTubevideostandard` – Target field to store the YouTube video URL.

### Preconditions
- Always load and validate against this context file before changes.
- Ask for confirmation before applying updates (preview first).
- Confidence-only: Apply mappings only when titles match with high confidence.

### Matching Rules
- Normalize titles from `Custom.Videotitleext`:
  - Strip HTML tags
  - Trim whitespace
  - Case-insensitive comparison
- Match against a user-provided list of video titles and URLs.
- Skip ambiguous or low-confidence matches; request clarification.

### Workflow Steps (Agent)
1. Retrieve the parent work item and enumerate child Episodes.
2. Batch fetch child fields: `System.Id`, `System.Title`, `Custom.Videotitleext`, `Custom.YouTubevideostandard`.
3. Filter according to mode:
   - Missing-only: include Episodes where `Custom.YouTubevideostandard` is empty.
   - Overwrite: include matched Episodes regardless of current value (requires approval).
4. Build a preview map of confident matches from the provided title→URL list.
5. Present the preview for confirmation.
6. Apply updates to `Custom.YouTubevideostandard` for confirmed items.
7. Verify by refetching updated Episodes and reporting results.

### Reporting Format (User Preference)
- Use the work item name as the hyperlink text and include the work item ID in parentheses.
- Example:
  - [Ep 16: From UX to AX: Why Agent Experience is the Next Frontier in Business AI (182266)](https://dev.azure.com/devrel/Studios/_workitems/edit/182266): set `Custom.YouTubevideostandard` → https://www.youtube.com/watch?v=VC6nM0t-bUw

### Safety & Confirmation
- Validate all operations against this context file.
- Preview before apply; require explicit confirmation for overwrite mode.
- Only perform confident mappings; hold uncertain items until clarified.

## Important Rules for Agent use

### Agent Usage Guidelines
1. DO NOT MAKE STUFF UP, if its not coming from a RoS or being explicity stated in the prompt, do NOT make up data. (IE do not add data to fields that is made up)
2. This ADO project utilizes workflows for both manual work item creation, automated creation via Azure Logic App flows and/or using a custom MCP server with Agent use.
 - It is imperative that users using the MCP server with Agent use do not prompt any command that would interfere with existing Power Automate Flows or Azure Logic App Flows. If such a prompt is used, the Agent should warn the user of such to prevent any unwanted actions from taking place in the ADO project. (Reference section: Power Automate Flows + Azure Logic App interference rules)
3. The Agent should promp the user whenever an issue would occur.
4. **Area Path and Iteration Path Inheritance**: When creating child work items (Episodes under Shows/Series/Events, or any child work items), ALWAYS inherit the area path and iteration path from the parent work item. Do NOT prompt the user for these values - automatically retrieve them from the parent and apply to all child work items to ensure proper tracking and consistency.
5. ALWAYS prompt the user with the work thats about to be performed before commiting to ensure accuracy.
6. Dont return api endpoints for work item urls, always return user friendly hyperlinks
    - Example: Convert `https://dev.azure.com/{org}/{project}/_apis/wit/workItems/{id}` to `https://dev.azure.com/{org}/{project}/_workitems/edit/{id}`.
7. **🔒 PROJECT SCOPE ENFORCEMENT**: ALL WIQL queries and ADO REST API calls MUST be scoped exclusively to the **Studios** project. Every WIQL query MUST include `[System.TeamProject] = 'Studios'` in its WHERE clause. The `devrel` organization contains multiple projects (MVP, Reactor, Student Ambassadors, MfS, learntvbit, etc.) — queries without a TeamProject filter will leak across the entire org. **Modifying work items in other projects is strictly prohibited.**

### Power Automate Flows + Azure Logic App interference rules
1. Do not create 'Scheduling', 'Editing', 'Uploading', 'Publishing, 'Graphics', 'Thumbnails', 'Full course video' or 'Upwork' work items as children to 'Shows', 'Series', 'Events', 'Episode', 'Post production support' or 'Publication support' without explicit command to overide the Azure Logic App automation flows. **Note:** Automation flows now create multiple Editing WIs per Episode when applicable (e.g., 'Editing - Shorts'). The agent should still not create these manually — automation handles it.
2. **Area path boundary**: Do not create or parent work items under `Studios\Ops` as children of video production work items (Shows/Series/Events/Episodes/Moments/Support requests), and vice versa. Each area path hierarchy is independent.
3. Do not create top-level work items as children work items to any other work item types
4. **Epic → Ops only**: Epic work items are exclusive to the Studios Ops team (`Studios\Ops` area path). Do not create Epics under any other area path. Do not parent video production work items under Epics.
5. **No cross-team parenting**: Ops work items (Action, Issue, Documentation, Task under `Studios\Ops`) MUST NOT be parented under, or have as children, any video production work items — and vice versa.

## Quarterly Reporting Metrics

### Reporting Model (effective FY26 Q3 onward)
Quarterly reporting uses a three-tier model to capture project throughput at increasing granularity:

| Tier | Metric | How it's counted |
|---|---|---|
| **Projects Completed** | Count of completed top-level work items (Shows, Series, Events, Moments, Support requests) in the quarter's iteration path | Simple count of completed top-level WIs |
| **Episodes Completed** | Count of completed Episode work items in the quarter's iteration path | Simple count of completed Episode WIs |
| **Videos Delivered** | Total number of video deliverables produced across all completed Episodes | Sum of `Custom.Total#ofvideos` from all **completed Editing children** of completed Episodes. Null/0 values are treated as 1 (backward compatibility). Broken down by: **Standard videos** (Editing WIs whose title does NOT contain "Shorts") and **Shorts videos** (Editing WIs whose title contains "Shorts") |
| **Graphics Delivered** | Total number of graphics deliverables produced across all completed Graphics work items | Sum of `Custom.Total#ofgraphics` from all **completed Graphics WIs** in the quarter's iteration path. Null/0 values are treated as 1 (backward compatibility). Effective FY26 Q4 onward; historical quarters report N/A |

### Historical quarters (before FY26 Q3)
For quarters before FY26 Q3, the "Videos Delivered" metric is reported as **N/A** since the `Custom.Total#ofvideos` field and multiple Editing WI pattern did not exist. The old 1 Episode = 1 video assumption remains for those quarters.

### Future consideration
A potential future enhancement is to add a `Total # of videos` rollup field directly on the Episode work item, aggregated from its Editing children via a Power Automate flow. This would simplify reporting queries (no hierarchy traversal needed) but requires an additional automation flow to keep the rollup in sync. Decision deferred.

A similar rollup for `Total # of graphics` could be added at the parent level (Shows/Series/Events) to aggregate from Graphics children. Decision deferred.

## Quarterly Ops Recon Cadence
**At the start of each fiscal quarter, perform the following recon on the Studios Ops backlog:**
1. **Stale item review** — Identify items unchanged for 30+ days; close, reassign, or update as needed
2. **Epic health check** — Verify all Ops items have a parent Epic; re-parent orphans
3. **Area path audit** — Confirm no Ops items have drifted to non-Ops area paths (and vice versa)
4. **Completed item cleanup** — Move resolved items to Completed state; archive if appropriate
5. **New quarter iteration** — Ensure the new quarter's iteration path exists and is assigned to the Studios Ops team

**Schedule**: Q1 (July), Q2 (October), Q3 (January), Q4 (April) — aligned with Microsoft FY

## Studios ADO project changelog

(4/1/2026) - `v1.3.0`
- Added `Custom.Total#ofgraphics` integer field to Graphics work items to track graphics deliverable count per graphics job
- Added Graphics Delivered metric to quarterly reporting model (effective FY26 Q4 onward; historical quarters report N/A)
- Reporting model is now four-tier: Projects Completed → Episodes Completed → Videos Delivered → Graphics Delivered
- Updated compare_quarters_external.py to collect and report Graphics Delivered metric

(2/23/2026) - `v1.2.0`
- **Decoupled 1:1 Episode-to-video assumption**: Episodes can now have multiple Editing work items as children, each representing a distinct deliverable type (standard, shorts, future types)
- Automation flows updated: `Custom.YouTubeshorts` toggle now creates a separate 'Editing - Shorts' child WI instead of trickling a boolean to a single Editing WI
- Added `Custom.Total#ofvideos` integer field to Editing work items to track video deliverable count per edit job
- New three-tier quarterly reporting model: Projects Completed → Episodes Completed → Videos Delivered (standard + shorts breakdown)
- Videos Delivered metric effective FY26 Q3 onward; historical quarters report N/A
- Uploading and Publishing WIs remain singular per Episode (cover all deliverable types)
- Updated interference rule #1 to acknowledge multiple Editing WI creation by automation
- Added "Multiple Editing Siblings Pattern" documentation to hierarchy guidelines
- Updated compare_quarters_external.py to collect and report Videos Delivered metric with standard/shorts breakdown

(2/11/2026) - `v1.1.0`
- **Studios Ops team migration complete**: Created dedicated Studios Ops team with its own backlog, area paths, iterations, queries, and dashboard
- Enabled Epic work item type as top-level organizer for Ops backlog (7 Epics: ADO Platform, Automation, Queries/Analytics, Documentation, AI Innovation, Studio Operations, Communications)
- Migrated custom 'Issues' type to standard 'Issue' type (6 items) and deleted legacy 'Issues' type from process template
- Established area-path-based ownership model: `Studios\Ops` = Ops team, all other paths = Studios Team
- Created 6 shared queries under `Shared Queries/Ops/` and renamed 3 existing JunkDrawer queries
- Created "Studios Ops Overview" dashboard (widgets require manual addition via ADO web UI)
- Updated interference rules from type-based to area-path-based segregation
- Added quarterly recon cadence for Ops backlog hygiene
- Cross-team parenting prohibition: Ops and video production hierarchies are independent

(2/4/2026) - `v1.0.4`
- Removed 'Final checks' work item state from Episode work items. Episode work items will move from 'Publication' to 'Completed' once published by the publisher.

(1/28/2026) - `v1.0.3`
- Added iteration path automation logic flows: Episode work items now automatically have their iteration path calculated and assigned based on the Episode Publish Date field. When parent work items (Shows/Series/Events/Moments/Support requests) are marked as 'Completed', their iteration path is automatically updated to match the latest Episode publish date.

(12/3/2025) - `v1.0.2`
- Automation flows will now create two 'General' work items as children to an Event upon creation. These two General work items 'Pre Event' and 'Post Event' will serve as a folder to hold Pre Event and/or Post Event work items (General and Scheduling) to help reduce overall clutter when viewing the Event in a full hierarchy view.

(11/21/2025) - `v1.0.1`
- Added top level work item type: 'Support requests' to use for Production support, Post production support and publication support projects in lieu of 'Series' work items to be more intuitive.

(00/00/0000) - `v1.0.0 and prior`
- _Untracked_

---

*Last Updated: February 23, 2026*
