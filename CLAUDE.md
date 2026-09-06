# courseT Agent Guide

`courseT` is the shared engine for separate hands-on terminal course apps.

## Rules

1. Keep the engine independent from course subjects such as Kubernetes or Ray.
2. Keep subject setup in each course's environment adapter.
3. Do not add a plugin system or setup workflow language without a real second use case.
4. Use Python 3.11+, `uv`, pytest, Ruff, and strict mypy.
5. Keep public functions typed and files under about 250 lines.
6. Use Pydantic for lesson and progress data.
7. Keep the copied starter in `template/` runnable.
8. Run engine checks and a fresh copied-template check after changing the public API.
9. Do not add GitHub CI unless requested.
10. Do not add course lessons to the engine. The one template lesson is only an example.

## Public boundary

- `CourseSpec` holds course identity, paths, and requirement behavior.
- `models.py` owns the shared YAML schema.
- `lesson.py` loads and validates course content.
- `checker.py` runs trusted bundled lesson checks.
- `state.py` keeps course progress in a course-specific file.
- `runner.py` and `cli.py` provide the simple terminal experience.

The engine does not own full-screen course-specific screens. A course may add them and pass a
`shell` command to `build_cli` when needed.
