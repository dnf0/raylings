"""Chapter 17: Multimodal & Vector Ray Data Pipelines - Solution 4: Streaming Parallel Ingestion into Vector Databases.

Reference Solution for data_genai04.
"""

import os
from collections.abc import Iterable
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray
import ray.data
from ray.data.block import Block, BlockAccessor
from ray.data.datasource.datasink import Datasink


@ray.remote
class MockVectorIndexStore:
    """Stateful actor representing a partitioned vector database index cluster."""

    def __init__(self, num_partitions: int = 4) -> None:
        self.num_partitions = num_partitions
        self.partitions: dict[int, dict[int, np.ndarray]] = {i: {} for i in range(num_partitions)}

    def upsert_batch(self, partition_id: int, records: list[tuple[int, np.ndarray]]) -> int:
        """Idempotently insert or update vectors in a specific partition."""
        for doc_id, vector in records:
            self.partitions[partition_id][doc_id] = vector
        return len(records)

    def get_stats(self) -> dict[str, Any]:
        """Return total document count and per-partition distribution."""
        total_docs = sum(len(p) for p in self.partitions.values())
        counts_per_part = {p: len(docs) for p, docs in self.partitions.items()}
        return {"total_docs": total_docs, "counts_per_partition": counts_per_part}

    def query_nearest(
        self, partition_id: int, query_vec: np.ndarray, top_k: int = 3
    ) -> list[tuple[int, float]]:
        """Search nearest vectors in a partition via dot-product cosine similarity."""
        part = self.partitions.get(partition_id, {})
        if not part:
            return []
        scores = []
        for doc_id, vec in part.items():
            sim = float(np.dot(query_vec, vec))
            scores.append((doc_id, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class VectorDatabaseDatasink(Datasink):
    """Custom streaming Ray Data sink for parallel ingestion into partitioned vector indices."""

    def __init__(self, store_actor: Any, num_partitions: int = 4) -> None:
        self.store_actor = store_actor
        self.num_partitions = num_partitions

    def write(self, blocks: Iterable[Block], ctx: Any) -> int:
        """Write blocks in parallel to target index partitions."""
        total_written = 0
        partition_buffers: dict[int, list[tuple[int, np.ndarray]]] = {
            i: [] for i in range(self.num_partitions)
        }

        for block in blocks:
            accessor = BlockAccessor.for_block(block)
            batch = accessor.to_numpy()
            doc_ids = batch["id"]
            embeddings = batch["embedding"]
            for doc_id, vec in zip(doc_ids, embeddings):
                int_id = int(doc_id)
                part_id = int_id % self.num_partitions
                partition_buffers[part_id].append((int_id, vec))

        futures = []
        for part_id, records in partition_buffers.items():
            if records:
                futures.append(self.store_actor.upsert_batch.remote(part_id, records))

        if futures:
            results = ray.get(futures)
            total_written += sum(results)

        return total_written


def generate_vector_documents(num_docs: int = 1000, dim: int = 32) -> list[dict[str, Any]]:
    """Generate document records with unit-normalized embedding vectors."""
    rng = np.random.default_rng(42)
    records = []
    for i in range(num_docs):
        vec = rng.standard_normal(dim).astype(np.float32)
        vec /= np.linalg.norm(vec)
        records.append({"id": i, "embedding": vec})
    return records


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    num_docs = 1000
    num_partitions = 4
    dim = 32

    # 1. Initialize mock partitioned vector database actor
    store = MockVectorIndexStore.remote(num_partitions=num_partitions)

    # 2. Create distributed dataset of embedded vectors
    docs = generate_vector_documents(num_docs=num_docs, dim=dim)
    ds = ray.data.from_items(docs).repartition(8)

    # 3. Stream parallel ingestion through custom Datasink
    sink = VectorDatabaseDatasink(store_actor=store, num_partitions=num_partitions)
    ds.write_datasink(sink)

    # 4. Verify ingestion consistency and partition distribution
    stats = ray.get(store.get_stats.remote())
    assert stats is not None, "get_stats returned None"
    assert stats["total_docs"] == num_docs, (
        f"Expected {num_docs} indexed documents, got {stats['total_docs']}"
    )

    counts = stats["counts_per_partition"]
    expected_per_part = num_docs // num_partitions
    for part_id, count in counts.items():
        assert count == expected_per_part, (
            f"Partition {part_id} has {count} docs, expected {expected_per_part}"
        )

    # 5. Verify similarity query retrieval
    query_target = docs[0]
    nearest = ray.get(
        store.query_nearest.remote(partition_id=0, query_vec=query_target["embedding"], top_k=1)
    )
    assert len(nearest) == 1, f"Expected 1 top match, got {nearest}"
    assert nearest[0][0] == query_target["id"], (
        f"Expected top match doc_id {query_target['id']}, got {nearest[0][0]}"
    )
    assert abs(nearest[0][1] - 1.0) < 1e-4, f"Self-similarity should be ~1.0, got {nearest[0][1]}"

    print(
        f"✓ data_genai04 verified: Streamed and indexed {num_docs} vectors across "
        f"{num_partitions} partitions with 100% data integrity!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
