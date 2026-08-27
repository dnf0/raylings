"""Chapter 11: Ray Tune - Solution 1: Search Spaces & Distributed Trials.

Reference Solution for tune01.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import tune


def trainable(config: dict) -> None:
    score = 1.0 / (1.0 + abs(config["lr"] - 0.05))
    tune.report({"score": score})


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    param_space = {
        "lr": tune.grid_search([0.01, 0.05, 0.1]),
        "batch_size": tune.choice([16, 32]),
    }
    tuner = tune.Tuner(trainable, param_space=param_space)
    results = tuner.fit()

    assert results is not None, "Tuner results must not be None"
    best_result = results.get_best_result(metric="score", mode="max")
    assert best_result.config["lr"] == 0.05, (
        f"Expected best lr 0.05, got {best_result.config['lr']}"
    )
    print(
        f"✓ tune01 verified: Found optimal hyperparameter config lr={best_result.config['lr']} with score={best_result.metrics['score']:.4f}!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
