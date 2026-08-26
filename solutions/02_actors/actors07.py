"""Chapter 2: Distributed State & Actors - Solution 7: ActorPool Dynamic Load Balancing.

Reference Solution for actors07.
"""

import ray
from ray.util.actor_pool import ActorPool


@ray.remote
class TextTransformer:
    def transform(self, text: str) -> str:
        return text.upper()


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    words = ["ray", "actors", "distributed", "plasma", "scalability"]

    actors = [TextTransformer.remote() for _ in range(3)]
    pool = ActorPool(actors)
    results = list(pool.map(lambda a, v: a.transform.remote(v), words))

    expected = ["RAY", "ACTORS", "DISTRIBUTED", "PLASMA", "SCALABILITY"]
    assert results == expected, f"Expected {expected}, got {results}"
    print(f"✓ actors07 verified: ActorPool dynamically balanced work across workers ({results})!")


if __name__ == "__main__":
    verify()
