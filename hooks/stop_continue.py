#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

STORIES_PATH = Path("tasks/stories.json")
AUTOMATIC_REVIEW_MODE = "automatic"
MANUAL_REVIEW_MODE = "manual"
PROMISE_PREFIX = "<promise>"
PROMISE_SUFFIX = "</promise>"
COMPLETION_TYPE = "STORY_COMPLETE"
PROTOCOL = "story-loop/v1"


@dataclass(frozen=True)
class StopPayload:
    cwd: Path
    last_assistant_message: str


@dataclass(frozen=True)
class StoryState:
    identifier: str | None
    passes: bool
    sprint: int | None
    priority: int | None
    order: int


@dataclass(frozen=True)
class CompletionEvent:
    story_id: str


@dataclass(frozen=True)
class ContinueDecision:
    prompt: str


@dataclass(frozen=True)
class StopDecision:
    reason: str


HookDecision = Union[ContinueDecision, StopDecision]


def load_payload() -> StopPayload:
    raw_payload = json.load(sys.stdin)
    cwd = Path(raw_payload["cwd"]).resolve()
    return StopPayload(
        cwd=cwd,
        last_assistant_message=str(raw_payload.get("last_assistant_message") or ""),
    )


def detect_repo_root(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    return Path(result.stdout.strip()).resolve()


def read_stories(stories_path: Path) -> list[dict[str, Any]]:
    data = json.loads(stories_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        stories = data
    elif isinstance(data, dict):
        for key in ("userStories", "stories", "items"):
            value = data.get(key)
            if isinstance(value, list):
                stories = value
                break
        else:
            stories = []
    else:
        stories = []

    return [story for story in stories if isinstance(story, dict)]


def story_id(story: dict[str, Any], index: int) -> str | None:
    for key in ("id", "storyId", "story_id", "key"):
        value = story.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    title = story.get("title")
    if isinstance(title, str) and title.strip():
        return f"story #{index + 1} ({title.strip()})"

    return None


def positive_int(value: Any) -> int | None:
    return value if isinstance(value, int) and value > 0 else None


def load_stories_state(stories_path: Path) -> list[StoryState]:
    return [
        StoryState(
            identifier=story_id(story, index),
            passes=story.get("passes") is True,
            sprint=positive_int(story.get("sprint")),
            priority=positive_int(story.get("priority")),
            order=index,
        )
        for index, story in enumerate(read_stories(stories_path))
    ]


def review_mode(stories_path: Path) -> str:
    data = json.loads(stories_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return AUTOMATIC_REVIEW_MODE

    sprint_config = data.get("sprintConfig")
    if sprint_config is None:
        return AUTOMATIC_REVIEW_MODE
    if not isinstance(sprint_config, dict):
        raise ValueError("sprintConfig must be an object.")

    mode = sprint_config.get("reviewMode", AUTOMATIC_REVIEW_MODE)
    if not isinstance(mode, str) or mode not in {
        AUTOMATIC_REVIEW_MODE,
        MANUAL_REVIEW_MODE,
    }:
        raise ValueError(
            'sprintConfig.reviewMode must be either "automatic" or "manual".'
        )
    return mode


def ordered_stories(stories: list[StoryState]) -> list[StoryState]:
    return sorted(
        stories,
        key=lambda story: (
            story.priority if story.priority is not None else sys.maxsize,
            story.order,
        ),
    )


def first_unfinished_story(
    stories: list[StoryState], *, sprint: int | None = None
) -> StoryState | None:
    for story in ordered_stories(stories):
        if story.passes or story.identifier is None:
            continue
        if sprint is not None and story.sprint != sprint:
            continue
        return story
    return None


def find_story_by_id(stories: list[StoryState], identifier: str) -> StoryState | None:
    matches = [story for story in stories if story.identifier == identifier]
    return matches[0] if len(matches) == 1 else None


def extract_completion_event(message: str) -> CompletionEvent | None:
    for line in reversed(message.splitlines()):
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith(PROMISE_PREFIX) or not stripped.endswith(
            PROMISE_SUFFIX
        ):
            return None

        content = (
            stripped.removeprefix(PROMISE_PREFIX).removesuffix(PROMISE_SUFFIX).strip()
        )
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None

        if (
            not isinstance(data, dict)
            or data.get("protocol") != PROTOCOL
            or data.get("type") != COMPLETION_TYPE
        ):
            return None

        identifier = data.get("storyId")
        if isinstance(identifier, str) and identifier.strip():
            return CompletionEvent(story_id=identifier.strip())
        return None

    return None


def build_story_prompt(identifier: str) -> str:
    return f"$story-loop {identifier}"


def build_review_prompt(sprint: int) -> str:
    return (
        f"Sprint {sprint} is complete. Spawn exactly one separate subagent to perform the review. "
        f"In that subagent, invoke `$code-review` to review sprint {sprint}. The implementation "
        "agent must not perform the review. Wait for the reviewer, "
        "return its findings, and stop for human review."
    )


def decide_next_action(
    stories_path: Path, completion_event: CompletionEvent
) -> HookDecision | None:
    if not stories_path.exists():
        return StopDecision(f"Story loop stopped: {stories_path} does not exist.")

    stories = load_stories_state(stories_path)
    completed_story = find_story_by_id(stories, completion_event.story_id)
    if completed_story is None:
        return StopDecision(
            f"Story loop stopped: completion event references unknown or duplicate story "
            f"{completion_event.story_id!r}."
        )
    if not completed_story.passes:
        return StopDecision(
            f"Story loop stopped: {completion_event.story_id!r} is not marked as passing."
        )

    if completed_story.sprint is not None:
        next_story = first_unfinished_story(stories, sprint=completed_story.sprint)
        if next_story is not None and next_story.identifier is not None:
            return ContinueDecision(build_story_prompt(next_story.identifier))
        if review_mode(stories_path) == MANUAL_REVIEW_MODE:
            return StopDecision(
                f"Sprint {completed_story.sprint} is complete. Run `$code-review` manually "
                "when ready, then explicitly resume `$story-loop`."
            )
        return ContinueDecision(build_review_prompt(completed_story.sprint))

    next_story = first_unfinished_story(stories)
    if next_story is None or next_story.identifier is None:
        return None
    return ContinueDecision(build_story_prompt(next_story.identifier))


def main() -> int:
    payload = load_payload()
    completion_event = extract_completion_event(payload.last_assistant_message)
    if completion_event is None:
        return 0

    repo_root = detect_repo_root(payload.cwd)
    if repo_root is None:
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": "Story loop stopped: current directory is not a Git repository.",
                }
            )
        )
        return 0

    try:
        decision = decide_next_action(repo_root / STORIES_PATH, completion_event)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        decision = StopDecision(
            f"Story loop stopped: could not read stories state: {exc}"
        )

    if decision is None:
        return 0
    if isinstance(decision, ContinueDecision):
        print(json.dumps({"decision": "block", "reason": decision.prompt}))
        return 0

    print(
        json.dumps(
            {
                "continue": False,
                "stopReason": decision.reason,
                "systemMessage": decision.reason,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
