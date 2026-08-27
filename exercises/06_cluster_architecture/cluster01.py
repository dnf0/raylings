"""Chapter 6: Cluster Topology & Multi-Node Architecture - Exercise 1: Head Node, Workers & GCS.

A Ray cluster consists of:
1. Head Node: Runs the Global Control Store (GCS), API server, Dashboard, and Autoscaler.
2. Worker Nodes: Run Raylets (scheduler and object store) and execute worker processes.
3. Global Control Store (GCS): Centralized metadata store (actors, placement groups, node registry).

Ray provides programmatic cluster introspection via `ray.nodes()`:
- Returns a list of dictionaries describing all nodes known to the GCS.
- Each entry contains `NodeID`, `NodeName` (IP), `Alive` (boolean), and `Resources` dictionary.

Example:
    nodes = ray.nodes()
    for n in nodes:
        if n["Alive"]:
            print(f"Active node: {n['NodeID']} with CPUs: {n['Resources'].get('CPU')}")

Your Task:
- Define a helper function `get_alive_node_count() -> int` that queries `ray.nodes()` and counts
  nodes where `n["Alive"] is True`.
- Define a helper function `get_total_cluster_cpus() -> float` that sums up `n["Resources"].get("CPU", 0.0)`
  across all active nodes.
- In `verify()`:
  - Initialize Ray.
  - Assert `get_alive_node_count() >= 1`.
  - Assert `get_total_cluster_cpus() >= 1.0`.
"""

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
