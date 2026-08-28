from pathlib import Path

from scripts.enrich_all_exercises import enrich_file

# ==================== CHAPTER 13: OBSERVABILITY ====================

enrich_file(
    Path("exercises/13_observability_and_debugging/perf01.py"),
    topic="Execution Profiling & Chrome Tracing with ray.timeline()",
    context_why="""
Diagnosing stragglers and serialization bottlenecks in distributed systems requires visual execution traces.
`ray.timeline(filename=\"timeline.json\")` exports complete Chrome Tracing / Perfetto JSON files
recording exact start, run, and completion timestamps for all tasks and actors across cluster nodes.
""",
    instructions=[
        "Instrument task execution and export trace events with `ray.timeline()`.",
        "Verify trace file generation and timeline event structure.",
    ],
    todo_replacements=[
        (
            "# TODO: Export execution timeline",
            "# TODO: Export execution timeline\n    # WHY: ray.timeline() exports JSON traces viewable in chrome://tracing or Perfetto UI.",
        )
    ],
)

enrich_file(
    Path("exercises/13_observability_and_debugging/perf02.py"),
    topic="Diagnosing Memory Leaks with ray memory",
    context_why="""
Holding onto `ObjectRef`s in global Python variables or long-lived actor state prevents Plasma from
garbage-collecting the underlying shared memory buffers.
`ray.util.state.list_objects()` or `ray.experimental.internal_kv` APIs inspect active object references,
pinned memory allocations, and spilled bytes across nodes.
""",
    instructions=[
        "Identify and release leaked ObjectRefs.",
        "Verify memory reclamation in the object store.",
    ],
    todo_replacements=[
        (
            "# TODO: Inspect object store memory",
            "# TODO: Inspect object store memory\n    # WHY: Inspecting active ObjectRefs allows finding uncollected references consuming Plasma memory.",
        )
    ],
)

enrich_file(
    Path("exercises/13_observability_and_debugging/perf03.py"),
    topic="Ray Metrics & Prometheus State APIs",
    context_why="""
Ray exports cluster telemetry (CPU, GPU, Plasma memory, task queues, actor counts) via standard
Prometheus endpoints and the `ray.util.state` Python SDK.
Querying state APIs enables building automated health dashboards and autoscaling controllers.
""",
    instructions=[
        "Query cluster metrics and actor states using `ray.util.state`.",
        "Assert expected task completion metrics.",
    ],
    todo_replacements=[
        (
            "# TODO: Query cluster state APIs",
            "# TODO: Query cluster state APIs\n    # WHY: ray.util.state queries the GCS state tables for active tasks, actors, and objects.",
        )
    ],
)

# ==================== CHAPTER 14: KUBERAY ====================

enrich_file(
    Path("exercises/14_kuberay/kuberay01.py"),
    topic="RayCluster Custom Resource Definition (CRD)",
    context_why="""
The KubeRay Operator manages Ray clusters natively on Kubernetes.
The `RayCluster` CRD declaratively specifies head pod and worker group pod templates, CPU/memory limits,
GPU tolerations, and container images.
""",
    instructions=[
        "Author a valid `RayCluster` YAML spec.",
        "Validate head and worker group configurations.",
    ],
    todo_replacements=[
        (
            "# TODO: Define RayCluster spec",
            "# TODO: Define RayCluster spec\n    # WHY: The RayCluster CRD defines Kubernetes pod templates and resource limits for declarative lifecycle management.",
        )
    ],
)

enrich_file(
    Path("exercises/14_kuberay/kuberay02.py"),
    topic="RayJob CRD & Ephemeral Batch Execution",
    context_why="""
For batch ML workflows, maintaining static clusters is expensive.
The `RayJob` CRD creates an ephemeral Ray cluster, submits your job script, streams logs, and
automatically deletes the worker pods upon job completion.
""",
    instructions=[
        "Author a `RayJob` specification with shutdown policies.",
        "Verify job lifecycle transitions.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure RayJob CRD",
            "# TODO: Configure RayJob CRD\n    # WHY: RayJob CRD automates ephemeral cluster creation and automatic teardown for cost efficiency.",
        )
    ],
)

enrich_file(
    Path("exercises/14_kuberay/kuberay03.py"),
    topic="RayService CRD & Zero-Downtime Serving",
    context_why="""
`RayService` CRD manages Ray Serve deployments on Kubernetes, providing rolling upgrades, health probes,
and zero-downtime traffic switching across cluster upgrades.
""",
    instructions=[
        "Author a `RayService` CRD spec.",
        "Verify multi-deployment service definitions.",
    ],
    todo_replacements=[
        (
            "# TODO: Author RayService spec",
            "# TODO: Author RayService spec\n    # WHY: RayService ensures high-availability and zero-downtime upgrades on Kubernetes.",
        )
    ],
)

enrich_file(
    Path("exercises/14_kuberay/kuberay04.py"),
    topic="Autoscaling with KEDA & Ray Autoscaler",
    context_why="""
Kubernetes Event-driven Autoscaling (KEDA) scales KubeRay worker pods based on queue depth, Prometheus metrics,
or Ray autoscaler demands, dynamically adapting Kubernetes capacity to real-time workload spikes.
""",
    instructions=[
        "Configure autoscaler scaling policies and min/max worker replicas.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure KubeRay autoscaling",
            "# TODO: Configure KubeRay autoscaling\n    # WHY: Dynamic autoscaling provisions worker pods on-demand to meet queue pressure.",
        )
    ],
)

enrich_file(
    Path("exercises/14_kuberay/kuberay05.py"),
    topic="Kubernetes Fault Tolerance & Pod Evictions",
    context_why="""
In Kubernetes, worker pods can be evicted due to node drain, out-of-memory (OOMKilled), or spot preemption.
KubeRay coordinates with Ray's GCS to re-spawn replacement pods and reconstruct lost state.
""",
    instructions=[
        "Handle simulated pod eviction and verify cluster recovery.",
    ],
    todo_replacements=[
        (
            "# TODO: Verify pod eviction resilience",
            "# TODO: Verify pod eviction resilience\n    # WHY: KubeRay detects terminated worker pods and provisions replacements automatically.",
        )
    ],
)

# ==================== CHAPTER 15: VLLM & LLMS ====================

enrich_file(
    Path("exercises/15_vllm_and_llms/vllm01.py"),
    topic="Tensor Parallelism & Ray Worker Actor Groups",
    context_why="""
Large Language Models (e.g. 70B parameters) exceed single-GPU memory.
**Tensor Parallelism (TP)** shards linear projection matrices across multiple Ray worker actors:
- `ColumnParallelLinear` splits weight matrix columns across workers.
- `RowParallelLinear` splits weight rows and performs an All-Reduce sum across workers.
""",
    instructions=[
        "Implement sharded linear forward passes across 2 Ray worker actors.",
        "Perform All-Reduce sum and assert mathematical equivalence to single-actor baseline.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement tensor parallel forward pass",
            "# TODO: Implement tensor parallel forward pass\n    # WHY: Tensor parallelism splits hidden dimension projections across actors to fit large LLMs in memory.",
        )
    ],
)

enrich_file(
    Path("exercises/15_vllm_and_llms/vllm02.py"),
    topic="PagedAttention & KV-Cache Block Management",
    context_why="""
Standard autoregressive generation suffers from severe GPU memory fragmentation due to dynamic sequence lengths.
**PagedAttention** (pioneered by vLLM) allocates Key-Value (KV) cache in non-contiguous physical blocks,
using a logical-to-physical block table (similar to OS virtual memory paging).
""",
    instructions=[
        "Implement dynamic physical block allocation and logical block table mapping.",
        "Verify prefix block sharing across prompts.",
    ],
    todo_replacements=[
        (
            "# TODO: Allocate KV cache block tables",
            "# TODO: Allocate KV cache block tables\n    # WHY: PagedAttention eliminates memory fragmentation by allocating fixed-size physical memory pages.",
        )
    ],
)

enrich_file(
    Path("exercises/15_vllm_and_llms/vllm03.py"),
    topic="Dynamic Multi-LoRA Adapter Serving",
    context_why="""
Serving hundreds of fine-tuned domain models simultaneously by loading separate base models is impossible.
**Multi-LoRA serving** keeps one shared base model in memory, dynamically applying low-rank adapter matrices
($A \times B$) per request with LRU cache eviction.
""",
    instructions=[
        "Implement dynamic LoRA adapter dispatch and forward computation.",
        "Verify multi-tenant adapter outputs.",
    ],
    todo_replacements=[
        (
            "# TODO: Apply LoRA adapter forward pass",
            "# TODO: Apply LoRA adapter forward pass\n    # WHY: Multi-LoRA serves customized fine-tuned models over a single shared base model instance.",
        )
    ],
)

enrich_file(
    Path("exercises/15_vllm_and_llms/vllm04.py"),
    topic="Speculative Decoding with Draft & Target Workers",
    context_why="""
LLM token generation is memory-bandwidth bound.
**Speculative Decoding** uses a fast draft model to generate $K$ candidate tokens cheaply,
and a large target model to verify all $K$ tokens in parallel in a single forward pass,
achieving 2-3x latency reduction.
""",
    instructions=[
        "Implement draft generation and parallel target verification loop.",
        "Verify exact sequence matching.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement speculative verification loop",
            "# TODO: Implement speculative verification loop\n    # WHY: Speculative decoding verifies multiple tokens in a single target pass to boost generation speed.",
        )
    ],
)

# ==================== CHAPTER 16: FSDP & DEEPSPEED ====================

enrich_file(
    Path("exercises/16_fsdp_and_deepspeed/fsdp01.py"),
    topic="PyTorch FSDP with Ray Train ScalingConfig",
    context_why="""
PyTorch Fully Sharded Data Parallel (FSDP) shards model parameters, gradients, and optimizer states
across data-parallel workers. Ray Train coordinates the multi-worker cluster and wraps modules with
FSDP auto-wrapping policies.
""",
    instructions=[
        "Configure FSDP wrapping and Ray Train `TorchTrainer`.",
        "Verify parameter sharding and loss convergence across workers.",
    ],
    todo_replacements=[
        (
            "# TODO: Wrap model with FSDP",
            "# TODO: Wrap model with FSDP\n    # WHY: FSDP shards model layers across workers, reducing per-GPU memory consumption proportionally to worker count.",
        )
    ],
)

enrich_file(
    Path("exercises/16_fsdp_and_deepspeed/fsdp02.py"),
    topic="DeepSpeed ZeRO-1 / ZeRO-2 / ZeRO-3 Memory Partitioning",
    context_why="""
DeepSpeed Zero Redundancy Optimizer (ZeRO) partitions memory:
- **ZeRO-1**: Partitions optimizer states (4x memory reduction).
- **ZeRO-2**: Partitions optimizer states + gradients (8x memory reduction).
- **ZeRO-3**: Partitions optimizer states + gradients + model parameters (linear scaling with world size).
""",
    instructions=[
        "Simulate ZeRO memory partitioning and AllGather / ReduceScatter actor communication.",
        "Verify memory reduction per ZeRO stage.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement ZeRO communication",
            "# TODO: Implement ZeRO communication\n    # WHY: ZeRO partitions state and streams parameters via AllGather and ReduceScatter collective operations.",
        )
    ],
)

enrich_file(
    Path("exercises/16_fsdp_and_deepspeed/fsdp03.py"),
    topic="Mixed Precision & Activation Checkpointing",
    context_why="""
During backpropagation, saving intermediate activations for large transformer layers consumes massive memory.
**Activation Checkpointing** discards activations during the forward pass and recomputes them during backward,
saving up to 60% activation memory at minimal compute cost.
""",
    instructions=[
        "Wrap transformer layers with activation checkpointing and mixed precision autocasting.",
        "Verify memory savings.",
    ],
    todo_replacements=[
        (
            "# TODO: Apply activation checkpointing",
            "# TODO: Apply activation checkpointing\n    # WHY: Activation checkpointing trades minimal recomputation for substantial memory savings.",
        )
    ],
)

enrich_file(
    Path("exercises/16_fsdp_and_deepspeed/fsdp04.py"),
    topic="Elastic Fault-Tolerant Distributed Checkpoints",
    context_why="""
Saving multi-terabyte checkpoints to a single file causes I/O bottlenecks.
Distributed Checkpointing saves sharded state dictionaries in parallel across all worker ranks,
with atomic metadata enabling elastic resumption if world size changes.
""",
    instructions=[
        "Implement distributed sharded state saving and fault recovery.",
    ],
    todo_replacements=[
        (
            "# TODO: Save sharded checkpoint",
            "# TODO: Save sharded checkpoint\n    # WHY: Distributed sharded checkpoints write rank-specific slices in parallel to maximize storage bandwidth.",
        )
    ],
)

# ==================== CHAPTER 17: MULTIMODAL & VECTORS ====================

enrich_file(
    Path("exercises/17_multimodal_and_vectors/data_genai01.py"),
    topic="Streaming Multimodal Image & Audio ETL",
    context_why="""
Multimodal pipelines process heterogeneous tensors (images, spectrograms, text).
Ray Data leverages PyArrow tensor extension types to stream and transform multimodal datasets
with zero-copy memory mapping and bounded memory usage.
""",
    instructions=[
        "Process multimodal records with PyArrow tensor extensions.",
        "Verify streaming batch throughput.",
    ],
    todo_replacements=[
        (
            "# TODO: Stream multimodal batches",
            "# TODO: Stream multimodal batches\n    # WHY: PyArrow tensor extensions enable zero-copy processing of high-dimensional image/audio arrays.",
        )
    ],
)

enrich_file(
    Path("exercises/17_multimodal_and_vectors/data_genai02.py"),
    topic="Accelerated Batch Embeddings with ActorPoolStrategy",
    context_why="""
Extracting vector embeddings from millions of documents requires persistent neural encoder models.
`dataset.map_batches(Encoder, compute=ActorPoolStrategy(min_size=2))` keeps embedding models loaded
in worker memory, streaming documents through GPU/CPU encoder pools.
""",
    instructions=[
        "Implement batch embedding extractor with `ActorPoolStrategy`.",
        "Verify embedding generation and normalization.",
    ],
    todo_replacements=[
        (
            "# TODO: Extract embeddings with ActorPoolStrategy",
            "# TODO: Extract embeddings with ActorPoolStrategy\n    # WHY: ActorPoolStrategy prevents reloading heavy transformer models between batch iterations.",
        )
    ],
)

enrich_file(
    Path("exercises/17_multimodal_and_vectors/data_genai03.py"),
    topic="Dynamic Token Length Bucketing & Padding Optimization",
    context_why="""
Padding all text sequences in a batch to the global maximum length wastes massive compute on padding tokens.
**Length Bucketing** clusters sequences of similar lengths into the same mini-batch, minimizing padding overhead.
""",
    instructions=[
        "Implement length bucketing on variable-length text records.",
        "Verify reduced padding token counts.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement length bucketing",
            "# TODO: Implement length bucketing\n    # WHY: Dynamic bucketing minimizes padding tokens to maximize tensor computing efficiency.",
        )
    ],
)

enrich_file(
    Path("exercises/17_multimodal_and_vectors/data_genai04.py"),
    topic="Streaming Parallel Ingestion into Vector Databases",
    context_why="""
Ingesting billions of vectors into vector stores (Milvus, Qdrant, Pinecone) requires high-throughput parallel writers.
Custom Ray Data `Datasink` classes stream and write vector partitions in parallel across worker nodes.
""",
    instructions=[
        "Implement custom vector store `Datasink`.",
        "Stream embeddings into partitioned vector index.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement vector Datasink",
            "# TODO: Implement vector Datasink\n    # WHY: Custom Datasink classes parallelize partition writes across cluster nodes directly to vector indices.",
        )
    ],
)

# ==================== CHAPTER 18: QUANT FINANCE ====================

enrich_file(
    Path("exercises/18_quant_finance/finance01.py"),
    topic="Distributed Monte Carlo Black-Scholes Option Pricing",
    context_why="""
Quantitative finance relies heavily on Monte Carlo simulations to price exotic derivatives.
Simulating millions of Geometric Brownian Motion (GBM) price paths across Ray worker tasks
achieves linear scaling and near-instant pricing.
""",
    instructions=[
        "Implement distributed Monte Carlo simulation across Ray tasks.",
        "Aggregate discounted payoff estimates and verify pricing accuracy against analytical Black-Scholes.",
    ],
    todo_replacements=[
        (
            "# TODO: Price option via distributed Monte Carlo",
            "# TODO: Price option via distributed Monte Carlo\n    # WHY: Monte Carlo simulation paths are embarrassingly parallel and scale linearly across Ray workers.",
        )
    ],
)

enrich_file(
    Path("exercises/18_quant_finance/finance02.py"),
    topic="Portfolio Value at Risk (VaR) & CVaR Stress Simulation",
    context_why="""
Risk management systems must calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR / Expected Shortfall)
across millions of historical market scenarios and multi-asset portfolios.
Ray distributes portfolio stress simulations across workers, aggregating loss distributions.
""",
    instructions=[
        "Simulate correlated portfolio returns across Ray tasks.",
        "Compute empirical 95% and 99% VaR and CVaR metrics.",
    ],
    todo_replacements=[
        (
            "# TODO: Compute VaR and CVaR",
            "# TODO: Compute VaR and CVaR\n    # WHY: Distributed scenario simulations allow real-time portfolio risk assessments under market shock conditions.",
        )
    ],
)

enrich_file(
    Path("exercises/18_quant_finance/finance03.py"),
    topic="Streaming Market Tick Analytics & Rolling VWAP",
    context_why="""
High-frequency trading systems process millions of market tick events per second.
Ray Data streaming pipelines ingest trade ticks and compute continuous Volume-Weighted Average Price (VWAP)
across partitioned equity tickers with bounded memory.
""",
    instructions=[
        "Implement Ray Data streaming pipeline for tick ingestion.",
        "Calculate rolling VWAP per instrument symbol.",
    ],
    todo_replacements=[
        (
            "# TODO: Compute rolling VWAP stream",
            "# TODO: Compute rolling VWAP stream\n    # WHY: Streaming Ray Data pipelines process tick data continuously without driver memory bottlenecks.",
        )
    ],
)

print("Chapters 13 to 18 enriched successfully!")
