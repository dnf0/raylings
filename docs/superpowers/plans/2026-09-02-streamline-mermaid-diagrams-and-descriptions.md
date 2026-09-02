# Streamline Mermaid Diagrams & Attach Concept Descriptions Implementation Plan

> **Goal:** Simplify all Mermaid diagrams across all 18 chapter guides and overview pages to a single, high-level, un-nested architectural flowchart, paired with a structured, attached concept breakdown.

**User Review Required:** No  
**Proposed Execution Mode:** Stateful / Subagent Execution  

---

## File Structure & Impact Map

- **Tests:**
  - `tests/test_guide_diagrams.py` — Updated to assert exactly 1 clean Mermaid flowchart per guide, no nested subgraphs, and presence of `> **Diagram Walkthrough & Core Concepts:**`.
- **Core Ray Guides:**
  - `docs/guides/01-tasks.md`
  - `docs/guides/02-actors.md`
  - `docs/guides/03-object-store.md`
  - `docs/guides/04-resources-scheduling.md`
  - `docs/guides/05-fault-tolerance.md`
  - `docs/guides/06-cluster-architecture.md`
  - `docs/guides/07-patterns-and-antipatterns.md`
- **Distributed ML & Scale Guides:**
  - `docs/guides/08-ray-data.md`
  - `docs/guides/09-distributed-ml.md`
  - `docs/guides/10-ray-train.md`
  - `docs/guides/11-ray-tune.md`
  - `docs/guides/12-ray-serve.md`
- **Advanced Cloud, LLMs & Quant Finance Guides:**
  - `docs/guides/13-observability.md`
  - `docs/guides/14-kuberay.md`
  - `docs/guides/15-vllm-and-llms.md`
  - `docs/guides/16-fsdp-deepspeed.md`
  - `docs/guides/17-multimodal-vectors.md`
  - `docs/guides/18-quant-finance.md`
- **Overview & Syllabus:**
  - `docs/index.md`
  - `docs/syllabus.md`

---

## Tasks

### Task 1: Update Test Suite for Single-Diagram & Attached Concept Verification
- **Files**: `tests/test_guide_diagrams.py`
- **Action**:
  - Update `test_guide_diagrams.py` to:
    1. Count Mermaid blocks in each guide and assert `len(blocks) == 1`.
    2. Assert that `> **Diagram Walkthrough & Core Concepts:**` exists in every guide file.
    3. Assert no nested subgraphs exist in the diagram code.
- **Verification**: Run `uv run pytest tests/test_guide_diagrams.py` and confirm it fails on current multi-diagram guides (Red Phase).

### Task 2: Streamline Core Ray Chapters (Chapters 01–07)
- **Files**: `docs/guides/01-tasks.md` through `docs/guides/07-patterns-and-antipatterns.md`
- **Action**:
  - Replace dual diagrams with single clean flowchart (4–7 nodes max, `LR` or `TD`).
  - Attach `> **Diagram Walkthrough & Core Concepts:**` detailing control/data flow, components, and memory/concurrency guarantees.
- **Verification**: Run `uv run pytest tests/test_guide_diagrams.py -k "01 or 02 or 03 or 04 or 05 or 06 or 07"`.

### Task 3: Streamline Distributed ML & Scale Chapters (Chapters 08–12)
- **Files**: `docs/guides/08-ray-data.md` through `docs/guides/12-ray-serve.md`
- **Action**:
  - Replace dual diagrams with single clean flowchart for Ray Data, Dist ML, Ray Train, Ray Tune, and Ray Serve.
  - Attach `> **Diagram Walkthrough & Core Concepts:**`.
- **Verification**: Run `uv run pytest tests/test_guide_diagrams.py -k "08 or 09 or 10 or 11 or 12"`.

### Task 4: Streamline Advanced Cloud, LLMs & Quant Finance Chapters (Chapters 13–18)
- **Files**: `docs/guides/13-observability.md` through `docs/guides/18-quant-finance.md`
- **Action**:
  - Replace dual diagrams with single clean flowchart for Observability, KubeRay, vLLM, FSDP, Multimodal Vectors, and Quant Finance.
  - Attach `> **Diagram Walkthrough & Core Concepts:**`.
- **Verification**: Run `uv run pytest tests/test_guide_diagrams.py -k "13 or 14 or 15 or 16 or 17 or 18"`.

### Task 5: Streamline Overview & Syllabus Pages (`docs/index.md` & `docs/syllabus.md`)
- **Files**: `docs/index.md`, `docs/syllabus.md`
- **Action**:
  - Update `docs/index.md` playground architecture to a single clean client-worker flowchart with attached concept breakdown.
  - Verify `docs/syllabus.md` learning path diagram and descriptions.
- **Verification**: Run `uv run mkdocs build --strict`.

### Task 6: Comprehensive Verification & Linting
- **Action**:
  - Run `uv run pytest tests/test_guide_diagrams.py -v` (assert 100% pass).
  - Run `uv run mkdocs build --strict` (assert clean exit 0).
  - Run `uv run pytest -m "not heavy"` (assert 100% pass).
  - Run `uv run ruff check docs tests src`.
