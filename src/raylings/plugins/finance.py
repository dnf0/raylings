"""Quantitative Finance Extension Pack plugin for Raylings."""

from __future__ import annotations

from raylings.models import Chapter, Exercise
from raylings.plugins.base import RaylingsPlugin


class FinancePlugin(RaylingsPlugin):
    """Provides Chapter 18: Distributed Quantitative Finance curriculum."""

    def __init__(self) -> None:
        super().__init__(
            name="finance",
            title="Distributed Quantitative Finance & High-Frequency Streaming",
            version="0.1.0",
            description=(
                "Domain-specific curriculum covering Monte Carlo derivative pricing, "
                "distributed portfolio Value-at-Risk (VaR), and streaming market tick analytics with Ray Data."
            ),
            author="Raylings Community",
        )

    def get_chapters(self) -> list[Chapter]:
        """Return Chapter 18 containing quant finance exercises."""
        return [
            Chapter(
                number=18,
                name="18_quant_finance",
                title="Distributed Quantitative Finance",
                description=(
                    "Scale computational finance workloads across Ray clusters: "
                    "Monte Carlo option simulation, correlated portfolio risk modeling, "
                    "and high-frequency market tick processing."
                ),
                exercises=[
                    Exercise(
                        name="finance01",
                        title="Monte Carlo European Option Pricing with Sharded Worker Actors",
                        path="exercises/18_quant_finance/finance01.py",
                        chapter_name="Distributed Quantitative Finance",
                        hints=[
                            "Simulate Geometric Brownian Motion: S_T = S_0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z).",
                            "Discount the European call payoff max(S_T - K, 0) by exp(-r * T) and average across workers.",
                        ],
                    ),
                    Exercise(
                        name="finance02",
                        title="Distributed Multi-Asset Portfolio Value-at-Risk (VaR) & CVaR",
                        path="exercises/18_quant_finance/finance02.py",
                        chapter_name="Distributed Quantitative Finance",
                        hints=[
                            "Combine common market factor with idiosyncratic noise to simulate correlated returns.",
                            "Sort combined P&L outcomes ascending; 99% VaR is the 1st percentile dollar loss.",
                        ],
                    ),
                    Exercise(
                        name="finance03",
                        title="High-Frequency Streaming Market Tick Analytics & VWAP with Ray Data",
                        path="exercises/18_quant_finance/finance03.py",
                        chapter_name="Distributed Quantitative Finance",
                        hints=[
                            "Compute dollar_volume = price * volume for each tick inside compute_tick_metrics.",
                            "Use map_batches to transform high-throughput streaming tick events in chunks.",
                        ],
                    ),
                ],
            )
        ]
