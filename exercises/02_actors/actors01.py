# I AM NOT DONE
"""Chapter 2: Distributed State & Actors - Exercise 1: Stateful Actor Lifecycle.

While Ray tasks are stateless functions, Ray Actors are stateful Python classes.
Decorating a Python class with `@ray.remote` turns it into an Actor.

Key Concepts:
1. Actor Instantiation: Calling `MyActor.remote(*args)` creates a dedicated worker
   process on the cluster and runs `__init__`. It returns an `ActorHandle`.
2. Method Invocations: Calling `actor.my_method.remote(*args)` sends a message to
   the actor process and returns an `ObjectRef` representing the method's return value.
3. State Preservation: An actor maintains its internal instance state (`self.xxx`)
   across multiple method calls for its entire lifetime.

Example:
    @ray.remote
    class Counter:
        def __init__(self):
            self.value = 0
        def inc(self):
            self.value += 1
            return self.value

    c = Counter.remote()
    ref1 = c.inc.remote()
    print(ray.get(ref1))  # 1
    ref2 = c.inc.remote()
    print(ray.get(ref2))  # 2

Your Task:
- Decorate `Counter` with `@ray.remote`.
- Implement `increment(step)`, `decrement(step)`, and `get_count()`.
- Instantiate `counter = Counter.remote(initial_value=10)`.
- Increment by 5, decrement by 3, and verify the final count is 12.
"""

import ray


# TODO: Decorate this class with @ray.remote
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
    print(f"✓ actors01 verified: Stateful Actor lifecycle and operations confirmed (count={final_count})!")


if __name__ == "__main__":
    verify()
