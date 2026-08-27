# Track 1: Next-Gen Distributed AI Curriculum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Raylings curriculum from 14 chapters (66 exercises) to 17 chapters (78 exercises), implementing Chapters 15 (Distributed LLM Serving & vLLM), 16 (DeepSpeed & PyTorch FSDP), and 17 (Multimodal & Vector Ray Data Pipelines) with full starter exercises, canonical solutions, manifest registry, documentation, and automated testing harness.

**Architecture:** 
Add 12 new hands-on distributed Python exercises and solutions across 3 new chapter directories (`exercises/15_vllm_and_llms/`, `exercises/16_fsdp_and_deepspeed/`, `exercises/17_multimodal_and_vectors/` and matching `solutions/`). Register the new chapters and exercises in `src/raylings/manifest.py`, update documentation in `docs/syllabus.md`, and verify full test suite pass.

**Tech Stack:** Python 3.10+, Ray 2.30+, PyTorch, NumPy, PyArrow, Typer, Rich, Pytest, Ruff.

---

### File Structure Map

```
raylings/
├── docs/
│   ├── ROADMAP.md
│   └── syllabus.md
├── src/
│   └── raylings/
│       └── manifest.py
├── exercises/
│   ├── 15_vllm_and_llms/
│   │   ├── vllm01.py
│   │   ├── vllm02.py
│   │   ├── vllm03.py
│   │   └── vllm04.py
│   ├── 16_fsdp_and_deepspeed/
│   │   ├── fsdp01.py
│   │   ├── fsdp02.py
│   │   ├── fsdp03.py
│   │   └── fsdp04.py
│   └── 17_multimodal_and_vectors/
│       ├── data_genai01.py
│       ├── data_genai02.py
│       ├── data_genai03.py
│       └── data_genai04.py
├── solutions/
│   ├── 15_vllm_and_llms/
│   │   ├── vllm01.py
│   │   ├── vllm02.py
│   │   ├── vllm03.py
│   │   └── vllm04.py
│   ├── 16_fsdp_and_deepspeed/
│   │   ├── fsdp01.py
│   │   ├── fsdp02.py
│   │   ├── fsdp03.py
│   │   └── fsdp04.py
│   └── 17_multimodal_and_vectors/
│       ├── data_genai01.py
│       ├── data_genai02.py
│       ├── data_genai03.py
│       └── data_genai04.py
└── tests/
    ├── test_infra.py
    └── test_manifest.py
```

---

### Task 1: Chapter 15 — Distributed LLM Serving & vLLM Architecture

**Files:**
- Create: `exercises/15_vllm_and_llms/vllm01.py`
- Create: `solutions/15_vllm_and_llms/vllm01.py`
- Create: `exercises/15_vllm_and_llms/vllm02.py`
- Create: `solutions/15_vllm_and_llms/vllm02.py`
- Create: `exercises/15_vllm_and_llms/vllm03.py`
- Create: `solutions/15_vllm_and_llms/vllm03.py`
- Create: `exercises/15_vllm_and_llms/vllm04.py`
- Create: `solutions/15_vllm_and_llms/vllm04.py`

- [ ] **Step 1: Implement `vllm01.py` (Tensor Parallelism & Worker Actor Groups)**
  - Exercise teaches multi-actor tensor parallelism (sharding attention projection weights across Ray actors and all-reducing intermediate activations).
  - Create skeleton in `exercises/15_vllm_and_llms/vllm01.py` with missing tensor slicing math.
  - Create solution in `solutions/15_vllm_and_llms/vllm01.py` with complete implementation.

- [ ] **Step 2: Implement `vllm02.py` (PagedAttention & KV-Cache Block Management)**
  - Exercise teaches non-contiguous memory management for token KV-caches (logical to physical block table allocation).
  - Create skeleton in `exercises/15_vllm_and_llms/vllm02.py` and solution in `solutions/15_vllm_and_llms/vllm02.py`.

- [ ] **Step 3: Implement `vllm03.py` (Dynamic Multi-LoRA Adapter Serving)**
  - Exercise teaches dynamic adapter weight injection across worker actor pools without reloading base weights.
  - Create skeleton in `exercises/15_vllm_and_llms/vllm03.py` and solution in `solutions/15_vllm_and_llms/vllm03.py`.

- [ ] **Step 4: Implement `vllm04.py` (Speculative Decoding with Draft Model Workers)**
  - Exercise teaches parallel draft token generation and speculative verification between draft actor and target model actor.
  - Create skeleton in `exercises/15_vllm_and_llms/vllm04.py` and solution in `solutions/15_vllm_and_llms/vllm04.py`.

- [ ] **Step 5: Verify Chapter 15 syntax & runner**
  - Run solutions through `raylings test solutions/15_vllm_and_llms/vllm*.py`.

- [ ] **Step 6: Commit Chapter 15**
  ```bash
  git add exercises/15_vllm_and_llms/ solutions/15_vllm_and_llms/
  git commit -m "feat(curriculum): add chapter 15 distributed LLM serving and vLLM exercises" --no-gpg-sign
  ```

---

### Task 2: Chapter 16 — DeepSpeed & PyTorch FSDP

**Files:**
- Create: `exercises/16_fsdp_and_deepspeed/fsdp01.py`
- Create: `solutions/16_fsdp_and_deepspeed/fsdp01.py`
- Create: `exercises/16_fsdp_and_deepspeed/fsdp02.py`
- Create: `solutions/16_fsdp_and_deepspeed/fsdp02.py`
- Create: `exercises/16_fsdp_and_deepspeed/fsdp03.py`
- Create: `solutions/16_fsdp_and_deepspeed/fsdp03.py`
- Create: `exercises/16_fsdp_and_deepspeed/fsdp04.py`
- Create: `solutions/16_fsdp_and_deepspeed/fsdp04.py`

- [ ] **Step 1: Implement `fsdp01.py` (PyTorch FSDP with Ray Train `ScalingConfig`)**
  - Exercise teaches distributed model parameter sharding (`FULL_SHARD`) and `TorchTrainer` multi-worker execution.
  - Create skeleton in `exercises/16_fsdp_and_deepspeed/fsdp01.py` and solution in `solutions/16_fsdp_and_deepspeed/fsdp01.py`.

- [ ] **Step 2: Implement `fsdp02.py` (DeepSpeed ZeRO-1/2/3 Memory Partitioning)**
  - Exercise teaches ZeRO stage configurations (optimizer state, gradients, model weights) on Ray worker groups.
  - Create skeleton in `exercises/16_fsdp_and_deepspeed/fsdp02.py` and solution in `solutions/16_fsdp_and_deepspeed/fsdp02.py`.

- [ ] **Step 3: Implement `fsdp03.py` (Mixed Precision & Activation Checkpointing)**
  - Exercise teaches peak VRAM reduction via gradient scaling and activation recomputation hooks.
  - Create skeleton in `exercises/16_fsdp_and_deepspeed/fsdp03.py` and solution in `solutions/16_fsdp_and_deepspeed/fsdp03.py`.

- [ ] **Step 4: Implement `fsdp04.py` (Elastic Fault-Tolerant Distributed Checkpoints)**
  - Exercise teaches distributed state dict checkpointing and resumption on worker preemption.
  - Create skeleton in `exercises/16_fsdp_and_deepspeed/fsdp04.py` and solution in `solutions/16_fsdp_and_deepspeed/fsdp04.py`.

- [ ] **Step 5: Verify Chapter 16 syntax & runner**
  - Run solutions through `raylings test solutions/16_fsdp_and_deepspeed/fsdp*.py`.

- [ ] **Step 6: Commit Chapter 16**
  ```bash
  git add exercises/16_fsdp_and_deepspeed/ solutions/16_fsdp_and_deepspeed/
  git commit -m "feat(curriculum): add chapter 16 deepspeed and FSDP distributed training exercises" --no-gpg-sign
  ```

---

### Task 3: Chapter 17 — Multimodal & Vector Ray Data Pipelines

**Files:**
- Create: `exercises/17_multimodal_and_vectors/data_genai01.py`
- Create: `solutions/17_multimodal_and_vectors/data_genai01.py`
- Create: `exercises/17_multimodal_and_vectors/data_genai02.py`
- Create: `solutions/17_multimodal_and_vectors/data_genai02.py`
- Create: `exercises/17_multimodal_and_vectors/data_genai03.py`
- Create: `solutions/17_multimodal_and_vectors/data_genai03.py`
- Create: `exercises/17_multimodal_and_vectors/data_genai04.py`
- Create: `solutions/17_multimodal_and_vectors/data_genai04.py`

- [ ] **Step 1: Implement `data_genai01.py` (Streaming Multimodal Image & Audio ETL)**
  - Exercise teaches high-throughput streaming dataset transforms with PyArrow tensor blocks and memory backpressure.
  - Create skeleton in `exercises/17_multimodal_and_vectors/data_genai01.py` and solution in `solutions/17_multimodal_and_vectors/data_genai01.py`.

- [ ] **Step 2: Implement `data_genai02.py` (GPU-Accelerated Batch Embeddings with `ActorPoolStrategy`)**
  - Exercise teaches batch embedding extraction using stateful actor pools and vectorized batch mapping.
  - Create skeleton in `exercises/17_multimodal_and_vectors/data_genai02.py` and solution in `solutions/17_multimodal_and_vectors/data_genai02.py`.

- [ ] **Step 3: Implement `data_genai03.py` (Dynamic Token Length Bucketing & Padding Optimization)**
  - Exercise teaches bucketing variable-length sequences to eliminate wasteful padding tokens.
  - Create skeleton in `exercises/17_multimodal_and_vectors/data_genai03.py` and solution in `solutions/17_multimodal_and_vectors/data_genai03.py`.

- [ ] **Step 4: Implement `data_genai04.py` (Streaming Parallel Ingestion into Vector Databases)**
  - Exercise teaches custom Ray Data batch write sinks with connection pooling into vector indexes.
  - Create skeleton in `exercises/17_multimodal_and_vectors/data_genai04.py` and solution in `solutions/17_multimodal_and_vectors/data_genai04.py`.

- [ ] **Step 5: Verify Chapter 17 syntax & runner**
  - Run solutions through `raylings test solutions/17_multimodal_and_vectors/data_genai*.py`.

- [ ] **Step 6: Commit Chapter 17**
  ```bash
  git add exercises/17_multimodal_and_vectors/ solutions/17_multimodal_and_vectors/
  git commit -m "feat(curriculum): add chapter 17 multimodal and vector ray data exercises" --no-gpg-sign
  ```

---

### Task 4: Manifest Registration, Syllabus Documentation, and Full Suite Verification

**Files:**
- Modify: `src/raylings/manifest.py` (register Chapters 15, 16, 17 and all 12 exercises)
- Modify: `docs/syllabus.md` (add Chapters 15, 16, 17 curriculum details)
- Modify: `tests/test_infra.py` (verify all 78 exercises and solutions statically)
- Modify: `tests/test_manifest.py` (verify 17 chapters and 78 exercises)

- [x] **Step 1: Update `src/raylings/manifest.py`**
  - Register Chapters 15 (`15_vllm_and_llms`), 16 (`16_fsdp_and_deepspeed`), 17 (`17_multimodal_and_vectors`) with titles, descriptions, and progressive hints.

- [x] **Step 2: Update `docs/syllabus.md`**
  - Add comprehensive curriculum syllabus sections for Chapters 15, 16, and 17.

- [x] **Step 3: Update and execute test suite**
  - Update `assert len(manifest.all_exercises) == 78` and `assert len(manifest.chapters) == 17`.
  - Run `uv run pytest -m "not heavy" -v`.
  - Run `uv run ruff check src tests` and `uv run ruff format --check src tests`.
  - Run `uvx --with mkdocs-material mkdocs build --strict`.

- [x] **Step 4: Commit and Push**
  ```bash
  git add src/raylings/manifest.py docs/syllabus.md tests/test_infra.py tests/test_manifest.py
  git commit -m "feat(manifest): register chapters 15-17 expanding curriculum to 78 exercises" --no-gpg-sign
  ```
