# I AM NOT DONE
"""Chapter 6: Cluster Topology & Multi-Node Architecture - Exercise 4: Ray Job Submission API.

In production environments (like CI/CD pipelines, Kubernetes, or Airflow orchestrators),
you often submit Ray jobs remotely via HTTP instead of running interactive driver scripts.

Ray provides the `JobSubmissionClient` for this workflow:
1. Initialize Client: `client = JobSubmissionClient("http://127.0.0.1:8265")`
2. Submit Job:
   ```python
   job_id = client.submit_job(
       entrypoint="python task.py",
       runtime_env={"env_vars": {"RUN_ID": "job_42"}}
   )
   ```
3. Poll Status: `status = client.get_job_status(job_id)` (`JobStatus.SUCCEEDED`, `PENDING`, `RUNNING`).
4. Retrieve Logs: `logs = client.get_job_logs(job_id)`.

Your Task:
- In `verify()`:
  - Connect to the local Ray cluster Dashboard via `JobSubmissionClient("http://127.0.0.1:8265")`.
  - Submit a job with `entrypoint='python -c "print(\'RAY_JOB_COMPLETE\')"'` and `runtime_env={}`.
  - Poll the job until it reaches a terminal status (`JobStatus.SUCCEEDED` or `JobStatus.FAILED`).
  - Assert that the final status is `JobStatus.SUCCEEDED`.
  - Retrieve the job logs and assert that `"RAY_JOB_COMPLETE" in logs`.
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
