# Design Spec: Raylings Documentation & Pedagogical Exercise Alignment (Kubelings Standard)

**Date**: 2026-08-28  
**Status**: Approved  
**Target Version**: `v0.5.1` / `v0.6.0`  

---

## 1. Executive Summary

Raylings has expanded to 18 chapters and 81 exercises spanning Ray Core, Plasma memory, actor state, placement groups, fault tolerance, Ray Data, PyTorch DDP/Ray Train, Ray Tune, Ray Serve, KubeRay, vLLM/LLMs, DeepSpeed/FSDP, Multimodal/Vector ETL, and pluggable Quantitative Finance.

To match the gold standard set by **Kubelings**:
1. **README & Documentation**: Overhaul `README.md` and `docs/` (`index.md`, `syllabus.md`, `getting-started.md`, `onboarding-guide.md`, etc.) with consistent branding, badges, architecture diagrams, pedagogical philosophy, complete 18-chapter syllabus tables, VS Code extension install guides, and ecosystem cross-links.
2. **Pedagogical Exercise Expansion**: Upgrade every exercise across all 18 chapters (`exercises/**/*.py`) with:
   - Structured header docstrings: `Exercise:`, `Topic:`, `Context & Why:`, `Instructions:`.
   - Inline directives: Pairing every `# TODO:` with a `# WHY:` comment explaining the distributed systems rationale, memory dynamics, scheduling trade-offs, or Ray architecture mechanics.

---

## 2. Architecture & Documentation Design

### 2.1 README.md Alignment
- **Hero & Badges**:
  - `[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://dnf0.github.io/raylings/)`
  - `[![CI](https://github.com/dnf0/raylings/actions/workflows/ci.yml/badge.svg)](https://github.com/dnf0/raylings/actions)`
  - `[![KubeRay CI](https://github.com/dnf0/raylings/actions/workflows/kuberay-e2e.yml/badge.svg)](https://github.com/dnf0/raylings/actions)`
  - `[![Playground](https://img.shields.io/badge/Playground-⚡%20Try%20in%20Browser-blueviolet)](https://dnf0.github.io/raylings/playground/)`
  - `[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)`
  - `[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)`
  - `[![Type checker: pyright](https://img.shields.io/badge/types-pyright-green.svg)](https://github.com/microsoft/pyright)`
  - `[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)`
- **Pedagogical Philosophy**:
  - Test-driven micro-learning with active debugging.
  - Sub-50ms instant feedback loop with hotkeys.
  - Dual-mode learning (Offline In-Memory WASM vs Live Multi-Node Cluster).
  - Progressive multi-tier hints.
- **Architecture Diagram**:
  - ASCII box diagram depicting Terminal -> Typer CLI -> File Watcher -> Rich UI -> Curriculum Manifest (18 Chapters / 81 Exercises) -> Runner -> Offline WASM Simulator OR Live Cluster Adapter.
- **Interactive Tooling Suite**:
  - Document all subcommands: `tour`, `watch`, `tui`, `top`, `doctor`, `new`, `plugins`, `daemon`, `verify`, `test`, `hint`, `list`.
- **VS Code & Cursor Extension**:
  - Feature list and installation instructions for CLI (`code --install-extension dist/raylings-vscode.vsix`) and Editor UI.
- **Full 18-Chapter Curriculum Syllabus Table**:
  - Detailed rows for Chapters 01 to 18 listing all 81 exercises and topic summaries.
- **The `*lings` Ecosystem**:
  - Cross-references to Kubelings, Terralings, Spanglings, and Raylings.

### 2.2 MkDocs Documentation Site Sync
- `docs/index.md`: Synchronize hero, badges, try-in-browser callout, and feature matrix.
- `docs/syllabus.md`: Expand to all 18 chapters with full exercise breakdowns and topic descriptions.
- `docs/getting-started.md`: Update with browser playground, uvx workflow, and CLI overview.
- `docs/onboarding-guide.md`: Update with 18-chapter overview and complete hotkey matrix.

---

## 3. Curriculum Exercise Pedagogical Standard

Every exercise file in `exercises/**/*.py` will follow this strict template:

```python
"""
Exercise: exercises/<chapter_dir>/<exercise_file>.py
Topic: <Descriptive Topic Name>

Context & Why:
<2-4 comprehensive paragraphs explaining:
 1. The core distributed computing concept and Ray's internal design (GCS, Raylets, Plasma store, object refs, actors, placement groups, DDP sync, etc.).
 2. Why this pattern is chosen in production distributed AI systems.
 3. Common pitfalls, anti-patterns, or failure modes (e.g., nested ray.get, worker OOM, object pinning leaks, scheduling bottlenecks).>

Instructions:
1. <Actionable step 1>
2. <Actionable step 2>
"""

import ray

# ...

# TODO: <Specific task instruction>
# WHY: <Deep architectural rationale explaining why this setting/call/decorator is required>
<code with placeholder>
```

---

## 4. Execution & Verification Plan

1. **Phase 1: Update Documentation & README**:
   - Overhaul `README.md`.
   - Update `docs/index.md`, `docs/syllabus.md`, `docs/getting-started.md`, and `docs/onboarding-guide.md`.
   - Rebuild playground catalog via `uv run python -c "from raylings.playground_assets import build_playground_catalog; build_playground_catalog()"` to ensure web playground catalog is 100% in sync.
2. **Phase 2: Pedagogical Overhaul of Exercises (Chapters 1 to 18)**:
   - Systematically update all 81 exercise files in `exercises/` with comprehensive `Context & Why:`, `# TODO:`, and `# WHY:` annotations.
3. **Phase 3: Verification & Test Suite**:
   - Run `uv run pytest` to ensure all 117+ unit tests pass.
   - Run `raylings test` to ensure all solutions pass verification.
   - Run `uv run mkdocs build --strict` to ensure 0 markdown warnings or broken links.
   - Run `uv run ruff check .` and `uv run ruff format --check .`.
   - Commit changes cleanly and merge.
