"""Chapter 2: Distributed State & Actors - Solution 6: Detached Named Actors.

Reference Solution for actors06.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
class GlobalConfigRegistry:
    def __init__(self) -> None:
        self.config: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.config[key] = value

    def get(self, key: str) -> str | None:
        return self.config.get(key)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    try:
        old_actor = ray.get_actor("app_config_registry")
        ray.kill(old_actor)
    except ValueError:
        pass

    registry = GlobalConfigRegistry.options(name="app_config_registry").remote()
    registry.set.remote("cluster_env", "production")

    discovered_handle = ray.get_actor("app_config_registry")
    retrieved_val = ray.get(discovered_handle.get.remote("cluster_env"))

    assert retrieved_val == "production", f"Expected 'production', but got '{retrieved_val}'"
    print(
        f"✓ actors06 verified: Named actor registered and retrieved by name successfully ('{retrieved_val}')!"
    )


if __name__ == "__main__":
    verify()
