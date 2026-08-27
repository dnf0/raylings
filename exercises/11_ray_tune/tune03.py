# I AM NOT DONE
"""Chapter 11: Ray Tune - Exercise 3: Population-Based Training (PBT).

Population-Based Training (PBT) combines parallel search with dynamic evolutionary
hyperparameter mutation. Top-performing agents pass their checkpoints and mutated
hyperparameters to underperforming agents during training.

Key Concepts:
- `PopulationBasedTraining`: Periodically exploits top models and explores hyperparameter mutations.
- Checkpoint persistence allows worker weights to be transferred across trials dynamically.

Your Task:
- In `pbt_trainable(config: dict)`:
  - Simulate training loop where `accuracy = config.get("factor", 1.0) * (step + 1)`.
  - Report accuracy on each of 3 steps.
- In `verify()`:
  - Configure `PopulationBasedTraining(metric="accuracy", mode="max", perturbation_interval=1)`.
  - Run `Tuner` across 2 trials and assert max accuracy is achieved.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import ray.train
from ray import tune
from ray.tune.schedulers import PopulationBasedTraining


def pbt_trainable(config: dict) -> None:
    # TODO: Report accuracy for 3 steps
    pass


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # TODO: Configure PopulationBasedTraining and Tuner
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
