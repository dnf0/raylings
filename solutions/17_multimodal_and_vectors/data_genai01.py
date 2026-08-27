"""Chapter 17: Multimodal & Vector Ray Data Pipelines - Solution 1: Streaming Multimodal Image & Audio ETL.

Reference Solution for data_genai01.
"""

import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import pyarrow as pa
import ray
import ray.data
from ray.data.extensions import ArrowTensorArray


def generate_multimodal_records(num_samples: int = 100) -> list[dict[str, Any]]:
    """Generate synthetic multimodal samples with raw uint8 images and audio spectrograms."""
    rng = np.random.default_rng(42)
    records = []
    for i in range(num_samples):
        # Raw uint8 RGB image [3, 32, 32]
        raw_img = rng.integers(0, 256, size=(3, 32, 32), dtype=np.uint8)
        # Raw audio spectrogram power [1, 16, 64]
        raw_spec = (rng.random(size=(1, 16, 64), dtype=np.float32) * 10.0).astype(np.float32)
        records.append({"id": i, "image": raw_img, "spectrogram": raw_spec})
    return records


def transform_multimodal_batch(batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Apply vectorized image normalization and audio log-spectrogram transformation."""
    # 1. Normalize image tensors: scale to [0, 1] float32 and standardize
    images = batch["image"].astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)
    normalized_images = (images - mean) / std

    # 2. Compute log power spectrogram
    log_spectrograms = np.log1p(np.maximum(0.0, batch["spectrogram"]))

    return {
        "id": batch["id"],
        "image": normalized_images,
        "spectrogram": log_spectrograms,
    }


def pack_to_arrow_tensor_table(batch: dict[str, np.ndarray]) -> pa.Table:
    """Pack NumPy multimodal arrays into an Apache Arrow Table with Tensor extension types."""
    id_array = pa.array(batch["id"])
    image_tensor_array = ArrowTensorArray.from_numpy(batch["image"])
    spec_tensor_array = ArrowTensorArray.from_numpy(batch["spectrogram"])

    table = pa.Table.from_arrays(
        [id_array, image_tensor_array, spec_tensor_array],
        names=["id", "image", "spectrogram"],
    )
    return table


def stream_pipeline_batches(
    ds: ray.data.Dataset, batch_size: int = 20
) -> list[dict[str, np.ndarray]]:
    """Stream batches lazily from dataset with bounded memory footprint."""
    streamed = []
    for batch in ds.iter_batches(batch_size=batch_size, batch_format="numpy"):
        streamed.append(batch)
    return streamed


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    num_samples = 100
    batch_size = 20
    records = generate_multimodal_records(num_samples=num_samples)

    # 1. Create Ray Dataset
    ds = ray.data.from_items(records)

    # 2. Test Arrow Tensor packing on a sample batch
    sample_batch = {
        "id": np.array([r["id"] for r in records[:5]]),
        "image": np.stack([r["image"] for r in records[:5]]),
        "spectrogram": np.stack([r["spectrogram"] for r in records[:5]]),
    }
    arrow_table = pack_to_arrow_tensor_table(sample_batch)
    assert arrow_table is not None, "pack_to_arrow_tensor_table returned None"
    assert "image" in arrow_table.column_names and "spectrogram" in arrow_table.column_names, (
        f"Missing columns in Arrow table: {arrow_table.column_names}"
    )

    # 3. Apply lazy map_batches transform
    transformed_ds = ds.map_batches(transform_multimodal_batch, batch_format="numpy")

    # 4. Stream transformed batches
    streamed_batches = stream_pipeline_batches(transformed_ds, batch_size=batch_size)
    assert streamed_batches is not None, "stream_pipeline_batches returned None"
    assert len(streamed_batches) == (num_samples // batch_size), (
        f"Expected {num_samples // batch_size} batches, got {len(streamed_batches)}"
    )

    total_rows = 0
    for idx, batch in enumerate(streamed_batches):
        b_size = len(batch["id"])
        total_rows += b_size
        assert batch["image"].shape == (b_size, 3, 32, 32), (
            f"Batch {idx} image shape mismatch: {batch['image'].shape}"
        )
        assert batch["spectrogram"].shape == (b_size, 1, 16, 64), (
            f"Batch {idx} spectrogram shape mismatch: {batch['spectrogram'].shape}"
        )
        assert batch["image"].dtype == np.float32, (
            f"Batch {idx} image dtype must be float32, got {batch['image'].dtype}"
        )

    assert total_rows == num_samples, f"Expected {num_samples} total rows, got {total_rows}"

    print(
        f"✓ data_genai01 verified: Streamed {num_samples} multimodal samples across "
        f"{len(streamed_batches)} batches with zero-copy Arrow tensor packing!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
