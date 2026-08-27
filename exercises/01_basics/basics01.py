"""Chapter 1: Ray Core Foundations - Exercise 1: Ray Init & First Remote Task.

Welcome to Raylings!

Ray is an open-source unified framework for scaling AI and Python applications.
At its core, Ray turns standard Python functions into asynchronous, distributed
tasks executed across worker processes.

Key Concepts:
1. `ray.init(ignore_reinit_error=True)`: Connects your Python script to a local
   Ray cluster or starts one automatically if not already running.
2. `@ray.remote`: A decorator that designates a Python function as a distributed
   remote task.
3. `func.remote(*args)`: Invoking a remote function returns an `ObjectRef` (a future),
   submitting the task to the Ray scheduler without blocking.
4. `ray.get(object_ref)`: Blocks until the task completes and retrieves the computed result.

Your Task:
- Initialize Ray using `ray.init(ignore_reinit_error=True)`.
- Decorate the `square` function with `@ray.remote`.
- Call `square.remote(7)` and retrieve the result using `ray.get()`.
"""

import ray


# TODO: Decorate this function with @ray.remote
def square(x: int) -> int:
    return x * x


def verify() -> None:
    # TODO: Initialize Ray
    # ray.init(ignore_reinit_error=True)

    # TODO: Invoke the remote task and get the ObjectRef
    # result_ref = square.remote(7)
    # result = ray.get(result_ref)
    result = None

    assert ray.is_initialized(), "Ray should be initialized"
    assert result == 49, f"Expected 49, but got {result}"
    print("✓ basics01 verified: Ray initialized and remote task executed successfully!")


if __name__ == "__main__":
    verify()
