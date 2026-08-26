# I AM NOT DONE
"""Chapter 6: Cluster Topology & Multi-Node Architecture - Exercise 3: Simulating Node Failure.

In production clusters, worker nodes may terminate abruptly due to Spot instance preemption,
hardware faults, or Kubernetes node drain events.

When a node terminates:
1. GCS Heartbeat Timeout: The GCS detects missed heartbeats from the node's Raylet.
2. Node Status Update: GCS marks the node `Alive = False` in the cluster registry.
3. Work Rescheduling: Any new or retryable work is routed to the surviving nodes.

You can simulate node failures using `cluster.remove_node(worker_node)`:
```python
cluster.remove_node(worker_node)
# The cluster continues operating with remaining nodes!
```

Your Task:
- Define a `@ray.remote` function `compute_task(x: int) -> int` that returns `x + 100`.
- In `verify()`:
  - Create a 2-node cluster (head node + 1 worker node).
  - Connect with `ray.init(address=cluster.address)`.
  - Terminate the worker node with `cluster.remove_node(worker_node)`.
  - Execute `compute_task.remote(42)` on the remaining head node.
  - Assert the task successfully returns 142.
  - Assert that exactly 1 node remains alive in `ray.nodes()`.
"""

import ray
from ray.cluster_utils import Cluster


# TODO: Define compute_task remote task
def compute_task(x: int) -> int:
    return x + 100


def verify() -> None:
    cluster = Cluster()
    try:
        head = cluster.add_node(num_cpus=1)
        ray.init(address=cluster.address, ignore_reinit_error=True)
        worker = cluster.add_node(num_cpus=1)

        # TODO: Simulate worker node failure
        # cluster.remove_node(worker)

        # TODO: Run task on surviving node
        # result = ray.get(compute_task.remote(42))
        # alive_nodes = sum(1 for n in ray.nodes() if n["Alive"])
        result, alive_nodes = None, None

        assert result == 142, f"Expected result 142, got {result}"
        assert alive_nodes == 1, f"Expected 1 alive node after termination, got {alive_nodes}"
        print(
            f"✓ cluster03 verified: Node failure simulated and workload survived on head node (alive={alive_nodes})!"
        )
    finally:
        ray.shutdown()
        cluster.shutdown()


if __name__ == "__main__":
    verify()
