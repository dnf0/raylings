"""
Exercise: exercises/07_patterns_and_antipatterns/antipattern01.py
Topic: Nested ray.get() Bottlenecks & Driver Stalls

Context & Why:
A frequent performance hazard in distributed architectures is calling `ray.get()` inside a remote
task or worker function. When worker tasks synchronously block on other tasks with `ray.get()`,
they hold worker process slots hostage, leading to thread starvation, high latency, and deadlocks.

The recommended pattern is passing `ObjectRef`s directly to downstream tasks to form a pure DAG,
allowing Ray's C++ scheduler to orchestrate execution asynchronously without worker stalls.

Instructions:
1. Identify and eliminate the nested `ray.get()` call inside the remote worker.
2. Pass ObjectRefs directly to construct a streamlined execution DAG.
"""

# I AM NOT DONE

import ray


# TODO: Define stage1 remote task returning 42
def stage1() -> int:
    return 42


# TODO: Define stage2 remote task taking unwrapped int and returning val + 100
def stage2(val: int) -> int:
    return val + 100


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Pipeline stage1 into stage2 directly via ObjectRef
    # ref1 = stage1.remote()
    # ref2 = stage2.remote(ref1)
    # result = ray.get(ref2)
    result = None

    assert result == 142, f"Expected 142, got {result}"
    print(
        f"✓ antipattern01 verified: ObjectRef pipelined cleanly without blocking ray.get() inside tasks ({result})!"
    )


if __name__ == "__main__":
    verify()
