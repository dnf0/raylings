"""Chapter 12: Ray Serve - Exercise 3: Composable Multi-Model Pipelines (DAGs).

Ray Serve allows composing deployments into computational graphs (DAGs), where one
deployment passes requests or handles to downstream model deployments.

Key Concepts:
- `Pipeline.bind(stage1_handle, stage2_handle)`: Connects deployment handles declaratively.
- Enables multi-stage pipelines: Preprocessing -> Embedding -> LLM / Classifier -> Postprocessing.

Your Task:
- In `Tokenizer`: Deployment returning `prompt.strip().lower()`.
- In `Classifier`: Deployment returning `{"label": "positive" if "good" in text else "neutral"}`.
- In `Pipeline`: Takes both handles and pipes tokenizer output into classifier.
- In `verify()`:
  - Deploy pipeline: `app = Pipeline.bind(Tokenizer.bind(), Classifier.bind())`.
  - Query with `"  VERY GOOD PRODUCT  "` and verify `{"label": "positive"}`.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import serve
from ray.serve.handle import DeploymentHandle


@serve.deployment
class Tokenizer:
    def __call__(self, text: str) -> str:
        # TODO: Return stripped, lowercase text
        pass


@serve.deployment
class Classifier:
    def __call__(self, clean_text: str) -> dict:
        # TODO: Return positive if 'good' in text else neutral
        pass


@serve.deployment
class Pipeline:
    def __init__(self, tokenizer: DeploymentHandle, classifier: DeploymentHandle) -> None:
        self.tokenizer = tokenizer
        self.classifier = classifier

    async def __call__(self, raw_text: str) -> dict:
        # TODO: Call tokenizer and pipe into classifier
        pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Build and run Pipeline.bind(Tokenizer.bind(), Classifier.bind())
    handle = None

    assert handle is not None, "Handle must not be None"
    ref = handle.remote("  VERY GOOD PRODUCT  ")
    result = ref.result()
    assert result == {"label": "positive"}, f"Expected positive label, got {result}"
    print(f"✓ serve03 verified: Composable DAG pipeline returned: {result}!")
    serve.shutdown()
    ray.shutdown()


if __name__ == "__main__":
    verify()
