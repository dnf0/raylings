"""Chapter 8: Ray Data for High-Throughput ETL - Solution 5: PyTorch DataLoader Interop (iter_torch_batches).

Reference Solution for data05.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.data
import torch


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    items = [{"x": float(i), "y": float(i * 2)} for i in range(16)]
    ds = ray.data.from_items(items)

    batch_count = 0
    for batch in ds.iter_torch_batches(batch_size=4):
        assert isinstance(batch["x"], torch.Tensor)
        assert batch["x"].shape == torch.Size([4])
        batch_count += 1

    assert batch_count == 4, f"Expected 4 mini-batches, got {batch_count}"
    print(f"✓ data05 verified: Streamed {batch_count} mini-batches into PyTorch tensors!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
