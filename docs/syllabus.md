# Complete Curriculum Syllabus 📚

The Raylings curriculum consists of **17 comprehensive chapters** containing **78 hands-on exercises**. The syllabus is designed to take you from core distributed primitives to production-scale AI training, serving, and cloud-native Kubernetes orchestration.

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
| **13** | [`13_observability_and_debugging`](#chapter-13-13_observability_and_debugging-observability-profiling-memory-debugging) | **Observability & Memory Debugging** | 3 | Chrome Timelines, Plasma Leak Profiling, State APIs | Expert |
| **14** | [`14_kuberay`](#chapter-14-14_kuberay-kuberay-cloud-native-ray-on-kubernetes) | **KubeRay & Cloud-Native Kubernetes** | 5 | RayCluster CRD, RayJob, RayService, KEDA Autoscaling | Expert |
| **15** | [`15_vllm_and_llms`](#chapter-15-15_vllm_and_llms-distributed-llm-serving-vllm) | **Distributed LLM Serving & vLLM** | 4 | Tensor Parallelism, PagedAttention, Multi-LoRA, Speculative Decoding | Expert |
| **16** | [`16_fsdp_and_deepspeed`](#chapter-16-16_fsdp_and_deepspeed-deepspeed-pytorch-fsdp) | **DeepSpeed & PyTorch FSDP** | 4 | Fully Sharded Data Parallel, ZeRO Memory Optimization, Fault Recovery | Expert |
| **17** | [`17_multimodal_and_vectors`](#chapter-17-17_multimodal_and_vectors-multimodal-vector-ray-data) | **Multimodal & Vector Ray Data** | 4 | Streaming Multimodal ETL, ActorPool Embeddings, Vector Stores | Expert |

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
| `fault02` | `exercises/05_fault_tolerance/fault02.py` | **Actor Failure & Restart Recovery** — Rebuilding actor state automatically using `max_restarts` and checkpointing. |
| `fault03` | `exercises/05_fault_tolerance/fault03.py` | **Lineage Reconstruction** — Recomputing lost object store buffers using the deterministic lineage DAG. |
| `fault04` | `exercises/05_fault_tolerance/fault04.py` | **Spot Instance & Preemption Handling** — Graceful failure handling during spot instance termination. |

---

### Chapter 6: `06_cluster_architecture` - Cluster Topology & Multi-Node Simulation

Covers cluster architecture (Head Node, Raylets, GCS), multi-node simulation in Python, and programmatic job submission.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `cluster01` | `exercises/06_cluster_architecture/cluster01.py` | **Head Node, Workers & GCS** — Inspecting cluster nodes, heartbeats, and metadata via `ray.nodes()`. |
| `cluster02` | `exercises/06_cluster_architecture/cluster02.py` | **Programmatic Cluster Simulation** — Simulating dynamic multi-node topologies using `ray.cluster_utils.Cluster`. |
| `cluster03` | `exercises/06_cluster_architecture/cluster03.py` | **Simulating Node Death & Rescheduling** — Testing scheduler behavior when worker nodes disappear dynamically. |
| `cluster04` | `exercises/06_cluster_architecture/cluster04.py` | **Ray Job Submission API** — Packaging and submitting jobs remotely with `ray.job_submission.JobSubmissionClient`. |

---

### Chapter 7: `07_patterns_and_antipatterns` - Production Patterns & Anti-Patterns

Identifies critical architectural bottlenecks and teaches production-grade distributed patterns.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `antipattern01` | `exercises/07_patterns_and_antipatterns/antipattern01.py` | **Fixing ray.get() Inside Tasks** — Eliminating blocking dependency stalls by passing ObjectRefs directly. |
| `antipattern02` | `exercises/07_patterns_and_antipatterns/antipattern02.py` | **Fixing Fine-Grained Overhead** — Amortizing scheduling overhead by batching micro-tasks into coarse chunks. |
| `antipattern03` | `exercises/07_patterns_and_antipatterns/antipattern03.py` | **Fixing Actor Bottlenecks** — Decoupling high-frequency read/write pathways with actor replication pools. |
| `antipattern04` | `exercises/07_patterns_and_antipatterns/antipattern04.py` | **Tree-Reduce Reduction** — Replacing $O(N)$ linear aggregation with $O(\log N)$ logarithmic tree reduction. |

---

### Chapter 8: `08_ray_data` - Ray Data for High-Throughput ETL

Covers streaming data pipelines, block partitioning, vectorized batch transformations, and PyTorch dataloader integration.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `data01` | `exercises/08_ray_data/data01.py` | **Datasets & Block Partitioning** — Ingesting data, inspecting block partitions (`ds.num_blocks()`), and repartitioning. |
| `data02` | `exercises/08_ray_data/data02.py` | **map vs map_batches** — Accelerating transformations with PyArrow/NumPy vectorized batch processing. |
| `data03` | `exercises/08_ray_data/data03.py` | **Stateful Transforms with ActorPoolStrategy** — Reusing initialized model weights across data blocks. |
| `data04` | `exercises/08_ray_data/data04.py` | **Streaming Pipelines & Backpressure** — Streaming infinite or multi-gigabyte datasets with bounded RAM usage. |
| `data05` | `exercises/08_ray_data/data05.py` | **PyTorch DataLoader Interop** — Zero-copy streaming into PyTorch training loops using `ds.iter_torch_batches()`. |

---

### Chapter 9: `09_ml_from_scratch` - Distributed ML Primitives from Scratch

Builds core distributed machine learning building blocks directly on top of Ray Core actors and tasks.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `ml_scratch01` | `exercises/09_ml_from_scratch/ml_scratch01.py` | **Distributed Parameter Server** — Implementing central parameter storage and worker gradient updates. |
| `ml_scratch02` | `exercises/09_ml_from_scratch/ml_scratch02.py` | **Async vs Sync Gradient Averaging** — Comparing lock-step synchronization vs asynchronous stale gradient updates. |
| `ml_scratch03` | `exercises/09_ml_from_scratch/ml_scratch03.py` | **Ring All-Reduce Implementation** — Building 2-phase Scatter-Reduce and Allgather across a logical actor ring. |
| `ml_scratch04` | `exercises/09_ml_from_scratch/ml_scratch04.py` | **Distributed Data-Parallel Trainer** — Assembling a custom multi-worker DDP training harness. |

---

### Chapter 10: `10_ray_train_and_tune` - Ray Train & Distributed Deep Learning

Covers production distributed training using PyTorch and Ray Train (`TorchTrainer`), data sharding, and checkpointing.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `train01` | `exercises/10_ray_train_and_tune/train01.py` | **PyTorch TorchTrainer & ScalingConfig** — Setting up multi-worker DDP training loops with `TorchTrainer`. |
| `train02` | `exercises/10_ray_train_and_tune/train02.py` | **Distributed DataLoader via DataConfig** — Auto-sharding datasets across distributed training workers. |
| `train03` | `exercises/10_ray_train_and_tune/train03.py` | **Multi-Worker Gradient Sync & Metrics** — Synchronizing models with `prepare_model` and reporting metrics with `ray.train.report`. |
| `train04` | `exercises/10_ray_train_and_tune/train04.py` | **Distributed Checkpointing & Fault Recovery** — Saving and resuming training states from durable checkpoints. |

---

### Chapter 11: `11_ray_tune` - Scalable Hyperparameter Tuning

Covers search space exploration, early-stopping schedulers, and Population-Based Training.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `tune01` | `exercises/11_ray_tune/tune01.py` | **Search Spaces & Distributed Trials** — Defining hyperparameter spaces (`tune.uniform`, `tune.choice`) and fitting Tuners. |
| `tune02` | `exercises/11_ray_tune/tune02.py` | **ASHA / HyperBand Schedulers** — Terminating poorly performing trials early with `ASHAScheduler`. |
| `tune03` | `exercises/11_ray_tune/tune03.py` | **Population-Based Training (PBT)** — Dynamic hyperparameter mutation and weight exploitation during training. |

---

### Chapter 12: `12_ray_serve` - Ray Serve & Production Model Serving

Covers production-grade HTTP model serving, dynamic request batching, DAG composition, streaming token responses, and autoscaling.

| Exercise | File Path | Topic & Learning Objective |
| :--- | :--- | :--- |
| `serve01` | `exercises/12_ray_serve/serve01.py` | **Ray Serve Deployments & HTTP Ingress** — Defining `@serve.deployment` classes and binding HTTP entrypoints. |
| `serve02` | `exercises/12_ray_serve/serve02.py` | **Dynamic Request Batching (@serve.batch)** — Coalescing concurrent HTTP requests into unified vectorized batches. |
| `serve03` | `exercises/12_ray_serve/serve03.py` | **Multi-Model Composable Pipelines (DAGs)** — Chaining preprocessing, inference, and postprocessing deployments. |
| `serve04` | `exercises/12_ray_serve/serve04.py` | **Streaming Responses with FastAPI** — Streaming real-time tokens from LLM deployments using Python generators. |
| `serve05` | `exercises/12_ray_serve/serve05.py` | **Serve Autoscaling Policies** — Scaling replicas dynamically based on `target_ongoing_requests`. |

---

### Chapter 13: `13_observability_and_debugging` - Observability, Profiling & Memory Debugging

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

