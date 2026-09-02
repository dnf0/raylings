# Design Specification: Standardized Playground & Architectural Reference Documentation

**Date**: 2026-09-02  
**Author**: Daniel Fisher / Raylings Team  
**Status**: Approved  
**Target Repository**: `dnf0/raylings`

---

## 1. Overview & Goal

Standardize the Raylings documentation site structure to match [**Kubelings**](https://github.com/dnf0/kubelings) 1:1 by focusing squarely on the **Zero-Install WebAssembly Interactive Playground** and **18 Comprehensive Architectural Reference Guides**.

This transforms the documentation from a general CLI README into a modern, web-first interactive learning hub and production reference manual for distributed systems engineering with Ray.

---

## 2. Architectural Pillars

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Raylings Web Documentation                      │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Landing Hub (docs/index.md)                   │  │
│  │  • Hero: Zero-Install Interactive WebAssembly IDE Launch         │  │
│  │  • 2 Primary Cards: Playground Launch + 18-Chapter Guides         │  │
│  │  • 4 Thematic Curriculum Grids (Core, ML, Perf/Sec, Cloud/LLM)   │  │
│  │  • Pure Client-Side WebAssembly Architecture Diagram             │  │
│  └──────────────────┬─────────────────────────────┬─────────────────┘  │
│                     │                             │                    │
│                     ▼                             ▼                    │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────┐  │
│  │    Standalone Playground Shell       │  │   18 Chapter Guides     │  │
│  │    (docs/playground/index.html)     │  │   (docs/guides/*.md)    │  │
│  │  • Full-viewport Monaco IDE         │  │  • Wasm Launch CTA      │  │
│  │  • Pyodide v0.26 Web Worker         │  │  • ASCII Flow Diagrams  │  │
│  │  • 18 Chapters | 81 Exercises       │  │  • Annotated API Code   │  │
│  │  • Real-Time Cluster Telemetry      │  │  • Best Practices & Fix │  │
│  │  • Client-Side State Persistence    │  │  • Linked Exercises     │  │
│  └─────────────────────────────────────┘  └─────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1. Landing Hub (`docs/index.md`)
Restructure `docs/index.md` to emulate `kubelings/docs/index.md`:
1. **Title & Badge Header**:
   - `Playground` badge (`playground/index.html`)
   - `License` badge (`Apache-2.0`)
   - `Curriculum` badge (`18 Chapters | 81 Exercises` -> `syllabus.md`)
2. **Hero Section ("⚡ The Modern Way to Master Distributed Ray")**:
   - Dual primary callout card grid:
     - Card 1: `Zero-Install Web IDE` with primary CTA button `Launch Playground →` (`playground/index.html`).
     - Card 2: `18-Chapter Reference Manual` with secondary CTA button `Explore Reference Guides →` (`#-comprehensive-18-chapter-reference-guides`).
3. **Comprehensive 18-Chapter Reference Guides Grid**:
   - 4 categorized card columns:
     - **Ray Core & Distributed Memory**: Chapters 01 (Tasks), 02 (Actors), 03 (Object Store), 04 (Resources & Scheduling), 05 (Placement Groups), 06 (Fault Tolerance).
     - **Distributed Data & Scalable ML**: Chapters 07 (Ray Data), 08 (Distributed ML), 09 (Ray Train), 10 (Ray Tune), 11 (Ray Serve).
     - **Observability, Performance & Security**: Chapters 12 (Observability), 13 (High-Performance Internals), 14 (Enterprise Security & mTLS).
     - **Cloud, Kubernetes & LLM Systems**: Chapters 15 (KubeRay), 16 (FSDP / DeepSpeed), 17 (vLLM & Vector RAG), 18 (Quant Finance Pack).
4. **How the Playground Works**:
   - WebAssembly client-side execution diagram (Monaco Editor -> Web Worker Pyodide -> WASM Engine -> Cluster Telemetry Inspector).
5. **Key Advantages**:
   - 100% Client-Side, Zero Servers, Real-Time Interactive Validation.

---

### 3.2. MkDocs Navigation Configuration (`mkdocs.yml`)
Reorganize `mkdocs.yml` navigation hierarchy:
```yaml
nav:
  - Overview: index.md
  - Interactive Playground: playground/index.html
  - Syllabus & Curriculum: syllabus.md
  - Ray Core & Distributed Memory:
      - 01. Remote Tasks & Futures: guides/01-tasks.md
      - 02. Stateful Actors & Concurrency: guides/02-actors.md
      - 03. Plasma Object Store: guides/03-object-store.md
      - 04. Resource Scheduling: guides/04-resources-scheduling.md
      - 05. Placement Groups: guides/05-placement-groups.md
      - 06. Fault Tolerance & Lineage: guides/06-fault-tolerance.md
  - Distributed Data & Scalable ML:
      - 07. Streaming Ray Data: guides/07-ray-data.md
      - 08. Distributed ML from Scratch: guides/08-distributed-ml.md
      - 09. PyTorch Training (Ray Train): guides/09-ray-train.md
      - 10. Hyperparameter Tuning (Ray Tune): guides/10-ray-tune.md
      - 11. Scalable Model Serving (Ray Serve): guides/11-ray-serve.md
  - Observability, Performance & Security:
      - 12. Observability & Tracing: guides/12-observability.md
      - 13. High-Performance Internals: guides/13-performance.md
      - 14. Enterprise Security & TLS: guides/14-security.md
  - Cloud, Kubernetes & LLM Systems:
      - 15. Kubernetes Orchestration (KubeRay): guides/15-kuberay.md
      - 16. Multi-Node LLM Training (FSDP/DeepSpeed): guides/16-fsdp-deepspeed.md
      - 17. High-Throughput vLLM & Vector RAG: guides/17-vllm-rag.md
      - 18. Quantitative Finance Modeling: guides/18-quant-finance.md
  - Contributing: contributing.md

not_in_nav: |
  superpowers/**
  playground/**
  getting-started.md
  onboarding-guide.md
  cli-reference.md
  plugins.md
  cloud-kuberay.md
  troubleshooting.md
  ROADMAP.md
  ONBOARDING.md
```

---

### 3.3. 18 Comprehensive Chapter Reference Guides (`docs/guides/*.md`)
Create all 18 guides adhering to the standardized template:

1. `docs/guides/01-tasks.md` — Chapter 01: Remote Tasks, Object Refs, and Asynchronous Execution
2. `docs/guides/02-actors.md` — Chapter 02: Stateful Actors, Concurrency Groups, and Lifecycle
3. `docs/guides/03-object-store.md` — Chapter 03: Plasma Shared-Memory Object Store & Zero-Copy Deserialization
4. `docs/guides/04-resources-scheduling.md` — Chapter 04: Custom Resources, GPU Scheduling, and Node Affinities
5. `docs/guides/05-placement-groups.md` — Chapter 05: Placement Groups, Bundles, and Gang-Scheduling Strategies
6. `docs/guides/06-fault-tolerance.md` — Chapter 06: Task Retries, Actor Reconstruction, and Lineage Recovery
7. `docs/guides/07-ray-data.md` — Chapter 07: Streaming Ray Data, Block Partitions, and High-Throughput Pipelines
8. `docs/guides/08-distributed-ml.md` — Chapter 08: Distributed Machine Learning from Scratch (Parameter Servers & All-Reduce)
9. `docs/guides/09-ray-train.md` — Chapter 09: Scalable PyTorch Distributed Training with Ray Train
10. `docs/guides/10-ray-tune.md` — Chapter 10: Hyperparameter Optimization, ASHA Schedulers, and Search Algorithms with Ray Tune
11. `docs/guides/11-ray-serve.md` — Chapter 11: Production Model Serving, Multiplexing, and Autoscaling with Ray Serve
12. `docs/guides/12-observability.md` — Chapter 12: Production Observability, OpenTelemetry Tracing, and Dashboard Metrics
13. `docs/guides/13-performance.md` — Chapter 13: Zero-Copy Serialization, Zero-Overhead Memory Spilling, and Performance Tuning
14. `docs/guides/14-security.md` — Chapter 14: Enterprise Security, Node Authentication, and mTLS Cluster Encryption
15. `docs/guides/15-kuberay.md` — Chapter 15: Kubernetes Native Distributed AI with KubeRay Operators
16. `docs/guides/16-fsdp-deepspeed.md` — Chapter 16: Multi-Node LLM Distributed Training with PyTorch FSDP & DeepSpeed
17. `docs/guides/17-vllm-rag.md` — Chapter 17: High-Throughput LLM Inference with vLLM PagedAttention and Distributed Vector RAG
18. `docs/guides/18-quant-finance.md` — Chapter 18: High-Performance Quantitative Finance, Monte Carlo Simulations & Risk Modeling

#### Standard Guide Structure:
- **Metadata Card**: Topic description, total hands-on exercises count, and `Launch Playground in Wasm →` CTA button (`../playground/index.html?chapter=N`).
- **1. Architectural Overview & Control Plane Mechanics**: Deep technical explanation with ASCII diagram of control plane / data plane flows.
- **2. Annotated Python Code Anatomy & API Reference**: Production Python code example with field-by-field and parameter breakdowns.
- **3. Production Best Practices & Hardening Guidelines**: 5 specific production rules.
- **4. Troubleshooting & Diagnostic Workflows**: 3 common failure scenarios and diagnostic steps.
- **5. Hands-on Practice Exercises**: List of exercises with direct links to playground exercise URLs (`../playground/index.html?exercise=<id>`).

---

## 4. Verification & Quality Gates

- `uv run ruff check src tests scripts` (0 errors)
- `uv run pyright src` (0 errors)
- `uv run pytest -q` (all tests passing)
- `uv run mkdocs build --strict` (clean exit 0, all links valid, zero 404s, all 18 guides correctly built and referenced)
- Verify `site/playground/index.html` intact and all 18 guide paths built in `site/guides/`.
