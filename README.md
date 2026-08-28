# Raylings ⚡

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://dnf0.github.io/raylings/)
[![CI](https://github.com/dnf0/raylings/actions/workflows/ci.yml/badge.svg)](https://github.com/dnf0/raylings/actions)
[![KubeRay CI](https://github.com/dnf0/raylings/actions/workflows/kuberay-e2e.yml/badge.svg)](https://github.com/dnf0/raylings/actions)
[![Playground](https://img.shields.io/badge/Playground-⚡%20Try%20in%20Browser-blueviolet)](https://dnf0.github.io/raylings/playground/)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checker: pyright](https://img.shields.io/badge/types-pyright-green.svg)](https://github.com/microsoft/pyright)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> **Master distributed AI, Ray Core actors, and scalable clusters from scratch through small, interactive, hands-on Python exercises.**

<p align="center">
  <img src="docs/assets/demo.svg" alt="Raylings Terminal Demo" width="840">
</p>

Inspired by the pedagogical brilliance of [rustlings](https://github.com/rust-lang/rustlings) and [ziglings](https://codeberg.org/ziglings/exercises), **Raylings** guides engineers through self-paced, iterative exercises. You will fix broken distributed tasks, construct stateful actor pools, eliminate object store memory bottlenecks, configure custom placement groups, build fault-tolerant streaming pipelines, coordinate PyTorch FSDP & DeepSpeed ZeRO training, serve LLMs with vLLM tensor parallelism, orchestrate KubeRay clusters on Kubernetes, and deploy domain-specific financial analytics packs.

---

## Pedagogical Philosophy

Learning distributed computing and Ray from static documentation or raw copy-pasted boilerplate is difficult because distributed error messages are complex and feedback loops are slow. Raylings solves this through **guided, test-driven micro-learning**:

1. **Active Debugging & Iteration**: Every exercise starts in a broken or incomplete state with clear `# TODO:` instructions and `# WHY:` architectural rationale. You read the problem description, inspect the failure, and edit the code until it passes all verification checks.
2. **Instant Feedback Loop & Interactive Hotkeys**: An automated watcher observes file modifications in real time (< 50ms). When an exercise passes, press `n` or `Enter` to advance, `p` to revisit previous exercises, `h` to reveal progressive hints, `r` to force a rerun, `l` to list exercises, or `q` to quit.
3. **Dual-Mode Learning (Offline WASM & Live Cluster)**:
   - **Offline WASM Mode**: Zero cluster setup required. The pure-Python WebAssembly simulator validates tasks, actors, object store references, and dataset transformations directly in-memory or in your browser.
   - **Live Cluster Mode**: Seamlessly connect to a local Ray session, remote Ray cluster, or multi-node Kubernetes `KubeRay` cluster (`ray://localhost:10001`). Exercises provision real actors and verify distributed execution across nodes.
4. **Progressive Hints**: When stuck, multi-tiered hints (`raylings hint <exercise>`) nudge you in the right direction without spoiling the answer.

---

## Architecture

```
                                  +-----------------------+
                                  |     User Terminal     |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   Raylings CLI (Typer)|
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
         +-----------------------+                         +-----------------------+
         |  File Watcher Engine  |                         | Rich UI & TUI Engine  |
         |      (watchfiles)     |                         |  (split-pane / top)   |
         +-----------+-----------+                         +-----------------------+
                     |
                     v
         +-----------------------+
         |  Curriculum Manifest  |  (18 Chapters / 81 Exercises)
         +-----------+-----------+
                     |
                     v
         +-----------------------+
         |   Exercise Runner     |
         +-----------+-----------+
                     |
        +------------+------------+
        |                         |
        v                         v
+----------------+       +-------------------+
| Pure-Python    |       | Live Ray Cluster  |
| In-Memory WASM |  OR   | & KubeRay Multi-  |
| Ray Simulator  |       | Node Adapter      |
+----------------+       +-------------------+
```

---

## Quickstart & Installation

### Try in Browser (Zero Installation)

Test Raylings directly inside your web browser without installing any tools or starting a local daemon:

👉 **[⚡ Try in Browser](https://dnf0.github.io/raylings/playground/)** — Run Python 3.12, Monaco Editor, and in-memory Ray simulation 100% client-side via Pyodide WebAssembly.

### Prerequisites

- Python `>= 3.10`
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip` / `pipx`
- *Optional (for multi-node KubeRay exercises)*: `kubectl`, `helm`, and a local cluster (`kind`, `minikube`, or `k3d`)

### Running Instantly (No Clone Needed)

You can run Raylings anywhere using [`uvx`](https://docs.astral.sh/uv/) or [`pipx`](https://pipx.pypa.io/stable/):

```bash
# Launch the interactive guided onboarding tour
uvx raylings tour

# Run preflight system & cluster diagnostics
uvx raylings doctor

# Initialize exercises in your current folder
uvx raylings init

# Launch the full-screen interactive TUI
uvx raylings tui

# Or start the background file watcher
uvx raylings watch
```

Or install globally:

```bash
pipx install raylings
raylings tour
raylings init
raylings watch
```

> 📖 **New to Raylings?** Check out the [**Complete Onboarding & Learner's Guide**](https://dnf0.github.io/raylings/onboarding-guide/) for a visual step-by-step tutorial!

### Local Development Installation

Clone the repository and install dependencies in editable mode:

#### Using `uv` (Fastest)

```bash
git clone https://github.com/dnf0/raylings.git
cd raylings
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Using Standard `pip`

```bash
git clone https://github.com/dnf0/raylings.git
cd raylings
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Verify your installation:

```bash
raylings --help
```

---

## Interactive Learning Commands

### 1. Interactive Onboarding Tour (`raylings tour`)

Launch the rich, 5-step terminal walkthrough with live environment probes, workflow introduction, and guided `basics01` resolution:

```bash
raylings tour
# or run non-interactively / output json
raylings tour --non-interactive
raylings tour --step 3
raylings tour --json
```

### 2. Interactive Full-Screen Split-Pane TUI (`raylings tui`)

Explore the curriculum, preview syntax-highlighted code with line numbers, inspect live telemetry, and trigger evaluations inside a split-pane full-screen terminal interface:

```bash
raylings tui
```

| Key | Action | Description |
| :---: | :--- | :--- |
| `[r]` | **Run** | Execute active exercise and view execution diagnostics. |
| `[h]` | **Hint** | Toggle layered progressive hints drawer. |
| `[j]` / `[↓]` / `[n]` | **Next** | Navigate to the next exercise. |
| `[k]` / `[↑]` / `[p]` | **Previous** | Navigate to the previous exercise. |
| `[t]` | **Telemetry** | Open live Ray cluster resource & Plasma memory inspector overlay. |
| `[d]` | **Doctor** | Open preflight system diagnostics overlay. |
| `[q]` | **Quit** | Exit the TUI. |

### 3. Live Background Watcher (`raylings watch`)

Start the interactive development loop. Whenever you save an exercise in `exercises/`, Raylings immediately evaluates your changes (< 50ms):

```bash
raylings watch
```

> **Interactive Hotkeys**:
> - `n` / `Enter` : Advance to next exercise
> - `p` : Navigate to previous exercise
> - `h` : Reveal progressive hint tier
> - `r` : Force rerun current exercise
> - `l` : List curriculum exercises
> - `q` : Exit watcher

### 4. Cluster Health & Telemetry Inspector (`raylings top`)

Inspect your local Ray cluster's live Plasma memory allocations, object spill rates, CPU/GPU core saturation, and instantiated actor tables in real time:

```bash
raylings top --interval 0.5
# or output a one-shot JSON snapshot:
raylings top --json
```

### 5. Preflight System & Ray Diagnostics (`raylings doctor`)

Audit your local environment, Python runtime, Ray installation, shared memory (`/dev/shm`), and cluster connectivity:

```bash
raylings doctor
# or output machine-readable json
raylings doctor --json
```

### 6. Exercise Scaffolding Tool (`raylings new`)

Generate new exercise and solution boilerplate matching Raylings pedagogical standards with a single command:

```bash
raylings new 15 vllm05 --title "Speculative Decoding" --description "Coordinate draft model worker actors."
```

### 7. Pluggable Curriculum Extension Registry (`raylings plugins`)

Discover, inspect, and validate external domain-specific curriculum packs (e.g., Chapter 18 Quantitative Finance):

```bash
# List all registered curriculum plugins
raylings plugins list

# Inspect detailed metadata and syllabus of a plugin
raylings plugins info finance

# Validate custom plugin pack manifests and exercise code
raylings plugins validate path/to/my_plugin.py
```

### 8. Cloud & KubeRay Multi-Node Testing (`scripts/kuberay/`)

Deploy ephemeral 3-node KinD clusters and verify distributed execution across real Kubernetes worker pods:

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

### 9. Run a Single Exercise (`raylings run`)

Execute and evaluate a single exercise directly:

```bash
raylings run basics01
```

### 10. Progressive Hints (`raylings hint`)

Get step-by-step clues for any exercise:

```bash
raylings hint basics01
```

### 11. List All Chapters & Progress (`raylings list` & `raylings progress`)

Browse the entire curriculum syllabus or check your completion progress:

```bash
raylings list
raylings progress
```

### 12. Test Reference Solutions (`raylings test`)

Run built-in automated verification across all 81 reference solutions:

```bash
raylings test
```

---

## VS Code & Cursor Extension 💻

Raylings provides an official extension for **Visual Studio Code** and **Cursor** that turns your editor into a fully integrated distributed AI learning IDE.

### ✨ Extension Features

- 🗺️ **Interactive Welcome Walkthrough**: Built-in editor walkthrough (`Raylings: Open Welcome Walkthrough`) guiding you through curriculum navigation, preflight diagnostics, and first exercise resolution.
- 📚 **Activity Bar Curriculum Tree View**: Browse all 18 chapters and 81 exercises directly from the sidebar with real-time pass/fail status and chapter completion counters.
- 📊 **Status Bar Progress Indicator**: Persistent status bar item showing your total completion percentage, current progress, and next active exercise. Click to jump straight to the code.
- ⚡ **On-Save Diagnostics**: Automatic in-editor validation whenever you save an exercise (`exercises/**/*.py`), surfacing distributed exceptions, assertion failures, or Raylet deadlocks.
- 💡 **Code Actions & Quick Fixes**: Lightbulb quick fixes directly on errors to:
  - **Reveal Hint**: Display progressive hints in the editor without spoiling the answer.
  - **Compare with Reference Solution**: Instantly open a side-by-side diff comparing your exercise code against the official reference solution.
- 🔍 **Solution Diffing**: Interactive diff viewer (`raylings.showSolutionDiff`) for visual code comparison.
- 💻 **Integrated Terminal Watch Mode**: Launch `raylings watch` or `raylings tui` into a dedicated integrated terminal with a single click.

### 📦 Extension Installation

#### Via Command Line (VSIX)

```bash
# For VS Code
code --install-extension dist/raylings-vscode.vsix

# For Cursor
cursor --install-extension dist/raylings-vscode.vsix
```

#### Via Editor UI (VSIX)

1. Open the Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`).
2. Click the **`...`** (Views and More Actions) menu in the top-right corner of the Extensions pane.
3. Select **Install from VSIX...** and choose `dist/raylings-vscode.vsix` (available from the repository root after packaging or downloaded from GitHub Releases).

---

## Curriculum & Syllabus

Raylings covers 18 structured chapters with **81 practical exercises**:

| Chapter | Title | Topic Overview | Exercises |
| :--- | :--- | :--- | :--- |
| **01** | **Ray Core Foundations** | `ray.init()` mechanics, `@ray.remote` tasks, `ObjectRef` futures, parallel task graphs, non-blocking `ray.wait()`, and multiple return values. | `basics01` – `basics06` (6) |
| **02** | **Distributed State & Actors** | Stateful actor classes, method serialization, actor handles, async actors, threaded actors, detached named actors, and dynamic actor pools. | `actors01` – `actors07` (7) |
| **03** | **Plasma Object Store & Zero-Copy** | Plasma in-memory shared memory, zero-copy NumPy/PyArrow transfers, `ray.put()`, object pinning, disk spilling, and serialization closures. | `object_store01` – `object_store06` (6) |
| **04** | **Scheduling & Placement Groups** | Fractional CPU/GPU resources, custom resource tags, node affinity, `STRICT_SPREAD`, `STRICT_PACK`, gang scheduling, and runtime environments. | `scheduling01` – `scheduling06` (6) |
| **05** | **Fault Tolerance & Recovery** | Automatic task retries (`max_retries`), actor restart policies (`max_restarts`), lineage reconstruction, and spot instance preemption handling. | `fault01` – `fault04` (4) |
| **06** | **Cluster Architecture & Simulation** | Head vs worker node roles, Global Control Store (GCS), Raylet schedulers, multi-node testing with `ray.cluster_utils.Cluster`, and Ray Job Submission API. | `cluster01` – `cluster04` (4) |
| **07** | **Patterns & Anti-Patterns** | Fixing nested `ray.get()` blocking, task batching/chunking, actor bottleneck elimination, and tree-structured distributed aggregations. | `antipattern01` – `antipattern04` (4) |
| **08** | **Ray Data (ETL & Batch)** | Ray Datasets, block partitioning, `map_batches` with PyArrow/NumPy, `ActorPoolStrategy`, streaming backpressure, and PyTorch dataloader interop. | `data01` – `data05` (5) |
| **09** | **ML Primitives from Scratch** | Distributed parameter servers, async vs sync parameter updates, ring all-reduce gradient communication, and distributed linear regression trainers. | `ml_scratch01` – `ml_scratch04` (4) |
| **10** | **Ray Train (PyTorch DDP)** | `TorchTrainer`, `ScalingConfig`, distributed dataloaders, multi-worker gradient synchronization, and distributed checkpointing. | `train01` – `train04` (4) |
| **11** | **Ray Tune (Hyperparameter Optimization)** | Hyperparameter search spaces, distributed trial execution, ASHA / HyperBand early stopping schedulers, and Population-Based Training (PBT). | `tune01` – `tune03` (3) |
| **12** | **Ray Serve (Model Deployment)** | `@serve.deployment` decorators, HTTP ingress handlers, dynamic request batching (`@serve.batch`), multi-model pipeline DAGs, and autoscaling replicas. | `serve01` – `serve05` (5) |
| **13** | **Observability & Debugging** | Chrome execution timelines (`ray timeline`), memory allocation profiling (`ray memory`), Prometheus metrics, and GCS actor table dumps. | `perf01` – `perf03` (3) |
| **14** | **KubeRay on Kubernetes** | RayCluster CRDs, RayJob batch lifecycles, RayService rolling zero-downtime serving, KEDA autoscaling, and pod eviction recovery. | `kuberay01` – `kuberay05` (5) |
| **15** | **Distributed LLM Serving & vLLM** | Tensor parallelism weight sharding across Ray worker actors, PagedAttention KV-cache block tables, dynamic multi-LoRA adapters, and speculative decoding. | `vllm01` – `vllm04` (4) |
| **16** | **DeepSpeed & PyTorch FSDP** | PyTorch FSDP with Ray Train `ScalingConfig`, DeepSpeed ZeRO-1/ZeRO-2/ZeRO-3 memory partitioning, mixed precision & activation checkpointing, and elastic checkpoints. | `fsdp01` – `fsdp04` (4) |
| **17** | **Multimodal & Vector Ray Data** | Streaming multimodal image and audio ETL, GPU-accelerated batch embedding extraction with `ActorPoolStrategy`, dynamic sequence length bucketing, and parallel vector DB ingestion. | `data_genai01` – `data_genai04` (4) |
| **18** | **Distributed Quantitative Finance** | Distributed Monte Carlo Black-Scholes option pricing, historical Value at Risk (VaR) & CVaR risk simulation, and streaming market tick analytics & rolling VWAP. | `finance01` – `finance03` (3) |

---

## 🌐 The *lings Ecosystem

If you enjoy the hands-on, terminal-driven learning loop of **Raylings**, explore the other interactive platforms in our `*lings` suite:

- ☸️ [**Kubelings**](https://github.com/dnf0/kubelings) – Master Kubernetes from scratch through interactive YAML manifests, operators, sidecars, and cluster incident drills.
- 🏗️ [**Terralings**](https://github.com/dnf0/terralings) – Master Terraform and OpenTofu through interactive infrastructure-as-code exercises.
- 🇪🇸 [**Spanglings**](https://github.com/dnf0/spanglings) – Developer-grade CLI & interactive TUI for learning intermediate-to-advanced Spanish (B1–C1).
- ⚡ [**Raylings**](https://github.com/dnf0/raylings) – Learn distributed AI, Ray Core actors, and scalable clusters through hands-on Python exercises.

> *All projects in the `*lings` suite are deeply inspired by the pioneering terminal-based pedagogy of [Rustlings](https://github.com/rust-lang/rustlings) and [Ziglings](https://codeberg.org/ziglings/exercises).*

---

## Contributing

We welcome contributions, new exercises, bug fixes, and documentation improvements! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup, exercise authoring standards, and test instructions.

---

## License

Raylings is distributed under the terms of the [Apache-2.0](LICENSE) license.
