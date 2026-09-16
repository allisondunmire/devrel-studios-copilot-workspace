---
name: aka-redirect
description: >
  Use when the user wants to create an aka.ms short URL redirect, including
  requests like "create a redirect", "aka.ms link", "short URL", "redirection",
  or when they provide a long URL they want shortened. Files a Redirection work
  item in the Studios ADO project, collects the target URL, short URL path name,
  and requestor alias, and relies on the Logic App automation to populate the
  Short URL field.
---

# aka.ms Redirect Skill

When the user asks to create an aka.ms redirect / short URL, follow this procedure exactly.

## Required Information

Collect these from the user (or infer from context):

| Field | Description | Example |
|---|---|---|
| **Target URL** | The full destination URL to redirect to | `https://forms.office.com/...` |
| **Short URL Path** | The desired aka.ms path (no spaces, lowercase) | `developergreenlight` |
| **Requestor Alias** | Microsoft alias of the person requesting | *(ask the user)* |

- If the user provides a URL and a name, you have enough to proceed.
- Always ask the user for the **Requestor Alias** when it cannot be inferred from context.
- The **Short URL Path** is what comes after `aka.ms/` — confirm with the user if ambiguous.

## Steps

1. **Pre-check ADO MCP server availability** — before proceeding, verify that the Azure DevOps MCP tools are available (e.g., attempt a lightweight read operation). If the ADO MCP server is not available, inform the user that the redirect cannot be created right now and suggest they try again later.

2. **Create a Redirection work item** in the **Studios** ADO project using `ado-wit_create_work_item`:
   - `workItemType`: `redirection`
   - `project`: `Studios`
   - Required fields:
     - `System.Title` → the short URL path name
     - `Custom.TargetURL` → the full destination URL
     - `Custom.ShortURLPath` → the short URL path (same as title)
     - `Custom.RequestorAlias` → the requestor's Microsoft alias

3. **Confirm creation** — tell the user the work item ID and that the Logic App automation will process it and create the aka.ms link.

4. **Do NOT attempt** to create the aka.ms link directly — the Logic App on dsautomation-la1 handles that automatically.

## ADO Work Item Type Details

- **Type reference:** `Studios.redirection`
- **Custom fields:**
  - `Custom.TargetURL` (required) — the destination URL
  - `Custom.ShortURLPath` (required) — the aka.ms path
  - `Custom.RequestorAlias` (required) — who requested it
  - `Custom.ShortURL` (optional) — automation fills this with the final `https://aka.ms/{path}` link
- **States:** New → Active → Closed
- The automation sets the state to Active when processing, and Closed when done (with `Custom.ShortURL` populated).

## Example

User: "Create a redirect for https://example.com/long-page and call it myshortlink"

→ Create Redirection work item:
- Title: `myshortlink`
- Target URL: `https://example.com/long-page`
- Short URL Path: `myshortlink`
- Requestor Alias: *(asked from the user)*

→ Reply: "Created Redirection #12345. The automation will create aka.ms/myshortlink — I'll let you know when it's ready, or you can check the work item."
