"""
Exercise: exercises/11_ray_tune/tune03.py
Topic: Population-Based Training (PBT)

Context & Why:
**Population-Based Training (PBT)** dynamically explores hyperparameters while training a population
of neural networks simultaneously. Underperforming networks periodically replace their weights with
top-performing networks ('exploit') and mutate their hyperparameters ('explore').

Instructions:
1. Configure `PopulationBasedTraining` scheduler.
2. Verify parameter mutation during trial evolution.
"""

# I AM NOT DONE

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
from ray import tune
from ray.tune.schedulers import PopulationBasedTraining


def pbt_trainable(config: dict) -> None:
    # TODO: Report accuracy for 3 steps
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Configure PopulationBasedTraining
    # WHY: PBT optimizes dynamic schedules (e.g. learning rate schedules) by evolving models in real time. and Tuner
    results = None

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
