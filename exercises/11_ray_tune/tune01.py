"""
Exercise: exercises/11_ray_tune/tune01.py
Topic: Ray Tune Search Spaces & Distributed Grid Search

Context & Why:
Hyperparameter tuning is embarrassingly parallel. Ray Tune manages distributed trials across cluster nodes.
Defining search spaces with `tune.choice()`, `tune.uniform()`, or `tune.loguniform()` allows exploring
hyperparameters with maximum concurrency.

Instructions:
1. Define a hyperparameter search space.
2. Run `Tuner.fit()` and inspect the best trial hyperparameters.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import tune


def trainable(config: dict) -> None:
    # TODO: Compute score based on abs(lr - 0.05) and report score
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Define param_space with grid_search and run Tuner
    # param_space = {
    #     "lr": tune.grid_search([0.01, 0.05, 0.1]),
    #     "batch_size": tune.choice([16, 32]),
    # }
    # tuner = tune.Tuner(trainable, param_space=param_space)
    # results = tuner.fit()
    results = None

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
