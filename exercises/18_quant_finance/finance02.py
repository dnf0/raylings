"""Chapter 18: Distributed Quantitative Finance - Exercise 2: Distributed Portfolio Value-at-Risk (VaR).

Value-at-Risk (VaR) measures the maximum potential loss on an investment portfolio
over a defined time horizon at a given confidence level (e.g., 99%).
Expected Shortfall (CVaR) computes the average loss given that the loss exceeds the VaR threshold.

Key Concepts:
1. Covariance Sharding: Sharding multi-asset correlated return simulations across Ray actors.
2. Distributed Loss Aggregation: Merging simulated portfolio P&L vectors in parallel.
3. Percentile & Tail Loss Extraction: Computing 99% VaR and 99% CVaR.

Your Task:
- Implement `PortfolioRiskWorker.simulate_portfolio_returns` to simulate `n_scenarios` P&L values.
- Calculate 99% Value-at-Risk and Expected Shortfall from the combined simulations.
"""

import math
import os
import random

import ray

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"


@ray.remote
class PortfolioRiskWorker:
    """Simulates correlated asset movements and computes portfolio P&L realizations."""

    def __init__(self, seed: int = 123) -> None:
        self.rng = random.Random(seed)

    def simulate_portfolio_returns(
        self,
        weights: list[float],
        volatilities: list[float],
        portfolio_value: float,
        n_scenarios: int,
    ) -> list[float]:
        """Simulate P&L distribution for a weighted multi-asset portfolio.

        Returns:
            list[float]: Simulated dollar P&L outcomes (negative indicates loss).
        """
        # TODO: Implement multi-asset return simulation
        # pnl_outcomes: list[float] = []
        # num_assets = len(weights)
        # for _ in range(n_scenarios):
        #     # Common market factor + idiosyncratic asset noise
        #     market_z = self.rng.gauss(0.0, 1.0)
        #     scenario_pnl = 0.0
        #     for i in range(num_assets):
        #         idio_z = self.rng.gauss(0.0, 1.0)
        #         combined_z = 0.7 * market_z + math.sqrt(1 - 0.7**2) * idio_z
        #         asset_return = volatilities[i] * combined_z
        #         asset_pnl = portfolio_value * weights[i] * asset_return
        #         scenario_pnl += asset_pnl
        #     pnl_outcomes.append(scenario_pnl)
        # return pnl_outcomes
        return []


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    portfolio_value = 10_000_000.0  # $10M Portfolio
    weights = [0.4, 0.3, 0.2, 0.1]  # 4 assets
    volatilities = [0.015, 0.020, 0.025, 0.035]  # Daily volatilities

    total_scenarios = 40_000
    num_workers = 4
    scenarios_per_worker = total_scenarios // num_workers

    workers = [PortfolioRiskWorker.remote(seed=500 + i) for i in range(num_workers)]
    futures = [
        w.simulate_portfolio_returns.remote(
            weights, volatilities, portfolio_value, scenarios_per_worker
        )
        for w in workers
    ]

    worker_pnls = ray.get(futures)
    all_pnls: list[float] = []
    for chunk in worker_pnls:
        all_pnls.extend(chunk)

    assert len(all_pnls) == total_scenarios, (
        f"Expected {total_scenarios} scenarios, got {len(all_pnls)}"
    )

    # Sort P&L ascending (worst losses first)
    all_pnls.sort()

    # 99% VaR is the 1st percentile of losses
    var_index = int(0.01 * len(all_pnls))
    var_99 = -all_pnls[var_index]
    cvar_99 = -sum(all_pnls[:var_index]) / max(var_index, 1)

    print(f"99% 1-Day VaR:  ${var_99:,.2f}")
    print(f"99% 1-Day CVaR: ${cvar_99:,.2f}")

    assert var_99 > 200_000, f"VaR {var_99} lower than expected"
    assert cvar_99 > var_99, "CVaR (Expected Shortfall) must exceed VaR"
    print("✓ finance02 verified: Distributed Portfolio VaR and CVaR computed successfully!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
