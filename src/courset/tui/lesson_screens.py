from collections.abc import Callable
from typing import ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Markdown, RichLog, Static

from courset.checker import run_check
from courset.course import CourseSpec
from courset.lesson import discover_lessons
from courset.models import Lesson, ManualCheck, Question
from courset.state import ProgressStore
from courset.tui.quiz_screen import QuizScreen

ClipboardCopy = Callable[[str], str | None]


class LessonItem(ListItem):
    def __init__(self, lesson: Lesson, marker: str) -> None:
        super().__init__(Label(f"{marker} {lesson.id} - {lesson.title}", markup=False))
        self.lesson = lesson


class LessonPickerScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(
        self, course: CourseSpec, store: ProgressStore, copy_text: ClipboardCopy | None = None
    ) -> None:
        super().__init__()
        self.course = course
        self.store = store
        self.copy_text = copy_text

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Pick a lesson", id="title")
        completed = self.store.load().completed_lessons
        yield ListView(
            *[
                LessonItem(lesson, "[x]" if lesson.id in completed else "[ ]")
                for lesson in discover_lessons(self.course.lessons_root)
            ],
            id="lessons",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, LessonItem):
            self.app.pop_screen()
            self.app.push_screen(
                LessonScreen(self.course, self.store, event.item.lesson, self.copy_text)
            )


class LessonScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("c", "do_primary", "Check / Confirm"),
        Binding("h", "do_hint", "Hint"),
        Binding("w", "do_warmup", "Warm-up quiz"),
        Binding("r", "do_review", "Review quiz"),
        Binding("n", "do_next", "Next lesson"),
        Binding("s", "app.pop_screen", "Skip"),
    ]
    CSS = """
    LessonScreen { layout: vertical; }
    LessonScreen > VerticalScroll { height: 1fr; }
    #output { height: 3; margin: 0 2; padding: 0 1; border: round $primary; }
    """

    def __init__(
        self,
        course: CourseSpec,
        store: ProgressStore,
        lesson: Lesson,
        copy_text: ClipboardCopy | None = None,
    ) -> None:
        super().__init__()
        self.course = course
        self.store = store
        self.lesson = lesson
        self.copy_text = copy_text

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"[b]{self.lesson.id}[/b] - {self.lesson.title}", id="lesson-title")
        if self.lesson.learning_goal:
            yield Static(f"[b]Goal:[/b] {self.lesson.learning_goal}", id="learning-goal")
        with VerticalScroll():
            yield Markdown(self.lesson.intro, id="intro")
            if not isinstance(self.lesson.check, ManualCheck):
                yield Markdown(self.lesson.task, id="task")
            extras = self._build_extras()
            if extras:
                yield Markdown(extras, id="extras")
        yield RichLog(id="output", markup=True)
        yield Footer()

    def _build_extras(self) -> str:
        parts: list[str] = []
        if self.lesson.prerequisites:
            parts.append("## Builds on\n" + ", ".join(self.lesson.prerequisites))
        if self.lesson.warm_up:
            parts.append("## Warm-up\nPress **w** to start.")
        if self.lesson.troubleshooting:
            item = self.lesson.troubleshooting
            parts.append(f"## Troubleshooting\n{item.scenario}\n\n**Question:** {item.question}")
        if self.lesson.review_questions:
            parts.append("## Review\nPress **r** to start.")
        if self.lesson.common_mistakes:
            mistakes = (
                f"- **{item.mistake}** - {item.fix}" for item in self.lesson.common_mistakes
            )
            parts.append("## Common mistakes\n" + "\n".join(mistakes))
        if self.lesson.summary:
            parts.append(f"## Summary\n{self.lesson.summary}")
        return "\n\n".join(parts)

    def on_mount(self) -> None:
        ok, message = self._check_requirements()
        if not ok:
            self.query_one("#output", RichLog).write(f"[red]{message}[/red]")

    def _check_requirements(self) -> tuple[bool, str]:
        for requirement in self.lesson.requires:
            ok, message = self.course.check_requirement(requirement)
            if not ok:
                return False, message
        return True, ""

    def action_do_primary(self) -> None:
        log = self.query_one("#output", RichLog)
        ok, message = self._check_requirements()
        if not ok:
            log.write(f"[red]{message}[/red]")
            return
        result = run_check(self.lesson.check)
        if not result.passed:
            log.write(f"[red]FAIL: {result.detail}[/red]")
            return
        self._mark_complete()
        log.write("[green]Lesson complete.[/green]")

    def action_do_hint(self) -> None:
        self.query_one("#output", RichLog).write(f"[blue]{self.lesson.hint or 'No hint.'}[/blue]")

    def action_do_warmup(self) -> None:
        self._push_quiz(self.lesson.warm_up, "Warm-up quiz")

    def action_do_review(self) -> None:
        self._push_quiz(self.lesson.review_questions, "Review quiz")

    def _push_quiz(self, questions: list[Question], title: str) -> None:
        if questions:
            self.app.push_screen(QuizScreen(self.store, self.lesson, questions, title))

    def on_mouse_up(self, event: events.MouseUp) -> None:
        self.call_after_refresh(self._copy_selection)

    def _copy_selection(self) -> None:
        text = self.get_selected_text()
        if text and (self.copy_text is None or self.copy_text(text) is None):
            self.app.copy_to_clipboard(text)

    def action_do_next(self) -> None:
        completed = self.store.load().completed_lessons
        for lesson in discover_lessons(self.course.lessons_root):
            if lesson.id != self.lesson.id and lesson.id not in completed:
                self.app.pop_screen()
                self.app.push_screen(LessonScreen(self.course, self.store, lesson, self.copy_text))
                return

    def _mark_complete(self) -> None:
        progress = self.store.load()
        if self.lesson.id not in progress.completed_lessons:
            progress.completed_lessons.append(self.lesson.id)
        self.store.save(progress)
