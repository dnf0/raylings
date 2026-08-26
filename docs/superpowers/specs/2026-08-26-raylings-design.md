# Raylings: An Interactive Hands-On Ray Learning Environment

**Date:** 2026-08-26  
**Status:** Approved  
**Target Repository:** `dnf0/raylings`  

---

## 1. Executive Summary & Vision

`raylings` is an interactive, terminal-driven educational tool and curriculum designed to teach Python Ray from the ground up—inspired by the pedagogy and developer experience of `rustlings` and `ziglings`.

Learners progress through progressively challenging exercises where they fix broken code, fill in missing distributed patterns, resolve performance bottlenecks, debug memory leaks, and build real distributed systems (from simple remote functions to multi-node cluster simulators, distributed parameter servers, PyTorch DDP pipelines, and production Ray Serve DAGs).

---

## 2. System Architecture

```
                                +-----------------------------+
                                |      Learner Terminal       |
                                |       raylings watch        |
                                +--------------+--------------+
                                               |
                                               v
+------------------------------------------------------------------------------------------+
|                                    Raylings CLI Engine                                   |
|                                                                                          |
|  +--------------------+   +-----------------------+   +-------------------------------+  |
|  | File Watcher       |   | Progress / State Mgr  |   | Exercise Runner & Validator   |  |
|  | (watchfiles)       |-->| (exercise index &     |-->| (syntax check, test eval,     |  |
|  |                    |   |  marker parser)       |   |  output capture & assertion)  |  |
|  +--------------------+   +-----------------------+   +---------------+---------------+  |
|                                                                       |                  |
+-----------------------------------------------------------------------|------------------+
                                                                        |
                                       +--------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------------------+
|                                Ray Runtime & Cluster Layer                               |
|                                                                                          |
|  +---------------------------------------------+  +-----------------------------------+  |
|  | Background Shared Ray Session Daemon        |  | Isolated Subprocess Mode          |  |
|  | - Instant ~30ms reconnect per exercise      |  | - Custom cluster topology tests   |  |
|  | - Auto-cleans object store & named actors   |  | - Multi-node simulation (Cluster) |  |
|  +---------------------------------------------+  +-----------------------------------+  |
|                                                                                          |
+------------------------------------------------------------------------------------------+
```

### 2.1 Core Components

1. **CLI Engine (`raylings/cli.py`, `raylings/runner.py`, `raylings/watcher.py`, `raylings/ui.py`)**:
   - Built on `typer` and `rich`.
   - Manages interactive command modes (`watch`, `run`, `test`, `hint`, `list`, `verify`).
   - Renders clean, color-coded terminal diagnostics, stack traces, progress bars, and congratulatory ASCII banners.

2. **Ray Lifecycle Daemon (`raylings/daemon.py`)**:
   - Launches a headless local Ray instance in the background during `raylings watch` or reuses an existing session.
   - Allows exercises to attach in <50ms without the 2s cold-start penalty of `ray.init()`.
   - Cleans up state between runs (detaches actors, flushes plasma references).
   - Gracefully shuts down on watcher exit (`SIGINT` / `Ctrl+C`).

3. **Exercise Manifest & Registry (`raylings/manifest.py`)**:
   - Declarative catalogue of all 13 chapters and 50+ exercises with titles, paths, prerequisites, and progressive hints.
   - Parses `# I AM NOT DONE` marker at the top of exercise files.

4. **Canonical Solutions & Testing Harness (`solutions/`, `tests/`)**:
   - `solutions/` mirrors every exercise file in `exercises/` with fully functional, verified implementations.
   - Pytest test suite validates that:
     - All solutions pass verification on a real Ray runtime.
     - All starter exercises in `exercises/` fail before the user fixes them (preventing accidental no-op exercises).
     - The CLI runner and watcher components work correctly.

---

## 3. Curriculum & Syllabus Specification

The curriculum is divided into 13 numbered chapters spanning fundamental tasks to advanced production systems:

### Chapter 1: Ray Core Foundations (Tasks & Futures)
- `exercises/01_basics/basics01.py`: `ray.init()` mechanics, local vs cluster connection, core worker concepts.
- `exercises/01_basics/basics02.py`: `@ray.remote` tasks, `ObjectRef` vs Python values, non-blocking futures.
- `exercises/01_basics/basics03.py`: Parallel pipeline topologies & latency benchmarking vs multiprocessing.
- `exercises/01_basics/basics04.py`: Passing `ObjectRef`s into tasks (direct task dependency graphs without `ray.get()`).
- `exercises/01_basics/basics05.py`: `ray.wait()` for dynamic streaming results and timeout handling.
- `exercises/01_basics/basics06.py`: Multiple return values with `@ray.remote(num_returns=N)`.

### Chapter 2: Distributed State & Actors
- `exercises/02_actors/actors01.py`: Stateful actor lifecycle & remote class instantiations.
- `exercises/02_actors/actors02.py`: Actor method calls, sequential queueing, and state mutation.
- `exercises/02_actors/actors03.py`: Actor handles: passing actor references between tasks & other actors.
- `exercises/02_actors/actors04.py`: Async Actors (`async def` methods, `max_concurrency`, non-blocking I/O).
- `exercises/02_actors/actors05.py`: Threaded Actors (Python thread pool concurrency for blocking C extensions).
- `exercises/02_actors/actors06.py`: Detached Named Actors (`lifetime="detached"`, namespaces, cross-job lookup).
- `exercises/02_actors/actors07.py`: `ActorPool` pattern for dynamic load balancing across stateful workers.

### Chapter 3: Plasma Object Store, Zero-Copy & Serialization
- `exercises/03_object_store/object_store01.py`: Plasma in-memory store architecture & zero-copy NumPy/PyArrow reads.
- `exercises/03_object_store/object_store02.py`: `ray.put()` vs implicit serialization: avoiding repetitive copying.
- `exercises/03_object_store/object_store03.py`: Object pinning, reference counting, and avoiding OOM memory leaks.
- `exercises/03_object_store/object_store04.py`: Object spilling to disk when Plasma store exceeds memory capacity.
- `exercises/03_object_store/object_store05.py`: Serialization traps: closures capturing large globals vs explicit refs.
- `exercises/03_object_store/object_store06.py`: Custom serializers and out-of-band buffers with `ray.util.register_serializer`.

### Chapter 4: Advanced Resource Scheduling & Placement Groups
- `exercises/04_scheduling_resources/scheduling01.py`: Fractional resources (`num_cpus=0.5`, `num_gpus=0.25`) & custom resource tags.
- `exercises/04_scheduling_resources/scheduling02.py`: Node affinity scheduling (`NodeAffinitySchedulingStrategy`).
- `exercises/04_scheduling_resources/scheduling03.py`: Placement groups: `STRICT_SPREAD` (anti-affinity across physical nodes).
- `exercises/04_scheduling_resources/scheduling04.py`: Placement groups: `STRICT_PACK` (co-locating tasks for high-bandwidth interconnect).
- `exercises/04_scheduling_resources/scheduling05.py`: Gang scheduling with multi-bundle Placement Groups (all-or-nothing scheduling).
- `exercises/04_scheduling_resources/scheduling06.py`: Dynamic runtime environments (`runtime_env` pip/conda/env vars/working_dir).

### Chapter 5: Fault Tolerance, Lineage & Recovery
- `exercises/05_fault_tolerance/fault01.py`: Automatic task retries (`max_retries`, `retry_exceptions`).
- `exercises/05_fault_tolerance/fault02.py`: Actor failure recovery (`max_restarts`, `max_task_retries`).
- `exercises/05_fault_tolerance/fault03.py`: Lineage reconstruction: how Ray reconstructs lost object store values automatically.
- `exercises/05_fault_tolerance/fault04.py`: Spot instance handling & node preemption simulation.

### Chapter 6: Cluster Topology & Multi-Node Simulation
- `exercises/06_cluster_architecture/cluster01.py`: Head node vs Worker nodes, GCS (Global Control Store), Raylets.
- `exercises/06_cluster_architecture/cluster02.py`: Programmatic multi-node cluster testing with `ray.cluster_utils.Cluster`.
- `exercises/06_cluster_architecture/cluster03.py`: Simulating node death, node addition, and rescheduling.
- `exercises/06_cluster_architecture/cluster04.py`: Ray Job Submission API (`JobSubmissionClient`) and cluster packaging.

### Chapter 7: Production Patterns & Anti-Patterns
- `exercises/07_patterns_and_antipatterns/antipattern01.py`: Fixing the `ray.get()`-inside-task anti-pattern (deadlocks & wasted parallelism).
- `exercises/07_patterns_and_antipatterns/antipattern02.py`: Fixing fine-grained task overhead (batching small tasks into optimal chunks).
- `exercises/07_patterns_and_antipatterns/antipattern03.py`: Fixing actor bottlenecks with worker pooling & async pipelining.
- `exercises/07_patterns_and_antipatterns/antipattern04.py`: Nested remote calls and tree-structured aggregation (Tree-Reduce).

### Chapter 8: Ray Data for High-Throughput Distributed ETL
- `exercises/08_ray_data/data01.py`: Ray Datasets, block partitioning, and lazy execution DAGs.
- `exercises/08_ray_data/data02.py`: `map` vs `map_batches` (zero-copy PyArrow & NumPy vectorization).
- `exercises/08_ray_data/data03.py`: Stateful transformations with `ActorPoolStrategy` (GPU/Model batching).
- `exercises/08_ray_data/data04.py`: Streaming pipelines with backpressure & memory capping.
- `exercises/08_ray_data/data05.py`: Interop with PyTorch: `iter_torch_batches()`, zero-copy tensor streaming to GPU.

### Chapter 9: Distributed ML Primitives from Scratch
- `exercises/09_ml_from_scratch/ml_scratch01.py`: Building a Distributed Parameter Server actor from scratch with worker tasks.
- `exercises/09_ml_from_scratch/ml_scratch02.py`: Asynchronous vs Synchronous Parameter Updates & Gradient Averaging.
- `exercises/09_ml_from_scratch/ml_scratch03.py`: Implementing Ring All-Reduce communication across Ray Actors.
- `exercises/09_ml_from_scratch/ml_scratch04.py`: Building a Distributed Data-Parallel Trainer from scratch.

### Chapter 10: Ray Train & Distributed Deep Learning (PyTorch)
- `exercises/10_ray_train_and_tune/train01.py`: PyTorch `TorchTrainer` & `ScalingConfig` (Distributed Data Parallelism).
- `exercises/10_ray_train_and_tune/train02.py`: Distributed DataLoader streaming via Ray Data (`DataConfig`).
- `exercises/10_ray_train_and_tune/train03.py`: Multi-GPU worker gradient synchronization & distributed metrics.
- `exercises/10_ray_train_and_tune/train04.py`: Distributed model checkpointing to cloud storage and fault recovery.

### Chapter 11: Ray Tune (Scalable Hyperparameter Optimization)
- `exercises/11_ray_tune/tune01.py`: Tune search spaces and distributed trial execution.
- `exercises/11_ray_tune/tune02.py`: Early-stopping schedulers (ASHA / HyperBand).
- `exercises/11_ray_tune/tune03.py`: Population-Based Training (PBT) for dynamic hyperparameter schedules.

### Chapter 12: Ray Serve & Production Model Deployment
- `exercises/12_ray_serve/serve01.py`: `@serve.deployment` decorator, HTTP ingress, and deployment handles.
- `exercises/12_ray_serve/serve02.py`: Dynamic Request Batching (`@serve.batch` with windowing & max batch size).
- `exercises/12_ray_serve/serve03.py`: Multi-Model Composable Pipelines (DAGs: Tokenizer -> Embedding -> LLM/Classifier).
- `exercises/12_ray_serve/serve04.py`: Streaming LLM responses (FastAPI + Ray Serve generator streams).
- `exercises/12_ray_serve/serve05.py`: Autoscaling policies (target replica queue length, min/max replicas, fractional GPUs).

### Chapter 13: Observability, Profiling & Memory Debugging
- `exercises/13_observability_and_debugging/perf01.py`: Generating and analyzing Chrome execution timelines (`ray timeline`).
- `exercises/13_observability_and_debugging/perf02.py`: Diagnosing memory leaks and plasma usage with `ray memory`.
- `exercises/13_observability_and_debugging/perf03.py`: Using Ray Metrics, Prometheus exports, and GCS task/actor summary dumps.

---

## 4. Exercise & Solution File Structure

Every exercise file follows a consistent convention:

```python
"""
Exercise: exercises/01_basics/basics02.py
Topic: Understanding ObjectRefs and ray.get()

Instructions:
Fix the function below so that both remote tasks run concurrently,
and retrieve their results properly using ray.get().
"""

# I AM NOT DONE

import ray
import time

@ray.remote
def slow_square(x: int) -> int:
    time.sleep(0.1)
    return x * x

def run():
    # TODO: Modify the lines below to launch in parallel and retrieve both results
    ref1 = slow_square.remote(4)
    ref2 = slow_square.remote(5)
    
    # FIX ME: Retrieve results
    result1 = None
    result2 = None
    
    return result1, result2

def verify():
    start = time.time()
    r1, r2 = run()
    duration = time.time() - start
    
    assert r1 == 16, f"Expected 16, got {r1}"
    assert r2 == 25, f"Expected 25, got {r2}"
    assert duration < 0.18, f"Tasks did not run in parallel! Duration: {duration:.2f}s"
    print("✓ basics02 passed!")

if __name__ == "__main__":
    ray.init(ignore_reinit_error=True)
    verify()
```

---

## 5. Repository Infrastructure & CI

### 5.1 Packaging & Environment (`pyproject.toml`)
- Build Backend: `hatchling`
- Entry Point: `[project.scripts] raylings = "raylings.cli:app"`
- Package Manager: `uv`
- Python Version: `>=3.10`
- Core Dependencies:
  - `ray[default]>=2.30.0`
  - `torch>=2.2.0`
  - `rich>=13.7.0`
  - `typer>=0.12.0`
  - `watchfiles>=0.21.0`
  - `numpy>=1.24.0`
  - `pyarrow>=14.0.0`
- Dev Dependencies:
  - `pytest>=8.0.0`
  - `pytest-cov>=4.1.0`
  - `ruff>=0.4.0`
  - `pyright>=1.1.350`
  - `pre-commit>=3.7.0`

### 5.2 Agent Rules & Git Isolation
- Development environment uses `agent-rules` templates locally.
- Strict `.gitignore` ensures that all agent-internal paths (`.agents/`, `.agent-state/`, `.superpowers/`, `graphify-out/`, `.roborev/`, `.claude/`, `.gemini/`) are excluded from commits, keeping `dnf0/raylings` clean and ready for public GitHub publication.

### 5.3 Automated CI Workflow (`.github/workflows/ci.yml`)
- Triggers on push to `main` and pull requests.
- Matrix runs on Python `3.10`, `3.11`, `3.12`.
- Execution Steps:
  1. `uv sync` dependencies.
  2. `ruff check` and `ruff format --check`.
  3. `pyright` type checks on `raylings/` and `solutions/`.
  4. `pytest tests/` verifying that:
     - All solutions in `solutions/` pass verification.
     - All starter exercises in `exercises/` fail as expected.
     - CLI commands and watcher logic pass unit tests.

---

## 6. Verification and Acceptance Criteria

1. **CLI Commands**:
   - `raylings watch` automatically discovers incomplete exercises, monitors edits, re-evaluates in <50ms, and updates live status.
   - `raylings run <path>` runs any exercise or solution.
   - `raylings hint` reveals progressive hints per exercise.
   - `raylings test` verifies all reference solutions.
   - `raylings list` outputs the complete curriculum table with statuses.
2. **Curriculum Completeness**:
   - 13 chapters, 50+ deep-dive exercises with verified matching solutions.
3. **CI & Code Quality**:
   - 100% passing test suite on Python 3.10+.
   - Clean linting (`ruff`) and static typing (`pyright`).
4. **GitHub Deployment Ready**:
   - Remote target: `git@github.com:dnf0/raylings.git` (or HTTPS equivalent).
