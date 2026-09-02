# Chapter 04: Resource Scheduling, Custom Constraints & Placement Groups

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Hardware Resource Demands, Custom Resource Tags, Placement Groups, and Gang Scheduling
-   :material-play-circle: **Interactive Challenges** &bull; 6 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=4){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

Ray's distributed scheduler uses logical resource requirements (`num_cpus`, `num_gpus`, `resources={"custom_accelerator": 1}`) to match tasks and actors to available node capacity across the cluster.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          Placement Group Engine                        │
│                                                                        │
│   Bundles: [{"CPU": 2, "GPU": 1}, {"CPU": 2, "GPU": 1}]               │
│   Strategy: STRICT_SPREAD / STRICT_PACK / PACK / SPREAD                │
│                                                                        │
│   ┌───────────────────────────┐         ┌───────────────────────────┐  │
│   │        Node A (GPU)       │         │        Node B (GPU)       │  │
│   │  [ Bundle 0 Allocated ]   │         │  [ Bundle 1 Allocated ]   │  │
│   │  • Actor Worker 0         │         │  • Actor Worker 1         │  │
│   └───────────────────────────┘         └───────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

**Placement Groups** provide atomic, gang-scheduled resource reservations across nodes, enabling co-location (STRICT_PACK) for low-latency communication or anti-affinity distribution (STRICT_SPREAD) for high availability.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from ray.util.placement_group import placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

# 1. Define atomic resource bundles for distributed training
pg = placement_group(
    bundles=[{"CPU": 2, "GPU": 1}, {"CPU": 2, "GPU": 1}],
    strategy="STRICT_SPREAD"
)

# 2. Block until the gang-scheduling reservation is granted
ray.get(pg.ready())

# 3. Schedule actors onto specific reserved bundles
@ray.remote(num_cpus=2, num_gpus=1)
class DistributedWorker:
    def __init__(self, rank: int):
        self.rank = rank

    def run_training_step(self) -> str:
        return f"Worker {self.rank} completed step on dedicated GPU"

workers = [
    DistributedWorker.options(
        scheduling_strategy=PlacementGroupSchedulingStrategy(
            placement_group=pg,
            placement_group_bundle_index=idx
        )
    ).remote(idx)
    for idx in range(2)
]
```

### Key API Parameter Reference

- **`@ray.remote(num_cpus=N, num_gpus=M, resources={...})`**: Resource demands.
- **`placement_group(bundles, strategy)`**: Allocates atomic multi-node resource reservations. Strategies: `STRICT_SPREAD`, `STRICT_PACK`, `PACK`, `SPREAD`.
- **`PlacementGroupSchedulingStrategy`**: Binds a task or actor to an allocated bundle.
- **`ray.util.remove_placement_group(pg)`**: Releases reserved capacity back to the cluster pool.

---

## 3. Production Best Practices & Hardening Guidelines

1. **Use Fractional GPUs for Inference**: Declare `num_gpus=0.25` for lightweight inference tasks to multiplex up to 4 workers onto a single physical GPU.
2. **Always Check `pg.ready()` with Timeout**: When allocating placement groups in dynamic clusters, wait for `pg.ready()` before scheduling dependent workloads.
3. **Release Unused Placement Groups**: Always call `remove_placement_group()` in `finally:` blocks to prevent resource leaks.
4. **Prefer STRICT_PACK for All-Reduce**: Co-locate distributed workers on NVLink-connected multi-GPU nodes with `STRICT_PACK` for maximum communication bandwidth.
5. **Use Custom Resources for Hardware Affinity**: Tag specialized nodes with custom resources (e.g. `{"h100": 1, "fpga": 1}`).

---

## 4. Troubleshooting & Diagnostic Workflows

1. **Placement Group Pending Indefinitely**:
   - *Symptom*: Cluster hangs on `ray.get(pg.ready())`.
   - *Fix*: Verify total bundle requirements do not exceed total cluster node resources; check for autoscaler node provisioning delays.
2. **Fractional GPU CUDA OOM**:
   - *Symptom*: Out of memory when multiple workers share a single GPU.
   - *Fix*: Set PyTorch memory allocation caps (`torch.cuda.set_per_process_memory_fraction()`).
3. **Infeasible Scheduling Request**:
   - *Symptom*: Task warning "Task requires resources that cannot fit on any node".
   - *Fix*: Verify individual bundle sizes fit within single node maximum resource bounds.

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `scheduling01` | Fractional & Custom Resources | [**Open Exercise scheduling01 →**](../playground/index.html?exercise=scheduling01) |
| `scheduling02` | Node Affinity Scheduling | [**Open Exercise scheduling02 →**](../playground/index.html?exercise=scheduling02) |
| `scheduling03` | Placement Groups: SPREAD Strategy | [**Open Exercise scheduling03 →**](../playground/index.html?exercise=scheduling03) |
| `scheduling04` | Placement Groups: PACK Strategy | [**Open Exercise scheduling04 →**](../playground/index.html?exercise=scheduling04) |
| `scheduling05` | Gang Scheduling Multi-Bundle | [**Open Exercise scheduling05 →**](../playground/index.html?exercise=scheduling05) |
| `scheduling06` | Dynamic Runtime Environments | [**Open Exercise scheduling06 →**](../playground/index.html?exercise=scheduling06) |
