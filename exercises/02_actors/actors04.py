"""
Exercise: exercises/02_actors/actors04.py
Topic: Async Actors & Coroutine Concurrency

Context & Why:
By default, Ray actors execute one method call at a time. If an actor method performs I/O
(e.g., waiting for external REST APIs, database queries, or network requests), the actor sits idle,
blocking all other incoming calls in its mailbox.

Ray solves this with **Async Actors**:
1. Define methods using `async def` and `await`.
2. Configure `@ray.remote(max_concurrency=N)` to allow up to `N` coroutines to run concurrently
   on the actor's single-threaded `asyncio` event loop.

Instructions:
1. Define an async actor with `@ray.remote(max_concurrency=10)`.
2. Implement an `async def fetch_data(self, url: str)` method using `await asyncio.sleep(...)`.
3. Verify that multiple async requests run concurrently with significant speedup over sequential execution.
"""

# I AM NOT DONE

import asyncio  # noqa: F401
import time  # noqa: F401

import ray


# TODO: Decorate with @ray.remote(max_concurrency=5)
class AsyncRateLimiter:
    def __init__(self) -> None:
        self.served_count = 0

    # TODO: Implement async def process_request(self, req_id: int, delay: float) -> str
    def process_request(self, req_id: int, delay: float) -> str:
        # await asyncio.sleep(delay)
        # self.served_count += 1
        # return f"req_{req_id}_ok"
        pass

    async def get_served_count(self) -> int:
        return self.served_count


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate AsyncRateLimiter
    # actor = AsyncRateLimiter.remote()
    # ray.get(actor.get_served_count.remote())  # Warm-up actor process
    # start = time.perf_counter()
    # refs = [actor.process_request.remote(i, 0.08) for i in range(4)]
    # results = ray.get(refs)
    # elapsed = time.perf_counter() - start
    # count = ray.get(actor.get_served_count.remote())
    results, elapsed, count = None, 999.0, 0

    expected_results = ["req_0_ok", "req_1_ok", "req_2_ok", "req_3_ok"]
    assert results == expected_results, f"Expected {expected_results}, got {results}"
    assert count == 4, f"Expected count 4, got {count}"
    print(f"Elapsed time for 4 concurrent async requests: {elapsed:.3f}s")
    assert elapsed < 0.30, f"Async actor took too long ({elapsed:.3f}s), concurrency not active"
    print("✓ actors04 verified: Async Actor max_concurrency coroutine concurrency confirmed!")


if __name__ == "__main__":
    verify()
