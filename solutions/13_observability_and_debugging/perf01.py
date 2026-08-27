"""Chapter 13: Observability - Solution 1: Ray Execution Profiling & Chrome Timelines.

Reference Solution for perf01.
"""

import json
import os
import tempfile
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import os

import ray

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"


@ray.remote
def compute_work(task_id: int) -> int:
    return task_id**2


def dump_execution_timeline(filepath: str) -> list[dict[str, Any]]:
    refs = [compute_work.remote(i) for i in range(3)]
    ray.get(refs)

    ray.timeline(filename=filepath)
    with open(filepath, "r") as f:
        events = json.load(f)
    return events


def verify() -> None:
    ray.init(ignore_reinit_error=True)
    try:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            timeline_path = f.name

        events = dump_execution_timeline(timeline_path)
        assert events is not None and len(events) > 0, f"Expected timeline events, got {events}"
        assert any("task" in e.get("name", "") for e in events), "Expected task events in timeline"
        print(f"✓ perf01 verified: Ray timeline exported {len(events)} Chrome tracing events!")
    finally:
        if os.path.exists(timeline_path):
            os.remove(timeline_path)
        ray.shutdown()


if __name__ == "__main__":
    verify()
