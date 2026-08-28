---
title: Interactive WASM Playground
description: Run and solve Raylings exercises directly in your browser using Pyodide WebAssembly without installing Python or Ray locally.
---

# ⚡ Interactive WebAssembly Playground

Welcome to the **Raylings Interactive Playground**! You can solve, execute, and verify Raylings distributed AI and distributed computing exercises **directly in your browser** powered by [Pyodide](https://pyodide.org/) WebAssembly and our zero-dependency pure-Python Ray simulation runtime.

<div style="position: relative; width: 100%; height: 820px; border-radius: 8px; overflow: hidden; border: 1px solid var(--md-default-fg-color--lightest); margin: 1.5rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
  <iframe 
    src="../assets/playground.html" 
    style="width: 100%; height: 100%; border: none;"
    title="Raylings WASM Interactive Playground"
    allow="clipboard-read; clipboard-write">
  </iframe>
</div>

---

## 🚀 Key Features

- **Zero Local Setup**: Run Python Ray tasks, actors, object store calls, and data streaming pipelines inside WebAssembly with 0 local dependencies.
- **Monaco Code Editor**: VS Code-powered browser code editing with autocomplete, syntax highlighting, and keyboard shortcuts (`Ctrl+Enter` or `Cmd+Enter` to run).
- **Simulated Cluster State**: Monitor virtual worker nodes, virtual CPU allocations, Plasma object store usage gauges, and active actor pools in real time.
- **Step-by-Step Curriculum**: Interactive sidebar with all 78 exercises across 17 chapters, live progress checkmarks, hints, and reference solutions.
- **Offline Capable**: Works entirely client-side once assets and Pyodide runtime are cached.

---

## 🛠️ Offline & Self-Hosted Usage

You can also run the playground locally using the Raylings CLI or open the standalone HTML file in your browser:

```bash
# Export the complete exercise catalog bundle
python -c "from raylings.playground_assets import export_playground_bundle; export_playground_bundle('docs/assets/playground_catalog.json')"

# Preview with MkDocs local server
uv run mkdocs serve
```
