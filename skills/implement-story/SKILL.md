---
name: implement-story
description: >
  Implement one user story from a stories.json file end-to-end. Use when the user names a story ID
  or asks to implement the next story as a standalone task: read the PRD and prior progress, make
  focused code changes, verify the acceptance criteria and project quality checks, update tracking,
  and propose a commit message without committing unless explicitly instructed.
---

# Implement Story

Implement exactly one story from the project's task-tracking files. This workflow is standalone;
it does not assume an automatic loop or a particular branching strategy.

## Required Inputs

- The exact story ID
- A `tasks/` directory containing one PRD and `stories.json`

Use `tasks/progress.txt` when it exists. If it does not exist, create it when recording the first
completed story and start it with an empty `## Codebase Patterns` section. If the story ID, PRD, or
stories file cannot be found unambiguously, stop and ask for the missing input.

## Quality Contract

- Satisfy every acceptance criterion with observable evidence.
- Run the project-required typecheck, lint, test, build, or generated-file checks that apply.
- Keep changes focused on the requested story and follow existing code patterns.
- Preserve unrelated user changes and never stage or overwrite them.
- Do not mark a story passing or propose a commit for broken or unverified code.

## 1. Build Context

1. Read the PRD in full.
2. Read `tasks/stories.json`, find the exact story, and confirm it is not already passing.
3. Read `tasks/progress.txt` when present, starting with `Codebase Patterns` and recent related
   entries.
4. Read applicable `AGENTS.md` files and inspect the working tree before editing. Note existing
   changes so they remain untouched.
5. Read the relevant source and tests before deciding how to implement the story.

## 2. Implement The Story

Implement only what the story requires. Do not add speculative features or unrelated refactors.
Add or update tests when the behavior is testable.

If implementation exposes an ambiguity or conflict in the requirements, stop and surface it. Do
not silently reinterpret the PRD or rewrite acceptance criteria to match the code.

## 3. Verify Definition Of Done

Check every acceptance criterion individually and record the evidence that satisfies it. Then run
all relevant project quality commands. Fix failures caused by the story and rerun checks until they
pass.

If an unrelated pre-existing failure prevents full verification, report it clearly and do not mark
the story passing without explicit user direction.

## 4. Preserve Reusable Learnings

Update the nearest applicable `AGENTS.md` only when the work revealed durable guidance such as:

- A non-obvious module convention
- Files that must stay synchronized
- A reusable testing approach
- A configuration or environment requirement

Do not add story-specific notes, temporary debugging details, or information already captured in
the progress log.

## 5. Update Tracking

Only after implementation and verification succeed:

1. Set the story's `passes` field to `true` and add a one-line `notes` summary in
   `tasks/stories.json`.
2. Ensure `tasks/progress.txt` exists with a top-level `## Codebase Patterns` section.
3. Append—never replace—an entry:

```text
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- Verification commands and results
- Acceptance-criteria evidence
- **Learnings for future iterations:**
  - Reusable patterns or gotchas, or `None`
---
```

Add an item to `Codebase Patterns` only when it is reusable across future stories.

## 6. Hand Off

Review the final diff and ensure it contains only implementation and tracking changes for this
story. Propose a conventional commit message with a concise imperative subject of at most 72
characters and a body explaining the behavior change when useful.

Do not add a story ID, fixed prefix, or custom trailer solely for this workflow. Follow an existing
repository convention or an explicit user request when one applies. Do not create a commit unless
the user explicitly instructed you to.

Summarize the change, acceptance evidence, checks run, and any residual risk.
