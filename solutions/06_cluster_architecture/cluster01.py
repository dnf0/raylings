"""Chapter 6: Cluster Topology & Multi-Node Architecture - Solution 1: Head Node, Workers & GCS.

Reference Solution for cluster01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


def get_alive_node_count() -> int:
    nodes = ray.nodes()
    return sum(1 for n in nodes if n.get("Alive", False))


def get_total_cluster_cpus() -> float:
    nodes = ray.nodes()
    return sum(n.get("Resources", {}).get("CPU", 0.0) for n in nodes if n.get("Alive", False))


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    alive_count = get_alive_node_count()
    total_cpus = get_total_cluster_cpus()

    assert alive_count is not None and alive_count >= 1, (
        f"Expected >=1 alive nodes, got {alive_count}"
    )
    assert total_cpus is not None and total_cpus >= 1.0, (
        f"Expected >=1.0 cluster CPUs, got {total_cpus}"
    )
    print(
        f"✓ cluster01 verified: Cluster topology inspected via GCS (nodes={alive_count}, total_cpus={total_cpus})!"
    )


if __name__ == "__main__":
    verify()
