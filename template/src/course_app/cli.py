from courset.cli import build_cli
from courset.tui import run_app

from course_app.course import COURSE


def shell() -> None:
    """Open the full-screen course app."""
    run_app(COURSE)


app = build_cli(COURSE, shell)
