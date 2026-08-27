"""Tests for Ray session daemon and lifecycle manager."""

import ray

from raylings.daemon import RayDaemon


def test_daemon_full_lifecycle_and_introspection():
    """Verify RayDaemon start, status introspection, state reset, and shutdown."""
    if ray.is_initialized():
        ray.shutdown()

    daemon = RayDaemon(num_cpus=2, object_store_memory=100 * 1024 * 1024)

    try:
        # 1. Stopped state inspection
        assert not daemon.is_running()
        stopped_info = daemon.get_cluster_info()
        assert stopped_info["is_running"] is False
        assert stopped_info["address"] is None
        assert stopped_info["node_count"] == 0

        # 2. Start daemon
        started = daemon.start()
        assert started is True
        assert daemon.is_running() is True
        assert ray.is_initialized() is True

        # Idempotent start
        assert daemon.start() is True

        # 3. Active cluster info
        info = daemon.get_cluster_info()
        assert info["is_running"] is True
        assert info["address"] is not None
        assert info["node_count"] >= 1
        assert "CPU" in info["cluster_resources"]
        assert info["cluster_resources"]["CPU"] == 2.0

        # 4. State reset with live object
        obj_ref = ray.put({"key": "value"})
        assert ray.get(obj_ref) == {"key": "value"}
        daemon.reset_state()
        assert daemon.is_running()

        # 5. Shutdown and idempotency
        stopped = daemon.stop()
        assert stopped is True
        assert daemon.is_running() is False
        assert ray.is_initialized() is False
        assert daemon.stop() is True
    finally:
        if ray.is_initialized():
            ray.shutdown()
