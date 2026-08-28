from pathlib import Path

from scripts.enrich_all_exercises import enrich_file

# ==================== CHAPTER 07: PATTERNS & ANTI-PATTERNS ====================

enrich_file(
    Path("exercises/07_patterns_and_antipatterns/antipattern01.py"),
    topic="Nested ray.get() Bottlenecks & Driver Stalls",
    context_why="""
A frequent performance hazard in distributed architectures is calling `ray.get()` inside a remote
task or worker function. When worker tasks synchronously block on other tasks with `ray.get()`,
they hold worker process slots hostage, leading to thread starvation, high latency, and deadlocks.

The recommended pattern is passing `ObjectRef`s directly to downstream tasks to form a pure DAG,
allowing Ray's C++ scheduler to orchestrate execution asynchronously without worker stalls.
""",
    instructions=[
        "Identify and eliminate the nested `ray.get()` call inside the remote worker.",
        "Pass ObjectRefs directly to construct a streamlined execution DAG.",
    ],
    todo_replacements=[
        (
            "# TODO: Refactor to eliminate nested ray.get()",
            "# TODO: Refactor to eliminate nested ray.get()\n    # WHY: Calling ray.get() inside worker tasks ties up execution threads and prevents parallel scheduling.",
        )
    ],
)

enrich_file(
    Path("exercises/07_patterns_and_antipatterns/antipattern02.py"),
    topic="Micro-Task Chunking & Batching",
    context_why="""
Ray's task scheduler is extraordinarily fast (sub-millisecond latency), but scheduling 1,000,000
individual tasks that each compute for 1 microsecond results in scheduling and serialization overhead
vastly exceeding the actual computation time.

To achieve maximum throughput, fine-grained tasks should be chunked into coarse batches (e.g.,
processing 1,000 items per task invocation), amortizing scheduling overhead.
""",
    instructions=[
        "Group fine-grained items into batches before submitting remote tasks.",
        "Verify that batching significantly reduces total execution time.",
    ],
    todo_replacements=[
        (
            "# TODO: Batch items into chunks",
            "# TODO: Batch items into chunks\n    # WHY: Task chunking amortizes scheduling and serialization latency across millions of fine-grained items.",
        )
    ],
)

enrich_file(
    Path("exercises/07_patterns_and_antipatterns/antipattern03.py"),
    topic="Actor Bottleneck Elimination via Sharding",
    context_why="""
Because a single Ray actor executes method calls sequentially, routing high-throughput traffic
from 100 workers to a single centralized actor creates a severe serialization bottleneck.

Sharding the actor state across an Actor Pool or partitioning keys across multiple independent actors
allows concurrent reads and writes, achieving horizontal scalability.
""",
    instructions=[
        "Partition workloads across a pool of shard actors instead of a single bottleneck actor.",
        "Verify throughput gains.",
    ],
    todo_replacements=[
        (
            "# TODO: Shard actor state",
            "# TODO: Shard actor state\n    # WHY: Sharding eliminates single-actor mailbox contention and unlocks multi-core parallelism.",
        )
    ],
)

enrich_file(
    Path("exercises/07_patterns_and_antipatterns/antipattern04.py"),
    topic="Tree-Structured Distributed Aggregation",
    context_why=r"""
Aggregating $N$ items on a single driver process with `sum(ray.get(refs))` requires transferring all
$N$ results back to the driver's memory, creating an $O(N)$ network and memory bottleneck.

A **Tree Aggregate** recursively pairs and reduces intermediate results across distributed workers in
$\log_k(N)$ steps. The driver only ever receives the single final scalar result.
""",
    instructions=[
        "Implement a recursive tree reduction using `@ray.remote` aggregator tasks.",
        r"Verify $O(\log N)$ aggregation depth.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement tree reduction",
            "# TODO: Implement tree reduction\n    # WHY: Tree reduction distributes intermediate aggregations across cluster nodes, avoiding driver memory saturation.",
        )
    ],
)

# ==================== CHAPTER 08: RAY DATA ====================

enrich_file(
    Path("exercises/08_ray_data/data01.py"),
    topic="Ray Data Ingestion & Block Partitioning",
    context_why="""
Ray Data is a scalable, distributed data processing engine designed for ML datasets.
Datasets in Ray Data are partitioned into **Blocks** (backed by Apache Arrow tables).
Each block is stored in the Plasma object store and processed independently across workers.

Controlling block count (`override_num_blocks`) ensures balanced parallelism and prevents memory spills.
""",
    instructions=[
        "Create a Ray Dataset using `ray.data.from_items()` or `read_parquet()`.",
        "Inspect block partitioning, schema, and dataset count.",
    ],
    todo_replacements=[
        (
            "# TODO: Create and partition Ray Dataset",
            "# TODO: Create and partition Ray Dataset\n    # WHY: Ray Data partitions collections into Apache Arrow blocks for distributed vectorized processing.",
        )
    ],
)

enrich_file(
    Path("exercises/08_ray_data/data02.py"),
    topic="Vectorized Batch Transformations with map_batches",
    context_why="""
Processing items row-by-row in Python (`map()`) incurs heavy per-row interpretation overhead.
`map_batches(fn, batch_format=\"pyarrow\" | \"numpy\" | \"pandas\")` passes zero-copy columnar chunks
to your transformation function, allowing vectorized SIMD execution via NumPy and PyArrow C-libraries.
""",
    instructions=[
        "Apply `map_batches` with vectorized NumPy / PyArrow transformations.",
        "Verify throughput improvements over row-wise operations.",
    ],
    todo_replacements=[
        (
            "# TODO: Apply map_batches",
            "# TODO: Apply map_batches\n    # WHY: map_batches operates on zero-copy columnar Arrow batches to achieve maximum throughput.",
        )
    ],
)

enrich_file(
    Path("exercises/08_ray_data/data03.py"),
    topic="Stateful Batch Inference with ActorPoolStrategy",
    context_why="""
When performing batch inference with neural networks or heavy ML models, re-initializing the model
inside every task is prohibitively slow.

Passing `compute=ray.data.ActorPoolStrategy(min_size=N, max_size=M)` to `map_batches()` creates
a persistent pool of actor workers that keep model weights pinned in GPU/CPU memory across stream batches.
""",
    instructions=[
        "Define an inference class with a `__call__` method.",
        "Execute `map_batches(InferenceClass, compute=ActorPoolStrategy(min_size=2))`.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure ActorPoolStrategy for batch inference",
            "# TODO: Configure ActorPoolStrategy for batch inference\n    # WHY: ActorPoolStrategy retains instantiated models in worker memory across multiple data batches.",
        )
    ],
)

enrich_file(
    Path("exercises/08_ray_data/data04.py"),
    topic="Streaming Backpressure & Bounded Memory Windows",
    context_why="""
When reading a 10TB dataset, loading all data into memory at once causes Out-Of-Memory (OOM) crashes.
Ray Data streams blocks through an execution pipeline using **dynamic backpressure**:
upstream operators only produce new blocks when downstream operators have capacity to consume them.
""",
    instructions=[
        "Configure bounded streaming windows and iterate through dataset batches without memory explosion.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure streaming execution",
            "# TODO: Configure streaming execution\n    # WHY: Streaming backpressure ensures peak memory stays within fixed bounds regardless of total dataset size.",
        )
    ],
)

enrich_file(
    Path("exercises/08_ray_data/data05.py"),
    topic="PyTorch DataLoader Interoperability",
    context_why="""
Ray Data provides seamless zero-copy streaming into distributed PyTorch training loops via
`dataset.iter_torch_batches(batch_size=B, prefetch_batches=P)`.

This replaces standard PyTorch `DataLoader` with multi-node distributed streaming, prefetching, and sharding.
""",
    instructions=[
        "Convert a Ray Dataset into PyTorch tensors using `iter_torch_batches()`.",
        "Iterate batches in a simulated training loop.",
    ],
    todo_replacements=[
        (
            "# TODO: Stream PyTorch batches",
            "# TODO: Stream PyTorch batches\n    # WHY: iter_torch_batches yields PyTorch tensors directly from Arrow blocks with background prefetching.",
        )
    ],
)

# ==================== CHAPTER 09: ML FROM SCRATCH ====================

enrich_file(
    Path("exercises/09_ml_from_scratch/ml_scratch01.py"),
    topic="Synchronous Parameter Server Architecture",
    context_why="""
The **Parameter Server** pattern is a foundational distributed machine learning architecture.
A centralized `ParameterServer` actor holds global model weights. Multiple stateless `Worker` tasks
fetch the latest weights, compute gradients on local data batches, and send gradients back.

In the **Synchronous** variant, the server waits for gradients from ALL workers before applying
an optimizer step, ensuring mathematical equivalence to large-batch SGD.
""",
    instructions=[
        "Implement `ParameterServer` actor and distributed `Worker` gradient computation tasks.",
        "Implement synchronous barrier update.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement synchronous parameter server",
            "# TODO: Implement synchronous parameter server\n# WHY: Synchronous parameter updates guarantee consistent model state across all worker iterations.",
        )
    ],
)

enrich_file(
    Path("exercises/09_ml_from_scratch/ml_scratch02.py"),
    topic="Asynchronous Parameter Server Architecture (Hogwild!)",
    context_why="""
In heterogeneous clusters where workers have differing speeds, synchronous parameter updates suffer
from the **straggler problem** (fast workers sit idle waiting for the slowest worker).

In **Asynchronous Parameter Servers**, workers pull weights and push gradients independently
without waiting for peers. While gradients may be slightly stale, total training throughput is maximized.
""",
    instructions=[
        "Implement asynchronous non-blocking gradient updates on the parameter server.",
        "Verify convergence under asynchronous updates.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement asynchronous gradient updates",
            "# TODO: Implement asynchronous gradient updates\n# WHY: Asynchronous updates eliminate worker idle time by allowing workers to compute continuously.",
        )
    ],
)

enrich_file(
    Path("exercises/09_ml_from_scratch/ml_scratch03.py"),
    topic="Ring All-Reduce Distributed Gradient Synchronization",
    context_why="""
In large-scale distributed training, centralized parameter servers become network bottlenecks.
**Ring All-Reduce** (used by NCCL and Horovod) arranges $N$ workers in a logical ring.
Each worker only communicates with its immediate neighbor, reducing gradients in $2(N-1)$ ring transfers.

Total communication volume per worker is independent of cluster size $N$, enabling linear scaling.
""",
    instructions=[
        "Implement a Ring All-Reduce exchange across Ray worker actors.",
        "Verify that all workers reach synchronized gradient consensus.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement Ring All-Reduce step",
            "# TODO: Implement Ring All-Reduce step\n# WHY: Ring All-Reduce achieves optimal $O(1)$ communication bandwidth per worker regardless of cluster size.",
        )
    ],
)

enrich_file(
    Path("exercises/09_ml_from_scratch/ml_scratch04.py"),
    topic="Distributed Data-Parallel Linear Regression Trainer",
    context_why="""
Combining Ray tasks, actors, and object store primitives allows building complete end-to-end
data-parallel training pipelines from scratch without external ML frameworks.
""",
    instructions=[
        "Build a distributed data-parallel linear regression trainer.",
        "Verify loss convergence on synthetic regression data.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement distributed trainer",
            "# TODO: Implement distributed trainer\n# WHY: Data parallelism shards training samples across workers while synchronizing model parameters.",
        )
    ],
)

# ==================== CHAPTER 10: RAY TRAIN ====================

enrich_file(
    Path("exercises/10_ray_train_and_tune/train01.py"),
    topic="TorchTrainer & ScalingConfig Distributed PyTorch",
    context_why="""
`ray.train.torch.TorchTrainer` provides native orchestration for PyTorch Distributed Data Parallel (DDP).
`ScalingConfig(num_workers=2, use_gpu=False)` coordinates worker processes, sets up `torch.distributed`
process groups (NCCL/Gloo), and handles rank assignments automatically.
""",
    instructions=[
        "Define a distributed training function.",
        "Instantiate `TorchTrainer` with `ScalingConfig(num_workers=2)` and execute `trainer.fit()`.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure TorchTrainer",
            "# TODO: Configure TorchTrainer\n    # WHY: TorchTrainer sets up distributed process groups and coordinates rank initialization across nodes.",
        )
    ],
)

enrich_file(
    Path("exercises/10_ray_train_and_tune/train02.py"),
    topic="Distributed Dataset Sharding in Ray Train",
    context_why="""
In DDP training, each worker rank must only process its assigned shard of data to prevent redundant gradient computations.
`ray.train.torch.prepare_data_loader(loader)` or `ray.train.get_dataset_shard(\"train\")` automatically
partitions data across ranks with zero manual math.
""",
    instructions=[
        "Shard dataset across training workers using Ray Train data APIs.",
        "Verify each worker receives unique data partitions.",
    ],
    todo_replacements=[
        (
            "# TODO: Shard dataset across ranks",
            "# TODO: Shard dataset across ranks\n    # WHY: Dataset sharding ensures non-overlapping mini-batches are delivered to each DDP worker.",
        )
    ],
)

enrich_file(
    Path("exercises/10_ray_train_and_tune/train03.py"),
    topic="Distributed Metrics Reporting & Checkpoint Persistence",
    context_why="""
`ray.train.report(metrics={\"loss\": loss}, checkpoint=checkpoint)` streams training loss/accuracy
to the driver and saves distributed model checkpoints to cloud or shared storage without blocking the training loop.
""",
    instructions=[
        "Call `ray.train.report` with epoch loss and PyTorch model state dictionary.",
        "Verify checkpoints are persisted.",
    ],
    todo_replacements=[
        (
            "# TODO: Report metrics and checkpoints",
            "# TODO: Report metrics and checkpoints\n    # WHY: ray.train.report synchronizes metrics with the driver and uploads atomic model checkpoints.",
        )
    ],
)

enrich_file(
    Path("exercises/10_ray_train_and_tune/train04.py"),
    topic="Fault-Tolerant Training & Elastic Worker Recovery",
    context_why="""
When training deep neural networks for days on spot instances, worker preemption is inevitable.
Ray Train integrates with `RunConfig(failure_config=FailureConfig(max_failures=3))` to automatically
re-provision failed workers and resume training from the latest valid checkpoint.
""",
    instructions=[
        "Configure failure recovery in `RunConfig`.",
        "Simulate worker failure and verify seamless training resumption.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure fault recovery",
            "# TODO: Configure fault recovery\n    # WHY: Automated recovery restores model weights from the last valid checkpoint without restarting from epoch 0.",
        )
    ],
)

# ==================== CHAPTER 11: RAY TUNE ====================

enrich_file(
    Path("exercises/11_ray_tune/tune01.py"),
    topic="Ray Tune Search Spaces & Distributed Grid Search",
    context_why="""
Hyperparameter tuning is embarrassingly parallel. Ray Tune manages distributed trials across cluster nodes.
Defining search spaces with `tune.choice()`, `tune.uniform()`, or `tune.loguniform()` allows exploring
hyperparameters with maximum concurrency.
""",
    instructions=[
        "Define a hyperparameter search space.",
        "Run `Tuner.fit()` and inspect the best trial hyperparameters.",
    ],
    todo_replacements=[
        (
            "# TODO: Define search space and Tuner",
            "# TODO: Define search space and Tuner\n    # WHY: Tuner coordinates parallel trial execution across available cluster cores.",
        )
    ],
)

enrich_file(
    Path("exercises/11_ray_tune/tune02.py"),
    topic="ASHA Early Stopping Trial Scheduler",
    context_why="""
Training unpromising hyperparameter configurations to completion wastes massive compute resources.
The **Asynchronous Successive Halving Algorithm (ASHA)** aggressively terminates underperforming trials
early, reallocating compute to the top-performing configurations.
""",
    instructions=[
        'Configure `ASHAScheduler(metric="loss", mode="min", grace_period=1)`.',
        "Verify early termination of poor trials.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure ASHAScheduler",
            "# TODO: Configure ASHAScheduler\n    # WHY: ASHA scheduler prunes bottom-quartile trials early, saving over 70% of compute time.",
        )
    ],
)

enrich_file(
    Path("exercises/11_ray_tune/tune03.py"),
    topic="Population-Based Training (PBT)",
    context_why="""
**Population-Based Training (PBT)** dynamically explores hyperparameters while training a population
of neural networks simultaneously. Underperforming networks periodically replace their weights with
top-performing networks ('exploit') and mutate their hyperparameters ('explore').
""",
    instructions=[
        "Configure `PopulationBasedTraining` scheduler.",
        "Verify parameter mutation during trial evolution.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure PopulationBasedTraining",
            "# TODO: Configure PopulationBasedTraining\n    # WHY: PBT optimizes dynamic schedules (e.g. learning rate schedules) by evolving models in real time.",
        )
    ],
)

# ==================== CHAPTER 12: RAY SERVE ====================

enrich_file(
    Path("exercises/12_ray_serve/serve01.py"),
    topic="Ray Serve HTTP Deployment & Ingress",
    context_why="""
Ray Serve is a scalable model serving library built on Ray actors.
Decorating a class with `@serve.deployment` turns it into an autoscaling, HTTP-accessible microservice
with built-in request routing and load balancing.
""",
    instructions=[
        "Define a `@serve.deployment` class with `__call__(self, request)`.",
        "Deploy the application with `serve.run()` and query via HTTP client.",
    ],
    todo_replacements=[
        (
            "# TODO: Define serve deployment",
            "# TODO: Define serve deployment\n# WHY: @serve.deployment wraps classes in an HTTP endpoint managed by Ray Serve routers.",
        )
    ],
)

enrich_file(
    Path("exercises/12_ray_serve/serve02.py"),
    topic="Dynamic Dynamic Request Batching with @serve.batch",
    context_why="""
Machine learning models (especially GPUs) achieve peak throughput when processing batches rather than
single requests.
`@serve.batch(max_batch_size=8, batch_wait_timeout_s=0.05)` dynamically buffers individual incoming HTTP
requests into a single vectorized batch before passing it to the inference function.
""",
    instructions=[
        "Decorate inference method with `@serve.batch`.",
        "Send multiple concurrent requests and verify they are processed in batches.",
    ],
    todo_replacements=[
        (
            "# TODO: Decorate with @serve.batch",
            "# TODO: Decorate with @serve.batch\n    # WHY: @serve.batch buffers incoming single HTTP calls into vectorized batches for GPU acceleration.",
        )
    ],
)

enrich_file(
    Path("exercises/12_ray_serve/serve03.py"),
    topic="Multi-Model Pipeline DAGs in Ray Serve",
    context_why="""
Production AI applications rarely consist of a single model; they chain text preprocessing,
tokenization, multiple neural models, and postprocessing.
Ray Serve allows composing deployments into a Direct Acyclic Graph (DAG) with type-safe deployment handles.
""",
    instructions=[
        "Build a pipeline connecting an Ingestion deployment to an Inference deployment.",
        "Route requests through the deployment graph.",
    ],
    todo_replacements=[
        (
            "# TODO: Chain multi-deployment pipeline",
            "# TODO: Chain multi-deployment pipeline\n    # WHY: Composing deployments into DAGs enables modular scaling of individual pipeline stages.",
        )
    ],
)

enrich_file(
    Path("exercises/12_ray_serve/serve04.py"),
    topic="Autoscaling & Replica Dynamics in Ray Serve",
    context_why="""
Traffic spikes require rapid horizontal scaling of model replicas.
`autoscaling_config={\"min_replicas\": 1, \"max_replicas\": 5, \"target_ongoing_requests\": 2}`
instructs Ray Serve controller to monitor queue depth and scale replica actors automatically.
""",
    instructions=[
        "Configure `autoscaling_config` on a deployment.",
        "Verify dynamic replica scaling under simulated request load.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure autoscaling_config",
            "# TODO: Configure autoscaling_config\n# WHY: Autoscaling adapts replica count to incoming traffic volume to maintain latency SLAs.",
        )
    ],
)

enrich_file(
    Path("exercises/12_ray_serve/serve05.py"),
    topic="Streaming LLM Token Responses via Async Generators",
    context_why="""
For Large Language Models (LLMs), waiting for the entire sequence to generate creates high Time-To-First-Token (TTFT)
latency for users.
Ray Serve supports streaming HTTP responses using Python `async def` generators and `StreamingResponse`.
""",
    instructions=[
        "Implement an async generator deployment yielding token chunks.",
        "Stream chunks to client in real time.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement streaming deployment",
            "# TODO: Implement streaming deployment\n    # WHY: Async generators enable streaming LLM tokens incrementally to minimize user perceived latency.",
        )
    ],
)

print("Chapters 07 to 12 enriched successfully!")
