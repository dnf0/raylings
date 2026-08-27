"""Chapter 17: Multimodal & Vector Ray Data Pipelines - Solution 3: Dynamic Token Length Bucketing & Padding Optimization.

Reference Solution for data_genai03.
"""

import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray
import ray.data


def generate_variable_length_dataset(
    num_docs: int = 200, min_len: int = 16, max_len: int = 512, seed: int = 42
) -> list[dict[str, Any]]:
    """Generate synthetic documents with heavy-tailed variable sequence lengths."""
    rng = np.random.default_rng(seed)
    records = []
    for i in range(num_docs):
        length = int(rng.exponential(scale=100)) + min_len
        length = min(max_len, max(min_len, length))
        tokens = rng.integers(1, 10000, size=length).tolist()
        records.append({"doc_id": i, "tokens": tokens, "seq_len": length})
    return records


def pad_token_batch(
    batch: dict[str, list[list[int]] | np.ndarray], pad_token_id: int = 0
) -> dict[str, Any]:
    """Dynamically pad token sequences in a batch to the batch maximum length."""
    tokens_list = list(batch["tokens"])
    batch_size = len(tokens_list)
    lengths = [len(toks) for toks in tokens_list]
    max_len = max(lengths)

    input_ids = np.full((batch_size, max_len), pad_token_id, dtype=np.int64)
    attention_mask = np.zeros((batch_size, max_len), dtype=np.int64)

    actual_tokens = 0
    pad_tokens = 0
    for idx, (toks, length) in enumerate(zip(tokens_list, lengths)):
        input_ids[idx, :length] = toks
        attention_mask[idx, :length] = 1
        actual_tokens += length
        pad_tokens += max_len - length

    return {
        "doc_id": batch["doc_id"],
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "actual_tokens": actual_tokens,
        "pad_tokens": pad_tokens,
    }


def compute_batch_padding_stats(batches: list[dict[str, Any]]) -> tuple[int, int, float]:
    """Aggregate total actual tokens, padding tokens, and padding overhead ratio."""
    total_actual = sum(b["actual_tokens"] for b in batches)
    total_pad = sum(b["pad_tokens"] for b in batches)
    total_tokens = total_actual + total_pad
    ratio = total_pad / total_tokens if total_tokens > 0 else 0.0
    return total_actual, total_pad, ratio


def create_bucketed_dataset(ds: ray.data.Dataset) -> ray.data.Dataset:
    """Sort or partition dataset by sequence length for minimal padding variance."""
    return ds.sort(key="seq_len")


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    num_docs = 200
    batch_size = 16
    records = generate_variable_length_dataset(num_docs=num_docs)

    # 1. Evaluate Naive Sequential Batching
    naive_ds = ray.data.from_items(records)
    naive_batches = [
        pad_token_batch(b)
        for b in naive_ds.iter_batches(batch_size=batch_size, batch_format="numpy")
    ]
    n_act, n_pad, n_ratio = compute_batch_padding_stats(naive_batches)

    # 2. Evaluate Dynamic Length Bucketed Batching
    bucketed_ds = create_bucketed_dataset(naive_ds)
    bucketed_batches = [
        pad_token_batch(b)
        for b in bucketed_ds.iter_batches(batch_size=batch_size, batch_format="numpy")
    ]
    b_act, b_pad, b_ratio = compute_batch_padding_stats(bucketed_batches)

    # 3. Assertions & Verification
    assert n_act == b_act, f"Actual token count mismatch: naive={n_act} vs bucketed={b_act}"
    assert n_pad > 0, "Naive padding must be greater than 0"
    assert b_pad < n_pad, f"Bucketed padding ({b_pad}) should be lower than naive ({n_pad})"

    padding_reduction = (n_pad - b_pad) / n_pad
    assert padding_reduction > 0.50, (
        f"Expected >50% padding reduction from bucketing, got {padding_reduction:.2%}"
    )

    # Check batch shapes and mask alignment
    for batch in bucketed_batches:
        ids = batch["input_ids"]
        mask = batch["attention_mask"]
        assert ids.shape == mask.shape, f"Shape mismatch: {ids.shape} vs {mask.shape}"
        assert np.all((mask == 1) | (mask == 0)), "Mask values must be binary (0 or 1)"

    print(
        f"✓ data_genai03 verified: Dynamic length bucketing slashed padding overhead by "
        f"{padding_reduction:.2%} (naive: {n_ratio:.2%} pad -> bucketed: {b_ratio:.2%} pad)!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
