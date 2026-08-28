"""Chapter 6: Cluster Topology & Multi-Node Architecture - Solution 3: Simulating Node Failure.

Reference Solution for cluster03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.cluster_utils import Cluster


@ray.remote
def compute_task(x: int) -> int:
    return x + 100


def verify() -> None:
    cluster = Cluster()
    try:
        cluster.add_node(num_cpus=1)
        ray.init(address=cluster.address, ignore_reinit_error=True)
        worker = cluster.add_node(num_cpus=1)

        cluster.remove_node(worker)

        result = ray.get(compute_task.remote(42))
        alive_nodes = sum(1 for n in ray.nodes() if n["Alive"])

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
