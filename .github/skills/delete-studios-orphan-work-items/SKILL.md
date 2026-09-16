---
name: delete-studios-orphan-work-items
description: >
  Use when the user wants to find and remove orphaned Episode or production-task
  work items from the DevRel Studios Azure DevOps project, including requests
  like "delete orphan Studios work items", "clean up parentless Episodes", or
  "remove orphan production tasks". Previews parentless trees, reports invalid
  or suspicious parent relationships, and requires explicit confirmation before
  recoverable deletion to the Azure DevOps Recycle Bin.
argument-hint: "Optional filters such as work item type, area path, iteration, assignee, state scope, or result limit"
---

# Delete Studios Orphan Work Items

Find parentless Studios Episodes and production-task work items, preview the
exact deletion trees, and move confirmed trees to the Azure DevOps Recycle Bin.
Invalid or suspicious parent relationships are review-only.

## Routing Guardrails

1. Use this skill only for orphan cleanup in the `devrel` organization and
   `Studios` project.
2. Treat MVP backlog hygiene as out of scope and route it to
   `review-mvp-backlog-health`.
3. Treat requests to find a replacement parent or repair a hierarchy as out of
   scope. This skill never reparents or unlinks work items.
4. If the request does not clearly identify Studios, ask exactly one
   clarifying question: `Should I inspect the devrel / Studios project?`

## Supported Types

1. `Episode`
2. `Scheduling`
3. `Editing`
4. `Uploading`
5. `Publishing`
6. `Thumbnails`
7. `Graphics`
8. `Shorts`
9. `Full course video`
10. `Upwork`
11. `Postmortem`

Do not expand this set from similar titles or tags. An unsupported descendant
blocks deletion of its entire tree.

## Defaults

1. Target organization: `devrel`.
2. Target project: `Studios`.
3. Include active and non-terminal items only.
4. The user may explicitly request all states.
5. Query all supported types unless the user supplies a narrower type filter.
6. Accept optional exact area path, iteration, and assignee filters.
7. Default preview limit: 50 total work items, including descendants.
8. Never execute a batch larger than 50 items. Ask the user to narrow the scope.
9. Scan candidate IDs in pages of 200, with a 5,000-candidate safety cap.
10. Never describe a capped or interrupted scan as complete. Ask the user to
    narrow the scope before continuing.
11. No minimum-age filter is applied.
12. Deletion is recoverable soft deletion only. Never permanently destroy a
    work item and never use a `destroy` option or REST parameter.

## Prerequisites

### Azure DevOps MCP reads

Use the plugin-packaged ADO MCP for `devrel`:

| Tool | Purpose |
|---|---|
| `ado-wit_query` | Query candidate IDs with WIQL |
| `ado-wit_work_item` | Read fields, type metadata, parents, children, and revisions |

### Azure CLI deletion

The deterministic deletion helper requires:

1. Azure CLI available as `az`.
2. The Azure DevOps CLI extension.
3. An authenticated identity with permission to delete work items in Studios.

If Azure CLI is unavailable, complete discovery and preview, then stop. Do not
replace the helper with improvised REST, browser, or shell deletion.

## State Scope

1. Read work item type metadata with `ado-wit_work_item` action `get_type` when
   terminal states are not already known.
2. By default exclude states in the completed or removed categories.
3. Studios fallback terminal states are `Completed` and `Cancelled`.
4. When the user explicitly requests all states, include terminal items but
   label their state clearly in the preview.

## Discovery

### Step 1: Query candidates

Use `ado-wit_query` with action `wiql` and `top: 200`. Select only the fields
needed for the preview:

```wiql
SELECT
  [System.Id],
  [System.WorkItemType],
  [System.Title],
  [System.State],
  [System.AreaPath],
  [System.IterationPath],
  [System.AssignedTo],
  [System.CreatedDate],
  [System.ChangedDate]
FROM WorkItems
WHERE [System.TeamProject] = 'Studios'
  AND [System.Id] > <LAST_SEEN_ID>
  AND [System.WorkItemType] IN
    ('Episode', 'Scheduling', 'Editing', 'Uploading',
     'Publishing', 'Thumbnails', 'Graphics', 'Shorts',
     'Full course video', 'Upwork', 'Postmortem')
  AND [System.State] <> 'Completed'
  AND [System.State] <> 'Cancelled'
ORDER BY [System.Id] ASC
```

Start with `<LAST_SEEN_ID>` equal to `0`. After each full page, set it to the
highest returned ID and repeat until a page contains fewer than 200 IDs. Add
only filters requested by the user.

When the user explicitly requests all states, omit the two state predicates.
Do not fetch relations until the complete filtered ID scan finishes. Stop and
ask the user to narrow the scope if the scan reaches 5,000 candidates, returns
an unexpected page, or cannot advance the last-seen ID. State the scanned
candidate count in every preview.

### Step 2: Read relations

For each narrowed candidate, use `ado-wit_work_item` action `get` with
`expand: "Relations"`. Record:

1. ID and revision.
2. Type, title, and state.
3. Area and iteration.
4. Assignee.
5. Created and changed dates.
6. `System.Parent`, when present.
7. `System.LinkTypes.Hierarchy-Reverse` parent links.
8. `System.LinkTypes.Hierarchy-Forward` child links.

## Classification

### Parentless

Classify an item as parentless only when both are absent:

1. `System.Parent`
2. A `System.LinkTypes.Hierarchy-Reverse` relation

Parentless items are the only roots eligible for deletion.

### Invalid parent

Classify an item as invalid-parent when a parent field or relation exists but
the target cannot be read, is inaccessible, or is deleted. Report it for manual
review. Do not delete, unlink, or modify it.

### Wrong hierarchy

Fetch readable parents and conservatively compare their types with this known
Studios matrix:

| Child | Known parent types |
|---|---|
| `Episode` | `Events`, `Shows`, `Series`, `Moments`, `General`, `Support requests`, `Post production support`, `Publishing request` |
| `Scheduling` | `Episode`, `General` |
| `Editing` | `Episode` |
| `Uploading` | `Episode` |
| `Publishing` | `Episode` |
| `Thumbnails` | `Episode` |
| `Graphics` | `Episode`, `Events`, `Shows`, `Series`, `Moments`, `General`, `Support requests`, `Post production support`, `Publishing request` |
| `Shorts` | `Episode` |
| `Full course video` | None observed; parented items remain review-only |
| `Upwork` | `Episode` |
| `Postmortem` | `Events`, `Shows`, `Series`, `Support requests` |

When a readable parent is outside the known matrix, label the item
`wrong-hierarchy review`. This is a review signal, not proof that the
relationship is invalid. Never delete it from this category.

## Tree Construction

For each parentless root:

1. Recursively follow `System.LinkTypes.Hierarchy-Forward` child relations.
2. Read every descendant with relations.
3. Include the tree only when every node:
   - Belongs to the `Studios` project.
   - Has a supported work item type.
   - Has a valid parent-child type combination from the known Studios matrix.
   - Is readable.
   - Appears only once in the tree.
4. Block the tree when:
   - A descendant type is unsupported.
   - Any descendant is classified as invalid-parent or wrong-hierarchy review.
   - A node is inaccessible.
   - A relation cycle exists.
   - Trees overlap.
   - The combined confirmed batch would exceed 50 items.
5. Record each node's revision, expected parent ID, and exact child IDs for the
   deletion manifest.

## Preview

Group results in this order:

1. `Deletable parentless trees`
2. `Invalid-parent review`
3. `Wrong-hierarchy review`
4. `Blocked trees`

For each deletable tree, show:

| Root | Type | Title | State | Area | Iteration | Assignee | Changed | Descendants | Delete order |
|---|---|---|---|---|---|---|---|---:|---|

Use leaf-first delete order. List every work item ID; never summarize hidden
descendants as `and others`.

End the preview with:

`This will move N work items to the Azure DevOps Recycle Bin. It will not permanently destroy them. Confirm the exact listed IDs to continue.`

Do not treat a general response such as `clean them up` as confirmation when
the user has not seen the current exact list.

## Manifest Contract

After confirmation, write a temporary JSON manifest:

```json
{
  "version": 1,
  "organization": "https://dev.azure.com/devrel",
  "project": "Studios",
  "trees": [
    {
      "rootId": 123,
      "nodes": [
        {
          "id": 123,
          "type": "Episode",
          "revision": 4,
          "parentId": null,
          "children": [124]
        },
        {
          "id": 124,
          "type": "Editing",
          "revision": 2,
          "parentId": 123,
          "children": []
        }
      ]
    }
  ]
}
```

Use the relation snapshot from the confirmed preview. Do not omit revisions or
child lists.

## Delete Procedure

Invoke the packaged helper:

```text
node <PLUGIN_ROOT>/skills/delete-studios-orphan-work-items/scripts/delete-orphan-trees.mjs --manifest <MANIFEST_PATH> --execute
```

`<PLUGIN_ROOT>` is `plugins/devrel-studios` in the source repository or
`.github/plugins/devrel-studios` after workspace deployment.

The helper must:

1. Reject any organization, project, type, or count outside this skill's fixed
   safety policy.
2. Re-read every tree immediately before deleting it.
3. Verify every revision, parent, and child relation against the manifest.
4. Re-read each node again at its point of deletion and verify its parent,
   remaining children, and expected revision after already deleted direct
   children are accounted for.
5. Skip the entire tree when preflight finds drift. Stop the remaining tree if
   a point-of-delete guard finds drift after earlier descendants were deleted.
6. Delete leaf-first with `az boards work-item delete --yes`.
7. Stop the current tree after the first delete failure.
8. Never pass or accept permanent-destruction options.
9. Return structured JSON for reporting.

Delete the temporary manifest after the helper finishes.

## Output

Report one row per tree:

| Root | Planned | Deleted | Skipped | Failed | Result |
|---|---:|---:|---:|---:|---|

Then list invalid-parent, wrong-hierarchy, and blocked findings separately with
edit links and reasons.

Always state:

1. Deleted work items were moved to the Azure DevOps Recycle Bin.
2. Invalid and suspicious parent relationships were not modified.
3. Any tree skipped for drift requires a fresh preview and confirmation.

## Safety Rules

1. Never delete before showing and confirming the exact IDs.
2. Never delete more than 50 total items in one confirmed run.
3. Never permanently destroy work items.
4. Never delete invalid-parent or wrong-hierarchy findings.
5. Never reparent, unlink, tag, comment on, cancel, or edit fields.
6. Never delete a partial or unvalidated tree because a descendant could not be
   read.
7. Never continue deleting a tree after an operational failure.
8. Never reuse a stale manifest after any drift result.
9. Prefer a smaller trustworthy queue over speculative cleanup.
