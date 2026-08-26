"""Ray session daemon and lifecycle manager for interactive exercise execution."""

import gc
import logging
from typing import Any

import ray

logger = logging.getLogger("raylings.daemon")


class RayDaemon:
    """Lifecycle manager for the background Python Ray session."""

    def __init__(
        self,
        num_cpus: int = 2,
        object_store_memory: int = 100 * 1024 * 1024,
    ) -> None:
        """Initialize RayDaemon with default cluster configuration parameters.

        Args:
            num_cpus: Default number of logical CPUs to allocate if starting a local cluster.
            object_store_memory: Default size in bytes for the Plasma object store (100MB default).
        """
        self.num_cpus = num_cpus
        self.object_store_memory = object_store_memory

    def is_running(self) -> bool:
        """Return True if Ray runtime is initialized and active."""
        return bool(ray.is_initialized())

    def start(
        self,
        num_cpus: int | None = None,
        object_store_memory: int | None = None,
    ) -> bool:
        """Start or connect to the local Ray cluster session.

        Args:
            num_cpus: Number of CPUs to allocate (overrides instance default if provided).
            object_store_memory: Object store memory in bytes (overrides instance default).

        Returns:
            bool: True if Ray is running and initialized.
        """
        cpus = num_cpus if num_cpus is not None else self.num_cpus
        mem = object_store_memory if object_store_memory is not None else self.object_store_memory

        if not ray.is_initialized():
            logger.info("Initializing Ray daemon with %d CPUs and %d bytes object store", cpus, mem)
            ray.init(
                ignore_reinit_error=True,
                num_cpus=cpus,
                object_store_memory=mem,
                include_dashboard=False,
                log_to_driver=False,
            )
        return self.is_running()

    def stop(self) -> bool:
        """Shut down the active Ray cluster session if running.

        Returns:
            bool: True if Ray is no longer running.
        """
        if ray.is_initialized():
            logger.info("Shutting down Ray daemon session")
            ray.shutdown()
        return not self.is_running()

    def reset_state(self) -> None:
        """Safely clean up runtime state and garbage collect between exercise runs."""
        if ray.is_initialized():
            gc.collect()

    def get_cluster_info(self) -> dict[str, Any]:
        """Return cluster metadata, address, node count, and resource statistics.

        Returns:
            dict containing cluster status, gcs address, node count, and resource maps.
        """
        if not self.is_running():
            return {
                "is_running": False,
                "address": None,
                "node_count": 0,
                "cluster_resources": {},
                "available_resources": {},
            }

        ctx = ray.get_runtime_context()
        return {
            "is_running": True,
            "address": getattr(ctx, "gcs_address", None),
            "node_count": len(ray.nodes()),
            "cluster_resources": ray.cluster_resources(),
            "available_resources": ray.available_resources(),
        }

    # Compatibility aliases
    def ensure_started(self) -> bool:
        """Ensure the daemon is running, starting it if necessary."""
        return self.start()

    def shutdown(self) -> bool:
        """Alias for stop()."""
        return self.stop()

    def cleanup_session(self) -> None:
        """Alias for reset_state()."""
        self.reset_state()
