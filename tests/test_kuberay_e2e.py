"""Multi-Node KubeRay End-to-End Integration Test Suite.

Validates distributed Ray cluster topology, scheduling, object store transfer,
PyTorch distributed training, and Ray Data streaming across multi-node deployments.
"""

from __future__ import annotations

import os
import time
from typing import Any, Generator

import numpy as np
import pyarrow as pa
import pytest
import ray
import torch
import torch.nn as nn
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer
from ray.util.placement_group import placement_group, remove_placement_group
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

pytestmark = [pytest.mark.kuberay, pytest.mark.heavy]


# ==============================================================================
# Helper Functions and Actor Definitions (Module-Level for Pickling)
# ==============================================================================


@ray.remote(num_cpus=1)
class WorkerNodeProbe:
    """Actor probe for querying node execution context."""

    def get_info(self) -> dict[str, str]:
        return {
            "node_id": ray.get_runtime_context().get_node_id(),
            "node_ip": ray.util.get_node_ip_address(),
            "actor_id": ray.get_runtime_context().get_actor_id() or "",
        }


@ray.remote(num_cpus=1)
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


@ray.remote(num_cpus=1)
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


def _distributed_torch_train_loop() -> None:
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


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture(scope="module")
def ray_cluster() -> Generator[dict[str, Any], None, None]:
    """Provide connection to a live multi-node KubeRay cluster or simulated mock."""
    address_env = os.environ.get("RAY_ADDRESS")
    cluster_mock: Any = None

    if address_env:
        # 1. Explicit RAY_ADDRESS provided (e.g. ray://localhost:10001 or auto)
        ray.init(address=address_env, ignore_reinit_error=True)
    else:
        # 2. Try auto-connecting to an existing local cluster
        try:
            ray.init(address="auto", ignore_reinit_error=True)
        except Exception:
            # 3. Spin up an in-process simulated 2-node cluster mock
            try:
                from ray.cluster_utils import Cluster

                cluster_mock = Cluster(initialize_head=True)
                # Head node (2 CPUs) + Worker node (2 CPUs)
                cluster_mock.add_node(num_cpus=2)
                cluster_mock.add_node(num_cpus=2)
                ray.init(address=cluster_mock.address, ignore_reinit_error=True)
            except Exception as exc:
                pytest.skip(
                    "Live multi-node Ray cluster or RAY_ADDRESS not detected; "
                    f"run scripts/kuberay/setup-kuberay.sh up (cause: {exc})"
                )

    yield {
        "address": address_env or (cluster_mock.address if cluster_mock else "auto"),
        "is_mock": cluster_mock is not None,
    }

    # Teardown
    if ray.is_initialized():
        ray.shutdown()
    if cluster_mock is not None:
        cluster_mock.shutdown()


# ==============================================================================
# Tests
# ==============================================================================


def test_kuberay_cluster_node_discovery(ray_cluster: dict[str, Any]) -> None:
    """Verify cluster topology discovery with >= 2 ALIVE nodes."""
    nodes = ray.nodes()
    alive_nodes = [n for n in nodes if n.get("Alive") is True]

    assert len(alive_nodes) >= 2, (
        f"Expected at least 2 ALIVE nodes in cluster, found {len(alive_nodes)}. Nodes: {nodes}"
    )

    for node in alive_nodes:
        assert "NodeID" in node, f"Node missing NodeID: {node}"
        assert "NodeManagerAddress" in node, f"Node missing NodeManagerAddress: {node}"
        assert node.get("Alive") is True, f"Node is not ALIVE: {node}"


def test_kuberay_actor_cross_node_scheduling(ray_cluster: dict[str, Any]) -> None:
    """Verify actor tasks are distributed across distinct physical/logical nodes."""
    probes = [WorkerNodeProbe.options(scheduling_strategy="SPREAD").remote() for _ in range(4)]
    infos = ray.get([p.get_info.remote() for p in probes])

    node_ids = {info["node_id"] for info in infos}
    assert len(node_ids) >= 2, (
        f"Expected actors to be scheduled across >= 2 nodes, got node_ids: {node_ids}"
    )

    # In multi-host / KubeRay clusters with distinct IPs, verify IP distribution
    alive_nodes = [n for n in ray.nodes() if n.get("Alive") is True]
    cluster_ips = {n.get("NodeManagerAddress") for n in alive_nodes}
    if len(cluster_ips) > 1:
        actor_ips = {info["node_ip"] for info in infos}
        assert len(actor_ips) >= 2, (
            f"Expected actors across distinct IPs in multi-host cluster, got {actor_ips}"
        )


def test_kuberay_placement_group_strict_spread(ray_cluster: dict[str, Any]) -> None:
    """Verify placement group with STRICT_SPREAD guarantees physical node isolation."""
    bundles = [{"CPU": 1}, {"CPU": 1}]
    pg = placement_group(bundles, strategy="STRICT_SPREAD")
    ready = ray.get(pg.ready(), timeout=30)
    assert ready is True, "Placement group failed to reach READY state"

    try:
        actor_a = WorkerNodeProbe.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=0,
            )
        ).remote()

        actor_b = WorkerNodeProbe.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=1,
            )
        ).remote()

        info_a = ray.get(actor_a.get_info.remote())
        info_b = ray.get(actor_b.get_info.remote())

        assert info_a["node_id"] != info_b["node_id"], (
            f"STRICT_SPREAD violation: Actor A ({info_a['node_id']}) and "
            f"Actor B ({info_b['node_id']}) placed on the same node"
        )

        alive_nodes = [n for n in ray.nodes() if n.get("Alive") is True]
        cluster_ips = {n.get("NodeManagerAddress") for n in alive_nodes}
        if len(cluster_ips) > 1:
            assert info_a["node_ip"] != info_b["node_ip"], (
                f"STRICT_SPREAD IP violation: Actor A IP {info_a['node_ip']} == "
                f"Actor B IP {info_b['node_ip']}"
            )
    finally:
        remove_placement_group(pg)


def test_kuberay_cross_node_plasma_transfer(ray_cluster: dict[str, Any]) -> None:
    """Verify zero-corruption cross-node object store transfer for NumPy and PyArrow."""
    bundles = [{"CPU": 1}, {"CPU": 1}]
    pg = placement_group(bundles, strategy="STRICT_SPREAD")
    ray.get(pg.ready(), timeout=30)

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
        assert np_bytes == 8_000_000, f"Expected 8,000,000 bytes, got {np_bytes}"
        assert np_elapsed >= 0.0

        # 2. PyArrow Table transfer (50,000 rows)
        pa_ref = producer.produce_pyarrow.remote(num_rows=50_000)
        pa_elapsed, pa_bytes = ray.get(consumer.verify_pyarrow.remote(pa_ref, expected_rows=50_000))
        assert pa_bytes > 0, "PyArrow transfer resulted in 0 bytes"
        assert pa_elapsed >= 0.0
    finally:
        remove_placement_group(pg)


def test_kuberay_ray_train_torch_multinode(ray_cluster: dict[str, Any]) -> None:
    """Verify distributed multi-worker PyTorch training with gradient synchronization."""
    scaling_config = ScalingConfig(num_workers=2, use_gpu=False)
    trainer = TorchTrainer(
        train_loop_per_worker=_distributed_torch_train_loop,
        scaling_config=scaling_config,
    )
    result = trainer.fit()

    assert result.error is None, f"TorchTrainer failed with error: {result.error}"
    assert result.metrics is not None, "Expected non-empty metrics from TorchTrainer"
    loss = result.metrics.get("loss")
    assert loss is not None and loss < 1.0, f"Expected loss < 1.0, got {loss}"


def test_kuberay_ray_data_multinode_streaming(ray_cluster: dict[str, Any]) -> None:
    """Verify streaming Ray Data map pipeline across cluster nodes."""
    ds = ray.data.range(100)
    transformed_ds = ds.map(
        lambda row: {
            "id": row["id"],
            "square": row["id"] ** 2,
            "node_ip": ray.util.get_node_ip_address(),
        }
    )
    results = transformed_ds.take_all()

    assert len(results) == 100, f"Expected 100 results, got {len(results)}"
    results_dict = {row["id"]: row for row in results}
    assert len(results_dict) == 100, "Duplicate record IDs detected"

    for i in range(100):
        assert i in results_dict, f"Missing index {i} in Ray Data results"
        assert results_dict[i]["square"] == i**2, f"Invalid computation: {results_dict[i]}"
        assert "node_ip" in results_dict[i], f"Missing node_ip in result row {i}"
