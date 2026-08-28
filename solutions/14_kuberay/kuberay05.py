"""Chapter 14: KubeRay - Solution 5: Kubernetes Fault Tolerance & Pod Evictions.

Reference Solution for kuberay05.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"


class SimulatedK8sCluster:
    def __init__(self, desired_replicas: int) -> None:
        self.desired_replicas = desired_replicas
        self.pods = [f"ray-worker-{i}" for i in range(desired_replicas)]
        self.evicted: list[str] = []
        self._next_id = desired_replicas

    def evict_pod(self, pod_name: str) -> None:
        if pod_name in self.pods:
            self.pods.remove(pod_name)
            self.evicted.append(pod_name)

    def reconcile(self) -> list[str]:
        spawned = []
        while len(self.pods) < self.desired_replicas:
            new_pod = f"ray-worker-{self._next_id}"
            self._next_id += 1
            self.pods.append(new_pod)
            spawned.append(new_pod)
        return spawned


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
