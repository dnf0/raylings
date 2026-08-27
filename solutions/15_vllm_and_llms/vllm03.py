r"""Chapter 15: Distributed LLM Serving & vLLM - Solution 3: Dynamic Multi-LoRA Adapter Serving.

Reference Solution for vllm03.
"""

import os
from collections import OrderedDict

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import numpy as np
import ray


@ray.remote
class MultiLoRAServingWorker:
    """Stateful model serving actor supporting dynamic LoRA adapter loading and LRU eviction."""

    def __init__(self, base_weight: np.ndarray, max_cached_adapters: int = 3) -> None:
        self.base_weight = base_weight  # Shape: [d_in, d_out]
        self.max_cached_adapters = max_cached_adapters
        # Cache maps adapter_id -> (lora_a, lora_b, scaling_factor)
        self.adapter_cache: OrderedDict[str, tuple[np.ndarray, np.ndarray, float]] = OrderedDict()

    def load_adapter(
        self,
        adapter_id: str,
        lora_a: np.ndarray,
        lora_b: np.ndarray,
        alpha: float = 1.0,
    ) -> None:
        """Load and cache low-rank adapter weights (lora_a: [d_in, r], lora_b: [r, d_out])."""
        rank = lora_a.shape[1]
        scaling = alpha / float(rank)

        if adapter_id in self.adapter_cache:
            self.adapter_cache.move_to_end(adapter_id)
            self.adapter_cache[adapter_id] = (lora_a, lora_b, scaling)
        else:
            if len(self.adapter_cache) >= self.max_cached_adapters:
                # Evict least recently used adapter
                self.adapter_cache.popitem(last=False)
            self.adapter_cache[adapter_id] = (lora_a, lora_b, scaling)

    def forward(self, x: np.ndarray, adapter_id: str | None = None) -> np.ndarray:
        """Execute forward pass: Y = X @ W_base + scale * (X @ A) @ B if adapter requested."""
        base_output = np.matmul(x, self.base_weight)

        if adapter_id is None:
            return base_output

        if adapter_id not in self.adapter_cache:
            raise KeyError(f"Adapter '{adapter_id}' is not loaded in worker cache")

        # Mark adapter as recently used
        self.adapter_cache.move_to_end(adapter_id)
        lora_a, lora_b, scaling = self.adapter_cache[adapter_id]

        # Compute low-rank adaptation: scale * ((X @ A) @ B)
        lora_hidden = np.matmul(x, lora_a)
        lora_output = scaling * np.matmul(lora_hidden, lora_b)

        return base_output + lora_output

    def get_cached_adapters(self) -> list[str]:
        """Return list of currently cached adapter IDs in LRU order."""
        return list(self.adapter_cache.keys())


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    rng = np.random.default_rng(42)
    d_in = 8
    d_out = 8
    rank = 2
    batch_size = 2

    base_w = rng.standard_normal((d_in, d_out)).astype(np.float32)
    x = rng.standard_normal((batch_size, d_in)).astype(np.float32)

    worker = MultiLoRAServingWorker.remote(base_weight=base_w, max_cached_adapters=3)

    # 1. Base model forward pass without adapter
    base_out = ray.get(worker.forward.remote(x))
    expected_base = np.matmul(x, base_w)
    assert np.allclose(base_out, expected_base, atol=1e-5), "Base forward pass mismatch"

    # 2. Create 4 LoRA adapters
    adapters = {
        "finance": (
            rng.standard_normal((d_in, rank)).astype(np.float32),
            rng.standard_normal((rank, d_out)).astype(np.float32),
            2.0,
        ),
        "legal": (
            rng.standard_normal((d_in, rank)).astype(np.float32),
            rng.standard_normal((rank, d_out)).astype(np.float32),
            1.0,
        ),
        "medical": (
            rng.standard_normal((d_in, rank)).astype(np.float32),
            rng.standard_normal((rank, d_out)).astype(np.float32),
            4.0,
        ),
        "code": (
            rng.standard_normal((d_in, rank)).astype(np.float32),
            rng.standard_normal((rank, d_out)).astype(np.float32),
            2.0,
        ),
    }

    # 3. Load first 3 adapters
    for name in ["finance", "legal", "medical"]:
        a, b, alpha = adapters[name]
        ray.get(worker.load_adapter.remote(name, a, b, alpha=alpha))

    cached = ray.get(worker.get_cached_adapters.remote())
    assert cached == ["finance", "legal", "medical"], f"Unexpected cache state: {cached}"

    # 4. Forward with 'finance' adapter
    fin_out = ray.get(worker.forward.remote(x, adapter_id="finance"))
    a_fin, b_fin, alpha_fin = adapters["finance"]
    expected_fin = expected_base + (alpha_fin / rank) * np.matmul(np.matmul(x, a_fin), b_fin)
    assert np.allclose(fin_out, expected_fin, atol=1e-5), "Finance LoRA output mismatch"

    # 5. Forward with 'legal' adapter (access order now: medical, finance, legal)
    leg_out = ray.get(worker.forward.remote(x, adapter_id="legal"))
    a_leg, b_leg, alpha_leg = adapters["legal"]
    expected_leg = expected_base + (alpha_leg / rank) * np.matmul(np.matmul(x, a_leg), b_leg)
    assert np.allclose(leg_out, expected_leg, atol=1e-5), "Legal LoRA output mismatch"

    # 6. Load 4th adapter ('code') -> triggers LRU eviction of 'medical'
    a_code, b_code, alpha_code = adapters["code"]
    ray.get(worker.load_adapter.remote("code", a_code, b_code, alpha=alpha_code))

    cached_after = ray.get(worker.get_cached_adapters.remote())
    assert cached_after == ["finance", "legal", "code"], (
        f"LRU eviction failed. Expected ['finance', 'legal', 'code'], got {cached_after}"
    )

    # 7. Forward with 'code' adapter
    code_out = ray.get(worker.forward.remote(x, adapter_id="code"))
    expected_code = expected_base + (alpha_code / rank) * np.matmul(np.matmul(x, a_code), b_code)
    assert np.allclose(code_out, expected_code, atol=1e-5), "Code LoRA output mismatch"

    # 8. Evicted adapter ('medical') should raise KeyError
    try:
        ray.get(worker.forward.remote(x, adapter_id="medical"))
        raise AssertionError("Expected KeyError for evicted adapter 'medical'")
    except Exception as exc:
        assert "medical" in str(exc), f"Expected error mentioning 'medical', got: {exc}"

    print("✓ vllm03 verified: Multi-LoRA dynamic adapter loading and LRU eviction validated!")
    ray.shutdown()


if __name__ == "__main__":
    verify()
