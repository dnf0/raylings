"""Chapter 17: Multimodal & Vector Ray Data Pipelines - Exercise 2: Accelerated Batch Embeddings with ActorPoolStrategy.

High-throughput embedding pipelines (e.g. for Vector Search, RAG indexing, or contrastive learning)
require extracting dense representations from millions of text or image records.
Re-initializing heavy neural models (such as BERT, CLIP, or SentenceTransformers) on every
individual task incurs catastrophic model loading latency and memory churn.

Ray Data addresses this using stateful callable classes mapped via `ActorPoolStrategy`.
Actors load model weights into device memory once during `__init__`, and subsequent
batches are streamed through the existing actor pool with zero serialization overhead.

Key Concepts:
- `ActorPoolStrategy(min_size=K, max_size=K)`: Spawns an actor pool of persistent workers
  that maintain stateful neural weights in memory across batch invocations.
- `Vectorized map_batches`: Feeds micro-batches to actor workers, maximizing hardware
  vectorization (SIMD / Tensor Cores).
- `Zero-Copy In-Flight Execution`: Avoids copying intermediate activations by transforming
  directly between NumPy/PyTorch/Arrow memory buffers.

Your Task:
- In `BatchEmbeddingExtractor`:
  - In `__init__(self, in_features, embedding_dim, normalize)`:
    - Initialize a PyTorch linear projection `nn.Linear(in_features, embedding_dim, bias=False)`.
    - Set the model to evaluation mode (`self.model.eval()`).
    - Record `self.worker_pid = os.getpid()`.
  - In `__call__(self, batch)`:
    - Convert `batch["tokens"]` to a PyTorch float tensor.
    - Inside `torch.no_grad()`, compute projected embeddings: `self.model(x)`.
    - If `self.normalize` is True, apply L2 normalization: `torch.nn.functional.normalize(emb, p=2, dim=-1)`.
    - Return dict containing `"doc_id"`, `"embedding"` (NumPy array of shape `[batch_size, embedding_dim]`),
      and `"worker_pid"` array filled with `self.worker_pid`.
- In `extract_embeddings_distributed(ds, min_workers, max_workers, batch_size)`:
  - Map `BatchEmbeddingExtractor` over `ds` using `compute=ray.data.ActorPoolStrategy(min_size=min_workers, max_size=max_workers)`
    with the specified `batch_size` and `batch_format="numpy"`.
"""

import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray
import ray.data
import torch
import torch.nn as nn


class BatchEmbeddingExtractor:
    """Stateful actor worker that loads an embedding model once and processes batched records."""

    def __init__(
        self, in_features: int = 32, embedding_dim: int = 64, normalize: bool = True
    ) -> None:
        self.in_features = in_features
        self.embedding_dim = embedding_dim
        self.normalize = normalize
        # TODO: Initialize nn.Linear, eval mode, and store os.getpid()
        pass

    def __call__(self, batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        # TODO: Forward pass in torch.no_grad(), optional L2 normalization, return dict
        pass


def extract_embeddings_distributed(
    ds: ray.data.Dataset,
    min_workers: int = 2,
    max_workers: int = 2,
    batch_size: int = 16,
) -> ray.data.Dataset:
    """Extract embeddings across a Ray Data ActorPoolStrategy worker pool."""
    # TODO: Invoke ds.map_batches with BatchEmbeddingExtractor and ActorPoolStrategy
    pass


def generate_document_records(num_docs: int = 100, in_features: int = 32) -> list[dict[str, Any]]:
    """Generate mock document records with synthetic token representations."""
    rng = np.random.default_rng(42)
    return [
        {"doc_id": i, "tokens": rng.standard_normal(in_features).astype(np.float32)}
        for i in range(num_docs)
    ]


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    num_docs = 100
    in_features = 32
    embedding_dim = 64
    min_workers = 2
    max_workers = 2
    batch_size = 16

    docs = generate_document_records(num_docs=num_docs, in_features=in_features)
    ds = ray.data.from_items(docs)

    embedded_ds = extract_embeddings_distributed(
        ds=ds,
        min_workers=min_workers,
        max_workers=max_workers,
        batch_size=batch_size,
    )
    assert embedded_ds is not None, "extract_embeddings_distributed returned None"

    results = embedded_ds.take_all()
    assert len(results) == num_docs, f"Expected {num_docs} results, got {len(results)}"

    # Validate output shapes and normalization
    worker_pids = set()
    for row in results:
        emb = row["embedding"]
        assert emb.shape == (embedding_dim,), f"Expected shape ({embedding_dim},), got {emb.shape}"
        l2_norm = float(np.linalg.norm(emb))
        assert abs(l2_norm - 1.0) < 1e-4, f"Embedding is not unit normalized: L2 norm = {l2_norm}"
        worker_pids.add(row["worker_pid"])

    assert len(worker_pids) >= min_workers, (
        f"Expected at least {min_workers} distinct worker actor processes, got {len(worker_pids)}"
    )

    print(
        f"✓ data_genai02 verified: Extracted {embedding_dim}-dim unit embeddings for {num_docs} "
        f"documents across {len(worker_pids)} stateful ActorPool workers!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
