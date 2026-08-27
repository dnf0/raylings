"""Chapter 6: Cluster Topology & Multi-Node Architecture - Solution 2: Programmatic Cluster Simulation.

Reference Solution for cluster02.
"""

import ray
from ray.cluster_utils import Cluster


@ray.remote
def probe_worker(x: int) -> int:
    return x * 10


def verify() -> None:
    cluster = Cluster()
    try:
        cluster.add_node(num_cpus=1)
        ray.init(address=cluster.address, ignore_reinit_error=True)

        cluster.add_node(num_cpus=1)

        refs = [probe_worker.remote(i) for i in [1, 2, 3, 4]]
        results = ray.get(refs)

        alive_nodes = sum(1 for n in ray.nodes() if n["Alive"])

        assert results == [10, 20, 30, 40], f"Expected [10, 20, 30, 40], got {results}"
        assert alive_nodes == 2, f"Expected 2 alive nodes, got {alive_nodes}"
        print(f"✓ cluster02 verified: Simulated multi-node cluster scaled to {alive_nodes} nodes!")
    finally:
        ray.shutdown()
        cluster.shutdown()


if __name__ == "__main__":
    verify()
