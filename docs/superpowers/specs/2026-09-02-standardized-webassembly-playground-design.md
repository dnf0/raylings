# Standardized WebAssembly Learning Platform Design

- **Date:** 2026-09-02
- **Topic:** Raylings WebAssembly Playground UI & Architecture Standardization with Kubelings
- **Status:** Approved

## 1. Executive Summary

This design standardizes the client-side WebAssembly learning platform for **Raylings** to match the visual presentation, file organization, styling, and background Web Worker architecture of **Kubelings**.

The platform operates 100% client-side in the browser via Pyodide (Python 3.12 WebAssembly) and Monaco Editor, requiring zero backend server infrastructure, while delivering a 3-pane split-layout interactive IDE for all 81 curriculum exercises across 18 chapters.

---

## 2. Architectural Blueprint & File Layout

```
docs/
├── playground/
│   └── index.html               # Standalone 100vw × 100vh app shell with top navbar
└── assets/
    └── playground/
        ├── playground.css        # Responsive 3-pane CSS grid with dark/light themes
        ├── playground.js         # Client-side controller, Monaco AMD loader, state engine
        ├── playground-worker.js  # Pyodide v0.26 background Web Worker & Ray WASM runtime
        └── playground-bundle.json# Compiled static catalog of 81 exercises & reference solutions
scripts/
└── build_playground_bundle.py   # Exercise & validator bundle compilation script
mkdocs.yml                        # Navigation config linking to playground/index.html
```

---

## 3. Core Components

### 3.1. Standalone Web App Shell (`docs/playground/index.html`)
- Standalone HTML5 document with zero MkDocs chrome overhead.
- Header bar featuring:
  - Brand identity: `⚡ Raylings` with badge `⚡ Interactive Playground`.
  - Quick navigation links: `📖 Documentation`, `📚 Syllabus`, GitHub repository link.
  - Dark / light theme toggle (`🌓 Theme`) synchronizing with Monaco Editor.
- Root mount point: `<div id="raylings-playground" class="raylings-playground"></div>`.

### 3.2. UI Stylesheet (`docs/assets/playground/playground.css`)
- CSS custom properties (`--pg-bg`, `--pg-card-bg`, `--pg-accent`, `--pg-border`, `--pg-term-bg`).
- Full support for `data-theme="dark"` / `data-theme="light"` and MkDocs `data-md-color-scheme="slate"`.
- 3-pane responsive layout:
  - Collapsible 320px syllabus sidebar (left).
  - Monaco editor with breadcrumbs and action bar (center).
  - Diagnostic split pane (right) with tabs for Pyodide Terminal and Simulated Ray Cluster Inspector.
- Side-by-side modal styling for Monaco Diff Editor.

### 3.3. Client-Side Controller & State Engine (`docs/assets/playground/playground.js`)
- Loads Monaco Editor via CDN AMD loader (`https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs`).
- **`RaylingsStorage`**:
  - LocalStorage key: `raylings_learning_state_v1`.
  - Auto-saves user code edits with 300ms debounce.
  - Tracks exercise completion statuses (`not_started`, `in_progress`, `completed`), timestamps, and revealed hint tiers.
  - Backup & restore via JSON file import/export (`raylings-progress-YYYY-MM-DD.json`).
- Keyboard shortcuts:
  - `Ctrl + Enter` / `Cmd + Enter`: Run current exercise.
  - `Alt + Left` / `Alt + Right`: Navigate between exercises.
  - `F11`: Toggle fullscreen editor mode.
- Progressive Hints: Multi-tier accordion revealing hints without spoiling the full solution.
- Diff Viewer: Opens Monaco Diff Editor side-by-side comparison between user code and reference solution.

### 3.4. Pyodide WebAssembly Background Worker (`docs/assets/playground/playground-worker.js`)
- Background Web Worker running Pyodide v0.26 (`https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js`).
- Pre-loads standard library and pure-Python modules.
- Mounts `/lib/raylings/wasm_compat.py` into the virtual Pyodide filesystem to provide an in-memory Ray simulation engine (`@ray.remote`, actor pools, Plasma object store, `ray.wait`, `ray.data`).
- Captures `sys.stdout` and `sys.stderr`, returning execution results and millisecond timing to the UI thread via `postMessage`.

### 3.5. Bundle Compiler (`scripts/build_playground_bundle.py`)
- Python script extracting all 81 exercises, starter code, reference solutions, and hint metadata.
- Emits `docs/assets/playground/playground-bundle.json`.
- Tested and verifiable via `tests/test_playground.py`.

### 3.6. Documentation & Deployment Configuration
- `mkdocs.yml`: Configures `Interactive Playground: playground/index.html` in navigation and excludes `playground/**` from standard markdown nav wrapping.
- `.github/workflows/docs.yml`: Automated GitHub Actions workflow deploying to GitHub Pages on push to `main`.

---

## 4. Verification & Testing Strategy
- Unit tests verifying the static bundle generator: `tests/test_playground.py`.
- Unit tests verifying the WASM compatibility engine: `tests/test_wasm_compat.py`.
- Strict MkDocs documentation build: `uv run mkdocs build --strict`.
- Static typing & linter checks: `uv run pyright src` and `uv run ruff check src tests`.
