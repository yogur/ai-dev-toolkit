from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".codex" / "hooks" / "stop_continue.py"


def load_stop_continue_module():
    spec = importlib.util.spec_from_file_location("stop_continue", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


stop_continue = load_stop_continue_module()


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)


def write_stories(repo_root: Path, payload: dict) -> None:
    tasks_dir = repo_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "stories.json").write_text(json.dumps(payload, indent=2) + "\n")


class StopContinueTests(unittest.TestCase):
    maxDiff = None

    def test_extracts_structured_completion_event(self) -> None:
        event = stop_continue.extract_completion_event(
            '<promise>{"type":"STORY_COMPLETE","storyId":"ticket-42"}</promise>'
        )

        self.assertEqual(event, stop_continue.CompletionEvent(story_id="ticket-42"))

    def test_accepts_legacy_completion_event_without_story_id(self) -> None:
        event = stop_continue.extract_completion_event("<promise>STORY_COMPLETE</promise>")

        self.assertEqual(event, stop_continue.CompletionEvent(story_id=None))

    def test_same_sprint_continues_to_next_story_by_priority(self) -> None:
        self.assert_decision(
            payload={
                "sprintConfig": {"checkpointEnabled": True},
                "userStories": [
                    {"id": "story-c", "passes": False, "sprint": 1, "priority": 3},
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 1, "priority": 2},
                ],
            },
            completion_event=stop_continue.CompletionEvent(story_id="story-a"),
            expected_prompt="$story-loop story-b",
        )

    def test_last_story_in_sprint_triggers_checkpoint(self) -> None:
        self.assert_decision(
            payload={
                "sprintConfig": {"checkpointEnabled": True},
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 2, "priority": 2},
                ],
            },
            completion_event=stop_continue.CompletionEvent(story_id="story-a"),
            expected_prompt="$sprint-checkpoint 1",
        )

    def test_checkpoint_disabled_falls_through_to_next_story(self) -> None:
        self.assert_decision(
            payload={
                "sprintConfig": {"checkpointEnabled": False},
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 2, "priority": 2},
                ],
            },
            completion_event=stop_continue.CompletionEvent(story_id="story-a"),
            expected_prompt="$story-loop story-b",
        )

    def test_missing_sprint_fields_keep_continuous_mode(self) -> None:
        self.assert_decision(
            payload={
                "userStories": [
                    {"id": "story-a", "passes": True, "priority": 1},
                    {"id": "story-b", "passes": False, "priority": 2},
                ]
            },
            completion_event=stop_continue.CompletionEvent(story_id="story-a"),
            expected_prompt="$story-loop story-b",
        )

    def test_prepassed_story_in_next_sprint_still_triggers_checkpoint(self) -> None:
        self.assert_decision(
            payload={
                "sprintConfig": {"checkpointEnabled": True},
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": True, "sprint": 2, "priority": 2},
                    {"id": "story-c", "passes": False, "sprint": 2, "priority": 3},
                ],
            },
            completion_event=stop_continue.CompletionEvent(story_id="story-a"),
            expected_prompt="$sprint-checkpoint 1",
        )

    def test_unknown_completed_story_falls_back_to_next_unfinished(self) -> None:
        self.assert_decision(
            payload={
                "sprintConfig": {"checkpointEnabled": True},
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 2, "priority": 2},
                ],
            },
            completion_event=stop_continue.CompletionEvent(story_id="story-z"),
            expected_prompt="$story-loop story-b",
        )

    def test_main_uses_structured_promise_to_emit_checkpoint(self) -> None:
        with tempfile_repo() as repo_root:
            write_stories(
                repo_root,
                {
                    "sprintConfig": {"checkpointEnabled": True},
                    "userStories": [
                        {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                        {"id": "story-b", "passes": False, "sprint": 2, "priority": 2},
                    ],
                },
            )

            result = subprocess.run(
                [sys.executable, str(MODULE_PATH)],
                input=json.dumps(
                    {
                        "cwd": str(repo_root),
                        "last_assistant_message": '<promise>{"type":"STORY_COMPLETE","storyId":"story-a"}</promise>',
                    }
                ),
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertEqual(
                json.loads(result.stdout),
                {"decision": "block", "reason": "$sprint-checkpoint 1"},
            )
            self.assertEqual(result.stderr, "")

    def assert_decision(
        self,
        *,
        payload: dict,
        completion_event: object,
        expected_prompt: str,
    ) -> None:
        with tempfile_repo() as repo_root:
            write_stories(repo_root, payload)
            decision = stop_continue.decide_next_action(
                repo_root / "tasks" / "stories.json",
                completion_event,
            )

            self.assertIsNotNone(decision)
            assert decision is not None
            self.assertEqual(decision.prompt, expected_prompt)


class TempRepo:
    def __init__(self) -> None:
        self._path: Path | None = None
        self._tempdir: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> Path:
        self._tempdir = tempfile.TemporaryDirectory()
        self._path = Path(self._tempdir.name)
        init_git_repo(self._path)
        return self._path

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self._tempdir is not None
        self._tempdir.cleanup()


def tempfile_repo() -> TempRepo:
    return TempRepo()


if __name__ == "__main__":
    unittest.main()
