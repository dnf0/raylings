# Design Spec: Streamline & Modernize README.md

**Date:** 2026-09-02
**Author:** Raylings Engineering Team

## 1. Objective
Modernize and streamline `README.md` to adhere to [Make a README](https://www.makeareadme.com/) best practices, replace legacy ASCII diagrams with a clean high-level Mermaid flowchart, document all CLI commands (including `daemon`, `doctor`, `tour`, `top`), and directly link all 18 chapters to their published online documentation guides.

---

## 2. Requirements & Standards

1. **Conciseness & High-Density Layout**:
   - Avoid verbose repetition; use clean markdown tables and bulleted lists.
   - Maintain clear headings and prominent action links (Playground, Tour, Documentation).

2. **Mermaid Architecture Flowchart**:
   - Replace the legacy ASCII box diagram with a single standard Mermaid flowchart (`flowchart TD`) representing CLI/TUI, Watcher, Curriculum Engine, Runner, In-Memory WASM Engine, and Live Ray Cluster / KubeRay.
   - Attach a concise 3-bullet walkthrough explaining core architectural boundaries.

3. **Curriculum Table with Direct Guide Links**:
   - Update the 18-chapter table to link each title to its corresponding published documentation guide (`https://dnf0.github.io/raylings/guides/<slug>/`).
   - Include clear exercise ranges and counts (total 81 exercises).

4. **CLI Command Reference Table**:
   - Compact table documenting all commands: `tour`, `doctor`, `init`, `tui`, `watch`, `daemon`, `top`, `run`, `hint`, `new`, `plugins`, `test`.
   - Compact table for TUI and Watcher hotkeys.

5. **Tooling & Installation**:
   - Prioritize `uv` and `uvx` zero-install one-liners (`uvx raylings tour`, `uvx raylings init`, etc.).
   - Provide standard `pip` / editable clone instructions.

6. **VS Code & Cursor Extension**:
   - Feature summary and 1-line installation commands.

7. **Ecosystem & License**:
   - Links to Kubelings, Terralings, Spanglings, CONTRIBUTING.md, and Apache-2.0.

---

## 3. Section-by-Section Plan

1. **Title, Badges & Tagline**:
   - Badges: Docs, VS Code Marketplace, CI, Playground, Python 3.10+, Ruff, Pyright, Apache-2.0.
   - Hero banner / terminal demo link.
   - 1-sentence tagline.

2. **Why Raylings?**:
   - 3 bullet points: Active Debugging, Instant Feedback (<50ms watcher), Dual Execution (WASM vs Live Cluster).

3. **Architecture**:
   - High-level Mermaid flowchart (`flowchart TD`).
   - 3-bullet walkthrough.

4. **Quickstart & Try in Browser**:
   - WebAssembly playground link.
   - `uvx` zero-install workflow.
   - Local clone (`uv venv` / `pip`).

5. **CLI & TUI Reference**:
   - Command table with name, syntax, description.
   - Hotkey table for TUI & Watcher.

6. **VS Code & Cursor Extension**:
   - Overview of tree view, live diagnostics, hints, and diffing.
   - Marketplace and CLI installation commands.

7. **Curriculum Syllabus**:
   - 18 chapters with direct URLs to `https://dnf0.github.io/raylings/guides/XX-name/`.

8. **Ecosystem & Contributing**:
   - Other `*lings` repositories.
   - Contributing and License.

---

## 4. Verification

- `uv run mkdocs build --strict` ensures documentation links and build integrity.
- `uv run pytest tests/test_guide_diagrams.py` ensures guide diagrams remain intact.
- Check rendered `README.md` for formatting and link validity.
