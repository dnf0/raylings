"""
Exercise: exercises/14_kuberay/kuberay03.py
Topic: RayService CRD & Zero-Downtime Serving

Context & Why:
`RayService` CRD manages Ray Serve deployments on Kubernetes, providing rolling upgrades, health probes,
and zero-downtime traffic switching across cluster upgrades.

Instructions:
1. Author a `RayService` CRD spec.
2. Verify multi-deployment service definitions.
"""

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
