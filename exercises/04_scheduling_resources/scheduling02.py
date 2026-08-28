"""
Exercise: exercises/04_scheduling_resources/scheduling02.py
Topic: Node Affinity Scheduling Strategy

Context & Why:
In heterogeneous multi-node clusters, specific nodes may possess specialized hardware (local NVMe scratch,
high-bandwidth networking, or InfiniBand interconnects).

`NodeAffinitySchedulingStrategy` allows pinning tasks or actors to specific cluster nodes by node ID,
or specifying soft affinity preferences.

Instructions:
1. Retrieve the current node ID via `ray.get_runtime_context().get_node_id()`.
2. Schedule an actor specifically on that target node using `NodeAffinitySchedulingStrategy`.
"""

import ray
from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy


# TODO: Define get_running_node_id remote task
def get_running_node_id() -> str:
    return ""


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    expected_node_id = ray.get_runtime_context().get_node_id()

    # TODO: Create NodeAffinitySchedulingStrategy with expected_node_id and soft=False
    # strategy = NodeAffinitySchedulingStrategy(node_id=expected_node_id, soft=False)

    # TODO: Run get_running_node_id task with affinity strategy
    # ref = get_running_node_id.options(scheduling_strategy=strategy).remote()
    # actual_node_id = ray.get(ref)
    actual_node_id = None

    assert actual_node_id == expected_node_id, (
        f"Expected node {expected_node_id}, got {actual_node_id}"
    )
    print(
        f"✓ scheduling02 verified: NodeAffinitySchedulingStrategy pinned execution to node {actual_node_id}!"
    )


if __name__ == "__main__":
    verify()
