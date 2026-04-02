#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMPLETION_PROMISE = "<promise>STORY_COMPLETE</promise>"
STORIES_PATH = Path("tasks/stories.json")


@dataclass(frozen=True)
class StopPayload:
    cwd: Path
    last_assistant_message: str


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


def read_stories(stories_path: Path) -> list[dict]:
    if not stories_path.exists():
        return []

    data = json.loads(stories_path.read_text())
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


def story_id(story: dict, index: int) -> str | None:
    for key in ("id", "storyId", "story_id", "key"):
        value = story.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    title = story.get("title")
    if isinstance(title, str) and title.strip():
        return f"story #{index + 1} ({title.strip()})"

    return None


def next_unfinished_story_id(stories_path: Path) -> str | None:
    for index, story in enumerate(read_stories(stories_path)):
        if story.get("passes") is True:
            continue
        return story_id(story, index)
    return None


def has_completion_promise(message: str) -> bool:
    for line in reversed(message.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped == COMPLETION_PROMISE
    return False


def build_prompt(next_story: str) -> str:
    return f"$story-loop {next_story}"


def main() -> int:
    payload = load_payload()
    repo_root = detect_repo_root(payload.cwd)
    if repo_root is None:
        return 0

    if not has_completion_promise(payload.last_assistant_message):
        return 0

    next_story = next_unfinished_story_id(repo_root / STORIES_PATH)
    if next_story is None:
        return 0

    print(json.dumps({"decision": "block", "reason": build_prompt(next_story)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
