# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Full Browser WebAssembly Learning Platform**: Zero-install interactive learning environment powered by Pyodide WebAssembly and Monaco code editor.
  - Complete curriculum catalog bundle generator (`src/raylings/playground_assets.py`) supporting all 81 exercises across 18 chapters (`docs/assets/playground_catalog.json`).
  - Enhanced pure-Python in-memory Ray simulation engine (`src/raylings/wasm_compat.py` & `docs/assets/playground.html`) supporting remote tasks, stateful actors, `ActorPool`, Plasma object store byte accounting, simulated `ray.data` streaming pipelines, and cluster telemetry.
  - Zero-backend client-side state persistence engine (`RaylingsStorage`) with debounced auto-save to `localStorage`, completion tracking, and backup JSON export/import.
  - Responsive 3-pane split IDE with collapsible 18-chapter syllabus accordion, Monaco editor, execution terminal, and live cluster state inspector tab.
  - Global hotkeys (`Ctrl+Enter` to run, `Alt+Left`/`Alt+Right` to navigate, `F11` for fullscreen).
  - Comprehensive unit test suite (`tests/test_playground.py`, `tests/test_wasm_compat.py`).

## [0.1.0] - 2026-08-27

### Added
- Initial project scaffolding, packaging configuration (`pyproject.toml`), and CI workflows with multi-Python test matrix (`3.10`, `3.11`, `3.12`).
- Core CLI framework (`watch`, `run`, `hint`, `list`, `progress`, `test`, `init`, `version`) and background Ray lifecycle daemon architecture for sub-50ms execution.
- Declarative curriculum manifest covering 14 chapters and 66 hands-on exercises including Ray Core, Actors, Plasma Store, Scheduling, Fault Tolerance, Clusters, Patterns, Ray Data, ML from Scratch, Ray Train, Ray Tune, Ray Serve, Observability, and KubeRay.
- Comprehensive testing harness for exercises and canonical solutions with zero-magic `# I AM NOT DONE` marker detection.
- Interactive onboarding tour engine (`src/raylings/tour.py`, `raylings tour`) with 5 guided curriculum steps, interactive stepping, `--step` jumping, non-interactive mode, and JSON export.
- Preflight diagnostics doctor command (`raylings doctor`) verifying Python runtime, Ray installation, daemon state, curriculum manifest, and CPU/RAM resources.
- Native VS Code extension (`editors/vscode`) with Exercise Explorer tree view, auto-run on save, status bar progress, and interactive welcome walkthrough.
- Complete 7-page MkDocs Material documentation suite hosted on GitHub Pages (`https://dnf0.github.io/raylings/`) with automated deployment CI/CD.
- Automated release workflow (`.github/workflows/release.yaml`) for PyPI publishing and GitHub Release generation.
- Hardened secret and virtual environment protection in `.gitignore` and infrastructure test suite.
