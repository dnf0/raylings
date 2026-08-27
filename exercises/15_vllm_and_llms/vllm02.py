"""Chapter 15: Distributed LLM Serving & vLLM - Exercise 2: PagedAttention & KV-Cache Block Management.

PagedAttention eliminates KV-cache memory fragmentation by managing memory in fixed-size
physical blocks, translating logical token positions into physical block addresses via block tables.

Key Concepts:
- `Block Tables`: Maps each sequence's logical token blocks to non-contiguous physical memory blocks.
- `Dynamic Allocation`: As new tokens are generated autoregressively, new physical blocks are
  allocated on-demand only when existing blocks are full (`curr_len % block_size == 0`).
- `Prefix Caching & Block Sharing`: Identical prompt prefixes share physical blocks via reference
  counting, reducing memory footprint across concurrent requests.

Your Task:
- In `PagedKVCacheManager.allocate_sequence(seq_id, prompt_tokens)`:
  - Slice `prompt_tokens` into chunks of `self.block_size`.
  - Check if a full chunk is in `self.prefix_cache`; if so, reuse that physical block and increment its ref count.
  - Otherwise, pop a new block from `self.free_blocks`, set ref count = 1, and cache the prefix chunk.
  - Store the resulting block table and sequence length.
- In `PagedKVCacheManager.append_token(seq_id, token_id)`:
  - If the current sequence length is a multiple of `self.block_size`, allocate a new physical block from `self.free_blocks`.
  - Increment `self.seq_lengths[seq_id]` and return `(physical_block_id, offset)`.
- In `PagedKVCacheManager.translate_logical_to_physical(seq_id, logical_token_idx)`:
  - Compute `logical_block_idx = logical_token_idx // self.block_size` and `offset = logical_token_idx % self.block_size`.
  - Return `(self.block_tables[seq_id][logical_block_idx], offset)`.
- In `PagedKVCacheManager.free_sequence(seq_id)`:
  - Decrement ref counts for all allocated blocks in `seq_id`. Reclaim blocks with ref count == 0 back to `self.free_blocks`.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray


@ray.remote
class PagedKVCacheManager:
    """Manages non-contiguous physical KV-cache memory blocks and sequence block tables."""

    def __init__(self, num_blocks: int, block_size: int = 4) -> None:
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.free_blocks: list[int] = list(range(num_blocks))
        self.block_ref_counts: dict[int, int] = {i: 0 for i in range(num_blocks)}
        self.block_tables: dict[str, list[int]] = {}
        self.seq_lengths: dict[str, int] = {}
        # Prefix cache maps full block token tuples to physical block IDs
        self.prefix_cache: dict[tuple[int, ...], int] = {}

    def allocate_sequence(self, seq_id: str, prompt_tokens: list[int]) -> list[int]:
        # TODO: Chunk prompt tokens, reuse matching prefix blocks or allocate new blocks
        pass

    def append_token(self, seq_id: str, token_id: int) -> tuple[int, int]:
        # TODO: Append token, dynamically allocating new block if block boundary crossed
        pass

    def translate_logical_to_physical(self, seq_id: str, logical_token_idx: int) -> tuple[int, int]:
        # TODO: Translate logical token index to (physical_block_id, offset)
        pass

    def free_sequence(self, seq_id: str) -> None:
        # TODO: Decrement ref counts and return unused blocks to free pool
        pass

    def get_num_free_blocks(self) -> int:
        """Return the count of unallocated physical memory blocks."""
        return len(self.free_blocks)

    def get_block_table(self, seq_id: str) -> list[int]:
        """Return the physical block IDs mapped to a sequence."""
        return list(self.block_tables.get(seq_id, []))


def verify() -> None:
    ray.init(ignore_reinit_error=True)

    manager = PagedKVCacheManager.remote(num_blocks=8, block_size=4)
    assert ray.get(manager.get_num_free_blocks.remote()) == 8

    # 1. Allocate sequence A (6 tokens -> 2 physical blocks)
    prompt_a = [101, 102, 103, 104, 201, 202]
    table_a = ray.get(manager.allocate_sequence.remote("seq_A", prompt_a))
    assert table_a is not None, "allocate_sequence returned None"
    assert len(table_a) == 2, f"Expected 2 blocks for 6 tokens, got {len(table_a)}"
    assert ray.get(manager.get_num_free_blocks.remote()) == 6

    # 2. Translate logical token index to physical block + offset
    p_blk, offset = ray.get(manager.translate_logical_to_physical.remote("seq_A", 5))
    assert p_blk == table_a[1], f"Expected physical block {table_a[1]}, got {p_blk}"
    assert offset == 1, f"Expected offset 1, got {offset}"

    # 3. Allocate sequence B with shared 4-token prompt prefix
    prompt_b = [101, 102, 103, 104, 301, 302]
    table_b = ray.get(manager.allocate_sequence.remote("seq_B", prompt_b))
    assert table_b is not None, "allocate_sequence returned None"
    assert len(table_b) == 2
    # Prefix block must be reused!
    assert table_b[0] == table_a[0], (
        f"Prefix block was not reused: seq_A block {table_a[0]} vs seq_B block {table_b[0]}"
    )
    assert table_b[1] != table_a[1], "Distinct suffix tokens should occupy distinct physical blocks"
    # Only 1 additional block consumed due to prefix sharing (8 - 2 - 1 = 5 free)
    assert ray.get(manager.get_num_free_blocks.remote()) == 5

    # 4. Append tokens dynamically to sequence A (cross block boundary: 6 -> 9 tokens)
    ray.get(manager.append_token.remote("seq_A", 203))  # token 7 (offset 2 in block 1)
    ray.get(manager.append_token.remote("seq_A", 204))  # token 8 (offset 3 in block 1)
    assert ray.get(manager.get_num_free_blocks.remote()) == 5

    ray.get(manager.append_token.remote("seq_A", 205))  # token 9 (triggers block 2 allocation)
    table_a_updated = ray.get(manager.get_block_table.remote("seq_A"))
    assert len(table_a_updated) == 3, f"Expected 3 blocks for 9 tokens, got {len(table_a_updated)}"
    assert ray.get(manager.get_num_free_blocks.remote()) == 4

    # 5. Free sequence A and sequence B, verifying reference counting
    ray.get(manager.free_sequence.remote("seq_A"))
    # Shared prefix block is still held by seq_B, so only 2 blocks freed (4 + 2 = 6 free)
    assert ray.get(manager.get_num_free_blocks.remote()) == 6

    ray.get(manager.free_sequence.remote("seq_B"))
    # All 8 blocks must be returned to free pool
    assert ray.get(manager.get_num_free_blocks.remote()) == 8

    print(
        "✓ vllm02 verified: PagedAttention KV-cache block allocation and prefix sharing validated!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
