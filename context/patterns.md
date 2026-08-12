# Patterns

<!-- Copilot maintains this file automatically. It logs patterns it notices in how you work — repeated tasks, friction points, and automation candidates. Review this periodically and promote useful patterns to skills. -->

## Repeated Workflows
<!-- Tasks you do more than twice that could become a skill or automation -->

## Friction Points
<!-- Things that take multiple attempts, require manual steps, or slow you down -->

- **Power Automate caches stale SharePoint schemas** — Adding or deleting List columns left flow actions with missing fields, duplicate display names, and invalid references such as `AvailableSlotID1` and `Notes0`. Refreshing an action by switching its List Name away and back exposes the current schema; List settings and the URL's `Field=` value identify the correct internal column. *Why it matters:* Schema drift repeatedly broke otherwise-correct booking flows and can silently clear mappings. Flagged 2026-08-11.
- **OneNote automation blocked at two layers** — Building the daily to-do OneNote flow hit (1) a DLP block on the Graph/HTTP connector in the personal dev environment, then (2) a persistent "Sync of this section is not supported" (422) error from the OneNote Business connector on both old and brand-new notebooks. *Why it matters:* The daily-page automation may not be achievable via Power Automate on this account without IT involvement; a no-API fallback (OneNote template + reminder) is the pragmatic path. Flagged 2026-07-30.

## Skill Candidates
<!-- Patterns ready to be turned into reusable skills -->

- **Recurring OneNote daily page automation** — Daily to-do pages in the "Allison @ Microsoft" notebook need to be created each weekday, copied from the prior day, following a nested section-group naming convention (`TO DO LIST → year → M##_Month → W#_range → day pages`). *Why it matters:* Repetitive daily manual step; strong Power Automate + Microsoft Graph fit. Full build guide drafted at [projects/onenote-daily-flow.md](../projects/onenote-daily-flow.md). Key gotcha: week sections are manually curated around holidays, so auto-naming is best-effort and locates sections by ID. Flagged 2026-07-28.

- **Shoot-type email template → calendar invite** — Each shoot type has a corresponding email template whose content currently has to be manually copy/pasted into the matching calendar invite. *Why it matters:* High-frequency, error-prone manual step tied to the `drstudios@microsoft.com` calendar workflow. Strong fit for a Power Automate flow (trigger on invite creation → look up template by shoot type → populate invite body) or an Outlook Quick Step / template mapping. Flagged during setup-interview 2026-04-21.

## Promoted to Skills
<!-- Patterns that became skills — kept here for history -->
