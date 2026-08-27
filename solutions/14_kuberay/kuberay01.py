"""Chapter 14: KubeRay - Solution 1: RayCluster Custom Resource (CRD).

Reference Solution for kuberay01.
"""

from typing import Any


def build_ray_cluster_crd(
    name: str, ray_version: str, min_workers: int, max_workers: int
) -> dict[str, Any]:
    return {
        "apiVersion": "ray.io/v1",
        "kind": "RayCluster",
        "metadata": {"name": name},
        "spec": {
            "rayVersion": ray_version,
            "headGroupSpec": {
                "rayStartParams": {"dashboard-host": "0.0.0.0"},
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "ray-head",
                                "image": f"rayproject/ray:{ray_version}",
                                "resources": {
                                    "limits": {"cpu": "2", "memory": "4Gi"},
                                    "requests": {"cpu": "2", "memory": "4Gi"},
                                },
                            }
                        ]
                    }
                },
            },
            "workerGroupSpecs": [
                {
                    "groupName": "default-worker",
                    "minReplicas": min_workers,
                    "maxReplicas": max_workers,
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "ray-worker",
                                    "image": f"rayproject/ray:{ray_version}",
                                    "resources": {
                                        "limits": {"cpu": "2", "memory": "4Gi"},
                                        "requests": {"cpu": "2", "memory": "4Gi"},
                                    },
                                }
                            ]
                        }
                    },
                }
            ],
        },
    }


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
