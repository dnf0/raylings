"""Chapter 12: Ray Serve - Solution 3: Composable Multi-Model Pipelines (DAGs).

Reference Solution for serve03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve
from ray.serve.handle import DeploymentHandle


@serve.deployment
class Tokenizer:
    def __call__(self, text: str) -> str:
        return text.strip().lower()


@serve.deployment
class Classifier:
    def __call__(self, clean_text: str) -> dict:
        return {"label": "positive" if "good" in clean_text else "neutral"}


@serve.deployment
class Pipeline:
    def __init__(self, tokenizer: DeploymentHandle, classifier: DeploymentHandle) -> None:
        self.tokenizer = tokenizer
        self.classifier = classifier

    async def __call__(self, raw_text: str) -> dict:
        clean = await self.tokenizer.remote(raw_text)
        return await self.classifier.remote(clean)


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    app = Pipeline.bind(Tokenizer.bind(), Classifier.bind())
    handle = serve.run(app)
    assert handle is not None, "Handle must not be None"

    ref = handle.remote("  VERY GOOD PRODUCT  ")
    result = ref.result()
    assert result == {"label": "positive"}, f"Expected positive label, got {result}"
    print(f"✓ serve03 verified: Composable DAG pipeline returned: {result}!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
