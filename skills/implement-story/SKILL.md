---
name: implement-story
description: >
  Implements a single user story from a stories.json file, following project conventions and
  quality checks. Use this skill when the user provides a story ID (e.g. "US-003", "implement
  story 5", "work on US-012") and wants it implemented end-to-end: read requirements, write
  code, run tests, update tracking files, and propose a commit message. Trigger on any request
  that combines a story ID with intent to implement, even if the user phrases it casually (e.g.
  "do US-007", "let's tackle story 3", "implement the next story", "knock out US-002").
---

# implement-story

Implement a single user story from the project's task tracking files.

## Required inputs

- **Story ID**: provided by the user (e.g. `US-003`). If not provided, ask for it.
- **`tasks/` directory** (relative to the working directory): must contain:
  - A PRD file (`.md`) describing the project
  - `stories.json` with the user stories list
  - `progress.txt` with the running progress log

If any of these files are missing or cannot be found, ask the user to provide their location before proceeding.

## Quality requirements

- ALL quality checks must pass before proposing a commit (typecheck, lint, test — use whatever the project requires)
- Do NOT propose a commit for broken code
- Keep changes focused and minimal
- Follow existing code patterns
- Work on ONE story per iteration

## Workflow

### 1. Read the PRD

Read the PRD file in `tasks/` in full. It is important to understand context, architecture decisions, and constraints before writing any code.

### 2. Read the progress log

Read `tasks/progress.txt`. Check the **Codebase Patterns** section first — prior iterations have left hard-won knowledge there. Don't repeat their mistakes.

### 3. Implement the story

Find the target story in `tasks/stories.json` by its ID. Read its `description` and `acceptanceCriteria` carefully — these are your definition of done.

Read the relevant source files before writing any changes. Understand existing patterns; don't invent conventions.

Make the changes needed to satisfy all acceptance criteria. Keep changes focused: implement what the story requires, nothing more. Don't refactor surrounding code, add extra features, or improve things that weren't asked for.

### 4. Run quality checks

Run whatever checks the project requires (typecheck, lint, test). Fix any failures before continuing.

### 5. Update CLAUDE.md

Before proposing a commit, check whether your changes contain learnings worth preserving in the `CLAUDE.md` file:

1. **Identify directories with edited files** — look at which directories you modified.
2. **Check the root `CLAUDE.md`** — this is where project-wide conventions live by default.
3. **Add valuable learnings** — if you discovered something future developers/agents should know:
   - API patterns or conventions specific to that module
   - Gotchas or non-obvious requirements
   - Dependencies between files
   - Testing approaches for that area
   - Configuration or environment requirements

Examples of good additions:
- "When modifying X, also update Y to keep them in sync"
- "This module uses pattern Z for all API calls"
- "Tests require the dev server running on PORT 3000"
- "Field names must match the template exactly"

Do **not** add:
- Story-specific implementation details
- Temporary debugging notes
- Information already in `tasks/progress.txt`

Only update `CLAUDE.md` if you have genuinely reusable knowledge that would help future work in that directory.

### 6. Propose a commit message

If all quality checks pass, write a commit message and present it to the user. **Do not commit unless explicitly instructed by the user.**

The commit message should:
- Be detailed enough to understand what changed and why
- Start with a concise subject line (imperative mood, ≤72 chars)
- Include a body if the change is non-trivial
- **Not** include implementation deliberations or decision trails (no "considered X but decided Y", no "initially tried Z")

### 7. Update stories.json

Mark the completed story as passing in `tasks/stories.json`:
```json
{
  "passes": true,
  "notes": "<one-line summary of what was implemented>"
}
```

### 8. Append to progress.txt

Append (never replace) a new entry to `tasks/progress.txt`:

```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "this codebase uses X for Y")
  - Gotchas encountered (e.g., "don't forget to update Z when changing W")
  - Useful context (e.g., "the evaluation panel is in component X")
---
```

The learnings section is critical — it helps future iterations avoid repeating mistakes and understand the codebase better.

If you discovered a **reusable, general pattern** (not story-specific), also add it to the `## Codebase Patterns` section at the **top** of `tasks/progress.txt`. Create that section if it doesn't exist:

```
## Codebase Patterns
- Example: Use `sql<number>` template for aggregations
- Example: Always use `IF NOT EXISTS` for migrations
- Example: Export types from actions.ts for UI components
```

Only add patterns that are general and reusable, not story-specific details.
