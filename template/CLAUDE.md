# Course Agent Guide

Read this file before changing the course.

## Project rules

1. Use Python 3.11+, `uv`, and the local `.venv` made by `uv sync`.
2. Keep these commands working: `make install`, `make run`, `make test`, `make lint`,
   `make type`, and `make clean`.
3. Keep course content in YAML. Do not edit Python to add a lesson.
4. Put lessons at `lessons/NN-module/NN-lesson.yaml`.
5. Make each lesson `id` match its path without `.yaml`.
6. Write learner text in A2 English. Use short sentences and explain new words.
7. Give every lesson one clear learning goal.
8. Use real practice when it is safe. Use `command` or `multiple` checks for work a
   program can test. Use `manual` only for reading or discussion.
9. Keep environment setup in `src/course_app/environment.py`, not in the shared engine.
10. Declare every lesson environment need in `requires`.
11. Do not run commands against an unsafe remote system.
12. Run tests, Ruff, and mypy before every commit.

## Lesson structure

Required fields:

```yaml
id: 01-module/01-lesson
title: "Lesson title"
module: module
order: 1
estimated_minutes: 5
learning_goal: "Do one clear thing."
intro: |
  Explain the idea.
task: |
  Give the learner a small task.
hint: "Give one useful hint."
summary: "Repeat the main idea."
cheat: |
  - Add a short reference.
check:
  type: command
  cmd: "a safe local command"
  expect: "expected text"
```

Useful active-learning fields are `prerequisites`, `warm_up`, `troubleshooting`,
`review_questions`, `common_mistakes`, and `spaced_hooks`.

## Course design

- Keep the roadmap in `ROADMAP.md` and update it when lessons change.
- Teach simple ideas before hard ideas.
- Revisit old ideas in later warm-up questions.
- Make cleanup steps clear when a task changes local files or services.
- Add a test when the environment adapter gains new behavior.
