# Chapter 16: Multi-Node LLM Distributed Training (FSDP & DeepSpeed)

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Fully Sharded Data Parallel (FSDP), DeepSpeed ZeRO-3, Activation Checkpointing, and Multi-Node Scaling
-   :material-play-circle: **Interactive Challenges** &bull; 4 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=16){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

Training billion-parameter foundation models exceeds the VRAM capacity of any single GPU. **Fully Sharded Data Parallel (FSDP)** and **DeepSpeed ZeRO-3** eliminate memory redundancy by sharding optimizer states, gradients, and model parameters across all distributed ranks.

```mermaid
flowchart TD
    subgraph ModelDecomp["Foundation Model Decomposition (100B+ Parameters)"]
        FullModel["Full Model Architecture: Parameters (W), Gradients (G), AdamW States (O)"]
    end

    subgraph ShardedGPUCluster["ZeRO-3 / FSDP Uniform Memory Sharding"]
        subgraph Rank0["GPU Rank 0 (Worker 0)"]
            S0_W["Shard 0: Weights W[0] (25%)"]
            S0_G["Shard 0: Grads G[0] (25%)"]
            S0_O["Shard 0: Optimizer O[0] (25%)"]
        end

        subgraph Rank1["GPU Rank 1 (Worker 1)"]
            S1_W["Shard 1: Weights W[1] (25%)"]
            S1_G["Shard 1: Grads G[1] (25%)"]
            S1_O["Shard 1: Optimizer O[1] (25%)"]
        end

        subgraph Rank2["GPU Rank 2 (Worker 2)"]
            S2_W["Shard 2: Weights W[2] (25%)"]
            S2_G["Shard 2: Grads G[2] (25%)"]
            S2_O["Shard 2: Optimizer O[2] (25%)"]
        end

        subgraph Rank3["GPU Rank 3 (Worker 3)"]
            S3_W["Shard 3: Weights W[3] (25%)"]
            S3_G["Shard 3: Grads G[3] (25%)"]
            S3_O["Shard 3: Optimizer O[3] (25%)"]
        end
    end

    subgraph DynamicInterconnect["Just-In-Time Hardware Collectives (NVLink / InfiniBand)"]
        AllGather["Forward Pass: Layer-by-Layer All-Gather (W Full Reconstructed -> Compute -> Discarded)"]
        ReduceScatter["Backward Pass: Reduce-Scatter (Gradients Sharded Across Ranks)"]
    end

    FullModel --> ShardedGPUCluster
    Rank0 <==> DynamicInterconnect
    Rank1 <==> DynamicInterconnect
    Rank2 <==> DynamicInterconnect
    Rank3 <==> DynamicInterconnect

    style ModelDecomp fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style ShardedGPUCluster fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style DynamicInterconnect fill:#1e1e38,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style Rank0 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
    style Rank1 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
    style Rank2 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
    style Rank3 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
```

```mermaid
sequenceDiagram
    autonumber
    participant R0 as GPU Rank 0 (Holds W0)
    participant R1 as GPU Rank 1 (Holds W1)
    participant NV as NVLink Collective Fabric

    Note over R0,R1: Forward Pass (Layer L): Just-In-Time All-Gather
    R0->>NV: Broadcast Local Shard W0
    R1->>NV: Broadcast Local Shard W1
    NV-->>R0: Full Layer Weights [W0 + W1]
    NV-->>R1: Full Layer Weights [W0 + W1]
    R0->>R0: Forward Activation Compute(Layer L)
    R1->>R1: Forward Activation Compute(Layer L)
    Note over R0,R1: Immediate Memory Release (Free non-sharded weights)

    Note over R0,R1: Backward Pass (Layer L): Reduce-Scatter Gradients
    R0->>R0: Backward Gradient Compute -> Full Grad G_L
    R1->>R1: Backward Gradient Compute -> Full Grad G_L
    R0->>NV: ReduceScatter(G_L)
    R1->>NV: ReduceScatter(G_L)
    NV-->>R0: Sharded Gradient G0
    NV-->>R1: Sharded Gradient G1
    Note over R0,R1: Optimizer Step: Each rank updates only its local optimizer state & shard
```

During forward and backward passes, each layer's weights are gathered just-in-time via high-speed All-Gather operations and immediately released after computation, slashing per-GPU memory consumption by up to $8\times$ while scaling across hundreds of nodes.

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

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `fsdp01` | PyTorch FSDP with Ray Train ScalingConfig | [**Open Exercise fsdp01 →**](../playground/index.html?exercise=fsdp01) |
| `fsdp02` | DeepSpeed ZeRO-1 / ZeRO-2 / ZeRO-3 Memory Partitioning | [**Open Exercise fsdp02 →**](../playground/index.html?exercise=fsdp02) |
| `fsdp03` | Mixed Precision & Activation Checkpointing | [**Open Exercise fsdp03 →**](../playground/index.html?exercise=fsdp03) |
| `fsdp04` | Elastic Fault-Tolerant Distributed Checkpoints | [**Open Exercise fsdp04 →**](../playground/index.html?exercise=fsdp04) |
