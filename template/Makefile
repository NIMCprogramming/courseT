.PHONY: help install run test lint type clean

help:
	@echo "make install   create .venv and install dependencies"
	@echo "make run       open the course"
	@echo "make test      run tests"
	@echo "make lint      run ruff"
	@echo "make type      run mypy"
	@echo "make clean     delete local build files"

install:
	uv sync --extra dev

run:
	uv run your-course shell

test:
	uv run pytest

lint:
	uv run ruff check .

type:
	uv run mypy

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache dist build
