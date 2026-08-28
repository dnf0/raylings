"""
Exercise: exercises/02_actors/actors07.py
Topic: ActorPool Dynamic Load Balancing

Context & Why:
When you have multiple worker actors (e.g., loaded neural networks, inference engines) and a batch of
tasks to process, manually tracking which actor is busy and which is idle is complex.

`ray.util.ActorPool` manages an elastic pool of actors, automatically routing each new work item
to whichever actor becomes idle first. This maximizes resource utilization and prevents worker starvation.

Instructions:
1. Create a list of 3 `Worker` actor handles.
2. Wrap them in `ray.util.ActorPool(actors)`.
3. Use `pool.map()` to process a list of inputs and collect transformed outputs.
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
    ray.shutdown()


if __name__ == "__main__":
    verify()
