"""Chapter 12: Ray Serve - Solution 5: Serve Autoscaling Policies.

Reference Solution for serve05.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 3,
        "target_ongoing_requests": 1,
    }
)
class AutoscaledWorker:
    def __call__(self, request_id: int) -> dict:
        return {"status": "ok", "id": request_id}


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    handle = serve.run(AutoscaledWorker.bind())
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
