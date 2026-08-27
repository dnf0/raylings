"""Chapter 11: Ray Tune - Solution 3: Population-Based Training (PBT).

Reference Solution for tune03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.train
from ray import tune
from ray.tune.schedulers import PopulationBasedTraining


def pbt_trainable(config: dict) -> None:
    factor = config.get("factor", 1.0)
    for step in range(3):
        accuracy = factor * (step + 1.0)
        tune.report({"step": step, "accuracy": accuracy})


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    pbt = PopulationBasedTraining(
        metric="accuracy",
        mode="max",
        perturbation_interval=1,
        hyperparam_mutations={"factor": [2.0, 3.0]},
    )
    param_space = {"factor": tune.grid_search([1.0, 2.0])}
    tuner = tune.Tuner(
        pbt_trainable,
        param_space=param_space,
        tune_config=tune.TuneConfig(scheduler=pbt),
    )
    results = tuner.fit()

    assert results is not None, "Results must not be None"
    best = results.get_best_result(metric="accuracy", mode="max")
    assert best.metrics["accuracy"] >= 6.0, (
        f"Expected accuracy >= 6.0, got {best.metrics['accuracy']}"
    )
    print(
        f"✓ tune03 verified: Population-Based Training evolved top candidate with accuracy={best.metrics['accuracy']}!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
