# I AM NOT DONE
"""Chapter 2: Distributed State & Actors - Exercise 6: Detached Named Actors.

Normally, an actor's lifecycle is bound to the driver job that created it.
When the creating process exits or its `ActorHandle` is garbage collected, the actor dies.

However, in many distributed architectures (e.g. centralized service registries, shared caches),
you need actors that can be discovered and accessed across different jobs or tasks by name.

Key Concepts:
1. Named Actors: Pass `name="my_actor"` (and optionally `lifetime="detached"`) to `options()`:
       `actor = GlobalRegistry.options(name="registry", lifetime="detached").remote()`
2. Retrieving by Name: Any task or process connected to the Ray cluster can retrieve the handle via:
       `registry = ray.get_actor("registry")`
3. Namespaces: Named actors can be isolated within namespaces using `namespace="my_app"`.

Your Task:
- Define a `@ray.remote` class `GlobalConfigRegistry` with methods:
  - `set(key: str, value: str) -> None`
  - `get(key: str) -> str | None`
- Instantiate it with `name="app_config_registry"`.
- Retrieve the actor handle using `ray.get_actor("app_config_registry")`.
- Store a config key `"cluster_env" -> "production"` and retrieve it via the retrieved handle.
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

    assert (
        retrieved_val == "production"
    ), f"Expected 'production', but got '{retrieved_val}'"
    print(f"✓ actors06 verified: Named actor registered and retrieved by name successfully ('{retrieved_val}')!")


if __name__ == "__main__":
    verify()
