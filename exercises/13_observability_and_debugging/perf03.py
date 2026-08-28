"""
Exercise: exercises/13_observability_and_debugging/perf03.py
Topic: Ray Metrics & Prometheus State APIs

Context & Why:
Ray exports cluster telemetry (CPU, GPU, Plasma memory, task queues, actor counts) via standard
Prometheus endpoints and the `ray.util.state` Python SDK.
Querying state APIs enables building automated health dashboards and autoscaling controllers.

Instructions:
1. Query cluster metrics and actor states using `ray.util.state`.
2. Assert expected task completion metrics.
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
