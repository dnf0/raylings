# Getting Started with Raylings 🚀

Welcome to **Raylings**! This guide takes you from an empty environment to solving your first distributed Ray exercise in under 5 minutes.

---

## 📋 Prerequisites

Before installing Raylings, verify that your environment satisfies the following minimum requirements:

- **Python**: Version `3.10`, `3.11`, or `3.12` (Python 3.10+ is required).
- **Operating System**:
    - **macOS**: Apple Silicon (M1/M2/M3/M4) or Intel x86_64.
    - **Linux**: Ubuntu 20.04+, Debian 11+, RHEL 8+, or equivalent (x86_64 and aarch64).
    - **Windows**: Windows Subsystem for Linux (WSL2 with Ubuntu) recommended for Ray compatibility.
- **Hardware Resources**: Minimum 2 CPU cores and 4GB RAM (8GB+ recommended for multi-worker and Ray Train exercises).

---

## 📦 Installation Options

Choose your preferred installation method below. We strongly recommend [uv](https://github.com/astral-sh/uv) for the fastest, most isolated developer experience.

=== "Option 1: uv tool / uvx (Recommended)"

    Install Raylings as an isolated global tool with [Astral's `uv`](https://docs.astral.sh/uv/):

    ```bash
    # Install globally into an isolated environment
    uv tool install raylings

    # Or run on-demand without prior installation
    uvx raylings --help
    ```

=== "Option 2: pipx / pip"

    Install into an isolated virtual environment using `pipx` or standard `pip`:

    ```bash
    # Using pipx (recommended for global CLI apps)
    pipx install raylings

    # Or inside an activated virtual environment
    pip install raylings
    ```

=== "Option 3: From Source (Development / Editable)"

    Clone the repository to build or contribute to Raylings directly:

    ```bash
    git clone https://github.com/dnf0/raylings.git
    cd raylings
    uv venv --python 3.12
    source .venv/bin/activate
    uv pip install -e ".[dev,docs]"
    ```

---

## 🛠️ Workspace Initialization

If you installed Raylings as a standalone package (e.g. via `uv tool install` or `pip`), bootstrap an exercise workspace in your current directory:

```bash
raylings init
```

This creates the standard curriculum folder hierarchy in your workspace:

```text
my-workspace/
└── exercises/
    ├── 01_basics/
    ├── 02_actors/
    ├── 03_object_store/
    ├── 04_scheduling_resources/
    ├── 05_fault_tolerance/
    ├── 06_cluster_architecture/
    ├── 07_patterns_and_antipatterns/
    ├── 08_ray_data/
    ├── 09_ml_from_scratch/
    ├── 10_ray_train_and_tune/
    ├── 11_ray_tune/
    ├── 12_ray_serve/
    ├── 13_observability_and_debugging/
    └── 14_kuberay/
```

!!! tip "Cloned Repository Users"
    If you cloned the `raylings` repository from Git, the `exercises/` directory is already present and ready to use. You do not need to run `raylings init`.

---

## ⏱️ Your First 5 Minutes

Follow these four steps to experience the complete Raylings workflow.

### Step 1: Preflight Health Check

Run `raylings doctor` to verify that your Python runtime, Ray installation, and cluster prerequisites are healthy:

```bash
raylings doctor
```

Output:

```text
                     Preflight Diagnostics Summary                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Diagnostic Check          ┃ Status ┃ Details                        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python Version            │ ✓ PASS │ Python 3.12.3 (>= 3.10)        │
│ Ray Installation          │ ✓ PASS │ Ray v2.43.0 installed          │
│ Ray Daemon / Cluster      │ ✓ PASS │ Cluster session active         │
│ Exercises Manifest        │ ✓ PASS │ Found 66 exercises in 14 chap  │
│ System Resources          │ ✓ PASS │ 10 logical CPUs, 32.0 GB RAM   │
└───────────────────────────┴────────┴────────────────────────────────┘

Summary: 5 passed, 0 warnings, 0 failed
```

---

### Step 2: Take the Interactive Tour

Launch the interactive onboarding tour to learn the curriculum structure and keystroke shortcuts:

```bash
raylings tour
```

Press `Enter` to cycle through the 5 onboarding steps, or run non-interactively with `raylings tour -y`.

---

### Step 3: Launch the Live Watcher

Start the Raylings file watcher in your terminal:

```bash
raylings watch
```

Raylings starts a background warm Ray daemon session and immediately evaluates the first incomplete exercise (`exercises/01_basics/basics01.py`).

---

### Step 4: Solve `basics01.py`

Open `exercises/01_basics/basics01.py` in your code editor. You will see something like this:

```python
# I AM NOT DONE
"""
Exercise: basics01.py
Topic: Ray Init & First Remote Task

Objective:
Transform standard Python functions into distributed Ray tasks using
the `@ray.remote` decorator and execute them asynchronously with `.remote()`.
"""

import ray


def add(a: int, b: int) -> int:
    return a + b


def main() -> None:
    # 1. Initialize Ray runtime
    # TODO: Initialize ray with ignore_reinit_error=True

    # 2. Transform 'add' into a remote task and execute it
    # TODO: Invoke add asynchronously with arguments (10, 32)
    # result_ref = ...

    # 3. Retrieve the computed value from the ObjectRef
    # result = ...

    assert result == 42, f"Expected 42, got {result}"
    print(f"Success! Result: {result}")


if __name__ == "__main__":
    main()
```

#### How to Solve:

1. Decorate the `add` function with `@ray.remote`:
   ```python
   @ray.remote
   def add(a: int, b: int) -> int:
       return a + b
   ```
2. Initialize Ray and execute the remote task:
   ```python
   ray.init(ignore_reinit_error=True)
   result_ref = add.remote(10, 32)
   result = ray.get(result_ref)
   ```
3. Remove or delete the `# I AM NOT DONE` comment line from the very top of the file.
4. Save the file.

The live watcher will instantly detect the file modification, execute the test, output a green checkmark, and automatically advance to `basics02.py`!

```text
✓ Successfully ran exercises/01_basics/basics01.py!
🎉 Exercise completed! Advancing to basics02.py...
```

---

## ⌨️ Watcher Keyboard Shortcuts

While `raylings watch` is running, you have access to interactive hotkeys:

| Key | Action | Description |
| :--- | :--- | :--- |
| `[n]` | **Next** | Skip forward to the next exercise |
| `[p]` | **Previous** | Jump back to the previous exercise |
| `[r]` | **Rerun** | Re-execute the current active exercise |
| `[h]` | **Hint** | Display progressive hint levels for the current exercise |
| `[q]` | **Quit** | Stop the watcher and shut down the Ray session |

---

## 🧭 Next Steps

Now that you have solved your first exercise:

- Read the [**Interactive Onboarding Guide**](onboarding-guide.md) to set up the VS Code extension and understand state tracking.
- Explore the [**Curriculum Syllabus**](syllabus.md) to see all 14 chapters and learning paths.
- Check the [**CLI Reference**](cli-reference.md) for full details on flags and JSON integration.
