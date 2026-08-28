"""
Exercise: exercises/12_ray_serve/serve05.py
Topic: Streaming LLM Token Responses via Async Generators

Context & Why:
For Large Language Models (LLMs), waiting for the entire sequence to generate creates high Time-To-First-Token (TTFT)
latency for users.
Ray Serve supports streaming HTTP responses using Python `async def` generators and `StreamingResponse`.

Instructions:
1. Implement an async generator deployment yielding token chunks.
2. Stream chunks to client in real time.
"""

# I AM NOT DONE

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve


# TODO: Configure autoscaling_config on AutoscaledWorker
class AutoscaledWorker:
    def __call__(self, request_id: int) -> dict:
        pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Deploy AutoscaledWorker and query handle
    handle = None

    assert handle is not None, "Handle must not be None"
    refs = [handle.remote(i) for i in range(3)]
    results = [r.result() for r in refs]
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    assert all(r["status"] == "ok" for r in results)
    print(
        f"✓ serve05 verified: Autoscaled Serve deployment handled {len(results)} concurrent requests cleanly!"
    )
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
