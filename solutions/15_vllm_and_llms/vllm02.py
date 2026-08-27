"""Chapter 15: Distributed LLM Serving & vLLM - Solution 2: PagedAttention & KV-Cache Block Management.

Reference Solution for vllm02.
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
        """Allocate physical blocks for a prompt sequence with prefix block sharing."""
        table: list[int] = []
        num_tokens = len(prompt_tokens)

        # Chunk prompt tokens into block_size slices
        for start_idx in range(0, num_tokens, self.block_size):
            chunk = tuple(prompt_tokens[start_idx : start_idx + self.block_size])
            is_full_block = len(chunk) == self.block_size

            # If full block matches an existing cached prefix, share physical block
            if is_full_block and chunk in self.prefix_cache:
                physical_block_id = self.prefix_cache[chunk]
                self.block_ref_counts[physical_block_id] += 1
            else:
                if not self.free_blocks:
                    raise RuntimeError("Out of physical KV-cache memory blocks")
                physical_block_id = self.free_blocks.pop(0)
                self.block_ref_counts[physical_block_id] = 1
                if is_full_block:
                    self.prefix_cache[chunk] = physical_block_id

            table.append(physical_block_id)

        self.block_tables[seq_id] = table
        self.seq_lengths[seq_id] = num_tokens
        return table

    def append_token(self, seq_id: str, token_id: int) -> tuple[int, int]:
        """Append a newly generated token, allocating a new physical block if needed."""
        if seq_id not in self.block_tables:
            raise KeyError(f"Sequence '{seq_id}' not found")

        curr_len = self.seq_lengths[seq_id]
        offset = curr_len % self.block_size

        # If current block is full (offset == 0 and curr_len > 0), allocate a new block
        if offset == 0:
            if not self.free_blocks:
                raise RuntimeError("Out of physical KV-cache memory blocks")
            new_block_id = self.free_blocks.pop(0)
            self.block_ref_counts[new_block_id] = 1
            self.block_tables[seq_id].append(new_block_id)

        physical_block_id = self.block_tables[seq_id][-1]
        self.seq_lengths[seq_id] += 1
        return physical_block_id, offset

    def translate_logical_to_physical(self, seq_id: str, logical_token_idx: int) -> tuple[int, int]:
        """Translate sequence token index to (physical_block_id, block_offset)."""
        if seq_id not in self.block_tables:
            raise KeyError(f"Sequence '{seq_id}' not found")
        if logical_token_idx >= self.seq_lengths[seq_id]:
            raise IndexError(
                f"Token index {logical_token_idx} out of range for sequence length {self.seq_lengths[seq_id]}"
            )

        logical_block_idx = logical_token_idx // self.block_size
        offset = logical_token_idx % self.block_size
        physical_block_id = self.block_tables[seq_id][logical_block_idx]
        return physical_block_id, offset

    def free_sequence(self, seq_id: str) -> None:
        """Release blocks for a completed sequence, decrementing refs and reclaiming memory."""
        if seq_id not in self.block_tables:
            return

        for block_id in self.block_tables[seq_id]:
            self.block_ref_counts[block_id] -= 1
            if self.block_ref_counts[block_id] == 0:
                # Remove from prefix cache if this block is no longer referenced
                for prefix, pid in list(self.prefix_cache.items()):
                    if pid == block_id:
                        del self.prefix_cache[prefix]
                self.free_blocks.append(block_id)

        del self.block_tables[seq_id]
        del self.seq_lengths[seq_id]

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
    assert len(table_a) == 2, f"Expected 2 blocks for 6 tokens, got {len(table_a)}"
    assert ray.get(manager.get_num_free_blocks.remote()) == 6

    # 2. Translate logical token index to physical block + offset
    p_blk, offset = ray.get(manager.translate_logical_to_physical.remote("seq_A", 5))
    assert p_blk == table_a[1], f"Expected physical block {table_a[1]}, got {p_blk}"
    assert offset == 1, f"Expected offset 1, got {offset}"

    # 3. Allocate sequence B with shared 4-token prompt prefix
    prompt_b = [101, 102, 103, 104, 301, 302]
    table_b = ray.get(manager.allocate_sequence.remote("seq_B", prompt_b))
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
