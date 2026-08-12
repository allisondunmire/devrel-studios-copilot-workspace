# Learnings

<!-- Copilot adds to this file as you work together. Format:
- **[Topic]** — what you learned. *Why it matters:* [context]
-->

## Copilot Tips

## Workflow Tips

## Tool Tips

- **Standard Outlook connector can read the DRStudios shared calendar** — `Get calendar view of events (V3)` successfully queried only `drstudios@microsoft.com`, while the Outlook `Send an HTTP request` action was blocked by DLP with status 442. *Why it matters:* Shared-calendar availability and event creation are possible without the blocked HTTP/Graph connector or personal-calendar access.
- **SharePoint Choice fields are objects in Power Automate** — Stage and Status often require their nested `Value` property, such as `item()?['Stage']?['Value']`. *Why it matters:* Comparing the whole object to text silently produces empty filters and incorrect availability.
- **Outlook calendar boundaries need explicit overlap filtering** — Calendar View may return an event that ends exactly when a requested slot begins. *Why it matters:* Use strict overlap logic (`start < slot end` and `end > slot start`) to avoid false conflicts between adjacent appointments.
- **Power Automate personal dev environment blocks connectors** — The "Personal Developer - (default)" DLP policy blocks the `HTTP with Microsoft Entra ID` connector, so you can't call the Microsoft Graph API directly from your personal environment. *Why it matters:* Rules out the "proper" deep-folder OneNote automation; standard connectors (like OneNote Business) are still allowed. To use Graph, you'd need IT to allow the connector or move to an approved environment.
- **OneNote API can't sync your notebooks ("Sync of this section is not supported", 422)** — The OneNote (Business) connector fails with this error on both an existing section and a brand-new web-created notebook in your `v-adunmire` OneDrive. *Why it matters:* Appears to be an account/tenant-level limitation, not a flow mistake — brand-new notebooks failing rules out size/age. Worth a Helpdesk ticket asking why the OneNote API can't sync your notebooks. Backup: use OneNote's built-in template feature + a daily reminder instead of the API.
- **Browser popup blocker breaks connector sign-in** — "The browser has blocked the connection authentication popup window" just means Edge blocked the sign-in popup. *Why it matters:* Not a permissions problem — allow pop-ups for `[*.]powerautomate.com` and retry.
