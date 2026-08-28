"""
Exercise: exercises/06_cluster_architecture/cluster01.py
Topic: Head Node vs Worker Node Architecture & GCS

Context & Why:
A Ray cluster consists of one **Head Node** and zero or more **Worker Nodes**.
The Head node hosts the Global Control Store (GCS), which manages metadata, actor registration,
and cluster-wide heartbeat monitoring. Every node runs a **Raylet** (local scheduler and Plasma store).

Instructions:
1. Query cluster state using `ray.nodes()`.
2. Inspect node IP addresses, alive status, and available compute resources.
"""

# I AM NOT DONE

import ray


# TODO: Implement get_alive_node_count
def get_alive_node_count() -> int:
    return 0


# TODO: Implement get_total_cluster_cpus
def get_total_cluster_cpus() -> float:
    return 0.0


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Query cluster metadata
    # alive_count = get_alive_node_count()
    # total_cpus = get_total_cluster_cpus()
    alive_count, total_cpus = None, None

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
