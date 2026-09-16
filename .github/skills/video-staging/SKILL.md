---
name: video-staging
description: >
  Use when the user provides a video file and wants the full publishing pipeline,
  including requests like "stage this video", "upload to msdev", "publish this video",
  "prep this for YouTube", "stage for msdev", or "create an episode". Uploads the
  .mp4 to YouTube as unlisted, generates metadata from an .srt or .vtt transcript,
  tracks the work in Azure DevOps, and handles transcript parsing, title and description
  generation, YouTube upload, and ADO work item creation.
  (Support requests → Episode → Graphics). Even if the user only provides a video
  file without a transcript, offer to generate metadata from context and proceed
  with the upload and ADO tracking.
---

# Video Staging Skill

Stage a video for publishing on the Microsoft Developer YouTube channel. This skill
handles the full pipeline: transcript analysis → metadata generation → YouTube upload
(unlisted) → ADO work item tracking.

## When to Use

- User provides a video file and wants it staged on msdev
- User says "stage this video", "upload to msdev", "prep for YouTube"
- User has a video + transcript and wants the full publishing workflow
- User wants to create ADO tracking for a new on-demand video

## Prerequisites

1. **YouTube API tokens** at `~/.copilot/youtube-tokens/msdev.json`
2. **Azure DevOps MCP** for creating work items in the Studios project
3. **Node.js** installed
4. **Python 3.8+** for transcript parsing

## Workflow

### Step 1: Collect Inputs

Ask the user for (use `ask_user` tool, one question at a time):

1. **Video file path** (.mp4) — required
2. **Transcript file path** (.srt or .vtt) — optional but recommended; check if one
   exists in the same directory as the video with a matching filename
3. **Channel** — default to `msdev` unless specified
4. **Any specific branding or context** — e.g., "Build branding", show name, series

If a transcript file exists alongside the video (same name, .srt or .vtt extension),
auto-detect it and confirm with the user.

### Step 2: Parse Transcript & Generate Metadata

If a transcript is provided:

1. Run the VTT/SRT parser:
   ```powershell
   python ~/.copilot/installed-plugins/mvp-copilot-plugins/devrel-studios/scripts/parse-vtt.py "<transcript_file>"
   ```

2. Read the full parsed output and generate:
   - **2–3 creative title options** (under 70 characters each)
   - **One paragraph description** (3–5 sentences, SEO-friendly, with relevant links)
   - Include links to relevant GitHub repos or project pages if mentioned in the transcript

3. Present the metadata to the user for review:
   ```
   ## 🎬 Title Options
   1. [Title 1]
   2. [Title 2]
   3. [Title 3]

   ## 📝 Description
   [Description paragraph]
   ```

4. Ask the user to pick a title (or mark as TBD) and approve/edit the description.

If no transcript is provided, ask the user to describe the video content so you can
craft a title and description manually.

### Step 3: Upload to YouTube

1. Write the approved description to a temp file:
   ```
   ~/.copilot/session-state/{session-id}/files/yt-description-{timestamp}.txt
   ```

2. Upload the video using the YouTube API helper:
   ```powershell
   node ~/.copilot/skills/youtube-description/youtube-api.js <channel> upload "<video_file>" "<title>" "<description_file>" unlisted
   ```

3. Capture the returned video ID and URL from the JSON output.

4. Confirm success to the user:
   ```
   ✅ Uploaded to YouTube (unlisted)
   🎬 https://youtu.be/<videoId>
   ```

### Step 4: Create ADO Work Items

Create a three-level work item hierarchy in the **Studios** project (org: `devrel`):

#### 4a. Support requests (top-level)

Create a **Support requests** work item:
- **Title**: `<Video topic> — On-Demand Video`
- **Description** (HTML): Include a summary of the video, the YouTube URL, and any
  relevant links (GitHub repo, project page, etc.)

#### 4b. Episode (child of Support requests)

Create an **Episode** work item as a child:
- **Title**: The chosen video title
- **Description** (HTML): Include the YouTube URL and the approved video description
- Use `ado-wit_add_child_work_items` with `parentId` set to the Support requests ID

#### 4c. Graphics (child of Episode) — if thumbnail is needed

Ask the user if they need a custom thumbnail. If yes:

- Ask who to assign it to (suggest Chris Armstrong as the default)
- Ask about branding (e.g., "Build branding for on-demand videos")
- Create a **Graphics** work item as a child of the Episode:
  - **Title**: `Custom Thumbnail — <Video topic>`
  - **Description** (HTML): Include the branding instructions, video link, and
    1920×1080px size requirement
  - **Assigned To**: The specified person's Microsoft email

Use `ado-wit_update_work_item` to set the Assigned To field after creation.

### Step 5: Summary

Always present a final summary with all ADO links. Format for easy copy-paste into Teams:

```
📋 <Video Topic> — On-Demand Video Setup Summary

1. Generated video metadata from transcript
   - Title: <chosen title>
   - Description with linked resources

2. Uploaded to YouTube
   - Channel: Microsoft Developer (msdev)
   - Visibility: Unlisted
   - 🎬 <YouTube URL>

3. Created ADO work items in Studios project
   - Support requests #<ID> — <title>
     https://dev.azure.com/devrel/Studios/_workitems/edit/<ID>

   - Episode #<ID> — <title>
     https://dev.azure.com/devrel/Studios/_workitems/edit/<ID>

   - Graphics #<ID> — <title> (assigned: <person>)
     https://dev.azure.com/devrel/Studios/_workitems/edit/<ID>

⏳ Next steps:
   - Finalize the video title (if TBD)
   - <Assignee> to create the custom thumbnail
   - Update visibility from unlisted → public when ready
```

**Always include ADO links in every summary.**

## ADO Field Reference

| Work Item Type | Key Fields |
|---|---|
| Support requests | System.Title, System.Description |
| Episode | System.Title, System.Description, Custom.Videotitleext, Custom.Videodescriptionexternal, Custom.YouTubevideostandard |
| Graphics | System.Title, System.Description, System.AssignedTo |

## Known Team Members (Graphics)

| Name | Email | Role |
|------|-------|------|
| Chris Armstrong | v-chrisar@microsoft.com | Graphics / Thumbnails |

## Channel Tokens

Available channels can be listed with:
```powershell
Get-ChildItem ~/.copilot/youtube-tokens/*.json | ForEach-Object { $_.BaseName }
```

Default channel: **msdev**

## Error Handling

| Error | Action |
|---|---|
| No transcript file | Ask user to describe video content; generate metadata manually |
| Token not found | Tell user to run: `node ~/.copilot/youtube-tokens/auth.js <channel>` |
| Upload fails | Show the error, check token validity, retry once |
| ADO MCP unavailable | Generate all metadata and upload to YouTube; output ADO info for manual entry |
| Video file not found | Ask user to verify the path |

## Edge Cases

- **No transcript**: Still upload the video and create ADO items; craft metadata from user-provided context
- **Multiple videos**: Process one at a time; ask user if they want to batch
- **Title TBD**: Use the best option as placeholder, note it's pending finalization
- **Non-msdev channel**: Support any channel with a valid token in `~/.copilot/youtube-tokens/`
- **Existing ADO items**: If user provides an existing Support Request or Episode ID, create children under it instead of new top-level items
