"""Chapter 16: DeepSpeed & PyTorch FSDP - Solution 3: Mixed Precision & Activation Checkpointing.

Reference Solution for fsdp03.
"""

import os

os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
import ray
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.checkpoint import checkpoint


class TransformerBlock(nn.Module):
    """Feed-forward residual block simulating a transformer sub-layer."""

    def __init__(self, d_model: int = 128, d_ff: int = 512) -> None:
        super().__init__()
        self.norm = nn.LayerNorm(d_model)
        self.fc1 = nn.Linear(d_model, d_ff)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(d_ff, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        h = self.norm(x)
        h = self.act(self.fc1(h))
        h = self.fc2(h)
        return residual + h


class DeepSequentialModel(nn.Module):
    """Deep network supporting activation checkpointing across layers."""

    def __init__(
        self, num_blocks: int = 8, d_model: int = 128, use_checkpointing: bool = False
    ) -> None:
        super().__init__()
        self.blocks = nn.ModuleList([TransformerBlock(d_model=d_model) for _ in range(num_blocks)])
        self.head = nn.Linear(d_model, 1)
        self.use_checkpointing = use_checkpointing

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for block in self.blocks:
            if self.use_checkpointing and self.training:
                x = checkpoint(block, x, use_reentrant=False)
            else:
                x = block(x)
        return self.head(x)


def measure_saved_activation_memory(
    model: nn.Module, x: torch.Tensor
) -> tuple[int, int, torch.Tensor]:
    """Measure the exact byte size and count of saved activation tensors during forward-backward pass."""
    saved_bytes = 0
    saved_count = 0

    def pack_hook(tensor: torch.Tensor) -> torch.Tensor:
        nonlocal saved_bytes, saved_count
        saved_bytes += tensor.numel() * tensor.element_size()
        saved_count += 1
        return tensor

    def unpack_hook(tensor: torch.Tensor) -> torch.Tensor:
        return tensor

    model.zero_grad()
    if x.grad is not None:
        x.grad.zero_()

    with torch.autograd.graph.saved_tensors_hooks(pack_hook, unpack_hook):
        out = model(x)
        loss = out.sum()
        loss.backward()

    assert x.grad is not None, "Input tensor x must have gradients computed"
    return saved_bytes, saved_count, x.grad.clone()


@ray.remote
class MixedPrecisionWorker:
    """Ray actor executing mixed-precision training with activation checkpointing."""

    def __init__(
        self,
        rank: int,
        num_blocks: int = 8,
        d_model: int = 128,
        lr: float = 0.001,
        use_checkpointing: bool = True,
    ) -> None:
        self.rank = rank
        self.model = DeepSequentialModel(
            num_blocks=num_blocks, d_model=d_model, use_checkpointing=use_checkpointing
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

    def train_step(
        self, x: torch.Tensor, target: torch.Tensor, use_autocast: bool = True
    ) -> dict[str, float]:
        """Execute a forward-backward training step under bfloat16 autocast."""
        self.optimizer.zero_grad()
        with torch.autocast(device_type="cpu", dtype=torch.bfloat16, enabled=use_autocast):
            output = self.model(x)
            loss = self.criterion(output.float(), target.float())

        loss.backward()
        self.optimizer.step()
        return {"loss": float(loss.item())}


def verify() -> None:
    # 1. Verify Activation Checkpointing memory savings and gradient equivalence
    torch.manual_seed(42)
    d_model = 128
    num_blocks = 8
    batch_size = 32

    x_raw = torch.randn(batch_size, d_model)

    # Standard model without checkpointing
    torch.manual_seed(100)
    model_standard = DeepSequentialModel(
        num_blocks=num_blocks, d_model=d_model, use_checkpointing=False
    )
    x_std = x_raw.clone().detach().requires_grad_(True)
    bytes_std, count_std, grad_std = measure_saved_activation_memory(model_standard, x_std)

    # Model with activation checkpointing enabled (identical initial weights)
    torch.manual_seed(100)
    model_checkpointed = DeepSequentialModel(
        num_blocks=num_blocks, d_model=d_model, use_checkpointing=True
    )
    x_ckpt = x_raw.clone().detach().requires_grad_(True)
    bytes_ckpt, count_ckpt, grad_ckpt = measure_saved_activation_memory(model_checkpointed, x_ckpt)

    # Verify memory reduction > 40%
    reduction = (bytes_std - bytes_ckpt) / bytes_std
    assert reduction > 0.40, (
        f"Expected > 40% activation memory reduction, got {reduction:.2%} "
        f"(std={bytes_std} bytes vs ckpt={bytes_ckpt} bytes)"
    )

    # Verify gradients computed with checkpointing match standard backpropagation
    assert torch.allclose(grad_ckpt, grad_std, atol=1e-5), (
        f"Gradients mismatch with activation checkpointing! "
        f"Max diff: {(grad_ckpt - grad_std).abs().max().item():.2e}"
    )

    # 2. Verify Distributed Ray Worker execution with Mixed Precision
    ray.init(ignore_reinit_error=True)

    workers = [
        MixedPrecisionWorker.remote(
            rank=i, num_blocks=4, d_model=64, lr=0.001, use_checkpointing=True
        )
        for i in range(2)
    ]

    # Generate synthetic training batch
    torch.manual_seed(42)
    x_train = torch.randn(16, 64)
    y_train = torch.zeros(16, 1)

    initial_losses = ray.get([w.train_step.remote(x_train, y_train) for w in workers])
    step_losses = initial_losses
    for _ in range(15):
        step_losses = ray.get([w.train_step.remote(x_train, y_train) for w in workers])

    final_losses = step_losses
    assert final_losses[0]["loss"] < initial_losses[0]["loss"], (
        f"Loss did not decrease: initial={initial_losses[0]['loss']:.4f}, final={final_losses[0]['loss']:.4f}"
    )

    print(
        f"✓ fsdp03 verified: Activation Checkpointing achieved {reduction:.1%} memory reduction "
        f"({bytes_std} -> {bytes_ckpt} bytes) with exact gradients and distributed mixed-precision training!"
    )
    ray.shutdown()


if __name__ == "__main__":
    verify()
