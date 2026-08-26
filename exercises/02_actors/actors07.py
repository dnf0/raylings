# I AM NOT DONE
"""Chapter 2: Distributed State & Actors - Exercise 7: ActorPool Dynamic Load Balancing.

When you have a pool of stateful actors (e.g., loaded neural network models, database connections)
and a stream of incoming items to process, manually tracking which actor is busy and which is idle
is tedious and error-prone.

`ray.util.ActorPool` solves this by providing dynamic load-balancing across a pool of actors:
1. `pool = ActorPool(actors)`: Wraps a list of actor handles.
2. `pool.map(fn, values)`: Dispatches items across the pool, sending each next item to
   whichever actor becomes idle first.
3. `pool.submit(fn, value)` / `pool.get_next()`: Pulls results in completion order.

Example:
    @ray.remote
    class Worker:
        def process(self, x): return x * 2

    actors = [Worker.remote() for _ in range(3)]
    pool = ActorPool(actors)
    results = list(pool.map(lambda a, v: a.process.remote(v), [1, 2, 3, 4, 5]))
    # results == [2, 4, 6, 8, 10]

Your Task:
- Define `@ray.remote class TextTransformer:` with method `transform(text: str) -> str` that returns `text.upper()`.
- Instantiate 3 `TextTransformer` actors.
- Wrap them in a `ray.util.ActorPool`.
- Use `pool.map()` to transform a list of words: `["ray", "actors", "distributed", "plasma", "scalability"]`.
- Verify transformed results.
"""

import ray
from ray.util.actor_pool import ActorPool  # noqa: F401


# TODO: Define TextTransformer actor
class TextTransformer:
    def transform(self, text: str) -> str:
        return text.upper()


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    words = ["ray", "actors", "distributed", "plasma", "scalability"]
    _ = words

    # TODO: 1. Create 3 TextTransformer actors
    # actors = [TextTransformer.remote() for _ in range(3)]
    # TODO: 2. Create an ActorPool
    # pool = ActorPool(actors)
    # TODO: 3. Process words using pool.map
    # results = list(pool.map(lambda a, v: a.transform.remote(v), words))
    results: list[str] = []

    expected = ["RAY", "ACTORS", "DISTRIBUTED", "PLASMA", "SCALABILITY"]
    assert results == expected, f"Expected {expected}, got {results}"
    print(f"✓ actors07 verified: ActorPool dynamically balanced work across workers ({results})!")


if __name__ == "__main__":
    verify()
