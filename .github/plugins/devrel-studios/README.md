# DevRel Studios Plugin

The DevRel Studios plugin packages video production workflows for the DevRel Studios team.

## What the Plugin Is

This plugin is a private GitHub Copilot package that bundles Studios-specific skills so they can be installed once and reused instead of being recreated in each workspace.

## Purpose

Streamline the full video publishing lifecycle — from transcript analysis and metadata generation, through YouTube upload and ADO work item tracking, to livestream comment analysis — and automate common DevRel operations like creating aka.ms short URL redirects.

## Value

1. It standardizes video metadata generation and livestream analysis for the DevRel Studios team.
2. It packages parser and download scripts with the plugin so consumers don't need to install them separately.
3. It keeps Azure DevOps MCP configuration packaged with the plugin for Episode work item updates.
4. It provides a clean boundary so Studios workflows do not drift into `mvp-ado` or `devrel-events`.

## Current Scope

This plugin currently contains fourteen skills:

1. `video-staging` — **End-to-end video publishing pipeline.** Parse a transcript, generate metadata (titles, description), upload the video to YouTube as unlisted, and create a full ADO work item hierarchy (Support requests → Episode → Graphics) to track the publishing process. Designed for on-demand videos destined for the Microsoft Developer channel.
2. `vtt-metadata` — Parse VTT/SRT transcripts and generate YouTube titles, descriptions, and chapter markers. Optionally write to ADO Episode work items.
3. `youtube-analysis` — Download and analyze YouTube livestream chat comments for sentiment, themes, geographic reach, and multi-stream comparison.
4. `aka-redirect` — Create aka.ms short URL redirects by filing a Redirection work item in the Studios ADO project. A Logic App automation processes the work item and provisions the aka.ms link.
5. `youtube-collaborator` — Add a YouTube channel as a collaborator on videos published to the Microsoft Developer channel. Automates YouTube Studio UI via Playwright CDP to create collaboration invite links, posts them to ADO, and emails the collaborator.
6. `youtube-description` — Update YouTube video titles and descriptions from ADO Episode work items using the YouTube Data API v3. Reads metadata fields (title, description, chapters, resources, social links, playlist URL), builds a formatted description from a standard template, and updates YouTube after user confirmation. Supports multiple channels.
7. `view-to-tam` — Analyze YouTube video performance relative to the product's Total Addressable Market (TAM). Given a YouTube link, identifies the primary product/technology from the video title, researches the TAM via 6sense web search, estimates the user base (companies × 250 median employees × 7.5% developer ratio), and calculates a view-to-TAM ratio with a performance rating (🔥 >10%, ✅ 3–10%, ⚠️ 1–3%, ❌ <1%). Includes a methodology disclaimer on every output so users can push back on assumptions.
8. `youtube-monthly-watchhours` — Analyze a month of YouTube Studio analytics data and produce an executive-ready report with top 3 videos per channel ranked by watch hours, channel share breakdown, key watch-hour drivers with editorial insight, and a narrative monthly summary suitable for leadership updates. Optionally generates a formatted .docx Word document.
9. `create-studio-support` — **Studio session booking workflow.** Create a Support request work item in the Studios ADO project with a child Episode, both populated with speaker name, studio stage (A/B/C), and start time. Automates the two-step process of creating the parent Support request and linking a child Episode with the correct fields (`Custom.Host1`, `Custom.Stage`, `Custom.Recordingstartdateandtime`).
10. `create-event-episodes` — **Bulk Episode creation from a session list.** Ingest a Topic/Speaker table, Loop/Excel export, or run-of-show and create the matching ADO Episodes under an Event, populate their metadata, and let the studio's child-task automation build each Episode's task tree (Scheduling, Editing, Uploading, Publishing). Verifies the cascading children landed, falls back to manually replicating the child template if the automation doesn't fire, and notifies the scheduling owner.
11. `transcript-proofread` — **Proofread and deliver AI-generated captions.** Ingest a `.vtt`/`.srt` transcript (YouTube auto-captions, Frame.io, or other tools), correct spelling and tech/brand names, and return clean synchronized caption files. Optionally generates SRT, VTT, and TTML together, attaches them to an ADO Episode, or uploads the corrected track through the YouTube Data API.
12. `send-calendar-invite` — **Studios recording invite workflow.** Read an ADO Episode, select the correct recording or livestream template, and produce a review-ready HTML calendar invite for a human to send from the Studios mailbox.
13. `build-event-run-of-show` — **Event agenda to production ROS workflow.** Extract a published event schedule and presenters, confirm production-only mappings such as session type and stage, and populate an existing Excel Run of Show while preserving its formulas and dropdown validation.
14. `delete-studios-orphan-work-items` — **Recoverable orphan cleanup workflow.** Find parentless Episodes and production-task trees in the Studios ADO project, report invalid or suspicious parent relationships, preview every affected ID, and soft-delete confirmed trees leaf-first to the Azure DevOps Recycle Bin with revision and relationship revalidation.

## Scripts

- `scripts/parse-vtt.py` — VTT/SRT parser that consolidates captions, removes duplicates, and outputs clean timestamped text.
- `scripts/download-comments.py` — Downloads chat comments from a YouTube livestream or video.
- `scripts/download-playlist.py` — Downloads comments for every video in a YouTube playlist for cross-stream comparison.

## MCP Server

This plugin includes a plugin-local `.mcp.json` with a baseline Azure DevOps MCP server definition using the `@azure-devops/mcp` package, hardcoded to the `devrel` organization. The packaged config is generic and does not embed secrets.

## Boundaries

This plugin is intentionally scoped to DevRel Studios workflows — video production and operational automation — rather than MVP project workflows or DevRel event management.

## Distribution

This plugin is intended for private distribution through direct install from this repository or from a local checkout.

<!-- BEGIN GENERATED: ownership-and-support -->
## Ownership and support

- Tier: `supported`
- Owners: `@jamescon`
- Policy: See [plugin governance](../../docs/developer-guide/plugin-governance.md)
<!-- END GENERATED: ownership-and-support -->
