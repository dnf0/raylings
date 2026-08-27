# Contributing to Raylings

Thank you for your interest in improving Raylings! We welcome contributions ranging from typo fixes and documentation improvements to new exercises and CLI enhancements.

---

## Development Environment

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) or standard `python -m venv`
- Git

### Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/raylings.git
   cd raylings
   ```

2. Create a virtual environment and install dependencies in editable mode:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. Optionally install pre-commit hooks:
   ```bash
   pre-commit install
   ```

---

## Development Commands

We provide a `Makefile` for common development tasks:

- `make bootstrap` — Install all dependencies and development tooling.
- `make lint` — Run `ruff check .` and `pyright` type checks.
- `make fmt` — Auto-format code using `ruff format .` and `ruff check --fix .`.
- `make test` — Run the full test suite with `pytest`.
- `make watch` — Launch the Raylings CLI watcher against local exercises.

---

## Exercise Design Guidelines

When creating or modifying exercises:

1. **Exercise File Structure**:
   - Every exercise in `exercises/<chapter>/<name>.py` must start with a docstring detailing the concept and challenge.
   - Include `# I AM NOT DONE` at the top of the file so the watcher knows the exercise is unsolved by default.
   - Provide a callable `run()` function or assertions that execute and validate the solution.
2. **Canonical Solutions**:
   - Every exercise file must have an exact matching file in `solutions/<chapter>/<name>.py`.
   - The solution in `solutions/` must NOT contain `# I AM NOT DONE` and must pass validation cleanly.
3. **Manifest Entry**:
   - Register the new exercise in `src/raylings/manifest.py` with appropriate chapter metadata, prerequisites, and layered hints.

---

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages:

- `feat:` — Introduces a new feature or exercise
- `fix:` — Fixes a bug or broken exercise
- `docs:` — Documentation improvements (README, docstrings, hints)
- `refactor:` — Code restructuring without feature changes
- `test:` — Adding or updating test suites
- `chore:` — Maintenance, tooling, and infrastructure updates

Keep commits atomic and self-contained.

---

## Pull Request Checklist

Before submitting your pull request:
- [ ] Run `make fmt` to ensure formatting passes.
- [ ] Run `make lint` with zero errors or warnings.
- [ ] Run `make test` and confirm all tests pass.
- [ ] Ensure all modified/new exercises have corresponding verified solutions.
