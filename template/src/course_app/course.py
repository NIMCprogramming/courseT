import os
from pathlib import Path

from courset.course import CourseSpec

from course_app.environment import REQUIREMENTS, check_requirement


def lessons_root() -> Path:
    installed = Path(__file__).resolve().parent / "lessons"
    source = Path(__file__).resolve().parent.parent.parent / "lessons"
    return installed if installed.exists() else source


def state_file() -> Path:
    base = os.getenv("YOUR_COURSE_STATE_DIR")
    return (Path(base) if base else Path.home() / ".your-course") / "progress.json"


COURSE = CourseSpec(
    slug="your-course",
    title="Your Course",
    subtitle="learn by practice in your terminal",
    lessons_root=lessons_root(),
    state_file=state_file(),
    requirement_names=REQUIREMENTS,
    check_requirement=check_requirement,
)
