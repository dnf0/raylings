"""
Exercise: exercises/04_scheduling_resources/scheduling06.py
Topic: Dynamic Runtime Environments (runtime_env)

Context & Why:
Different tasks or actors in the same cluster may require conflicting third-party packages, environment
variables, or local directory dependencies.

Ray `runtime_env` dynamically provisions isolated virtual environments, installs pip packages on the fly,
and syncs files to worker nodes before executing the task.

Instructions:
1. Configure `@ray.remote(runtime_env={"env_vars": {...}})`.
2. Verify that worker processes execute with the custom environment variables.
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
