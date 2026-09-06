from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

RequirementChecker = Callable[[str], tuple[bool, str]]


def allow_no_requirements(requirement: str) -> tuple[bool, str]:
    return False, f"Unknown course requirement: {requirement}"


@dataclass(frozen=True)
class CourseSpec:
    slug: str
    title: str
    subtitle: str
    lessons_root: Path
    state_file: Path
    requirement_names: frozenset[str] = frozenset()
    check_requirement: RequirementChecker = allow_no_requirements
