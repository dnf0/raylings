"""
Exercise: exercises/14_kuberay/kuberay04.py
Topic: Autoscaling with KEDA & Ray Autoscaler

Context & Why:
Kubernetes Event-driven Autoscaling (KEDA) scales KubeRay worker pods based on queue depth, Prometheus metrics,
or Ray autoscaler demands, dynamically adapting Kubernetes capacity to real-time workload spikes.

Instructions:
1. Configure autoscaler scaling policies and min/max worker replicas.
"""

# I AM NOT DONE

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
