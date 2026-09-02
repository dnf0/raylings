"""
Exercise: exercises/12_ray_serve/serve01.py
Topic: Ray Serve HTTP Deployment & Ingress

Context & Why:
Ray Serve is a scalable model serving library built on Ray actors.
Decorating a class with `@serve.deployment` turns it into an autoscaling, HTTP-accessible microservice
with built-in request routing and load balancing.

Instructions:
1. Define a `@serve.deployment` class with `__call__(self, request)`.
2. Deploy the application with `serve.run()` and query via HTTP client.
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
    serve.start(http_options={"location": "NoServer"})

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
