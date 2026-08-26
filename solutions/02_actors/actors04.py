"""Chapter 2: Distributed State & Actors - Solution 4: Async Actors & Concurrency.

Reference Solution for actors04.
"""

import asyncio
import time
import ray


@ray.remote(max_concurrency=5)
class AsyncRateLimiter:
    def __init__(self) -> None:
        self.served_count = 0

    async def process_request(self, req_id: int, delay: float) -> str:
        await asyncio.sleep(delay)
        self.served_count += 1
        return f"req_{req_id}_ok"

    async def get_served_count(self) -> int:
        return self.served_count


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    actor = AsyncRateLimiter.remote()
    ray.get(actor.get_served_count.remote())  # Warm-up actor process
    start = time.perf_counter()
    refs = [actor.process_request.remote(i, 0.08) for i in range(4)]
    results = ray.get(refs)
    elapsed = time.perf_counter() - start
    count = ray.get(actor.get_served_count.remote())

    expected_results = ["req_0_ok", "req_1_ok", "req_2_ok", "req_3_ok"]
    assert results == expected_results, f"Expected {expected_results}, got {results}"
    assert count == 4, f"Expected count 4, got {count}"
    print(f"Elapsed time for 4 concurrent async requests: {elapsed:.3f}s")
    assert elapsed < 0.22, f"Async actor took too long ({elapsed:.3f}s), concurrency not active"
    print("✓ actors04 verified: Async Actor max_concurrency coroutine concurrency confirmed!")


if __name__ == "__main__":
    verify()
