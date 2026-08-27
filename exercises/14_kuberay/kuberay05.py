# I AM NOT DONE
"""Chapter 14: KubeRay - Exercise 5: Kubernetes Fault Tolerance & Pod Evictions.

In Kubernetes environments (especially on Spot / Preemptible instances), worker pods
can be evicted at any time. KubeRay and Ray combine to detect lost nodes and re-schedule actors.

Key Concepts:
- Pod eviction triggers Ray GCS node dead event.
- Tasks with `max_retries > 0` and actors with `max_restarts > 0` are automatically rescheduled.

Your Task:
- In `SimulatedK8sCluster`:
  - Maintain active pods `self.pods: list[str]`.
  - Implement `evict_pod(pod_name: str)`: Removes pod from `self.pods` and adds to `self.evicted`.
  - Implement `reconcile()`: If `len(self.pods) < self.desired_replicas`, spawns replacement pods.
- In `verify()`:
  - Evict a pod, run reconcile(), and assert replacement pod was provisioned.
"""


class SimulatedK8sCluster:
    def __init__(self, desired_replicas: int) -> None:
        self.desired_replicas = desired_replicas
        self.pods = [f"ray-worker-{i}" for i in range(desired_replicas)]
        self.evicted: list[str] = []

    def evict_pod(self, pod_name: str) -> None:
        # TODO: Remove pod from pods and record in evicted
        pass

    def reconcile(self) -> list[str]:
        # TODO: Spawn replacement pods if len(pods) < desired_replicas and return new pod names
        pass


def verify() -> None:
    cluster = SimulatedK8sCluster(desired_replicas=3)
    assert len(cluster.pods) == 3

    # Simulate Kubernetes Spot eviction
    cluster.evict_pod("ray-worker-1")
    assert len(cluster.pods) == 2
    assert "ray-worker-1" in cluster.evicted

    # KubeRay controller reconciles state
    new_pods = cluster.reconcile()
    assert len(cluster.pods) == 3, f"Expected 3 pods after reconcile, got {len(cluster.pods)}"
    assert len(new_pods) == 1
    print(
        f"✓ kuberay05 verified: KubeRay controller reconciled eviction and spawned {new_pods[0]}!"
    )


if __name__ == "__main__":
    verify()
