# CLI Reference Manual ⌨️

Complete command-line interface reference for the `raylings` binary.

---

## 🧭 Global Overview

```bash
raylings [OPTIONS] COMMAND [ARGS]...
```

### Global Options

| Option | Flag | Description |
| :--- | :--- | :--- |
| `--version` | `-v` | Display the Raylings branding banner and current version, then exit. |
| `--help` | `-h` | Display global help message and command list, then exit. |

---

## ⚡ Commands

### `raylings watch`

Starts the continuous interactive exercise watcher. Monitors the `exercises/` directory for file modifications, executes the active incomplete exercise on save, and provides hotkey navigation.

```bash
raylings watch [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--warm-daemon` / `--no-warm-daemon` | `bool` | `True` | Pre-warms the background Ray session before watching to accelerate evaluations. |
| `--dir` / `-d` | `Path` | `exercises` | Custom directory path containing curriculum exercises. |

#### Interactive Hotkeys

| Key | Action | Description |
| :---: | :--- | :--- |
| `[n]` | **Next** | Advance to the next exercise in syllabus sequence. |
| `[p]` | **Previous** | Return to the previous exercise. |
| `[r]` | **Rerun** | Re-execute the current exercise immediately. |
| `[h]` | **Hint** | Display progressive hint levels for the current exercise. |
| `[q]` | **Quit** | Stop the watcher loop and shut down the Ray cluster cleanly. |

#### Example

```bash
# Start standard watcher with warm daemon
raylings watch

# Watch a custom exercise folder without daemon pre-warming
raylings watch --dir ./my-exercises --no-warm-daemon
```

---

### `raylings tui`

Launches the interactive full-screen split-pane Terminal User Interface (TUI). Browse curriculum chapters and exercises, view syntax-highlighted code with line numbers, trigger test runs, cycle progressive hints, and toggle live cluster telemetry or doctor diagnostics without leaving your terminal.

```bash
raylings tui [OPTIONS]
```

#### Split-Pane Layout Architecture

- **Sidebar (Left, 36 cols)**: Interactive curriculum chapter and exercise tree with live status badges (`✓` completed, `⏳` active/in-progress, `○` pending).
- **Code Preview Panel (Top Right)**: Syntax-highlighted exercise source code with line numbers and word wrapping.
- **Output & Diagnostics Panel (Bottom Right)**: Real-time execution logs, pass/fail status, assertion errors, or progressive hint levels.
- **Telemetry & Doctor Overlays**: Full-screen live overlays for Ray cluster resource inspection (`[t]`) and preflight environment diagnostics (`[d]`).
- **Header & Footer**: Overall curriculum progress meter (`X/Y completed (%)`) and contextual keybinding helper.

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--exercise` / `-e` | `str` | `None` | Pre-select a specific exercise by name identifier (e.g. `basics01`). |
| `--non-interactive` | `bool` | `False` | Render TUI layout once in headless mode and exit (useful for automated testing and CI pipelines). |

#### Interactive Keybindings

| Key | Action | Description |
| :---: | :--- | :--- |
| `[r]` | **Run** | Execute the currently selected exercise and display evaluation diagnostics. |
| `[h]` | **Hint** | Toggle and cycle progressive hints for the active exercise. |
| `[j]` / `[↓]` / `[n]` | **Next** | Advance to the next exercise in syllabus sequence. |
| `[k]` / `[↑]` / `[p]` | **Previous** | Return to the previous exercise. |
| `[t]` | **Top / Telemetry** | Toggle the real-time Ray cluster health & resource telemetry overlay. |
| `[d]` | **Doctor** | Toggle the system and environment preflight diagnostics overlay. |
| `[Esc]` | **Return** | Exit telemetry or doctor overlay back to split-pane exercise view. |
| `[q]` | **Quit** | Exit the interactive TUI. |

#### Example

```bash
# Launch interactive full-screen TUI starting on the active exercise
raylings tui

# Launch TUI pre-focused on a specific exercise
raylings tui --exercise basics02

# Headless single render for automation / CI
raylings tui --non-interactive
```

---

### `raylings run`

Executes a single exercise or solution file once and outputs diagnostic evaluation results.

```bash
raylings run EXERCISE_NAME_OR_PATH [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `exercise_name` | `str` | **Yes** | The exercise identifier (e.g. `basics01`) or relative path to a Python file. |

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--timeout` / `-t` | `float` | `30.0` | Maximum subprocess execution timeout in seconds. |
| `--json` | `bool` | `False` | Output execution results and diagnostics in JSON format. |

#### Exit Codes

- `0`: Exercise passed all assertions and does not contain `# I AM NOT DONE`.
- `1`: Exercise failed assertions, timed out, or still contains `# I AM NOT DONE`.

#### Example

=== "Terminal Output"

    ```bash
    raylings run basics01
    ```

    ```text
    ✓ Successfully ran exercises/01_basics/basics01.py!
    Result: 42
    ```

=== "JSON Output (`--json`)"

    ```bash
    raylings run basics01 --json
    ```

    ```json
    {
      "name": "basics01",
      "title": "Ray Init & First Remote Task",
      "path": "exercises/01_basics/basics01.py",
      "passed": true,
      "has_not_done_marker": false,
      "exit_code": 0,
      "output": "Success! Result: 42\n",
      "error": ""
    }
    ```

---

### `raylings hint`

Displays progressive hints for an exercise without spoiling the full solution.

```bash
raylings hint [EXERCISE_NAME] [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `exercise_name` | `str` | No | Name of the exercise. Defaults to the current active incomplete exercise. |

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--level` / `-l` | `int` | `0` | Progressive hint index (0 = conceptual nudge, 1 = API hint, 2 = code structure). |
| `--json` | `bool` | `False` | Output hint metadata and text as JSON. |

#### Example

=== "Terminal Output"

    ```bash
    raylings hint basics01 --level 1
    ```

    ```text
    💡 Hint for basics01 (Level 2/3):
    Decorate your Python function with @ray.remote.
    ```

=== "JSON Output (`--json`)"

    ```bash
    raylings hint basics01 --json
    ```

    ```json
    {
      "name": "basics01",
      "title": "Ray Init & First Remote Task",
      "hints": [
        "Use ray.init(ignore_reinit_error=True) to initialize Ray.",
        "Decorate your Python function with @ray.remote.",
        "Invoke remote functions using function_name.remote(*args)."
      ],
      "selected_level": 0,
      "selected_hint": "Use ray.init(ignore_reinit_error=True) to initialize Ray."
    }
    ```

---

### `raylings list`

Lists all 14 curriculum chapters, all 66 exercises, and their completion status.

```bash
raylings list [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Output full curriculum metadata, chapter hierarchy, and completion flags as JSON. |

#### Example

```bash
raylings list
```

```text
Progress: [====================>                    ] 50.0% (33/66 completed)

01_basics (Ray Core Foundations): 6/6 completed [DONE]
02_actors (Distributed State & Actors): 7/7 completed [DONE]
03_object_store (Plasma Object Store & Zero-Copy): 4/6 completed
...
```

---

### `raylings tour`

Starts the 5-step interactive onboarding walkthrough.

```bash
raylings tour [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--step` / `-s` | `int` | `None` | Jump directly to a specific 1-indexed tour step (`1`–`5`). |
| `--non-interactive` / `-y` | `bool` | `False` | Render all tour steps without waiting for user input. |
| `--json` | `bool` | `False` | Output all tour steps, summaries, and action labels as JSON. |

#### Example

```bash
# Jump to Step 3 non-interactively
raylings tour --step 3

# Export all tour step metadata for IDEs
raylings tour --json
```

---

### `raylings doctor`

Runs preflight system, Python, Ray, and hardware diagnostics.

```bash
raylings doctor [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Output diagnostic check results and cluster status as JSON. |

#### Exit Codes

- `0`: All critical checks passed (`healthy` or `degraded`).
- `1`: One or more critical checks failed (e.g. Python < 3.10 or Ray missing).

---

### `raylings daemon`

Manages the background persistent Python Ray cluster daemon session.

```bash
raylings daemon ACTION
```

#### Actions

| Action | Description |
| :--- | :--- |
| `status` | Query active Ray cluster status, GCS address, node count, and resource allocations. |
| `start` | Start a background Ray cluster session. |
| `stop` | Stop and shut down the active background Ray session. |
| `restart` | Stop the active session and start a fresh Ray cluster. |

#### Example

```bash
# Check daemon session status
raylings daemon status

# Restart daemon if cluster state is degraded
raylings daemon restart
```

---

### `raylings progress`

Displays an overall completion summary and the current active exercise.

```bash
raylings progress [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Output completion metrics and active exercise path as JSON. |

---

### `raylings test`

Executes reference canonical solutions located in `solutions/` to verify curriculum integrity.

```bash
raylings test [EXERCISE_NAME] [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `exercise_name` | `str` | No | Optional specific exercise solution to test. |

#### Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--all` | `bool` | `True` | Execute all 66 reference solutions. |

---

### `raylings init`

Bootstraps a fresh Raylings workspace by extracting the bundled exercise suite into the target directory.

```bash
raylings init [OPTIONS]
```

#### Options

| Option | Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| `--directory` | `-d` | `.` | Target directory to initialize `exercises/` within. |
| `--force` | `-f` | `False` | Overwrite existing `exercises/` files if they already exist. |

---

### `raylings version`

Displays branding ASCII banner and current version string.

```bash
raylings version
```

---

### `raylings top` / `raylings metrics`

Displays a real-time cluster health and telemetry inspector dashboard. Interrogates the active Ray cluster GCS, Plasma in-memory object store, actor tables, task queues, and worker node resource saturation.

```bash
raylings top [OPTIONS]
# or alias
raylings metrics [OPTIONS]
```

#### Options

| Option | Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--interval` | `-i` | `float` | `1.0` | Refresh period in seconds for live telemetry monitoring. |
| `--once` | | `bool` | `False` | Capture and render a single cluster telemetry snapshot and exit immediately. |
| `--json` | | `bool` | `False` | Output structured cluster telemetry snapshot as JSON. |

#### Key Telemetry Metrics Displayed

- **⚡ Cluster Overview**: GCS address, Ray runtime version, Python runtime version, cluster uptime, total/used CPU cores, and total/used GPUs.
- **🖥️ Node Allocation Table**: Node ID, Node IP, Role (`Head` / `Worker`), Status (`ALIVE` / `DEAD`), CPU utilization percentage gauges, Plasma memory allocations per node, and GPU counts.
- **📦 Plasma Object Store & Memory Telemetry**: Total Plasma buffer capacity, used vs. available bytes, active in-memory objects count, disk spilled bytes & object count, and restored bytes from disk.
- **🎭 Instantiated Actors Table**: Actor ID, actor name / class name, process ID (PID), lifecycle state (`ALIVE`, `RESTARTING`, `DEAD`), host node IP, and crash/restart count.
- **📋 Task Queue Statistics**: Total tasks, pending tasks, running tasks, finished tasks, and failed task counters.

#### Example

=== "Live Dashboard (`raylings top`)"

    ```bash
    raylings top --interval 0.5
    ```

=== "One-Shot Snapshot (`--once`)"

    ```bash
    raylings top --once
    ```

=== "JSON Output (`--json`)"

    ```bash
    raylings top --json
    ```

    ```json
    {
      "timestamp": 1700000000.0,
      "timestamp_iso": "2023-11-14T22:13:20Z",
      "is_active": true,
      "ray_version": "2.43.0",
      "python_version": "3.12.9",
      "cluster_address": "127.0.0.1:6379",
      "dashboard_url": "http://127.0.0.1:8265",
      "uptime_seconds": 125.0,
      "total_cpus": 8.0,
      "used_cpus": 2.0,
      "total_gpus": 0.0,
      "used_gpus": 0.0,
      "nodes": [
        {
          "node_id": "abcd1234efgh5678",
          "node_ip": "127.0.0.1",
          "is_head_node": true,
          "status": "ALIVE",
          "cpu_cores_total": 8.0,
          "cpu_cores_used": 2.0,
          "cpu_percent": 25.0,
          "ram_total_bytes": 17179869184,
          "ram_used_bytes": 0,
          "ram_percent": 0.0,
          "object_store_total_bytes": 2147483648,
          "object_store_used_bytes": 536870912,
          "object_store_percent": 25.0,
          "gpus_total": 0.0,
          "gpus_used": 0.0,
          "custom_resources": {}
        }
      ],
      "object_store": {
        "total_bytes": 2147483648,
        "used_bytes": 536870912,
        "free_bytes": 1610612736,
        "usage_percent": 25.0,
        "active_objects": 4,
        "spilled_bytes": 0,
        "spilled_objects": 0,
        "restored_bytes": 0
      },
      "actors": [
        {
          "actor_id": "01000000ffffffff",
          "name": "StatefulWorker",
          "class_name": "StatefulWorker",
          "state": "ALIVE",
          "pid": 54321,
          "node_ip": "127.0.0.1",
          "node_id": "abcd1234efgh5678",
          "restart_count": 0,
          "job_id": "01000000"
        }
      ],
      "tasks": {
        "total_tasks": 12,
        "pending_tasks": 0,
        "running_tasks": 2,
        "finished_tasks": 10,
        "failed_tasks": 0
      },
      "error": null
    }
    ```

---

### `raylings new` / `raylings new-exercise`

Scaffolds a new curriculum exercise and reference solution template with boilerplate code, docstrings, imports, `verify()` validation harness, and a ready-to-use manifest registration snippet.

```bash
raylings new CHAPTER NAME [OPTIONS]
# or alias
raylings new-exercise CHAPTER NAME [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `chapter` | `str` | **Yes** | Chapter number (e.g. `15` or `01`) or chapter directory name (e.g. `15_vllm_and_llms`). |
| `name` | `str` | **Yes** | Exercise filename/identifier without `.py` extension (e.g. `vllm05`). |

#### Options

| Option | Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--title` | `-t` | `str` | `None` | Human-readable exercise title. Defaults to title-cased name. |
| `--description` | `-d` | `str` | `None` | Summary description of exercise learning goals and key concepts. |
| `--dry-run` | | `bool` | `False` | Preview generated file templates and manifest snippet without writing to disk. |
| `--json` | | `bool` | `False` | Output scaffolding result and manifest snippet as JSON. |

#### Example

=== "Terminal Output"

    ```bash
    raylings new 15 vllm05 --title "Speculative Decoding" --description "Coordinate draft model worker actors for speculative decoding."
    ```

    ```text
    ✓ Successfully scaffolded exercise 'vllm05'!

    Chapter: 15_vllm_and_llms
    Exercise File: exercises/15_vllm_and_llms/vllm05.py
    Solution File: solutions/15_vllm_and_llms/vllm05.py

    Next Step: Register this exercise in src/raylings/manifest.py under chapter 15_vllm_and_llms:

    ╭─────────────────── Manifest Registration Snippet ───────────────────╮
    │ Exercise(                                                           │
    │     name="vllm05",                                                  │
    │     title="Speculative Decoding",                                   │
    │     path="exercises/15_vllm_and_llms/vllm05.py",                    │
    │     chapter_name="15_vllm_and_llms",                                │
    │     hints=[                                                         │
    │         "Initialize Ray using ray.init(ignore_reinit_error=True).", │
    │         "Complete the exercise task and ensure assertions pass.",   │
    │     ],                                                              │
    │ ),                                                                  │
    ╰─────────────────────────────────────────────────────────────────────╯
    ```

=== "Dry Run (`--dry-run`)"

    ```bash
    raylings new 01 custom_task --dry-run
    ```

    ```text
    DRY RUN PREVIEW (No files were written to disk)

    Chapter: 01_basics
    Exercise File: exercises/01_basics/custom_task.py
    Solution File: solutions/01_basics/custom_task.py
    ```

=== "JSON Output (`--json`)"

    ```bash
    raylings new 15 vllm05 --dry-run --json
    ```

    ```json
    {
      "exercise_path": "exercises/15_vllm_and_llms/vllm05.py",
      "solution_path": "solutions/15_vllm_and_llms/vllm05.py",
      "chapter_name": "15_vllm_and_llms",
      "exercise_name": "vllm05",
      "title": "Vllm05",
      "description": "Hands-on exercise implementing Vllm05.",
      "manifest_snippet": "Exercise(\n    name=\"vllm05\",\n    title=\"Vllm05\",\n    path=\"exercises/15_vllm_and_llms/vllm05.py\",\n    chapter_name=\"15_vllm_and_llms\",\n    hints=[\n        \"Initialize Ray using ray.init(ignore_reinit_error=True).\",\n        \"Complete the exercise task and ensure assertions pass.\",\n    ],\n),",
      "created_files": [],
      "dry_run": true
    }
    ```
