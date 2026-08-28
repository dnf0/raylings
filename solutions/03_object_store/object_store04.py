"""Chapter 3: Plasma Object Store & Zero-Copy - Solution 4: Object Spilling & Memory Limits.

Reference Solution for object_store04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray
from ray import ObjectRef


def create_chunks(num_chunks: int, chunk_size: int) -> list[ObjectRef]:
    """Store multiple chunks of data in Plasma object store."""
    refs = [ray.put(np.ones(chunk_size, dtype=np.float64) * i) for i in range(num_chunks)]
    return refs


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    num_chunks = 10
    chunk_size = 10_000

    chunk_refs = create_chunks(num_chunks, chunk_size)

    assert len(chunk_refs) == num_chunks, f"Expected {num_chunks} refs, got {len(chunk_refs)}"

    first_chunk = ray.get(chunk_refs[0])
    last_chunk = ray.get(chunk_refs[-1])

    assert np.all(first_chunk == 0.0), "First chunk should be filled with 0.0"
    assert np.all(last_chunk == 9.0), "Last chunk should be filled with 9.0"

    del chunk_refs
    print(
        f"✓ object_store04 verified: Stored {num_chunks} chunks ({num_chunks * chunk_size * 8 / 1024:.1f} KB) and validated retrieval & lifecycle!"
    )


if __name__ == "__main__":
    verify()
