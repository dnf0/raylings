.PHONY: help bootstrap lint fmt test watch clean

help:
	@echo "Available make targets:"
	@echo "  bootstrap  - Install dependencies in editable mode with development tools"
	@echo "  lint       - Run ruff linter and pyright type checker"
	@echo "  fmt        - Format code with ruff and auto-fix lint errors"
	@echo "  test       - Run pytest test suite"
	@echo "  watch      - Start raylings interactive watcher"
	@echo "  clean      - Remove build artifacts and cache directories"

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

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache .coverage htmlcov

