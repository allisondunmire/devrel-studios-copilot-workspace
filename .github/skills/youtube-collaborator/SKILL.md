---
name: youtube-collaborator
description: >
  Use when the user wants to add a YouTube channel as a collaborator on a Microsoft
  Developer video, including requests like "add a YouTube collaborator", "collaboration
  invite", "cross-promote video", or when they want to add a specific channel on a video.
  Collects the ADO work item ID or YouTube video URL and collaborator channel name, then
  automates YouTube Studio to create a collaboration invite link, posts it to ADO, and
  emails the collaborator.
---

# YouTube Video Collaborator Skill

Add another YouTube channel as a "collaborator" on videos published to the Microsoft Developer channel. This makes the video appear on both channels and cross-promotes content.

## Key Facts
- Collaboration is **per-video only** — there is no playlist-level collaboration
- Each video needs its own collaborator invite link
- The collaborator must **accept** the invite from their end
- Default channel: **Microsoft Developer** (youtube.com/@MicrosoftDeveloper)
- Common collaborator: **Stacey Haffner's channel** (@staceyhaffner, Quest to Compile)

## Quick Start
When the user says **"add a YouTube collaborator"** (or similar), immediately ask them for two pieces of info using the `ask_user` tool — one question at a time:

1. **First question:** "What's the ADO work item ID or YouTube video URL?"
2. **Second question:** "Who should be added as collaborator?" *(provide choices from the Known Collaborator Channels table below, plus allow freeform)*

Then run the full automation flow below — no further confirmation needed.

## What You Need From the User
1. **ADO work item ID** (e.g., "Episode 229938") — OR — a **YouTube video URL/ID**
2. **Collaborator channel name** (e.g., "Stacey Haffner")

## Known Collaborator Channels
| Collaborator | YouTube Handle | Email | Use Case |
|-------------|---------------|-------|----------|
| Stacey Haffner | @staceyhaffner | shaffner@microsoft.com | Quest to Compile episodes |
| *(add more as needed)* | | | |

## Finding the Collaborator's Contact Info
The collaborator's email (for sending the invite notification) is typically stored in the ADO work item in one of these presenter fields:
- `Custom.Primarypresenter`
- `Custom.Secondarypresenter`
- `Custom.Remotepresenters`
- `Custom.Additionalpresenters`
- `Custom.Additionalinvitees`

When pulling the ADO work item in Step 1, also read these fields. Match the collaborator name to the correct field to get their email address for the notification email.

---

## Automated Flow

### Prerequisites
- **Edge must be running** with `--remote-debugging-port=9222`
- **User must be logged into YouTube Studio** in that Edge window
- **mcp-config.json** must be set to CDP mode: `--cdp-endpoint http://localhost:9222`
- If Edge was restarted without the debugging flag, CDP will fail
- **Outlook desktop app** must be installed and running for email automation (Step 12). If Outlook COM is not available, fall back to asking the user to send the invite link manually

### How to Start Edge with Debugging Port
```powershell
Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList "--remote-debugging-port=9222"
```

### End-to-End Automation Steps

#### Step 1: Get the YouTube Video URL from ADO
- Pull the ADO work item using the work item ID
- Look for field `Custom.YouTubevideostandard` (Studios project, Episode type)
- Alternative field: `Custom.YouTubeURL` (Learn TV project, Segment type)
- Other available fields: `Custom.YouTubeChannel`, `Custom.YouTubeplaylist`, `Custom.YouTubevideoshorts`

#### Step 2: Extract the Video ID
- From `https://youtu.be/6Q6zcwCB8x0` → video ID = `6Q6zcwCB8x0`
- From `https://youtube.com/watch?v=6Q6zcwCB8x0` → video ID = `6Q6zcwCB8x0`

#### Step 3: Navigate to YouTube Studio
- Go to: `https://studio.youtube.com/video/{videoID}/edit`

#### Step 4: Expand Advanced Settings
- YouTube Studio hides the Collaboration section behind a **"Show more"** button
- Click the "Show more" button using JavaScript:
```javascript
document.evaluate(
  "//button[.//span[contains(text(),'Show more')]]",
  document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
).singleNodeValue.click();
```

#### Step 5: Scroll to Collaboration Section
- The page uses **internal scrollable containers**, NOT `window.scrollBy()`
- Find the scrollable container and the Collaboration section label:
<!-- inline-ok -->
```javascript
const labels = document.querySelectorAll('.section-label-with-description');
for (const label of labels) {
  if (label.textContent.includes('Collaboration')) {
    label.scrollIntoView({ behavior: 'smooth', block: 'center' });
    break;
  }
}
```

#### Step 6: Open the Collaborator Dialog
> ⚠️ **There are TWO different flows depending on whether the video already has collaborators.**

##### Flow A: Video Has NO Existing Collaborators
- The button says **"Invite a collaborator"**
```javascript
document.evaluate(
  "//button[.//span[contains(text(),'Invite a collaborator')]]",
  document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
).singleNodeValue.click();
```

##### Flow B: Video ALREADY HAS Collaborators
- The button says **"Manage collaborators"**
```javascript
document.evaluate(
  "//button[.//span[contains(text(),'Manage collaborators')]]",
  document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
).singleNodeValue.click();
```

**Tip:** Try both selectors — whichever matches is the correct flow.

#### Step 7: Search for the Collaborator Channel
- The dialog has a search input with placeholder "Search for a channel"
- Type the collaborator's name and wait for results:
```javascript
const input = document.querySelector('input.search-input[placeholder="Search for a channel"]');
input.value = 'Stacey Haffner';
input.dispatchEvent(new Event('input', { bubbles: true }));
```

#### Step 8: Select the Channel from Results
- Wait 2-3 seconds for search results to appear
- The results appear as clickable items below the search bar
- Use keyboard navigation to select the result (resolution-independent — works regardless of screen size, DPI, or zoom):
```javascript
// Press ArrowDown to move focus to the first search result, then Enter to select
await page.keyboard.press('ArrowDown');
await page.keyboard.press('Enter');
```
- If keyboard navigation doesn't work, fall back to finding the result element by its text content:
<!-- inline-ok -->
```javascript
const results = document.querySelectorAll('[role="option"], [role="listbox"] > *');
for (const r of results) {
  if (r.textContent.includes('Stacey Haffner')) {
    r.click();
    break;
  }
}
```

#### Step 9: Create and Copy the Invite Link
- After selecting the channel, a **"Create link"** button appears
- Click **"Create link"**
- A dialog appears with the generated invite URL
- Extract the link from the DOM:
<!-- inline-ok -->
```javascript
// Match the invite link URL pattern (works for any channel, not just Microsoft Developer)
const divs = document.querySelectorAll('div, span, p');
for (const el of divs) {
  if (el.textContent.includes('studio.youtube.com/channel/') &&
      el.textContent.includes('/collaboration/') &&
      el.children.length === 0) {
    return el.textContent.trim();
  }
}
```
- The invite link format: `https://studio.youtube.com/channel/{channelID}/collaboration/{collaboratorChannelID}`

#### Step 10: Close the Link Dialog and Save
- Close the inner "Copy invite link" dialog:
```javascript
document.querySelector('.close-button.style-scope.ytcp-video-collaborator-invite-link-dialog').click();
```
- Then click **Save** on the collaborator dialog:
<!-- inline-ok -->
```javascript
const buttons = document.querySelectorAll('ytcp-button, button');
for (const b of buttons) {
  if (b.textContent.trim() === 'Save' && b.closest('ytcp-video-collaborators-dialog')) {
    b.click();
    break;
  }
}
```
- **Note:** The main page Save button may remain disabled — this is normal. The collaborator dialog saves its own changes independently.

#### Step 11: Post the Invite Link to ADO
- Add a comment to the original ADO work item:
  ```
  YouTube collaborator invite link for **[Collaborator Name]** (@handle):

  [invite link URL]

  Please share this link with [Collaborator] so they can accept the collaboration invite.
  ```

#### Step 12: Send Email to the Collaborator
- Look up the collaborator's email from the ADO work item presenter fields (see "Finding the Collaborator's Contact Info" above)
- If the collaborator's email can't be found in ADO, use `ado-core_get_identity_ids` to look up their Microsoft email, or ask the user for it
- **Try Outlook COM automation first** (requires Outlook desktop app to be installed and running):
<!-- environment-specific COM automation; requires Outlook desktop running, cannot be tested or reused independently -->
<!-- inline-ok -->
  ```powershell
  $outlook = New-Object -ComObject Outlook.Application
  $mail = $outlook.CreateItem(0)
  $mail.To = "[collaborator email]"
  $mail.Subject = "YouTube Collaboration Invite - [Video Title]"
  $mail.Body = "Hi [Name]!`n`nHere's the YouTube collaboration invite link for `"[Video Title]`". Please click the link and accept from your YouTube channel:`n`n[invite link]`n`nThank you!"
  $mail.Send()
  ```
- **Fallback if Outlook COM is not available:** Tell the user the invite link was created and posted to ADO, and provide the collaborator's email and a pre-written message they can copy-paste to send manually.

---

## How to Confirm It Worked
After the flow completes, the Collaboration section button text changes:
- **Before** (no collaborators): "Invite a collaborator"
- **After** (collaborator added): "Manage collaborators"

The collaborator will show with status **"Pending acceptance"** until they accept the invite.

---

## Sending Notifications via Teams
If the user prefers a Teams message instead of (or in addition to) email, use the **Teams-Send-Message** skill.

Key points:
- For 1:1 messages to a collaborator: use the **deep link** approach
- For posting to a group chat: use the **search + clipboard paste** approach
- ⚠️ **NEVER use `innerText`** to set text in Teams' compose box — always use clipboard paste (Ctrl+V)

---

## YouTube Studio DOM Quirks & Troubleshooting

| Issue | Solution |
|-------|----------|
| Accessibility snapshots return empty | YouTube Studio uses heavy JS/Shadow DOM; must use `document.evaluate()` and DOM queries |
| Page scrolling doesn't work | YouTube Studio uses **internal scrollable containers**, not `window.scrollBy()`. Use `element.scrollIntoView()` instead |
| "Show more" button hides Collaboration | Always click "Show more" first before looking for Collaboration section |
| Button text varies by state | "Invite a collaborator" (no collabs) vs "Manage collaborators" (has collabs) |
| Search results hard to click | Use `page.mouse.click(x, y)` at coordinate positions; custom elements resist standard selectors |
| Multiple "Close" / "Save" buttons | Scope selectors to the specific dialog class |
| Main page Save disabled after dialog save | Normal — collaborator dialog saves independently |
| CDP connection fails | Edge must be running with `--remote-debugging-port=9222`; restart Edge with the flag |

## ADO Field Reference

### YouTube URL Fields
| Project | Work Item Type | YouTube URL Field |
|---------|---------------|-------------------|
| Studios | Episode | `Custom.YouTubevideostandard` (standard video) |
| Studios | Episode | `Custom.YouTubevideoshorts` (shorts video) |
| Studios | Episode | `Custom.YouTubeChannel` |
| Studios | Episode | `Custom.YouTubeplaylist` |
| Learn TV | Segment | `Custom.YouTubeURL` |

### Presenter / Contact Fields
| Field | Description |
|-------|-------------|
| `Custom.Primarypresenter` | Main presenter — most likely collaborator |
| `Custom.Secondarypresenter` | Secondary presenter |
| `Custom.Remotepresenters` | Remote presenters |
| `Custom.Additionalpresenters` | Additional presenters |
| `Custom.Additionalinvitees` | Additional invitees |

## Batch Workflow (Multiple Videos)
When publishing a series (like Quest to Compile), repeat the automation for each video:

1. Get all child Episode work items from the parent Show work item
2. For each Episode with a `Custom.YouTubevideostandard` URL:
   - Run the automation flow above
   - Collect all invite links
3. Post a summary comment on the parent Show work item with all the links
