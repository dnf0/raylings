"""
Exercise: exercises/08_ray_data/data05.py
Topic: PyTorch DataLoader Interoperability

Context & Why:
Ray Data provides seamless zero-copy streaming into distributed PyTorch training loops via
`dataset.iter_torch_batches(batch_size=B, prefetch_batches=P)`.

This replaces standard PyTorch `DataLoader` with multi-node distributed streaming, prefetching, and sharding.

Instructions:
1. Convert a Ray Dataset into PyTorch tensors using `iter_torch_batches()`.
2. Iterate batches in a simulated training loop.
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
