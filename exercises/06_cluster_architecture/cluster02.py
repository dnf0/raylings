# I AM NOT DONE
"""Chapter 6: Cluster Topology & Multi-Node Architecture - Exercise 2: Programmatic Cluster Simulation.

To test multi-node behaviors (distributed scheduling, cross-node data transfer, scale-up)
without launching real cloud VMs, Ray provides `ray.cluster_utils.Cluster`.

`Cluster` allows you to programmatically spawn a mock multi-node Ray cluster on a single machine:
```python
from ray.cluster_utils import Cluster

cluster = Cluster()
head_node = cluster.add_node(num_cpus=2)
ray.init(address=cluster.address)

# Dynamically add worker nodes:
worker_node = cluster.add_node(num_cpus=2)

# Verify cluster expanded to 2 nodes:
assert len([n for n in ray.nodes() if n["Alive"]]) == 2

# Clean up
ray.shutdown()
cluster.shutdown()
```

Your Task:
- Define a `@ray.remote` function `probe_worker(x: int) -> int` that returns `x * 10`.
- In `verify()`:
  - Create a `Cluster()` instance and add a head node with 1 CPU.
  - Connect to the cluster via `ray.init(address=cluster.address)`.
  - Add a second worker node with 1 CPU.
  - Launch 4 `probe_worker` tasks across the multi-node cluster and collect their results.
  - Assert that total active nodes in `ray.nodes()` is 2.
  - Gracefully shutdown Ray and the cluster.
"""

import ray
from ray.cluster_utils import Cluster


# TODO: Define probe_worker remote task
def probe_worker(x: int) -> int:
    return x * 10


def verify() -> None:
    cluster = Cluster()
    try:
        # TODO: Add head node and connect
        # head = cluster.add_node(num_cpus=1)
        # ray.init(address=cluster.address, ignore_reinit_error=True)

        # TODO: Add worker node
        # worker = cluster.add_node(num_cpus=1)

        # TODO: Run probe_worker tasks across cluster
        # refs = [probe_worker.remote(i) for i in [1, 2, 3, 4]]
        # results = ray.get(refs)

        # TODO: Check alive nodes count
        # alive_nodes = sum(1 for n in ray.nodes() if n["Alive"])
        results, alive_nodes = None, None

        assert results == [10, 20, 30, 40], f"Expected [10, 20, 30, 40], got {results}"
        assert alive_nodes == 2, f"Expected 2 alive nodes, got {alive_nodes}"
        print(f"✓ cluster02 verified: Simulated multi-node cluster scaled to {alive_nodes} nodes!")
    finally:
        ray.shutdown()
        cluster.shutdown()


if __name__ == "__main__":
    verify()
