# Track 3: Cloud & Ephemeral Multi-Node CI Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Track 3 Cloud & Ephemeral Multi-Node CI Testing:
1. Multi-Node KinD & KubeRay deployment infrastructure (`scripts/kuberay/`).
2. Comprehensive multi-node end-to-end integration test suite (`tests/test_kuberay_e2e.py`).
3. Dedicated GitHub Actions automated workflow (`.github/workflows/kuberay-e2e.yml`).
4. Documentation in `docs/cloud-kuberay.md` and roadmap reconciliation.

**Architecture:**
- `scripts/kuberay/kind-config.yaml`: 3-node KinD cluster (1 control-plane + 2 worker nodes) with port mapping for Ray head (10001) and dashboard (8265).
- `scripts/kuberay/ray-cluster.yaml`: KubeRay `RayCluster` CRD spec with 1 head pod and 2 worker pods with CPU/RAM resource limits.
- `scripts/kuberay/setup-kuberay.sh`: Provisioning & teardown script that bootstraps KinD, installs KubeRay Helm operator, applies the `RayCluster`, and waits for readiness.
- `tests/test_kuberay_e2e.py`: Test suite tagged with `@pytest.mark.kuberay` testing multi-node node discovery, actor spread across distinct node IPs, strict spread placement groups, cross-node Plasma object transfer, and multi-node TorchTrainer.
- `.github/workflows/kuberay-e2e.yml`: Automated CI pipeline that provisions ephemeral KinD clusters, runs the multi-node test suite, and collects cluster logs on failure.

---

### Task 1: KinD & KubeRay Cluster Manifests and Setup Script

**Files:**
- Create: `scripts/kuberay/kind-config.yaml`
- Create: `scripts/kuberay/ray-cluster.yaml`
- Create: `scripts/kuberay/setup-kuberay.sh`

- [x] **Step 1: Create `scripts/kuberay/kind-config.yaml`**
  - 3-node configuration (1 control-plane, 2 worker nodes).
  - Port mappings for Ray Client (10001), Ray Dashboard (8265), and Ray GCS (6379).

- [x] **Step 2: Create `scripts/kuberay/ray-cluster.yaml`**
  - KubeRay `RayCluster` specification (v1 apiVersion `ray.io/v1`).
  - Head node: 1 replica with Ray client port 10001, dashboard port 8265.
  - Worker group: 2 replicas with memory and CPU resources.

- [x] **Step 3: Create `scripts/kuberay/setup-kuberay.sh`**
  - Executable bash script supporting commands: `up`, `down`, `wait`, `forward`, `status`.
  - Checks for prerequisites (`kind`, `kubectl`, `helm`).
  - Implements robust readiness checks (`kubectl wait`).

- [x] **Step 4: Commit Task 1**
  ```bash
  git add scripts/kuberay/
  git commit -m "feat(kuberay): add KinD and KubeRay cluster manifests and lifecycle script" --no-gpg-sign
  ```

---

### Task 2: Multi-Node Integration Test Suite (`tests/test_kuberay_e2e.py`)

**Files:**
- Create: `tests/test_kuberay_e2e.py`
- Modify: `pyproject.toml` (register `kuberay` pytest marker)

- [ ] **Step 1: Register `kuberay` marker in `pyproject.toml`**
  - Add `kuberay: marks tests that require a live KubeRay or multi-node Ray cluster`.

- [ ] **Step 2: Implement `tests/test_kuberay_e2e.py`**
  - Connection fixture connecting to Ray cluster via `RAY_ADDRESS` or local multi-node mock.
  - `test_kuberay_cluster_node_discovery`: Asserts cluster has >= 2 active nodes.
  - `test_kuberay_actor_cross_node_scheduling`: Schedules actors with distinct CPU requirements, verifying execution across distinct node IPs.
  - `test_kuberay_placement_group_strict_spread`: Creates `STRICT_SPREAD` placement group bundles and verifies actors land on distinct nodes.
  - `test_kuberay_cross_node_plasma_transfer`: Puts 50MB tensor into Plasma object store on Node A and fetches it on Node B, verifying data integrity.
  - `test_kuberay_torch_trainer_multinode`: Runs multi-worker `TorchTrainer` distributed across nodes.

- [ ] **Step 3: Verify tests pass with mock/local multi-node harness**
  - Run `uv run pytest tests/test_kuberay_e2e.py -v`.

- [ ] **Step 4: Commit Task 2**
  ```bash
  git add tests/test_kuberay_e2e.py pyproject.toml
  git commit -m "feat(testing): add multi-node KubeRay integration test suite" --no-gpg-sign
  ```

---

### Task 3: Dedicated GitHub Actions Multi-Node Workflow (`.github/workflows/kuberay-e2e.yml`)

**Files:**
- Create: `.github/workflows/kuberay-e2e.yml`

- [ ] **Step 1: Implement `.github/workflows/kuberay-e2e.yml`**
  - Trigger on push/PR with path filters (`scripts/kuberay/**`, `tests/test_kuberay_e2e.py`, `.github/workflows/kuberay-e2e.yml`) and `workflow_dispatch`.
  - Actions:
    - Setup KinD cluster with `engineerd/setup-kind@v0.5.0` or `helm/kind-action@v1`.
    - Install KubeRay Operator via Helm.
    - Deploy RayCluster and wait for ready state.
    - Setup port-forwarding to Ray Client port 10001.
    - Run `RAY_ADDRESS=ray://localhost:10001 uv run pytest tests/test_kuberay_e2e.py -v`.
    - Dump cluster logs and diagnostics if failed (`kubectl describe rayclusters`, `kubectl logs`).

- [ ] **Step 2: Commit Task 3**
  ```bash
  git add .github/workflows/kuberay-e2e.yml
  git commit -m "ci(kuberay): add automated multi-node KinD and KubeRay GitHub Actions workflow" --no-gpg-sign
  ```

---

### Task 4: Documentation & Final Verification

**Files:**
- Create: `docs/cloud-kuberay.md`
- Modify: `mkdocs.yml`
- Modify: `docs/ROADMAP.md`
- Modify: `README.md`

- [ ] **Step 1: Create `docs/cloud-kuberay.md`**
  - Guide on local KinD testing, KubeRay architecture, Helm installation, and running multi-node exercises.

- [ ] **Step 2: Update `mkdocs.yml`, `README.md`, `docs/ROADMAP.md`**
  - Add `Cloud & KubeRay: cloud-kuberay.md` to `mkdocs.yml`.
  - Mark Track 3 as completed in `docs/ROADMAP.md`.

- [ ] **Step 3: Run full verification suite**
  - Run `uv run pytest -m "not heavy" -v`.
  - Run `uv run ruff check .` and `uv run ruff format --check .`.
  - Run `uvx --with mkdocs-material mkdocs build --strict`.

- [ ] **Step 4: Commit and Merge**
  ```bash
  git add docs/ mkdocs.yml README.md docs/ROADMAP.md
  git commit -m "docs(kuberay): document cloud and multi-node KubeRay deployment and CI testing" --no-gpg-sign
  ```
