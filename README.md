# Raylings ⚡

> An interactive, hands-on CLI learning environment for mastering Python Ray from scratch.

Inspired by the pedagogy of [Rustlings](https://github.com/rust-lang/rustlings) and [Ziglings](https://github.com/ziglings/exercises), **Raylings** guides you through progressively challenging distributed computing exercises in Python. You will fix broken code, fill in missing distributed patterns, resolve performance bottlenecks, eliminate memory leaks, and build real-world distributed systems.

👉 **New to Raylings? Read the [Comprehensive Onboarding Guide](docs/ONBOARDING.md)** for a deep dive into setup, preflight diagnostics, the tour engine, keyboard shortcuts, and troubleshooting.

---

## What is Raylings?

Ray is a unified framework for scaling AI and Python applications from single laptops to massive multi-node clusters. While powerful, mastering Ray's mental models—futures, stateful actors, Plasma zero-copy memory, dynamic placement groups, and lineage-based fault tolerance—requires hands-on practice.

Raylings provides:
- **Preflight Diagnostics (`raylings doctor`)**: Built-in environment & hardware diagnostics checking Python 3.10+, Ray installation, CPU/RAM capacity, and cluster health.
- **Interactive Tour (`raylings tour`)**: 5-step interactive curriculum tour explaining distributed primitives, exercise workflow, and developer shortcuts.
- **Interactive File Watcher (`raylings watch`)**: Edit exercises in your favorite editor; Raylings automatically re-runs and validates your changes on save.
- **Sub-50ms Execution**: Background Ray daemon re-uses a warm local cluster session for rapid turnaround.
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
uvx raylings watch
```

### 2. Standard Installation

Install globally or in your virtual environment:

```bash
pip install raylings
raylings init
raylings doctor
raylings tour
raylings watch
```

### 3. From Source

Clone the repository and install in editable mode:

```bash
git clone https://github.com/dnf0/raylings.git
cd raylings
pip install -e ".[dev]"
raylings doctor
raylings tour
raylings watch
```

---

## Interactive Learning Workflow

Raylings starts on the first exercise in `exercises/01_basics/basics01.py`. 

```
1. Open exercises/01_basics/basics01.py in your code editor.
2. Read the instructions, implement the Ray distributed calls, and remove '# I AM NOT DONE'.
3. Save the file. Raylings immediately tests your changes and advances to the next exercise.
```

### Key CLI Commands

- `raylings doctor` — Run preflight system, Python, and Ray environment diagnostics.
- `raylings tour` — Launch the 5-step interactive onboarding tour (`--step`, `-y`, `--json`).
- `raylings init` — Extract bundled exercises into the current directory.
- `raylings watch` — Start continuous watching mode with keyboard shortcuts (`n`, `p`, `r`, `h`, `q`).
- `raylings run <exercise_name>` — Run and verify a specific exercise.
- `raylings test` — Run automated verification across all canonical reference solutions.
- `raylings hint <exercise_name>` — Show progressive hints for an exercise (`--level`).
- `raylings list` — View all chapters, exercises, and completion progress.
- `raylings verify` — Verify full curriculum progress and validate solutions.
- `raylings daemon [status|start|stop|restart]` — Manage the warm background Ray cluster session.

---

## VS Code & IDE Integration

Raylings provides a first-class extension for VS Code and Cursor (`editors/vscode`):
- **Welcome Walkthrough**: Interactive onboarding via **Help > Welcome > Walkthroughs > Welcome to Raylings**.
- **Exercise Explorer**: Browse chapters and exercises with status badges in the Activity Bar.
- **Auto-run on Save**: Automatically evaluates exercises on file save.
- **Status Bar**: Live progress tracking and active exercise display.

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

- 📖 [Onboarding & Learner Guide](docs/ONBOARDING.md) — Detailed quickstart, preflight diagnostics, tour engine, watcher shortcuts, and troubleshooting.
- 🤝 [Contributing Guide](CONTRIBUTING.md) — Local development setup, testing workflows, and PR guidelines.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
