"""Chapter 13: Observability - Solution 3: Ray Metrics & Cluster Introspection.

Reference Solution for perf03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray.util.state import list_actors


@ray.remote
class MonitoredWorker:
    def ping(self) -> str:
        return "pong"


def inspect_cluster() -> tuple[int, int]:
    w1 = MonitoredWorker.remote()
    w2 = MonitoredWorker.remote()
    ray.get([w1.ping.remote(), w2.ping.remote()])

    actors = list_actors(filters=[("state", "=", "ALIVE")])
    alive_nodes = [node for node in ray.nodes() if node.get("Alive", True)]

    return len(actors), len(alive_nodes)


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
