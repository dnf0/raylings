# Design Specification: Full Browser WebAssembly (Pyodide) Learning Platform for Raylings

- **Date:** 2026-09-02
- **Topic:** Full Browser WebAssembly Learning Platform with Zero-Backend Client State Persistence
- **Status:** Approved / Ready for Planning

---

## 1. Executive Summary

Raylings is an interactive hands-on CLI learning environment for distributed computing with Python Ray. This specification defines the architecture, data structures, and user experience for a comprehensive **in-browser WebAssembly learning platform** powered by [Pyodide](https://pyodide.org/) and a zero-dependency pure-Python Ray simulation engine.

The platform provides a 3-pane split IDE layout with a full 18-chapter, 81-exercise syllabus sidebar, Monaco editor with debounced auto-saving to `localStorage`, real-time terminal diagnostics, and a live simulated Ray cluster inspector.

---

## 2. Architectural Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Main Browser Window (/playground/)                                                     │
│                                                                                        │
│  ┌───────────────────────────┬───────────────────────────┬──────────────────────────┐  │
│  │ 📚 Curriculum Syllabus    │ ⚡ Monaco Code Editor      │ 📊 Diagnostics & Cluster │  │
│  │  • 18 Chapters / 81 Exs   │  • Action Bar & Hotkeys   │  • Tab 1: Terminal Log   │  │
│  │  • Progress Bar & Search  │  • Debounced Auto-Save    │  • Tab 2: Cluster State  │  │
│  │  • Status Badges (✓/⏳/○) │  • Progressive Hints      │    (Nodes, Plasma, CPUs, │  │
│  │  • Export / Import JSON   │  • Reference Solution Diff│     Active Actors/Tasks) │  │
│  └─────────────┬─────────────┴─────────────┬─────────────┴─────────────┬────────────┘  │
│                │                           │                           │               │
│                ▼                           ▼                           ▼               │
│  ┌───────────────────────────┐            ┌─────────────────────────────────────────┐  │
│  │ LocalStorage State Engine │            │ Pyodide WebAssembly Runtime (v0.26.4)   │  │
│  │  • Per-exercise code      │            │  • Pure-Python In-Memory Ray Core       │  │
│  │  • Completion timestamps  │◄───────────┤  • Tasks, Actors, Plasma Object Store   │  │
│  │  • Backup JSON Portability│            │  • Datasets & Cluster Metrics Interop   │  │
│  └───────────────────────────┘            └─────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Core Components

1. **Build-Time Catalog Bundle Generator (`src/raylings/playground_assets.py`)**:
   - Programmatically parses all 18 chapters and 81 exercises from `raylings.manifest.get_manifest()`.
   - Extracts starter code, solutions, hints, docstring prompts, and metadata into `docs/assets/playground_catalog.json`.
   - Verified via unit test suite (`tests/test_playground.py`).

2. **Client-Side State Engine (`RaylingsStorage`)**:
   - Manages persistence directly in browser `localStorage` without requiring any external server.
   - Debounces code changes (300ms) to ensure unsaved work is never lost on refresh.
   - Tracks exercise statuses (`not_started`, `in_progress`, `completed`), completion counts, and timestamps.
   - Supports portable JSON backup export (`raylings-progress-YYYY-MM-DD.json`) and restoration import.

3. **Pure-Python Pyodide WebAssembly Simulation Engine**:
   - Runs client-side Python 3.12 in WebAssembly via Pyodide.
   - Simulates core Ray semantics in pure Python:
     - `@ray.remote` tasks, asynchronous futures (`ObjectRef`), `ray.get()`, `ray.wait()`, and `ray.put()`.
     - `@ray.remote` stateful Actor classes, method dispatching, and `ActorPool`.
     - `WasmPlasmaStore` in-memory object store with byte accounting and zero-copy semantics.
     - `ray.data` streaming dataset primitives (`map`, `filter`, `map_batches`, `take_all`).
     - Cluster telemetry hooks updating the Cluster State Inspector.

---

## 3. Detailed Technical Design

### 3.1 Data Schema: Exercise Catalog (`playground_catalog.json`)

```typescript
interface PlaygroundCatalogExercise {
  chapter: number;              // 1..18
  chapter_name: string;         // e.g. "01_basics"
  chapter_title: string;        // e.g. "Ray Core Foundations"
  name: string;                 // e.g. "basics01"
  title: string;                // e.g. "Ray Init & First Remote Task"
  path: string;                 // e.g. "exercises/01_basics/basics01.py"
  prompt: string;               // Exercise docstring description
  hint: string;                 // Hints string
  code: string;                 // Exercise starter code
  solution: string;             // Reference solution code
}
```

### 3.2 State Persistence Model: `RaylingsStorage`

```typescript
interface RaylingsStoredExercise {
  status: "not_started" | "in_progress" | "completed";
  userCode: string;
  hintVisible: boolean;
  lastEvaluatedAt?: string;     // ISO8601 string
  passedAt?: string;            // ISO8601 string
}

interface RaylingsWorkspaceState {
  version: 1;
  lastActiveExerciseIndex: number;
  exercises: Record<string, RaylingsStoredExercise>;
}
```

#### Key State Operations
- `saveExerciseCode(name: string, code: string)`: Debounced update to localStorage.
- `markExerciseCompleted(name: string)`: Sets status to `completed`, records timestamp, and refreshes progress stats.
- `resetExercise(name: string)`: Restores starter code from the catalog bundle.
- `resetAll()`: Clears stored workspace state after confirmation modal.
- `exportState()`: Triggers browser download of `raylings-progress-YYYY-MM-DD.json`.
- `importState(jsonData: string)`: Validates schema and merges/replaces workspace state.

---

## 4. User Interface & Interactions

### 4.1 3-Pane Split Layout
1. **Left Sidebar (300px width)**:
   - Overall progress bar with completed count (e.g., `14 / 81 Completed (17%)`).
   - Quick action buttons: `Export JSON`, `Import JSON`, `Reset All`.
   - Real-time search filter input and status dropdown (`All`, `To Do`, `Done`).
   - 18 collapsible chapter accordions with completion status indicators (e.g., `01. Ray Core Foundations (6/6 ✓)`).
   - Exercise list items with status icons (`✓` completed, `⏳` in progress, `○` not started).

2. **Center Workspace**:
   - Header with active chapter, exercise title, file path, and `⛶ Fullscreen` toggle.
   - Action Toolbar:
     - `▶ Run Solution` (`Ctrl+Enter` / `Cmd+Enter`)
     - `💡 Hint` (`H`)
     - `🔍 Solution`
     - `↺ Reset`
     - `Next →` (`Alt+Right`) / `← Prev` (`Alt+Left`)
   - Monaco Editor instance with Python syntax highlighting and auto-formatting.
   - Collapsible hint drawer and diff viewer.

3. **Right Inspector Pane (360px width)**:
   - **Tab 1 (Terminal)**: Formatted console output with ANSI coloring, evaluation execution duration, and traceback diagnostics.
   - **Tab 2 (Cluster State)**:
     - Virtual Node Status (`● ALIVE 127.0.0.1`)
     - Allocated Virtual CPUs (`4 Cores`)
     - Plasma Object Store Gauge (`Used Bytes / 100 MB`, `Object Count`)
     - Active Actors & Completed Task counters.

### 4.2 Keyboard Shortcuts
- `Ctrl+Enter` / `Cmd+Enter`: Run and verify active exercise.
- `Alt+Right`: Navigate to next exercise.
- `Alt+Left`: Navigate to previous exercise.
- `H`: Toggle hint panel.
- `F11` / `Esc`: Toggle fullscreen mode.

---

## 5. Verification & Testing Plan

1. **Bundle Generator Integrity (`tests/test_playground.py`)**:
   - Verify that all 18 chapters and 81 exercises are parsed without omissions.
   - Verify that starter code and reference solutions are valid and non-empty.
   - Ensure generated JSON catalog matches expected schema.
2. **In-Memory Simulation Integrity**:
   - Validate that the pure-Python simulation module passes `verify()` for Core tasks, actors, and object store exercises.
3. **MkDocs Build Verification**:
   - Run `uv run mkdocs build --strict` to verify clean build with zero broken links or asset errors.
4. **Code Quality**:
   - Run `uv run ruff check .` and `uv run pyright src` for static analysis and linting compliance.
