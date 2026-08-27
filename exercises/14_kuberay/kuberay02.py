"""Chapter 14: KubeRay - Exercise 2: RayJob CRD & Batch Job Lifecycle.

The `RayJob` CRD allows submitting non-interactive batch workloads (ETL, distributed training)
to an ephemeral or existing Ray cluster and automatically tearing it down when complete.

Key Concepts:
- `kind: RayJob`
- `spec.entrypoint`: CLI command to execute inside driver container.
- `spec.shutdownAfterJobFinishes: true`: Automatically garbage collects compute after job finishes.
- `spec.ttlSecondsAfterFinished`: Kubernetes TTL controller cleanup delay.

Your Task:
- In `build_ray_job_crd(name: str, entrypoint: str, ttl_seconds: int) -> dict`:
  - Build a valid `RayJob` CRD with `shutdownAfterJobFinishes=True` and `ttlSecondsAfterFinished`.
- In `verify()`:
  - Validate that the manifest includes entrypoint and TTL cleanup parameters.
"""

from typing import Any


def build_ray_job_crd(name: str, entrypoint: str, ttl_seconds: int) -> dict[str, Any]:
    # TODO: Build RayJob CRD dictionary
    pass


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
