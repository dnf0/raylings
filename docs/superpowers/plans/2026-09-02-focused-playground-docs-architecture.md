# Focused Playground & 18-Chapter Architectural Reference Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Raylings documentation site into a Kubelings-standardized interactive learning hub centered on the WebAssembly Interactive Playground and 18 comprehensive architectural reference guides.

**Architecture:** Restructure `docs/index.md` around playground CTA cards and 4 curriculum categories; author 18 detailed chapter reference guides under `docs/guides/` with ASCII control plane mechanics, API code anatomy, production best practices, troubleshooting workflows, and playground exercise deep links; reorganize `mkdocs.yml` into themed navigation sections; validate with strict MkDocs build assertions.

**Tech Stack:** MkDocs Material, Python 3.12, Pyodide v0.26 WebAssembly, Monaco Editor, Pytest.

## Global Constraints
- Every guide under `docs/guides/` must feature the standard topic banner with a `Launch Playground in Wasm →` button targeting `../playground/index.html?chapter=N`.
- Every guide must include ASCII architecture/dataflow diagrams, annotated Python code snippets, 5 production best practices, 3 troubleshooting workflows, and linked exercise lists with `../playground/index.html?exercise=<id>`.
- `mkdocs build --strict` must succeed with zero broken links and zero warnings.

---

### Task 1: Core Workloads & Distributed Memory Guides (Chapters 01-06)

**Files:**
- Create: `docs/guides/01-tasks.md`
- Create: `docs/guides/02-actors.md`
- Create: `docs/guides/03-object-store.md`
- Create: `docs/guides/04-resources-scheduling.md`
- Create: `docs/guides/05-placement-groups.md`
- Create: `docs/guides/06-fault-tolerance.md`
- Test: `tests/test_playground.py`

**Interfaces:**
- Produces: Architectural reference documentation and exercise deep links for Core Ray primitives (Tasks, Actors, Plasma Store, Resources, Placement Groups, Lineage Fault Tolerance).

- [ ] **Step 1: Write Chapter 01-03 guides (`01-tasks.md`, `02-actors.md`, `03-object-store.md`)**
- [ ] **Step 2: Write Chapter 04-06 guides (`04-resources-scheduling.md`, `05-placement-groups.md`, `06-fault-tolerance.md`)**
- [ ] **Step 3: Verify markdown formatting, ASCII diagrams, and exercise URLs**
- [ ] **Step 4: Commit Task 1 changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/guides/01-*.md docs/guides/02-*.md docs/guides/03-*.md docs/guides/04-*.md docs/guides/05-*.md docs/guides/06-*.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "docs(guides): add architectural reference guides for chapters 01-06 (core & memory)"
```

---

### Task 2: Distributed Data & Scalable Machine Learning Guides (Chapters 07-11)

**Files:**
- Create: `docs/guides/07-ray-data.md`
- Create: `docs/guides/08-distributed-ml.md`
- Create: `docs/guides/09-ray-train.md`
- Create: `docs/guides/10-ray-tune.md`
- Create: `docs/guides/11-ray-serve.md`
- Test: `tests/test_playground.py`

**Interfaces:**
- Produces: Architectural reference documentation for streaming Ray Data, parameter server / all-reduce ML architectures, PyTorch distributed training, ASHA hyperparameter search, and Ray Serve model multiplexing.

- [ ] **Step 1: Write Chapter 07-09 guides (`07-ray-data.md`, `08-distributed-ml.md`, `09-ray-train.md`)**
- [ ] **Step 2: Write Chapter 10-11 guides (`10-ray-tune.md`, `11-ray-serve.md`)**
- [ ] **Step 3: Verify markdown formatting and exercise deep links**
- [ ] **Step 4: Commit Task 2 changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/guides/07-*.md docs/guides/08-*.md docs/guides/09-*.md docs/guides/10-*.md docs/guides/11-*.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "docs(guides): add architectural reference guides for chapters 07-11 (data & ml)"
```

---

### Task 3: Observability, Performance & Security Guides (Chapters 12-14)

**Files:**
- Create: `docs/guides/12-observability.md`
- Create: `docs/guides/13-performance.md`
- Create: `docs/guides/14-security.md`
- Test: `tests/test_playground.py`

**Interfaces:**
- Produces: Architectural reference documentation for OpenTelemetry tracing, memory spilling optimization, zero-copy deserialization, and mTLS enterprise cluster authentication.

- [ ] **Step 1: Write Chapter 12-14 guides (`12-observability.md`, `13-performance.md`, `14-security.md`)**
- [ ] **Step 2: Verify code examples and troubleshooting checklists**
- [ ] **Step 3: Commit Task 3 changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/guides/12-*.md docs/guides/13-*.md docs/guides/14-*.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "docs(guides): add architectural reference guides for chapters 12-14 (observability, perf, security)"
```

---

### Task 4: Cloud, KubeRay, LLMs & Quantitative Finance Guides (Chapters 15-18)

**Files:**
- Create: `docs/guides/15-kuberay.md`
- Create: `docs/guides/16-fsdp-deepspeed.md`
- Create: `docs/guides/17-vllm-rag.md`
- Create: `docs/guides/18-quant-finance.md`
- Test: `tests/test_playground.py`

**Interfaces:**
- Produces: Architectural reference documentation for KubeRay operators, PyTorch FSDP / DeepSpeed multi-node training, vLLM PagedAttention inference, and quantitative finance risk models.

- [ ] **Step 1: Write Chapter 15-16 guides (`15-kuberay.md`, `16-fsdp-deepspeed.md`)**
- [ ] **Step 2: Write Chapter 17-18 guides (`17-vllm-rag.md`, `18-quant-finance.md`)**
- [ ] **Step 3: Verify markdown formatting, code snippets, and exercise URLs**
- [ ] **Step 4: Commit Task 4 changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/guides/15-*.md docs/guides/16-*.md docs/guides/17-*.md docs/guides/18-*.md
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "docs(guides): add architectural reference guides for chapters 15-18 (kuberay, llms, quant)"
```

---

### Task 5: Documentation Landing Hub, MkDocs Navigation Restructure & Strict Build Validation

**Files:**
- Modify: `docs/index.md`
- Modify: `mkdocs.yml`
- Modify: `tests/test_playground.py`

**Interfaces:**
- Produces: Restructured landing page spotlighting the playground and chapter guides, organized navigation tree in `mkdocs.yml`, and test suite assertions validating all 18 guides build cleanly without broken links.

- [ ] **Step 1: Restructure `docs/index.md` matching Kubelings hero and 4-column guide grid**
- [ ] **Step 2: Update `mkdocs.yml` navigation with 4 themed guide groups**
- [ ] **Step 3: Update `tests/test_playground.py` with guide path and link validation tests**
- [ ] **Step 4: Run full verification suite (`ruff`, `pyright`, `pytest`, `mkdocs build --strict`)**
- [ ] **Step 5: Commit Task 5 changes**

```bash
PRE_COMMIT_ALLOW_NO_CONFIG=1 git add docs/index.md mkdocs.yml tests/test_playground.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit --no-gpg-sign -m "docs: restructure landing hub and mkdocs navigation to spotlight playground and 18 chapter guides"
```

---

## Plan Self-Review Check
- [x] All 18 chapters covered with dedicated guide files under `docs/guides/`.
- [x] Every guide includes standard metadata banner, ASCII mechanics diagram, annotated code, 5 best practices, 3 diagnostic workflows, and exercise links.
- [x] Strict build verification guarantees zero broken links and clean artifact output.
