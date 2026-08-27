"""Chapter 6: Cluster Topology & Multi-Node Architecture - Solution 4: Ray Job Submission API.

Reference Solution for cluster04.
"""

import time

import ray
from ray.job_submission import JobStatus, JobSubmissionClient


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    client = JobSubmissionClient("http://127.0.0.1:8265")

    job_id = client.submit_job(
        entrypoint="python -c \"print('RAY_JOB_COMPLETE')\"",
        runtime_env={},
    )

    final_status = None
    start = time.time()
    while time.time() - start < 30:
        final_status = client.get_job_status(job_id)
        if final_status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED}:
            break
        time.sleep(0.5)

    logs = client.get_job_logs(job_id)

    assert final_status == JobStatus.SUCCEEDED, f"Expected JobStatus.SUCCEEDED, got {final_status}"
    assert logs is not None and "RAY_JOB_COMPLETE" in logs, (
        f"Expected 'RAY_JOB_COMPLETE' in logs, got {logs}"
    )
    print(f"✓ cluster04 verified: Job submitted, completed ({final_status}), and logs verified!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
