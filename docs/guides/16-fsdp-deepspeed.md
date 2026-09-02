# Chapter 16: Multi-Node LLM Distributed Training (FSDP & DeepSpeed)

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Fully Sharded Data Parallel (FSDP), DeepSpeed ZeRO-3, Activation Checkpointing, and Multi-Node Scaling
-   :material-play-circle: **Interactive Challenges** &bull; 4 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=16){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

Training billion-parameter foundation models exceeds the VRAM capacity of any single GPU. **Fully Sharded Data Parallel (FSDP)** and **DeepSpeed ZeRO-3** eliminate memory redundancy by sharding optimizer states, gradients, and model parameters across all distributed ranks.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        FSDP ZeRO-3 Parameter Sharding                  │
│                                                                        │
│   Layer Parameters (W), Gradients (G), Optimizer States (O)            │
│                                                                        │
│   ┌───────────────────────────┐         ┌───────────────────────────┐  │
│   │ Rank 0 (Worker 0)         │         │ Rank 1 (Worker 1)         │  │
│   │ • Shard 0: W[0], G[0], O[0│         │ • Shard 1: W[1], G[1], O[1│  │
│   └─────────────┬─────────────┘         └─────────────┬─────────────┘  │
│                 │                                     │                │
│                 └───────────► All-Gather ◄────────────┘                │
│                        (On-Demand Forward Layer)                       │
└────────────────────────────────────────────────────────────────────────┘
```

During forward and backward passes, each layer's weights are gathered just-in-time via high-speed All-Gather operations and immediately released after computation, slashing per-GPU memory consumption by up to $8\times$.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from ray import train
from ray.train.torch import TorchTrainer, TorchConfig
from ray.train import ScalingConfig

def fsdp_train_loop_per_worker(config: dict):
    import torch
    import torch.nn as nn
    
    # In full environments: from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
    model = nn.Sequential(
        nn.Linear(1024, 2048),
        nn.ReLU(),
        nn.Linear(2048, 1024)
    )
    
    # Wrap model with distributed training coordinator
    model = train.torch.prepare_model(model)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    for step in range(config.get("steps", 5)):
        inputs = torch.randn(16, 1024)
        optimizer.zero_grad()
        loss = model(inputs).sum()
        loss.backward()
        optimizer.step()
        train.report({"loss": loss.item(), "step": step})

trainer = TorchTrainer(
    train_loop_per_worker=fsdp_train_loop_per_worker,
    scaling_config=ScalingConfig(num_workers=2, use_gpu=False)
)
```

---

## 3. Production Best Practices & Hardening Guidelines

1. **Enable Activation Checkpointing (Gradient Checkpointing)**: Discard intermediate activations during forward pass and recompute them during backward pass to save up to 70% VRAM.
2. **Use Mixed Precision (`torch.bfloat16`)**: Train in `bfloat16` to halve communication bandwidth and leverage Tensor Cores without underflow risks.
3. **Configure Backward Prefetching**: Set `backward_prefetch=BackwardPrefetch.BACKWARD_PRE` to overlap communication with backprop tensor calculations.
4. **Tune Auto-Wrapping Policy**: Wrap transformer blocks (e.g. `LlamaDecoderLayer`) with `transformer_auto_wrap_policy` for fine-grained sharding units.
5. **Set CPU Offloading for Giant Models**: Offload optimizer states to host RAM via `cpu_offload=CPUOffload(offload_params=True)` when model size exceeds aggregate GPU memory.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **Slow Training Due to High All-Gather Overhead**:
   - *Symptom*: GPU compute utilization drops below 40% with high communication wait times.
   - *Fix*: Increase batch size per rank or group layers into larger wrapping units to reduce communication frequency.
2. **Checkpoint Save Memory Spike**:
   - *Symptom*: Node crashes during model saving due to CPU RAM exhaustion.
   - *Fix*: Use `StateDictType.SHARDED_STATE_DICT` so each rank writes only its local shard directly to storage.
3. **Loss Instability / NaN in Mixed Precision**:
   - *Symptom*: Loss turns to NaN during early training steps.
   - *Fix*: Apply gradient norm clipping (`torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`).

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal | Playground Link |
| :--- | :--- | :--- |
| `fsdp01` | Configure PyTorch FSDP auto-wrapping policies for transformer layers | [**Open Exercise fsdp01 →**](../playground/index.html?exercise=fsdp01) |
| `fsdp02` | Apply activation checkpointing and bfloat16 mixed-precision training | [**Open Exercise fsdp02 →**](../playground/index.html?exercise=fsdp02) |
| `fsdp03` | Configure DeepSpeed ZeRO-3 optimizer state and parameter sharding | [**Open Exercise fsdp03 →**](../playground/index.html?exercise=fsdp03) |
| `fsdp04` | Save and restore distributed sharded checkpoints across multi-node clusters | [**Open Exercise fsdp04 →**](../playground/index.html?exercise=fsdp04) |
