"""Chapter 15: Distributed LLM Serving & vLLM - Exercise 4: Speculative Decoding with Draft & Target Workers.

Speculative Decoding accelerates autoregressive inference by generating multiple candidate tokens
using a fast, lightweight draft model and verifying them in parallel with a large target model.

Key Concepts:
- `Draft Model Worker`: Quickly generates $K$ speculative tokens autoregressively.
- `Target Model Worker`: Validates all $K$ tokens in a single batch forward pass.
- `Speculative Verification Loop`:
  - Compares draft tokens against target predictions sequentially.
  - If draft token matches: accepts the draft token.
  - On first mismatch: rejects remaining draft tokens, emits target model's corrected token, and halts round.
  - If all $K$ draft tokens match: accepts all $K$ tokens plus an additional bonus token from the target model.

Your Task:
- In `SpeculativeEngine.generate(prompt, total_length)`:
  - While `len(sequence) < total_length`:
    - Generate `k_speculative` draft tokens from `draft_worker`.
    - Evaluate candidates in a single batch call with `target_worker`.
    - Implement the verification loop:
      - Compare `draft_tokens[i]` with `target_tokens[i]`.
      - On match: append `draft_tok` and increment `self.accepted_draft_tokens`.
      - On mismatch: append `target_tok` (the correction) and break out of the draft loop.
    - If all draft tokens matched and sequence is not full, append `target_tokens[len(draft_tokens)]` (the bonus token).
"""

import os
from typing import Any

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
class DraftModelWorker:
    """Fast, lightweight draft model actor producing K speculative candidate tokens."""

    def __init__(self, error_on_token: int = 5, mistake_token: int = 99) -> None:
        self.error_on_token = error_on_token
        self.mistake_token = mistake_token

    def generate_draft(self, prefix: list[int], k: int) -> list[int]:
        """Generate K candidate tokens autoregressively."""
        tokens: list[int] = []
        curr = prefix[-1] if prefix else 0
        for _ in range(k):
            if curr == self.error_on_token:
                nxt = self.mistake_token
            else:
                nxt = curr + 1
            tokens.append(nxt)
            curr = nxt
        return tokens


@ray.remote
class TargetModelWorker:
    """Large, authoritative target model actor validating candidate sequences in a single batch pass."""

    def __init__(self) -> None:
        self.forward_pass_count = 0

    def evaluate_candidates(self, prefix: list[int], draft_tokens: list[int]) -> list[int]:
        """Evaluate prefix + all draft candidates in a single parallel pass."""
        self.forward_pass_count += 1
        target_tokens: list[int] = []

        curr = list(prefix)
        target_tokens.append(curr[-1] + 1 if curr else 1)

        for d in draft_tokens:
            curr.append(d)
            target_tokens.append(curr[-1] + 1)

        return target_tokens

    def get_forward_pass_count(self) -> int:
        return self.forward_pass_count


class SpeculativeEngine:
    """Coordinates speculative drafting and parallel target verification."""

    def __init__(self, draft_worker: Any, target_worker: Any, k_speculative: int = 3) -> None:
        self.draft_worker = draft_worker
        self.target_worker = target_worker
        self.k_speculative = k_speculative
        self.accepted_draft_tokens = 0
        self.total_draft_tokens = 0
        self.target_forward_passes = 0

    def generate(self, prompt: list[int], total_length: int) -> tuple[list[int], dict[str, int]]:
        # TODO: Implement speculative generation and verification loop
        sequence = list(prompt)
        stats = {
            "target_forward_passes": 0,
            "total_draft_tokens": 0,
            "accepted_draft_tokens": 0,
        }
        return sequence, stats


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    prompt = [1]
    target_len = 12

    # Baseline sequential target model generation (1 token per forward pass)
    baseline_seq = list(prompt)
    while len(baseline_seq) < target_len:
        baseline_seq.append(baseline_seq[-1] + 1)
    baseline_forward_passes = target_len - len(prompt)  # 11 forward passes

    # Speculative decoding setup
    draft_worker = DraftModelWorker.remote(error_on_token=5, mistake_token=99)
    target_worker = TargetModelWorker.remote()

    engine = SpeculativeEngine(draft_worker, target_worker, k_speculative=3)
    generated_seq, stats = engine.generate(prompt, total_length=target_len)

    # 1. Output sequence must exactly match target model baseline
    assert generated_seq is not None, "generate() returned None"
    assert generated_seq == baseline_seq, (
        f"Speculative decoding produced incorrect sequence:\n"
        f"Got:      {generated_seq}\n"
        f"Expected: {baseline_seq}"
    )

    # 2. Target forward passes must be significantly fewer than sequential baseline
    assert stats["target_forward_passes"] < baseline_forward_passes, (
        f"No speculative speedup: {stats['target_forward_passes']} passes vs {baseline_forward_passes} baseline"
    )

    # 3. Verify acceptance metrics
    assert stats["accepted_draft_tokens"] > 0, "No draft tokens were accepted"
    acceptance_rate = stats["accepted_draft_tokens"] / stats["total_draft_tokens"]

    print(
        f"✓ vllm04 verified: Generated {len(generated_seq)} tokens in "
        f"{stats['target_forward_passes']} target passes (vs {baseline_forward_passes} baseline)! "
        f"Draft acceptance rate: {acceptance_rate:.1%}"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
