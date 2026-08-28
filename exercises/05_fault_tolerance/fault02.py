"""
Exercise: exercises/05_fault_tolerance/fault02.py
Topic: Actor Restarts & State Recovery

Context & Why:
Unlike stateless tasks, when a stateful actor process crashes, its in-memory state is lost.
Configuring `@ray.remote(max_restarts=2)` instructs Ray to automatically restart the actor process.

Actors can recover state by loading checkpoints from persistent storage inside their `__init__` method.

Instructions:
1. Configure `max_restarts=2` on a stateful actor.
2. Simulate worker process failure and verify that Ray restarts the actor.
"""

# I AM NOT DONE

import os
import time

import ray


# TODO: Define SelfHealingActor with max_restarts=2 and max_task_retries=0
class SelfHealingActor:
    def __init__(self) -> None:
        self.created_at = time.time()

    def ping(self) -> str:
        return "pong"

    def crash(self) -> None:
        os._exit(1)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Instantiate SelfHealingActor
    # actor = SelfHealingActor.remote()
    # first_ping = ray.get(actor.ping.remote())

    # TODO: Trigger a crash and wait for recovery
    # try:
    #     ray.get(actor.crash.remote())
    # except Exception:
    #     pass

    # TODO: Wait for restarted actor and retrieve ping
    # recovered_ping = None
    # for _ in range(10):
    #     try:
    #         recovered_ping = ray.get(actor.ping.remote())
    #         break
    #     except Exception:
    #         time.sleep(0.5)
    first_ping, recovered_ping = None, None

    assert first_ping == "pong", f"Expected first ping 'pong', got {first_ping}"
    assert recovered_ping == "pong", f"Expected recovered ping 'pong', got {recovered_ping}"
    print(
        f"✓ fault02 verified: SelfHealingActor crashed and recovered automatically (first={first_ping}, recovered={recovered_ping})!"
    )


if __name__ == "__main__":
    verify()
