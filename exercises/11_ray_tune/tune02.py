# I AM NOT DONE
"""Chapter 11: Ray Tune - Exercise 2: ASHA / HyperBand Schedulers for Early Stopping.

Asynchronous Successive Halving Algorithm (ASHA) dynamically prunes underperforming
trials at intermediate milestones, saving 5x-10x compute compared to naive grid search.

Key Concepts:
- `ASHAScheduler(metric='loss', mode='min', max_t=10, grace_period=2, reduction_factor=2)`:
  Allows trials to run for `grace_period` steps before ranking and terminating bottom performers.
- `tune.TuneConfig(scheduler=asha, num_samples=6)`: Configures search scheduler.

Your Task:
- In `train_step(config: dict)`:
  - Simulate 5 training steps: for `step` in range(5), `loss = config["base_loss"] / (step + 1)`.
  - Report `{"step": step, "loss": loss}` on each step.
- In `verify()`:
  - Configure `ASHAScheduler(metric="loss", mode="min", max_t=5, grace_period=1)`.
  - Run `Tuner` with 4 trials exploring `base_loss` in `[1.0, 5.0, 10.0, 20.0]`.
  - Assert best result minimized loss (< 0.25).
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.train
from ray import tune
from ray.tune.schedulers import ASHAScheduler


def train_step(config: dict) -> None:
    # TODO: Simulate 5 training steps reporting loss
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Configure ASHAScheduler and run Tuner
    results = None

    assert results is not None, "Results must not be None"
    best = results.get_best_result(metric="loss", mode="min")
    assert best.metrics["loss"] < 0.25, f"Expected loss < 0.25, got {best.metrics['loss']}"
    print(
        f"✓ tune02 verified: ASHA scheduler discovered best configuration with loss={best.metrics['loss']:.4f}!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
