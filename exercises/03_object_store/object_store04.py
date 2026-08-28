"""
Exercise: exercises/03_object_store/object_store04.py
Topic: Plasma Object Spilling & Bounded Capacity

Context & Why:
The Plasma object store operates in a pre-allocated shared memory partition (typically 30% of system RAM).
When total active objects exceed available Plasma memory, Ray's object manager automatically
**spills** cold objects to local NVMe disk or cloud storage (e.g. S3), restoring them transparently when requested.

Understanding object references and avoiding leaked `ObjectRef`s prevents excessive disk thrashing.

Instructions:
1. Configure object spilling parameters or observe object lifecycle behavior.
2. Verify that Ray handles objects larger than individual worker memory seamlessly.
"""

# I AM NOT DONE

import numpy as np
import ray
from ray import ObjectRef


def create_chunks(num_chunks: int, chunk_size: int) -> list[ObjectRef]:
    """Store multiple chunks of data in Plasma object store."""
    # TODO: Create `num_chunks` NumPy arrays of `chunk_size` floats and store each with ray.put()
    # refs = [ray.put(np.ones(chunk_size, dtype=np.float64) * i) for i in range(num_chunks)]
    # return refs
    return []


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    num_chunks = 10
    chunk_size = 10_000

    # TODO: Create chunks
    # chunk_refs = create_chunks(num_chunks, chunk_size)
    chunk_refs: list[ObjectRef] = []

    assert len(chunk_refs) == num_chunks, f"Expected {num_chunks} refs, got {len(chunk_refs)}"

    # Retrieve first and last chunks
    first_chunk = ray.get(chunk_refs[0])
    last_chunk = ray.get(chunk_refs[-1])

    assert np.all(first_chunk == 0.0), "First chunk should be filled with 0.0"
    assert np.all(last_chunk == 9.0), "Last chunk should be filled with 9.0"

    # Demonstrate garbage collection: removing references allows Ray to free Plasma memory
    del chunk_refs
    print(
        f"✓ object_store04 verified: Stored {num_chunks} chunks ({num_chunks * chunk_size * 8 / 1024:.1f} KB) and validated retrieval & lifecycle!"
    )


if __name__ == "__main__":
    verify()
