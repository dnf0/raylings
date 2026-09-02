# Standardized WebAssembly Learning Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize the Raylings browser learning platform to match the visual presentation, file architecture, styling, and Web Worker implementation of Kubelings.

**Architecture:** A standalone HTML5 shell (`docs/playground/index.html`) using a 3-pane responsive CSS layout (`docs/assets/playground/playground.css`), Monaco Editor AMD loader with `RaylingsStorage` client persistence (`docs/assets/playground/playground.js`), and a background Pyodide Web Worker (`docs/assets/playground/playground-worker.js`) evaluating all 81 curriculum exercises from `docs/assets/playground/playground-bundle.json`.

**Tech Stack:** Python 3.12, Pyodide v0.26 WebAssembly, Monaco Editor 0.45.0 AMD Loader, Material for MkDocs, CSS Grid / Flexbox.

## Global Constraints
- Target directory in worktree: `/Users/danielfisher/repos/raylings/.worktrees/feat-browser-learning-platform`
- Total exercises: 81 across 18 chapters
- Full viewport: 100vw × 100vh standalone application shell
- Zero backend server dependencies: 100% client-side evaluation

---

### Task 1: Static Bundle Compilation Script & Output Alignment

**Files:**
- Create: `scripts/build_playground_bundle.py`
- Modify: `src/raylings/playground_assets.py`
- Test: `tests/test_playground.py`

**Interfaces:**
- Consumes: `raylings.manifest.load_manifest()`, `exercises/**/*.py`, `solutions/**/*.py`, `hints/**/*.md`
- Produces: `docs/assets/playground/playground-bundle.json`

- [ ] **Step 1: Write failing test for standard bundle structure**

```python
def test_standard_bundle_builder_and_asset_path():
    from raylings.playground_assets import generate_playground_bundle, BUNDLE_PATH
    bundle = generate_playground_bundle()
    assert "exercises" in bundle
    assert len(bundle["exercises"]) == 81
    assert "wasm_compat_code" in bundle
```

- [ ] **Step 2: Run test to verify failure / execution**

Run: `uv run pytest tests/test_playground.py -k test_standard_bundle_builder_and_asset_path`

- [ ] **Step 3: Implement `scripts/build_playground_bundle.py` and update `src/raylings/playground_assets.py`**

```python
# scripts/build_playground_bundle.py
from raylings.playground_assets import export_bundle_to_file

if __name__ == "__main__":
    out_path = export_bundle_to_file()
    print(f"Playground bundle generated at {out_path}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_playground.py`

- [ ] **Step 5: Commit changes**

```bash
git add scripts/build_playground_bundle.py src/raylings/playground_assets.py tests/test_playground.py
git commit -m "feat: align playground bundle build script and asset output path"
```

---

### Task 2: Pyodide Background Web Worker (`playground-worker.js`)

**Files:**
- Create: `docs/assets/playground/playground-worker.js`
- Test: `tests/test_wasm_compat.py`

**Interfaces:**
- Consumes: `playground-bundle.json` (`wasm_compat_code`, exercise files)
- Produces: Web Worker postMessage protocol (`STATUS`, `RUN_RESULT`)

- [ ] **Step 1: Write failing test verifying WASM compat code embedding**

```python
def test_wasm_compat_embedding():
    from raylings.playground_assets import generate_playground_bundle
    bundle = generate_playground_bundle()
    assert "class RayWasmRuntime" in bundle["wasm_compat_code"]
```

- [ ] **Step 2: Run test to verify**

Run: `uv run pytest tests/test_playground.py -k test_wasm_compat_embedding`

- [ ] **Step 3: Implement `docs/assets/playground/playground-worker.js`**

Implement Pyodide v0.26 background worker:
- Loads `https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js`
- Mounts `/lib/raylings/wasm_compat.py` into virtual Pyodide filesystem
- Handles `INIT` and `RUN_EXERCISE` messages
- Captures `sys.stdout`/`sys.stderr` and returns `{ passed, error, output, durationMs, clusterState }`

- [ ] **Step 4: Run verification tests**

Run: `uv run pytest tests/test_wasm_compat.py tests/test_playground.py`

- [ ] **Step 5: Commit changes**

```bash
git add docs/assets/playground/playground-worker.js tests/test_playground.py
git commit -m "feat: implement Pyodide v0.26 Web Worker runtime for Raylings"
```

---

### Task 3: UI Stylesheet Alignment (`playground.css`)

**Files:**
- Create: `docs/assets/playground/playground.css`

**Interfaces:**
- Consumes: CSS variables, Monaco editor classes, HTML layout structure
- Produces: Complete responsive styling for 3-pane split layout, dark/light themes, and modals

- [ ] **Step 1: Implement `docs/assets/playground/playground.css`**

Port and adapt complete Kubelings CSS:
- CSS custom properties (`--pg-bg`, `--pg-card-bg`, `--pg-accent`, `--pg-border`, `--pg-term-bg`)
- Themes: Default Light and Slate (`[data-md-color-scheme="slate"]` and `html[data-theme="dark"]`)
- Split layout: 320px syllabus sidebar, center Monaco editor, right diagnostics pane with tab navigation
- Diff view modal, progressive hint tiers, status icons, and fullscreen mode

- [ ] **Step 2: Verify CSS formatting & file existence**

Check `docs/assets/playground/playground.css` exists and is formatted cleanly.

- [ ] **Step 3: Commit changes**

```bash
git add docs/assets/playground/playground.css
git commit -m "style: standardize playground stylesheet with 3-pane layout and theme variables"
```

---

### Task 4: Standalone Shell & Client Controller (`playground/index.html` & `playground.js`)

**Files:**
- Create: `docs/playground/index.html`
- Create: `docs/assets/playground/playground.js`

**Interfaces:**
- Consumes: `playground.css`, `playground-worker.js`, `playground-bundle.json`, Monaco CDN
- Produces: Interactive client UI, `RaylingsStorage` state persistence, hotkeys, diff modal, hints

- [ ] **Step 1: Implement `docs/playground/index.html`**

Create standalone 100vw × 100vh HTML5 shell:
- `#standalone-header` with brand badge `⚡ Raylings` + `⚡ Interactive Playground`, documentation links, and `🌓 Theme` button.
- Target container `<div id="raylings-playground" class="raylings-playground"></div>`.
- Theme toggle script synchronizing `data-theme` attribute and Monaco theme.

- [ ] **Step 2: Implement `docs/assets/playground/playground.js`**

Create controller engine:
- Monaco AMD loader from `https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs`
- `RaylingsStorage`: 300ms debounced auto-save, status tracking, stats calculation, JSON backup export/import
- 18 Chapter accordions, search & filter across 81 exercises
- Progressive hint accordion
- Side-by-side Monaco Diff modal
- Cluster state visualizer tab and terminal tab
- Keyboard shortcuts (`Ctrl+Enter`, `Alt+Left`/`Alt+Right`, `F11`)

- [ ] **Step 3: Commit changes**

```bash
git add docs/playground/index.html docs/assets/playground/playground.js
git commit -m "feat: implement standalone playground shell and Monaco UI controller"
```

---

### Task 5: MkDocs Configuration, Navigation & Strict Verification

**Files:**
- Modify: `mkdocs.yml`
- Modify: `docs/playground.md`
- Test: All test suites (`pytest`, `pyright`, `ruff`, `mkdocs build --strict`)

**Interfaces:**
- Consumes: All documentation and playground assets
- Produces: Passing test suite, clean linter, strict mkdocs build

- [ ] **Step 1: Update `mkdocs.yml` navigation**

Configure:
```yaml
nav:
  - Overview: index.md
  - Interactive Playground: playground/index.html
  - Curriculum Syllabus: syllabus.md
  ...
not_in_nav: |
  superpowers/**
  playground/**
```

- [ ] **Step 2: Run verification checks**

```bash
uv run python scripts/build_playground_bundle.py
uv run pytest tests/test_playground.py tests/test_wasm_compat.py tests/test_cli.py -q
uv run pyright src
uv run ruff check src tests
uv run mkdocs build --strict
```

- [ ] **Step 3: Commit final integration changes**

```bash
git add mkdocs.yml docs/playground.md scripts/build_playground_bundle.py
git commit -m "chore: integrate standardized playground into mkdocs navigation and build"
```
