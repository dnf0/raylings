"""
Exercise: exercises/12_ray_serve/serve03.py
Topic: Multi-Model Pipeline DAGs in Ray Serve

Context & Why:
Production AI applications rarely consist of a single model; they chain text preprocessing,
tokenization, multiple neural models, and postprocessing.
Ray Serve allows composing deployments into a Direct Acyclic Graph (DAG) with type-safe deployment handles.

Instructions:
1. Build a pipeline connecting an Ingestion deployment to an Inference deployment.
2. Route requests through the deployment graph.
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
