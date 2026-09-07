from pathlib import Path

from courset.course import CourseSpec
from courset.models import Lesson, ManualCheck, Question
from courset.state import ProgressStore
from courset.tui import CourseApp, LessonPickerScreen, LessonScreen, QuizScreen


def make_course(tmp_path: Path) -> CourseSpec:
    return CourseSpec(
        slug="test",
        title="Test Course",
        subtitle="learn by testing",
        lessons_root=tmp_path / "lessons",
        state_file=tmp_path / "progress.json",
    )


def make_lesson() -> Lesson:
    return Lesson(
        id="01-start/01-test",
        title="Test",
        module="start",
        order=1,
        intro="Read this.",
        task="Do this.",
        check=ManualCheck(type="manual"),
    )


def test_course_app_uses_course_branding(tmp_path: Path) -> None:
    app = CourseApp(make_course(tmp_path))
    assert app.title == "Test Course"
    assert app.sub_title == "learn by testing"


def test_lesson_picker_holds_course_and_store(tmp_path: Path) -> None:
    course = make_course(tmp_path)
    store = ProgressStore(course.state_file)
    screen = LessonPickerScreen(course, store)
    assert screen.course is course
    assert screen.store is store


def test_lesson_screen_checks_requirements(tmp_path: Path) -> None:
    course = make_course(tmp_path)
    screen = LessonScreen(course, ProgressStore(course.state_file), make_lesson())
    assert screen._check_requirements() == (True, "")


def test_lesson_screen_marks_complete(tmp_path: Path) -> None:
    course = make_course(tmp_path)
    store = ProgressStore(course.state_file)
    screen = LessonScreen(course, store, make_lesson())
    screen._mark_complete()
    assert store.load().completed_lessons == ["01-start/01-test"]


def test_quiz_screen_holds_questions(tmp_path: Path) -> None:
    question = Question(prompt="Question?", answer="Answer.")
    screen = QuizScreen(
        ProgressStore(tmp_path / "progress.json"),
        make_lesson(),
        [question],
        "Review",
    )
    assert screen.questions == [question]
    assert screen.revealed is False
