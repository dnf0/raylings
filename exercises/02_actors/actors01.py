"""
Exercise: exercises/02_actors/actors01.py
Topic: Stateful Actor Lifecycle & Remote Classes

Context & Why:
While Ray tasks are stateless functions, Ray Actors are stateful Python classes.
Decorating a Python class with `@ray.remote` transforms it into a dedicated, long-running
worker process that preserves internal instance state (`self.xxx`) across method calls.

When you call `MyActor.remote(*args)`, Ray provisions a worker process, executes `__init__`,
and returns an `ActorHandle`. Subsequent method invocations `actor.method.remote()` send
messages to the actor's FIFO mailbox and return `ObjectRef` futures.

Instructions:
1. Decorate `Counter` with `@ray.remote`.
2. Instantiate `Counter.remote(initial_val=10)` to receive an `ActorHandle`.
3. Invoke `increment.remote(5)` and `get_count.remote()`, then verify with `ray.get()`.
"""

import ray


# TODO: Decorate this class with @ray.remote
# WHY: Decorating a class with @ray.remote instructs Ray to manage instances as dedicated stateful worker processes.
class Counter:
    def __init__(self, initial_value: int = 0) -> None:
        self.count = initial_value

    def increment(self, step: int = 1) -> int:
        # TODO: update self.count and return it
        pass

    def decrement(self, step: int = 1) -> int:
        # TODO: update self.count and return it
        pass

    def get_count(self) -> int:
        # TODO: return self.count
        pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate Counter.remote(initial_value=10)
    # counter = Counter.remote(initial_value=10)
    # counter.increment.remote(5)
    # counter.decrement.remote(3)
    # final_count = ray.get(counter.get_count.remote())
    final_count = None

    assert final_count == 12, f"Expected final count 12, got {final_count}"
    print(
        f"✓ actors01 verified: Stateful Actor lifecycle and operations confirmed (count={final_count})!"
    )


if __name__ == "__main__":
    verify()
