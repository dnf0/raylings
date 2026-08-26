"""Chapter 4: Scheduling & Resources - Solution 6: Dynamic Runtime Environments.

Reference Solution for scheduling06.
"""

import os
import ray


@ray.remote
def read_env_var(key: str) -> str | None:
    return os.environ.get(key)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    env_config = {"env_vars": {"RAYLINGS_STAGE": "eval_v2", "MODEL_TIMEOUT": "30s"}}

    stage_ref = read_env_var.options(runtime_env=env_config).remote("RAYLINGS_STAGE")
    timeout_ref = read_env_var.options(runtime_env=env_config).remote("MODEL_TIMEOUT")
    stage_val, timeout_val = ray.get([stage_ref, timeout_ref])

    assert stage_val == "eval_v2", f"Expected 'eval_v2', got {stage_val}"
    assert timeout_val == "30s", f"Expected '30s', got {timeout_val}"
    print(
        f"✓ scheduling06 verified: Dynamic runtime_env injected successfully ({stage_val}, {timeout_val})!"
    )


if __name__ == "__main__":
    verify()
