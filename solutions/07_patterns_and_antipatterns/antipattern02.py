"""Chapter 7: Production Patterns & Anti-Patterns - Solution 2: Fixing Fine-Grained Task Overhead.

Reference Solution for antipattern02.
"""

import ray


@ray.remote
def batch_square(numbers: list[int]) -> list[int]:
    return [x * x for x in numbers]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = list(range(100))
    chunk_size = 25

    chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
    refs = [batch_square.remote(c) for c in chunks]
    batch_results = ray.get(refs)
    flattened = [val for sublist in batch_results for val in sublist]

    expected = [x * x for x in range(100)]
    assert flattened == expected, f"Expected 100 squared items, got {len(flattened)} items"
    print(
        f"✓ antipattern02 verified: Batched processing completed cleanly with 4 tasks ({len(flattened)} elements)!"
    )


if __name__ == "__main__":
    verify()
