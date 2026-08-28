"""
Exercise: exercises/11_ray_tune/tune02.py
Topic: ASHA Early Stopping Trial Scheduler

Context & Why:
Training unpromising hyperparameter configurations to completion wastes massive compute resources.
The **Asynchronous Successive Halving Algorithm (ASHA)** aggressively terminates underperforming trials
early, reallocating compute to the top-performing configurations.

Instructions:
1. Configure `ASHAScheduler(metric="loss", mode="min", grace_period=1)`.
2. Verify early termination of poor trials.
"""

# I AM NOT DONE

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import tune
from ray.tune.schedulers import ASHAScheduler


def train_step(config: dict) -> None:
    # TODO: Simulate 5 training steps reporting loss
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Configure ASHAScheduler
    # WHY: ASHA scheduler prunes bottom-quartile trials early, saving over 70% of compute time. and run Tuner
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
