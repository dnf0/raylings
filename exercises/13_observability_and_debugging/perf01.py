"""Chapter 13: Observability - Exercise 1: Ray Execution Profiling & Chrome Timelines.

Ray provides built-in execution timeline profiling via `ray.timeline(filename=...)`.
The exported JSON trace follows the Chrome Tracing / Perfetto format, showing exact
task dispatch, deserialization, execution durations, and cluster scheduling gaps.

Key Concepts:
- `ray.timeline(filename="timeline.json")`: Exports distributed execution profiling events.
- Compatible with Chrome Tracing (`chrome://tracing`) and Perfetto (`ui.perfetto.dev`).

Your Task:
- In `compute_work(task_id: int) -> int`:
  - Remote task performing `task_id ** 2`.
- In `dump_execution_timeline(filepath: str) -> list[dict]`:
  - Launch 3 `compute_work.remote()` tasks and wait for them via `ray.get`.
  - Export trace events using `ray.timeline(filename=filepath)`.
  - Load and return the JSON events list from `filepath`.
- In `verify()`:
  - Assert that timeline events were generated and contain task profiling traces.
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
