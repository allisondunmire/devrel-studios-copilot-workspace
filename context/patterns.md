# Patterns

<!-- Copilot maintains this file automatically. It logs patterns it notices in how you work — repeated tasks, friction points, and automation candidates. Review this periodically and promote useful patterns to skills. -->

## Repeated Workflows
<!-- Tasks you do more than twice that could become a skill or automation -->

- **Reconcile live-show ROS, calendar, and ADO Episodes** — After schedule or format changes, re-download the current ROS, align attendee-free calendar placeholders, and synchronize Episode production mode, filming location, stage, remote platform, and live recording window. *Why it matters:* The same source changes can leave both Outlook template language and ADO production metadata stale; this is a strong extension candidate for [`skills/live-show-calendar/`](../skills/live-show-calendar/). Flagged 2026-10-28.

## Friction Points
<!-- Things that take multiple attempts, require manual steps, or slow you down -->

- **Outlook Word renderer changes invitation list spacing** — Inline `<ul>` margin rules were discarded or reconstructed with default spacing, and clipboard-based Outlook automation could add unintended body artifacts. Use Aptos bullet paragraphs with explicit zero margins, guard any clipboard replacement against the expected Episode ID, and verify the saved rendered body plus one visual sample per template type. *Why it matters:* Source HTML checks alone repeatedly missed visible formatting problems in live-event invitations. Flagged 2026-10-27.
- **Power Automate caches stale SharePoint schemas** — Adding or deleting List columns left flow actions with missing fields, duplicate display names, and invalid references such as `AvailableSlotID1` and `Notes0`. Refreshing an action by switching its List Name away and back exposes the current schema; List settings and the URL's `Field=` value identify the correct internal column. *Why it matters:* Schema drift repeatedly broke otherwise-correct booking flows and can silently clear mappings. Flagged 2026-08-11.
- **OneNote automation blocked at two layers** — Building the daily to-do OneNote flow hit (1) a DLP block on the Graph/HTTP connector in the personal dev environment, then (2) a persistent "Sync of this section is not supported" (422) error from the OneNote Business connector on both old and brand-new notebooks. *Why it matters:* The daily-page automation may not be achievable via Power Automate on this account without IT involvement; a no-API fallback (OneNote template + reminder) is the pragmatic path. Flagged 2026-07-30.

## Skill Candidates
<!-- Patterns ready to be turned into reusable skills -->

- **Recurring OneNote daily page automation** — Daily to-do pages in the "Allison @ Microsoft" notebook need to be created each weekday, copied from the prior day, following a nested section-group naming convention (`TO DO LIST → year → M##_Month → W#_range → day pages`). *Why it matters:* Repetitive daily manual step; strong Power Automate + Microsoft Graph fit. Full build guide drafted at [projects/onenote-daily-flow.md](../projects/onenote-daily-flow.md). Key gotcha: week sections are manually curated around holidays, so auto-naming is best-effort and locates sections by ID. Flagged 2026-07-28.

## Promoted to Skills
<!-- Patterns that became skills — kept here for history -->

- **Outlook-safe live-event invitation formatting** — Added to [`skills/live-show-calendar/`](../skills/live-show-calendar/) on 2026-10-27. The skill now enforces Aptos typography, a 10pt DRStudios contact note, non-bold blue headers, zero-gap bullet paragraphs, attendee-facing studio locations, no accidental embedded images, and rendered-body verification.
- **Weekly WIP agenda reconciliation** — Promoted to [`skills/wip-onenote-update/`](../skills/wip-onenote-update/) on 2026-08-26. The skill previews a merge of top-level ADO projects and categorized DRStudios recording sessions into the existing Development & In Planning format while preserving handwritten notes. A Microsoft List is the preferred future destination because direct OneNote access is unavailable through Work IQ.
- **Live Show Excel → DRStudios calendar appointments** — Promoted to [`skills/live-show-calendar/`](../skills/live-show-calendar/) on 2026-08-17. The skill reads the `LiveShow` table, applies session-type setup buffers, previews and checks duplicates, and creates no-attendee appointments in `drstudios@microsoft.com` only after explicit approval. Originated from the shoot-type template/calendar invite candidate flagged 2026-04-21.
