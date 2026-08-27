"""Chapter 12: Ray Serve - Solution 1: Ray Serve Deployments & Ingress.

Reference Solution for serve01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve


@serve.deployment(name="text_gen")
class TextGenerator:
    def __call__(self, prompt: str) -> str:
        return f"Generated: {prompt.upper()}"


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    handle = serve.run(TextGenerator.bind())
    assert handle is not None, "Serve handle must not be None"

    ref = handle.remote("raylings")
    result = ref.result()
    assert result == "Generated: RAYLINGS", f"Expected 'Generated: RAYLINGS', got {result}"
    print(f"✓ serve01 verified: Ray Serve deployment responded successfully: {result}!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
