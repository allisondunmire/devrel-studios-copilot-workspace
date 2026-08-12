# Skills

Reusable prompts and workflows for common tasks. Skills come in two formats:

- **Single-file skills** — a `.md` file with a structured prompt you paste into Copilot (e.g. `setup-interview.md`).
- **Folder-based skills** — a directory with a `SKILL.md` (with YAML frontmatter) plus supporting scripts/references. These are auto-invoked by Copilot when your task matches the skill's description (e.g. `transcript-proofread/`).

## How to Use a Skill

**Single-file skill:**

1. Open the skill file
2. Copy the prompt (or reference it by name if Copilot has context)
3. Paste into Copilot CLI or VS Code Copilot Chat
4. Fill in any `[placeholders]` with your specifics

**Folder-based skill:**

Just describe your task (e.g. "proofread this transcript"). Copilot auto-loads the skill from its `SKILL.md` when the request matches the skill's `description`.

## How to Create a Single-File Skill

Create a new `.md` file in this directory with:

```markdown
# Skill Name

## What it does
[One-line description]

## When to use it
[What situation triggers this skill]

## Prompt
[The actual prompt to give Copilot — include placeholders for variable parts]

## Example
[A filled-in example so people can see how it works]
```

## How to Create a Folder-Based Skill

Create a subdirectory with a `SKILL.md` that has YAML frontmatter:

```markdown
---
name: my-skill
description: >
  What the skill does and when to trigger it. Be specific — Copilot uses this
  text to decide when to auto-invoke the skill. Include trigger phrases.
---

# Skill Title

Step-by-step instructions, workflow, and edge cases go here.
```

Add any supporting files (scripts, reference data) in subfolders like `scripts/` or `references/`, and document them inside `SKILL.md`. See `transcript-proofread/` for a working example.

## Contributing to Team Skills

If you build a skill that others would find useful, add it to the [studio-copilot-skills](TODO) repo so the whole team can use it.
