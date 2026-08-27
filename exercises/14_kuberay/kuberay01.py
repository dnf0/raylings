# I AM NOT DONE
"""Chapter 14: KubeRay - Exercise 1: RayCluster Custom Resource (CRD).

KubeRay manages declarative Ray clusters on Kubernetes using the `RayCluster` CRD.

Key Concepts:
- `apiVersion: ray.io/v1`, `kind: RayCluster`
- `spec.headGroupSpec`: Defines head node pod template, Ray start parameters, and ports.
- `spec.workerGroupSpecs`: Defines worker pod pools with `minReplicas`, `maxReplicas`, and resource limits.

Your Task:
- In `build_ray_cluster_crd(name: str, ray_version: str, min_workers: int, max_workers: int) -> dict`:
  - Construct a valid `RayCluster` CRD dictionary.
  - Configure `headGroupSpec` with rayStartParams `{"dashboard-host": "0.0.0.0"}`.
  - Configure `workerGroupSpecs` with `groupName: "default-worker"`, `minReplicas`, and `maxReplicas`.
- In `verify()`:
  - Generate the CRD and validate required KubeRay schema fields and replica bounds.
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
