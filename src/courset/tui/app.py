from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from courset.course import CourseSpec
from courset.lesson import discover_lessons
from courset.state import ProgressStore
from courset.tui.cheat_screen import CheatPanelScreen
from courset.tui.lesson_screens import LessonPickerScreen, LessonScreen


class MainMenuScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("q", "app.quit", "Quit")]

    def __init__(self, course: CourseSpec, store: ProgressStore) -> None:
        super().__init__()
        self.course = course
        self.store = store

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"[b]Welcome to {self.course.title}[/b]", id="welcome")
        yield ListView(
            ListItem(Label("Run next unfinished lesson"), id="a-next"),
            ListItem(Label("Pick a lesson"), id="a-pick"),
            ListItem(Label("Cheat panel"), id="a-cheat"),
            ListItem(Label("Reset lesson progress"), id="a-progress"),
            ListItem(Label("Quit"), id="a-quit"),
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        action = (event.item.id or "").removeprefix("a-")
        if action == "quit":
            self.app.exit()
        elif action == "pick":
            self.app.push_screen(LessonPickerScreen(self.course, self.store))
        elif action == "cheat":
            self.app.push_screen(CheatPanelScreen(self.course, self.store))
        elif action == "progress":
            self.store.reset()
        elif action == "next":
            completed = self.store.load().completed_lessons
            for lesson in discover_lessons(self.course.lessons_root):
                if lesson.id not in completed:
                    self.app.push_screen(LessonScreen(self.course, self.store, lesson))
                    return


class CourseApp(App[None]):
    SELECT_AUTO_SCROLL_LINES = 5
    SELECT_AUTO_SCROLL_SPEED = 120.0

    def __init__(self, course: CourseSpec) -> None:
        super().__init__()
        self.course = course
        self.store = ProgressStore(course.state_file)
        self.title = course.title
        self.sub_title = course.subtitle

    def on_mount(self) -> None:
        self.push_screen(MainMenuScreen(self.course, self.store))


def run_app(course: CourseSpec) -> None:
    CourseApp(course).run()
