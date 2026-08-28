"""
Exercise: exercises/12_ray_serve/serve04.py
Topic: Autoscaling & Replica Dynamics in Ray Serve

Context & Why:
Traffic spikes require rapid horizontal scaling of model replicas.
`autoscaling_config={"min_replicas": 1, "max_replicas": 5, "target_ongoing_requests": 2}`
instructs Ray Serve controller to monitor queue depth and scale replica actors automatically.

Instructions:
1. Configure `autoscaling_config` on a deployment.
2. Verify dynamic replica scaling under simulated request load.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
from typing import AsyncIterator

import ray
from ray import serve


@serve.deployment
class StreamingLLM:
    # TODO: Implement async generator stream_tokens
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Deploy StreamingLLM and consume stream
    handle = None

    assert handle is not None, "Handle must not be None"
    gen = handle.options(stream=True).stream_tokens.remote(["Ray", "is", "fast"])
    collected = []
    for chunk in gen:
        collected.append(chunk)

    full_text = "".join(collected)
    assert full_text == "Ray is fast ", f"Expected 'Ray is fast ', got '{full_text}'"
    print(f"✓ serve04 verified: Successfully streamed tokens in real time: '{full_text}'!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
