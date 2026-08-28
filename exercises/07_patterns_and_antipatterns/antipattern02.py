"""
Exercise: exercises/07_patterns_and_antipatterns/antipattern02.py
Topic: Micro-Task Chunking & Batching

Context & Why:
Ray's task scheduler is extraordinarily fast (sub-millisecond latency), but scheduling 1,000,000
individual tasks that each compute for 1 microsecond results in scheduling and serialization overhead
vastly exceeding the actual computation time.

To achieve maximum throughput, fine-grained tasks should be chunked into coarse batches (e.g.,
processing 1,000 items per task invocation), amortizing scheduling overhead.

Instructions:
1. Group fine-grained items into batches before submitting remote tasks.
2. Verify that batching significantly reduces total execution time.
"""

# I AM NOT DONE

import ray


# TODO: Define batch_square remote task
def batch_square(numbers: list[int]) -> list[int]:
    return [x * x for x in numbers]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = list(range(100))
    chunk_size = 25

    # TODO: Split items into chunks of 25 and dispatch batch_square
    # chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    # refs = [batch_square.remote(chunk) for chunk in chunks]
    # batch_results = ray.get(refs)
    # flattened = [val for sublist in batch_results for val in sublist]
    flattened = []

    expected = [x * x for x in range(100)]
    assert flattened == expected, f"Expected 100 squared items, got {len(flattened)} items"
    print(
        f"✓ antipattern02 verified: Batched processing completed cleanly with 4 tasks ({len(flattened)} elements)!"
    )


if __name__ == "__main__":
    verify()
