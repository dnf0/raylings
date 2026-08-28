# Kubelings-Standard Documentation, README, and Exercise Pedagogical Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul Raylings' README.md, MkDocs documentation, and all 81 curriculum exercises across 18 chapters to match the gold standard of Kubelings, featuring comprehensive architectural context (`Context & Why:`), detailed `# TODO:` and `# WHY:` inline guidance, Monaco WebAssembly playground badges/links, and full 18-chapter syllabus coverage.

**Architecture:** 
1. Upgrade `README.md` and documentation pages (`docs/index.md`, `docs/syllabus.md`, `docs/getting-started.md`, `docs/onboarding-guide.md`) with badges, architecture ASCII diagrams, pedagogical philosophy, and complete 18-chapter syllabus mapping.
2. Upgrade all 81 exercise files in `exercises/**/*.py` with structured headers (`Exercise:`, `Topic:`, `Context & Why:`, `Instructions:`) and deep `# WHY:` annotations explaining the underlying Ray C++/Python mechanics.
3. Re-bundle `docs/assets/playground_catalog.json` and run full strict verification (pytest, mkdocs strict build, ruff).

**Tech Stack:** Python 3.10-3.12, Ray 2.44+, Typer, Rich, Pyodide/WASM, Monaco Editor, MkDocs Material, Pytest.

---

### Task 1: Overhaul README.md to Kubelings Gold Standard

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write the updated README.md**
Include badges (Docs, CI, KubeRay CI, Playground, Python 3.10+, Ruff, Pyright, Apache-2.0), Pedagogical Philosophy, ASCII architecture diagram, quickstart with `uvx`, detailed CLI commands table, VS Code & Cursor extension guide, complete 18-chapter syllabus table (81 exercises), and the `*lings` ecosystem cross-reference.

- [ ] **Step 2: Verify README syntax and links**
Check that markdown tables and code blocks are well-formed.

- [ ] **Step 3: Commit**
```bash
git add README.md
git commit --no-gpg-sign -m "docs: align README with kubelings gold standard"
```

---

### Task 2: Synchronize MkDocs Documentation Pages

**Files:**
- Modify: `docs/index.md`
- Modify: `docs/syllabus.md`
- Modify: `docs/getting-started.md`
- Modify: `docs/onboarding-guide.md`

- [ ] **Step 1: Update docs/index.md**
Add Playground badge, Try in Browser callout, updated feature bullets, architecture diagram, and VS Code extension details.

- [ ] **Step 2: Update docs/syllabus.md**
Expand syllabus to include all 18 chapters (81 exercises) with full exercise topic names and detailed learning objective summaries.

- [ ] **Step 3: Update docs/getting-started.md and docs/onboarding-guide.md**
Include browser playground link, 18-chapter reference, updated commands, and troubleshooting notes.

- [ ] **Step 4: Verify mkdocs strict build**
Run: `uv run mkdocs build --strict`
Expected: PASS with 0 warnings.

- [ ] **Step 5: Commit**
```bash
git add docs/
git commit --no-gpg-sign -m "docs: update mkdocs site pages with full 18 chapters and playground"
```

---

### Task 3: Pedagogical Expansion of Chapters 01 - 06 (Core, Actors, Plasma, Scheduling, Fault Tolerance, Cluster Architecture)

**Files:**
- Modify: `exercises/01_basics/*.py` (basics01 to basics06)
- Modify: `exercises/02_actors/*.py` (actors01 to actors07)
- Modify: `exercises/03_object_store/*.py` (object_store01 to object_store06)
- Modify: `exercises/04_scheduling_resources/*.py` (scheduling01 to scheduling06)
- Modify: `exercises/05_fault_tolerance/*.py` (fault01 to fault04)
- Modify: `exercises/06_cluster_architecture/*.py` (cluster01 to cluster04)

- [ ] **Step 1: Expand Chapters 01 - 03 exercise headers and TODOs**
Add rich `Context & Why:` and `# WHY:` explanations covering GCS task scheduling, actor method mailboxes, async actors, actor pools, Plasma zero-copy memory, object pinning, and disk spilling.

- [ ] **Step 2: Expand Chapters 04 - 06 exercise headers and TODOs**
Add rich `Context & Why:` and `# WHY:` explanations covering CPU/GPU resource requirements, placement group strategies (`STRICT_SPREAD`, `STRICT_PACK`), lineage reconstruction, max retries, head/worker topologies, and Job Submission API.

- [ ] **Step 3: Run pytest on chapters 01-06 solutions**
Run: `uv run pytest tests/ -k "basics or actors or object_store or scheduling or fault or cluster"`
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add exercises/01_basics exercises/02_actors exercises/03_object_store exercises/04_scheduling_resources exercises/05_fault_tolerance exercises/06_cluster_architecture
git commit --no-gpg-sign -m "docs(exercises): expand context and why pedagogical guidance for chapters 01-06"
```

---

### Task 4: Pedagogical Expansion of Chapters 07 - 12 (Patterns, Ray Data, ML Scratch, Ray Train, Ray Tune, Ray Serve)

**Files:**
- Modify: `exercises/07_patterns_and_antipatterns/*.py` (antipattern01 to antipattern04)
- Modify: `exercises/08_ray_data/*.py` (data01 to data05)
- Modify: `exercises/09_ml_from_scratch/*.py` (ml_scratch01 to ml_scratch04)
- Modify: `exercises/10_ray_train_and_tune/*.py` (train01 to train04)
- Modify: `exercises/11_ray_tune/*.py` (tune01 to tune03)
- Modify: `exercises/12_ray_serve/*.py` (serve01 to serve05)

- [ ] **Step 1: Expand Chapters 07 - 09 exercise headers and TODOs**
Add rich `Context & Why:` and `# WHY:` explanations covering nested `ray.get` anti-patterns, tree aggregations, Ray Data block streaming and backpressure, and distributed parameter server sync/async updates.

- [ ] **Step 2: Expand Chapters 10 - 12 exercise headers and TODOs**
Add rich `Context & Why:` and `# WHY:` explanations covering PyTorch `TorchTrainer` DDP gradient sync, Ray Tune trial schedulers (ASHA/PBT), Ray Serve deployments, dynamic batching, and multi-model DAG routing.

- [ ] **Step 3: Run pytest on chapters 07-12 solutions**
Run: `uv run pytest tests/ -k "data or train or tune or serve or patterns"`
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add exercises/07_patterns_and_antipatterns exercises/08_ray_data exercises/09_ml_from_scratch exercises/10_ray_train_and_tune exercises/11_ray_tune exercises/12_ray_serve
git commit --no-gpg-sign -m "docs(exercises): expand context and why pedagogical guidance for chapters 07-12"
```

---

### Task 5: Pedagogical Expansion of Chapters 13 - 18 (Observability, KubeRay, vLLM/LLMs, FSDP/ZeRO, Multimodal/Vectors, Quant Finance)

**Files:**
- Modify: `exercises/13_observability_and_debugging/*.py` (perf01 to perf03)
- Modify: `exercises/14_kuberay/*.py` (kuberay01 to kuberay05)
- Modify: `exercises/15_vllm_and_llms/*.py` (vllm01 to vllm04)
- Modify: `exercises/16_fsdp_and_deepspeed/*.py` (fsdp01 to fsdp04)
- Modify: `exercises/17_multimodal_and_vectors/*.py` (data_genai01 to data_genai04)
- Modify: `exercises/18_quant_finance/*.py` (finance01 to finance03)

- [ ] **Step 1: Expand Chapters 13 - 15 exercise headers and TODOs**
Add rich `Context & Why:` and `# WHY:` explanations covering Chrome timeline tracing, KubeRay CRDs/operators, tensor parallelism weight sharding, and PagedAttention KV-cache block managers.

- [ ] **Step 2: Expand Chapters 16 - 18 exercise headers and TODOs**
Add rich `Context & Why:` and `# WHY:` explanations covering DeepSpeed ZeRO-1/2/3 parameter sharding, PyTorch FSDP, multimodal streaming ETL, vector DB batch ingestion, and distributed Monte Carlo / VaR quantitative modeling.

- [ ] **Step 3: Run pytest on chapters 13-18 solutions**
Run: `uv run pytest tests/ -k "kuberay or plugins or wasm"`
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add exercises/13_observability_and_debugging exercises/14_kuberay exercises/15_vllm_and_llms exercises/16_fsdp_and_deepspeed exercises/17_multimodal_and_vectors exercises/18_quant_finance
git commit --no-gpg-sign -m "docs(exercises): expand context and why pedagogical guidance for chapters 13-18"
```

---

### Task 6: Rebuild Playground Catalog & Strict Verification

**Files:**
- Modify: `docs/assets/playground_catalog.json`

- [ ] **Step 1: Rebuild playground catalog**
Run: `uv run python -c "from raylings.playground_assets import build_playground_catalog; build_playground_catalog()"`
Expected: Catalog generated with all 81 exercises and updated contexts.

- [ ] **Step 2: Run full test suite**
Run: `uv run pytest`
Expected: 117+ passed.

- [ ] **Step 3: Run reference solution verification**
Run: `uv run raylings test`
Expected: All solutions pass.

- [ ] **Step 4: Run MkDocs strict build**
Run: `uv run mkdocs build --strict`
Expected: PASS (0 warnings).

- [ ] **Step 5: Run linter and formatter**
Run: `uv run ruff check . && uv run ruff format --check .`
Expected: All clean.

- [ ] **Step 6: Commit and push**
```bash
git add docs/assets/playground_catalog.json
git commit --no-gpg-sign -m "docs(playground): update playground catalog with enriched exercise metadata"
```
