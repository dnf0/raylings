# I AM NOT DONE
"""Chapter 4: Scheduling & Resources - Exercise 6: Dynamic Runtime Environments.

In production clusters, different jobs or even different tasks within the same job may require
different environment variables, dependencies, or configuration without restarting the cluster.

Ray's `runtime_env` API provides per-task / per-actor environment isolation:
- `env_vars`: Dictionary of environment variables to inject into worker processes.
- `pip`: List of python packages or requirements file.
- `py_modules` / `working_dir`: Code directories packaged and sent to workers.

Example:
    @ray.remote
    def read_config():
        return os.environ.get("ENVIRONMENT_MODE")

    ref = read_config.options(
        runtime_env={"env_vars": {"ENVIRONMENT_MODE": "production"}}
    ).remote()

Your Task:
- Define a `@ray.remote` function `read_env_var(key: str) -> str | None` that returns
  `os.environ.get(key)`.
- In `verify()`, schedule `read_env_var` with a `runtime_env` that sets `"RAYLINGS_STAGE": "eval_v2"`
  and `"MODEL_TIMEOUT": "30s"`.
- Verify the task returns `"eval_v2"` for `"RAYLINGS_STAGE"` and `"30s"` for `"MODEL_TIMEOUT"`.
"""

import os

import ray


# TODO: Define read_env_var remote task
def read_env_var(key: str) -> str | None:
    return None


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Define runtime_env with env_vars
    # env_config = {"env_vars": {"RAYLINGS_STAGE": "eval_v2", "MODEL_TIMEOUT": "30s"}}

    # TODO: Execute read_env_var tasks with runtime_env option
    # stage_ref = read_env_var.options(runtime_env=env_config).remote("RAYLINGS_STAGE")
    # timeout_ref = read_env_var.options(runtime_env=env_config).remote("MODEL_TIMEOUT")
    # stage_val, timeout_val = ray.get([stage_ref, timeout_ref])
    stage_val, timeout_val = None, None

    assert stage_val == "eval_v2", f"Expected 'eval_v2', got {stage_val}"
    assert timeout_val == "30s", f"Expected '30s', got {timeout_val}"
    print(
        f"✓ scheduling06 verified: Dynamic runtime_env injected successfully ({stage_val}, {timeout_val})!"
    )


if __name__ == "__main__":
    verify()
