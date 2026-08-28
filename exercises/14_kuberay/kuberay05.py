"""
Exercise: exercises/14_kuberay/kuberay05.py
Topic: Kubernetes Fault Tolerance & Pod Evictions

Context & Why:
In Kubernetes, worker pods can be evicted due to node drain, out-of-memory (OOMKilled), or spot preemption.
KubeRay coordinates with Ray's GCS to re-spawn replacement pods and reconstruct lost state.

Instructions:
1. Handle simulated pod eviction and verify cluster recovery.
"""

# I AM NOT DONE


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
