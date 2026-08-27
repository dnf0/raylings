# ⚡ Interactive Watcher Mode

Raylings features a live file watcher that monitors your code changes and automatically re-evaluates exercises upon saving.

### 🔄 How Watcher Mode Works
- Automatically detects file modifications in `exercises/`.
- Pre-warms the background Ray daemon session for fast, non-blocking execution.
- Advances to the next exercise once your solution passes cleanly.

### ⌨️ Interactive Keyboard Controls
When running in your terminal, the watcher supports interactive single-key commands:
- **`n`** — Skip to the next exercise
- **`p`** — Return to the previous exercise
- **`r`** — Re-run the current exercise
- **`h`** — Reveal the next progressive hint
- **`q`** — Exit watcher mode

Click below to launch the watcher in an integrated terminal:

[Start Watcher](command:raylings.startWatcher)
