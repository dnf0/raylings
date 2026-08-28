"""Chapter 14: KubeRay - Solution 3: RayService CRD & Zero-Downtime Serving.

Reference Solution for kuberay03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
from typing import Any


def build_ray_service_crd(
    name: str, app_name: str, route_prefix: str, import_path: str
) -> dict[str, Any]:
    return {
        "apiVersion": "ray.io/v1",
        "kind": "RayService",
        "metadata": {"name": name},
        "spec": {
            "serveConfigV2": {
                "applications": [
                    {
                        "name": app_name,
                        "route_prefix": route_prefix,
                        "import_path": import_path,
                    }
                ]
            },
            "rayClusterConfig": {
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
                        "groupName": "serve-worker",
                        "minReplicas": 1,
                        "maxReplicas": 5,
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
    crd = build_ray_service_crd(
        name="llm-service",
        app_name="chat-app",
        route_prefix="/chat",
        import_path="deployments.app:model",
    )

    assert crd is not None, "CRD must not be None"
    assert crd.get("kind") == "RayService", f"Invalid kind: {crd.get('kind')}"
    apps = crd["spec"]["serveConfigV2"]["applications"]
    assert len(apps) == 1
    assert apps[0]["name"] == "chat-app"
    assert apps[0]["route_prefix"] == "/chat"
    assert apps[0]["import_path"] == "deployments.app:model"

    print(
        f"✓ kuberay03 verified: RayService CRD configured with route '{apps[0]['route_prefix']}'!"
    )


if __name__ == "__main__":
    verify()
