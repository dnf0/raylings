"""Chapter 4: Scheduling & Resources - Exercise 2: Node Affinity Scheduling.

In multi-node clusters, you frequently need fine-grained control over where tasks execute:
1. Data Locality: Scheduling a compute task on the exact physical node where disk data resides.
2. Hardware Pairing: Pinning specific tasks to particular specialized nodes.

Ray provides `NodeAffinitySchedulingStrategy` in `ray.util.scheduling_strategies`:
- `node_id`: The hex Node ID string (e.g. `ray.get_runtime_context().get_node_id()`).
- `soft`: If `False` (hard affinity), the task will ONLY execute on that node (or fail/block if unavailable).
  If `True` (soft affinity), Ray prefers that node but falls back to other available nodes.

Example:
    from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy

    strategy = NodeAffinitySchedulingStrategy(node_id=target_node, soft=False)
    ref = my_task.options(scheduling_strategy=strategy).remote()

Your Task:
- Define a `@ray.remote` function `get_running_node_id() -> str` that returns
  `ray.get_runtime_context().get_node_id()`.
- In `verify()`, retrieve the local driver's `node_id` using `ray.get_runtime_context().get_node_id()`.
- Create a `NodeAffinitySchedulingStrategy` targeting that `node_id` with `soft=False`.
- Schedule `get_running_node_id` using `.options(scheduling_strategy=strategy)`.
- Verify the returned node ID matches the expected node ID.
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
