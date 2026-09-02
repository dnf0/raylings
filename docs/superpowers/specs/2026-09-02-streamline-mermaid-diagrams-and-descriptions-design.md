# Design Specification: Streamlining Mermaid Diagrams & Attaching Conceptual Descriptions

**Date:** 2026-09-02  
**Status:** Approved  
**Approach:** Approach 1 (Streamlined Single Diagram + Attached Concept Breakdown)

---

## 1. Problem Statement & Motivation
The previous documentation revision introduced dual-diagram stacks (both a multi-subgraph flowchart and a dense sequence diagram) on every chapter guide page. This resulted in:
1. **Visual Overload & Complexity**: Nested subgraphs, dense multi-line bullet lists within nodes, and redundant sequence diagrams took up excessive vertical space and overwhelmed learners.
2. **Missing Conceptual Explanations**: Diagrams lacked direct textual walkthroughs connecting the visual nodes and edges to the underlying distributed computing principles.

## 2. Goals & Acceptance Criteria
1. **Single High-Level Architecture Diagram per Chapter**:
   - Exactly one focused Mermaid diagram per chapter guide (`docs/guides/01-tasks.md` through `docs/guides/18-quant-finance.md`), as well as `docs/index.md` and `docs/syllabus.md`.
   - Remove redundant sequence diagrams across all guides.
   - Eliminate nested subgraphs and verbose bullet points in node labels (keep node labels to 1–2 lines max).
   - Use clean Top-to-Bottom (`TD`) or Left-to-Right (`LR`) layout with 4–7 key components per diagram.
2. **Attached Concept Descriptions**:
   - Immediately beneath each diagram, include a structured `> **Diagram Walkthrough & Core Concepts:**` block.
   - Explain:
     - **Control & Data Flow**: Step-by-step sequence of events and message passing.
     - **Component Responsibilities**: The role of the Driver, Raylet, Worker, GCS, Plasma, or specialized modules (e.g. Train, Tune, Serve, vLLM).
     - **System Guarantees**: Concurrency semantics, zero-copy memory access, fault tolerance, or latency benefits.
3. **Automated Documentation & Diagram Validation**:
   - Update `tests/test_guide_diagrams.py` to assert that:
     - Every chapter guide contains exactly one clean Mermaid diagram block.
     - Every chapter guide contains the attached `> **Diagram Walkthrough & Core Concepts:**` block.
     - All Mermaid diagrams have valid syntax, no nested subgraphs, and pass lint/build checks.
   - `uv run mkdocs build --strict` builds cleanly.

---

## 3. Chapter-by-Chapter Architectural Diagrams & Descriptions

### Core Ray (Chapters 01–07)
- **01. Remote Tasks (`01-tasks.md`)**:
  - *Diagram*: `Driver` -> `Raylet` (worker lease) -> `Worker` (execution) -> `Plasma Store` (zero-copy return) -> `Driver` (`ray.get`).
  - *Concepts*: Non-blocking dispatch, independent process scheduling, shared memory zero-copy transfer.
- **02. Stateful Actors (`02-actors.md`)**:
  - *Diagram*: `Driver` -> `Actor Process` (state store / FIFO mailbox) -> `ObjectRef` returns.
  - *Concepts*: Stateful execution, serialized actor mailbox, state encapsulation across remote calls.
- **03. Plasma Object Store (`03-object-store.md`)**:
  - *Diagram*: `Driver` / `Worker A` -> `Plasma Shared Memory (/dev/shm)` <--> Inter-node Transfer <--> `Worker B`.
  - *Concepts*: Zero-copy Apache Arrow reads, immutable object buffers, transparent inter-node transfers and spillover to disk.
- **04. Resource Scheduling (`04-resources-scheduling.md`)**:
  - *Diagram*: `Task/Actor Request` (`num_cpus`, `num_gpus`) -> `Placement Group` (`STRICT_SPREAD` / `STRICT_PACK`) -> `Cluster Nodes`.
  - *Concepts*: Fractional resource allocation, co-location guarantees, scheduling bundle enforcement.
- **05. Fault Tolerance (`05-fault-tolerance.md`)**:
  - *Diagram*: `Task Failure` -> `Lineage Reconstruction` -> `GCS Lineage Graph` -> `Task Re-execution` -> `Object Restored`.
  - *Concepts*: Deterministic lineage tracking, automatic retry policies (`max_retries`), stateful actor resurrection (`max_restarts`).
- **06. Cluster Architecture & GCS (`06-cluster-architecture.md`)**:
  - *Diagram*: `Head Node (GCS + Dashboard)` <--> gRPC Heartbeats <--> `Worker Nodes (Raylet + Plasma + Workers)`.
  - *Concepts*: Centralized metadata coordination, decoupled local scheduling, cluster heartbeat monitoring.
- **07. Design Patterns & Anti-Patterns (`07-patterns-and-antipatterns.md`)**:
  - *Diagram*: `Tree Reduction Pattern`: Level 0 Tasks -> Intermediate Level 1 Reducers -> Final Aggregated Root.
  - *Concepts*: Avoiding driver bottleneck, logarithmic scaling of reductions, actor batching patterns.

### Distributed ML & Scale (Chapters 08–12)
- **08. Ray Data (`08-ray-data.md`)**:
  - *Diagram*: `Storage Ingestion` -> `Streaming Block Partitioning` -> `map_batches (Actor Pool)` -> `GPU Consumption`.
  - *Concepts*: Streaming block pipelining, vectorized zero-copy batching, memory-bounded execution.
- **09. Distributed ML Patterns (`09-distributed-ml.md`)**:
  - *Diagram*: `Ring All-Reduce Topology`: Ring gradient exchange across worker GPUs.
  - *Concepts*: Decentralized gradient synchronization, NCCL communication, avoidance of single-node parameter bottlenecks.
- **10. PyTorch Distributed / Ray Train (`10-ray-train.md`)**:
  - *Diagram*: `TorchTrainer` -> `Distributed Worker Group (DDP / FSDP)` -> `Object Store Checkpoints`.
  - *Concepts*: Process group initialization, automatic rendezvous, synchronized gradient all-reduce and checkpointing.
- **11. Ray Tune (`11-ray-tune.md`)**:
  - *Diagram*: `Tuner Controller` -> `Search Algorithm (Optuna / Random)` -> `Trial Runners (Concurrent Actors)` -> `ASHA Scheduler (Early Stopping)`.
  - *Concepts*: Asynchronous trial scheduling, dynamic pruning of underperforming configurations, search space exploration.
- **12. Ray Serve (`12-ray-serve.md`)**:
  - *Diagram*: `Client HTTP / gRPC` -> `Serve Controller & Proxy` -> `Replica Deployment Pool (Dynamic Batching)` -> `Streaming Generator Response`.
  - *Concepts*: Decoupled HTTP ingress, micro-batch coalescing (`@serve.batch`), autoscaling replica pools.

### Advanced Observability, Cloud & Generative AI (Chapters 13–18)
- **13. Observability & Tracing (`13-observability.md`)**:
  - *Diagram*: `Raylet & Workers` -> `OpenTelemetry / Prometheus Exporter` -> `Ray Dashboard & Jaeger`.
  - *Concepts*: Distributed tracing spans, real-time node telemetry, task timeline profiling.
- **14. Kubernetes AI with KubeRay (`14-kuberay.md`)**:
  - *Diagram*: `KubeRay Operator` -> `RayCluster CRD` -> `Head Pod` + `Worker Pods (K8s DaemonSets / Deployments)`.
  - *Concepts*: Custom Resource Definitions, automated cloud pod autoscaling, zero-downtime cluster lifecycle.
- **15. vLLM & LLM Serving (`15-vllm-and-llms.md`)**:
  - *Diagram*: `User Prompts` -> `Continuous Batching Engine` -> `PagedAttention KV Cache` -> `Tensor-Parallel GPU Workers`.
  - *Concepts*: Non-contiguous KV cache paging, token-level iteration batching, distributed tensor model sharding.
- **16. Multi-Node LLM Training (FSDP) (`16-fsdp-deepspeed.md`)**:
  - *Diagram*: `Full Model Parameters` -> `ZeRO-3 Sharding (Weights, Gradients, Optimizer States across GPUs)` -> `All-Gather Forward / Backward`.
  - *Concepts*: Eliminating redundant model replication, communication-overlap scheduling, 100B+ parameter scaling.
- **17. Multimodal Embeddings & Vectors (`17-multimodal-vectors.md`)**:
  - *Diagram*: `Multimodal Documents` -> `Ray Data Chunking` -> `Embedding Model Pipeline` -> `Distributed Vector Index`.
  - *Concepts*: Multi-stage parallel ETL, GPU batch inference, sharded vector indexing for RAG.
- **18. Quantitative Finance Risk Engines (`18-quant-finance.md`)**:
  - *Diagram*: `Market Volatility Matrices` -> `Ray Actor Pool (Monte Carlo Simulators)` -> `VaR / CVaR Risk Aggregator`.
  - *Concepts*: High-frequency parameter broadcasting, embarrassingly parallel path generation, sub-millisecond VaR risk evaluation.

---

## 4. Verification & Testing Strategy
1. **Diagram Syntax & Structure Unit Tests** (`tests/test_guide_diagrams.py`):
   - Assert each guide file has exactly 1 `mermaid` code block.
   - Assert presence of `> **Diagram Walkthrough & Core Concepts:**`.
   - Assert all diagrams use valid Mermaid flowchart syntax without nested subgraphs.
2. **Build Documentation**:
   - `uv run mkdocs build --strict`
3. **Test Suite**:
   - `uv run pytest -m "not heavy"`
   - `uv run ruff check docs tests src`
