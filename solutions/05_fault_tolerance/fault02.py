"""Chapter 5: Fault Tolerance & Recovery - Solution 2: Actor Failure & Automatic Restarts.

Reference Solution for fault02.
"""

import os
import time
import ray


@ray.remote(max_restarts=2, max_task_retries=0)
class SelfHealingActor:
    def __init__(self) -> None:
        self.created_at = time.time()

    def ping(self) -> str:
        return "pong"

    def crash(self) -> None:
        os._exit(1)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    actor = SelfHealingActor.remote()
    first_ping = ray.get(actor.ping.remote())

    try:
        ray.get(actor.crash.remote())
    except Exception:
        pass

    recovered_ping = None
    for _ in range(10):
        try:
            recovered_ping = ray.get(actor.ping.remote())
            break
        except Exception:
            time.sleep(0.5)

    assert first_ping == "pong", f"Expected first ping 'pong', got {first_ping}"
    assert recovered_ping == "pong", f"Expected recovered ping 'pong', got {recovered_ping}"
    print(
        f"✓ fault02 verified: SelfHealingActor crashed and recovered automatically (first={first_ping}, recovered={recovered_ping})!"
    )


if __name__ == "__main__":
    verify()
