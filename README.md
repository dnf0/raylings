# Raylings ⚡

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://dnf0.github.io/raylings/)
[![CI](https://github.com/dnf0/raylings/actions/workflows/ci.yml/badge.svg)](https://github.com/dnf0/raylings/actions/workflows/ci.yml)
[![KubeRay CI](https://github.com/dnf0/raylings/actions/workflows/kuberay-e2e.yml/badge.svg)](https://github.com/dnf0/raylings/actions/workflows/kuberay-e2e.yml)
[![TUI](https://img.shields.io/badge/TUI-Split--Pane%20Terminal-green.svg)](#interactive-full-screen-tui-raylings-tui)
[![Telemetry](https://img.shields.io/badge/Telemetry-Ray%20Cluster%20Top-purple.svg)](#cluster-health--telemetry-inspector-raylings-top)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> An interactive, hands-on CLI learning environment for mastering Python Ray from scratch.

Inspired by the pedagogy of [Rustlings](https://github.com/rust-lang/rustlings) and [Ziglings](https://github.com/ziglings/exercises), **Raylings** guides you through progressively challenging distributed computing exercises in Python. You will fix broken code, fill in missing distributed patterns, resolve performance bottlenecks, eliminate memory leaks, and build real-world distributed systems.

📚 **Full Documentation Site**: [https://dnf0.github.io/raylings/](https://dnf0.github.io/raylings/)  
👉 **New to Raylings? Read the [Interactive Onboarding Guide](https://dnf0.github.io/raylings/onboarding-guide/)** for a deep dive into setup, preflight diagnostics, the tour engine, keyboard shortcuts, and troubleshooting.

---

## What is Raylings?

Ray is a unified framework for scaling AI and Python applications from single laptops to massive multi-node clusters. While powerful, mastering Ray's mental models—futures, stateful actors, Plasma zero-copy memory, dynamic placement groups, and lineage-based fault tolerance—requires hands-on practice.

Raylings provides:
- **Interactive Full-Screen TUI (`raylings tui`)**: Rich split-pane terminal UI with a live curriculum tree, syntax-highlighted code preview, hotkey execution (`[r]`), progressive hints (`[h]`), and telemetry overlays (`[t]`).
- **Cluster Health & Telemetry Inspector (`raylings top` / `raylings metrics`)**: Real-time live dashboard monitoring Plasma object store memory, disk spill rates, node CPU/GPU saturation, and active actor tables.
- **Exercise Scaffolding CLI (`raylings new` / `raylings new-exercise`)**: One-command generator creating boilerplate exercises, reference solutions, validation harnesses, and manifest registration snippets.
- **Preflight Diagnostics (`raylings doctor`)**: Built-in environment & hardware diagnostics checking Python 3.10+, Ray installation, CPU/RAM capacity, and cluster health.
- **Interactive Tour (`raylings tour`)**: 5-step interactive curriculum tour explaining distributed primitives, exercise workflow, and developer shortcuts.
- **Interactive File Watcher (`raylings watch`)**: Edit exercises in your favorite editor; Raylings automatically re-runs and validates your changes on save.
- **Sub-50ms Execution**: Background Ray daemon re-uses a warm local cluster session for rapid turnaround.
- **Multi-Node Kubernetes & KubeRay (`scripts/kuberay/`)**: Ephemeral 3-node KinD cluster harness and end-to-end integration test suite for testing Ray clusters, remote Ray client execution, and DDP training on real Kubernetes topology.
- **14 Chapters & 66 Exercises**: From first remote tasks to distributed parameter servers, PyTorch DDP pipelines, Ray Serve DAGs, and KubeRay on Kubernetes.
- **Progressive Hints & Solutions**: Stuck on an exercise? Get layered hints without spoiling the answer, or inspect canonical solutions when finished.
- **First-Class VS Code Extension**: Dedicated sidebar tree view, status bar progress, on-save auto-evaluations, and built-in interactive walkthroughs.

---

## Quickstart

### Prerequisites
- Python 3.10, 3.11, or 3.12
- [uv](https://github.com/astral-sh/uv) (recommended) or `pipx` / `pip`

### 1. Instant Run with `uvx` (No installation needed)

Initialize a workspace in any directory, run diagnostics, take the tour, and jump right in:

```bash
uvx raylings init
uvx raylings doctor
uvx raylings tour
uvx raylings tui       # Or launch watcher: uvx raylings watch
```

### 2. Standard Installation

Install globally or in your virtual environment:

```bash
pip install raylings
raylings init
raylings doctor
raylings tour
raylings tui           # Or launch watcher: raylings watch
```

### 3. From Source

Clone the repository and install in editable mode:

```bash
git clone https://github.com/dnf0/raylings.git
cd raylings
pip install -e ".[dev]"
raylings doctor
raylings tour
raylings tui
```

---

## Interactive Learning Workflow

Raylings offers two ways to learn: the **Full-Screen Split-Pane TUI** and the **Live Background Watcher**.

### 1. Interactive Full-Screen TUI (`raylings tui`)

Launch the split-pane terminal interface to browse the entire curriculum, preview code with line numbers, run exercises, and reveal progressive hints with single keystrokes:

```bash
raylings tui
```

| Key | Action | Description |
| :---: | :--- | :--- |
| `[r]` | **Run** | Execute active exercise and view execution diagnostics. |
| `[h]` | **Hint** | Toggle layered progressive hints. |
| `[j]` / `[↓]` / `[n]` | **Next** | Navigate to the next exercise. |
| `[k]` / `[↑]` / `[p]` | **Previous** | Navigate to the previous exercise. |
| `[t]` | **Telemetry** | Open live Ray cluster resource & memory inspector overlay. |
| `[d]` | **Doctor** | Open preflight system diagnostics overlay. |
| `[q]` | **Quit** | Exit the TUI. |

### 2. Live Background Watcher (`raylings watch`)

Prefer using your favorite code editor (VS Code, Cursor, Neovim)? Start the continuous background watcher:

```
1. Run 'raylings watch' in a terminal.
2. Open exercises/01_basics/basics01.py in your code editor.
3. Read the instructions, implement the Ray distributed calls, and remove '# I AM NOT DONE'.
4. Save the file. Raylings immediately tests your changes and advances to the next exercise.
```

### 3. Cluster Health & Telemetry Inspector (`raylings top`)

Inspect your local Ray cluster's live Plasma memory allocations, object spill rates, CPU/GPU core usage, and instantiated actor states:

```bash
raylings top --interval 0.5
# Or output a one-shot JSON snapshot:
raylings top --json
```

### 4. Authoring New Exercises (`raylings new`)

Contribute new exercises to the Raylings curriculum with the built-in scaffolder:

```bash
raylings new 15 vllm05 --title "Speculative Decoding" --description "Coordinate draft model worker actors."
```

### Key CLI Commands

- `raylings tui` — Launch interactive full-screen split-pane TUI (`-e`, `--non-interactive`).
- `raylings top` / `raylings metrics` — Live cluster telemetry, memory inspector, and actor monitor (`-i`, `--once`, `--json`).
- `raylings new` / `raylings new-exercise` — Scaffold new exercise and solution templates (`-t`, `-d`, `--dry-run`, `--json`).
- `raylings watch` — Start continuous watching mode with keyboard shortcuts (`n`, `p`, `r`, `h`, `q`).
- `raylings doctor` — Run preflight system, Python, and Ray environment diagnostics.
- `raylings tour` — Launch the 5-step interactive onboarding tour (`--step`, `-y`, `--json`).
- `raylings init` — Extract bundled exercises into the current directory.
- `raylings run <exercise_name>` — Run and verify a specific exercise.
- `raylings test` — Run automated verification across all canonical reference solutions.
- `raylings hint <exercise_name>` — Show progressive hints for an exercise (`--level`).
- `raylings list` — View all chapters, exercises, and completion progress.
- `raylings progress` — Display progress summary and next recommended exercise.
- `raylings daemon [status|start|stop|restart]` — Manage the warm background Ray cluster session.

---

## VS Code & IDE Integration

Raylings provides a first-class extension for VS Code and Cursor (`editors/vscode`):
- **Welcome Walkthrough**: Interactive onboarding via **Help > Welcome > Walkthroughs > Welcome to Raylings**.
- **Exercise Explorer**: Browse chapters and exercises with status badges in the Activity Bar.
- **Auto-run on Save**: Automatically evaluates exercises on file save.
- **Status Bar**: Live progress tracking and active exercise display.

---

## Cloud & KubeRay Multi-Node Testing

Raylings provides automated scripts and test harnesses to deploy ephemeral multi-node Ray clusters on Kubernetes using **KinD** and the **KubeRay Operator**:

```bash
# 1. Provision 3-node KinD cluster & KubeRay operator
bash scripts/kuberay/setup-kuberay.sh up

# 2. Forward Ray client (10001) and dashboard (8265) ports
bash scripts/kuberay/setup-kuberay.sh forward

# 3. Run exercises or watch against the remote Kubernetes cluster
RAY_ADDRESS=ray://localhost:10001 raylings run exercises/14_kuberay/kuberay01.py

# 4. Run the multi-node end-to-end integration test suite
RAY_ADDRESS=ray://localhost:10001 uv run pytest tests/test_kuberay_e2e.py -v

# 5. Teardown cluster
bash scripts/kuberay/setup-kuberay.sh down
```

See the [**Cloud & KubeRay Guide**](https://dnf0.github.io/raylings/cloud-kuberay/) for architecture diagrams, Helm configuration, and CI workflows.

---

## Curriculum Map

Raylings covers 14 comprehensive chapters spanning core foundations to production ML engineering:

| Chapter | Title | Topics Covered |
| :--- | :--- | :--- |
| **01** | **Ray Core Foundations** | `ray.init()` mechanics, `@ray.remote` tasks, `ObjectRef` futures, parallel pipelines, `ray.wait()`, multiple return values |
| **02** | **Distributed State & Actors** | Stateful actor classes, method serialization, actor handles, async actors, threaded actors, detached named actors, actor pools |
| **03** | **Plasma Object Store & Zero-Copy** | Plasma in-memory architecture, zero-copy NumPy/PyArrow, `ray.put()`, object pinning, disk spilling, serialization closures |
| **04** | **Scheduling & Placement Groups** | Fractional CPU/GPU resources, node affinity, `STRICT_SPREAD`, `STRICT_PACK`, multi-bundle gang scheduling, runtime environments |
| **05** | **Fault Tolerance & Recovery** | Automatic task retries, actor restart policies, lineage reconstruction, spot instance & preemption handling |
| **06** | **Cluster Architecture & Simulation** | Head vs worker nodes, GCS, Raylets, multi-node testing with `ray.cluster_utils.Cluster`, Ray Job Submission API |
| **07** | **Patterns & Anti-Patterns** | Fixing nested `ray.get()`, task chunking/batching, actor bottleneck elimination, tree-structured aggregation |
| **08** | **Ray Data (ETL & Batch)** | Ray Datasets, block partitioning, `map_batches` with PyArrow/NumPy, `ActorPoolStrategy`, streaming backpressure, PyTorch interop |
| **09** | **ML Primitives from Scratch** | Distributed parameter servers, async vs sync parameter updates, ring all-reduce communication, distributed trainers |
| **10** | **Ray Train (PyTorch DDP)** | `TorchTrainer`, `ScalingConfig`, distributed dataloaders, multi-GPU gradient sync, distributed checkpointing |
| **11** | **Ray Tune (Hyperparameter Optimization)** | Search spaces, distributed trial execution, ASHA / HyperBand early stopping, Population-Based Training (PBT) |
| **12** | **Ray Serve (Model Deployment)** | `@serve.deployment`, HTTP ingress, dynamic request batching (`@serve.batch`), multi-model DAGs, streaming LLMs, autoscaling |
| **13** | **Observability & Debugging** | Chrome execution timelines (`ray timeline`), memory profiling (`ray memory`), Prometheus metrics, GCS dumps |
| **14** | **KubeRay on Kubernetes** | RayCluster CRD, RayJob batch lifecycles, RayService rolling zero-downtime serving, KEDA autoscaling, pod eviction recovery |

---

## Documentation

The full documentation is available at **[https://dnf0.github.io/raylings/](https://dnf0.github.io/raylings/)**.

- 🚀 [Getting Started](https://dnf0.github.io/raylings/getting-started/) — Prerequisites, installation methods (`uv tool`, `pipx`, editable), and first 5 minutes.
- 🧭 [Interactive Onboarding Guide](https://dnf0.github.io/raylings/onboarding-guide/) — Guided tour, doctor diagnostics, and VS Code integration.
- 📚 [Curriculum Syllabus](https://dnf0.github.io/raylings/syllabus/) — Complete 14-chapter map covering all 66 exercises.
- ⌨️ [CLI Reference Manual](https://dnf0.github.io/raylings/cli-reference/) — Comprehensive reference for all CLI subcommands and JSON outputs.
- 🛠️ [Troubleshooting Recipes](https://dnf0.github.io/raylings/troubleshooting/) — Diagnostic recipes for port conflicts, memory spilling, and DDP deadlocks.
- ☸️ [Cloud & KubeRay Deployment](https://dnf0.github.io/raylings/cloud-kuberay/) — KinD multi-node clusters, KubeRay operator, remote execution, and E2E test suite.
- 🤝 [Contributing Guide](https://dnf0.github.io/raylings/contributing/) — Exercise authoring standards, test suites, and contribution workflow.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
