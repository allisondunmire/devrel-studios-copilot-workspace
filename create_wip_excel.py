from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


def add_title(ws, title: str, subtitle: str | None = None) -> int:
    ws["A1"] = title
    ws["A1"].font = Font(size=16, bold=True)
    ws.merge_cells("A1:H1")

    next_row = 2
    if subtitle:
        ws["A2"] = subtitle
        ws["A2"].font = Font(italic=True, color="666666")
        ws.merge_cells("A2:H2")
        next_row = 3

    return next_row


def add_kv_table(ws, start_row: int, rows: list[tuple[str, str]]) -> int:
    ws.cell(row=start_row, column=1, value="Section")
    ws.cell(row=start_row, column=2, value="Details")
    for col in (1, 2):
        cell = ws.cell(row=start_row, column=col)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")

    row = start_row + 1
    for key, value in rows:
        ws.cell(row=row, column=1, value=key)
        ws.cell(row=row, column=2, value=value)
        row += 1

    return row + 1


def add_table(ws, start_row: int, headers: list[str], rows: list[list[str]]) -> int:
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=start_row, column=col_idx, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    row = start_row + 1
    for data_row in rows:
        for col_idx, value in enumerate(data_row, start=1):
            cell = ws.cell(row=row, column=col_idx, value=value)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        row += 1

    return row + 1


def autofit_columns(ws, min_width: int = 12, max_width: int = 70) -> None:
    col_max: dict[int, int] = {}
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            if cell.value is None:
                continue
            val = str(cell.value)
            longest_line = max((len(line) for line in val.splitlines()), default=0)
            col_max[cell.column] = max(col_max.get(cell.column, 0), longest_line)

    for col_idx, width in col_max.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = max(min_width, min(max_width, width + 2))


wb = Workbook()
ws_overview = wb.active
ws_overview.title = "Overview"

start = add_title(
    ws_overview,
    "DevRel Bird's Eye / WIP (Work In Progress)",
    "Captured from OneNote content | Source date in note: Tuesday, January 30, 2024 10:28 AM",
)

overview_rows = [
    (
        "DevRel high level check-in objectives",
        "Reduce standing meetings that needlessly consume calendar blocks; communicate project resource conflicts and overlapping deadlines; clarify relative priorities across simultaneous projects; keep this meeting at overview level (Project vs Project) for full-team audience; improve org-level overview for the entire team.",
    ),
    (
        "Project intake",
        "1) Send video requests to USF form: https://aka.ms/DevRelStudiosSubmission\n2) Proposals reviewed in Content Review meeting\n3) After approval, EP meets with content owner\n4) EP updates parent ADO item with episode items for creative team execution",
    ),
    (
        "CoreIdentity Entitlements for ADO access",
        "Studios ADO Entitlement: https://coreidentity.microsoft.com/manage/Entitlement/entitlement/studiosadopr-gyl1",
    ),
    (
        "DevRel Studios documentation wiki",
        "DevRel Studios wiki: https://dev.azure.com/devrel/Studios/_wiki/wikis/Studios.wiki/6301/DevRel-Studios",
    ),
    (
        "Run of Show template",
        "DevRelStudios_ROS_Template: https://microsoft.sharepoint.com/:x:/t/MicrosoftDeveloperStudiosChannel9/EZdkE5pjzK9DgSzGXyk1Jo4Bi7PL3RMFkWJgIEOvETCmsQ?e=rrXkI4",
    ),
    (
        "Social platforms guidelines",
        "MSDev Social Creative Overview for Videos.pptx: https://microsoft-my.sharepoint.com/:p:/r/personal/chrbooth_microsoft_com/Documents/MSDev%20Social%20Creative%20Overview%20for%20Videos.pptx?d=wc76987b3912546c8b8451c6e75414406&csf=1&web=1&e=X9WMIU",
    ),
    (
        "Studio JunkDrawer",
        "Studios Ops JunkDrawer Backlog: https://dev.azure.com/devrel/Studios/_backlogs/backlog/Studios%20Ops/JunkDrawer",
    ),
]
next_row = add_kv_table(ws_overview, start, overview_rows)

team_headers = [
    "Person with agenda item",
    "ADO (optional)",
    "Relevant dates",
    "Info/Discussion",
    "Action items / Questions",
]
team_rows = [
    [
        "Cameron / Matt",
        "",
        "Find a week to go dark - likely mid Aug",
        "Summer studio organization",
        "Team to identify summer OOF windows and land on a week for cleanup/organization.",
    ]
]
add_table(ws_overview, next_row, team_headers, team_rows)
autofit_columns(ws_overview)

ws_prod = wb.create_sheet("Production")
prod_start = add_title(ws_prod, "Production - Active Projects")
prod_headers = [
    "Timeframe",
    "Active project",
    "EP",
    "Type",
    "Recording dates",
    "TD",
    "Location",
    "Notes",
]
prod_rows = [
    ["THIS WEEK", "Data Exposed (ADO 182486)", "Ross", "Show", "5/18", "Anna H", "StreamYard", ""],
    ["THIS WEEK", "GitHub Copilot Dev Days (ADO 230864)", "Cameron", "Event", "5/27", "Matt", "Studio - Stages A & C", ""],
    [
        "THIS WEEK",
        "Cozy AI Kitchen (ADO 182227)",
        "Ross",
        "Show",
        "5/29",
        "Matt",
        "Studio - Stage A",
        "Guests: General Robotics reshoot, Rohan Malpani, Thoa Nguyen, Stacey Mulcahy",
    ],
    ["NEXT WEEK", "Data Exposed (ADO 228525)", "Ross", "Show", "6/1", "Anna H", "StreamYard", ""],
    [
        "NEXT WEEK",
        "GLEAM Pride 2026 Virtual Kick off - pre-record (ADO 221377)",
        "Kaitlin",
        "Pre-record",
        "6/2",
        "Matt",
        "StreamYard",
        "",
    ],
    [
        "NEXT WEEK",
        "Microsoft Build 2026 (ADO 225153)",
        "Golnaz / Kaitlin",
        "Event",
        "6/2 - 6/3",
        "On location",
        "On location - SF",
        "Live stage; content planning file noted in source. EP assignments: Kaitlin + Anna (red/blue Day 1), Sara + Kavita (yellow/green Day 2), Aurea (photography/thumbnails), Cameron (breakout), Ross (interstitial content).",
    ],
]
add_table(ws_prod, prod_start, prod_headers, prod_rows)
autofit_columns(ws_prod)

ws_pre = wb.create_sheet("Pre-Production")
pre_start = add_title(ws_pre, "Pre-Production - Active Projects")
pre_headers = [
    "Active project",
    "EP",
    "Type",
    "Relevant dates",
    "Location",
    "Status",
    "Action items / Questions",
]
pre_rows = [
    [
        "Fabric Tech Talk Fridays (ADO 174864)",
        "Golnaz",
        "Show",
        "June, TBD",
        "StreamYard",
        "Scheduling",
        "2 new episodes to schedule for early June.",
    ],
    [
        "GLEAM Pride 2026 Virtual Kick off (ADO 221377)",
        "Kaitlin",
        "Event",
        "6/10",
        "Studio",
        "Scheduling",
        "Content owner: Carlos Herquinio. ASL interpreters requested through RUN and confirmed, waiting on info. Green room reserved. Need session invite to Rain and other in-person presenters and crew invite. Note: Kaitlin to send invites while Allison is OOF/medical.",
    ],
    [
        "Quest to Compile (ADO 214995)",
        "Sara",
        "Series",
        "6/11",
        "Studio - Stage C",
        "Scheduled",
        "StreamYard self-service, in studio (recording 3 episodes).",
    ],
    [
        "Avatar shoot - Rick Claus (ADO 228439)",
        "Aurea",
        "Series",
        "6/11",
        "Studio - Stage A (green screen)",
        "Scheduled",
        "",
    ],
    [
        ".NET Day of Agentic Modernization 2026 (ADO 222161)",
        "Cameron",
        "Event",
        "6/16",
        "StreamYard",
        "Scheduling",
        "Half-day (9am-1pm) StreamYard event, Matt as TD. Presenters/hosts all remote (7 sessions). All pre-records scheduled for 6/8. Sessions need to be added to ADO.",
    ],
]
add_table(ws_pre, pre_start, pre_headers, pre_rows)
autofit_columns(ws_pre)

ws_plan = wb.create_sheet("Planning")
plan_start = add_title(ws_plan, "Development & In Planning")
plan_headers = [
    "Fiscal period",
    "Project",
    "EP",
    "Type",
    "Relevant dates",
    "Location",
    "Greenlit or Uncertain",
    "Notes / Action items",
]
plan_rows = [
    [
        "FY26 - Q4",
        "Build Your Personal Portfolio Website in Minutes: AI-Powered Coding for Students (ADO 227810)",
        "Cameron",
        "Series",
        "6/22 - 6/26",
        "TBD",
        "In planning",
        "Episode info needed in ADO. Chris working on branding. Holding week of 6/22 for recording (mix of studio and location). Could be pushed into FY27 - update needed.",
    ],
    [
        "FY27 - Q1",
        "Pure Virtual C++ (ADO 230213)",
        "",
        "",
        "",
        "Likely virtual",
        "",
        "Producing 8-10 on-demand sessions? Hosts TBD (Sinem Akinci? Erika Sweet?). Kaitlin waiting on content owner (Marion).",
    ],
    [
        "FY27 - Q1",
        "Visual Studio Live! @ MSHQ session recording (ADO 231304)",
        "",
        "Proposal - Event",
        "7/27 - 7/29",
        "Commons (B98) + B92 + Studio for VST episodes",
        "",
        "Want capture of 3 days instead of 2, plus some VST episodes in studio (with Leslie Richardson).",
    ],
    [
        "FY27 - Q1",
        "MCP Dev Days (ADO 228660)",
        "Sara / Aurea",
        "Proposal - Event",
        "9/15",
        "Studio + virtual (Teams)",
        "In planning",
        "3-hour livestream studio event with in-studio hosts and virtual presenters. Green room reserved. Should this be ingested?",
    ],
    [
        "FY27 - Q1",
        ".NET Conf 2026 (ADO 221377)",
        "Cameron",
        "Event",
        "Week of 11/9",
        "Studio - all stages",
        "In planning",
        "Green room reserved.",
    ],
    [
        "FY27 - Q1",
        "PROPOSALS and any other upcoming projects",
        "",
        "",
        "",
        "",
        "",
        "ADO query: https://dev.azure.com/devrel/Studios/_queries/query/4ad8ccbc-1cfb-4b6b-b863-a492b382e206/",
    ],
]
add_table(ws_plan, plan_start, plan_headers, plan_rows)
autofit_columns(ws_plan)

ws_post = wb.create_sheet("Post-Prod & Pub")
post_start = add_title(ws_post, "Post Production + Publication")
post_headers = [
    "Active projects",
    "On Demand",
    "Publish Date",
    "Info/Discussion",
    "Priority/Lift/Notes",
    "Action items/Questions",
]
post_rows = [["", "", "", "", "", ""]]
add_table(ws_post, post_start, post_headers, post_rows)
autofit_columns(ws_post)

for ws in wb.worksheets:
    ws.freeze_panes = "A4"

output_path = Path("DevRel_BirdsEye_WIP.xlsx")
wb.save(output_path)
print(f"Created: {output_path.resolve()}")
