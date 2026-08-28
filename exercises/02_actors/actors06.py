"""
Exercise: exercises/02_actors/actors06.py
Topic: Detached Named Actors for Cross-Job State

Context & Why:
Normally, an actor's lifecycle is bound to the driver job that created it. When the driver script exits
or the `ActorHandle` is garbage collected, Ray terminates the actor process.

For persistent infrastructure like shared caches, centralized model registries, or long-lived services,
Ray provides **Named Detached Actors**:
- `Actor.options(name="my_service", lifetime="detached").remote()` creates an actor that outlives the driver.
- Any subsequent client can look up the handle with `ray.get_actor("my_service")`.

Instructions:
1. Define `GlobalConfigRegistry` actor.
2. Instantiate it with `options(name="app_config_registry", lifetime="detached")`.
3. Retrieve the actor by name using `ray.get_actor("app_config_registry")` and verify values.
"""

import ray


# TODO: Define GlobalConfigRegistry actor
class GlobalConfigRegistry:
    def __init__(self) -> None:
        self.config: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.config[key] = value

    def get(self, key: str) -> str | None:
        return self.config.get(key)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # Clean up any existing actor with this name if re-running
    try:
        old_actor = ray.get_actor("app_config_registry")
        ray.kill(old_actor)
    except ValueError:
        pass

    # TODO: Instantiate GlobalConfigRegistry with name="app_config_registry"
    # registry = GlobalConfigRegistry.options(name="app_config_registry").remote()
    # registry.set.remote("cluster_env", "production")

    # TODO: Retrieve the actor from the cluster by name using ray.get_actor()
    # discovered_handle = ray.get_actor("app_config_registry")
    # retrieved_val = ray.get(discovered_handle.get.remote("cluster_env"))
    retrieved_val = None

    assert retrieved_val == "production", f"Expected 'production', but got '{retrieved_val}'"
    print(
        f"✓ actors06 verified: Named actor registered and retrieved by name successfully ('{retrieved_val}')!"
    )


if __name__ == "__main__":
    verify()
