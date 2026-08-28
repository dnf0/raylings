"""
Exercise: exercises/06_cluster_architecture/cluster04.py
Topic: Cross-Node Object Transfers & Networking

Context & Why:
When a worker task on Node B accesses an `ObjectRef` created on Node A, Ray's object manager
automatically initiates an asynchronous point-to-point network transfer between Plasma stores.

Understanding cross-node transfer overhead is critical for designing latency-sensitive distributed algorithms.

Instructions:
1. Measure and observe cross-node object transfer dynamics.
"""

import time

import ray
from ray.job_submission import JobStatus, JobSubmissionClient


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Connect JobSubmissionClient to local dashboard
    # client = JobSubmissionClient("http://127.0.0.1:8265")

    # TODO: Submit job
    # job_id = client.submit_job(
    #     entrypoint='python -c "print(\'RAY_JOB_COMPLETE\')"',
    #     runtime_env={},
    # )

    # TODO: Wait for completion
    # final_status = None
    # start = time.time()
    # while time.time() - start < 30:
    #     final_status = client.get_job_status(job_id)
    #     if final_status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED}:
    #         break
    #     time.sleep(0.5)

    # TODO: Retrieve logs
    # logs = client.get_job_logs(job_id)
    final_status, logs = None, None

    assert final_status == JobStatus.SUCCEEDED, f"Expected JobStatus.SUCCEEDED, got {final_status}"
    assert logs is not None and "RAY_JOB_COMPLETE" in logs, (
        f"Expected 'RAY_JOB_COMPLETE' in logs, got {logs}"
    )
    print(f"✓ cluster04 verified: Job submitted, completed ({final_status}), and logs verified!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
