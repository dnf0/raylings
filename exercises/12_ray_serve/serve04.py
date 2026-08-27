"""Chapter 12: Ray Serve - Exercise 4: Streaming Responses with FastApi & Generators.

Ray Serve natively supports token streaming (e.g. for LLMs) using async generators
and FastAPI integration.

Key Concepts:
- `async def generate(self, prompt: str)`: Async generator yielding token chunks.
- When querying via `DeploymentHandle`, iterating over `handle.remote()` streams tokens.

Your Task:
- In `StreamingLLM`:
  - Implement async generator `stream_tokens(self, words: list[str])` yielding each word with a trailing space.
- In `verify()`:
  - Query `handle.stream_tokens.remote(["Ray", "is", "fast"])`.
  - Collect streamed tokens into a single joined string and verify `"Ray is fast "`.
"""

# I AM NOT DONE
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
