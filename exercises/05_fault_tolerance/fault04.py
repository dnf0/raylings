# I AM NOT DONE
"""Chapter 5: Fault Tolerance & Recovery - Exercise 4: Actor State Checkpointing.

When running distributed workloads on Spot Instances or preemptible machines, an actor
might be restarted from scratch. While `max_restarts` spins up a fresh actor process,
the actor's in-memory variables revert to their initial state unless explicitly restored.

Production Checkpointing Pattern:
1. State Persistence: The actor periodically writes a checkpoint (to local disk, S3, or GCS)
   during state modifications.
2. Startup Recovery: In `__init__`, the actor checks if a checkpoint file exists and
   restores its internal state.

Example:
    @ray.remote(max_restarts=2, max_task_retries=0)
    class CheckpointWorker:
        def __init__(self, ckpt_path: Path):
            self.ckpt_path = ckpt_path
            self.step = self._load()

        def _load(self):
            if self.ckpt_path.exists():
                text = self.ckpt_path.read_text().strip()
                return int(text) if text else 0
            return 0

Your Task:
- Define a `@ray.remote(max_restarts=2, max_task_retries=0)` actor `CheckpointCounter`:
  - `__init__(self, checkpoint_file: str)`:
    - Checks if `checkpoint_file` exists. If so, reads non-empty integer count; otherwise initializes to 0.
  - `increment(self) -> int`:
    - Increments `self.count`, writes `str(self.count)` to `checkpoint_file`, and returns `self.count`.
  - `crash(self) -> None`:
    - Calls `os._exit(1)` to simulate abrupt process death.
  - `get_count(self) -> int`: returns `self.count`.
- In `verify()`:
  - Increment count to 5.
  - Crash the actor.
  - Call `get_count()` on the restarted actor and assert state was restored to 5!
"""

import os
import tempfile
import time
from pathlib import Path

import ray


# TODO: Define CheckpointCounter actor with max_restarts=2, max_task_retries=0
class CheckpointCounter:
    def __init__(self, checkpoint_file: str) -> None:
        self.checkpoint_file = Path(checkpoint_file)
        self.count = self._load_state()

    def _load_state(self) -> int:
        if self.checkpoint_file.exists():
            content = self.checkpoint_file.read_text(encoding="utf-8").strip()
            if content:
                return int(content)
        return 0

    def increment(self) -> int:
        self.count += 1
        self.checkpoint_file.write_text(str(self.count), encoding="utf-8")
        return self.count

    def get_count(self) -> int:
        return self.count

    def crash(self) -> None:
        os._exit(1)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        ckpt_path = tmp.name

    try:
        # TODO: Instantiate actor with ckpt_path
        # actor = CheckpointCounter.remote(ckpt_path)

        # TODO: Increment count 5 times
        # for _ in range(5):
        #     ray.get(actor.increment.remote())

        # TODO: Trigger crash
        # try:
        #     ray.get(actor.crash.remote())
        # except Exception:
        #     pass

        # TODO: Retrieve count after automatic restart
        # restored_count = None
        # for _ in range(10):
        #     try:
        #         restored_count = ray.get(actor.get_count.remote())
        #         break
        #     except Exception:
        #         time.sleep(0.5)
        restored_count = None

        assert restored_count == 5, f"Expected restored count 5, got {restored_count}"
        print(
            f"✓ fault04 verified: Checkpoint state successfully recovered after actor crash (count={restored_count})!"
        )
    finally:
        if Path(ckpt_path).exists():
            Path(ckpt_path).unlink()


if __name__ == "__main__":
    verify()
