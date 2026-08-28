"""
Exercise: exercises/14_kuberay/kuberay01.py
Topic: RayCluster Custom Resource Definition (CRD)

Context & Why:
The KubeRay Operator manages Ray clusters natively on Kubernetes.
The `RayCluster` CRD declaratively specifies head pod and worker group pod templates, CPU/memory limits,
GPU tolerations, and container images.

Instructions:
1. Author a valid `RayCluster` YAML spec.
2. Validate head and worker group configurations.
"""

from typing import Any


def build_ray_cluster_crd(
    name: str, ray_version: str, min_workers: int, max_workers: int
) -> dict[str, Any]:
    # TODO: Construct and return RayCluster CRD dictionary
    pass


def verify() -> None:
    crd = build_ray_cluster_crd(
        name="ray-ml-cluster",
        ray_version="2.40.0",
        min_workers=2,
        max_workers=8,
    )

    assert crd is not None, "CRD must not be None"
    assert crd.get("apiVersion") == "ray.io/v1", f"Invalid apiVersion: {crd.get('apiVersion')}"
    assert crd.get("kind") == "RayCluster", f"Invalid kind: {crd.get('kind')}"
    assert crd["metadata"]["name"] == "ray-ml-cluster"

    spec = crd["spec"]
    assert spec["rayVersion"] == "2.40.0"
    assert "headGroupSpec" in spec
    assert spec["headGroupSpec"]["rayStartParams"]["dashboard-host"] == "0.0.0.0"

    workers = spec["workerGroupSpecs"][0]
    assert workers["groupName"] == "default-worker"
    assert workers["minReplicas"] == 2
    assert workers["maxReplicas"] == 8

    print(
        f"✓ kuberay01 verified: RayCluster CRD for '{crd['metadata']['name']}' built and validated!"
    )


if __name__ == "__main__":
    verify()
