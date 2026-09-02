# Full Browser WebAssembly (Pyodide) Learning Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-backend, client-side WebAssembly learning platform for Raylings covering all 81 exercises across 18 chapters with Monaco editor, debounced localStorage state persistence, terminal diagnostics, and live simulated Ray cluster inspector.

**Architecture:** A build-time Python catalog generator bundles all 18 chapters and 81 exercises into `docs/assets/playground_catalog.json`. The browser client loads Pyodide WebAssembly with an in-memory pure-Python Ray simulation engine. A client-side `RaylingsStorage` manager syncs exercise code and completion state to `localStorage` with JSON export/import support.

**Tech Stack:** Python 3.12, Pyodide 0.26.4 (WebAssembly), Monaco Editor 0.45.0, Tailwind CSS, MkDocs Material, Pytest.

## Global Constraints

- Python 3.12 compatibility with explicit typing, `ruff` linting, and `pyright` type checks.
- All 81 exercises across 18 chapters must be bundled with non-empty code, solutions, and hints.
- Client state must persist to `localStorage` with debounced auto-saving (300ms) and export/import JSON backup.
- Clean execution with zero external server dependencies.

---

### Task 1: Full Curriculum Catalog Bundle Generator & Unit Test Suite

**Files:**
- Modify: `src/raylings/playground_assets.py`
- Modify: `tests/test_playground.py`
- Test: `tests/test_playground.py`

**Interfaces:**
- Consumes: `raylings.manifest.get_manifest()`
- Produces: `generate_playground_catalog() -> list[dict[str, Any]]`, `export_playground_bundle(output_path: Path | str) -> Path`

- [ ] **Step 1: Write unit tests verifying full 18-chapter, 81-exercise extraction**

```python
# In tests/test_playground.py
import json
from pathlib import Path
from raylings.playground_assets import export_playground_bundle, generate_playground_catalog

def test_generate_playground_catalog_all_81_exercises():
    catalog = generate_playground_catalog()
    assert isinstance(catalog, list)
    assert len(catalog) == 81, f"Expected 81 exercises, got {len(catalog)}"
    
    chapters = {ex["chapter"] for ex in catalog}
    assert len(chapters) == 18, f"Expected 18 chapters, got {len(chapters)}"
    
    for ex in catalog:
        assert ex["name"], "Exercise name must not be empty"
        assert ex["chapter_name"], "Chapter name must not be empty"
        assert ex["code"], f"Starter code missing for {ex['name']}"
        assert ex["solution"], f"Solution code missing for {ex['name']}"
        assert ex["prompt"], f"Prompt missing for {ex['name']}"
        assert ex["hint"], f"Hint missing for {ex['name']}"

def test_export_playground_bundle_file(tmp_path: Path):
    out_file = tmp_path / "playground_catalog.json"
    result_path = export_playground_bundle(out_file)
    assert result_path.exists()
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert len(data) == 81
```

- [ ] **Step 2: Run test to observe baseline state**

Run: `uv run pytest tests/test_playground.py -v`
Expected: Passes if 81 exercises are present, or fails if counts differ.

- [ ] **Step 3: Enhance `src/raylings/playground_assets.py`**

Ensure `generate_playground_catalog` extracts docstring prompts, multi-line hints, and clean metadata for all exercises.

```python
"""Asset generation and catalog bundling for the interactive WASM / Pyodide Playground."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raylings.manifest import get_manifest


def generate_playground_catalog() -> list[dict[str, Any]]:
    """Extract all exercises and reference solutions for the web playground.

    Returns:
        list[dict[str, Any]]: Array of exercise payloads with metadata, code, hints, and solutions.
    """
    manifest = get_manifest()
    catalog: list[dict[str, Any]] = []

    for chapter in manifest.chapters:
        for ex in chapter.exercises:
            code_str = ""
            if ex.file_path.exists():
                code_str = ex.file_path.read_text(encoding="utf-8")

            sol_str = ""
            if ex.solution_path.exists():
                sol_str = ex.solution_path.read_text(encoding="utf-8")

            # Extract docstring description from exercise code
            prompt = ex.title
            if code_str.strip().startswith('"""'):
                end_idx = code_str.find('"""', 3)
                if end_idx != -1:
                    prompt = code_str[3:end_idx].strip()

            hint_str = (
                "\n".join(f"• {h}" for h in ex.hints)
                if ex.hints
                else "Read the docstrings carefully and implement the missing logic."
            )

            catalog.append(
                {
                    "chapter": chapter.number,
                    "chapter_name": chapter.name,
                    "chapter_title": chapter.title,
                    "name": ex.name,
                    "title": ex.title,
                    "path": ex.path,
                    "prompt": prompt,
                    "hint": hint_str,
                    "code": code_str,
                    "solution": sol_str,
                }
            )

    return catalog


def export_playground_bundle(output_path: Path | str) -> Path:
    """Export the playground exercise catalog as JSON to the specified path.

    Args:
        output_path: Destination path for the exported JSON catalog.

    Returns:
        Path: Path to written catalog file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    catalog = generate_playground_catalog()
    path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return path
```

- [ ] **Step 4: Generate the latest bundle asset**

Run: `uv run python -c "from raylings.playground_assets import export_playground_bundle; export_playground_bundle('docs/assets/playground_catalog.json')"`
Run: `uv run pytest tests/test_playground.py -v`
Expected: PASS with 81 exercises bundled.

- [ ] **Step 5: Commit changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add src/raylings/playground_assets.py tests/test_playground.py docs/assets/playground_catalog.json
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "feat: extract and bundle all 81 curriculum exercises for wasm playground"
```

---

### Task 2: Enhanced Pure-Python In-Memory Ray Simulation Module

**Files:**
- Modify: `docs/assets/playground.html`
- Test: `tests/test_playground.py`

**Interfaces:**
- Produces: `WASM_COMPAT_SOURCE` pure-Python simulation module injected into Pyodide.

- [ ] **Step 1: Expand `WASM_COMPAT_SOURCE` inside `docs/assets/playground.html`**

Implement comprehensive simulation for:
- `@ray.remote` functions (with `num_returns`, `options`, async futures resolution).
- `@ray.remote` classes (Actors with state retention, async methods, detached actor names, `ActorPool`).
- `WasmPlasmaStore` (with byte size tracking, object count, `put`, `get`, `wait`, zero-copy array emulation).
- `ray.data` operations (`from_items`, `range`, `map`, `filter`, `map_batches`, `take_all`).
- Telemetry reporting hook `_get_cluster_stats()` returning `{cpus, objects, bytes, actors, tasks}` for the UI inspector.

- [ ] **Step 2: Add Python simulation unit test in `tests/test_playground.py`**

Test the simulation module directly using Python `exec()` to ensure that core task, actor, and object store flows execute without error.

- [ ] **Step 3: Run test to verify simulation passes**

Run: `uv run pytest tests/test_playground.py -v`
Expected: PASS.

- [ ] **Step 4: Commit changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/assets/playground.html tests/test_playground.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "feat: enhance pure-python in-memory ray simulation engine"
```

---

### Task 3: Zero-Backend Client State Persistence Engine (`RaylingsStorage`) & Hotkeys

**Files:**
- Modify: `docs/assets/playground.html`

**Interfaces:**
- Produces: `class RaylingsStorage` managing `localStorage`, auto-saving, JSON export/import, and progress stats.

- [ ] **Step 1: Implement `RaylingsStorage` in `docs/assets/playground.html`**

```javascript
class RaylingsStorage {
  constructor(storageKey = 'raylings_playground_v1') {
    this.storageKey = storageKey;
    this.state = this.loadState();
  }

  loadState() {
    try {
      const raw = localStorage.getItem(this.storageKey);
      if (raw) return JSON.parse(raw);
    } catch (e) {
      console.warn("Failed to load state from localStorage:", e);
    }
    return {
      version: 1,
      lastActiveExerciseIndex: 0,
      exercises: {},
    };
  }

  saveState() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.state));
    } catch (e) {
      console.warn("Failed to save state to localStorage:", e);
    }
  }

  getExercise(name) {
    return this.state.exercises[name] || null;
  }

  saveCode(name, code) {
    if (!this.state.exercises[name]) {
      this.state.exercises[name] = { status: 'in_progress', userCode: code, hintVisible: false };
    } else {
      this.state.exercises[name].userCode = code;
      if (this.state.exercises[name].status === 'not_started') {
        this.state.exercises[name].status = 'in_progress';
      }
    }
    this.state.exercises[name].lastModifiedAt = new Date().toISOString();
    this.saveState();
  }

  markCompleted(name) {
    if (!this.state.exercises[name]) {
      this.state.exercises[name] = { status: 'completed', userCode: '', hintVisible: false };
    }
    this.state.exercises[name].status = 'completed';
    this.state.exercises[name].passedAt = new Date().toISOString();
    this.saveState();
  }

  exportBackup() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.state, null, 2));
    const downloadAnchor = document.createElement('a');
    const date = new Date().toISOString().slice(0, 10);
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `raylings-progress-${date}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  }

  importBackup(jsonString) {
    const parsed = JSON.parse(jsonString);
    if (parsed && parsed.exercises) {
      this.state = parsed;
      this.saveState();
      return true;
    }
    return false;
  }

  resetExercise(name) {
    if (this.state.exercises[name]) {
      delete this.state.exercises[name];
      this.saveState();
    }
  }

  resetAll() {
    this.state = { version: 1, lastActiveExerciseIndex: 0, exercises: {} };
    this.saveState();
  }
}
```

- [ ] **Step 2: Bind debounced Monaco editor keystrokes and keyboard shortcuts**

- Keystroke debounce (300ms) calls `storage.saveCode(currentEx.name, code)`.
- `Ctrl+Enter` / `Cmd+Enter` runs code verification.
- `Alt+Left` and `Alt+Right` navigates exercises.
- `H` toggles the progressive hint drawer.
- `F11` toggles fullscreen mode.

- [ ] **Step 3: Commit changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/assets/playground.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "feat: add raylings client-side state persistence and keyboard hotkeys"
```

---

### Task 4: Interactive Split-Pane Syllabus UI & Cluster Inspector

**Files:**
- Modify: `docs/assets/playground.html`
- Modify: `tests/test_playground.py`

- [ ] **Step 1: Build the 300px collapsible Syllabus Sidebar**
  - Course progress bar with completion stats (e.g., `42 / 81 completed (52%)`).
  - Search input with instantaneous fuzzy matching and status filters (`All`, `To Do`, `Done`).
  - 18 collapsible chapter accordions showing chapter titles and progress badges (e.g. `01. Basics (6/6 ✓)`).
  - Exercise item buttons with status icons (`✓`, `⏳`, `○`).

- [ ] **Step 2: Build Center Monaco Editor Workspace & Action Toolbar**
  - Header breadcrumbs: Chapter name, exercise name, file path.
  - Action buttons: Run (`Ctrl+Enter`), Hint (`H`), Solution Diff, Reset, Next.
  - Collapsible hint panel and solution diff viewer.

- [ ] **Step 3: Build Right Inspector Pane with Real-Time Cluster Telemetry**
  - Execution Output Tab: Formatted terminal stdout/stderr, elapsed time, error traceback callouts.
  - Simulated Cluster State Tab: Live gauges for Virtual Worker Nodes, Allocated vCPUs, Plasma Object Store memory bar, Active Actors, and Remote Tasks.
  - Synchronize telemetry updates after every Pyodide execution.

- [ ] **Step 4: Add Fullscreen Toggle (`⛶` / `F11`)**
  - Implements full-bleed fullscreen breakout mode with automatic Monaco editor resize (`editor.layout()`).

- [ ] **Step 5: Run tests and verify HTML integrity**

Run: `uv run pytest tests/test_playground.py -v`
Expected: PASS.

- [ ] **Step 6: Commit changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/assets/playground.html tests/test_playground.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "feat: complete interactive split-pane syllabus ui and cluster inspector"
```

---

### Task 5: Documentation, MkDocs Integration & Quality Checks

**Files:**
- Modify: `docs/playground.md`
- Modify: `CHANGELOG.md`
- Test: `mkdocs build --strict`, `ruff check .`, `pyright src`

- [ ] **Step 1: Update `docs/playground.md` with full platform guide**
  - Detail 18 chapters and 81 exercises.
  - Detail state persistence, backup JSON export/import, and keyboard shortcuts.
  - Full-width container styling for MkDocs rendering.

- [ ] **Step 2: Update `CHANGELOG.md`**
  - Record the Full WebAssembly Browser Learning Platform release under `[Unreleased]` or latest version.

- [ ] **Step 3: Run comprehensive verification checks**

Run: `uv run pytest -q`
Run: `uv run ruff check .`
Run: `uv run pyright src`
Run: `uv run mkdocs build --strict`
Expected: All tests pass, zero lint/type errors, MkDocs builds cleanly.

- [ ] **Step 4: Commit changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/playground.md CHANGELOG.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "docs: document full browser wasm platform and update changelog"
```
