"""
Exercise: exercises/01_basics/basics01.py
Topic: Ray Initialization & First Remote Task

Context & Why:
Ray is an open-source unified framework for scaling AI and Python applications.
At its core, Ray turns standard Python functions into asynchronous, distributed
tasks executed across worker processes managed by local Raylet schedulers and
coordinated by the Global Control Store (GCS).

In standard synchronous Python, function execution blocks the main thread. In distributed
computing, operations should be dispatched asynchronously to maximize core utilization.
Decorating a function with `@ray.remote` transforms it into a task that returns a future
(`ObjectRef`) immediately, enabling non-blocking distributed pipelines.

Instructions:
1. Initialize Ray using `ray.init(ignore_reinit_error=True)`.
2. Decorate the `square` function with `@ray.remote`.
3. Submit the task asynchronously with `square.remote(7)` and retrieve the result via `ray.get()`.
"""

import ray


# TODO: Decorate this function with @ray.remote
# WHY: The @ray.remote decorator registers this function with Ray's core worker engine,
# allowing it to be scheduled asynchronously across worker processes as an independent task.
def square(x: int) -> int:
    return x * x


def verify() -> None:
    # TODO: Initialize Ray
    # WHY: ray.init() bootstraps the Raylet scheduler, Plasma in-memory object store,
    # and connects the driver process to the GCS.
    # ray.init(ignore_reinit_error=True)

    # TODO: Invoke the remote task and get the ObjectRef
    # WHY: Calling .remote() dispatches the task asynchronously and returns an ObjectRef;
    # ray.get() resolves the ObjectRef by reading the value from the shared-memory object store.
    # result_ref = square.remote(7)
    # result = ray.get(result_ref)
    result = None

    assert ray.is_initialized(), "Ray should be initialized"
    assert result == 49, f"Expected 49, but got {result}"
    print("✓ basics01 verified: Ray initialized and remote task executed successfully!")


if __name__ == "__main__":
    verify()
