"""
Exercise: exercises/06_cluster_architecture/cluster03.py
Topic: Ray Job Submission API

Context & Why:
In production, machine learning jobs are submitted to remote Ray clusters using the **Job Submission API**
(`ray.job_submission.JobSubmissionClient`).

This client allows submitting scripts, packaging dependencies via `runtime_env`, streaming remote logs,
and monitoring job status via REST over HTTP (port 8265).

Instructions:
1. Submit a job programmatically using `JobSubmissionClient`.
2. Poll job status until success and inspect execution logs.
"""

import ray
from ray.cluster_utils import Cluster


# TODO: Define compute_task remote task
def compute_task(x: int) -> int:
    return x + 100


def verify() -> None:
    cluster = Cluster()
    try:
        head = cluster.add_node(num_cpus=1)
        ray.init(address=cluster.address, ignore_reinit_error=True)
        worker = cluster.add_node(num_cpus=1)

        # TODO: Simulate worker node failure
        # cluster.remove_node(worker)

        # TODO: Run task on surviving node
        # result = ray.get(compute_task.remote(42))
        # alive_nodes = sum(1 for n in ray.nodes() if n["Alive"])
        result, alive_nodes = None, None

        assert result == 142, f"Expected result 142, got {result}"
        assert alive_nodes == 1, f"Expected 1 alive node after termination, got {alive_nodes}"
        print(
            f"✓ cluster03 verified: Node failure simulated and workload survived on head node (alive={alive_nodes})!"
        )
    finally:
        ray.shutdown()
        cluster.shutdown()


if __name__ == "__main__":
    verify()
