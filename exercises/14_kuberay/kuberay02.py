"""
Exercise: exercises/14_kuberay/kuberay02.py
Topic: RayJob CRD & Ephemeral Batch Execution

Context & Why:
For batch ML workflows, maintaining static clusters is expensive.
The `RayJob` CRD creates an ephemeral Ray cluster, submits your job script, streams logs, and
automatically deletes the worker pods upon job completion.

Instructions:
1. Author a `RayJob` specification with shutdown policies.
2. Verify job lifecycle transitions.
"""

# I AM NOT DONE

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
