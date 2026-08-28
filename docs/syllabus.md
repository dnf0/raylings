# Complete Curriculum Syllabus 📚

The Raylings curriculum consists of **18 comprehensive chapters** containing **81 hands-on exercises**. The syllabus is designed to take you from core distributed primitives to production-scale AI training, serving, cloud-native Kubernetes orchestration, and quantitative domain applications.

---

## 🗺️ Curriculum Overview

| # | Chapter Identifier | Chapter Title | Exercises | Focus Area | Difficulty |
| :-: | :--- | :--- | :-: | :--- | :--- |
| **01** | [`01_basics`](#chapter-1-01_basics-ray-core-foundations) | **Ray Core Foundations** | 6 | Tasks, ObjectRefs, Asynchronous Execution | Beginner |
| **02** | [`02_actors`](#chapter-2-02_actors-distributed-state-actors) | **Distributed State & Actors** | 7 | Stateful Actors, Concurrency, Actor Pools | Beginner |
| **03** | [`03_object_store`](#chapter-3-03_object_store-plasma-object-store-zero-copy) | **Plasma Object Store & Zero-Copy** | 6 | Zero-Copy Reads, Memory Limits, Custom Serializers | Intermediate |
| **04** | [`04_scheduling_resources`](#chapter-4-04_scheduling_resources-resource-scheduling-placement-groups) | **Resource Scheduling & Placement Groups** | 6 | Fractional CPUs, SPREAD/PACK, Gang Scheduling | Intermediate |
| **05** | [`05_fault_tolerance`](#chapter-5-05_fault_tolerance-fault-tolerance-lineage-recovery) | **Fault Tolerance & Lineage Recovery** | 4 | Automatic Retries, Actor Restarts, DAG Recomputation | Intermediate |
| **06** | [`06_cluster_architecture`](#chapter-6-06_cluster_architecture-cluster-topology-multi-node-simulation) | **Cluster Topology & Simulation** | 4 | GCS, Multi-Node Simulation, Job Submission API | Intermediate |
| **07** | [`07_patterns_and_antipatterns`](#chapter-7-07_patterns_and_antipatterns-production-patterns-anti-patterns) | **Production Patterns & Anti-Patterns** | 4 | Avoiding Stalls, Micro-Task Batching, Tree-Reduce | Advanced |
| **08** | [`08_ray_data`](#chapter-8-08_ray_data-ray-data-for-high-throughput-etl) | **Ray Data for High-Throughput ETL** | 5 | Block Partitioning, PyArrow Vectorization, Streaming | Advanced |
| **09** | [`09_ml_from_scratch`](#chapter-9-09_ml_from_scratch-distributed-ml-primitives-from-scratch) | **Distributed ML Primitives from Scratch** | 4 | Parameter Servers, All-Reduce Ring, Data-Parallelism | Advanced |
| **10** | [`10_ray_train_and_tune`](#chapter-10-10_ray_train_and_tune-ray-train-distributed-deep-learning) | **Ray Train & Distributed Deep Learning** | 4 | TorchTrainer, ScalingConfig, Distributed Checkpointing | Advanced |
| **11** | [`11_ray_tune`](#chapter-11-11_ray_tune-scalable-hyperparameter-tuning) | **Ray Tune: Scalable Hyperparameter Tuning** | 3 | Search Spaces, ASHA Scheduler, Population-Based Training | Advanced |
| **12** | [`12_ray_serve`](#chapter-12-12_ray_serve-ray-serve-production-model-serving) | **Ray Serve & Production Model Serving** | 5 | HTTP Deployments, Request Batching, Pipeline DAGs | Advanced |
| **13** | [`13_observability_and_debugging`](#chapter-13-13_observability_and_debugging-observability-memory-debugging) | **Observability & Memory Debugging** | 3 | Chrome Timelines, Plasma Leak Profiling, State APIs | Expert |
| **14** | [`14_kuberay`](#chapter-14-14_kuberay-kuberay-cloud-native-ray-on-kubernetes) | **KubeRay & Cloud-Native Kubernetes** | 5 | RayCluster CRD, RayJob, RayService, KEDA Autoscaling | Expert |
| **15** | [`15_vllm_and_llms`](#chapter-15-15_vllm_and_llms-distributed-llm-serving-vllm) | **Distributed LLM Serving & vLLM** | 4 | Tensor Parallelism, PagedAttention, Multi-LoRA, Speculative Decoding | Expert |
| **16** | [`16_fsdp_and_deepspeed`](#chapter-16-16_fsdp_and_deepspeed-deepspeed-pytorch-fsdp) | **DeepSpeed & PyTorch FSDP** | 4 | Fully Sharded Data Parallel, ZeRO Memory Optimization, Fault Recovery | Expert |
| **17** | [`17_multimodal_and_vectors`](#chapter-17-17_multimodal_and_vectors-multimodal-vector-ray-data) | **Multimodal & Vector Ray Data** | 4 | Streaming Multimodal ETL, ActorPool Embeddings, Vector Stores | Expert |
| **18** | [`18_quant_finance`](#chapter-18-18_quant_finance-distributed-quantitative-finance) | **Distributed Quantitative Finance** | 3 | Monte Carlo Options, Historical VaR/CVaR, Streaming VWAP Analytics | Expert |

---

## 📖 Detailed Chapter Breakdown

### Chapter 1: `01_basics` - Ray Core Foundations

Covers the core primitives of distributed computing: converting synchronous Python functions into non-blocking asynchronous tasks, capturing futures, and managing data dependencies.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `basics01` | `exercises/01_basics/basics01.py` | **Ray Init & First Remote Task** — Initializing Ray with `ray.init()`, applying `@ray.remote`, and invoking via `.remote()`. |
| `basics02` | `exercises/01_basics/basics02.py` | **ObjectRefs & ray.get()** — Handling return futures (`ObjectRef`), blocking on results, and fetching batch references. |
| `basics03` | `exercises/01_basics/basics03.py` | **Parallel Pipeline Execution** — Eliminating serialization bottlenecks by launching tasks concurrently before blocking. |
| `basics04` | `exercises/01_basics/basics04.py` | **Passing ObjectRefs to Tasks** — Passing futures directly into downstream tasks without intermediate driver serialization. |
| `basics05` | `exercises/01_basics/basics05.py` | **Dynamic Completion with ray.wait()** — Processing tasks dynamically as they finish using `ray.wait()` loops. |
| `basics06` | `exercises/01_basics/basics06.py` | **Multiple Returns in Remote Tasks** — Returning multiple distinct `ObjectRef` handles using `num_returns=N`. |

---

### Chapter 2: `02_actors` - Distributed State & Actors

Covers stateful distributed objects (Actors), managing mutable internal state across processes, async concurrency, and worker pools.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `actors01` | `exercises/02_actors/actors01.py` | **Stateful Actor Lifecycle** — Defining `@ray.remote` classes, actor instantiation, and method scheduling. |
| `actors02` | `exercises/02_actors/actors02.py` | **Actor Method Calls & Mutation** — Mutating actor internal state across sequential remote method calls. |
| `actors03` | `exercises/02_actors/actors03.py` | **Passing Actor Handles** — Sharing actor handles across multiple worker tasks for centralized state coordination. |
| `actors04` | `exercises/02_actors/actors04.py` | **Async Actors & Coroutine Concurrency** — Using `async def` methods and `max_concurrency` for async I/O actors. |
| `actors05` | `exercises/02_actors/actors05.py` | **Threaded Actors for Blocking I/O** — Utilizing threaded actor pools to execute blocking C-extensions or network calls. |
| `actors06` | `exercises/02_actors/actors06.py` | **Detached Named Actors** — Registering persistent actors that survive driver disconnection (`lifetime="detached"`). |
| `actors07` | `exercises/02_actors/actors07.py` | **ActorPool Dynamic Load Balancing** — Managing elastic worker pools with `ray.util.ActorPool`. |

---

### Chapter 3: `03_object_store` - Plasma Object Store & Zero-Copy

Covers Ray's shared-memory Plasma object store, zero-copy deserialization semantics, memory bounds, and custom object serializers.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `object_store01` | `exercises/03_object_store/object_store01.py` | **Zero-Copy Plasma Reads** — Reading shared-memory NumPy and PyArrow buffers without memory duplication. |
| `object_store02` | `exercises/03_object_store/object_store02.py` | **ray.put() vs Implicit Serialization** — Pre-allocating shared objects to prevent redundant driver broadcasts. |
| `object_store03` | `exercises/03_object_store/object_store03.py` | **Object Immutability Semantics** — Understanding read-only buffer constraints (`flags.writeable == False`) and safe copies. |
| `object_store04` | `exercises/03_object_store/object_store04.py` | **Object Spilling & Memory Limits** — Managing bounded Plasma capacity and automatic NVMe/disk spilling. |
| `object_store05` | `exercises/03_object_store/object_store05.py` | **Nested ObjectRefs** — Resolving nested references (`ObjectRef[ObjectRef[T]]`) in complex pipelines. |
| `object_store06` | `exercises/03_object_store/object_store06.py` | **Custom Serializers with ray.util** — Registering optimized serializer/deserializer functions with `register_serializer`. |

---

### Chapter 4: `04_scheduling_resources` - Resource Scheduling & Placement Groups

Covers resource requirements, custom hardware constraints, node affinity, placement groups (PACK/SPREAD), and dynamic runtime environments.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `scheduling01` | `exercises/04_scheduling_resources/scheduling01.py` | **Fractional & Custom Resources** — Requesting fractional cores (`num_cpus=0.5`) and custom accelerators. |
| `scheduling02` | `exercises/04_scheduling_resources/scheduling02.py` | **Node Affinity Scheduling** — Pinning critical workloads using `NodeAffinitySchedulingStrategy`. |
| `scheduling03` | `exercises/04_scheduling_resources/scheduling03.py` | **Placement Groups: SPREAD** — Distributing worker bundles across distinct nodes for failure isolation. |
| `scheduling04` | `exercises/04_scheduling_resources/scheduling04.py` | **Placement Groups: PACK** — Co-locating latency-sensitive workers onto the same physical node. |
| `scheduling05` | `exercises/04_scheduling_resources/scheduling05.py` | **Gang Scheduling Multi-Bundle** — Atomic resource reservation requiring all bundles ready before job dispatch. |
| `scheduling06` | `exercises/04_scheduling_resources/scheduling06.py` | **Dynamic Runtime Environments** — Isolating dependencies with `runtime_env={"pip": [...], "env_vars": {...}}`. |

---

### Chapter 5: `05_fault_tolerance` - Fault Tolerance & Lineage Recovery

Covers automatic failure recovery, task retries, actor reconstruction, and lineage recomputation on preemption.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `fault01` | `exercises/05_fault_tolerance/fault01.py` | **Automatic Task Retries** — Configuring `max_retries` and `retry_exceptions` for idempotent task resilience. |
| `fault02` | `exercises/05_fault_tolerance/fault02.py` | **Actor Restarts & State Loss** — Managing state recovery upon actor failure with `max_restarts`. |
| `fault03` | `exercises/05_fault_tolerance/fault03.py` | **Lineage Recomputation** — Automatic object recreation when Plasma objects are lost during node failure. |
| `fault04` | `exercises/05_fault_tolerance/fault04.py` | **Spot Instance & Preemption Handling** — Graceful handling of node drain signals and actor migration. |

---

### Chapter 6: `06_cluster_architecture` - Cluster Topology & Multi-Node Simulation

Covers cluster architecture, Global Control Store (GCS), Raylet schedulers, multi-node testing, and the Ray Job Submission API.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `cluster01` | `exercises/06_cluster_architecture/cluster01.py` | **Head vs Worker Architecture** — Inspecting GCS state, node tables, and Raylet communication. |
| `cluster02` | `exercises/06_cluster_architecture/cluster02.py` | **Multi-Node Testing with Cluster Utils** — Simulating multi-node topologies in local tests using `ray.cluster_utils.Cluster`. |
| `cluster03` | `exercises/06_cluster_architecture/cluster03.py` | **Ray Job Submission API** — Submitting and monitoring remote jobs via `JobSubmissionClient`. |
| `cluster04` | `exercises/06_cluster_architecture/cluster04.py` | **Cross-Node Object Transfers** — Measuring bandwidth and serialization overhead across simulated physical nodes. |

---

### Chapter 7: `07_patterns_and_antipatterns` - Production Patterns & Anti-Patterns

Covers real-world production anti-patterns, pipeline stalls, micro-task overhead, actor bottlenecks, and tree aggregations.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `antipattern01` | `exercises/07_patterns_and_antipatterns/antipattern01.py` | **Nested ray.get() Bottlenecks** — Eliminating nested driver blocking in distributed pipelines. |
| `antipattern02` | `exercises/07_patterns_and_antipatterns/antipattern02.py` | **Micro-Task Chunking** — Grouping fine-grained tasks into optimal batch sizes to eliminate scheduler overhead. |
| `antipattern03` | `exercises/07_patterns_and_antipatterns/antipattern03.py` | **Actor Bottleneck Elimination** — Sharding high-contention actor state across dynamic actor pools. |
| `antipattern04` | `exercises/07_patterns_and_antipatterns/antipattern04.py` | **Tree-Structured Distributed Aggregation** — Implementing $O(\log N)$ tree reductions to prevent single-driver memory saturation. |

---

### Chapter 8: `08_ray_data` - Ray Data for High-Throughput ETL

Covers distributed streaming datasets, block partitioning, vectorized transformations, and streaming backpressure.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `data01` | `exercises/08_ray_data/data01.py` | **Dataset Ingestion & Block Partitioning** — Reading distributed data into partitioned Ray Dataset blocks. |
| `data02` | `exercises/08_ray_data/data02.py` | **Vectorized Batch Transformations** — High-throughput transforms with `map_batches` and PyArrow tables. |
| `data03` | `exercises/08_ray_data/data03.py` | **ActorPool Batch Compute** — Stateful neural network batch inference with `compute=ActorPoolStrategy(...)`. |
| `data04` | `exercises/08_ray_data/data04.py` | **Streaming Backpressure & Windowing** — Bounded memory execution preventing driver OOM on large streaming datasets. |
| `data05` | `exercises/08_ray_data/data05.py` | **PyTorch DataLoader Interoperability** — Streaming Ray Data directly into distributed PyTorch training loops. |

---

### Chapter 9: `09_ml_from_scratch` - Distributed ML Primitives from Scratch

Covers implementing fundamental distributed machine learning building blocks from first principles.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `ml_scratch01` | `exercises/09_ml_from_scratch/ml_scratch01.py` | **Synchronous Parameter Server** — Centralized parameter storage with barrier-synchronized gradient updates. |
| `ml_scratch02` | `exercises/09_ml_from_scratch/ml_scratch02.py` | **Asynchronous Parameter Server** — High-throughput non-blocking parameter updates with staleness tolerance. |
| `ml_scratch03` | `exercises/09_ml_from_scratch/ml_scratch03.py` | **Ring All-Reduce Communication** — Decentralized gradient reduction ring minimizing communication bandwidth. |
| `ml_scratch04` | `exercises/09_ml_from_scratch/ml_scratch04.py` | **Distributed Linear Regression Trainer** — End-to-end data-parallel SGD trainer with distributed Ray workers. |

---

### Chapter 10: `10_ray_train_and_tune` - Ray Train & Distributed Deep Learning

Covers PyTorch Distributed Data Parallel (DDP) training with Ray Train.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `train01` | `exercises/10_ray_train_and_tune/train01.py` | **TorchTrainer & ScalingConfig** — Distributed PyTorch training coordination across multi-worker CPU/GPU clusters. |
| `train02` | `exercises/10_ray_train_and_tune/train02.py` | **Distributed Data Sharding & Loading** — Sharding datasets across distributed DDP workers with `ray.train.torch.prepare_data_loader`. |
| `train03` | `exercises/10_ray_train_and_tune/train03.py` | **Distributed Checkpointing & Metrics** — Reporting training loss metrics and persisting distributed checkpoints with `ray.train.report`. |
| `train04` | `exercises/10_ray_train_and_tune/train04.py` | **Fault-Tolerant Elastic Worker Recovery** — Recovering training sessions seamlessly from checkpoints upon worker interruption. |

---

### Chapter 11: `11_ray_tune` - Scalable Hyperparameter Tuning

Covers distributed hyperparameter optimization algorithms and trial schedulers.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `tune01` | `exercises/11_ray_tune/tune01.py` | **Tune Search Spaces & Grid Search** — Defining distributed search spaces with `tune.choice` and `tune.uniform`. |
| `tune02` | `exercises/11_ray_tune/tune02.py` | **ASHA Early Stopping Scheduler** — Aggressive trial pruning with Asynchronous Successive Halving Algorithm. |
| `tune03` | `exercises/11_ray_tune/tune03.py` | **Population-Based Training (PBT)** | Dynamic hyperparameter exploration and weight inheritance during training. |

---

### Chapter 12: `12_ray_serve` - Ray Serve & Production Model Serving

Covers production inference architectures, request batching, multi-model pipelines, and streaming.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `serve01` | `exercises/12_ray_serve/serve01.py` | **First Serve Deployment & HTTP Ingress** — Defining `@serve.deployment` classes and handling HTTP requests. |
| `serve02` | `exercises/12_ray_serve/serve02.py` | **Dynamic Request Batching with @serve.batch** — Micro-batching individual HTTP requests to maximize GPU throughput. |
| `serve03` | `exercises/12_ray_serve/serve03.py` | **Multi-Model Pipeline DAGs** — Composing complex multi-stage deployment graphs with `ray.serve.deployment`. |
| `serve04` | `exercises/12_ray_serve/serve04.py` | **Autoscaling & Replica Dynamics** — Configuring `autoscaling_config` for traffic-driven elasticity. |
| `serve05` | `exercises/12_ray_serve/serve05.py` | **Streaming LLM Token Responses** — Streaming token responses chunk-by-chunk using async generators. |

---

### Chapter 13: `13_observability_and_debugging` - Observability & Memory Debugging

Covers distributed profiling, execution timelines, memory debugging, and Prometheus state APIs.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `perf01` | `exercises/13_observability_and_debugging/perf01.py` | **Execution Profiling & Chrome Timelines** — Exporting execution traces via `ray.timeline()` for Perfetto / Chrome Tracing. |
| `perf02` | `exercises/13_observability_and_debugging/perf02.py` | **Diagnosing Memory Leaks with ray memory** — Inspecting active and leaked ObjectRefs across cluster Plasma stores. |
| `perf03` | `exercises/13_observability_and_debugging/perf03.py` | **Ray Metrics & Prometheus State APIs** — Querying task queues and worker states using `ray.util.state`. |

---

### Chapter 14: `14_kuberay` - KubeRay & Cloud-Native Ray on Kubernetes

Covers deploying, scaling, and managing production Ray clusters on Kubernetes with the KubeRay Operator.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `kuberay01` | `exercises/14_kuberay/kuberay01.py` | **RayCluster Custom Resource (CRD)** — Authoring declarative head and worker group pod templates in YAML. |
| `kuberay02` | `exercises/14_kuberay/kuberay02.py` | **RayJob CRD & Batch Lifecycles** — Submitting ephemeral batch jobs with automatic cluster teardown on completion. |
| `kuberay03` | `exercises/14_kuberay/kuberay03.py` | **RayService CRD & Zero-Downtime Serving** — Operating rolling upgrades and health-checked endpoints on Kubernetes. |
| `kuberay04` | `exercises/14_kuberay/kuberay04.py` | **Autoscaling with KEDA & Ray Autoscaler** — Scaling Kubernetes worker pods dynamically under queue pressure. |
| `kuberay05` | `exercises/14_kuberay/kuberay05.py` | **Kubernetes Fault Tolerance & Pod Evictions** — Preserving cluster state and reconstructing lineage across pod evictions. |

---

### Chapter 15: `15_vllm_and_llms` - Distributed LLM Serving & vLLM

Covers high-throughput LLM serving architectures, tensor parallel worker actor groups, PagedAttention KV-cache management, multi-LoRA dynamic adapter loading, and speculative decoding.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `vllm01` | `exercises/15_vllm_and_llms/vllm01.py` | **Tensor Parallelism & Worker Actor Groups** — Sharding linear projection matrices across Ray actors (ColumnParallel and RowParallel) with All-Reduce output aggregation. |
| `vllm02` | `exercises/15_vllm_and_llms/vllm02.py` | **PagedAttention & KV-Cache Block Management** — Managing non-contiguous physical KV-cache memory blocks, logical-to-physical block tables, dynamic boundary allocation, and prefix sharing. |
| `vllm03` | `exercises/15_vllm_and_llms/vllm03.py` | **Dynamic Multi-LoRA Adapter Serving** — Serving multi-tenant low-rank adapters over a shared base model with LRU cache eviction and dynamic scaling factors. |
| `vllm04` | `exercises/15_vllm_and_llms/vllm04.py` | **Speculative Decoding with Draft & Target Workers** — Accelerating autoregressive token generation using lightweight draft workers and parallel batch verification with target model workers. |

---

### Chapter 16: `16_fsdp_and_deepspeed` - DeepSpeed & PyTorch FSDP

Covers large-scale distributed model training with PyTorch Fully Sharded Data Parallel (FSDP), DeepSpeed ZeRO memory partitioning stages (ZeRO-1/2/3), activation checkpointing, mixed precision, and fault-tolerant elastic checkpoints.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `fsdp01` | `exercises/16_fsdp_and_deepspeed/fsdp01.py` | **PyTorch FSDP with Ray Train ScalingConfig** — Wrapping PyTorch models in Fully Sharded Data Parallel (`FULL_SHARD`) with size-based auto-wrap policies across Ray Train workers. |
| `fsdp02` | `exercises/16_fsdp_and_deepspeed/fsdp02.py` | **DeepSpeed ZeRO-1 / ZeRO-2 / ZeRO-3 Memory Partitioning** — Partitioning optimizer states, gradients, and model parameters with ReduceScatter gradient synchronization and AllGather reconstruction. |
| `fsdp03` | `exercises/16_fsdp_and_deepspeed/fsdp03.py` | **Mixed Precision & Activation Checkpointing** — Slashing peak activation memory via `torch.utils.checkpoint` and mixed-precision `torch.autocast` forward passes. |
| `fsdp04` | `exercises/16_fsdp_and_deepspeed/fsdp04.py` | **Elastic Fault-Tolerant Distributed Checkpoints** — Saving per-rank sharded checkpoint slices and atomic metadata with elastic recovery upon worker preemption. |

---

### Chapter 17: `17_multimodal_and_vectors` - Multimodal & Vector Ray Data

Covers streaming multimodal ETL pipelines, high-throughput batch embedding extraction via stateful `ActorPoolStrategy`, dynamic token length bucketing, and parallel streaming ingestion into partitioned vector databases.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `data_genai01` | `exercises/17_multimodal_and_vectors/data_genai01.py` | **Streaming Multimodal Image & Audio ETL** — Processing heterogeneous image and audio data with PyArrow tensor extensions, zero-copy transformations, and bounded memory streaming. |
| `data_genai02` | `exercises/17_multimodal_and_vectors/data_genai02.py` | **Accelerated Batch Embeddings with ActorPoolStrategy** — Streaming document embeddings through persistent stateful neural worker pools with `ActorPoolStrategy`. |
| `data_genai03` | `exercises/17_multimodal_and_vectors/data_genai03.py` | **Dynamic Token Length Bucketing & Padding Optimization** — Grouping variable-length sequences into length buckets to minimize wasteful padding tokens and attention mask overhead. |
| `data_genai04` | `exercises/17_multimodal_and_vectors/data_genai04.py` | **Streaming Parallel Ingestion into Vector Databases** — Authoring custom Ray Data `Datasink` classes for partition-aware, high-throughput parallel upserts into vector indices. |

---

### Chapter 18: `18_quant_finance` - Distributed Quantitative Finance

Covers high-throughput financial risk simulations, distributed derivatives pricing, Value at Risk (VaR/CVaR) calculations, and streaming market tick analytics.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `finance01` | `exercises/18_quant_finance/finance01.py` | **Distributed Monte Carlo Black-Scholes Option Pricing** — Simulating parallel Geometric Brownian Motion (GBM) asset price paths across Ray tasks and aggregating discounted call payoffs. |
| `finance02` | `exercises/18_quant_finance/finance02.py` | **Portfolio Value at Risk (VaR) & CVaR Stress Simulation** — Estimating empirical Value at Risk ($95\%$ and $99\%$ percentiles) and Conditional VaR (Expected Shortfall) across multi-asset portfolio returns. |
| `finance03` | `exercises/18_quant_finance/finance03.py` | **Streaming Market Tick Analytics & Rolling VWAP** — Ingesting high-frequency trade ticks through Ray Data streaming pipelines to compute continuous Volume-Weighted Average Price (VWAP) across instrument partitions. |
