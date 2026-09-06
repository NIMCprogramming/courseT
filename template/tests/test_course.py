from courset.lesson import validate_course

from course_app.course import COURSE


def test_course_is_valid() -> None:
    assert validate_course(COURSE) == []
