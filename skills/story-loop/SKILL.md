---
name: story-loop
description: >
  Run one story-sized implementation pass using the implement-story workflow, then commit on
  success and end with the completion promise consumed by a repo-local Stop hook. Use this when
  the user provides a story ID and wants Codex to continue story-by-story in the same interactive
  session, typically in repositories that keep progress in tasks/stories.json.
---

# story-loop

Run exactly one story iteration in the interactive hook-driven story loop.

## Required input

- **Story ID**: provided by the user (for example `US-003`). If not provided, ask for it.

## Core behavior

This skill is a thin wrapper around `implement-story`. Follow the `implement-story` skill in full
for the provided story ID.

In addition to the `implement-story` workflow:

1. Treat invocation of `story-loop` as explicit user instruction to create a git commit once the
   story is complete and all required quality checks are passing.
2. Create exactly one focused commit for the completed story.
3. End your final response with this exact line and nothing after it:

```text
<promise>STORY_COMPLETE</promise>
```

## Guardrails

- Work on exactly one story per invocation.
- Do not emit the completion promise unless the story is complete according to `implement-story`,
  `tasks/stories.json` has been updated, `tasks/progress.txt` has been appended, and the commit has
  succeeded.
- If you are blocked, need user input, or cannot complete the commit safely, stop normally and do
  not emit the completion promise.
