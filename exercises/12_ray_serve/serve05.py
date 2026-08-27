"""Chapter 12: Ray Serve - Exercise 5: Serve Autoscaling Policies.

Ray Serve features intelligent autoscaling that dynamically provisions actor replicas
based on real-time request queue depth and latency targets.

Key Concepts:
- `autoscaling_config={
    "min_replicas": 1,
    "max_replicas": 4,
    "target_ongoing_requests": 2,
}`:
  Directs Serve to maintain 2 ongoing requests per replica.
- Allows cost optimization: scales down to `min_replicas` during quiet periods, and scales up under load.

Your Task:
- In `AutoscaledWorker`:
  - Decorate with `@serve.deployment(autoscaling_config={"min_replicas": 1, "max_replicas": 3, "target_ongoing_requests": 1})`.
  - Return `{"status": "ok", "id": request_id}`.
- In `verify()`:
  - Deploy and test multiple concurrent requests.
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
