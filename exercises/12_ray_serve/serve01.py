# I AM NOT DONE
"""Chapter 12: Ray Serve - Exercise 1: Ray Serve Deployments & Ingress.

Ray Serve is a scalable model serving framework built on Ray actors.
Deployments are stateful actor replicas exposed via HTTP or Python `DeploymentHandle`.

Key Concepts:
- `@serve.deployment`: Decorates Python class or function as a Serve deployment.
- `serve.run(Deployment.bind())`: Deploys the application locally or to a cluster.
- `handle = serve.run(...)` or `handle = deployment.bind()`: Provides async callable handle.

Your Task:
- In `TextGenerator`:
  - Decorate with `@serve.deployment(name="text_gen")`.
  - Implement `__call__(self, prompt: str) -> str` returning `f"Generated: {prompt.upper()}"`.
- In `verify()`:
  - Run the deployment: `handle = serve.run(TextGenerator.bind())`.
  - Send request via `handle.remote("raylings")`.
  - Assert response is `"Generated: RAYLINGS"`.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve


# TODO: Add @serve.deployment decorator and implement TextGenerator
class TextGenerator:
    def __call__(self, prompt: str) -> str:
        pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Deploy TextGenerator via serve.run and query handle
    handle = None

    assert handle is not None, "Serve handle must not be None"
    ref = handle.remote("raylings")
    result = ref.result()
    assert result == "Generated: RAYLINGS", f"Expected 'Generated: RAYLINGS', got {result}"
    print(f"✓ serve01 verified: Ray Serve deployment responded successfully: {result}!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
