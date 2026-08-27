"""Chapter 17: Multimodal & Vector Ray Data Pipelines - Exercise 3: Dynamic Token Length Bucketing & Padding Optimization.

In LLM pre-training, fine-tuning, and embedding extraction, inputs exhibit variable sequence lengths.
To perform batched tensor operations on GPUs/TPUs, sequences within each batch must be padded
to the maximum sequence length in that batch.

Naive batching groups arbitrary documents together. When a short sequence (e.g. 16 tokens)
is paired with a long document (e.g. 512 tokens), 496 tokens (over 96%) are wasted padding tokens,
wasting memory bandwidth and matrix multiplication FLOPs.

Dynamic length bucketing groups sequences of similar lengths into matched bins before micro-batching,
dramatically minimizing padding token overhead (>50% reduction).

Key Concepts:
- `Length Bucketing / Sorting`: Grouping or sorting dataset items by `seq_len` ensures that
  within any micro-batch, sequence lengths are nearly uniform.
- `Dynamic In-Batch Padding`: Instead of padding all batches globally to `MAX_SEQ_LEN` (e.g., 2048 or 4096),
  each batch is padded dynamically only to the local maximum length of that specific batch.
- `Attention Mask Generation`: Produces binary masks (`1` for real tokens, `0` for `<pad>`)
  alongside padded `input_ids` for transformer attention kernels.

Your Task:
- In `pad_token_batch(batch, pad_token_id)`:
  - Find `max_len = max(len(toks) for toks in batch["tokens"])`.
  - For each sample, pad `tokens` up to `max_len` using `pad_token_id` (default `0`).
  - Construct `attention_mask` (`1` for token, `0` for padding).
  - Compute total actual tokens and total padding tokens.
  - Return dict with `"doc_id"`, `"input_ids"`, `"attention_mask"`, `"actual_tokens"`, and `"pad_tokens"`.
- In `compute_batch_padding_stats(batches)`:
  - Sum `actual_tokens` and `pad_tokens` across all batches.
  - Calculate `padding_ratio = total_pad / (total_actual + total_pad)`.
  - Return `(total_actual, total_pad, padding_ratio)`.
- In `create_bucketed_dataset(ds)`:
  - Sort or bucket `ds` by `"seq_len"` so that sequences of similar lengths are placed adjacent to each other.
"""

# I AM NOT DONE
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
    # TODO: 1. Determine max_len in this batch
    # TODO: 2. Create rectangular input_ids and attention_mask arrays
    # TODO: 3. Calculate actual_tokens and pad_tokens
    # TODO: 4. Return dict with doc_id, input_ids, attention_mask, actual_tokens, pad_tokens
    pass


def compute_batch_padding_stats(batches: list[dict[str, Any]]) -> tuple[int, int, float]:
    """Aggregate total actual tokens, padding tokens, and padding overhead ratio."""
    # TODO: Sum actual_tokens and pad_tokens across batches and compute ratio
    pass


def create_bucketed_dataset(ds: ray.data.Dataset) -> ray.data.Dataset:
    """Sort or partition dataset by sequence length for minimal padding variance."""
    # TODO: Sort dataset by "seq_len"
    pass


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
