# I AM NOT DONE
"""Chapter 11: Ray Tune - Exercise 1: Search Spaces & Distributed Trials.

Ray Tune is an industry-standard library for distributed hyperparameter optimization.
It manages trial scheduling, resource allocation, and distributed evaluation across clusters.

Key Concepts:
- `tune.grid_search([...])` or `tune.choice([...])`: Defines categorical or discrete hyperparameter spaces.
- `ray.tune.report(metrics)`: Transmits trial metrics back to the Tune coordinator.
- `tune.Tuner(trainable, param_space=...)`: Configures and manages trial runs.
- `results.get_best_result(metric=..., mode=...)`: Finds the optimal trial outcome.

Your Task:
- In `trainable(config: dict)`:
  - Calculate `score = 1.0 / (1.0 + abs(config["lr"] - 0.05))`.
  - Report `{"score": score}` via `tune.report()`.
- In `verify()`:
  - Define `param_space = {"lr": tune.grid_search([0.01, 0.05, 0.1]), "batch_size": tune.choice([16, 32])}`.
  - Execute `tuner = tune.Tuner(trainable, param_space=param_space).fit()`.
  - Assert that the best result achieves `best_result.config["lr"] == 0.05`.
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
