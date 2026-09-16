---
name: youtube-description
description: >
  Use when the user wants to update YouTube video titles and descriptions from Azure
  DevOps Episode work item fields, including requests like "update YouTube description",
  "push description to YouTube", "sync ADO to YouTube", or when they want to set a
  video's title or description from ADO Episode data. Reads metadata from the work item,
  builds a description from the standard template, shows a dry-run preview, and updates
  YouTube via the API after user confirmation. Supports standard videos and Shorts with
  different
  templates. Supports multiple channels (msdev, azd, vs, etc.).
---

# YouTube Description Updater Skill

Update YouTube video titles and descriptions from Azure DevOps Episode work item fields using the YouTube Data API v3.

## When to Use

- User asks to "update YouTube description", "push description to YouTube", or "sync ADO to YouTube"
- User wants to set or update a video's title/description from ADO Episode data
- User says "write the description" or "update the show description on YouTube"

## Prerequisites

1. **YouTube API tokens** must exist at `~/.copilot/youtube-tokens/<channel>.json`
2. **Azure DevOps MCP** must be available for reading work items
3. **Node.js** must be installed

## Quick Start

When the user asks to update a YouTube description, collect:

1. **ADO work item ID** — e.g., "Episode 229938" or just "229938"
2. **Channel** — which YouTube channel (defaults to `msdev` if not specified)

Available channels can be found by listing `~/.copilot/youtube-tokens/*.json` files.

Then run the full automation flow below. Always show a dry-run preview and get confirmation before saving.

## API Helper Script

The helper script is located at:
```
~/.copilot/skills/youtube-description/youtube-api.js
```

### Commands

**Get current video metadata:**
```powershell
node ~/.copilot/skills/youtube-description/youtube-api.js <channel> get <videoId>
```

**Update video title and description:**
```powershell
node ~/.copilot/skills/youtube-description/youtube-api.js <channel> update <videoId> "<title>" <descriptionFile>
```
The description must be written to a temp file first, then passed as the `<descriptionFile>` argument.

**List recent channel videos:**
```powershell
node ~/.copilot/skills/youtube-description/youtube-api.js <channel> list [maxResults]
```

## ADO Field Reference

### Content Fields (for building the description)

| User-Facing Name | ADO Field | Maps To |
|---|---|---|
| External show title | `Custom.Videotitleext` | YouTube **Title** field |
| External show description | `Custom.Videodescriptionexternal` | Main description body |
| Chapter markers | `Custom.Chaptermarkersexternal` | Timestamped chapter list |
| Resource links | `Custom.Resourcelinksexternal` | Links & resources section |
| Speaker social / hashtags | `Custom.Speakersociallinksexternal` | Hashtags and social links |
| YouTube playlist URL | `Custom.YouTubeplaylist` | Playlist link line |

### Target Video Fields

| User-Facing Name | ADO Field | Purpose |
|---|---|---|
| YouTube video (Standard) | `Custom.YouTubevideostandard` | Standard video to update |
| YouTube video (Shorts) | `Custom.YouTubevideoshorts` | Shorts video to update |

> **Note:** All content fields are HTML-formatted in ADO and must be converted to plain text before use (see Step 2).

## Description Templates

### Standard Video

**Title field:**
```
{External show title}
```

**Description field:**
```
{External show description}

{Chapter markers}

{Resource links}

📺 Full playlist: {YouTube playlist URL}

{Speaker social / hashtags}
```

### Shorts Video

**Title field:**
```
{External show title}
```

**Description field:**
```
▶️ Watch the full episode: {Standard video URL}

{External show description}

📺 Full playlist: {YouTube playlist URL}

{Speaker social / hashtags}
```

**Template rules:**
- Omit any section whose source field is missing or empty — do not leave blank headers or placeholders.
- If the playlist URL is missing/empty, omit the playlist line entirely.
- If updating a Short and the standard video URL is missing, **ask the user** whether to omit the "Watch the full episode" line or provide the URL manually. Never publish a line with an empty URL.
- Shorts descriptions do NOT include chapter markers or resource links.

## Automation Flow

### Step 1: Read the ADO Work Item

Fetch the Episode work item from the **Studios** project (org: `devrel`) using the ADO MCP tool (`ado-wit_get_work_item`).

Read these fields:
- `System.Title`
- `Custom.Videotitleext`
- `Custom.Videodescriptionexternal`
- `Custom.Chaptermarkersexternal`
- `Custom.Resourcelinksexternal`
- `Custom.Speakersociallinksexternal`
- `Custom.YouTubeplaylist`
- `Custom.YouTubevideostandard`
- `Custom.YouTubevideoshorts`

**Validation:** The title (`Custom.Videotitleext`) and at least one video URL field must be populated. If the title is missing, stop and ask the user. If content fields are empty, proceed but note which sections will be omitted.

### Step 2: Convert ADO HTML to Plain Text

ADO rich-text fields contain HTML markup. Convert to plain text:

- Replace `<br>`, `<br/>`, `<br />` with newlines
- Replace `</p>`, `</div>` with newlines
- Replace `<li>` with `• ` and `</li>` with newline
- Strip all remaining HTML tags
- Decode HTML entities: `&nbsp;` → space, `&amp;` → `&`, `&lt;` → `<`, etc.
- Decode numeric HTML entities: `&#127918;` → 🎮
- Collapse multiple consecutive spaces to single space
- Trim each line
- Collapse 3+ consecutive newlines to 2 (preserve paragraph spacing)

### Step 3: Build the Description Text

Construct the final description using the appropriate template (Standard or Shorts).

**Length check:** YouTube descriptions have a 5,000-character limit. YouTube titles have a 100-character limit. Warn the user if either limit is exceeded.

### Step 4: Dry-Run Preview and Confirmation

Before modifying YouTube, show the user the exact title and description for each video:

```
📝 Preview — Standard Video (ID: {videoId}):
─────────────────────────────────
Title: {title}

Description:
{constructed description}
─────────────────────────────────
Character count: {count}/5000
```

Ask: "Does this look correct? Should I update YouTube now?"

**Only proceed after the user confirms.**

### Step 5: Extract Video IDs

Extract the video ID from each URL. Support these formats:

| URL Format | Video ID |
|---|---|
| `https://youtu.be/6Q6zcwCB8x0` | `6Q6zcwCB8x0` |
| `https://www.youtube.com/watch?v=6Q6zcwCB8x0` | `6Q6zcwCB8x0` |
| `https://youtube.com/shorts/6Q6zcwCB8x0` | `6Q6zcwCB8x0` |
| Raw 11-character ID: `6Q6zcwCB8x0` | `6Q6zcwCB8x0` |

### Step 6: Write Description to Temp File

Write the constructed description to a temporary file. Use a path like:
```
~/.copilot/session-state/{session-id}/files/yt-description-{videoId}.txt
```

### Step 7: Update YouTube via API

Run the helper script to update each video:

```powershell
node ~/.copilot/skills/youtube-description/youtube-api.js <channel> update <videoId> "<title>" <descriptionFile>
```

The script will:
1. Load the channel's token (auto-refreshes if expired)
2. Get the current video metadata (to preserve tags, category, etc.)
3. Update only the title and description
4. Return a JSON result with success/failure

### Step 8: Verify the Update

After updating, use the `get` command to verify the changes took effect:

```powershell
node ~/.copilot/skills/youtube-description/youtube-api.js <channel> get <videoId>
```

Confirm the returned title and description match what was submitted.

### Step 9: Repeat for Shorts (if applicable)

If both standard and Shorts URLs exist, repeat Steps 6-8 for the Shorts video using the Shorts template.

### Step 10: Report Results

```
✅ YouTube updated:
  • Standard video ({videoId}): Title and description updated
  • Shorts ({videoId}): Title and description updated

Source: ADO Episode #{workItemId} — "{External show title}"
Channel: {channel}
```

## Batch Workflow

When updating multiple episodes:

1. Accept a list of work item IDs from the user
2. For each Episode: read ADO → build descriptions → collect previews
3. Show a combined dry-run preview for all episodes
4. After user confirms, update each video sequentially
5. Report a summary at the end

## Channel Selection

If the user doesn't specify a channel, default to `msdev`. If the video isn't found on that channel, suggest trying other available channels.

To see available channels:
```powershell
Get-ChildItem ~/.copilot/youtube-tokens/*.json | ForEach-Object { $_.BaseName }
```

## Error Handling

| Error | Action |
|---|---|
| Token not found | Tell user to run: `node ~/.copilot/youtube-tokens/auth.js <channel>` |
| Token refresh failed | Token may be revoked. Re-run the auth flow. |
| Video not found | Check the video ID and channel. Try a different channel. |
| 403 Forbidden | Channel account may not have access. Check test users in Google Cloud Console. |
| Description > 5000 chars | Warn user, ask how to truncate. |
| Title > 100 chars | Warn user, ask how to shorten. |

## Notes

- This skill modifies **live, public-facing YouTube metadata**. Always preview and confirm.
- YouTube descriptions support plain text only — no markdown or HTML.
- Standard and Shorts updates are independent. Partial success is valid.
- The API preserves existing tags, category, and other metadata not being updated.
