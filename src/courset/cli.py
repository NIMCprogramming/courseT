from collections.abc import Callable

import typer
from rich.console import Console

from courset.course import CourseSpec
from courset.lesson import discover_lessons
from courset.runner import run_lesson
from courset.state import ProgressStore


def build_cli(course: CourseSpec, shell: Callable[[], None] | None = None) -> typer.Typer:
    app = typer.Typer(help=f"{course.title} - {course.subtitle}.", no_args_is_help=True)
    console = Console()
    store = ProgressStore(course.state_file)

    @app.command(name="list")
    def list_lessons() -> None:
        """List all lessons."""
        completed = store.load().completed_lessons
        for lesson in discover_lessons(course.lessons_root):
            mark = "[green][x][/green]" if lesson.id in completed else "[dim][ ][/dim]"
            console.print(f"{mark} {lesson.id} - {lesson.title}")

    @app.command(name="next")
    def next_lesson() -> None:
        """Run the next unfinished lesson."""
        progress = store.load()
        for lesson in discover_lessons(course.lessons_root):
            if lesson.id not in progress.completed_lessons:
                run_lesson(course, store, lesson)
                return
        console.print("[bold green][OK][/bold green] All lessons complete. Well done!")

    @app.command()
    def lesson(lesson_id: str) -> None:
        """Run a specific lesson by ID."""
        for entry in discover_lessons(course.lessons_root):
            if entry.id == lesson_id:
                run_lesson(course, store, entry)
                return
        console.print(f"[bold red][FAIL][/bold red] No lesson with id '{lesson_id}'.")
        raise typer.Exit(code=1)

    if shell is not None:
        app.command()(shell)
    return app
