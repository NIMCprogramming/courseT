.PHONY: install test lint type clean

install:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

type:
	uv run mypy

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache dist build
