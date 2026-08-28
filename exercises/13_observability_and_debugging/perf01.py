"""
Exercise: exercises/13_observability_and_debugging/perf01.py
Topic: Execution Profiling & Chrome Tracing with ray.timeline()

Context & Why:
Diagnosing stragglers and serialization bottlenecks in distributed systems requires visual execution traces.
`ray.timeline(filename="timeline.json")` exports complete Chrome Tracing / Perfetto JSON files
recording exact start, run, and completion timestamps for all tasks and actors across cluster nodes.

Instructions:
1. Instrument task execution and export trace events with `ray.timeline()`.
2. Verify trace file generation and timeline event structure.
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
    # TODO: Implement compute_work
    pass


def dump_execution_timeline(filepath: str) -> list[dict[str, Any]]:
    # TODO: Execute tasks, call ray.timeline, load and return json events
    pass


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
