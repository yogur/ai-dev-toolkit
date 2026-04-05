---
name: prd
description: >
  Create and manage Product Requirements Documents (PRDs) and decompose them into sprint-aware
  user stories. Use this skill when the user wants to: write a PRD for a new project, draft
  requirements for a new release or feature, break down a PRD into user stories, or convert
  requirements into a stories.json file. Trigger on mentions of PRD, product requirements, user
  stories, acceptance criteria, feature specs, release planning, or story decomposition — even if
  the user doesn't use the exact term "PRD" (e.g., "spec out this feature", "write up
  requirements", "plan the next release", "break this into stories").
---

# PRD Skill

This skill produces two kinds of artifacts:

1. **PRDs** — markdown documents that define what to build and why.
2. **User story files** — JSON files that decompose a PRD into outcome-focused, implementation-sequenced work items.

There are two PRD modes and one story mode. Identify which the user needs from context, or ask if ambiguous.

## Core Boundary

PRDs and stories define **what must be true**, **why it matters**, and **what constraints apply**. They do **not** prescribe the exact internal implementation unless the user explicitly asks for that level of detail or the codebase has a mandatory integration point that must be named.

Stay focused on:

- Product behavior, user value, scope boundaries, and success criteria
- High-level technical design, architecture impact, data flow, and external interfaces
- Constraints the implementor must respect

Avoid over-specifying:

- Exact file names to create or modify
- Class names, function names, or method signatures
- Step-by-step coding plans
- Internal refactors described at the level of source edits rather than design intent

The implementor should explore the current codebase, understand existing patterns, and choose the best technical implementation. The PRD and stories should preserve that freedom.

## Choosing the Right Mode

| Signal | Mode |
|--------|------|
| New project, greenfield, no existing codebase | **Comprehensive PRD** |
| New release, new feature, addition to existing project | **Focused PRD** |
| "Break this into stories", "decompose", existing PRD referenced | **Story Decomposition** |

**After completing a focused PRD**, always offer to decompose it into a `stories.json` file. A simple "Want me to decompose this into user stories?" is enough. Do not auto-generate stories without asking — the user may want to review the PRD first.

---

## Mode 1: Comprehensive PRD (New Project)

For greenfield projects or major rewrites that are effectively new projects. These PRDs are thorough and self-contained — a reader should understand the entire system from this document alone.

### Interview Process

Before writing, gather enough context to produce a substantive PRD. Ask only critical questions where the initial prompt is ambiguous or incomplete. Focus on:

- **Problem/Goal:** What problem does this solve? Who has this problem?
- **Core Functionality:** What are the key actions and capabilities?
- **Scope/Boundaries:** What should it NOT do? What is deferred?
- **Technical Constraints:** Language, framework, deployment, or integration requirements?
- **Success Criteria:** How do we know it's done and working?

Do not barrage the user with 20 questions. Batch related questions together. If the user has already provided substantial context (e.g., a detailed description, prior conversation, reference materials), acknowledge what you already know and only ask about gaps. The goal is to fill blind spots, not to rehash what the user already told you.

When the user is exploring an idea, help them think through it — suggest possibilities, surface tradeoffs, challenge vague goals. When they have a clear vision, get out of the way and draft.

### Document Structure

A comprehensive PRD follows this general structure. Not every section is required for every project — use judgment about what's relevant. The ordering below is a sensible default; adjust if the project calls for it.

```
# <Project Name> — Product Requirements Document

**Author:** <name>
**Date:** <date>
**Status:** Draft

---

## 1. Problem Statement / Overview
Why this project exists. What problem it solves. Brief solution description.

## 2. Target Users
Primary, secondary, and tertiary user segments. Who benefits and how.

## 3. Architecture Overview
High-level system design. ASCII diagrams showing component relationships,
data flow, trust boundaries, and integration points. Include phase
boundaries if the system ships incrementally (e.g., MVP vs Phase 2).

## 4. Feature Set / Functional Requirements
Detailed specification of each feature. For each:
- Purpose and behavior
- User-visible flows and system outcomes
- Configuration or external/API contracts when relevant
- Data models or schemas when they are part of the product contract
- Edge cases and limitations
- Phase/scope notes (MVP vs future)

## 5. Technical Stack
Language, frameworks, package manager, testing tools, project layout.
Include a project structure tree showing directory organization.

## 6. Configuration Reference
Complete configuration file example with all fields, defaults, and comments.

## 7. Technical Constraints & Assumptions
Runtime requirements, latency budgets, security model, deployment assumptions.

## 8. Success Metrics / Criteria
Measurable targets that define whether the project achieved its goals.

## 9. Open Questions
Unresolved decisions with context about each. These are genuine unknowns,
not todos — each should explain the tradeoff being considered.
```

### Content Guidelines

**Architecture diagrams:** Use ASCII art for system architecture, data flow, and component relationships. These should show how components connect, where trust boundaries exist, and how data moves through the system. Keep them readable — if a diagram needs more than ~30 lines, split it into multiple diagrams.

**Feature specifications:** Each feature should be concrete enough that an engineer can implement it without asking clarifying questions about behavior. Include:
- Configuration examples when configuration is part of the product surface
- Data models and schemas when they are part of the product contract
- External/API contracts and payload shapes when relevant
- Decision matrices (tables showing behavior under different conditions)
- Concrete usage examples

Prefer module boundaries, responsibilities, and integration points over file-by-file or function-by-function prescriptions. Only name exact files, classes, or functions when the codebase already exposes a required extension point and ambiguity would cause the implementor to wire it incorrectly.

**Tables:** Use tables for decision matrices, CLI parameter references, comparison of options, and any structured data that would be harder to parse in prose.

**Code blocks:** Use code blocks for configuration files, schemas, API payloads, project structure trees, CLI examples, and architecture diagrams. Avoid using code blocks to sketch internal implementation unless the user explicitly wants design-level pseudocode.

**Scope boundaries:** Explicitly state what is out of scope. Group deferred work into phases (Phase 2, Phase 3, Future) when multiple items are deferred.

**Design principles:** If the project has guiding principles that inform decisions throughout the document, state them early. Keep them short (one line each) with a bold keyword and a dash. These are reference anchors, not essays.

**Open questions:** These should be genuine unresolved decisions, not action items. Each should explain the tradeoff: "Question X: Context about why this is hard to decide. Option A does Y. Option B does Z. Recommendation: start with A, revisit if..."

**What NOT to include:** Do not include user stories in comprehensive PRDs. Stories are a separate artifact produced by the decomposition mode. Do not include implementation timelines or effort estimates — the PRD defines what to build, not when.

---

## Mode 2: Focused PRD (Release / Feature)

For new releases or features on existing projects. These are scoped additions, not full system descriptions. The reader already knows the system; the PRD explains what's changing.

### Interview Process

Same principles as comprehensive mode, but lighter. Focus questions on:

- **Release Goal:** What does this release accomplish?
- **Scope:** What's in, what's out?
- **Integration:** How does this interact with existing architecture?
- **Breaking Changes:** Does this change existing behavior?

**Context sources are flexible.** The user may provide full codebase access, or they may provide just existing PRDs, a README, and config files — that is often sufficient. Do not insist on reading source code. Work with what you are given. If the user has granted codebase access, read relevant files (README, existing PRDs, main modules, config files) to build context before asking questions. If they have provided documents instead, use those. Do not ask what the project does if you can read it from the provided materials.

### Document Structure

Focused PRDs are shorter and assume familiarity with the system. They typically contain user stories inline (unlike comprehensive PRDs).

```
# <Project Name> <Release/Feature> — Product Requirements Document

**Author:** <name>
**Date:** <date>
**Status:** Draft
**Builds on:** <previous version or baseline> (<brief description of current state>)

---

## 1. Overview

### 1.1 Release Goal
One paragraph: what this release achieves and why it matters.

### 1.2 Scope
**In scope:** Bulleted list of what's included.
**Out of scope:** Bulleted list of what's deferred, with brief rationale.

### 1.3 Design Principles
Carry forward existing principles. Add new ones relevant to this release,
marked with *(New)*.

## 2. Architecture / Data Model
Only if this release introduces new architectural concepts. Describe the new
abstractions, data models, integration points, or structural changes. Show
conceptual before/after when changing existing behavior.

## 3. Functional Requirements
Detailed specification of each new feature or change. Same depth as
comprehensive mode but scoped to what's new or changing.

## 4. Design / Refactor Impact
If existing code needs restructuring, explain the design intent, affected
areas, and what changes semantically versus what stays stable. Keep this at
the module, boundary, or workflow level rather than prescribing edits.

## 5. CLI / API Changes
New flags, parameters, or endpoints. Table format with type, default,
and description.

## 6. Open Questions
Same format as comprehensive mode.

## 7. User Stories
Inline user stories when the release scope is well-defined enough.
Each story follows the format described in the Story Decomposition section.
```

### Content Guidelines

**"Builds on" header:** Always reference the baseline the reader should know. Include a parenthetical describing the current state in a few words.

**New vs. changed:** Clearly distinguish between entirely new functionality and changes to existing behavior. When modifying existing behavior, show before/after in terms of user flows, API behavior, CLI behavior, or data contracts.

**Technical stack:** Only include a technical stack section if this release introduces new dependencies or architectural components. If the stack is unchanged, omit it. If a few new tools are added, mention them inline within the relevant feature section rather than creating a dedicated section.

**Backward compatibility:** Call out breaking changes explicitly. Show how existing usage continues to work (or doesn't).

**Cross-references:** Reference the existing PRD or codebase for context the reader needs. Don't repeat what's already documented — point to it.

**User stories:** Focused PRDs may include user stories inline. When included, they follow the same format and guidelines as the Story Decomposition mode's output. Keep them outcome-oriented: what capability gets added, what constraint matters, and how completion is verified. Do not turn them into coding checklists. If the scope is large or exploratory, omit inline stories and let the user decompose separately.

---

## Mode 3: Story Decomposition

Convert a PRD into a `stories.json` file of outcome-focused implementation slices. This mode can be triggered in two ways:

1. **After writing a focused PRD** — automatically offer to decompose the PRD into stories once it is complete. The user may accept or decline.
2. **Standalone** — the user provides an existing PRD (as a file path or pasted content) and asks for story decomposition directly. This is a first-class entry point, not just a follow-up to PRD writing.

### Process

1. Read the PRD thoroughly.
2. If the PRD already contains user stories (common in focused PRDs), extract and reformat them to match the JSON schema. Refine acceptance criteria for verifiability, adjust sizing, remove unnecessary implementation prescription, and fix dependency ordering.
3. If the PRD does not contain user stories, analyze the requirements and formulate stories from scratch. Think through the implementation order, identify natural boundaries, assign each story to a sprint, and create stories that are each completable in one iteration without dictating the exact source-level solution.
4. Write the output to the specified path (default: `stories.json` next to the PRD).

### Output Format

```json
{
  "project": "<project name and version/release>",
  "branchName": "<suggested git branch name>",
  "description": "<one-line description of what this set of stories delivers>",
  "sprintConfig": {
    "checkpointEnabled": true
  },
  "userStories": [
    {
      "id": "US-001",
      "title": "Short descriptive title",
      "description": "As a <role>, I want <capability> so that <benefit>",
      "acceptanceCriteria": [
        "Concrete, verifiable criterion 1",
        "Concrete, verifiable criterion 2",
        "Tests pass"
      ],
      "sprint": 1,
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

`sprintConfig` is optional. When the PRD or user context does not call for sprint checkpoints, it may be omitted entirely without making the story file invalid. Every generated story should still include the existing fields plus a positive integer `sprint`.

### Sprint Assignment

Assign sprints as part of decomposition rather than as a separate follow-up step unless the user explicitly asks for a two-step workflow.

- Sprint 1 should contain 2-3 foundational stories such as data contracts, core abstractions, or configuration changes.
- Later sprints should usually contain 3-5 stories grouped by dependency cluster and delivered capability.
- The final sprint should include any end-to-end integration, verification, or release-readiness stories.
- Adjust sprint sizes when the project shape warrants it. Infrastructure-heavy work may need smaller sprints; straightforward feature work may support larger ones.
- Keep sprint boundaries cohesive. Stories in the same sprint should make sense to review together at a checkpoint.
- If the project is too small to justify many sprints, prefer fewer sprints over artificial splitting.

### Story Sizing

Each story must be completable in one iteration (one context window). This is the most important rule.

Each story should describe a coherent outcome, not a coding recipe. The implementor should still need to inspect the codebase and decide how to realize the story cleanly.

**Right-sized examples:**
- Persist user notification preferences
- Add a configurable retry option to the CLI
- Support one additional prompt stage in the workflow
- Expose a new API field required by the UI
- Verify the end-to-end flow for a single integration path

**Too big (split these):**
- "Build the entire dashboard" — split into: data exposure, primary view, filtering, verification
- "Add authentication" — split into: sign-in flow, session behavior, protected access, verification
- "Implement the full pipeline" — split into: one story per meaningful stage or user-visible capability

**Rule of thumb:** If you cannot describe the change in 2-3 sentences, it is too big.

### Story Ordering

Stories execute in priority order. Earlier stories must not depend on later ones.

**Correct ordering pattern:**
1. Foundational contracts or data changes
2. Core behavior needed by later slices
3. Integration and orchestration
4. User-facing surfaces
5. End-to-end verification

Within that ordering, assign sprint numbers so the earliest foundational stories stay in Sprint 1, dependent work follows in later sprints, and the final sprint contains integration or verification slices. Sprint numbers must increase only when the dependency cluster changes or the review boundary is meaningful.

### Acceptance Criteria

Every criterion must be objectively verifiable — something you can CHECK, not something vague.

Acceptance criteria should describe observable behavior, contracts, and constraints. Avoid naming exact files, classes, or functions unless the codebase already has a mandatory integration point that must be used.

**Good (verifiable):**
- "A user can save notification preferences and see them persist after reload"
- "Running `app --help` displays the `--verbose` flag with description"
- "The API returns the new `retryPolicy` field when workflow settings are requested"
- "Invalid provider configuration is rejected with a descriptive error message"
- "Tests pass"

**Bad (vague):**
- "Works correctly"
- "Handles edge cases"
- "Good performance"
- "Clean code"

**Too implementation-specific (avoid by default):**
- "`src/app/models.py` exports a `User` dataclass with fields: `id`, `name`, `email`"
- "`get_engine('claude-code')` returns a `ClaudeCodeEngine` instance"
- "Create `foo.ts` with `buildFoo()` helper"

For stories with testable logic, include the exact string `"Tests pass"` as the final acceptance criterion. Do not rephrase it (e.g., "Tests verify X" or "Unit tests cover Y") — those are separate criteria. `"Tests pass"` is a universal gate that confirms all tests still pass after the story is implemented.

### Additional Rules

- **IDs:** Sequential `US-001`, `US-002`, etc.
- **Priority:** Based on dependency order, then document order. Priority 1 is highest.
- **All stories start with:** `"passes": false` and `"notes": ""`
- **No story depends on a later story.** If you find a dependency cycle, reorder.
- **E2E tests:** Add end-to-end integration test stories at the end, after all component stories. These verify that the pieces work together.

---

## General Writing Principles

These apply across all modes.

**Be concrete, not abstract.** Show configuration examples, CLI invocations, data schemas, and interface contracts. A PRD that says "the system should handle authentication" is useless. A PRD that shows the auth flow, the session schema, the config format, and the CLI flags is actionable.

**Be concrete about outcomes, not source edits.** Good PRDs make behavior and constraints unambiguous while leaving room for the implementor to discover the right files, abstractions, and control flow in the existing codebase.

**Tables over prose for structured data.** CLI parameters, feature matrices, decision logic, and comparisons are always clearer as tables.

**ASCII diagrams over descriptions.** A 10-line ASCII architecture diagram communicates more than 3 paragraphs of prose. Use them for system architecture, data flow, component relationships, and phase boundaries.

**Scope is a feature.** Explicitly stating what's out of scope is as valuable as defining what's in scope. It prevents scope creep and sets expectations.

**Open questions are honest.** If something is genuinely unresolved, say so. Include the tradeoff and a recommendation. Do not hide uncertainty — surface it so it can be discussed.

**Match the project's voice.** If the user has existing PRDs or documentation, match their style, terminology, and level of detail. Read existing artifacts before writing.

---

## File Naming and Location

- PRDs: Save as markdown (`.md`) in the location the user specifies. If no location is specified, ask. Common patterns: `tasks/`, `docs/`, or project root.
- Stories: Save as `stories.json` in the same directory as the PRD, unless the user specifies otherwise.
