# Your Course

A hands-on course that runs in your terminal.

## Requirements

- Python 3.11+
- `uv`
- `make`

## Start

```bash
make install
make run
```

`uv sync` creates a local `.venv`. Always run course commands through `uv run` or Make.

## Develop

```bash
make test
make lint
make type
```

See `ROADMAP.md` for the lesson list and `CLAUDE.md` for course-writing rules.
