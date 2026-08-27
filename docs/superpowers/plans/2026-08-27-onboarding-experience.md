# Raylings Onboarding Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cohesive, 5-step interactive onboarding tour engine (`raylings tour`), diagnostics utility (`raylings doctor`), native VS Code walkthrough, and onboarding documentation for Raylings learners.

**Architecture:** 
- A modular `TourEngine` in `src/raylings/tour.py` provides step definition, formatted rich UI rendering, interactive key navigation, non-interactive execution, and JSON payload export.
- CLI registration in `src/raylings/cli.py` exposes `raylings tour` (with `--step`, `--non-interactive`, `--json` flags) and `raylings doctor` for preflight diagnostics.
- VS Code extension `editors/vscode` contributes declarative walkthroughs in `package.json` with dedicated markdown step assets and command bridge integration (`raylings.startTour`, `raylings.runDoctor`).
- Complete onboarding reference in `docs/ONBOARDING.md` and updated `README.md`.

**Tech Stack:** Python 3.10+, Typer, Rich, Ray, TypeScript, VS Code Extension API.

---

### Task 1: CLI Tour Engine (`src/raylings/tour.py`) & Tests

**Files:**
- Create: `src/raylings/tour.py`
- Create: `tests/test_tour.py`
- Modify: `src/raylings/__init__.py`

- [x] **Step 1: Write failing tests for TourEngine and TourStep**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/raylings/tour.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

```bash
git add src/raylings/tour.py tests/test_tour.py
git commit --no-gpg-sign -m "feat(tour): implement TourEngine and step definitions"
```

---

### Task 2: CLI Command Registration & Doctor Diagnostics (`src/raylings/cli.py`)

**Files:**
- Modify: `src/raylings/cli.py`
- Modify: `tests/test_cli.py`

- [x] **Step 1: Write failing tests for `raylings tour` and `raylings doctor`**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `tour` and `doctor` commands in `src/raylings/cli.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

```bash
git add src/raylings/cli.py tests/test_cli.py
git commit --no-gpg-sign -m "feat(cli): register raylings tour and raylings doctor commands"
```

---

### Task 3: VS Code Extension Walkthrough & Command Bridge

**Files:**
- Create: `editors/vscode/walkthroughs/welcome.md`
- Create: `editors/vscode/walkthroughs/environment.md`
- Create: `editors/vscode/walkthroughs/first-exercise.md`
- Create: `editors/vscode/walkthroughs/watcher.md`
- Create: `editors/vscode/walkthroughs/tree-view.md`
- Modify: `editors/vscode/package.json`
- Modify: `editors/vscode/src/commands.ts`
- Modify: `editors/vscode/src/extension.ts`

- [x] **Step 1: Create markdown walkthrough assets in `editors/vscode/walkthroughs/`**
- [x] **Step 2: Register `contributes.walkthroughs` in `editors/vscode/package.json` and commands `raylings.startTour` & `raylings.runDoctor`**
- [x] **Step 3: Implement command handlers in `editors/vscode/src/commands.ts`**
- [x] **Step 4: Build extension with `npm run compile` in `editors/vscode`**
- [x] **Step 5: Commit**

```bash
git add editors/vscode/
git commit --no-gpg-sign -m "feat(vscode): add interactive onboarding walkthrough and diagnostics command"
```

---

### Task 4: Comprehensive Onboarding Documentation & Verification

**Files:**
- Create: `docs/ONBOARDING.md`
- Modify: `README.md`

- [ ] **Step 1: Write comprehensive `docs/ONBOARDING.md`**
- [ ] **Step 2: Update `README.md` with links and quickstart commands (`raylings tour`, `raylings doctor`)**
- [ ] **Step 3: Run full verification suite (`uv run pytest -m "not heavy" -v`, `uv run ruff check src tests`)**
- [ ] **Step 4: Commit**

```bash
git add docs/ONBOARDING.md README.md
git commit --no-gpg-sign -m "docs: add comprehensive onboarding guide and update README"
```
