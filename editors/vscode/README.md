# Raylings for VS Code & Cursor ⚡

An interactive visual companion for **Raylings**, the interactive curriculum designed to take engineers from zero to distributed systems master with Python Ray.

---

## ✨ Features

- **⚡ Activity Bar Exercise Explorer**: Browse all 18 curriculum chapters and 81 exercises with real-time completion checkmarks (`✓`), pending badges (`⏳`), and exercise metadata.
- **📊 Real-Time Status Bar Tracker**: View current chapter completion percentages and jump straight to your next incomplete exercise in one click.
- **🚀 Auto-Run on Save**: Edit an exercise file in `exercises/**/*.py`, save, and get instant feedback in the Raylings output pane.
- **💡 Progressive Hint Reveal**: Browse multi-tier progressive hints directly within VS Code without spoiling solutions.
- **📖 Side-by-Side Reference Solutions**: Open canonical reference solutions alongside your active exercise editor for quick comparison.
- **🖥️ Integrated Watcher Terminal**: Launch the full interactive Raylings terminal watcher with a single command.

---

## 📦 Getting Started

1. **Install Raylings CLI** (via `uv` or `pip`):
   ```bash
   # Via uv (recommended)
   uv tool install raylings
   # Or via pipx
   pipx install raylings
   ```

2. **Initialize Workspace**:
   Run the command **`Raylings: Initialize Exercises Workspace`** from the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) or run:
   ```bash
   raylings init
   ```

3. **Open the Raylings Sidebar**:
   Click the **⚡ Raylings** icon on the Activity Bar to view all chapters and select your first exercise!

---

## 🛠️ Extension Commands

| Command | Identifier | Description |
| :--- | :--- | :--- |
| **Open Next Exercise** | `raylings.openNextExercise` | Jumps to the current incomplete exercise. |
| **Run Current Exercise** | `raylings.runCurrent` | Executes the active exercise file. |
| **Show Exercise Hint** | `raylings.showHint` | Displays multi-level progressive hints. |
| **View Reference Solution** | `raylings.viewSolution` | Opens matching solution in side-by-side editor. |
| **Start Watcher in Terminal** | `raylings.startWatcher` | Spawns `raylings watch` in integrated terminal. |
| **Initialize Workspace** | `raylings.initWorkspace` | Extracts exercises into current workspace. |
| **Sync Progress** | `raylings.syncProgress` | Refreshes tree explorer and status bar counters. |

---

## ⚙️ Configuration

| Setting | Default | Description |
| :--- | :--- | :--- |
| `raylings.executablePath` | `"raylings"` | Path to the `raylings` CLI binary (e.g. `raylings`, `uv run raylings`). |
| `raylings.autoRunOnSave` | `true` | Automatically runs exercise validation when saving files in `exercises/`. |
| `raylings.showStatusBar` | `true` | Enables or disables the Raylings status bar item. |

---

## 📄 License

Apache 2.0. Built with ❤️ for the Ray and Python distributed systems community.
