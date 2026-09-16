---
name: create-studio-support
description: >
  Use when the user wants to book studio time, schedule a recording, or create a studio
  support request, including requests like "create a support request", "book studio time",
  "schedule a recording", "studio support work item", or "create a studio support".
  Creates a Studio Support request work item in the Studios ADO project with a child
  Episode work item, collecting speaker name, studio stage, and start time, then applying
  the correct fields and parent-child relationship.
---

# Create Studio Support Request

Create a Support request and child Episode work item in the Studios ADO project for a
studio recording session.

## When to Use

- User asks to create a studio support request or work item
- User wants to book studio time or schedule a recording session
- User says "create a support request", "book studio time", "schedule a recording"

## Prerequisites

- `@azure-devops/mcp` MCP server configured for the `devrel` org (see `.mcp.json`)
- User has access to the **Studios** project in the `devrel` ADO org

## Required MCP Tools

| Tool | Purpose |
|------|---------|
| `ado-wit_create_work_item` | Create the Support request |
| `ado-wit_add_child_work_items` | Create the child Episode |
| `ado-core_get_identity_ids` | Look up speaker identity (optional) |

## Workflow

### Step 1 — Gather Details

Collect the following from the user. Ask for anything missing:

| Detail | Required | Example |
|--------|----------|---------|
| **Speaker name** | Yes | Steph Rogers |
| **Studio stage** | Yes | A, B, or C |
| **Start date and time** | Yes | Friday June 12, 2026 at 1:00 PM PT |
| **Title override** | No | Defaults to `{Speaker} - Studio {Stage} Recording` |

### Step 2 — Create Support Request

Use `ado-wit_create_work_item` with:

- **Project:** `Studios`
- **Work item type:** `Support requests`
- **Fields:**

| Field | Value |
|-------|-------|
| `System.Title` | `{Speaker} - Studio {Stage} Recording` (or user-provided title) |
| `Custom.FilmingLocation` | `Studio` |
| `Microsoft.VSTS.Scheduling.StartDate` | ISO 8601 datetime with timezone |
| `System.Description` | HTML block with speaker, location (with stage), and start time |

**Description template (HTML):**
```html
<div><strong>Speaker:</strong> {Speaker}</div>
<div><strong>Location:</strong> Studio {Stage}</div>
<div><strong>Start Time:</strong> {Day}, {Date} at {Time} PT</div>
```

### Step 3 — Create Child Episode

Use `ado-wit_add_child_work_items` with:

- **Parent ID:** The Support request ID from Step 2
- **Project:** `Studios`
- **Work item type:** `Episode`
- **Fields via `items` array:**

| Field | Value |
|-------|-------|
| `title` | Same as Support request title |
| `description` | Same HTML description as Support request |

After creation, update the Episode with additional fields using `ado-wit_update_work_item`:

| Field | Value |
|-------|-------|
| `Custom.Host1` | Speaker name |
| `Custom.Stage` | A, B, or C |
| `Custom.FilmingLocation` | `Studio` |
| `Custom.Recordingstartdateandtime` | Same ISO 8601 datetime |

### Step 4 — Confirm

Show the user both work items with clickable links:

```
✅ Created:
- Support request #<id>: <title>
  https://dev.azure.com/devrel/Studios/_workitems/edit/<id>
- Episode #<id>: <title> (child of #<parent_id>)
  https://dev.azure.com/devrel/Studios/_workitems/edit/<id>
```

## Field Reference

| Detail | Support request field | Episode field |
|--------|----------------------|---------------|
| Title | `System.Title` | `System.Title` |
| Speaker | Description only (no dedicated field) | `Custom.Host1` |
| Stage | N/A | `Custom.Stage` |
| Location | `Custom.FilmingLocation` → `Studio` | `Custom.FilmingLocation` → `Studio` |
| Start time | `Microsoft.VSTS.Scheduling.StartDate` | `Custom.Recordingstartdateandtime` |

## Important Notes

- `Custom.FilmingLocation` only accepts `Studio` as a value — the specific stage (A/B/C) goes in `Custom.Stage` on Episodes only.
- There is no dedicated Speaker field on Support requests — include the speaker in the title and description.
- ADO work items cannot be permanently deleted via the API — use `Cancelled` state to remove mistakes.
- Speaker identity can be resolved with `ado-core_get_identity_ids` if identity-type fields are needed.
