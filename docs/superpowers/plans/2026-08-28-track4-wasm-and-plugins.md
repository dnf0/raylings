# Track 4: Ecosystem Extensions & Interactive WASM Playground Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-dependency Pyodide/WebAssembly Ray simulation layer, an interactive browser-based learning playground embedded in documentation, and an extensible pluggable curriculum plugin architecture with a reference quantitative finance pack.

**Architecture:**
- `raylings.wasm_compat`: Pure-Python, in-memory cooperative simulation of core Ray APIs (`init`, `remote`, `put`, `get`, `wait`, `ActorPool`, `ray.data`) executable in sandboxed WebAssembly / Pyodide environments without C++ binaries or multi-process dependencies.
- `docs/playground.html` & `docs/playground.md`: Responsive browser-based IDE with Monaco editor, Pyodide 0.26+ runtime, exercise selection, hint drawer, simulated cluster telemetry, and live execution console.
- `raylings.plugins`: Extensible plugin discovery system leveraging `importlib.metadata.entry_points(group="raylings.plugins")` and CLI management (`raylings plugins list`, `raylings plugins info`, `raylings plugins validate`) paired with a reference quantitative finance extension pack.

**Tech Stack:** Python 3.10-3.12, Typer, Rich, Pyodide 0.26.4 (WASM), HTML5 / CSS3 / JavaScript, MkDocs Material, Pytest.

---

### Task 1: Pure-Python WASM Ray Simulation Engine (`src/raylings/wasm_compat.py`)

**Files:**
- Create: `src/raylings/wasm_compat.py`
- Test: `tests/test_wasm_compat.py`

- [ ] **Step 1: Write comprehensive failing tests for WASM compatibility layer**
  - Test `ray.init()`, `ray.shutdown()`, `ray.is_initialized()`.
  - Test `@ray.remote` on functions: invocation with `.remote(*args)`, returning `WasmObjectRef`, and resolution with `ray.get()`.
  - Test `ray.put()` and `ray.get()` with simulated Plasma object store (hex IDs, byte accounting, caching).
  - Test `ray.wait()` with timeouts and `num_returns`.
  - Test `@ray.remote` on stateful actor classes: instantiation via `.remote()`, remote method dispatch, state mutation, and concurrent task queues.
  - Test `ActorPool` implementation (`map`, `map_unordered`, `submit`, `get_next`, `has_next`).
  - Test `ray.data` simulated pipeline (`range`, `from_items`, `map`, `map_batches`, `filter`, `take_all`, `count`).

- [ ] **Step 2: Run test to verify failure**
  - Run: `uv run pytest tests/test_wasm_compat.py -v`
  - Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 3: Implement `src/raylings/wasm_compat.py`**
  - Implement `WasmObjectRef`, `WasmPlasmaStore`, `WasmActorHandle`, `WasmRemoteFunction`, `WasmRemoteClass`.
  - Implement `WasmRayModule` exposing standard Ray namespace (`init`, `shutdown`, `is_initialized`, `remote`, `put`, `get`, `wait`, `ActorPool`, `data`).
  - Add auto-detection logic for Pyodide (`sys.platform == "emscripten"` or `os.environ.get("RAYLINGS_WASM") == "1"`).

- [ ] **Step 4: Run test to verify it passes**
  - Run: `uv run pytest tests/test_wasm_compat.py -v`
  - Expected: PASS (100%).

- [ ] **Step 5: Format and lint**
  - Run: `uv run ruff format src/raylings/wasm_compat.py tests/test_wasm_compat.py && uv run ruff check src/raylings/wasm_compat.py tests/test_wasm_compat.py`

---

### Task 2: Interactive Browser WASM Playground (`docs/playground.html` & `docs/playground.md`)

**Files:**
- Create: `src/raylings/playground_assets.py`
- Create: `docs/playground.md`
- Create: `docs/assets/playground.html`
- Test: `tests/test_playground.py`

- [ ] **Step 1: Write test for playground assets and exercise catalog exporter**
  - Verify `generate_playground_catalog()` exports exercises and solutions to JSON/JS format.
  - Verify `docs/playground.md` and HTML templates exist with valid syntax and CDN references.

- [ ] **Step 2: Run test to verify failure**
  - Run: `uv run pytest tests/test_playground.py -v`
  - Expected: FAIL.

- [ ] **Step 3: Implement playground asset exporter and web interface**
  - Implement `src/raylings/playground_assets.py` to generate bundled exercise metadata and Pyodide bootstrap scripts.
  - Build `docs/assets/playground.html` with Monaco editor, Pyodide WebWorker runner, chapter/exercise selector, reset button, solution toggle, ANSI terminal rendering, and cluster resource visualizer.
  - Build `docs/playground.md` embedding the playground seamlessly within MkDocs.

- [ ] **Step 4: Run test to verify it passes**
  - Run: `uv run pytest tests/test_playground.py -v`
  - Expected: PASS.

- [ ] **Step 5: Format and lint**
  - Run: `uv run ruff format src/raylings/playground_assets.py tests/test_playground.py && uv run ruff check src/raylings/playground_assets.py tests/test_playground.py`

---

### Task 3: Pluggable Curriculum Plugin Architecture & CLI Registry (`src/raylings/plugins/`)

**Files:**
- Create: `src/raylings/plugins/__init__.py`
- Create: `src/raylings/plugins/base.py`
- Create: `src/raylings/plugins/finance.py`
- Modify: `src/raylings/manifest.py`
- Modify: `src/raylings/cli.py`
- Test: `tests/test_plugins.py`

- [ ] **Step 1: Write comprehensive failing tests for plugin system**
  - Test `RaylingsPlugin` protocol and registration.
  - Test plugin discovery from `entry_points` and local directories.
  - Test manifest merging with external plugin chapters.
  - Test `raylings plugins list`, `raylings plugins info <name>`, `raylings plugins validate <module>`.
  - Test Quantitative Finance plugin exercises (`finance01.py`, `finance02.py`, `finance03.py`).

- [ ] **Step 2: Run test to verify failure**
  - Run: `uv run pytest tests/test_plugins.py -v`
  - Expected: FAIL.

- [ ] **Step 3: Implement plugin protocol, loader, and CLI commands**
  - Implement `RaylingsPlugin` base class / protocol in `src/raylings/plugins/base.py`.
  - Implement plugin discovery in `src/raylings/plugins/__init__.py`.
  - Implement Quantitative Finance reference pack in `src/raylings/plugins/finance.py`.
  - Add `plugins` Typer subcommand group to `src/raylings/cli.py`.
  - Update `src/raylings/manifest.py` to include registered plugins.

- [ ] **Step 4: Run test to verify it passes**
  - Run: `uv run pytest tests/test_plugins.py -v`
  - Expected: PASS.

- [ ] **Step 5: Format and lint**
  - Run: `uv run ruff format src/raylings/plugins/ tests/test_plugins.py && uv run ruff check src/raylings/plugins/ tests/test_plugins.py`

---

### Task 4: Documentation, MkDocs Navigation, and Full Suite Verification

**Files:**
- Create: `docs/plugins.md`
- Modify: `mkdocs.yml`
- Modify: `docs/ROADMAP.md`
- Modify: `README.md`

- [ ] **Step 1: Create plugin authoring guide `docs/plugins.md`**
  - Document plugin protocol, `pyproject.toml` entry points, chapter registration, and distribution on PyPI.

- [ ] **Step 2: Update `mkdocs.yml` and `README.md`**
  - Add Playground and Plugins Guide to MkDocs nav.
  - Update feature matrix in `README.md`.

- [ ] **Step 3: Update `docs/ROADMAP.md`**
  - Mark Track 4 as Completed.

- [ ] **Step 4: Run full verification suite**
  - Run: `uv run ruff format --check .`
  - Run: `uv run ruff check .`
  - Run: `uv run mkdocs build --strict`
  - Run: `uv run pytest tests/test_infra.py tests/test_manifest.py tests/test_cli.py tests/test_runner.py tests/test_tui.py tests/test_metrics.py tests/test_scaffolder.py tests/test_wasm_compat.py tests/test_playground.py tests/test_plugins.py`

- [ ] **Step 5: Commit and open PR**
  - Branch: `feat/track4-wasm-playground-and-plugins`
  - Commit message: `feat(ecosystem): implement WASM Pyodide playground and curriculum plugin registry`
