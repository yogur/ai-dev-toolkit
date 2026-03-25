---
name: prd
description: >
  Create and manage Product Requirements Documents (PRDs) and decompose them into user stories.
  Use this skill when the user wants to: write a PRD for a new project, draft requirements for a
  new release or feature, break down a PRD into user stories, or convert requirements into a
  stories.json file. Trigger on mentions of PRD, product requirements, user stories, acceptance
  criteria, feature specs, release planning, or story decomposition — even if the user doesn't
  use the exact term "PRD" (e.g., "spec out this feature", "write up requirements", "plan the
  next release", "break this into stories").
---

# PRD Skill

This skill produces two kinds of artifacts:

1. **PRDs** — markdown documents that define what to build and why.
2. **User story files** — JSON files that decompose a PRD into implementation-ready work items.

There are two PRD modes and one story mode. Identify which the user needs from context, or ask if ambiguous.

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
data flow, and integration points. Include phase boundaries if the system
ships incrementally (e.g., MVP vs Phase 2).

## 4. Feature Set / Functional Requirements
Detailed specification of each feature. For each:
- Purpose and behavior
- Configuration (with YAML/JSON examples where relevant)
- Interfaces (internal APIs, schemas, data models)
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
- Configuration examples (YAML, JSON, or code snippets)
- Data models and schemas (SQL CREATE TABLE, Python dataclasses, or similar)
- Interface contracts (function signatures, API shapes)
- Decision matrices (tables showing behavior under different conditions)
- Concrete CLI invocations or usage examples

**Tables:** Use tables for decision matrices, CLI parameter references, comparison of options, and any structured data that would be harder to parse in prose.

**Code blocks:** Use code blocks for configuration files, schemas, interfaces, project structure trees, CLI examples, and architecture diagrams.

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
abstractions, data models, or structural changes. Show before/after if
refactoring existing code.

## 3. Functional Requirements
Detailed specification of each new feature or change. Same depth as
comprehensive mode but scoped to what's new or changing.

## 4. Refactor Details
If existing code needs restructuring. Show before/after code patterns,
explain what changes and what doesn't.

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

**New vs. changed:** Clearly distinguish between entirely new functionality and changes to existing behavior. When modifying existing behavior, show before/after where possible (code patterns, CLI invocations, data models).

**Technical stack:** Only include a technical stack section if this release introduces new dependencies or architectural components. If the stack is unchanged, omit it. If a few new tools are added, mention them inline within the relevant feature section rather than creating a dedicated section.

**Backward compatibility:** Call out breaking changes explicitly. Show how existing usage continues to work (or doesn't).

**Cross-references:** Reference the existing PRD or codebase for context the reader needs. Don't repeat what's already documented — point to it.

**User stories:** Focused PRDs may include user stories inline. When included, they follow the same format and guidelines as the Story Decomposition mode's output. This is appropriate when the release scope is clear and the stories naturally emerge from the requirements. If the scope is large or exploratory, omit inline stories and let the user decompose separately.

---

## Mode 3: Story Decomposition

Convert a PRD into an implementation-ready `stories.json` file. This mode can be triggered in two ways:

1. **After writing a focused PRD** — automatically offer to decompose the PRD into stories once it is complete. The user may accept or decline.
2. **Standalone** — the user provides an existing PRD (as a file path or pasted content) and asks for story decomposition directly. This is a first-class entry point, not just a follow-up to PRD writing.

### Process

1. Read the PRD thoroughly.
2. If the PRD already contains user stories (common in focused PRDs), extract and reformat them to match the JSON schema. Refine acceptance criteria for verifiability, adjust sizing, and fix dependency ordering.
3. If the PRD does not contain user stories, analyze the requirements and formulate stories from scratch. Think through the implementation order, identify natural boundaries, and create stories that are each completable in one iteration.
4. Write the output to the specified path (default: `stories.json` next to the PRD).

### Output Format

```json
{
  "project": "<project name and version/release>",
  "branchName": "<suggested git branch name>",
  "description": "<one-line description of what this set of stories delivers>",
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
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Story Sizing

Each story must be completable in one iteration (one context window). This is the most important rule.

**Right-sized examples:**
- Add a database column and migration
- Implement an abstract base class with interface methods
- Add a CLI flag with validation
- Write a prompt template for a single stage
- Add a utility function with tests

**Too big (split these):**
- "Build the entire dashboard" — split into: schema, queries, UI components, filters
- "Add authentication" — split into: schema, middleware, login UI, session handling
- "Implement the full pipeline" — split into: one story per stage or component

**Rule of thumb:** If you cannot describe the change in 2-3 sentences, it is too big.

### Story Ordering

Stories execute in priority order. Earlier stories must not depend on later ones.

**Correct ordering pattern:**
1. Data models, schemas, abstractions (foundation)
2. Core logic, engines, utilities (building blocks)
3. Integration, orchestration (connecting pieces)
4. CLI, API surface (user-facing)
5. End-to-end tests (verification)

### Acceptance Criteria

Every criterion must be objectively verifiable — something you can CHECK, not something vague.

**Good (verifiable):**
- "`src/app/models.py` exports a `User` dataclass with fields: `id`, `name`, `email`"
- "`get_engine('claude-code')` returns a `ClaudeCodeEngine` instance"
- "Running `app --help` displays the `--verbose` flag with description"
- "Tests pass"

**Bad (vague):**
- "Works correctly"
- "Handles edge cases"
- "Good performance"
- "Clean code"

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

**Tables over prose for structured data.** CLI parameters, feature matrices, decision logic, and comparisons are always clearer as tables.

**ASCII diagrams over descriptions.** A 10-line ASCII architecture diagram communicates more than 3 paragraphs of prose. Use them for system architecture, data flow, component relationships, and phase boundaries.

**Scope is a feature.** Explicitly stating what's out of scope is as valuable as defining what's in scope. It prevents scope creep and sets expectations.

**Open questions are honest.** If something is genuinely unresolved, say so. Include the tradeoff and a recommendation. Do not hide uncertainty — surface it so it can be discussed.

**Match the project's voice.** If the user has existing PRDs or documentation, match their style, terminology, and level of detail. Read existing artifacts before writing.

---

## File Naming and Location

- PRDs: Save as markdown (`.md`) in the location the user specifies. If no location is specified, ask. Common patterns: `tasks/`, `docs/`, or project root.
- Stories: Save as `stories.json` in the same directory as the PRD, unless the user specifies otherwise.
