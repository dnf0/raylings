"""Chapter 14: KubeRay - Solution 2: RayJob CRD & Batch Job Lifecycle.

Reference Solution for kuberay02.
"""

from typing import Any


def build_ray_job_crd(name: str, entrypoint: str, ttl_seconds: int) -> dict[str, Any]:
    return {
        "apiVersion": "ray.io/v1",
        "kind": "RayJob",
        "metadata": {"name": name},
        "spec": {
            "entrypoint": entrypoint,
            "shutdownAfterJobFinishes": True,
            "ttlSecondsAfterFinished": ttl_seconds,
            "rayClusterSpec": {
                "rayVersion": "2.40.0",
                "headGroupSpec": {
                    "rayStartParams": {"dashboard-host": "0.0.0.0"},
                    "template": {
                        "spec": {
                            "containers": [{"name": "ray-head", "image": "rayproject/ray:2.40.0"}]
                        }
                    },
                },
                "workerGroupSpecs": [
                    {
                        "groupName": "small-worker",
                        "minReplicas": 1,
                        "maxReplicas": 4,
                        "template": {
                            "spec": {
                                "containers": [
                                    {"name": "ray-worker", "image": "rayproject/ray:2.40.0"}
                                ]
                            }
                        },
                    }
                ],
            },
        },
    }


def verify() -> None:
    crd = build_ray_job_crd(
        name="batch-etl-job",
        entrypoint="python /workspace/train.py --epochs 10",
        ttl_seconds=300,
    )

    assert crd is not None, "CRD must not be None"
    assert crd.get("kind") == "RayJob", f"Invalid kind: {crd.get('kind')}"
    assert crd["spec"]["entrypoint"] == "python /workspace/train.py --epochs 10"
    assert crd["spec"]["shutdownAfterJobFinishes"] is True
    assert crd["spec"]["ttlSecondsAfterFinished"] == 300

    print(f"✓ kuberay02 verified: RayJob CRD for '{crd['metadata']['name']}' verified!")


if __name__ == "__main__":
    verify()
