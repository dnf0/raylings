"""Chapter 7: Production Patterns & Anti-Patterns - Exercise 1: Fixing ray.get() Inside Tasks.

Anti-Pattern: Calling `ray.get()` inside a task.
When a worker task calls `ray.get(upstream_ref)` synchronously, the worker process is blocked
waiting for the object, consuming CPU resources and worker slots without doing any actual work.
This can lead to cluster deadlocks if all worker processes block waiting on each other!

Correct Pattern:
Pass the `ObjectRef` directly into the downstream task!
Ray's scheduler automatically tracks data dependencies. The downstream task will only be scheduled
when the upstream `ObjectRef` is ready, and Ray will automatically resolve the argument into
its actual Python object value without blocking worker slots:

```python
# Bad:
@ray.remote
def bad_pipeline(ref):
    val = ray.get(ref)  # Anti-pattern: blocks worker slot!
    return val * 2

# Good:
@ray.remote
def good_pipeline(val: int) -> int:
    # Ray automatically unwraps the ObjectRef passed into 'val'!
    return val * 2

ref1 = stage1.remote()
ref2 = good_pipeline.remote(ref1)  # Passed as ObjectRef directly
```

Your Task:
- Define `@ray.remote` task `stage1() -> int` that returns 42.
- Define `@ray.remote` task `stage2(val: int) -> int` that receives the unwrapped integer value
  directly and returns `val + 100`.
- In `verify()`, chain `stage1` into `stage2` by passing `stage1.remote()` directly to `stage2.remote()`
  WITHOUT calling `ray.get()` inside any task.
- Retrieve the final value with a single `ray.get()` at the driver level.
"""

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
