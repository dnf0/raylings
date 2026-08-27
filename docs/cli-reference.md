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
