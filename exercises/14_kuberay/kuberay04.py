# I AM NOT DONE
"""Chapter 14: KubeRay - Exercise 4: Autoscaling with KEDA & Ray Autoscaler.

KubeRay integrates with the Ray native autoscaler to dynamically provision Kubernetes
pods as pending tasks and resource demands surge.

Key Concepts:
- `pending_resources`: Unsatisfied CPU/GPU/custom resource requests in Ray GCS.
- `calculate_desired_replicas`: Determines replica count to meet pending demand within [min, max].

Your Task:
- In `autoscaler_step(current_replicas: int, min_replicas: int, max_replicas: int, pending_cpus: int, cpus_per_worker: int) -> int`:
  - Calculate required worker pods: `ceil(pending_cpus / cpus_per_worker)`.
  - Clamp target replica count between `min_replicas` and `max_replicas`.
  - Return desired replicas.
- In `verify()`:
  - Test scale-up and scale-down calculations under various workloads.
"""

import math


def autoscaler_step(
    current_replicas: int,
    min_replicas: int,
    max_replicas: int,
    pending_cpus: int,
    cpus_per_worker: int,
) -> int:
    # TODO: Calculate desired replicas clamped to [min_replicas, max_replicas]
    pass


def verify() -> None:
    # Scale up on burst demand
    scale_up = autoscaler_step(
        current_replicas=2,
        min_replicas=1,
        max_replicas=10,
        pending_cpus=16,
        cpus_per_worker=4,
    )
    assert scale_up == 6, f"Expected 6 replicas (2 current + 4 needed), got {scale_up}"

    # Clamp to max_replicas
    clamped_max = autoscaler_step(
        current_replicas=2,
        min_replicas=1,
        max_replicas=5,
        pending_cpus=32,
        cpus_per_worker=4,
    )
    assert clamped_max == 5, f"Expected 5 (max clamped), got {clamped_max}"

    # Scale down on zero pending demand
    scale_down = autoscaler_step(
        current_replicas=5,
        min_replicas=2,
        max_replicas=10,
        pending_cpus=0,
        cpus_per_worker=4,
    )
    assert scale_down == 2, f"Expected scale down to min_replicas 2, got {scale_down}"

    print("✓ kuberay04 verified: KubeRay autoscaling policy calculations verified!")


if __name__ == "__main__":
    verify()
