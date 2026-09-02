# Design Specification: High-Fidelity Mermaid Architecture & Sequence Diagrams

## 1. Executive Summary & Objective

The Raylings documentation ecosystem currently uses simplified ASCII text boxes in its 18 chapter architectural reference guides (`docs/guides/01-tasks.md` through `docs/guides/18-quant-finance.md`), landing page (`docs/index.md`), and syllabus (`docs/syllabus.md`). While functional, these diagrams do not fully illustrate Ray's low-level distributed systems mechanics—such as **Core Worker direct gRPC communication**, **Raylet worker leasing and scheduling protocols**, **Plasma zero-copy shared memory POSIX IPC**, **GCS metadata pub/sub**, **NCCL gradient synchronization rings**, and **KubeRay Kubernetes Operator reconciliation loops**.

This specification outlines the systematic upgrade of the entire Raylings documentation suite to rich, modern **Mermaid.js** multi-tier architecture diagrams and protocol sequence diagrams, fully leveraging MkDocs Material's native dark/light theme rendering.

---

## 2. Diagram Architecture & Styling Standards

### 2.1 Theme & Styling Guidelines
All Mermaid diagrams will follow a standardized visual taxonomy:
- **Subgraphs for Physical & Process Boundaries**: Explicit subgraphs separating Driver Process, Head Node (GCS, Dashboard), Worker Nodes (Raylet, Plasma Store, Core Workers), GPU hardware, and Kubernetes control planes.
- **Protocol & Network Edge Labels**: Explicit labels on connection edges designating protocols (`gRPC`, `POSIX IPC (Shared Memory)`, `TCP / Heartbeat`, `NCCL Ring`, `Kubernetes API`).
- **Standardized Color Scheme**: Subgraphs and nodes will use clean, themed styling compatible with MkDocs Material dark and light themes:
  - Driver / Ingress: `fill:#1e293b,stroke:#38bdf8,stroke-width:2px`
  - Core Workers / Actors: `fill:#0f172a,stroke:#818cf8,stroke-width:2px`
  - Plasma Object Store / Memory: `fill:#1e1e38,stroke:#c084fc,stroke-width:2px`
  - Raylet / Scheduler: `fill:#1e293b,stroke:#34d399,stroke-width:2px`
  - GCS / Control Plane: `fill:#1e293b,stroke:#f59e0b,stroke-width:2px`

### 2.2 Dual-Visualization Paradigm
Where appropriate, chapters will provide:
1. **Structural Component Architecture (`flowchart TD` or `flowchart LR`)**: Showing memory layouts, process trees, and component boundaries.
2. **Lifecycle & Coordination Protocol (`sequenceDiagram`)**: Showing step-by-step asynchronous messaging, leasing, and object resolution order.

---

## 3. Chapter-by-Chapter Architectural Diagram Specifications

### Part I: Ray Core & Distributed Systems Fundamentals
1. **01. Remote Tasks & Futures (`docs/guides/01-tasks.md`)**:
   - *Flowchart*: Driver Process -> Local Raylet -> Core Worker Pool (Worker Lease) -> Plasma Store Object Allocation.
   - *Sequence Diagram*: Asynchronous Task Submission Protocol (`RequestWorkerLease` -> `ExecuteTask` via direct gRPC -> `PutObject` -> `ReturnObjectRef`).

2. **02. Stateful Actors & Concurrency (`docs/guides/02-actors.md`)**:
   - *Flowchart*: Actor Lifecycle (Driver -> Raylet Actor Creation -> Dedicated Worker Process with In-Memory State -> Direct Worker-to-Worker gRPC calls).
   - *Sequence Diagram*: Threaded / Async Actor Queueing (`async def` concurrent task interleaving vs sync FIFO execution).

3. **03. Plasma Object Store & Memory Management (`docs/guides/03-object-store.md`)**:
   - *Flowchart*: Plasma Shared Memory (`/dev/shm` POSIX IPC), Zero-Copy Deserialization with PyArrow/NumPy, Object Directory in Raylet/GCS, Object Spilling to Local SSD / S3.
   - *Sequence Diagram*: `ray.put()` and `ray.get()` zero-copy pointer retrieval and fallback cross-node object pulling.

4. **04. Scheduling, Resources & Placement Groups (`docs/guides/04-resources-scheduling.md`)**:
   - *Flowchart*: Two-tier Scheduling (Local Raylet Scheduler -> Node Manager -> Global Resource Scheduling via GCS), Placement Groups (`STRICT_SPREAD`, `STRICT_PACK`).

5. **05. Lineage Reconstruction & Fault Tolerance (`docs/guides/05-fault-tolerance.md`)**:
   - *Flowchart*: Object Lineage DAG tracking, Worker Crash Detection, Raylet Heartbeat Failure Domain, Lineage-based Task Replay.
   - *Sequence Diagram*: Actor Reconstruction Protocol (`max_restarts` policy, state restoration from checkpoint).

6. **06. Cluster Architecture & Global Control Store (`docs/guides/06-cluster-architecture.md`)**:
   - *Flowchart*: Cluster Topology: Head Node (GCS, Redis/Internal KV, Dashboard API Server, Cluster Autoscaler) and Worker Nodes (Raylet, Plasma Store Daemon, Python Core Workers).

7. **07. Production Patterns & Anti-Patterns (`docs/guides/07-patterns-and-antipatterns.md`)**:
   - *Flowchart*: Comparison: Anti-Pattern (Nested `ray.get()` blocking worker process slots and stalling driver) vs Production Pattern (Direct `ObjectRef` DAG pipelining).

---

### Part II: Distributed Data & Machine Learning Frameworks
8. **08. Streaming Ray Data (`docs/guides/08-ray-data.md`)**:
   - *Flowchart*: Streaming Execution Graph, Block Partitioning (`Block`, `BlockRef`), Streaming Pipeline Operators (`map_batches`, `filter`, `repartition`), ActorPool Execution.

9. **09. Distributed Machine Learning from Scratch (`docs/guides/09-distributed-ml.md`)**:
   - *Flowchart*: Parameter Server Architecture (Parameter Server Actor + Worker Actors) vs AllReduce Ring Topology for distributed SGD.

10. **10. Distributed PyTorch with Ray Train (`docs/guides/10-ray-train.md`)**:
    - *Flowchart*: `TorchTrainer` Coordinator -> `ScalingConfig` Worker Group Actors -> PyTorch DDP / FSDP Process Group -> High-Speed NCCL Inter-GPU Gradient Sync Ring.

11. **11. Hyperparameter Tuning with Ray Tune (`docs/guides/11-ray-tune.md`)**:
    - *Flowchart*: `Tuner` Driver -> Search Algorithm -> TrialRunner Actor -> Trial Executor Actors -> ASHA / Median Early Stopping Scheduler.

12. **12. High-Performance Model Serving with Ray Serve (`docs/guides/12-ray-serve.md`)**:
    - *Flowchart*: Serve Controller -> HTTP/gRPC Ingress Proxy -> Router / Replica Actors -> Dynamic Request Batching & Horizontal Pod Autoscaling.

---

### Part III: Observability, Cloud Orchestration & Enterprise Scale
13. **13. Observability, Tracing & Profiling (`docs/guides/13-observability.md`)**:
    - *Flowchart*: OpenTelemetry Tracing Pipeline, Raylet Prometheus Exporters, GCS Event Streams, Ray Dashboard Control Plane.

14. **14. Kubernetes AI with KubeRay (`docs/guides/14-kuberay.md`)**:
    - *Flowchart*: Kubernetes Control Plane (KubeRay Operator Controller) -> `RayCluster` CRD Reconciliation -> Head Pod (GCS, Dashboard) + Worker Pods StatefulSets/Deployments.

15. **15. High-Throughput vLLM & LLM Serving (`docs/guides/15-vllm-and-llms.md`)**:
    - *Flowchart*: Ray Serve Ingress -> Tensor-Parallel vLLM Worker Engine -> PagedAttention Distributed KV-Cache Memory Blocks -> Continuous Iteration-Level Batching.

16. **16. Multi-Node LLM Training with FSDP & DeepSpeed (`docs/guides/16-fsdp-deepspeed.md`)**:
    - *Flowchart*: ZeRO-3 Memory Sharding: Sharded Parameters, Gradients, and Optimizer States across multi-node GPU clusters with Inter-Node AllGather / ReduceScatter.

17. **17. Multimodal Embeddings & Vector RAG (`docs/guides/17-multimodal-vectors.md`)**:
    - *Flowchart*: Dual Modality Ingestion (Text + Vision) -> Ray Data Embedding Batches -> Distributed HNSW Vector Index Actor -> Sub-millisecond ANN Search & Reranking.

18. **18. Quantitative Finance Risk Engines (`docs/guides/18-quant-finance.md`)**:
    - *Flowchart*: Monte Carlo Scenario Dispatcher -> GPU Simulation Workers -> Parallel Pricing Actors -> Fast Map-Reduce Value-at-Risk (VaR) Aggregator.

---

### Part IV: Overview Hub & Syllabus
19. **Overview Hub (`docs/index.md`)**:
    - *Flowchart*: Complete 360° Ray Architecture Map: Applications -> Ray AI Libraries (Data, Train, Tune, Serve, RLlib) -> Ray Core Engine (Tasks, Actors, Objects, Scheduler) -> Infrastructure (KubeRay, Cloud VMs, On-Prem).

20. **Syllabus & Learning Tracks (`docs/syllabus.md`)**:
    - *Flowchart*: 4 Guided Learning Paths:
      - Track 1: Ray Core Engineering (Ch 01–07)
      - Track 2: Distributed Data & ML Systems (Ch 08–12)
      - Track 3: Cloud & Enterprise Infrastructure (Ch 13–14)
      - Track 4: Generative AI & High Performance (Ch 15–18)

---

## 4. Verification & Testing Strategy

1. **MkDocs Build Verification**:
   - Run `uv run mkdocs build --strict` to ensure all Mermaid markdown fences render without syntax warnings or parse errors.
2. **Automated Unit Testing**:
   - Update `tests/test_playground.py` and `tests/` to assert that all 18 guides contain valid ````mermaid` code blocks and no legacy ASCII placeholders.
3. **Browser & Theme Verification**:
   - Verify on local development server (`http://127.0.0.1:8001/raylings/`) that diagrams render with high clarity in both Dark Mode (`scheme: slate`) and Light Mode (`scheme: default`).
