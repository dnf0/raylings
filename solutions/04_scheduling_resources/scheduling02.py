"""Chapter 4: Scheduling & Resources - Solution 2: Node Affinity Scheduling.

Reference Solution for scheduling02.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy


@ray.remote
def get_running_node_id() -> str:
    return ray.get_runtime_context().get_node_id()


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    expected_node_id = ray.get_runtime_context().get_node_id()
    strategy = NodeAffinitySchedulingStrategy(node_id=expected_node_id, soft=False)

    ref = get_running_node_id.options(scheduling_strategy=strategy).remote()
    actual_node_id = ray.get(ref)

    assert actual_node_id == expected_node_id, (
        f"Expected node {expected_node_id}, got {actual_node_id}"
    )
    print(
        f"✓ scheduling02 verified: NodeAffinitySchedulingStrategy pinned execution to node {actual_node_id}!"
    )


if __name__ == "__main__":
    verify()
