# YouTube Description Skill — Setup Guide

This guide walks you through setting up your machine to use the **youtube-description** skill, which updates video titles and descriptions on YouTube from ADO Episode work items using the YouTube Data API.

## Prerequisites

- Windows machine
- Node.js installed
- Access to Azure DevOps (`devrel` org, `Studios` project)
- GitHub Copilot CLI installed and licensed
- Google account added as a **test user** in the YouTube API project (ask your team lead)

## Step 1: Install the Skill

Clone or copy the skill files to your Copilot skills directory:

```
~\.copilot\skills\youtube-description\
  ├── SKILL.md
  ├── SETUP.md
  └── youtube-api.js
```

## Step 2: Get the OAuth Client Credentials

Ask your team lead for the `credentials.json` file (contains the Google OAuth client ID and secret). This is shared across the team.

Save it to:
```
~\.copilot\youtube-tokens\credentials.json
```

The file looks like:
```json
{
  "client_id": "...",
  "client_secret": "..."
}
```

## Step 3: Run the Auth Flow

The auth script is located at `~\.copilot\youtube-tokens\auth.js`.

If you don't have it yet, ask your team lead for a copy, or create it from the repo.

Run the auth flow for each channel you need access to:

```powershell
node ~/.copilot/youtube-tokens/auth.js msdev
```

This will:
1. Open your browser for Google authorization
2. Ask you to grant YouTube access
3. Save a token to `~\.copilot\youtube-tokens\msdev.json`

Repeat for each channel:
```powershell
node ~/.copilot/youtube-tokens/auth.js azd
node ~/.copilot/youtube-tokens/auth.js vs
```

> **Note:** You must be logged into the correct Google account for each channel when authorizing.

## Step 4: Verify Your Setup

Open Copilot CLI and try:

```
Update YouTube description for Episode #221450 on msdev
```

The skill will:
1. Fetch the Episode's metadata from ADO
2. Show you a preview of the title and description
3. Ask for confirmation before writing to YouTube
4. Update the video via the YouTube API
5. Verify the changes

## Available Channels

Check which channels you have tokens for:

```powershell
Get-ChildItem ~/.copilot/youtube-tokens/*.json | ForEach-Object { $_.BaseName }
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Skill definition | `~\.copilot\skills\youtube-description\SKILL.md` | Instructions for Copilot |
| API helper script | `~\.copilot\skills\youtube-description\youtube-api.js` | YouTube API wrapper |
| Auth script | `~\.copilot\youtube-tokens\auth.js` | OAuth flow for new channels |
| Channel tokens | `~\.copilot\youtube-tokens\<channel>.json` | Per-channel auth tokens |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No token found for channel" | Run: `node ~/.copilot/youtube-tokens/auth.js <channel>` |
| "Token refresh failed" | Your refresh token may be revoked. Re-run the auth flow. |
| "Access blocked" during auth | Your Google account needs to be added as a test user in the Google Cloud Console. Ask your team lead. |
| "Video not found" | Check the video ID and make sure you're using the right channel. |
| 403 Forbidden | The channel account may not have access. Verify test user setup. |

## Security Notes

- **Never commit tokens** to any git repository
- Tokens are stored locally on your machine only
- Each person gets their own tokens via the auth flow
- The OAuth client ID/secret should be shared via a secure channel (Teams, 1Password), not in code
- The skill always shows a preview and asks for confirmation before writing to YouTube

## Questions?

Reach out to your team lead for help with setup or access to the Google Cloud project.
