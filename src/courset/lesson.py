from pathlib import Path

import yaml

from courset.course import CourseSpec
from courset.models import Lesson


def load_lesson_file(path: Path) -> Lesson:
    return Lesson.model_validate(yaml.safe_load(path.read_text()))


def discover_lessons(lessons_root: Path) -> list[Lesson]:
    return [load_lesson_file(path) for path in sorted(lessons_root.rglob("*.yaml"))]


def validate_lesson_paths(lessons_root: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for path in sorted(lessons_root.rglob("*.yaml")):
        lesson = load_lesson_file(path)
        expected_id = path.relative_to(lessons_root).with_suffix("").as_posix()
        if lesson.id != expected_id:
            errors.append(f"{path}: id must be '{expected_id}'")
        if lesson.id in seen:
            errors.append(f"{path}: duplicate id '{lesson.id}'")
        seen.add(lesson.id)
    return errors


def validate_course(course: CourseSpec) -> list[str]:
    errors = validate_lesson_paths(course.lessons_root)
    for lesson in discover_lessons(course.lessons_root):
        unknown = set(lesson.requires) - course.requirement_names
        if unknown:
            errors.append(f"{lesson.id}: unknown requirements: {', '.join(sorted(unknown))}")
    return errors
