# Getting Started with Raylings 🚀

Welcome to **Raylings**! This guide takes you from an empty environment to solving your first distributed Ray exercise in under 5 minutes.

---

## ⚡ Try in Browser (Zero Installation)

If you'd like to test Raylings immediately without installing Python or Ray locally, jump into our client-side WebAssembly playground:

👉 **[Launch Interactive WebAssembly Playground](https://dnf0.github.io/raylings/playground/)** — Features Python 3.12, Monaco code editor, progressive hints, solution diffing, and in-memory execution 100% in your browser.

---

## 📋 Prerequisites

Before installing Raylings locally, verify that your environment satisfies the following minimum requirements:

- **Python**: Version `3.10`, `3.11`, or `3.12` (Python 3.10+ is required).
- **Operating System**:
    - **macOS**: Apple Silicon (M1/M2/M3/M4) or Intel x86_64.
    - **Linux**: Ubuntu 20.04+, Debian 11+, RHEL 8+, or equivalent (x86_64 and aarch64).
    - **Windows**: Windows Subsystem for Linux (WSL2 with Ubuntu) recommended for Ray compatibility.
- **Hardware Resources**: Minimum 2 CPU cores and 4GB RAM (8GB+ recommended for multi-worker, Ray Train, and DeepSpeed exercises).

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
    ├── 14_kuberay/
    ├── 15_vllm_and_llms/
    ├── 16_fsdp_and_deepspeed/
    ├── 17_multimodal_and_vectors/
    └── 18_quant_finance/
```

!!! tip "Cloned Repository Users"
    If you cloned the `raylings` repository from Git, the `exercises/` directory is already present and ready to use. You do not need to run `raylings init`.

---

## ⏱️ Your First 5 Minutes

Follow these four steps to experience the complete Raylings workflow.

### Step 1: Preflight Health Check

Ensure your system, Python environment, and Ray prerequisites are healthy:

```bash
raylings doctor
```

### Step 2: Take the Interactive Tour

Launch the 5-step guided tour introducing Ray tasks, actors, and keyboard controls:

```bash
raylings tour
```

### Step 3: Start the Watcher or TUI

Choose your preferred learning interface:

=== "Option A: Background Watcher (VS Code / Editor)"

    ```bash
    raylings watch
    ```

=== "Option B: Full-Screen Interactive TUI"

    ```bash
    raylings tui
    ```

### Step 4: Solve Your First Exercise

Open `exercises/01_basics/basics01.py` in your editor, follow the `# TODO:` and `# WHY:` instructions, remove `# I AM NOT DONE`, and save!

---

## 💻 VS Code & Cursor Setup

To get real-time code actions, inline hints, and solution diffing directly in VS Code or Cursor:

```bash
# Install directly from the VS Code Marketplace
code --install-extension dnf0.raylings-vscode
# Or for Cursor
cursor --install-extension dnf0.raylings-vscode
```

Explore the [**Interactive Onboarding Guide**](onboarding-guide.md) for full editor keybindings and walkthrough instructions.
