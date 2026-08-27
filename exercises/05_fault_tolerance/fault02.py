"""Chapter 5: Fault Tolerance & Recovery - Exercise 2: Actor Failure & Automatic Restarts.

Unlike stateless tasks, actors maintain internal state in their worker process memory.
If an actor process crashes (due to OOM, segfault, or machine death):
- By default (`max_restarts=0`), any subsequent calls to the actor raise `RayActorError`.
- If `max_restarts > 0`, Ray automatically restarts the actor process up to `max_restarts` times!
- When the actor is recreated, subsequent method invocations succeed on the new actor process.

Example:
    @ray.remote(max_restarts=2, max_task_retries=0)
    class ResilientService:
        def __init__(self):
            self.count = 0

        def crash(self):
            os._exit(1)

        def ping(self):
            return "alive"

Your Task:
- Define a `@ray.remote(max_restarts=2, max_task_retries=0)` actor `SelfHealingActor` with:
  - `__init__(self)`: initializes `self.created_at = time.time()`
  - `ping(self) -> str`: returns `"pong"`
  - `crash(self) -> None`: immediately terminates the actor process using `os._exit(1)`
- In `verify()`:
  - Create an instance of `SelfHealingActor`.
  - Verify `ping()` returns `"pong"`.
  - Call `crash()` (catch and ignore the `Exception` caused by the crashing process).
  - Verify that subsequent calls to `ping()` succeed and return `"pong"` as Ray restarts the actor!
"""

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
