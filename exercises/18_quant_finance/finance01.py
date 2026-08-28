"""
Exercise: exercises/18_quant_finance/finance01.py
Topic: Distributed Monte Carlo Black-Scholes Option Pricing

Context & Why:
Quantitative finance relies heavily on Monte Carlo simulations to price exotic derivatives.
Simulating millions of Geometric Brownian Motion (GBM) price paths across Ray worker tasks
achieves linear scaling and near-instant pricing.

Instructions:
1. Implement distributed Monte Carlo simulation across Ray tasks.
2. Aggregate discounted payoff estimates and verify pricing accuracy against analytical Black-Scholes.
"""

# I AM NOT DONE

import math
import os
import random

import ray

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"


@ray.remote
class MonteCarloPricingWorker:
    """Worker actor generating Geometric Brownian Motion paths and computing discounted payoffs."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)

    def price_european_call_batch(
        self,
        s0: float,
        strike: float,
        r: float,
        sigma: float,
        t: float,
        num_paths: int,
    ) -> tuple[float, int]:
        """Simulate asset price trajectories and compute discounted European call payoff sum.

        Returns:
            tuple[float, int]: (sum_of_discounted_payoffs, num_paths)
        """
        # TODO: Implement GBM path simulation and discounted payoff sum
        # drift = (r - 0.5 * sigma ** 2) * t
        # vol = sigma * math.sqrt(t)
        # discount = math.exp(-r * t)
        # payoff_sum = 0.0
        # for _ in range(num_paths):
        #     z = self.rng.gauss(0.0, 1.0)
        #     st = s0 * math.exp(drift + vol * z)
        #     payoff = max(st - strike, 0.0)
        #     payoff_sum += discount * payoff
        # return payoff_sum, num_paths
        return 0.0, 0


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    # Market Parameters
    s0 = 100.0  # Current stock price
    strike = 100.0  # Strike price (At-The-Money)
    r = 0.05  # 5% risk-free rate
    sigma = 0.20  # 20% annual volatility
    t = 1.0  # 1 year maturity
    total_paths = 20_000
    num_workers = 4
    paths_per_worker = total_paths // num_workers

    workers = [MonteCarloPricingWorker.remote(seed=100 + i) for i in range(num_workers)]
    futures = [
        w.price_european_call_batch.remote(s0, strike, r, sigma, t, paths_per_worker)
        for w in workers
    ]

    results = ray.get(futures)
    total_payoff_sum = sum(res[0] for res in results)
    total_simulated = sum(res[1] for res in results)

    assert total_simulated == total_paths, f"Expected {total_paths} paths, got {total_simulated}"
    option_price = total_payoff_sum / total_simulated

    # Black-Scholes analytical ATM call price is ~10.45
    print(f"Computed Monte Carlo Call Price: ${option_price:.4f}")
    assert 9.5 < option_price < 11.5, (
        f"Option price {option_price} out of expected bounds [9.5, 11.5]"
    )
    print("✓ finance01 verified: Distributed Monte Carlo Option Pricing succeeded!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
