"""
Exercise: exercises/17_multimodal_and_vectors/data_genai02.py
Topic: Accelerated Batch Embeddings with ActorPoolStrategy

Context & Why:
Extracting vector embeddings from millions of documents requires persistent neural encoder models.
`dataset.map_batches(Encoder, compute=ActorPoolStrategy(min_size=2))` keeps embedding models loaded
in worker memory, streaming documents through GPU/CPU encoder pools.

Instructions:
1. Implement batch embedding extractor with `ActorPoolStrategy`.
2. Verify embedding generation and normalization.
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
