# Chapter 08: Streaming Ray Data & Distributed Data Pipelines

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Ray Data, Streaming Datasets, Block Partitioning, and Zero-Copy Batch Transformations
-   :material-play-circle: **Interactive Challenges** &bull; 5 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=8){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

**Ray Data** provides scalable, streaming data processing designed specifically for distributed AI/ML training and inference workloads. Instead of loading whole datasets into memory, Ray Data streams discrete **Block Partitions** through pipelined execution stages.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Ray Data Streaming Pipeline                     │
│                                                                        │
│   [ S3 / Parquet ] ──► [ Read Blocks ] ──► [ Map Batches ] ──► [ Train ]│
│         │                     │                   │               │    │
│         │                     ▼                   ▼               ▼    │
│         └────────────► [ Block 0 ] ──────► [ Block 0' ] ──► [ Worker 0 ]
│                        [ Block 1 ] ──────► [ Block 1' ] ──► [ Worker 1 ]
└────────────────────────────────────────────────────────────────────────┘
```

This streaming architecture overlaps data reading, preprocessing, and GPU tensor loading, preventing training worker starvation.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray

# 1. Create a distributed streaming dataset from in-memory records or storage
dataset = ray.data.range(1000)

# 2. Apply vectorized transformations using map_batches
def normalize_batch(batch: dict) -> dict:
    # batch is an Arrow table or NumPy dict
    values = batch["id"]
    return {"id": values, "normalized": [v / 1000.0 for v in values]}

transformed_ds = (
    dataset
    .map_batches(normalize_batch, batch_format="numpy", batch_size=100)
    .filter(lambda row: row["normalized"] > 0.5)
)

# 3. Stream batches directly into ML training loops
for batch in transformed_ds.iter_batches(batch_size=32):
    pass
```

### Key API Parameter Reference

- **`ray.data.read_parquet(paths)`**: Reads Parquet files in parallel into distributed blocks.
- **`ds.map_batches(fn, batch_size=N, batch_format="numpy"|"arrow")`**: Vectorized batch transformation.
- **`ds.repartition(num_blocks)`**: Reshapes dataset block partitions across cluster nodes.
- **`ds.iter_torch_batches(batch_size, dtypes=...)`**: Streams preprocessed batches directly as PyTorch tensors.

---

## 3. Production Best Practices & Hardening Guidelines

1. **Use `map_batches` Over `map`**: `map_batches` operates on vectorized NumPy/PyArrow chunks, achieving 10–50x higher throughput than row-by-row `map`.
2. **Tune Block Sizes**: Target block sizes between 50MB and 200MB to balance parallelism and metadata overhead.
3. **Use Actor Pools for Stateful Models in `map_batches`**: Pass `compute=ray.data.ActorPoolStrategy(min=2, max=8)` when applying embedding or inference models.
4. **Window Pipelines with `window(blocks_per_window=N)`**: For datasets larger than cluster memory, use streaming windows to bound memory consumption.
5. **Set Explicit Prefetch Batches**: Use `ds.iter_batches(prefetch_batches=2)` to overlap GPU execution with CPU preprocessing.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **High Memory Spilling in Data Pipelines**:
   - *Symptom*: Object store memory fills and spills gigabytes of intermediate blocks.
   - *Fix*: Reduce batch sizes in `map_batches` or enable streaming mode to discard consumed blocks immediately.
2. **Slow Reader Throughput**:
   - *Symptom*: GPU training workers idle waiting for data batches.
   - *Fix*: Increase `parallelism` parameter during file read; check network bandwidth to object store.
3. **Arrow Type Incompatibility in `map_batches`**:
   - *Symptom*: Schema errors when returning heterogeneous dictionary keys.
   - *Fix*: Ensure all returned batch dictionaries maintain strict, consistent type schemas across all partitions.

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal | Playground Link |
| :--- | :--- | :--- |
| `data01` | Create and transform basic streaming Ray Datasets | [**Open Exercise data01 →**](../playground/index.html?exercise=data01) |
| `data02` | Apply high-throughput vectorized `map_batches` transformations | [**Open Exercise data02 →**](../playground/index.html?exercise=data02) |
| `data03` | Partition and balance distributed blocks with `repartition()` | [**Open Exercise data03 →**](../playground/index.html?exercise=data03) |
| `data04` | Stream batches into simulated PyTorch ML training loops | [**Open Exercise data04 →**](../playground/index.html?exercise=data04) |
| `data05` | Build a multi-stage streaming pipeline with actor compute pools | [**Open Exercise data05 →**](../playground/index.html?exercise=data05) |
