"""Chapter 13: Observability - Exercise 3: Ray Metrics & Cluster Introspection.

Ray exposes system metrics (CPU, RAM, GCS state, actor lifecycle) for Prometheus & Grafana.

Key Concepts:
- `ray.util.state.list_actors()`: Lists all alive and dead actor instances with PIDs and resources.
- `ray.nodes()`: Reports active physical/virtual nodes, IP addresses, and remaining resources.

Your Task:
- In `MonitoredWorker`:
  - An actor with `ping() -> str` returning `"pong"`.
- In `inspect_cluster() -> tuple[int, int]`:
  - Launch 2 `MonitoredWorker` actors and call `ping.remote()`.
  - Query `actors = ray.util.state.list_actors()` and count alive actors.
  - Query `nodes = ray.nodes()` and count active nodes with `node["Alive"] is True`.
  - Return `(num_alive_actors, num_active_nodes)`.
- In `verify()`:
  - Assert that at least 2 alive actors and 1 active node are detected.
"""

# I AM NOT DONE
import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.state import list_actors


@ray.remote
class MonitoredWorker:
    def ping(self) -> str:
        # TODO: Return pong
        pass


def inspect_cluster() -> tuple[int, int]:
    # TODO: Instantiate actors, query list_actors and ray.nodes
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)
    try:
        num_actors, num_nodes = inspect_cluster()
        assert num_actors >= 2, f"Expected >= 2 actors, got {num_actors}"
        assert num_nodes >= 1, f"Expected >= 1 active node, got {num_nodes}"
        print(
            f"✓ perf03 verified: Cluster telemetry observed {num_actors} actors on {num_nodes} node(s)!"
        )
    finally:
        ray.shutdown()


if __name__ == "__main__":
    verify()
