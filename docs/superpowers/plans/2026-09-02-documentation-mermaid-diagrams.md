# High-Fidelity Mermaid Architecture Diagrams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade all 18 chapter guides (`docs/guides/01-tasks.md` through `docs/guides/18-quant-finance.md`), landing page (`docs/index.md`), and syllabus (`docs/syllabus.md`) from basic ASCII text boxes into rich, multi-tier Mermaid.js component flowcharts and coordination sequence diagrams.

**Architecture:** Standardize all architecture diagrams into MkDocs Material-compatible `mermaid` code blocks with explicit subgraphs representing process boundaries (Driver, Raylet, Core Worker, Plasma Shared Memory, GCS, Kubernetes Operator) and sequence diagrams for asynchronous communication protocols.

**Tech Stack:** Python 3.12, MkDocs Material (Mermaid.js plugin), Pytest.

## Global Constraints
- Every guide file in `docs/guides/` must contain valid ````mermaid` syntax without legacy ASCII art boxes.
- All diagrams must pass `uv run mkdocs build --strict` with zero warnings.
- All node labels containing special characters must be properly quoted in Mermaid to prevent syntax errors.

---

### Task 1: Create Test Harness for Documentation Mermaid Diagrams

**Files:**
- Create: `tests/test_guide_diagrams.py`

**Interfaces:**
- Consumes: `docs/guides/*.md`, `docs/index.md`, `docs/syllabus.md`
- Produces: Pytest test asserting all 18 guides contain non-empty ```mermaid blocks, proper subgraphs/syntax, and zero legacy ASCII box drawings.

- [ ] **Step 1: Write the failing test**

```python
"""Tests verifying all architectural guides contain rich, valid Mermaid diagrams."""
import re
from pathlib import Path


def test_all_18_guides_contain_rich_mermaid_diagrams():
    guides_dir = Path("docs/guides")
    assert guides_dir.is_dir()
    guide_files = sorted(guides_dir.glob("*.md"))
    assert len(guide_files) == 18

    for guide in guide_files:
        content = guide.read_text(encoding="utf-8")
        assert "```mermaid" in content, f"Guide {guide.name} must contain at least one mermaid diagram"
        assert "┌──" not in content, f"Guide {guide.name} still contains legacy ASCII box drawings"

        # Check for mermaid block completeness
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        assert len(mermaid_blocks) >= 1, f"Guide {guide.name} has empty mermaid block"
        for block in mermaid_blocks:
            assert ("flowchart" in block or "graph" in block or "sequenceDiagram" in block), (
                f"Guide {guide.name} mermaid block missing valid diagram header"
            )


def test_overview_and_syllabus_contain_mermaid_diagrams():
    index_md = Path("docs/index.md")
    assert index_md.exists()
    assert "```mermaid" in index_md.read_text(encoding="utf-8")

    syllabus_md = Path("docs/syllabus.md")
    assert syllabus_md.exists()
    assert "```mermaid" in syllabus_md.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_guide_diagrams.py -v`
Expected: FAIL (guides still contain legacy ASCII box drawings `┌──`)

- [ ] **Step 3: Commit initial test harness**

```bash
git add tests/test_guide_diagrams.py
git commit -m "test(docs): add verification test for documentation mermaid diagrams"
```

---

### Task 2: Implement Rich Mermaid Diagrams for Part I: Ray Core & Distributed Fundamentals (Guides 01–07)

**Files:**
- Modify: `docs/guides/01-tasks.md`
- Modify: `docs/guides/02-actors.md`
- Modify: `docs/guides/03-object-store.md`
- Modify: `docs/guides/04-resources-scheduling.md`
- Modify: `docs/guides/05-fault-tolerance.md`
- Modify: `docs/guides/06-cluster-architecture.md`
- Modify: `docs/guides/07-patterns-and-antipatterns.md`

**Interfaces:**
- Consumes: Task 1 test harness
- Produces: Updated markdown documentation with rich Mermaid flowcharts and sequence diagrams.

- [ ] **Step 1: Update `docs/guides/01-tasks.md` with Task Scheduling Architecture & Sequence Diagram**
- [ ] **Step 2: Update `docs/guides/02-actors.md` with Stateful Actor Lifecycle & Direct Call Sequence Diagram**
- [ ] **Step 3: Update `docs/guides/03-object-store.md` with Plasma Zero-Copy Shared Memory & IPC Resolution Diagram**
- [ ] **Step 4: Update `docs/guides/04-resources-scheduling.md` with Two-Tier Raylet Scheduling & Placement Groups Diagram**
- [ ] **Step 5: Update `docs/guides/05-fault-tolerance.md` with Object Lineage DAG & Actor Reconstruction Sequence Diagram**
- [ ] **Step 6: Update `docs/guides/06-cluster-architecture.md` with Head Node (GCS/Dashboard) & Worker Nodes Process Topology**
- [ ] **Step 7: Update `docs/guides/07-patterns-and-antipatterns.md` with Anti-Pattern Blocking vs Direct ObjectRef DAG Pipeline Diagram**
- [ ] **Step 8: Verify Part I syntax via MkDocs build**

Run: `uv run mkdocs build --strict`
Expected: PASS

- [ ] **Step 9: Commit Part I changes**

```bash
git add docs/guides/01-tasks.md docs/guides/02-actors.md docs/guides/03-object-store.md docs/guides/04-resources-scheduling.md docs/guides/05-fault-tolerance.md docs/guides/06-cluster-architecture.md docs/guides/07-patterns-and-antipatterns.md
git commit -m "docs(guides): upgrade Ray Core chapters 01-07 to rich Mermaid architecture diagrams"
```

---

### Task 3: Implement Rich Mermaid Diagrams for Part II: Distributed Data & ML Frameworks (Guides 08–12)

**Files:**
- Modify: `docs/guides/08-ray-data.md`
- Modify: `docs/guides/09-distributed-ml.md`
- Modify: `docs/guides/10-ray-train.md`
- Modify: `docs/guides/11-ray-tune.md`
- Modify: `docs/guides/12-ray-serve.md`

**Interfaces:**
- Consumes: Tasks 1-2
- Produces: Multi-tier diagrams for Ray Data streaming DAGs, Distributed ML parameter servers, PyTorch DDP/NCCL rings, Ray Tune ASHA, and Ray Serve routing.

- [ ] **Step 1: Update `docs/guides/08-ray-data.md` with Streaming Execution Block Pipeline & Operator Graph**
- [ ] **Step 2: Update `docs/guides/09-distributed-ml.md` with Parameter Server vs AllReduce Ring Topology**
- [ ] **Step 3: Update `docs/guides/10-ray-train.md` with TorchTrainer Coordinator, Worker Group Actors & NCCL Sync Ring**
- [ ] **Step 4: Update `docs/guides/11-ray-tune.md` with Tuner, TrialRunner, Trial Executors & ASHA Early Stopping Scheduler**
- [ ] **Step 5: Update `docs/guides/12-ray-serve.md` with Serve Controller, Ingress Proxy, Routers, Replica Actors & Autoscaling**
- [ ] **Step 6: Verify Part II syntax via MkDocs build**

Run: `uv run mkdocs build --strict`
Expected: PASS

- [ ] **Step 7: Commit Part II changes**

```bash
git add docs/guides/08-ray-data.md docs/guides/09-distributed-ml.md docs/guides/10-ray-train.md docs/guides/11-ray-tune.md docs/guides/12-ray-serve.md
git commit -m "docs(guides): upgrade Distributed Data and ML chapters 08-12 to rich Mermaid diagrams"
```

---

### Task 4: Implement Rich Mermaid Diagrams for Part III: Observability, Cloud & Advanced AI (Guides 13–18)

**Files:**
- Modify: `docs/guides/13-observability.md`
- Modify: `docs/guides/14-kuberay.md`
- Modify: `docs/guides/15-vllm-and-llms.md`
- Modify: `docs/guides/16-fsdp-deepspeed.md`
- Modify: `docs/guides/17-multimodal-vectors.md`
- Modify: `docs/guides/18-quant-finance.md`

**Interfaces:**
- Consumes: Tasks 1-3
- Produces: Upgraded diagrams for OpenTelemetry, KubeRay reconciliation loops, vLLM PagedAttention, ZeRO-3 sharding, multimodal RAG, and Monte Carlo risk engines.

- [ ] **Step 1: Update `docs/guides/13-observability.md` with OpenTelemetry Tracing Spans, Prometheus & Dashboard**
- [ ] **Step 2: Update `docs/guides/14-kuberay.md` with KubeRay Operator Controller loop & RayCluster CRD Lifecycle**
- [ ] **Step 3: Update `docs/guides/15-vllm-and-llms.md` with Tensor-Parallel vLLM Worker Engine & PagedAttention KV Cache Blocks**
- [ ] **Step 4: Update `docs/guides/16-fsdp-deepspeed.md` with ZeRO-3 Sharded Weights, Gradients, and Inter-Node AllGather/ReduceScatter**
- [ ] **Step 5: Update `docs/guides/17-multimodal-vectors.md` with Streaming Vision/Text Embeddings & Distributed HNSW Vector Index Actor**
- [ ] **Step 6: Update `docs/guides/18-quant-finance.md` with Monte Carlo Scenario Dispatcher, Pricing Workers & VaR Aggregator**
- [ ] **Step 7: Verify Part III syntax via MkDocs build**

Run: `uv run mkdocs build --strict`
Expected: PASS

- [ ] **Step 8: Commit Part III changes**

```bash
git add docs/guides/13-observability.md docs/guides/14-kuberay.md docs/guides/15-vllm-and-llms.md docs/guides/16-fsdp-deepspeed.md docs/guides/17-multimodal-vectors.md docs/guides/18-quant-finance.md
git commit -m "docs(guides): upgrade Cloud, GenAI and Quant chapters 13-18 to rich Mermaid diagrams"
```

---

### Task 5: Upgrade Overview Hub & Syllabus Diagrams

**Files:**
- Modify: `docs/index.md`
- Modify: `docs/syllabus.md`

**Interfaces:**
- Consumes: Tasks 1-4
- Produces: 360° Ray architectural stack map and 4 guided curriculum tracks.

- [ ] **Step 1: Update `docs/index.md` with 360° Ray Unified Platform Ecosystem Topology**
- [ ] **Step 2: Update `docs/syllabus.md` with 4 Guided Curriculum Learning Path Flowcharts**
- [ ] **Step 3: Run full pytest suite including test_guide_diagrams.py**

Run: `uv run pytest tests/test_guide_diagrams.py tests/test_playground.py -v`
Expected: 11 passed (100%)

- [ ] **Step 4: Commit Overview and Syllabus changes**

```bash
git add docs/index.md docs/syllabus.md
git commit -m "docs: add 360-degree ecosystem and curriculum pathway Mermaid diagrams to overview and syllabus"
```

---

### Task 6: Strict MkDocs Build, Linting & Verification

**Files:**
- None (Verification task across all built assets)

- [ ] **Step 1: Run code and style formatting checks**
Run: `uv run ruff check src tests`
- [ ] **Step 2: Run type checking**
Run: `uv run pyright src`
- [ ] **Step 3: Run full pytest test suite**
Run: `uv run pytest -q`
- [ ] **Step 4: Execute strict MkDocs documentation build**
Run: `uv run mkdocs build --strict`
Expected: Zero build warnings, clean documentation generation in `site/`
