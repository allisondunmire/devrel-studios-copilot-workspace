---
name: publish-skill-to-github
description: >
  Safely publish a skill or focused workspace change to a shared GitHub repository.
  Use when the user asks to share a skill, push a change to GitHub, contribute a skill
  to the team repository, open a pull request, publish an update for others, or walk
  through Git and GitHub as a first-time contributor. Isolates intended files, creates
  a feature branch, commits, handles missing write permission with a fork, and opens a
  pull request without including unrelated workspace changes.
---

# Publish a Skill to GitHub

Publish one skill or another focused workspace change to a shared GitHub repository.
Protect unrelated work, explain each Git concept for new contributors, and verify every
remote operation.

## Input

Identify these details from the request and repository before changing Git state:

- The exact file or directory to publish
- The source repository and default branch
- The current local branch and remotes
- Whether the user wants explanation only, guided execution, or direct execution

If the intended files are ambiguous, ask the user to identify them. Do not infer a broad
set of files from a dirty working tree.

## Interaction Mode

Choose the mode from the user's wording:

- **Explanation only**: For "how do I" questions, explain the workflow and commands but
  do not change Git state.
- **Guided execution**: For "walk me through it," perform one step at a time. Before each
  step, explain what the command changes and whether it affects only the local repository
  or GitHub.
- **Direct execution**: For explicit requests such as "publish this skill" or "open the
  PR," perform the complete workflow with concise progress updates.

Creating a commit, pushing a branch, forking a repository, and opening a pull request are
allowed only when the user's request clearly asks to publish or execute the workflow.

## Safety Rules

- Never use `git add -A`, `git add .`, or another broad staging command.
- Never include files outside the exact requested scope.
- Never discard, stash, reset, clean, or overwrite unrelated user changes.
- Never use `git push --force`, `git reset --hard`, or `git checkout --`.
- Never commit directly on the default branch. Create a feature branch first.
- Never amend or rewrite an existing commit unless the user explicitly requests it.
- Never overwrite an existing remote or branch. Reuse it only after verifying its URL
  and purpose.
- Treat HTTP 403 as a permissions signal. Do not retry direct pushes with credentials or
  alternate authentication methods; use a fork and pull request.
- Do not request passwords, personal access tokens, SSH keys, or other secrets in chat.

## Workflow

### 1. Inspect the Repository

Run read-only checks:

```powershell
git status --short --branch
git branch --show-current
git remote -v
```

Report:

- Current branch
- Intended changed files
- Count of unrelated modified and untracked files
- Source remote URL

If the working tree is dirty, continue only with exact-path staging. Do not ask the user
to discard unrelated work.

### 2. Verify the Intended Change

For every intended path, determine whether it is tracked, untracked, or ignored:

```powershell
git status --short --untracked-files=all -- <path>
git ls-files -- <path>
git check-ignore -v -- <path>
```

Review tracked changes with:

```powershell
git diff -- <path>
```

For an untracked skill, read its files and explain that the first commit will add the
whole skill. If an intended path is ignored, explain why and ask before changing ignore
rules.

### 3. Create a Feature Branch

Create the branch before staging or committing:

```powershell
git switch -c <short-descriptive-branch>
```

Use a lowercase kebab-case branch name such as `update-calendar-invite-subjects` or
`add-video-staging-skill`. If the branch exists, inspect it and reuse it only when it is
clearly for the same change.

Validate:

```powershell
git branch --show-current
```

### 4. Stage Exact Paths

Stage only the approved files or directory:

```powershell
git add -- <exact-path>
```

Immediately validate the staged set:

```powershell
git diff --cached --name-status
git diff --cached --check
```

If any unrelated path is staged, stop and unstage only that path with
`git restore --staged -- <path>`. Do not modify its working-tree contents.

### 5. Commit Locally

Use a present-tense commit message under 72 characters:

```powershell
git commit -m "<clear summary>"
```

Then report and validate:

```powershell
git show --stat --oneline --summary HEAD
```

Confirm that the commit contains only the intended files.

### 6. Determine the Publishing Path

Use the GitHub authenticated-user tool before other GitHub operations. Compare the
authenticated account with the source repository owner and available permissions.

If the user can push to the source repository, publish the feature branch:

```powershell
git push -u origin <branch>
```

Never push a contribution directly to the default branch.

If the push returns HTTP 403 or the user lacks write permission, continue with the fork
workflow. Do not treat this as a failed contribution.

### 7. Fork When Needed

Use the GitHub fork tool to create a fork under the authenticated user's account. Wait
until the fork exists before pushing.

Add a local remote only if one does not already point to that fork:

```powershell
git remote add fork https://github.com/<user>/<repository>.git
git push -u fork <branch>
```

If `fork` already exists, verify its URL. If it points elsewhere, choose a distinct name
such as `personal-fork`; never replace it silently.

Validate that the local branch tracks the expected remote branch and is up to date.

### 8. Open the Pull Request

Before creating a pull request, search for:

- `.github/pull_request_template.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/PULL_REQUEST_TEMPLATE/`

Use the template when present. Otherwise use:

```markdown
## Summary
- <what changed>
- <why it changed>

## Validation
- <checks performed>
```

Open the pull request against the source repository's default branch. For a fork, use
`<username>:<branch>` as the head. Allow maintainer edits unless the user says otherwise.

### 9. Verify and Explain the Result

Return:

- Commit hash and message
- Published branch and repository
- Pull-request link, when created
- Confirmation that unrelated local changes were untouched
- The next human action, such as review and merge by the repository owner

In guided mode, briefly reinforce these concepts:

- **Stage** selects files for the next commit.
- **Commit** records a local checkpoint.
- **Branch** isolates the proposed change.
- **Push** uploads a branch to GitHub.
- **Fork** is the contributor's copy of a repository.
- **Pull request** asks the source repository to review and merge the branch.

## Recovery Cases

### Commit Was Made on the Default Branch

If the intended commit exists only locally and has not been pushed, create a feature
branch at the current commit. Do not reset the default branch while unrelated working
changes exist. Publish the feature branch and explain that local default-branch cleanup
can be handled separately after protecting all work.

### Push Was Rejected

- HTTP 403: use a fork and pull request.
- Non-fast-forward: stop and inspect remote history. Do not force-push.
- Authentication prompt requiring a secret: ask the user to complete authentication
  directly in GitHub or the terminal; never collect the secret in chat.

### No Pull-Request Permission

Provide the published fork branch URL and the exact base/head values needed to open the
pull request manually. Do not claim that a pull request was created.

## Example Requests

> Share the updated calendar-invite skill with the team GitHub repository.

> Walk me through publishing this new skill. I have not used Git before.

> Push only `skills/my-skill/` and open a pull request without including my other changes.