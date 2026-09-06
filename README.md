# courseT

`courseT` is a small Python engine and repository template for hands-on terminal courses.

Repository: https://github.com/NIMCprogramming/courseT

Each course is a separate app and repository. For example, `kuberT` teaches Kubernetes and
a future `rayT` app can teach Ray. Both apps use `courseT` for lesson data, checks, and progress.

## What the engine provides

- A strict YAML lesson schema.
- Manual, command, and multiple checks.
- Warm-up and review questions.
- Troubleshooting, common mistakes, summaries, and cheat notes.
- Separate JSON progress for every course.

## Start a course

1. Copy the files in `template/` into a new repository.
2. Use Python 3.11+ and `uv`. `uv sync` creates `.venv` automatically.
3. Keep the included public `courset-engine` Git dependency.
4. Keep course lessons in `lessons/NN-module/NN-lesson.yaml`.
5. Change `your-course`, `Your Course`, and `YOUR_COURSE_STATE_DIR` to your course names.
6. Edit `src/course_app/environment.py` for course setup requirements.
7. Read the copied `CLAUDE.md` before asking an AI agent to build lessons.

The environment adapter belongs to the course app. For example, kuberT checks Docker, Kind,
and kubectl. A Ray course may check a Python environment and start local Ray. The engine does
not know about Kubernetes or Ray.

Each app defines one `CourseSpec`:

```python
from pathlib import Path

from courset.course import CourseSpec

COURSE = CourseSpec(
    slug="rayt",
    title="rayT",
    subtitle="learn Ray in your terminal",
    lessons_root=Path(__file__).parent / "lessons",
    state_file=Path.home() / ".rayt" / "progress.json",
)
```

Use `ProgressStore(COURSE.state_file)` for progress. Call `validate_course(COURSE)` in tests.

## Required commands

Every course repository must keep these commands:

```bash
make install
make run
make test
make lint
make type
make clean
```

## Lesson rules

- Write learner text in A2 English.
- One lesson teaches one clear goal.
- Put lessons in numbered module folders.
- The YAML `id` must match its path without `.yaml`.
- Use a command check for work that a program can test.
- Use a manual check only for reading or discussion.
- Never run a learner's command against an unsafe remote system.
- Keep setup and cleanup commands clear.
- Add warm-up questions from older lessons and review questions for the current lesson.

See `template/lessons/01-start/01-welcome.yaml` for the smallest complete lesson.
