# Update and Modernize README.md Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize and streamline `README.md` to follow [Make a README](https://www.makeareadme.com/) standards with a clean Mermaid architecture diagram, CLI/TUI tables, and direct links to all 18 published chapter guides.

**Architecture:** Replace legacy ASCII diagrams with a clean, high-level Mermaid flowchart. Consolidate CLI and TUI documentation into high-density tables. Deep-link every chapter in the 81-exercise syllabus to its corresponding online guide.

**Tech Stack:** GitHub Flavored Markdown, Mermaid.js, MkDocs.

## Global Constraints
- Preserve all active badge links and visual assets (`docs/assets/demo.svg`).
- Adhere to Make a README recommendations: concise, informative, actionable.
- Ensure all chapter guide links point to valid GitHub Pages routes (`https://dnf0.github.io/raylings/guides/<slug>/`).
- Keep tone pedagogical, developer-friendly, and concise.

---

### Task 1: Update `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write modernized `README.md`**
  - Section 1: Title, Badges (Docs, VS Code Marketplace, CI, Playground, Python 3.10+, Ruff, Pyright, Apache-2.0), Tagline, Terminal Demo image.
  - Section 2: Why Raylings? (Active Debugging, Sub-50ms Watcher, Dual Execution WASM/Live Cluster).
  - Section 3: Architecture (Clean Mermaid flowchart `flowchart TD` + 3-bullet walkthrough).
  - Section 4: Quickstart & Try in Browser (Playground link, `uvx` zero-install commands, local git clone with `uv`).
  - Section 5: CLI & TUI Command Reference (Table of all commands including `daemon`, `doctor`, `tour`, `top`, `tui`, `watch`, etc., plus hotkeys cheatsheet).
  - Section 6: VS Code & Cursor Extension (Key features, Marketplace link, CLI install command).
  - Section 7: Curriculum Syllabus (18 chapters with direct links to published online guides).
  - Section 8: `*lings` Ecosystem, Contributing & License.

### Task 2: Verification

**Files:**
- Test: `README.md`
- Verify: `uv run mkdocs build --strict`
- Verify: `uv run pytest tests/test_guide_diagrams.py`

- [ ] **Step 1: Verify MkDocs Build & Link Validation**
  - Run `uv run mkdocs build --strict` to ensure no documentation regressions.
- [ ] **Step 2: Verify Test Suite**
  - Run `uv run pytest tests/test_guide_diagrams.py` and `uv run pytest -m "not heavy"`
- [ ] **Step 3: Commit and Finish**
  - Commit with `docs: modernize and streamline README with mermaid architecture and guide deep-links`
