# OneNote Daily To-Do — Auto-Copy Flow (Power Automate)

**Goal:** Every weekday, automatically create that day's to-do page in the "Allison @ Microsoft" OneNote, copied as-is from the previous weekday's page, following the existing folder/naming conventions.

**Decisions locked in:**
- Runs **weekdays only** (Mon–Fri).
- New page copies the **previous weekday's page as-is** (including completed/checked-off items).
- **Best-effort auto-creation** of the year group, month group, and week section if they don't exist yet (names may need occasional manual rename around holidays/odd weeks).

---

## Notebook structure (reference)
```
Notebook: Allison @ Microsoft
└── Section group: TO DO LIST
    └── Section group: 2026            (year)
        └── Section group: M07_July    (M##_MonthName)
            └── Section: W4_7.27 - 7.31 (W#_M.d - M.d)  ← week
                └── Pages: Mon 7.27, Tues 7.28, ...     ← days
```

**Important nuance:** A week is filed under the month of its **Friday**. Example: `W1_6.29 - 7.3` lives under `M07_July` even though Monday (6.29) is in June. So all container names are computed from the **Friday of the target week**, not the page's own date.

**Custom day abbreviations:** Mon, **Tues**, Wed, **Thurs**, Fri (note Tues/Thurs, not Tue/Thu).

---

## Why Microsoft Graph (HTTP), not the OneNote connector
Pages live several **section groups** deep. The standard OneNote connector can't traverse nested section groups; Microsoft Graph can. Use the **"HTTP with Microsoft Entra ID"** connector with base resource URI `https://graph.microsoft.com` — it authenticates as you, no app registration required.

---

## 1. Trigger — Recurrence
- Frequency: **Week**, days **Monday–Friday**, time **5:00 AM**, time zone **Pacific Standard Time**.

## 2. Compute dates (Compose / Initialize variable)
| Variable | Expression |
|---|---|
| `targetDate` | `convertFromUtc(utcNow(),'Pacific Standard Time','yyyy-MM-dd')` |
| `targetDOW` | `formatDateTime(variables('targetDate'),'dddd')` |
| `mondayOffset` | Switch on `targetDOW`: Monday=0, Tuesday=-1, Wednesday=-2, Thursday=-3, Friday=-4 |
| `monday` | `addDays(variables('targetDate'), variables('mondayOffset'), 'yyyy-MM-dd')` |
| `friday` | `addDays(variables('monday'), 4, 'yyyy-MM-dd')` |
| `prevDate` | Switch on `targetDOW`: Monday → `addDays(variables('targetDate'),-3,'yyyy-MM-dd')`; default → `addDays(variables('targetDate'),-1,'yyyy-MM-dd')` |

> `friday` is the **anchor** for all container names.

## 3. Build names
**Title helper** (apply to any date `d`):
- 3-letter DOW: `formatDateTime(d,'ddd')`
- Custom abbrev — Switch: `Tue`→`Tues`, `Thu`→`Thurs`, else unchanged → `dayAbbrev`
- Month.day: `formatDateTime(d,'M.d')` → e.g. `7.28`
- **Title** = `concat(dayAbbrev,' ',formatDateTime(d,'M.d'))`

Produce:
- `targetTitle` from `targetDate` (e.g. `Tues 7.28`)
- `prevTitle` from `prevDate` (e.g. `Mon 7.27`)

**Container names** (from `friday`):
| Variable | Expression | Example |
|---|---|---|
| `yearName` | `formatDateTime(variables('friday'),'yyyy')` | `2026` |
| `monthName` | `concat('M',formatDateTime(variables('friday'),'MM'),'_',formatDateTime(variables('friday'),'MMMM'))` | `M07_July` |
| `weekRange` | `concat(formatDateTime(variables('monday'),'M.d'),' - ',formatDateTime(variables('friday'),'M.d'))` | `7.27 - 7.31` |
| `weekOrdinal` (best-effort) | `add(div(sub(int(formatDateTime(variables('friday'),'dd')),1),7),1)` | ordinal Friday of month |
| `weekName` | `concat('W',string(variables('weekOrdinal')),'_',variables('weekRange'))` | `W5_7.27 - 7.31` |

> ⚠️ `weekOrdinal` is a best-effort ordinal of the Friday within its month. Your manual numbering sometimes differs (holiday weeks, merged weeks), so the auto-created section name may need an occasional rename. All later steps locate the section by ID, so a rename won't break the flow mid-week.

## 4. Navigate / auto-create the container hierarchy (Graph)
Pattern for each level: **GET by displayName → if empty, POST to create → capture ID.**

1. **Notebook:** `GET /me/onenote/notebooks?$filter=displayName eq 'Allison @ Microsoft'` → `notebookId`.
2. **TO DO LIST group:** `GET /me/onenote/notebooks/{notebookId}/sectionGroups?$filter=displayName eq 'TO DO LIST'` → `todoGroupId`.
3. **Year group:**
   - `GET /me/onenote/sectionGroups/{todoGroupId}/sectionGroups?$filter=displayName eq '@{variables('yearName')}'`
   - If empty → `POST /me/onenote/sectionGroups/{todoGroupId}/sectionGroups` body `{ "displayName": "@{variables('yearName')}" }`
   - → `yearGroupId`
4. **Month group:** same pattern under `{yearGroupId}` using `monthName` → `monthGroupId`.
5. **Week section:**
   - `GET /me/onenote/sectionGroups/{monthGroupId}/sections?$filter=displayName eq '@{variables('weekName')}'`
   - If empty → `POST /me/onenote/sectionGroups/{monthGroupId}/sections` body `{ "displayName": "@{variables('weekName')}" }`
   - → `weekSectionId`

## 5. Find + read the previous day's page
6. Search current + prior week sections for the source page:
   `GET /me/onenote/sections/{sectionId}/pages?$filter=title eq '@{variables('prevTitle')}'`
   - Try `weekSectionId` first; if no match, list the month group's sections (`GET /me/onenote/sectionGroups/{monthGroupId}/sections`) and check the previous one (covers Monday, whose source is in last week's section — possibly a different month group at month rollover; if needed, repeat navigation for `prevDate`'s anchor).
   - → `sourcePageId`
7. `GET /me/onenote/pages/{sourcePageId}/content?includeIDs=true` → returns page **HTML** (`prevHtml`). This carries **everything as-is**, including completed to-dos.

## 6. Create the new day page
8. Build the new HTML (swap only the title):
```html
<!DOCTYPE html>
<html>
  <head><title>@{variables('targetTitle')}</title></head>
  <body>@{outputs('Get_source_html')?['body']}</body>
</html>
```
> If `prevHtml` is a full HTML doc, extract its `<body>` (Compose with `substring`/`split` on `<body>`…`</body>`) so you don't nest documents. Or `replace()` the old `<title>` text with `targetTitle`.

9. `POST /me/onenote/sections/{weekSectionId}/pages`
   - Header `Content-Type: text/html`
   - Body = the HTML from step 8.

## 7. Guardrails
- **Idempotency:** before step 9, `GET /me/onenote/sections/{weekSectionId}/pages?$filter=title eq '@{variables('targetTitle')}'`; if it exists, **skip** creation (safe re-runs).
- **Missing source page:** if step 6 finds nothing, create a blank template page instead and send yourself a Teams/Outlook notification so you can populate it manually.
- **Ordering:** OneNote orders pages by creation; since the flow runs each morning in sequence, days stay in order within the week section.

---

## Open follow-ups / tuning
- Confirm the `weekOrdinal` rule against a few months of history; if your numbering is consistently "count Mondays in the assigned month," swap the ordinal expression to use `monday`'s day-of-month instead of `friday`'s.
- Consider a second recurrence at month/year rollover to pre-create the next container early (optional; the auto-create in Step 4 already handles it lazily).
