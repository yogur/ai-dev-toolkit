---
name: story-loop
description: >
  Run exactly one story-sized implementation pass, commit it, and emit the structured completion
  promise consumed by the story-workflow Stop hook. Use only when the user explicitly invokes
  `$story-loop` with a story ID to start or resume automatic story-by-story work within one sprint.
---

# Story Loop

Implement exactly one story by following the `implement-story` workflow, then commit and signal the
hook. Invocation of this skill explicitly authorizes one focused commit, but not branch creation or
branch switching.

## Required Input

- The exact story ID
- `tasks/stories.json` with `branchName`, sprint assignments, and priorities
- The PRD required by `implement-story`

If any input is missing, stop without emitting a promise.

## 1. Inspect The Branch And Working Tree

Before editing:

1. Require a Git repository and read `branchName` from `tasks/stories.json`.
2. Confirm the current branch is exactly `branchName`. If it is not, stop and report the expected
   and current branches. Do not create, switch, rename, or delete a branch.
3. Inspect staged, unstaged, and untracked files. Require a clean working tree except for new or
   modified planning and tracking artifacts under `tasks/` that belong to this PRD. Stop if any
   unrelated path is dirty.

`branchName` is an assertion about where the user chose to work, not permission to manage branches.

## 2. Implement And Commit One Story

Load and follow the `implement-story` skill in full for the provided story ID. Work on no other
story, even if nearby work is easy.

After all acceptance criteria and project quality checks pass:

1. Update `tasks/stories.json`, `tasks/progress.txt`, and any justified `AGENTS.md` guidance.
2. Verify the working tree contains only this story's implementation and tracking changes, plus
   permitted PRD planning artifacts on the first iteration.
3. Create exactly one focused commit using the commit-message guidance from `implement-story`.
   Do not add a story ID, fixed prefix, or custom trailer solely for the loop.

The story-to-commit mapping lives in `stories.json`, `progress.txt`, and the one-story-per-commit
ordering rather than public Git message metadata.

## 3. Signal Completion

After the commit succeeds, verify that:

- The requested story is marked `passes: true`.
- The focused commit contains the story's implementation and tracking updates.
- The working tree is clean.

Then end the final response with this exact line and nothing after it, preserving the story ID:

```text
<promise>{"protocol":"story-loop/v1","type":"STORY_COMPLETE","storyId":"<story-id>"}</promise>
```

## Guardrails

- Do not emit the promise if implementation, verification, tracking, commit, or cleanup is incomplete.
- Do not amend, squash, rebase, merge, push, open a pull request, or manage branches during a story
  iteration.
- Do not stage or commit unrelated user changes.
- If blocked or human input is needed, stop normally without the promise.
