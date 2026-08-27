# Track 2: Developer Tooling & CLI Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Track 2 developer tooling:
1. Community Exercise Scaffolder CLI (`raylings new` / `src/raylings/scaffolder.py`)
2. Real-Time Cluster Health & Telemetry Inspector (`raylings top` / `raylings metrics` / `src/raylings/metrics.py`)
3. Interactive Full-Screen Split-Pane TUI (`raylings tui` / `src/raylings/tui.py`)
4. CLI registration, documentation, and comprehensive automated test coverage.

**Architecture:**
- `src/raylings/scaffolder.py`: Generates standardized exercise and solution templates, validates names and paths, and registers new exercises with AST/manifest updates.
- `src/raylings/metrics.py`: Telemetry collector that interrogates Ray cluster state (nodes, object store memory, actor tables, task queues) and renders live-updating Rich dashboard tables with JSON export.
- `src/raylings/tui.py`: Full-screen terminal user interface built with Rich `Layout`, `Live`, `Tree`, and non-blocking raw keystroke input, supporting interactive exercise browsing, real-time code execution, progressive hint revelation, and telemetry toggling.
- `src/raylings/cli.py`: Registers `raylings new`, `raylings top` / `raylings metrics`, and `raylings tui` subcommands with rich help text and flags.

**Tech Stack:** Python 3.10+, Ray Core, Rich (Layout, Live, Tree, Table, Syntax, Panel), Typer, Pytest, Ruff.

---

### File Structure Map

```
raylings/
├── src/
│   └── raylings/
│       ├── cli.py             # CLI command registrations (new, top, metrics, tui)
│       ├── scaffolder.py      # Exercise and solution scaffolding engine
│       ├── metrics.py         # Ray cluster telemetry and resource monitor
│       └── tui.py             # Full-screen split-pane interactive TUI
├── tests/
│   ├── test_scaffolder.py     # Unit tests for exercise scaffolding
│   ├── test_metrics.py        # Unit tests for cluster telemetry & metrics
│   └── test_tui.py            # Unit tests for full-screen TUI rendering and actions
└── docs/
    └── cli-reference.md       # Updated CLI documentation with new commands
```

---

### Task 1: Exercise Scaffolding Engine (`src/raylings/scaffolder.py` & `raylings new`)

**Files:**
- Create: `src/raylings/scaffolder.py`
- Modify: `src/raylings/cli.py`
- Create: `tests/test_scaffolder.py`

- [x] **Step 1: Write failing tests in `tests/test_scaffolder.py`**
  - Test exercise name and chapter validation.
  - Test generating exercise skeleton and solution files in temporary directory.
  - Test boilerplate formatting (`os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"`, docstrings, `verify()`, `__main__`).
  - Test `--json` payload output.

- [x] **Step 2: Run test to verify failure**
  - Run: `uv run pytest tests/test_scaffolder.py -v`
  - Expected: ModuleNotFoundError / FAIL.

- [x] **Step 3: Implement `src/raylings/scaffolder.py`**
  - `ExerciseScaffolder` class with `scaffold(chapter, name, title, description, hints, dry_run)`.
  - Generates `exercises/<chapter>/<name>.py` and `solutions/<chapter>/<name>.py`.
  - Helper functions for manifest snippet generation.

- [x] **Step 4: Register `raylings new` CLI command in `src/raylings/cli.py`**
  - Options: `--title` (`-t`), `--description` (`-d`), `--dry-run`, `--json`.

- [x] **Step 5: Run tests to verify pass**
  - Run: `uv run pytest tests/test_scaffolder.py -v`
  - Expected: PASS.

- [x] **Step 6: Commit Task 1**
  ```bash
  git add src/raylings/scaffolder.py src/raylings/cli.py tests/test_scaffolder.py
  git commit -m "feat(scaffolder): implement exercise template generator CLI" --no-gpg-sign
  ```

---

### Task 2: Real-Time Cluster Health & Telemetry Inspector (`src/raylings/metrics.py` & `raylings top`)

**Files:**
- Create: `src/raylings/metrics.py`
- Modify: `src/raylings/cli.py`
- Create: `tests/test_metrics.py`

- [x] **Step 1: Write failing tests in `tests/test_metrics.py`**
  - Test telemetry extraction with active/mock Ray cluster.
  - Test memory formatting, actor table formatting, node resource table.
  - Test `--json` serialization and one-shot snapshot mode.

- [x] **Step 2: Run test to verify failure**
  - Run: `uv run pytest tests/test_metrics.py -v`
  - Expected: ModuleNotFoundError / FAIL.

- [x] **Step 3: Implement `src/raylings/metrics.py`**
  - `ClusterMetricsCollector` class: collects cluster nodes, CPU/GPU utilization, object store memory / Plasma spill stats, actor table, and task metrics.
  - `render_metrics_dashboard()`: renders Rich layout with Node table, Object Store panel, and Actor state table.

- [x] **Step 4: Register `raylings top` and `raylings metrics` in `src/raylings/cli.py`**
  - Options: `--interval` (`-i`), `--once`, `--json`.

- [x] **Step 5: Run tests to verify pass**
  - Run: `uv run pytest tests/test_metrics.py -v`
  - Expected: PASS.

- [x] **Step 6: Commit Task 2**
  ```bash
  git add src/raylings/metrics.py src/raylings/cli.py tests/test_metrics.py
  git commit -m "feat(metrics): implement real-time cluster telemetry dashboard CLI" --no-gpg-sign
  ```

---

### Task 3: Interactive Full-Screen Split-Pane TUI (`src/raylings/tui.py` & `raylings tui`)

**Files:**
- Create: `src/raylings/tui.py`
- Modify: `src/raylings/cli.py`
- Create: `tests/test_tui.py`

- [x] **Step 1: Write failing tests in `tests/test_tui.py`**
  - Test TUI state manager (`TUIState`: active chapter, active exercise, hint level, telemetry toggle, run results).
  - Test split-pane Rich layout builder (`create_tui_layout()`: Tree explorer, Code preview panel, Output panel, Footer).
  - Test action dispatching (`navigate_next`, `navigate_prev`, `toggle_hints`, `trigger_run`, `toggle_telemetry`).

- [x] **Step 2: Run test to verify failure**
  - Run: `uv run pytest tests/test_tui.py -v`
  - Expected: ModuleNotFoundError / FAIL.

- [x] **Step 3: Implement `src/raylings/tui.py`**
  - `RaylingsTUI` class with split-pane Rich rendering and non-blocking key listener loop.
  - Seamless integration with exercise runner for instant in-TUI execution and hint reveals.

- [x] **Step 4: Register `raylings tui` CLI command in `src/raylings/cli.py`**
  - Options: `--exercise` (`-e`), `--non-interactive` (for headless tests / automation).

- [x] **Step 5: Run tests to verify pass**
  - Run: `uv run pytest tests/test_tui.py -v`
  - Expected: PASS.

- [x] **Step 6: Commit Task 3**
  ```bash
  git add src/raylings/tui.py src/raylings/cli.py tests/test_tui.py
  git commit -m "feat(tui): implement full-screen split-pane interactive TUI" --no-gpg-sign
  ```

---

### Task 4: Documentation, Integration Verification, and Suite Pass

**Files:**
- Modify: `docs/cli-reference.md` (document `raylings new`, `raylings top`, `raylings tui`)
- Modify: `README.md` (add TUI, Scaffolder, and Metrics features)
- Modify: `tests/test_cli.py`

- [x] **Step 1: Update documentation**
  - Document all new CLI flags, keybindings, and examples in `docs/cli-reference.md` and `README.md`.

- [x] **Step 2: Run full verification suite**
  - Run `uv run pytest -m "not heavy" -v`.
  - Run `uv run ruff check src tests` and `uv run ruff format --check src tests`.
  - Run `uvx --with mkdocs-material mkdocs build --strict`.

- [x] **Step 3: Commit and Merge**
  ```bash
  git add docs/ README.md tests/test_cli.py
  git commit -m "docs(cli): document new tui, scaffolder, and metrics commands" --no-gpg-sign
  ```
