---
name: vtt-metadata
description: >
  Use when the user provides a .vtt or .srt transcript and wants YouTube metadata,
  including requests like "process this VTT", "process this SRT", "generate titles from
  transcript", "chapter markers", "video description from transcript", "transcript to
  metadata", or "update the episode work item". Generates creative titles, a video
  description, chapter markers with timestamps, and can write results into Azure DevOps
  Episode work items.
---

# Transcript → Video Metadata

Parse a .vtt or .srt transcript file and generate YouTube-ready metadata: titles, description, and chapter markers. Optionally write results into an Azure DevOps Episode work item.

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| WebVTT | `.vtt` | Web Video Text Tracks — common for browser-based players and YouTube downloads |
| SubRip | `.srt` | SubRip subtitle format — widely used in video editing and media players |

The parser auto-detects the format from the file extension. Both formats use timestamped cue blocks with `-->` arrows.

## Workflow

### Step 1: Parse the transcript file

Read the provided `.vtt` or `.srt` file.

**VTT format:**
```
WEBVTT

00:00:01.000 --> 00:00:04.500
Welcome everyone to today's episode.

00:00:05.000 --> 00:00:09.200
We're going to be talking about GitHub Copilot agents.
```

**SRT format:**
```
1
00:00:01,000 --> 00:00:04,500
Welcome everyone to today's episode.

2
00:00:05,000 --> 00:00:09,200
We're going to be talking about GitHub Copilot agents.
```

Use the parsing script to extract clean text with timestamps:

```
python <PLUGIN_ROOT>/scripts/parse-vtt.py <VTT_FILE>
```

> **Path note:** `<PLUGIN_ROOT>` is `plugins/devrel-studios` when running from the source repo, or `.github/plugins/devrel-studios` after workspace installation.

This outputs a structured text file with merged speaker segments and timestamps, making it easier to analyze.

**Handling long transcripts (60–90+ minutes):**
- Process the transcript in chunks if needed, but always read the FULL transcript before generating output
- For chapter markers, scan the entire timeline — do not skip sections
- The parse script consolidates overlapping captions to reduce token usage

### Step 2: Generate creative titles (2–3 options)

Read the full transcript and craft **2–3 creative title options** for the video.

**Title guidelines:**
- Keep titles under 70 characters (YouTube truncates longer ones)
- Front-load the most compelling keyword or topic
- Use formats that work well on YouTube:
  - "How [topic] Changes Everything About [outcome]"
  - "[Topic]: The Complete Guide to [specific thing]"
  - "[Number] Things You Didn't Know About [topic]"
  - "Building [thing] with [technology] — Live Demo"
- Avoid clickbait — titles should be accurate and specific to the content
- Include the primary technology, product, or guest name if notable
- Consider the show name and episode format (e.g., "Cozy AI Kitchen Ep 47: ...")

### Step 3: Write a description (one paragraph)

Craft a **single paragraph** video description that:
- Opens with a hook — what will the viewer learn or see?
- Mentions the key topics, technologies, or guests covered
- Is 3–5 sentences long
- Includes relevant keywords naturally (for YouTube SEO)
- Ends with a reason to watch (e.g., a demo, an insight, a unique perspective)

Do NOT include links, social handles, or boilerplate — just the content description.

### Step 4: Generate chapter markers

Scan the full transcript for **key moments** and produce YouTube-compatible chapter markers.

**What to mark:**
- Intro / welcome (always starts at `0:00`)
- Topic transitions — when the conversation shifts to a new subject
- Demo starts — when someone switches to showing code, a product, or a tool
- Feature announcements — when a new feature or capability is introduced
- Q&A sections — when they start answering audience questions
- Key insights — memorable quotes, surprising revelations, or "aha" moments
- Wrap-up / outro

**Chapter marker format (YouTube-compatible):**
```
0:00 - Welcome & Intro
2:15 - What is GitHub Copilot Agents?
8:42 - Live Demo: Building a RAG pipeline
15:30 - How vector search works under the hood
22:10 - Audience Q&A
28:45 - Wrap-up & next episode preview
```

**Chapter marker rules:**
- First chapter MUST start at `0:00`
- **Target: ~2 chapters per 5 minutes of video** (e.g., 20 min → ~8, 60 min → ~24)
- Timestamps must be in `M:SS` or `H:MM:SS` format
- **Chapters should generally be at least 1 minute apart**
- Each chapter title should be concise (3–8 words)
- Focus on **high-level topic shifts** — but don't be rigid about it
- **If a section is dense** (e.g., a demo that transitions into a new topic, or multiple features shown back-to-back), add extra markers to capture those moments — viewer navigation matters more than sticking to a formula
- Think like a viewer scrubbing through: what are the moments they'd want to jump to?

### Step 5: Present results for review

Show the user all generated metadata clearly:

```
## 🎬 Title Options
1. [Title option 1]
2. [Title option 2]
3. [Title option 3]

## 📝 Description
[One paragraph description]

## 📌 Chapter Markers
0:00 - Welcome & Intro
2:15 - [Chapter 2]
...
```

Ask the user to:
1. **Pick a title** (or request revisions)
2. **Approve or edit** the description
3. **Approve or edit** the chapter markers

Once the user has approved the metadata, **always ask:**

> "Do you want me to update the corresponding ADO work item?"

If yes, ask for the work item ID (e.g., "What's the Episode work item ID?").

### Step 6: Write to Azure DevOps (when user confirms)

Once the user approves the metadata, update the Episode work item in Azure DevOps.

**The user must provide the work item ID** (e.g., "update work item 182228").

**Before writing, check which fields are already filled:**

1. Fetch the work item and read these three fields:
   - **`Custom.Videotitleext`** — Video title
   - **`Custom.Videodescriptionexternal`** — Video description
   - **`Custom.Chaptermarkersexternal`** — Chapter markers

2. **For EMPTY fields** — fill them automatically with the approved metadata. No confirmation needed.

3. **For fields that ALREADY have content** — DO NOT overwrite. Instead, show the user what's currently there vs. what you generated:

```
⚠️ These fields already have content:

📌 Chapter Markers (existing):
   0:00 - Welcome
   3:15 - Demo
   ...

📌 Chapter Markers (generated):
   0:00 - Intro & Demo Preview
   0:32 - Blender Agent in M365 Copilot
   ...

Overwrite with the new version?
```

Ask the user **per field** whether to overwrite or keep the existing content.

4. Update only the fields the user approved:
```
Update work item <ID> with:
  /fields/Custom.Videotitleext = "<chosen title>"
  /fields/Custom.Videodescriptionexternal = "<description in HTML>"
  /fields/Custom.Chaptermarkersexternal = "<chapter markers in HTML>"
```

Use HTML format for description and chapter markers (each line as `<br>`).

**Important:** Never auto-overwrite fields that already contain content.

## Edge cases

- **Very long transcripts (60–90 min):** Process in chunks but always produce a complete set of chapter markers covering the full duration. Do not truncate.
- **Short transcripts (< 2 min):** Still produce titles and description. Chapter markers may have only 3 entries.
- **Poor transcript quality:** If the VTT has many "[inaudible]" or garbled text, note this to the user and do your best with available content.
- **Multiple speakers not identified:** VTT files often don't label speakers — infer from context clues (introductions, "Thanks [name]", etc.).
- **No clear demo sections:** Not all videos have demos — skip the demo chapter markers and focus on topic transitions.

## Requirements

- Python 3.8+ (for the VTT parser script)
- Access to Azure DevOps `Studios` project (for work item updates)
- **Azure DevOps MCP server** — bundled with this plugin via `.mcp.json` (uses `@azure-devops/mcp`)

### Checking for ADO MCP server

Before attempting to write to ADO, verify the ADO MCP server is available by checking if ADO tools (like `ado-wit_get_work_item`) are accessible. If they are not:

1. Inform the user: "The Azure DevOps MCP server is not available. You'll need it to update Episode work items."
2. The ADO MCP server is packaged with this plugin in `.mcp.json`. If it's not loading, check that the plugin is installed correctly.
3. The skill can still generate titles, descriptions, and chapter markers without ADO — it just can't write them to a work item. Offer to output the metadata so the user can copy/paste manually.
