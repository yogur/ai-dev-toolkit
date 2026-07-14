from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "hooks" / "stop_continue.py"
HOOK_CONFIG_PATH = REPO_ROOT / "hooks" / "hooks.json"


def load_stop_continue_module():
    spec = importlib.util.spec_from_file_location("stop_continue", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


stop_continue = load_stop_continue_module()


def init_git_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, text=True
    )


def write_stories(repo_root: Path, payload: object) -> None:
    tasks_dir = repo_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "stories.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def completion_message(story_id: str) -> str:
    return (
        '<promise>{"protocol":"story-loop/v1","type":"STORY_COMPLETE",'
        f'"storyId":"{story_id}"}}</promise>'
    )


def run_hook(repo_root: Path, message: str) -> dict | None:
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH)],
        input=json.dumps({"cwd": str(repo_root), "last_assistant_message": message}),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


class HookConfigTests(unittest.TestCase):
    def test_plugin_hook_uses_portable_uv_command(self) -> None:
        payload = json.loads(HOOK_CONFIG_PATH.read_text(encoding="utf-8"))
        command = payload["hooks"]["Stop"][0]["hooks"][0]["command"]

        self.assertEqual(
            command,
            'uv run --script "${PLUGIN_ROOT}/hooks/stop_continue.py"',
        )
        self.assertNotIn("/usr/bin", command)


class StopContinueTests(unittest.TestCase):
    maxDiff = None

    def test_extracts_versioned_completion_event(self) -> None:
        event = stop_continue.extract_completion_event(completion_message("ticket-42"))

        self.assertEqual(event, stop_continue.CompletionEvent(story_id="ticket-42"))

    def test_rejects_legacy_completion_event(self) -> None:
        self.assertIsNone(
            stop_continue.extract_completion_event("<promise>STORY_COMPLETE</promise>")
        )

    def test_rejects_wrong_protocol(self) -> None:
        message = (
            '<promise>{"protocol":"story-loop/v0","type":"STORY_COMPLETE",'
            '"storyId":"story-a"}</promise>'
        )

        self.assertIsNone(stop_continue.extract_completion_event(message))

    def test_same_sprint_continues_to_next_story_by_priority(self) -> None:
        decision = self.decide(
            {
                "userStories": [
                    {"id": "story-c", "passes": False, "sprint": 1, "priority": 3},
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 1, "priority": 2},
                ]
            },
            "story-a",
        )

        self.assertEqual(
            decision, stop_continue.ContinueDecision("$story-loop story-b")
        )

    def test_does_not_jump_to_lower_priority_story_in_another_sprint(self) -> None:
        decision = self.decide(
            {
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 1, "priority": 5},
                    {"id": "story-c", "passes": False, "sprint": 2, "priority": 2},
                ]
            },
            "story-a",
        )

        self.assertEqual(
            decision, stop_continue.ContinueDecision("$story-loop story-b")
        )

    def test_sprint_boundary_triggers_mandatory_review(self) -> None:
        decision = self.decide(
            {
                "sprintConfig": {"checkpointEnabled": False},
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 1, "priority": 1},
                    {"id": "story-b", "passes": False, "sprint": 2, "priority": 2},
                ],
            },
            "story-a",
        )

        self.assertEqual(
            decision,
            stop_continue.ContinueDecision(
                "$code-review Review sprint 1 and stop for human review."
            ),
        )

    def test_final_sprint_also_triggers_review(self) -> None:
        decision = self.decide(
            {
                "userStories": [
                    {"id": "story-a", "passes": True, "sprint": 2, "priority": 1}
                ]
            },
            "story-a",
        )

        self.assertEqual(
            decision,
            stop_continue.ContinueDecision(
                "$code-review Review sprint 2 and stop for human review."
            ),
        )

    def test_unknown_story_stops_instead_of_advancing(self) -> None:
        decision = self.decide(
            {
                "userStories": [
                    {"id": "story-a", "passes": False, "sprint": 1, "priority": 1}
                ]
            },
            "story-z",
        )

        self.assertIsInstance(decision, stop_continue.StopDecision)
        self.assertIn("unknown or duplicate", decision.reason)

    def test_unpassed_completed_story_stops(self) -> None:
        decision = self.decide(
            {
                "userStories": [
                    {"id": "story-a", "passes": False, "sprint": 1, "priority": 1}
                ]
            },
            "story-a",
        )

        self.assertEqual(
            decision,
            stop_continue.StopDecision(
                "Story loop stopped: 'story-a' is not marked as passing."
            ),
        )

    def test_non_sprinted_flow_remains_continuous(self) -> None:
        decision = self.decide(
            {
                "userStories": [
                    {"id": "story-a", "passes": True, "priority": 1},
                    {"id": "story-b", "passes": False, "priority": 2},
                ]
            },
            "story-a",
        )

        self.assertEqual(
            decision, stop_continue.ContinueDecision("$story-loop story-b")
        )

    def test_main_emits_review_continuation(self) -> None:
        with tempfile_repo() as repo_root:
            write_stories(
                repo_root,
                {
                    "userStories": [
                        {"id": "story-a", "passes": True, "sprint": 1, "priority": 1}
                    ]
                },
            )

            output = run_hook(repo_root, completion_message("story-a"))

        self.assertEqual(
            output,
            {
                "decision": "block",
                "reason": "$code-review Review sprint 1 and stop for human review.",
            },
        )

    def test_main_surfaces_invalid_story_state(self) -> None:
        with tempfile_repo() as repo_root:
            write_stories(
                repo_root,
                {
                    "userStories": [
                        {"id": "story-a", "passes": False, "sprint": 1, "priority": 1}
                    ]
                },
            )

            output = run_hook(repo_root, completion_message("story-a"))

        assert output is not None
        self.assertFalse(output["continue"])
        self.assertIn("not marked as passing", output["stopReason"])

    def test_main_ignores_non_completion_messages(self) -> None:
        with tempfile_repo() as repo_root:
            output = run_hook(repo_root, "Normal assistant response")

        self.assertIsNone(output)

    def decide(self, payload: object, story_id: str):
        with tempfile_repo() as repo_root:
            write_stories(repo_root, payload)
            return stop_continue.decide_next_action(
                repo_root / "tasks" / "stories.json",
                stop_continue.CompletionEvent(story_id=story_id),
            )


class TempRepo:
    def __init__(self) -> None:
        self._tempdir: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> Path:
        self._tempdir = tempfile.TemporaryDirectory()
        path = Path(self._tempdir.name)
        init_git_repo(path)
        return path

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self._tempdir is not None
        self._tempdir.cleanup()


def tempfile_repo() -> TempRepo:
    return TempRepo()


if __name__ == "__main__":
    unittest.main()
