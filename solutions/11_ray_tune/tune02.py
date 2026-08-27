"""Chapter 11: Ray Tune - Solution 2: ASHA / HyperBand Schedulers for Early Stopping.

Reference Solution for tune02.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.train
from ray import tune
from ray.tune.schedulers import ASHAScheduler


def train_step(config: dict) -> None:
    for step in range(5):
        loss = config["base_loss"] / (step + 1.0)
        tune.report({"step": step, "loss": loss})


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    scheduler = ASHAScheduler(metric="loss", mode="min", max_t=5, grace_period=1)
    param_space = {"base_loss": tune.grid_search([1.0, 5.0, 10.0, 20.0])}
    tuner = tune.Tuner(
        train_step,
        param_space=param_space,
        tune_config=tune.TuneConfig(scheduler=scheduler),
    )
    results = tuner.fit()

    assert results is not None, "Results must not be None"
    best = results.get_best_result(metric="loss", mode="min")
    assert best.metrics["loss"] < 0.25, f"Expected loss < 0.25, got {best.metrics['loss']}"
    print(
        f"✓ tune02 verified: ASHA scheduler discovered best configuration with loss={best.metrics['loss']:.4f}!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
