from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown, Static

from courset.course import CourseSpec
from courset.lesson import discover_lessons
from courset.state import ProgressStore


class CheatPanelScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, course: CourseSpec, store: ProgressStore) -> None:
        super().__init__()
        self.course = course
        self.store = store

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("[b]Cheat panel[/b] - completed lessons", id="cheat-title")
        completed = self.store.load().completed_lessons
        lessons = [
            lesson
            for lesson in discover_lessons(self.course.lessons_root)
            if lesson.id in completed
        ]
        with VerticalScroll():
            if not lessons:
                yield Static("Complete a lesson to see its notes.")
            for lesson in lessons:
                yield Static(f"[b]{lesson.id}[/b] - {lesson.title}")
                yield Markdown(lesson.cheat or "_(no cheat notes)_")
        yield Footer()
