import sys

REQUIREMENTS = frozenset({"python-environment"})


def check_requirement(requirement: str) -> tuple[bool, str]:
    if requirement != "python-environment":
        return False, f"Unknown course requirement: {requirement}"
    if sys.prefix == sys.base_prefix:
        return False, "This lesson needs the course virtual environment. Run it with `uv run`."
    return True, ""
