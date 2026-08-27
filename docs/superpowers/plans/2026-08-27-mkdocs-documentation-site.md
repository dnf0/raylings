# MkDocs Material Documentation Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a documentation site for Raylings powered by MkDocs Material, hosted on GitHub Pages (`https://dnf0.github.io/raylings/`), complete with dark/light theme, search, syntax highlighting, comprehensive guides, and automated GitHub Actions deployment.

**Architecture:** A static documentation website configured via `mkdocs.yml` using `mkdocs-material`, structured into modular markdown pages in `docs/` (Overview, Getting Started, Onboarding Guide, Curriculum Syllabus, CLI Reference, Contributing, Troubleshooting), deployed automatically via GitHub Pages workflow `.github/workflows/docs.yml`.

**Tech Stack:** MkDocs Material, Python 3.10+, PyMdown Extensions, GitHub Actions, UV, GitHub Pages.

---

### File Structure Map

```
raylings/
├── mkdocs.yml
├── .github/
│   └── workflows/
│       └── docs.yml
├── pyproject.toml
├── README.md
└── docs/
    ├── index.md
    ├── getting-started.md
    ├── onboarding-guide.md
    ├── syllabus.md
    ├── cli-reference.md
    ├── troubleshooting.md
    └── contributing.md
```

---

### Task 1: MkDocs Configuration (`mkdocs.yml`) & Pyproject Metadata

**Files:**
- Create: `mkdocs.yml`
- Modify: `pyproject.toml`

- [x] **Step 1: Create `mkdocs.yml` with Material theme and palette configuration**

```yaml
site_name: Raylings
site_description: An interactive, hands-on CLI learning environment for Python Ray.
site_url: https://dnf0.github.io/raylings/
site_author: Raylings Contributors
repo_name: dnf0/raylings
repo_url: https://github.com/dnf0/raylings

theme:
  name: material
  palette:
    # Palette toggle for dark mode
    - scheme: slate
      primary: cyan
      accent: deep purple
      toggle:
        icon: material/weather-night
        name: Switch to light mode
    # Palette toggle for light mode
    - scheme: default
      primary: cyan
      accent: deep purple
      toggle:
        icon: material/weather-sunny
        name: Switch to dark mode
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - tables
  - attr_list

nav:
  - Overview: index.md
  - Getting Started: getting-started.md
  - Onboarding Guide: onboarding-guide.md
  - Curriculum Syllabus: syllabus.md
  - CLI Reference: cli-reference.md
  - Troubleshooting: troubleshooting.md
  - Contributing: contributing.md

not_in_nav: |
  superpowers/**
  ONBOARDING.md
```

- [x] **Step 2: Update `pyproject.toml` with `docs` optional dependencies and documentation URL**

Add `docs` dependency group:
```toml
[project.optional-dependencies]
docs = [
    "mkdocs-material>=9.5.0",
]
```
Add `Documentation` to `[project.urls]`:
```toml
Documentation = "https://dnf0.github.io/raylings/"
```

- [x] **Step 3: Commit Task 1**

```bash
git add mkdocs.yml pyproject.toml
git commit -m "feat(docs): add mkdocs configuration and docs dependencies" --no-gpg-sign
```

---

### Task 2: Author Documentation Pages

**Files:**
- Create: `docs/index.md`
- Create: `docs/getting-started.md`
- Create: `docs/onboarding-guide.md`
- Create: `docs/syllabus.md`
- Create: `docs/cli-reference.md`
- Create: `docs/troubleshooting.md`
- Create: `docs/contributing.md`

- [x] **Step 1: Author `docs/index.md`**
Overview of Raylings, motivation, core features, interactive GIF/demo placeholders, quick architecture diagram.

- [x] **Step 2: Author `docs/getting-started.md`**
Installation via `uvx`, `pipx`, `pip`, and editable git clone, initializing workspaces with `raylings init`, and running `raylings doctor`.

- [x] **Step 3: Author `docs/onboarding-guide.md`**
Comprehensive interactive onboarding guide covering the 5-step tour (`raylings tour`), watcher hotkeys, VS Code extension walkthrough, and learning workflows.

- [x] **Step 4: Author `docs/syllabus.md`**
Complete 14-chapter curriculum map (66 exercises) with topic breakdowns, exercise objectives, prerequisites, and concepts covered.

- [x] **Step 5: Author `docs/cli-reference.md`**
Comprehensive CLI reference documenting every subcommand (`init`, `doctor`, `tour`, `watch`, `run`, `test`, `hint`, `list`, `progress`, `daemon`, `version`), flags, and JSON payloads.

- [x] **Step 6: Author `docs/troubleshooting.md`**
Detailed recipes for Ray daemon issues, port conflicts, Plasma OOM, macOS/Linux file descriptor limits, and Python 3.13 compatibility workarounds.

- [x] **Step 7: Author `docs/contributing.md`**
Developer setup, running tests, ruff linting, curriculum authoring guidelines, and PR workflow.

- [x] **Step 8: Commit Task 2**

```bash
git add docs/*.md
git commit -m "docs: author comprehensive documentation site pages" --no-gpg-sign
```

---

### Task 3: GitHub Actions Deployment Workflow & Strict Build Verification

**Files:**
- Create: `.github/workflows/docs.yml`

- [x] **Step 1: Create `.github/workflows/docs.yml`**

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - "docs/**"
      - "mkdocs.yml"
      - "pyproject.toml"
      - ".github/workflows/docs.yml"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Install dependencies
        run: |
          uv pip install --system mkdocs-material

      - name: Deploy to GitHub Pages
        run: |
          mkdocs gh-deploy --force
```

- [x] **Step 2: Test strict MkDocs build locally**

Run: `uvx --from mkdocs-material mkdocs build --strict`
Expected: Documentation builds cleanly into `site/` with zero warnings and exit code 0.

- [x] **Step 3: Clean up `site/` build artifacts & ensure `.gitignore` ignores `site/`**

Verify `.gitignore` contains `site/`.

- [x] **Step 4: Commit Task 3**

```bash
git add .github/workflows/docs.yml .gitignore
git commit -m "ci(docs): add github pages deployment workflow" --no-gpg-sign
```

---

### Task 4: Integration, Verification & PR

**Files:**
- Modify: `README.md`

- [x] **Step 1: Update `README.md` with documentation site badges and links**
Add `[Documentation](https://dnf0.github.io/raylings/)` badge and links to the hosted documentation site.

- [x] **Step 2: Run full verification suite**

Run:
1. `uvx --with mkdocs-material mkdocs build --strict`
2. `uv run pytest -m "not heavy" -v`
3. `uv run ruff check src tests`
4. `uv run ruff format --check src tests`
5. `uvx --from graphifyy graphify update .`

- [x] **Step 3: Commit Task 4**

```bash
git add README.md
git commit -m "docs: add documentation site links and badges to README" --no-gpg-sign
```

- [x] **Step 4: Push branch and open Pull Request**
Push `feat/mkdocs-documentation-site` and create PR via `gh pr create`.
