"""Pure Ray distributed helpers for multi-node KubeRay integration tests.

Isolated from pytest dependencies to ensure clean cloudpickle serialization
and compatibility across remote Kubernetes worker pods.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
import pyarrow as pa
import ray
import torch
import torch.nn as nn


@ray.remote(num_cpus=0.5)
class WorkerNodeProbe:
    """Actor probe for querying node execution context."""

    def get_info(self) -> dict[str, str]:
        return {
            "node_id": ray.get_runtime_context().get_node_id(),
            "node_ip": ray.util.get_node_ip_address(),
            "actor_id": ray.get_runtime_context().get_actor_id() or "",
        }


@ray.remote(num_cpus=0.5)
class PlasmaProducer:
    """Actor that constructs and returns heavy objects placed into Plasma."""

    def produce_numpy(self, num_elements: int = 1_000_000) -> np.ndarray:
        return np.arange(num_elements, dtype=np.int64)

    def produce_pyarrow(self, num_rows: int = 50_000) -> pa.Table:
        return pa.Table.from_pydict(
            {
                "id": pa.array(range(num_rows)),
                "val": pa.array(np.linspace(0.0, 100.0, num=num_rows)),
                "tag": pa.array([f"kuberay_row_{i % 10}" for i in range(num_rows)]),
            }
        )


@ray.remote(num_cpus=0.5)
class PlasmaConsumer:
    """Actor that receives Plasma objects and verifies data integrity."""

    def verify_numpy(self, arr: np.ndarray, expected_len: int) -> tuple[float, int]:
        t0 = time.perf_counter()
        assert len(arr) == expected_len, f"Expected len {expected_len}, got {len(arr)}"
        assert arr[0] == 0, f"Expected first element 0, got {arr[0]}"
        assert arr[-1] == expected_len - 1, (
            f"Expected last element {expected_len - 1}, got {arr[-1]}"
        )
        elapsed = time.perf_counter() - t0
        return elapsed, arr.nbytes

    def verify_pyarrow(self, table: pa.Table, expected_rows: int) -> tuple[float, int]:
        t0 = time.perf_counter()
        assert len(table) == expected_rows, f"Expected {expected_rows} rows, got {len(table)}"
        assert table.column_names == ["id", "val", "tag"], (
            f"Unexpected columns: {table.column_names}"
        )
        assert table["id"][0].as_py() == 0
        assert table["id"][-1].as_py() == expected_rows - 1
        assert table["tag"][-1].as_py() == f"kuberay_row_{(expected_rows - 1) % 10}"
        elapsed = time.perf_counter() - t0
        return elapsed, table.nbytes


@ray.remote(num_cpus=0)
def run_plasma_transfer() -> dict[str, Any]:
    """Execute cross-node Plasma transfer test inside cluster context."""
    from ray.util.placement_group import placement_group, remove_placement_group
    from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

    pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="SPREAD")
    ready = ray.get(pg.ready(), timeout=30)
    assert ready is not None, "Placement group failed to reach READY state"

    try:
        producer = PlasmaProducer.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=0,
            )
        ).remote()

        consumer = PlasmaConsumer.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=1,
            )
        ).remote()

        # 1. NumPy transfer (1,000,000 int64 elements = 8 MB)
        np_ref = producer.produce_numpy.remote(num_elements=1_000_000)
        np_elapsed, np_bytes = ray.get(consumer.verify_numpy.remote(np_ref, expected_len=1_000_000))

        # 2. PyArrow Table transfer (50,000 rows)
        pa_ref = producer.produce_pyarrow.remote(num_rows=50_000)
        pa_elapsed, pa_bytes = ray.get(consumer.verify_pyarrow.remote(pa_ref, expected_rows=50_000))

        return {
            "numpy_bytes": np_bytes,
            "numpy_elapsed": np_elapsed,
            "pyarrow_bytes": pa_bytes,
            "pyarrow_elapsed": pa_elapsed,
        }
    finally:
        remove_placement_group(pg)


@ray.remote(num_cpus=0.5)
class DistributedSGDWorker:
    """Worker actor calculating local gradients for distributed training."""

    def compute_gradients(
        self, weights: np.ndarray, data_batch: np.ndarray, target_batch: np.ndarray
    ) -> np.ndarray:
        predictions = data_batch @ weights
        errors = predictions - target_batch
        gradients = (2.0 / len(data_batch)) * (data_batch.T @ errors)
        return gradients


def distributed_torch_train_loop() -> None:
    """Module-level distributed PyTorch training loop to ensure clean pickling."""
    import ray.train
    import ray.train.torch

    model = nn.Linear(1, 1)
    model = ray.train.torch.prepare_model(model)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    criterion = nn.MSELoss()

    x = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
    y = torch.tensor([[2.0], [4.0], [6.0], [8.0]])

    initial_loss = None
    final_loss = None

    for epoch in range(15):
        optimizer.zero_grad()
        pred = model(x)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()

        loss_val = float(loss.item())
        if epoch == 0:
            initial_loss = loss_val
        final_loss = loss_val

    assert initial_loss is not None
    assert final_loss is not None
    assert final_loss < initial_loss, (
        f"Model failed to converge: initial={initial_loss}, final={final_loss}"
    )
    ray.train.report({"loss": final_loss, "initial_loss": initial_loss})


@ray.remote(num_cpus=0)
def run_torch_train_multinode() -> dict[str, Any]:
    """Execute distributed multi-worker training with gradient synchronization."""
    from ray.util.placement_group import placement_group, remove_placement_group
    from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

    pg = placement_group([{"CPU": 0.5}, {"CPU": 0.5}], strategy="SPREAD")
    ready = ray.get(pg.ready(), timeout=30)
    assert ready is not None, "Placement group failed to reach READY state"

    try:
        w1 = DistributedSGDWorker.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=0,
            )
        ).remote()
        w2 = DistributedSGDWorker.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=1,
            )
        ).remote()

        # Synthetic dataset y = 2 * x + 1
        x1 = np.array([[1.0], [2.0]], dtype=np.float32)
        y1 = np.array([[3.0], [5.0]], dtype=np.float32)
        x2 = np.array([[3.0], [4.0]], dtype=np.float32)
        y2 = np.array([[7.0], [9.0]], dtype=np.float32)

        weights = np.array([[0.0]], dtype=np.float32)
        lr = 0.05
        initial_loss = float(
            np.mean((np.vstack([x1, x2]) @ weights - np.vstack([y1, y2])) ** 2)
        )

        for _ in range(25):
            g1_ref = w1.compute_gradients.remote(weights, x1, y1)
            g2_ref = w2.compute_gradients.remote(weights, x2, y2)
            g1, g2 = ray.get([g1_ref, g2_ref])
            avg_grad = (g1 + g2) / 2.0
            weights -= lr * avg_grad

        final_loss = float(np.mean((np.vstack([x1, x2]) @ weights - np.vstack([y1, y2])) ** 2))
        return {
            "backend": "ray_sgd",
            "metrics": {"loss": final_loss, "initial_loss": initial_loss},
            "error": None,
        }
    finally:
        remove_placement_group(pg)


@ray.remote(num_cpus=0)
def run_ray_data_multinode_pipeline() -> dict[str, Any]:
    """Execute streaming Ray Data pipeline within the cluster context."""
    import ray.data

    ds = ray.data.range(100)
    transformed_ds = ds.map(
        lambda row: {
            "id": row["id"],
            "square": row["id"] ** 2,
        }
    )
    results = transformed_ds.take_all()
    return {
        "count": len(results),
        "results": {row["id"]: row["square"] for row in results},
    }
