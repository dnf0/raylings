.PHONY: help bootstrap lint fmt test watch

help:
	@echo "Available make targets:"
	@echo "  bootstrap  - Install dependencies in editable mode with development tools"
	@echo "  lint       - Run ruff linter and pyright type checker"
	@echo "  fmt        - Format code with ruff and auto-fix lint errors"
	@echo "  test       - Run pytest test suite"
	@echo "  watch      - Start raylings interactive watcher"

bootstrap:
	pip install -e ".[dev]"

lint:
	ruff check .
	pyright

fmt:
	ruff format .
	ruff check --fix .

test:
	pytest

watch:
	raylings watch
