"""Unit tests for the Ray cluster telemetry inspector and metrics dashboard (metrics.py and top/metrics commands)."""

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from raylings.cli import app
from raylings.metrics import (
    ActorMetrics,
    ClusterMetricsCollector,
    ClusterSnapshot,
    NodeMetrics,
    ObjectStoreMetrics,
    TaskMetrics,
    format_bytes,
    format_duration,
    render_metrics_dashboard,
    run_top_dashboard,
)

cli_runner = CliRunner()


def test_format_bytes() -> None:
    """Verify byte formatting helper formats various sizes accurately."""
    assert format_bytes(0) == "0 B"
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1536) == "1.5 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
    assert format_bytes(100 * 1024 * 1024) == "100.0 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    assert format_bytes(2.5 * 1024 * 1024 * 1024) == "2.5 GB"
    assert format_bytes(1024**4) == "1.0 TB"


def test_format_duration() -> None:
    """Verify duration formatting helper handles sub-minute, minutes, hours, and days."""
    assert format_duration(0) == "0s"
    assert format_duration(45) == "45s"
    assert format_duration(59.9) in ("60s", "59s")
    assert format_duration(60) == "1m 00s"
    assert format_duration(125) == "2m 05s"
    assert format_duration(3600) == "1h 00m 00s"
    assert format_duration(3665) == "1h 01m 05s"
    assert format_duration(86400 + 3665) == "1d 01h 01m 05s"


def test_data_models_serialization() -> None:
    """Verify data model initialization and dictionary/JSON serialization."""
    node = NodeMetrics(
        node_id="node-123456",
        node_ip="192.168.1.50",
        is_head_node=True,
        status="ALIVE",
        cpu_cores_total=8.0,
        cpu_cores_used=4.0,
        cpu_percent=50.0,
        ram_total_bytes=16 * 1024**3,
        ram_used_bytes=8 * 1024**3,
        ram_percent=50.0,
        object_store_total_bytes=2 * 1024**3,
        object_store_used_bytes=1 * 1024**3,
        object_store_percent=50.0,
        gpus_total=1.0,
        gpus_used=0.0,
    )
    node_dict = node.to_dict()
    assert node_dict["node_id"] == "node-123456"
    assert node_dict["is_head_node"] is True
    assert node_dict["cpu_percent"] == 50.0

    obj_store = ObjectStoreMetrics(
        total_bytes=100 * 1024 * 1024,
        used_bytes=25 * 1024 * 1024,
        free_bytes=75 * 1024 * 1024,
        usage_percent=25.0,
        active_objects=12,
        spilled_bytes=0,
        spilled_objects=0,
        restored_bytes=0,
    )
    obj_dict = obj_store.to_dict()
    assert obj_dict["total_bytes"] == 100 * 1024 * 1024
    assert obj_dict["usage_percent"] == 25.0
    assert obj_dict["active_objects"] == 12

    actor = ActorMetrics(
        actor_id="actor-999",
        name="WorkerActor",
        class_name="WorkerActor",
        state="ALIVE",
        pid=12345,
        node_ip="192.168.1.50",
        node_id="node-123456",
        restart_count=0,
        job_id="01000000",
    )
    actor_dict = actor.to_dict()
    assert actor_dict["actor_id"] == "actor-999"
    assert actor_dict["state"] == "ALIVE"

    tasks = TaskMetrics(
        total_tasks=10,
        pending_tasks=2,
        running_tasks=3,
        finished_tasks=5,
        failed_tasks=0,
    )
    task_dict = tasks.to_dict()
    assert task_dict["total_tasks"] == 10
    assert task_dict["running_tasks"] == 3

    snapshot = ClusterSnapshot(
        timestamp=1700000000.0,
        timestamp_iso="2023-11-14T22:13:20Z",
        is_active=True,
        ray_version="2.40.0",
        python_version="3.12.0",
        cluster_address="127.0.0.1:6379",
        dashboard_url="http://127.0.0.1:8265",
        uptime_seconds=3600.0,
        nodes=[node],
        object_store=obj_store,
        actors=[actor],
        tasks=tasks,
        total_cpus=8.0,
        used_cpus=4.0,
        total_gpus=1.0,
        used_gpus=0.0,
    )

    snap_dict = snapshot.to_dict()
    assert snap_dict["is_active"] is True
    assert snap_dict["nodes"][0]["node_ip"] == "192.168.1.50"
    assert snap_dict["actors"][0]["name"] == "WorkerActor"

    snap_json = snapshot.to_json()
    parsed = json.loads(snap_json)
    assert parsed["is_active"] is True
    assert parsed["ray_version"] == "2.40.0"
    assert len(parsed["nodes"]) == 1


def test_collector_inactive_cluster() -> None:
    """Verify collector returns inactive snapshot when Ray cluster is not running."""
    collector = ClusterMetricsCollector()

    with patch("ray.is_initialized", return_value=False):
        snapshot = collector.collect_snapshot()
        assert snapshot.is_active is False
        assert snapshot.cluster_address is None
        assert snapshot.nodes == []
        assert snapshot.actors == []
        assert snapshot.error is not None
        assert "inactive" in snapshot.error.lower() or "not running" in snapshot.error.lower()


def test_collector_active_cluster_mocked() -> None:
    """Verify collector queries Ray APIs and extracts nodes, object store, and actor statistics."""
    collector = ClusterMetricsCollector()

    mock_node = {
        "NodeID": "abcd1234efgh5678",
        "NodeManagerAddress": "127.0.0.1",
        "NodeManagerHostname": "localhost",
        "Alive": True,
        "Resources": {
            "CPU": 4.0,
            "memory": 16 * 1024**3,
            "object_store_memory": 2 * 1024**3,
            "GPU": 1.0,
        },
    }

    mock_runtime_context = MagicMock()
    mock_runtime_context.gcs_address = "127.0.0.1:6379"

    mock_actor = {
        "actor_id": "01000000ffffffff",
        "class_name": "StatefulWorker",
        "name": "my_worker",
        "state": "ALIVE",
        "pid": 54321,
        "node_ip_address": "127.0.0.1",
        "num_restarts": 1,
        "job_id": "01000000",
    }

    with (
        patch("ray.is_initialized", return_value=True),
        patch("ray.nodes", return_value=[mock_node]),
        patch(
            "ray.cluster_resources",
            return_value={
                "CPU": 4.0,
                "memory": 16 * 1024**3,
                "object_store_memory": 2 * 1024**3,
                "GPU": 1.0,
            },
        ),
        patch(
            "ray.available_resources",
            return_value={
                "CPU": 2.0,
                "memory": 10 * 1024**3,
                "object_store_memory": 1.5 * 1024**3,
                "GPU": 1.0,
            },
        ),
        patch("ray.get_runtime_context", return_value=mock_runtime_context),
        patch(
            "ray.util.state.list_actors",
            return_value=[mock_actor],
            create=True,
        ),
        patch(
            "ray.util.state.list_objects",
            return_value=[{"object_size": 1024, "data_size": 1024}],
            create=True,
        ),
    ):
        snapshot = collector.collect_snapshot()
        assert snapshot.is_active is True
        assert snapshot.error is None
        assert snapshot.total_cpus == 4.0
        assert snapshot.used_cpus == 2.0  # 4.0 - 2.0
        assert len(snapshot.nodes) == 1
        assert snapshot.nodes[0].node_ip == "127.0.0.1"
        assert snapshot.nodes[0].cpu_cores_total == 4.0
        assert snapshot.nodes[0].cpu_cores_used == 2.0
        assert snapshot.nodes[0].cpu_percent == 50.0
        assert snapshot.object_store.total_bytes == 2 * 1024**3
        assert snapshot.object_store.free_bytes == 1.5 * 1024**3
        assert snapshot.object_store.used_bytes == 0.5 * 1024**3
        assert snapshot.object_store.usage_percent == 25.0
        assert len(snapshot.actors) == 1
        assert snapshot.actors[0].name == "my_worker"
        assert snapshot.actors[0].class_name == "StatefulWorker"
        assert snapshot.actors[0].state == "ALIVE"
        assert snapshot.actors[0].restart_count == 1


def test_collector_gracefully_handles_state_api_errors() -> None:
    """Verify collector falls back cleanly if state API raises exceptions."""
    collector = ClusterMetricsCollector()

    mock_node = {
        "NodeID": "abcd1234efgh5678",
        "NodeManagerAddress": "127.0.0.1",
        "Alive": True,
        "Resources": {"CPU": 2.0, "memory": 8 * 1024**3, "object_store_memory": 100 * 1024 * 1024},
    }

    with (
        patch("ray.is_initialized", return_value=True),
        patch("ray.nodes", return_value=[mock_node]),
        patch(
            "ray.cluster_resources",
            return_value={"CPU": 2.0, "object_store_memory": 100 * 1024 * 1024},
        ),
        patch(
            "ray.available_resources",
            return_value={"CPU": 2.0, "object_store_memory": 100 * 1024 * 1024},
        ),
        patch("ray.get_runtime_context", return_value=MagicMock(gcs_address="127.0.0.1:6379")),
        patch.object(
            collector, "_query_actors", side_effect=Exception("State API connection failed")
        ),
        patch.object(collector, "_query_objects", side_effect=Exception("Object query failed")),
        patch.object(collector, "_query_tasks", side_effect=Exception("Task query failed")),
    ):
        snapshot = collector.collect_snapshot()
        assert snapshot.is_active is True
        assert len(snapshot.nodes) == 1
        assert snapshot.actors == []
        assert snapshot.tasks.total_tasks == 0
        assert snapshot.error is None


def test_render_metrics_dashboard_inactive() -> None:
    """Verify render_metrics_dashboard handles inactive cluster snapshot."""
    snapshot = ClusterSnapshot(
        timestamp=1700000000.0,
        timestamp_iso="2023-11-14T22:13:20Z",
        is_active=False,
        ray_version="2.40.0",
        python_version="3.12.0",
        error="Ray cluster daemon is offline.",
    )

    rendered = render_metrics_dashboard(snapshot)
    assert rendered is not None


def test_render_metrics_dashboard_active() -> None:
    """Verify render_metrics_dashboard renders nodes, object store, and actors layout."""
    node = NodeMetrics(
        node_id="node-test",
        node_ip="127.0.0.1",
        is_head_node=True,
        status="ALIVE",
        cpu_cores_total=4.0,
        cpu_cores_used=2.0,
        cpu_percent=50.0,
        ram_total_bytes=16 * 1024**3,
        ram_used_bytes=8 * 1024**3,
        ram_percent=50.0,
        object_store_total_bytes=2 * 1024**3,
        object_store_used_bytes=500 * 1024**2,
        object_store_percent=24.4,
    )
    obj_store = ObjectStoreMetrics(
        total_bytes=2 * 1024**3,
        used_bytes=500 * 1024**2,
        free_bytes=1500 * 1024**2,
        usage_percent=24.4,
        active_objects=5,
        spilled_bytes=0,
        spilled_objects=0,
        restored_bytes=0,
    )
    actor = ActorMetrics(
        actor_id="actor-test",
        name="TrainerActor",
        class_name="TrainerActor",
        state="ALIVE",
        pid=1234,
        node_ip="127.0.0.1",
        node_id="node-test",
    )
    snapshot = ClusterSnapshot(
        timestamp=1700000000.0,
        timestamp_iso="2023-11-14T22:13:20Z",
        is_active=True,
        ray_version="2.40.0",
        python_version="3.12.0",
        cluster_address="127.0.0.1:6379",
        nodes=[node],
        object_store=obj_store,
        actors=[actor],
        total_cpus=4.0,
        used_cpus=2.0,
    )

    rendered = render_metrics_dashboard(snapshot)
    assert rendered is not None


def test_run_top_dashboard_once_and_json(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify run_top_dashboard in once and JSON mode."""
    mock_collector = MagicMock()
    mock_snapshot = ClusterSnapshot(
        timestamp=1700000000.0,
        timestamp_iso="2023-11-14T22:13:20Z",
        is_active=True,
        ray_version="2.40.0",
        python_version="3.12.0",
        cluster_address="127.0.0.1:6379",
    )
    mock_collector.collect_snapshot.return_value = mock_snapshot

    # Test once mode
    run_top_dashboard(once=True, collector=mock_collector)
    mock_collector.collect_snapshot.assert_called_once()
    capsys.readouterr()  # Clear capsys buffer

    # Test JSON mode
    mock_collector.reset_mock()
    run_top_dashboard(as_json=True, collector=mock_collector)
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["is_active"] is True
    assert payload["ray_version"] == "2.40.0"


def test_cli_top_command_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 'raylings top --once' executes single snapshot render."""
    mock_run = MagicMock()
    monkeypatch.setattr("raylings.metrics.run_top_dashboard", mock_run)

    res = cli_runner.invoke(app, ["top", "--once"])
    assert res.exit_code == 0
    mock_run.assert_called_once_with(interval=1.0, once=True, as_json=False)


def test_cli_top_command_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 'raylings top --json' calls run_top_dashboard with as_json=True."""
    mock_run = MagicMock()
    monkeypatch.setattr("raylings.metrics.run_top_dashboard", mock_run)

    res = cli_runner.invoke(app, ["top", "--json"])
    assert res.exit_code == 0
    mock_run.assert_called_once_with(interval=1.0, once=False, as_json=True)


def test_cli_top_command_interval(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 'raylings top --interval 2.5 --once' parses custom interval."""
    mock_run = MagicMock()
    monkeypatch.setattr("raylings.metrics.run_top_dashboard", mock_run)

    res = cli_runner.invoke(app, ["top", "-i", "2.5", "--once"])
    assert res.exit_code == 0
    mock_run.assert_called_once_with(interval=2.5, once=True, as_json=False)


def test_cli_metrics_command_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 'raylings metrics' command functions as alias to top/metrics dashboard."""
    mock_run = MagicMock()
    monkeypatch.setattr("raylings.metrics.run_top_dashboard", mock_run)

    res = cli_runner.invoke(app, ["metrics", "--once"])
    assert res.exit_code == 0
    mock_run.assert_called_once_with(interval=1.0, once=True, as_json=False)
