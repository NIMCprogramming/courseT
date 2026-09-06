import subprocess
from pathlib import Path
from unittest.mock import patch

from courset.checker import run_check
from courset.course import CourseSpec
from courset.lesson import discover_lessons, validate_course, validate_lesson_paths
from courset.models import CommandCheck, ManualCheck, MultipleCheck, UserProgress
from courset.state import ProgressStore


def test_loads_template_lesson() -> None:
    root = Path(__file__).parent.parent / "template" / "lessons"
    assert len(discover_lessons(root)) == 1
    assert validate_lesson_paths(root) == []


def test_course_rejects_unknown_requirements(tmp_path: Path) -> None:
    lessons = tmp_path / "lessons" / "01-start"
    lessons.mkdir(parents=True)
    (lessons / "01-test.yaml").write_text(
        """id: 01-start/01-test
title: Test
module: start
order: 1
intro: Read.
task: Try.
requires: [runtime]
check: {type: manual}
"""
    )
    course = CourseSpec("test", "Test", "Learn", tmp_path / "lessons", tmp_path / "state")
    assert validate_course(course) == ["01-start/01-test: unknown requirements: runtime"]


@patch("courset.checker.subprocess.run")
def test_failed_command_does_not_pass(mock_run) -> None:
    mock_run.return_value = subprocess.CompletedProcess([], 1, "PASS", "error")
    result = run_check(CommandCheck(type="command", cmd="test", expect="PASS"))
    assert result.passed is False


@patch("courset.checker.subprocess.run")
def test_command_check_passes_when_output_contains_expected(mock_run) -> None:
    mock_run.return_value = subprocess.CompletedProcess([], 0, "Running", "")
    assert run_check(CommandCheck(type="command", cmd="test", expect="Running")).passed


@patch("courset.checker.subprocess.run")
def test_command_check_fails_when_output_differs(mock_run) -> None:
    mock_run.return_value = subprocess.CompletedProcess([], 0, "Pending", "")
    assert not run_check(CommandCheck(type="command", cmd="test", expect="Running")).passed


@patch("courset.checker.subprocess.run", side_effect=subprocess.TimeoutExpired("test", 1))
def test_command_timeout_fails(_mock_run) -> None:
    assert not run_check(CommandCheck(type="command", cmd="test", expect="ok")).passed


def test_manual_check_passes() -> None:
    assert run_check(ManualCheck(type="manual")).passed


@patch("courset.checker.subprocess.run")
def test_multiple_checks_stop_after_failure(mock_run) -> None:
    mock_run.return_value = subprocess.CompletedProcess([], 0, "no", "")
    check = MultipleCheck(
        type="multiple",
        checks=[CommandCheck(type="command", cmd="test", expect="yes")],
    )
    assert not run_check(check).passed


def test_progress_is_separate_per_course(tmp_path: Path) -> None:
    first = ProgressStore(tmp_path / "first" / "progress.json")
    second = ProgressStore(tmp_path / "second" / "progress.json")
    first.save(UserProgress(completed_lessons=["01-start/01-welcome"]))
    assert first.load().completed_lessons
    assert second.load().completed_lessons == []
