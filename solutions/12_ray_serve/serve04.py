"""Chapter 12: Ray Serve - Solution 4: Streaming Responses with FastApi & Generators.

Reference Solution for serve04.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
from typing import AsyncIterator

import ray
from ray import serve


@serve.deployment
class StreamingLLM:
    async def stream_tokens(self, words: list[str]) -> AsyncIterator[str]:
        for word in words:
            yield f"{word} "


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    handle = serve.run(StreamingLLM.bind())
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
