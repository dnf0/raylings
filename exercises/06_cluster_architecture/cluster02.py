"""
Exercise: exercises/06_cluster_architecture/cluster02.py
Topic: Multi-Node Testing with Cluster Utils

Context & Why:
Testing distributed edge cases (network partitions, multi-node scheduling, cross-node serialization)
locally on a single machine can be challenging.

`ray.cluster_utils.Cluster` allows starting simulated multi-node Ray clusters directly inside
Python test processes, adding and removing worker nodes programmatically.

Instructions:
1. Instantiate a simulated 2-node cluster with `ray.cluster_utils.Cluster`.
2. Verify task distribution across the simulated nodes.
"""

# I AM NOT DONE

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
