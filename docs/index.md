# Raylings ⚡

**An interactive, client-side WebAssembly learning platform and comprehensive reference manual for Python Ray.**

[![Playground](https://img.shields.io/badge/Playground-⚡%20Launch%20Interactive%20IDE-blueviolet)](playground/index.html)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Curriculum](https://img.shields.io/badge/Curriculum-18%20Chapters%20%7C%2081%20Exercises-brightgreen)](syllabus.md)

---

## ⚡ The Modern Way to Master Distributed Ray

Raylings combines a **zero-install, 100% client-side WebAssembly interactive playground** with **18 comprehensive architectural reference guides** spanning distributed tasks, actors, plasma memory, Ray Data, PyTorch Train, Serve, vLLM, and KubeRay.

<div class="grid cards" markdown>

-   :material-play-circle-outline: **Zero-Install Web IDE**
    ---
    Run Monaco Editor, Pyodide WebAssembly (Python 3.12), and real-time Ray cluster simulation 100% in your browser. No Python environment setup, no cluster configuration, and no cloud GPU costs required.
    
    [**Launch Playground →**](playground/index.html){ .md-button .md-button--primary }

-   :material-book-open-page-variant-outline: **18-Chapter Reference Manual**
    ---
    Deep architectural documentation, annotated Python API anatomy, production best practices, and diagnostic troubleshooting workflows for modern distributed systems.

    [**Explore Reference Guides →**](#comprehensive-18-chapter-reference-guides){ .md-button }

</div>

---

## 📚 Comprehensive 18-Chapter Reference Guides

Explore in-depth architectural guides and launch linked practice exercises directly into the playground:

<div class="grid cards" markdown>

-   ### Ray Core & Distributed Memory
    ---
    - [**01. Remote Tasks & Futures**](guides/01-tasks.md) &bull; `@ray.remote`, ObjectRefs, async execution, batching
    - [**02. Stateful Actors & Concurrency**](guides/02-actors.md) &bull; Remote classes, state tracking, concurrency groups
    - [**03. Plasma Object Store**](guides/03-object-store.md) &bull; Shared memory, `ray.put()`, zero-copy Apache Arrow
    - [**04. Resource Scheduling**](guides/04-resources-scheduling.md) &bull; Fractional CPUs/GPUs, custom tags, placement groups
    - [**05. Fault Tolerance & Lineage**](guides/05-fault-tolerance.md) &bull; Task retries, actor restarts, lineage recovery
    - [**06. Cluster Architecture & GCS**](guides/06-cluster-architecture.md) &bull; Head node, raylets, Global Control Store
    - [**07. Design Patterns & Anti-Patterns**](guides/07-patterns-and-antipatterns.md) &bull; Tree aggregation, actor pipelines

-   ### Distributed Data & Scalable ML
    ---
    - [**08. Streaming Ray Data**](guides/08-ray-data.md) &bull; Block partitions, `map_batches`, streaming pipelines
    - [**09. Distributed ML from Scratch**](guides/09-distributed-ml.md) &bull; Parameter Servers, Ring All-Reduce, worker shards
    - [**10. PyTorch Distributed (Ray Train)**](guides/10-ray-train.md) &bull; `TorchTrainer`, DDP, fault-tolerant checkpoints
    - [**11. Hyperparameter Search (Ray Tune)**](guides/11-ray-tune.md) &bull; Search spaces, ASHA early stopping, trial tuners
    - [**12. Production Serving (Ray Serve)**](guides/12-ray-serve.md) &bull; `@serve.deployment`, HTTP ingress, dynamic batching

-   ### Observability & Cloud Orchestration
    ---
    - [**13. Observability, Tracing & Profiling**](guides/13-observability.md) &bull; Ray Dashboard, OpenTelemetry spans, metrics
    - [**14. Kubernetes AI with KubeRay**](guides/14-kuberay.md) &bull; `RayCluster`, `RayJob`, `RayService`, GPU pod groups

-   ### Generative AI, LLMs & High Performance
    ---
    - [**15. High-Throughput vLLM Serving**](guides/15-vllm-and-llms.md) &bull; PagedAttention KV cache, continuous batching
    - [**16. Multi-Node LLM Training (FSDP)**](guides/16-fsdp-deepspeed.md) &bull; ZeRO-3 parameter sharding, mixed precision
    - [**17. Multimodal Embeddings & Vector RAG**](guides/17-multimodal-vectors.md) &bull; Distributed chunking, vector indexing
    - [**18. Quantitative Finance Risk Engines**](guides/18-quant-finance.md) &bull; Monte Carlo Black-Scholes, VaR simulation

</div>

---

## 💡 How the Playground Works

The Raylings web playground runs entirely on client-side WebAssembly technology:

```mermaid
flowchart LR
    Monaco["Monaco Editor<br/>(User Code)"] -->|"1. postMessage"| Worker["Web Worker<br/>(Pyodide Wasm)"]
    Worker -->|"2. Simulated Ray Cluster"| Engine["Wasm Ray Engine<br/>(Tasks, Actors, Plasma)"]
    Engine -->|"3. Verification"| Tester["Harness Validator & Hints"]
    Tester -->|"4. Stream Output (<5ms)"| Term["xterm.js Terminal Output"]

    style Monaco fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style Worker fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style Engine fill:#1e1e38,stroke:#34d399,stroke-width:2px,color:#f8fafc
    style Tester fill:#1e293b,stroke:#f59e0b,stroke-width:1px,color:#f8fafc
    style Term fill:#1e1e38,stroke:#c084fc,stroke-width:2px,color:#f8fafc
```

> **Diagram Walkthrough & Core Concepts:**
> - **100% Client-Side WebAssembly**: Python code executes in a dedicated browser Web Worker powered by Pyodide, requiring zero external server backends or API keys.
> - **In-Browser Ray Simulation**: The `raylings.wasm_compat` runtime accurately emulates `@ray.remote` tasks, stateful actor mailboxes, and Plasma shared memory locally in your browser.
> - **Sub-5ms Terminal Feedback**: Code execution, assertion evaluations, and contextual diagnostic hints stream directly to the xterm.js terminal with instant interactive feedback.

1. **Instant Execution**: Python code compiles and evaluates inside a background Web Worker running Pyodide v0.26 WebAssembly.
2. **Local Cluster Simulation**: The pure-Python Ray compatibility engine simulates `@ray.remote` tasks, stateful actors, Plasma shared memory, and cluster stats directly in your browser.
3. **Zero Backend Required**: All state is stored locally via `localStorage`. Work completely offline on airplanes, trains, or behind corporate air-gaps.
