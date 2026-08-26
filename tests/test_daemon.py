"""Tests for Ray session daemon and lifecycle manager."""

import pytest
import ray

from raylings.daemon import RayDaemon


@pytest.fixture(autouse=True)
def cleanup_ray():
    """Ensure Ray is shut down before and after each test."""
    if ray.is_initialized():
        ray.shutdown()
    yield
    if ray.is_initialized():
        ray.shutdown()


def test_daemon_start_and_is_running():
    daemon = RayDaemon(num_cpus=2, object_store_memory=100 * 1024 * 1024)
    assert not daemon.is_running()

    started = daemon.start()
    assert started is True
    assert daemon.is_running() is True
    assert ray.is_initialized() is True

    # Test idempotency of start
    restarted = daemon.start()
    assert restarted is True
    assert daemon.is_running() is True


def test_daemon_get_cluster_info():
    daemon = RayDaemon(num_cpus=2, object_store_memory=100 * 1024 * 1024)

    # Info before start
    stopped_info = daemon.get_cluster_info()
    assert stopped_info["is_running"] is False
    assert stopped_info["address"] is None
    assert stopped_info["node_count"] == 0
    assert stopped_info["cluster_resources"] == {}
    assert stopped_info["available_resources"] == {}

    # Info after start
    daemon.start()
    info = daemon.get_cluster_info()
    assert info["is_running"] is True
    assert info["address"] is not None
    assert info["node_count"] >= 1
    assert "CPU" in info["cluster_resources"]
    assert info["cluster_resources"]["CPU"] == 2.0
    assert "object_store_memory" in info["cluster_resources"]
    assert "available_resources" in info


def test_daemon_reset_state():
    daemon = RayDaemon(num_cpus=2, object_store_memory=100 * 1024 * 1024)
    daemon.start()
    assert daemon.is_running()

    # Create an object in object store
    obj_ref = ray.put({"key": "value"})
    assert ray.get(obj_ref) == {"key": "value"}

    # Reset state should succeed without error
    daemon.reset_state()
    assert daemon.is_running()

    # Reset state when stopped should also succeed safely
    daemon.stop()
    assert not daemon.is_running()
    daemon.reset_state()
    assert not daemon.is_running()


def test_daemon_stop():
    daemon = RayDaemon(num_cpus=2, object_store_memory=100 * 1024 * 1024)
    daemon.start()
    assert daemon.is_running() is True
    assert ray.is_initialized() is True

    stopped = daemon.stop()
    assert stopped is True
    assert daemon.is_running() is False
    assert ray.is_initialized() is False

    # Stopping again is safe and idempotent
    stopped_again = daemon.stop()
    assert stopped_again is True
    assert daemon.is_running() is False
