# ai-dev-toolkit

Personal Claude Code and OpenAI Codex configuration and skills. 

The root `CLAUDE.md` (and the symbolic link `AGENTS.md`) contains global coding preferences and tooling rules that apply across all projects.

## Skills

| Skill | Description |
|-------|-------------|
| `prd` | Create Product Requirements Documents (comprehensive or focused) and decompose them into a `stories.json` file of implementation-ready user stories. |
| `implement-story` | Implement a single user story end-to-end: reads requirements from `tasks/stories.json`, writes code, runs quality checks, and proposes a commit. |
| `doc-coauthoring` | Structured three-stage workflow for co-authoring docs (context gathering → refinement → reader testing). Copied as-is from [Anthropic's skills repo](https://github.com/anthropics/skills). |
