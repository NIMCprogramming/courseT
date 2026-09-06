import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from courset.checker import run_check
from courset.course import CourseSpec
from courset.models import Lesson, ManualCheck
from courset.state import ProgressStore

console = Console()


def check_requirements(course: CourseSpec, lesson: Lesson) -> tuple[bool, str]:
    for requirement in lesson.requires:
        ok, message = course.check_requirement(requirement)
        if not ok:
            return False, message
    return True, ""


def run_lesson(course: CourseSpec, store: ProgressStore, lesson: Lesson) -> bool:
    console.print(Panel.fit(f"{lesson.id} - {lesson.title}", style="bold cyan"))
    ok, message = check_requirements(course, lesson)
    if not ok:
        console.print(f"[bold red][FAIL][/bold red] {message}")
        return False

    console.print(Markdown(lesson.intro))
    if isinstance(lesson.check, ManualCheck):
        console.input("\n[dim]Press Enter when you finish reading...[/dim]")
    else:
        console.print(Panel(Markdown(lesson.task), title="Task", border_style="yellow"))
        while True:
            choice = questionary.select(
                "What now?",
                choices=["Check my work", "Show hint", "Skip lesson"],
            ).ask()
            if choice in (None, "Skip lesson"):
                return False
            if choice == "Show hint":
                console.print(Panel(lesson.hint or "No hint.", title="Hint"))
                continue
            result = run_check(lesson.check)
            if not result.passed:
                console.print(f"[bold red][FAIL][/bold red] {result.detail}")
                continue
            console.print(f"[bold green][OK][/bold green] {result.detail}")
            break

    progress = store.load()
    if lesson.id not in progress.completed_lessons:
        progress.completed_lessons.append(lesson.id)
    store.save(progress)
    return True
