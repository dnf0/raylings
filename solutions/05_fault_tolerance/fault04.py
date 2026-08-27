"""Chapter 5: Fault Tolerance & Recovery - Solution 4: Actor State Checkpointing.

Reference Solution for fault04.
"""

import os
import tempfile
import time
from pathlib import Path

import ray


@ray.remote(max_restarts=2, max_task_retries=0)
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
        actor = CheckpointCounter.remote(ckpt_path)

        for _ in range(5):
            ray.get(actor.increment.remote())

        try:
            ray.get(actor.crash.remote())
        except Exception:
            pass

        restored_count = None
        for _ in range(10):
            try:
                restored_count = ray.get(actor.get_count.remote())
                break
            except Exception:
                time.sleep(0.5)

        assert restored_count == 5, f"Expected restored count 5, got {restored_count}"
        print(
            f"✓ fault04 verified: Checkpoint state successfully recovered after actor crash (count={restored_count})!"
        )
    finally:
        if Path(ckpt_path).exists():
            Path(ckpt_path).unlink()


if __name__ == "__main__":
    verify()
