"""Chapter 3: Plasma Object Store & Zero-Copy - Exercise 4: Object Spilling & Memory Limits.

Ray's in-memory object store (Plasma) has a fixed capacity (by default ~30% of system RAM).
What happens when your workload generates more objects than will fit in RAM?

Object Spilling:
When the Plasma object store approaches capacity, Ray's object manager automatically
"spills" cold (least recently used) objects to local disk storage (or cloud storage like S3).
When a task or the driver subsequently calls `ray.get()` on a spilled object, Ray transparently
reads the data back from disk into memory without user intervention.

Key Concepts:
1. Automatic Spilling: Enables jobs to process datasets larger than available RAM.
2. Object Lifecycle & GC: Objects are pinned in Plasma as long as at least one Python
   `ObjectRef` points to them. When all references go out of scope (or are `del`'d),
   Ray reclaims the shared memory.

Your Task:
- Create a series of objects in Plasma using `ray.put()`.
- Store the `ObjectRef`s in a list.
- Retrieve and verify values from the earliest and latest stored objects.
- Demonstrate reference cleanup: delete references and verify memory is reclaimable.
"""

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
