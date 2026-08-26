# Raylings ⚡

> An interactive, hands-on CLI learning environment for mastering Python Ray from scratch.

Inspired by the pedagogy of [Rustlings](https://github.com/rust-lang/rustlings) and [Ziglings](https://github.com/ziglings/exercises), **Raylings** guides you through progressively challenging distributed computing exercises in Python. You will fix broken code, fill in missing distributed patterns, resolve performance bottlenecks, eliminate memory leaks, and build real-world distributed systems.

---

## What is Raylings?

Ray is a unified framework for scaling AI and Python applications from single laptops to massive multi-node clusters. While powerful, mastering Ray's mental models—futures, stateful actors, Plasma zero-copy memory, dynamic placement groups, and lineage-based fault tolerance—requires hands-on practice.

Raylings provides:
- **Interactive File Watcher**: Edit exercises in your favorite editor; Raylings automatically re-runs and validates your changes on file save.
- **Fast Execution**: Background Ray daemon re-uses a warm local cluster session for sub-50ms exercise turnaround.
- **14 Chapters & 55+ Exercises**: From first remote tasks to distributed parameter servers, PyTorch DDP pipelines, Ray Serve DAGs, and KubeRay on Kubernetes.
- **Progressive Hints & Solutions**: Stuck on an exercise? Get layered hints without spoiling the answer, or inspect canonical solutions when finished.

---

## Quickstart

### Prerequisites
- Python 3.10, 3.11, or 3.12
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

Clone the repository and install dependencies in editable mode:

```bash
git clone https://github.com/dnf0/raylings.git
cd raylings
pip install -e ".[dev]"
```

### Starting the Interactive Watcher

Launch the watcher to start your learning journey:

```bash
raylings watch
```

Raylings will open the first exercise in `exercises/01_basics/basics01.py`. When you remove the `# I AM NOT DONE` marker and fix the code, Raylings automatically tests your solution and advances you to the next challenge.

### CLI Commands

- `raylings watch` — Start continuous watching mode (recommended).
- `raylings run <exercise_name>` — Run and verify a specific exercise.
- `raylings test` — Run automated verification across all exercises.
- `raylings hint <exercise_name>` — Show progressive hints for an exercise.
- `raylings list` — View all chapters, exercises, and completion progress.
- `raylings verify` — Verify full curriculum progress and validate solutions.

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

## Contributing

Contributions are warmly welcome! Whether you are adding new exercises, improving explanations, or fixing bugs, please check out [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup and guidelines.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
