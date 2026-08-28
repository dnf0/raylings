"""Chapter 18: Distributed Quantitative Finance - Exercise 3: High-Frequency Market Tick Analytics with Ray Data.

In high-frequency quantitative trading, millions of market order events and trades
arrive per second. Computing real-time Volume-Weighted Average Price (VWAP):
    VWAP = sum(Price_i * Volume_i) / sum(Volume_i)
requires high-throughput streaming batch pipelines with zero-copy vectorized transformations.

Key Concepts:
1. Streaming Ingestion: Consuming tick batches into Ray Data streaming pipelines.
2. Vectorized Windowing: Computing dollar volumes and cumulative quantities per symbol.
3. Stateful Stream Filtering: Discarding anomalous quotes (spread outliers) without stalling throughput.

Your Task:
- Implement `compute_tick_metrics` in `map_batches` to compute `dollar_volume` (`price * volume`).
- Filter out bad ticks where `spread <= 0`.
- Compute final global VWAP across all processed market events.
"""

import os
import random

import ray

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"


def generate_market_ticks(num_ticks: int = 1_000) -> list[dict[str, float]]:
    """Generate synthetic high-frequency market trade ticks."""
    rng = random.Random(42)
    ticks = []
    base_price = 150.0
    for i in range(num_ticks):
        # 98% valid ticks, 2% crossed/negative spread anomalies
        spread = rng.choice([0.01, 0.02, 0.05, -0.01])
        price_delta = rng.uniform(-0.1, 0.1)
        base_price = max(base_price + price_delta, 10.0)
        volume = float(rng.randint(10, 500))
        ticks.append(
            {
                "tick_id": float(i),
                "price": round(base_price, 2),
                "volume": volume,
                "spread": spread,
            }
        )
    return ticks


def compute_tick_metrics(batch: dict[str, list[float]]) -> dict[str, list[float]]:
    """Compute dollar_volume = price * volume for each tick in batch."""
    # TODO: Implement vectorized batch computation for dollar_volume
    # prices = batch["price"]
    # volumes = batch["volume"]
    # dollar_volumes = [p * v for p, v in zip(prices, volumes)]
    # return {
    #     "tick_id": batch["tick_id"],
    #     "price": prices,
    #     "volume": volumes,
    #     "spread": batch["spread"],
    #     "dollar_volume": dollar_volumes,
    # }
    return {k: [] for k in batch}


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    raw_ticks = generate_market_ticks(1_000)
    ds = ray.data.from_items(raw_ticks, override_num_blocks=2)

    # Filter out anomalous ticks with invalid spread
    valid_ds = ds.filter(lambda row: row["spread"] > 0)

    # Compute dollar volume in batches
    enriched_ds = valid_ds.map_batches(compute_tick_metrics, batch_size=250)

    results = enriched_ds.take_all()
    assert len(results) > 600, f"Expected >600 valid ticks, got {len(results)}"
    assert "dollar_volume" in results[0], "Missing dollar_volume field in enriched output"

    total_dollar_volume = sum(row["dollar_volume"] for row in results)
    total_volume = sum(row["volume"] for row in results)
    vwap = total_dollar_volume / total_volume

    print(f"Total Processed Volume: {total_volume:,.0f} shares")
    print(f"Calculated Global VWAP: ${vwap:.4f}")

    assert 140.0 < vwap < 160.0, f"Calculated VWAP {vwap} out of expected range [140.0, 160.0]"
    print("✓ finance03 verified: High-Frequency Streaming Market Tick Pipeline succeeded!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
