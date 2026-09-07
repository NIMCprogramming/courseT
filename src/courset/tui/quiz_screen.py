from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown, Static

from courset.models import Lesson, Question
from courset.state import ProgressStore


class QuizScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("space", "reveal_or_next", "Reveal / Next"),
        Binding("enter", "reveal_or_next", "Reveal / Next"),
        Binding("y", "mark_known", "I knew it"),
        Binding("n", "mark_missed", "I missed it"),
        Binding("escape", "app.pop_screen", "Exit quiz"),
    ]
    CSS = """
    QuizScreen { layout: vertical; }
    #quiz-title { padding: 0 2; margin: 1 2 0 2; color: $accent; }
    #quiz-progress { padding: 0 2; margin: 0 2; color: $primary; }
    #quiz-prompt { padding: 1 2; margin: 1 2; border: round $warning; }
    #quiz-answer { padding: 1 2; margin: 0 2 1 2; border: round $success; }
    #quiz-hint { padding: 0 2; color: $primary; }
    """

    def __init__(
        self, store: ProgressStore, lesson: Lesson, questions: list[Question], title: str
    ) -> None:
        super().__init__()
        self.store = store
        self.lesson = lesson
        self.questions = questions
        self.title_text = title
        self.index = 0
        self.revealed = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"[b]{self.title_text}[/b] - lesson {self.lesson.id}", id="quiz-title")
        yield Static("", id="quiz-progress")
        with VerticalScroll():
            yield Markdown("", id="quiz-prompt")
            yield Markdown("", id="quiz-answer")
        yield Static("Press Space to reveal, then y/n. Esc leaves the quiz.", id="quiz-hint")
        yield Footer()

    def on_mount(self) -> None:
        if not self.questions:
            self.app.pop_screen()
            return
        self._refresh_view()

    def _refresh_view(self) -> None:
        question = self.questions[self.index]
        self.query_one("#quiz-progress", Static).update(
            f"Question {self.index + 1} of {len(self.questions)} - {question.kind}"
        )
        body = question.prompt
        if question.kind == "multiple_choice" and question.options:
            body += "\n\n" + "\n".join(f"- {option}" for option in question.options)
        self.query_one("#quiz-prompt", Markdown).update(body)
        self.query_one("#quiz-answer", Markdown).update(
            f"**Answer:** {question.answer}" if self.revealed else ""
        )

    def action_reveal_or_next(self) -> None:
        if not self.revealed:
            self.revealed = True
            self._refresh_view()
        else:
            self._advance()

    def action_mark_known(self) -> None:
        if self.revealed:
            self._advance()

    def action_mark_missed(self) -> None:
        if not self.revealed:
            return
        question = self.questions[self.index]
        self.store.record_missed(self.store.load(), question.concept, self.lesson.id)
        self._advance()

    def _advance(self) -> None:
        self.index += 1
        self.revealed = False
        if self.index >= len(self.questions):
            self.app.pop_screen()
        else:
            self._refresh_view()
