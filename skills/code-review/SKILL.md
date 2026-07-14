---
name: code-review
description: >
  Review a sprint or other explicit Git change scope without modifying source code. Use at mandatory
  story-loop sprint boundaries, for a mid-sprint product-drift check, or when the user asks to
  review a branch, commit, range, uncommitted work, or completed stories against the PRD. Report
  prioritized actionable code findings and a separate product-alignment assessment, then stop for
  human review.
---

# Code Review

Perform a read-only review in two distinct passes: implementation quality and product alignment.
Report evidence and stop. Do not fix findings during this skill.

## Inputs

For a sprint review, require:

- The sprint number
- A Git repository with a clean working tree
- A `tasks/` directory containing one PRD, `stories.json`, and `progress.txt`

For an ad hoc review, accept an explicit base branch, commit, range, uncommitted-change scope, file
scope, or custom review criteria. If the requested scope cannot be determined reliably, stop and
ask rather than reviewing an arbitrary diff.

## 1. Establish An Explicit Diff Scope

1. Read the PRD, `tasks/stories.json`, and `tasks/progress.txt` when reviewing a sprint.
2. Collect every story assigned to the requested sprint and its acceptance criteria. Require all
   sprint stories to be marked `passes: true` at a boundary review. A manually requested
   mid-sprint review may be partial, but label it as such.
3. When `stories.json` declares `branchName`, confirm the current branch matches it. Report a
   mismatch and stop; do not create or switch branches.
4. For a story-loop boundary, use the one-story-per-commit invariant to identify the candidate
   sprint range: inspect the most recent first-parent commit for each completed story in the sprint,
   use the parent of the earliest candidate as `base`, and use the current `HEAD` as `head`.
5. Verify that commit contents, the combined diff, story order, and progress entries agree. Do not
   infer story ownership from commit-message prefixes or trailers.
6. If the sprint-only range is uncertain, fall back to the current branch diff against the
   repository's unambiguous default target branch and label the review as cumulative. Find the merge
   base and inspect that exact diff. If neither scope is reliable, stop and ask for an explicit base
   or range.
7. For an ad hoc review, honor the user's exact branch, commit, range, uncommitted, file, or custom
   scope.

Always state the exact Git commands or revisions used to establish the diff. Read the combined diff
and enough surrounding execution paths to understand the behavior; do not rely only on file lists
in `progress.txt`.

## 2. Implementation Review Pass

Review the scoped diff like a senior engineer. Report only discrete, actionable issues introduced
by the reviewed changes.

Prioritize:

1. Incorrect behavior, regressions, and unmet acceptance criteria
2. Missing edge cases and data-integrity, concurrency, error-handling, or compatibility risks
3. Missing, misleading, or insufficient tests
4. Maintainability problems with a concrete failure mode

Avoid style-only comments, speculative refactors, praise, and issues unrelated to the reviewed
change. Check applicable `AGENTS.md` guidance and reusable learnings in `progress.txt`.

Assign each finding one priority:

- `P0`: release-blocking or destructive
- `P1`: serious correctness or regression risk
- `P2`: real issue that should be fixed before continuing when practical
- `P3`: minor, non-blocking improvement

Give every finding a concise title, evidence, impact, and the narrowest useful file/line location.
Use inline code comments when the current Codex surface supports them. If no actionable findings
exist, say so explicitly.

## 3. Product Alignment Pass

Treat product alignment as a mandatory, separate assessment so requirement drift is not diluted
into ordinary code-review findings.

- Compare implemented behavior with the PRD goal, user value, scope boundaries, constraints, and
  cross-story design—not only literal acceptance criteria.
- Look for requirement drift, cross-story contradictions, invalidated assumptions, accidental
  scope expansion, and technically correct work converging on the wrong product shape.
- Consider what the completed work reveals about unfinished stories.
- Assign drift risk: `None`, `Low`, `Medium`, or `High`.
- For `Medium` or `High` risk, recommend pausing before the next sprint.
- List proposed PRD or unfinished-story amendments separately. Treat them as proposals for the
  human to accept, reject, or revise; do not edit planning artifacts during review.

If the human accepts a requirement change, they may invoke the PRD workflow explicitly to revise
the PRD and unfinished stories before resuming. The review does not invoke that workflow itself.

## 4. Output And Stop

Return, in this order:

1. Findings, ordered by priority
2. Product alignment and drift risk
3. Acceptance-criteria verification for every reviewed sprint story
4. Review scope (`base`, `head`, stories, clean-tree status, and whether the diff is sprint-only or
   cumulative)
5. Open questions or proposed PRD/story amendments
6. One recommendation: `continue`, `fix`, or `replan`
7. The explicit next `$story-loop <story-id>` command only when `continue` is appropriate and an
   unfinished story remains; otherwise state what the human should resolve first

Use `fix` when concrete implementation findings should be addressed before the next sprint. Use
`replan` for material drift or accepted requirement changes. The recommendation is advisory; only
the human resumes the loop.

Do not modify code, tracking files, the PRD, or Git history. Do not emit a completion promise. Stop
after the review so the human can inspect findings and the reviewed diff.
