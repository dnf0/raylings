"""Chapter 8: Ray Data for High-Throughput ETL - Exercise 5: PyTorch DataLoader Interop (iter_torch_batches).

Feeding data into PyTorch models efficiently is critical for high GPU utilization.
Ray Data provides `ds.iter_torch_batches(batch_size=B)` which streams mini-batches directly
as PyTorch `torch.Tensor`s with zero-copy memory transfers:

Key Parameters:
- `batch_size`: Number of samples per batch tensor.
- `dtypes`: Optional dict mapping column names to `torch.dtype` (e.g. `torch.float32`, `torch.int64`).
- `device`: Optional PyTorch device (e.g. `"cpu"` or `"cuda"`).

Example:
```python
for batch in ds.iter_torch_batches(batch_size=32):
    features = batch["features"]  # torch.Tensor of shape (32, ...)
    labels = batch["label"]       # torch.Tensor of shape (32,)
    # Forward pass: model(features)
```

Your Task:
- In `verify()`:
  - Create dataset from `[{'x': float(i), 'y': float(i * 2)} for i in range(16)]`.
  - Iterate over `ds.iter_torch_batches(batch_size=4)`.
  - Accumulate batch count and verify the shapes of `batch['x']` and `batch['y']` are `torch.Size([4])`.
  - Assert that exactly 4 mini-batches were produced.
"""

# I AM NOT DONE
import ray
import ray.data
import torch


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"x": float(i), "y": float(i * 2)} for i in range(16)]
    ds = ray.data.from_items(items)

    # TODO: Stream batches via iter_torch_batches
    # batch_count = 0
    # for batch in ds.iter_torch_batches(batch_size=4):
    #     assert isinstance(batch["x"], torch.Tensor)
    #     assert batch["x"].shape == torch.Size([4])
    #     batch_count += 1
    batch_count = 0

    assert batch_count == 4, f"Expected 4 mini-batches, got {batch_count}"
    print(f"✓ data05 verified: Streamed {batch_count} mini-batches into PyTorch tensors!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
