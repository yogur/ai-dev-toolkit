---
name: sprint-checkpoint
description: >
  Review a completed sprint in the interactive story loop and write a structured checkpoint report
  for operator review. Use when Codex is asked to run `$sprint-checkpoint` for a specific sprint,
  review a just-completed sprint against the PRD and `tasks/stories.json`, assess requirement
  alignment or code quality before the next sprint, or produce `tasks/checkpoint-sprint-N.md`.
---

# Sprint Checkpoint

## Overview

Use this skill at sprint boundaries to review what was built, write one checkpoint report, and stop
for operator decision. Treat the report contract in this skill as the source of truth; examples in
other documents are informative, not authoritative.

## Required Input

- Sprint number (for example `2`)
- A `tasks/` directory containing:
  - One PRD markdown file
  - `tasks/stories.json`
  - `tasks/progress.txt`

If the sprint number or required files are missing, stop and say what is missing instead of
guessing.

## Workflow

### 1. Build Sprint Context

1. Read the PRD in `tasks/`.
2. Read `tasks/stories.json` and collect the stories assigned to the requested sprint.
3. Read `tasks/progress.txt` and find the entries for those story IDs.
4. Read the source files referenced by those progress entries.

Use this priority order when locating source files from `progress.txt`:

- The `Files changed:` line
- Explicit file paths mentioned in implementation bullets
- Nearby files only when needed to understand behavior or confirm an issue

If the progress log does not identify enough code to review confidently, say so in the report
instead of inventing certainty.

### 2. Run Sequential Review Passes

Perform the checkpoint as two separate passes followed by a synthesis step. Keep the sections
distinct in both reasoning and report output.

**Pass 1 - Product Architect**

- Adopt this role explicitly: you are a product architect reviewing the sprint checkpoint.
- Evaluate whether the sprint still appears to be solving the right problem in the right way, given
  what implementation revealed.
- Compare the implemented behavior to the PRD goals, story descriptions, and intended user value,
  not just to the literal wording of acceptance criteria.
- Flag requirement drift, cross-story inconsistencies, cases where the implementation is
  technically acceptable but points toward the wrong solution shape, and places where the next
  stories or the PRD likely need a quick replan or pivot.
- Call out simplifications, reframes, or reprioritizations that now seem advisable.
- Assign a drift risk of `None`, `Low`, `Medium`, or `High`.
- Treat this pass as strategic and product-facing. Do not turn it into a line-by-line code review.

**Pass 2 - Code Reviewer**

- Adopt this role explicitly: you are a senior software engineer performing a code review.
- Verify acceptance criteria story by story at the implementation level.
- Check consistency with existing codebase patterns and `AGENTS.md`/`progress.txt` learnings.
- Assess structural quality, maintainability, readability, abstraction choices, and avoidable
  complexity.
- Recommend any best practices that appear missing for the current tech stack or code area when
  they would materially improve maintainability, correctness, or clarity.
- Keep those recommendations advisory rather than mandatory unless the omission is causing a real
  issue today.
- Record issues with severities `minor`, `moderate`, or `major`.
- Keep this pass implementation-focused. Do not use it to reconsider the product direction; that
  belongs in the Product Architect pass.

**Synthesis**

- Choose one verdict: `continue`, `fix`, or `pause`.
- Base `continue` on no blocking issues and no more than minor follow-ups.
- Base `fix` on localized implementation issues or code-review findings that should be addressed
  before the next sprint.
- Base `pause` on product-architecture drift, a likely need to replan the next work, or broader
  structural concerns that need operator direction.
- Treat recommendations as input to the operator's decision, not automatic follow-up work.

### 3. Write The Report

Write the report to `tasks/checkpoint-sprint-N.md` using this structure:

```md
# Sprint N Checkpoint

**Date:** <timestamp>
**Stories:** <comma-separated story ids>
**Verdict:** continue | fix | pause

---

## 1. Product Architect Pass

### Problem / Solution Fit
- <Does the sprint still look like the right path for the underlying problem?>

### Drift / Replan Signals
- <Requirement drift, new constraints, or signs that upcoming stories should be reframed>

### Drift Risk
None | Low | Medium | High - with explanation.

### Recommendations
- <Advisory product / planning recommendations for the operator>

---

## 2. Code Reviewer Pass

### Acceptance Criteria Verification
- `<story-id>` - <summary of whether the story's criteria are satisfied>

### Issues
| # | Story | Severity | Description |
|---|-------|----------|-------------|
| 1 | US-002 | minor | ... |

### Pattern Consistency
- ...

### Structural Quality
- ...

### Best-Practice Recommendations
- <Advisory recommendations for this tech stack or code area>

---

## 3. Verdict

### Recommendation
- **continue** - no blocking issues; only none or minor concerns
- **fix** - localized issues should be corrected before the next sprint
- **pause** - requirement drift or structural concerns need operator direction

### Why
- <Short synthesis tying the verdict to the two passes above>

### Operator Considerations
- <Optional notes about what to review before accepting or rejecting recommendations>
```

Additional report rules:

- Keep the `Product Architect Pass`, `Code Reviewer Pass`, and `Verdict` section headings exactly
  as shown.
- Under `Acceptance Criteria Verification`, cover every story in the sprint explicitly.
- Use `None noted.` when a subsection has no issues instead of leaving it blank.
- Keep the Product Architect and Code Reviewer sections independent; do not merge them into a
  single blended review narrative.
- Keep findings concrete and tied to observed code or missing behavior.
- Keep Product Architect recommendations focused on replan, pivot, or solution-shape questions.
- Keep Code Reviewer recommendations focused on implementation quality and missing best practices.
- Do not include remediation patches or code edits in the report itself.

### 4. Surface The Result And Stop

After writing the markdown report:

1. Summarize the checkpoint in a short operator-facing response.
2. Include the verdict and the highest-signal blocking or risky findings.
3. Stop. Do not resume the story loop automatically and do not emit a completion promise.
