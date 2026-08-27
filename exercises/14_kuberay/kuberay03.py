"""Chapter 14: KubeRay - Exercise 3: RayService CRD & Zero-Downtime Serving.

The `RayService` CRD manages production Ray Serve deployments on Kubernetes, providing
automated zero-downtime rolling upgrades and Kubernetes Service ingress.

Key Concepts:
- `kind: RayService`
- `spec.serveConfigV2`: Multi-application Serve configuration YAML or dictionary.
- `spec.upgradeStrategy`: Rollout policy (e.g. `Rollout`, `None`).

Your Task:
- In `build_ray_service_crd(name: str, app_name: str, route_prefix: str, import_path: str) -> dict`:
  - Construct a `RayService` CRD specifying `serveConfigV2` with applications list.
- In `verify()`:
  - Assert that application route prefix and deployment import path are valid.
"""

# I AM NOT DONE
from typing import Any


def build_ray_service_crd(
    name: str, app_name: str, route_prefix: str, import_path: str
) -> dict[str, Any]:
    # TODO: Build RayService CRD
    pass


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
