"""Curriculum manifest definition and exercise navigation helpers."""

from pathlib import Path
from typing import Optional

from raylings.models import Chapter, Exercise, Manifest


def build_manifest() -> Manifest:
    """Build and return the complete Raylings curriculum manifest."""
    chapters = [
        Chapter(
            number=1,
            name="01_basics",
            title="Ray Core Foundations",
            description="Tasks, Futures, and Asynchronous Execution",
            exercises=[
                Exercise(
                    name="basics01",
                    title="Ray Init & First Remote Task",
                    path="exercises/01_basics/basics01.py",
                    chapter_name="01_basics",
                    hints=[
                        "Use ray.init(ignore_reinit_error=True) to initialize Ray.",
                        "Decorate your Python function with @ray.remote.",
                        "Invoke remote functions using function_name.remote(*args).",
                    ],
                ),
                Exercise(
                    name="basics02",
                    title="ObjectRefs and ray.get()",
                    path="exercises/01_basics/basics02.py",
                    chapter_name="01_basics",
                    hints=[
                        "Calling .remote() returns an ObjectRef (a future), not the actual value.",
                        "Call ray.get(ref) to block and retrieve the computed value.",
                        "Pass a list of ObjectRefs to ray.get([ref1, ref2]) to fetch multiple results.",
                    ],
                ),
                Exercise(
                    name="basics03",
                    title="Parallel Pipeline Execution",
                    path="exercises/01_basics/basics03.py",
                    chapter_name="01_basics",
                    hints=[
                        "Launch all remote tasks before calling ray.get() to run them in parallel.",
                        "Calling ray.get() immediately after each task serializes execution.",
                    ],
                ),
                Exercise(
                    name="basics04",
                    title="Passing ObjectRefs to Tasks",
                    path="exercises/01_basics/basics04.py",
                    chapter_name="01_basics",
                    hints=[
                        "Pass ObjectRefs directly to another @ray.remote task without calling ray.get().",
                        "Ray automatically resolves ObjectRef arguments before executing downstream tasks.",
                    ],
                ),
                Exercise(
                    name="basics05",
                    title="Dynamic Completion with ray.wait()",
                    path="exercises/01_basics/basics05.py",
                    chapter_name="01_basics",
                    hints=[
                        "ray.wait(object_refs, num_returns=1) returns (ready_refs, remaining_refs).",
                        "Use a while loop to dynamically process tasks as they finish.",
                    ],
                ),
                Exercise(
                    name="basics06",
                    title="Multiple Returns in Remote Tasks",
                    path="exercises/01_basics/basics06.py",
                    chapter_name="01_basics",
                    hints=[
                        "Use @ray.remote(num_returns=2) to return multiple ObjectRefs from a single task.",
                        "Unpack the returned tuple of ObjectRefs: ref_a, ref_b = my_task.remote().",
                    ],
                ),
            ],
        ),
        Chapter(
            number=2,
            name="02_actors",
            title="Distributed State & Actors",
            description="Stateful actors, method calls, actor handles, and actor pools",
            exercises=[
                Exercise(
                    name="actors01",
                    title="Stateful Actor Lifecycle",
                    path="exercises/02_actors/actors01.py",
                    chapter_name="02_actors",
                    hints=[
                        "Decorate a Python class with @ray.remote to make it an Actor.",
                        "Instantiate the actor with ClassName.remote(*args).",
                        "Call methods using actor_handle.method.remote(*args).",
                    ],
                ),
                Exercise(
                    name="actors02",
                    title="Actor Method Calls & State Mutation",
                    path="exercises/02_actors/actors02.py",
                    chapter_name="02_actors",
                    hints=[
                        "Actor methods execute sequentially by default on the stateful actor process.",
                        "Use ray.get(actor.get_state.remote()) to read the actor's internal state.",
                    ],
                ),
                Exercise(
                    name="actors03",
                    title="Passing Actor Handles",
                    path="exercises/02_actors/actors03.py",
                    chapter_name="02_actors",
                    hints=[
                        "Actor handles can be passed as arguments to other tasks or actors.",
                        "Other workers can invoke methods directly on the shared actor handle.",
                    ],
                ),
                Exercise(
                    name="actors04",
                    title="Async Actors & Concurrency",
                    path="exercises/02_actors/actors04.py",
                    chapter_name="02_actors",
                    hints=[
                        "Define actor methods with async def.",
                        "Configure @ray.remote(max_concurrency=N) to allow concurrent coroutines on an actor.",
                    ],
                ),
                Exercise(
                    name="actors05",
                    title="Threaded Actors for Blocking I/O",
                    path="exercises/02_actors/actors05.py",
                    chapter_name="02_actors",
                    hints=[
                        "Use @ray.remote(max_concurrency=N) with regular def methods to enable a thread pool.",
                        "Threaded actors enable concurrent execution of blocking C extensions or I/O calls.",
                    ],
                ),
                Exercise(
                    name="actors06",
                    title="Detached Named Actors",
                    path="exercises/02_actors/actors06.py",
                    chapter_name="02_actors",
                    hints=[
                        "Create named detached actors with Class.options(name='...', lifetime='detached', namespace='...').remote().",
                        "Retrieve existing named actors with ray.get_actor('name', namespace='...').",
                    ],
                ),
                Exercise(
                    name="actors07",
                    title="ActorPool Dynamic Load Balancing",
                    path="exercises/02_actors/actors07.py",
                    chapter_name="02_actors",
                    hints=[
                        "Use ray.util.ActorPool([actor1, actor2, ...]) to manage a pool of stateful workers.",
                        "Use pool.map() or pool.submit() and pool.get_next() to balance incoming tasks.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=3,
            name="03_object_store",
            title="Plasma Object Store & Zero-Copy",
            description="In-memory object store, ray.put(), zero-copy reads, and memory management",
            exercises=[
                Exercise(
                    name="object_store01",
                    title="Zero-Copy Plasma Reads",
                    path="exercises/03_object_store/object_store01.py",
                    chapter_name="03_object_store",
                    hints=[
                        "NumPy arrays and PyArrow tables stored in Plasma are read via shared memory zero-copy.",
                        "Multiple processes on the same node can read data without deserialization overhead.",
                    ],
                ),
                Exercise(
                    name="object_store02",
                    title="ray.put() vs Implicit Serialization",
                    path="exercises/03_object_store/object_store02.py",
                    chapter_name="03_object_store",
                    hints=[
                        "Use ray.put(large_data) once to place data into the shared object store.",
                        "Pass the resulting ObjectRef to multiple tasks to prevent repeated serialization.",
                    ],
                ),
                Exercise(
                    name="object_store03",
                    title="Object Immutability & Read-Only Semantics",
                    path="exercises/03_object_store/object_store03.py",
                    chapter_name="03_object_store",
                    hints=[
                        "Plasma shared memory buffers are immutable (flags.writeable == False).",
                        "Attempting in-place mutation of zero-copy arrays raises ValueError.",
                        "Use arr.copy() to create a mutable local copy if modification is needed.",
                    ],
                ),
                Exercise(
                    name="object_store04",
                    title="Object Spilling & Memory Limits",
                    path="exercises/03_object_store/object_store04.py",
                    chapter_name="03_object_store",
                    hints=[
                        "Plasma has a bounded capacity (~30% of system RAM by default).",
                        "Cold objects are automatically spilled to disk and transparently retrieved on ray.get().",
                        "Deleting or scoping ObjectRefs allows Ray to reclaim Plasma memory.",
                    ],
                ),
                Exercise(
                    name="object_store05",
                    title="Handling & Resolving Nested ObjectRefs",
                    path="exercises/03_object_store/object_store05.py",
                    chapter_name="03_object_store",
                    hints=[
                        "Tasks returning other ObjectRefs yield ObjectRef[ObjectRef[T]].",
                        "Each ray.get() unwraps one level of nested references.",
                        "Ray does not automatically dereference ObjectRefs nested inside lists or dicts.",
                    ],
                ),
                Exercise(
                    name="object_store06",
                    title="Custom Serializers with ray.util",
                    path="exercises/03_object_store/object_store06.py",
                    chapter_name="03_object_store",
                    hints=[
                        "Register custom serializer and deserializer functions using ray.util.register_serializer.",
                        "Useful for optimizing custom types or objects that default pickle cannot serialize.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=4,
            name="04_scheduling_resources",
            title="Resource Scheduling & Placement Groups",
            description="CPUs, GPUs, custom resources, node affinity, and placement groups",
            exercises=[
                Exercise(
                    name="scheduling01",
                    title="Fractional & Custom Resources",
                    path="exercises/04_scheduling_resources/scheduling01.py",
                    chapter_name="04_scheduling_resources",
                    hints=[
                        "Specify fractional CPUs with @ray.remote(num_cpus=0.5) to pack tasks on cores.",
                        "Request custom resources via @ray.remote(resources={'custom_res': 1}).",
                    ],
                ),
                Exercise(
                    name="scheduling02",
                    title="Node Affinity Scheduling",
                    path="exercises/04_scheduling_resources/scheduling02.py",
                    chapter_name="04_scheduling_resources",
                    hints=[
                        "Use ray.util.scheduling_strategies.NodeAffinitySchedulingStrategy(node_id, soft=False).",
                        "Pass scheduling_strategy to task.options(scheduling_strategy=strategy).",
                    ],
                ),
                Exercise(
                    name="scheduling03",
                    title="Placement Groups: SPREAD Strategy",
                    path="exercises/04_scheduling_resources/scheduling03.py",
                    chapter_name="04_scheduling_resources",
                    hints=[
                        "Create a placement group with strategy='SPREAD' to distribute tasks across bundles.",
                        "Use ray.util.placement_group.placement_group([{'CPU': 0.5}, {'CPU': 0.5}], strategy='SPREAD').",
                    ],
                ),
                Exercise(
                    name="scheduling04",
                    title="Placement Groups: PACK Strategy",
                    path="exercises/04_scheduling_resources/scheduling04.py",
                    chapter_name="04_scheduling_resources",
                    hints=[
                        "Create a placement group with strategy='PACK' to co-locate tasks/actors on the same node.",
                        "Pass PlacementGroupSchedulingStrategy(placement_group=pg, placement_group_bundle_index=0) to options.",
                    ],
                ),
                Exercise(
                    name="scheduling05",
                    title="Gang Scheduling Multi-Bundle",
                    path="exercises/04_scheduling_resources/scheduling05.py",
                    chapter_name="04_scheduling_resources",
                    hints=[
                        "Gang scheduling guarantees all resource bundles are available before jobs begin.",
                        "Call ray.get(pg.ready()) to block until the entire placement group is scheduled.",
                    ],
                ),
                Exercise(
                    name="scheduling06",
                    title="Dynamic Runtime Environments",
                    path="exercises/04_scheduling_resources/scheduling06.py",
                    chapter_name="04_scheduling_resources",
                    hints=[
                        "Pass runtime_env={'pip': [...], 'env_vars': {...}} to ray.init() or task.options().",
                        "Isolates dependencies and environment variables per worker.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=5,
            name="05_fault_tolerance",
            title="Fault Tolerance & Lineage Recovery",
            description="Automatic retries, actor restarts, and object lineage reconstruction",
            exercises=[
                Exercise(
                    name="fault01",
                    title="Automatic Task Retries",
                    path="exercises/05_fault_tolerance/fault01.py",
                    chapter_name="05_fault_tolerance",
                    hints=[
                        "Use @ray.remote(max_retries=3, retry_exceptions=True) for automatic task retries.",
                        "Ray will re-execute the task upon worker crash or specified exception.",
                    ],
                ),
                Exercise(
                    name="fault02",
                    title="Actor Failure & Restart Recovery",
                    path="exercises/05_fault_tolerance/fault02.py",
                    chapter_name="05_fault_tolerance",
                    hints=[
                        "Use @ray.remote(max_restarts=3, max_task_retries=3) to automatically restart failed actors.",
                        "Actor state can be restored upon restart in __init__ or from persistent storage.",
                    ],
                ),
                Exercise(
                    name="fault03",
                    title="Lineage Reconstruction",
                    path="exercises/05_fault_tolerance/fault03.py",
                    chapter_name="05_fault_tolerance",
                    hints=[
                        "Ray records the task DAG that created each ObjectRef and can recompute lost objects.",
                        "Reconstruction re-runs tasks whose outputs were lost due to node failure.",
                    ],
                ),
                Exercise(
                    name="fault04",
                    title="Spot Instance & Preemption Handling",
                    path="exercises/05_fault_tolerance/fault04.py",
                    chapter_name="05_fault_tolerance",
                    hints=[
                        "Handle node preemption by catching RayTaskError / ObjectLostError.",
                        "Use durable checkpointing for long-running workflows.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=6,
            name="06_cluster_architecture",
            title="Cluster Topology & Multi-Node Simulation",
            description="GCS, Raylets, cluster simulation, and Job Submission API",
            exercises=[
                Exercise(
                    name="cluster01",
                    title="Head Node, Workers & GCS",
                    path="exercises/06_cluster_architecture/cluster01.py",
                    chapter_name="06_cluster_architecture",
                    hints=[
                        "Head node runs the Global Control Store (GCS) and dashboard; worker nodes run Raylets.",
                        "Inspect cluster nodes programmatically using ray.nodes().",
                    ],
                ),
                Exercise(
                    name="cluster02",
                    title="Programmatic Cluster Simulation",
                    path="exercises/06_cluster_architecture/cluster02.py",
                    chapter_name="06_cluster_architecture",
                    hints=[
                        "Use ray.cluster_utils.Cluster to simulate multi-node environments in Python.",
                        "Call cluster.add_node(num_cpus=2) to dynamically add nodes.",
                    ],
                ),
                Exercise(
                    name="cluster03",
                    title="Simulating Node Death & Rescheduling",
                    path="exercises/06_cluster_architecture/cluster03.py",
                    chapter_name="06_cluster_architecture",
                    hints=[
                        "Call cluster.remove_node(worker_node) to simulate unexpected node failure.",
                        "Verify that Ray detects the dead node and reschedules pending work.",
                    ],
                ),
                Exercise(
                    name="cluster04",
                    title="Ray Job Submission API",
                    path="exercises/06_cluster_architecture/cluster04.py",
                    chapter_name="06_cluster_architecture",
                    hints=[
                        "Use ray.job_submission.JobSubmissionClient to submit jobs programmatically.",
                        "Call client.submit_job(entrypoint='python main.py', runtime_env=...).",
                    ],
                ),
            ],
        ),
        Chapter(
            number=7,
            name="07_patterns_and_antipatterns",
            title="Production Patterns & Anti-Patterns",
            description="Common pitfalls, bottlenecks, and high-performance design patterns",
            exercises=[
                Exercise(
                    name="antipattern01",
                    title="Fixing ray.get() Inside Tasks",
                    path="exercises/07_patterns_and_antipatterns/antipattern01.py",
                    chapter_name="07_patterns_and_antipatterns",
                    hints=[
                        "Calling ray.get() inside a task on arguments creates unnecessary blocking dependencies.",
                        "Pass ObjectRefs directly to downstream tasks to let Ray manage data dependencies.",
                    ],
                ),
                Exercise(
                    name="antipattern02",
                    title="Fixing Fine-Grained Task Overhead",
                    path="exercises/07_patterns_and_antipatterns/antipattern02.py",
                    chapter_name="07_patterns_and_antipatterns",
                    hints=[
                        "Very small tasks (<10ms) are dominated by scheduling and serialization overhead.",
                        "Batch items into larger chunks before dispatching remote tasks.",
                    ],
                ),
                Exercise(
                    name="antipattern03",
                    title="Fixing Actor Bottlenecks",
                    path="exercises/07_patterns_and_antipatterns/antipattern03.py",
                    chapter_name="07_patterns_and_antipatterns",
                    hints=[
                        "A single synchronous actor serializes all requests and becomes a bottleneck.",
                        "Use an ActorPool, async actor methods, or separate read/write paths.",
                    ],
                ),
                Exercise(
                    name="antipattern04",
                    title="Nested Remote Calls & Tree-Reduce",
                    path="exercises/07_patterns_and_antipatterns/antipattern04.py",
                    chapter_name="07_patterns_and_antipatterns",
                    hints=[
                        "Linear accumulation requires O(N) sequential steps.",
                        "Use tree-structured reduction (Tree-Reduce) to reduce latency to O(log N).",
                    ],
                ),
            ],
        ),
        Chapter(
            number=8,
            name="08_ray_data",
            title="Ray Data for High-Throughput ETL",
            description="Datasets, streaming execution, zero-copy batching, and ML data loading",
            exercises=[
                Exercise(
                    name="data01",
                    title="Datasets & Block Partitioning",
                    path="exercises/08_ray_data/data01.py",
                    chapter_name="08_ray_data",
                    hints=[
                        "Create Ray Datasets with ray.data.from_items() or ray.data.read_parquet().",
                        "Check and adjust block partitions using ds.num_blocks() and ds.repartition().",
                    ],
                ),
                Exercise(
                    name="data02",
                    title="map vs map_batches (PyArrow Vectorization)",
                    path="exercises/08_ray_data/data02.py",
                    chapter_name="08_ray_data",
                    hints=[
                        "Use ds.map_batches(fn, batch_format='numpy' or 'pyarrow') for vectorized processing.",
                        "map_batches processes entire blocks at once, avoiding per-item Python overhead.",
                    ],
                ),
                Exercise(
                    name="data03",
                    title="Stateful Transforms with ActorPoolStrategy",
                    path="exercises/08_ray_data/data03.py",
                    chapter_name="08_ray_data",
                    hints=[
                        "Pass compute=ray.data.ActorPoolStrategy(min_size=2, max_size=4) to ds.map_batches().",
                        "Stateful actor transforms load models/weights once per worker.",
                    ],
                ),
                Exercise(
                    name="data04",
                    title="Streaming Pipelines & Backpressure",
                    path="exercises/08_ray_data/data04.py",
                    chapter_name="08_ray_data",
                    hints=[
                        "Ray Data streams execution across stages to keep memory footprint bounded.",
                        "Use dataset pipeline operations to process infinite or large-scale data streams.",
                    ],
                ),
                Exercise(
                    name="data05",
                    title="PyTorch DataLoader Interop (iter_torch_batches)",
                    path="exercises/08_ray_data/data05.py",
                    chapter_name="08_ray_data",
                    hints=[
                        "Use ds.iter_torch_batches(batch_size=32) for zero-copy streaming into PyTorch.",
                        "Specify dtypes to ensure tensors match expected model input types.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=9,
            name="09_ml_from_scratch",
            title="Distributed ML Primitives from Scratch",
            description="Parameter servers, gradient aggregation, All-Reduce, and data-parallel training",
            exercises=[
                Exercise(
                    name="ml_scratch01",
                    title="Distributed Parameter Server",
                    path="exercises/09_ml_from_scratch/ml_scratch01.py",
                    chapter_name="09_ml_from_scratch",
                    hints=[
                        "Create a ParameterServer actor that holds current weights and applies updates.",
                        "Worker tasks compute gradients and push updates to the ParameterServer.",
                    ],
                ),
                Exercise(
                    name="ml_scratch02",
                    title="Async vs Sync Gradient Averaging",
                    path="exercises/09_ml_from_scratch/ml_scratch02.py",
                    chapter_name="09_ml_from_scratch",
                    hints=[
                        "In synchronous training, wait for all workers before updating weights.",
                        "In asynchronous training, update weights immediately upon receiving worker gradients.",
                    ],
                ),
                Exercise(
                    name="ml_scratch03",
                    title="Ring All-Reduce Implementation",
                    path="exercises/09_ml_from_scratch/ml_scratch03.py",
                    chapter_name="09_ml_from_scratch",
                    hints=[
                        "Ring All-Reduce splits tensors into N chunks and passes them around a logical ring.",
                        "Includes two phases: Scatter-Reduce followed by Allgather.",
                    ],
                ),
                Exercise(
                    name="ml_scratch04",
                    title="Distributed Data-Parallel Trainer",
                    path="exercises/09_ml_from_scratch/ml_scratch04.py",
                    chapter_name="09_ml_from_scratch",
                    hints=[
                        "Assign training data shards to multiple worker actors.",
                        "Average gradients across workers after each batch or epoch.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=10,
            name="10_ray_train_and_tune",
            title="Ray Train & Distributed Deep Learning",
            description="TorchTrainer, ScalingConfig, distributed DataLoader, and model checkpointing",
            exercises=[
                Exercise(
                    name="train01",
                    title="PyTorch TorchTrainer & ScalingConfig",
                    path="exercises/10_ray_train_and_tune/train01.py",
                    chapter_name="10_ray_train_and_tune",
                    hints=[
                        "Use ray.train.torch.TorchTrainer(train_loop_per_worker=..., scaling_config=...).",
                        "Configure ray.train.ScalingConfig(num_workers=2, use_gpu=False).",
                    ],
                ),
                Exercise(
                    name="train02",
                    title="Distributed DataLoader via DataConfig",
                    path="exercises/10_ray_train_and_tune/train02.py",
                    chapter_name="10_ray_train_and_tune",
                    hints=[
                        "Pass datasets={'train': dataset} to TorchTrainer.",
                        "In the train loop, call ray.train.get_dataset_shard('train') to get the worker's data shard.",
                    ],
                ),
                Exercise(
                    name="train03",
                    title="Multi-Worker Gradient Sync & Metrics",
                    path="exercises/10_ray_train_and_tune/train03.py",
                    chapter_name="10_ray_train_and_tune",
                    hints=[
                        "Wrap model with ray.train.torch.prepare_model(model).",
                        "Report metrics with ray.train.report({'loss': loss.item()}).",
                    ],
                ),
                Exercise(
                    name="train04",
                    title="Distributed Checkpointing & Fault Recovery",
                    path="exercises/10_ray_train_and_tune/train04.py",
                    chapter_name="10_ray_train_and_tune",
                    hints=[
                        "Report checkpoints with ray.train.report(metrics, checkpoint=Checkpoint.from_directory(...)).",
                        "Resume training from a Checkpoint object upon failure.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=11,
            name="11_ray_tune",
            title="Ray Tune: Scalable Hyperparameter Tuning",
            description="Search spaces, distributed trials, ASHA schedulers, and Population-Based Training",
            exercises=[
                Exercise(
                    name="tune01",
                    title="Tune Search Spaces & Distributed Trials",
                    path="exercises/11_ray_tune/tune01.py",
                    chapter_name="11_ray_tune",
                    hints=[
                        "Define search space using tune.uniform(), tune.choice(), or tune.loguniform().",
                        "Execute trials with ray.tune.Tuner(trainable, param_space=...).fit().",
                    ],
                ),
                Exercise(
                    name="tune02",
                    title="ASHA / HyperBand Schedulers",
                    path="exercises/11_ray_tune/tune02.py",
                    chapter_name="11_ray_tune",
                    hints=[
                        "Configure tune.schedulers.ASHAScheduler(metric='loss', mode='min', max_t=100).",
                        "Early stopping terminates poorly performing trials automatically.",
                    ],
                ),
                Exercise(
                    name="tune03",
                    title="Population-Based Training (PBT)",
                    path="exercises/11_ray_tune/tune03.py",
                    chapter_name="11_ray_tune",
                    hints=[
                        "Use tune.schedulers.PopulationBasedTraining to mutate hyperparameters dynamically.",
                        "Underperforming trials copy weights and explore mutations of top performers.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=12,
            name="12_ray_serve",
            title="Ray Serve & Production Model Serving",
            description="Deployments, HTTP ingress, request batching, DAG pipelines, streaming, and autoscaling",
            exercises=[
                Exercise(
                    name="serve01",
                    title="Ray Serve Deployments & HTTP Ingress",
                    path="exercises/12_ray_serve/serve01.py",
                    chapter_name="12_ray_serve",
                    hints=[
                        "Use @serve.deployment decorator on class or function.",
                        "Deploy application with serve.run(Deployment.bind()).",
                    ],
                ),
                Exercise(
                    name="serve02",
                    title="Dynamic Request Batching (@serve.batch)",
                    path="exercises/12_ray_serve/serve02.py",
                    chapter_name="12_ray_serve",
                    hints=[
                        "Decorate method with @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.1).",
                        "Coalesces concurrent incoming HTTP requests into a single batch.",
                    ],
                ),
                Exercise(
                    name="serve03",
                    title="Multi-Model Composable Pipelines (DAGs)",
                    path="exercises/12_ray_serve/serve03.py",
                    chapter_name="12_ray_serve",
                    hints=[
                        "Compose deployments by passing bound handles: Pipeline.bind(step1.bind(), step2.bind()).",
                        "Execute multi-stage preprocessing, inference, and postprocessing pipelines.",
                    ],
                ),
                Exercise(
                    name="serve04",
                    title="Streaming Responses with FastApi & Generators",
                    path="exercises/12_ray_serve/serve04.py",
                    chapter_name="12_ray_serve",
                    hints=[
                        "Yield chunks from generator methods or return StreamingResponse.",
                        "Stream tokens in real time from LLM serving endpoints.",
                    ],
                ),
                Exercise(
                    name="serve05",
                    title="Serve Autoscaling Policies",
                    path="exercises/12_ray_serve/serve05.py",
                    chapter_name="12_ray_serve",
                    hints=[
                        "Configure autoscaling_config in @serve.deployment or Deployment.options().",
                        "Set target_ongoing_requests, min_replicas, and max_replicas.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=13,
            name="13_observability_and_debugging",
            title="Observability, Profiling & Memory Debugging",
            description="Chrome execution timelines, memory debugging, and Ray metrics",
            exercises=[
                Exercise(
                    name="perf01",
                    title="Ray Execution Profiling & Chrome Timelines",
                    path="exercises/13_observability_and_debugging/perf01.py",
                    chapter_name="13_observability_and_debugging",
                    hints=[
                        "Call ray.timeline(filename='timeline.json') to dump chrome tracing profiling data.",
                        "Open the JSON trace in chrome://tracing or Perfetto to inspect task durations and scheduling gaps.",
                    ],
                ),
                Exercise(
                    name="perf02",
                    title="Diagnosing Memory Leaks with ray memory",
                    path="exercises/13_observability_and_debugging/perf02.py",
                    chapter_name="13_observability_and_debugging",
                    hints=[
                        "Use ray._private.internal_api.memory_summary() or CLI ray memory to inspect memory.",
                        "Check for object store leaks from uncollected ObjectRefs.",
                    ],
                ),
                Exercise(
                    name="perf03",
                    title="Ray Metrics & Prometheus Exports",
                    path="exercises/13_observability_and_debugging/perf03.py",
                    chapter_name="13_observability_and_debugging",
                    hints=[
                        "Query Ray cluster state using ray.util.state.list_tasks() and list_actors().",
                        "Monitor task state distributions, actor health, and queue depths.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=14,
            name="14_kuberay",
            title="KubeRay & Cloud-Native Ray on Kubernetes",
            description="Deploying, scaling, and operating Ray workloads on Kubernetes with KubeRay",
            exercises=[
                Exercise(
                    name="kuberay01",
                    title="RayCluster Custom Resource (CRD)",
                    path="exercises/14_kuberay/kuberay01.py",
                    chapter_name="14_kuberay",
                    hints=[
                        "Define RayCluster spec with headGroupSpec and workerGroupSpecs.",
                        "Specify CPU/memory resource requests and limits in pod templates.",
                        "Validate Ray version and container image compatibility.",
                    ],
                ),
                Exercise(
                    name="kuberay02",
                    title="RayJob CRD & Batch Job Lifecycle",
                    path="exercises/14_kuberay/kuberay02.py",
                    chapter_name="14_kuberay",
                    hints=[
                        "Configure entrypoint command and runtime_env in RayJob spec.",
                        "Enable shutdownAfterJobFinishes for ephemeral batch clusters.",
                        "Monitor job status and retrieve task logs via Kubernetes API.",
                    ],
                ),
                Exercise(
                    name="kuberay03",
                    title="RayService CRD & Zero-Downtime Serving",
                    path="exercises/14_kuberay/kuberay03.py",
                    chapter_name="14_kuberay",
                    hints=[
                        "Define RayService spec embedding RayClusterSpec and serveConfigV2.",
                        "Configure multi-application serving routes and health checks.",
                        "Perform zero-downtime rolling upgrades using declarative spec updates.",
                    ],
                ),
                Exercise(
                    name="kuberay04",
                    title="Autoscaling with KEDA & Ray Autoscaler",
                    path="exercises/14_kuberay/kuberay04.py",
                    chapter_name="14_kuberay",
                    hints=[
                        "Configure Ray Autoscaler with minReplicas and maxReplicas per worker group.",
                        "Integrate KEDA ScaledObject for external queue metrics.",
                        "Test dynamic scale-up under load and graceful scale-down.",
                    ],
                ),
                Exercise(
                    name="kuberay05",
                    title="Kubernetes Fault Tolerance & Pod Evictions",
                    path="exercises/14_kuberay/kuberay05.py",
                    chapter_name="14_kuberay",
                    hints=[
                        "Configure GCS fault tolerance using external storage (Redis/etcd).",
                        "Simulate worker pod eviction and verify automatic rescheduling.",
                        "Ensure object lineage reconstruction completes without data loss.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=15,
            name="15_vllm_and_llms",
            title="Distributed LLM Serving & vLLM",
            description="Tensor Parallelism, PagedAttention, Multi-LoRA, and Speculative Decoding",
            exercises=[
                Exercise(
                    name="vllm01",
                    title="Tensor Parallelism & Worker Actor Groups",
                    path="exercises/15_vllm_and_llms/vllm01.py",
                    chapter_name="15_vllm_and_llms",
                    hints=[
                        "Shard W1 along columns (axis 1) and W2 along rows (axis 0) across world_size workers.",
                        "In TPWorker.forward(x), compute h_shard = x @ self.w1_shard and z_shard = h_shard @ self.w2_shard.",
                        "In tensor_parallel_forward, dispatch worker forward passes and sum (all-reduce) results across ranks.",
                    ],
                ),
                Exercise(
                    name="vllm02",
                    title="PagedAttention & KV-Cache Block Management",
                    path="exercises/15_vllm_and_llms/vllm02.py",
                    chapter_name="15_vllm_and_llms",
                    hints=[
                        "Slice prompt tokens into chunks of block_size and check self.prefix_cache for matching prefix blocks.",
                        "When appending tokens, allocate a new physical block only when crossing a block boundary ((curr_len - 1) % block_size == 0 or len % block_size == 0).",
                        "Translate logical token index to physical block and offset: logical_token_idx // block_size, logical_token_idx % block_size.",
                        "In free_sequence, decrement ref counts and return blocks with ref_count == 0 to self.free_blocks.",
                    ],
                ),
                Exercise(
                    name="vllm03",
                    title="Dynamic Multi-LoRA Adapter Serving",
                    path="exercises/15_vllm_and_llms/vllm03.py",
                    chapter_name="15_vllm_and_llms",
                    hints=[
                        "Calculate scaling factor as alpha / float(lora_a.shape[1]).",
                        "Use self.adapter_cache.popitem(last=False) to evict the oldest adapter when cache is full.",
                        "In forward(x, adapter_id), compute base_output = x @ self.base_weight and add scaling * ((x @ lora_a) @ lora_b) if adapter_id is given.",
                        "Call self.adapter_cache.move_to_end(adapter_id) on cache hits to maintain LRU access ordering.",
                    ],
                ),
                Exercise(
                    name="vllm04",
                    title="Speculative Decoding with Draft & Target Workers",
                    path="exercises/15_vllm_and_llms/vllm04.py",
                    chapter_name="15_vllm_and_llms",
                    hints=[
                        "Generate k draft candidate tokens using draft_worker.generate_draft.remote(sequence, k).",
                        "Evaluate candidate tokens in parallel using target_worker.evaluate_candidates.remote(sequence, draft_tokens).",
                        "Compare draft tokens against target predictions; on mismatch, append the target correction and break out of the draft loop.",
                        "If all draft tokens are accepted and the sequence is not full, append the target bonus token.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=16,
            name="16_fsdp_and_deepspeed",
            title="DeepSpeed & PyTorch FSDP",
            description="Fully Sharded Data Parallel, ZeRO Memory Optimization, Mixed Precision, and Fault Recovery",
            exercises=[
                Exercise(
                    name="fsdp01",
                    title="PyTorch FSDP with Ray Train ScalingConfig",
                    path="exercises/16_fsdp_and_deepspeed/fsdp01.py",
                    chapter_name="16_fsdp_and_deepspeed",
                    hints=[
                        "Create a size_based_auto_wrap_policy using functools.partial(size_based_auto_wrap_policy, min_num_params=min_num_params).",
                        "Wrap model with FullyShardedDataParallel(model, auto_wrap_policy=auto_wrap_policy, sharding_strategy=sharding_strategy, device_id=torch.device('cpu')).",
                        "In train_loop, optimize the FSDP model across epochs, report metrics with ray.train.report(), and return initial and final loss.",
                    ],
                ),
                Exercise(
                    name="fsdp02",
                    title="DeepSpeed ZeRO-1 / ZeRO-2 / ZeRO-3 Memory Partitioning",
                    path="exercises/16_fsdp_and_deepspeed/fsdp02.py",
                    chapter_name="16_fsdp_and_deepspeed",
                    hints=[
                        "Calculate memory: ZeRO-0 (p+g+3p), ZeRO-1 (p+g+3p/N), ZeRO-2 (p+g/N+3p/N), ZeRO-3 (p/N+g/N+3p/N).",
                        "In ZeROWorker.step(), update m and v moments, apply bias corrections (1 - beta^t), and update param_shard.",
                        "In reduce_scatter, average gradients across worker lists and split into world_size equal shards.",
                        "In zero_stage3_distributed_step, dispatch .step.remote to worker actors and all-gather updated shards.",
                    ],
                ),
                Exercise(
                    name="fsdp03",
                    title="Mixed Precision & Activation Checkpointing",
                    path="exercises/16_fsdp_and_deepspeed/fsdp03.py",
                    chapter_name="16_fsdp_and_deepspeed",
                    hints=[
                        "Use torch.utils.checkpoint.checkpoint(block, x, use_reentrant=False) when use_checkpointing and model.training are True.",
                        "Use torch.autograd.graph.saved_tensors_hooks(pack_hook, unpack_hook) to track saved activation tensor bytes and count.",
                        "Run forward pass inside torch.autocast(device_type='cpu', dtype=torch.bfloat16, enabled=use_autocast) in train_step.",
                    ],
                ),
                Exercise(
                    name="fsdp04",
                    title="Elastic Fault-Tolerant Distributed Checkpoints",
                    path="exercises/16_fsdp_and_deepspeed/fsdp04.py",
                    chapter_name="16_fsdp_and_deepspeed",
                    hints=[
                        "In save_sharded_checkpoint, save rank_{rank}_model.pt and rank_{rank}_optim.pt, and have rank 0 write metadata.json.",
                        "In load_sharded_checkpoint, read metadata.json and load the local rank model and optimizer tensors.",
                        "In ShardedTrainWorker, save and restore local weight_shard and optimizer state dict.",
                    ],
                ),
            ],
        ),
        Chapter(
            number=17,
            name="17_multimodal_and_vectors",
            title="Multimodal & Vector Ray Data",
            description="Streaming Multimodal ETL, ActorPool Batch Embeddings, Length Bucketing, and Vector Stores",
            exercises=[
                Exercise(
                    name="data_genai01",
                    title="Streaming Multimodal Image & Audio ETL",
                    path="exercises/17_multimodal_and_vectors/data_genai01.py",
                    chapter_name="17_multimodal_and_vectors",
                    hints=[
                        "Standardize image: (batch['image'].astype(np.float32) / 255.0 - mean) / std where mean/std are shaped (1, 3, 1, 1).",
                        "Compute log spectrogram using np.log1p(np.maximum(0.0, batch['spectrogram'])).",
                        "Wrap NumPy arrays in pa.Table using ArrowTensorArray.from_numpy(batch['image']) and ArrowTensorArray.from_numpy(batch['spectrogram']).",
                        "Stream dataset batches lazily with ds.iter_batches(batch_size=batch_size, batch_format='numpy').",
                    ],
                ),
                Exercise(
                    name="data_genai02",
                    title="Accelerated Batch Embeddings with ActorPoolStrategy",
                    path="exercises/17_multimodal_and_vectors/data_genai02.py",
                    chapter_name="17_multimodal_and_vectors",
                    hints=[
                        "Initialize nn.Linear(in_features, embedding_dim, bias=False), call self.model.eval(), and record os.getpid().",
                        "Compute embeddings in torch.no_grad() and apply torch.nn.functional.normalize(emb, p=2, dim=-1) if normalize is True.",
                        "Map BatchEmbeddingExtractor over ds using compute=ray.data.ActorPoolStrategy(min_size=min_workers, max_size=max_workers).",
                    ],
                ),
                Exercise(
                    name="data_genai03",
                    title="Dynamic Token Length Bucketing & Padding Optimization",
                    path="exercises/17_multimodal_and_vectors/data_genai03.py",
                    chapter_name="17_multimodal_and_vectors",
                    hints=[
                        "Find max_len = max(len(toks) for toks in batch['tokens']) for the current micro-batch.",
                        "Pad sequences with pad_token_id and create binary attention masks (1 for real token, 0 for padding).",
                        "Compute padding ratio as total_pad / (total_actual + total_pad).",
                        "Sort dataset using ds.sort('seq_len') to cluster sequences with similar token lengths into adjacent batches.",
                    ],
                ),
                Exercise(
                    name="data_genai04",
                    title="Streaming Parallel Ingestion into Vector Databases",
                    path="exercises/17_multimodal_and_vectors/data_genai04.py",
                    chapter_name="17_multimodal_and_vectors",
                    hints=[
                        "In MockVectorIndexStore.upsert_batch, insert (doc_id, vector) into self.partitions[partition_id] and return record count.",
                        "In VectorDatabaseDatasink.write, convert blocks via BlockAccessor.for_block(block).to_numpy() and route by doc_id % self.num_partitions.",
                        "Dispatch batch upserts via self.store_actor.upsert_batch.remote(part_id, buffer) and wait for all tasks with ray.get().",
                    ],
                ),
            ],
        ),
    ]
    return Manifest(chapters=chapters)


_MANIFEST: Optional[Manifest] = None


def get_manifest() -> Manifest:
    """Retrieve the singleton curriculum manifest instance, building it if needed."""
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = build_manifest()
    return _MANIFEST


def get_exercise_by_name(name: str) -> Optional[Exercise]:
    """Find an exercise by exact name, exact path, filename, or path suffix."""
    for ex in get_manifest().all_exercises:
        if (
            ex.name == name
            or ex.path == name
            or Path(ex.path).name == name
            or ex.path.endswith(f"/{name}")
        ):
            return ex
    return None


def get_next_exercise(current_name: str) -> Optional[Exercise]:
    """Return the next exercise in the curriculum after the specified exercise."""
    current = get_exercise_by_name(current_name)
    if current is None:
        return None
    exercises = get_manifest().all_exercises
    try:
        idx = exercises.index(current)
    except ValueError:
        return None
    if idx + 1 < len(exercises):
        return exercises[idx + 1]
    return None


def get_previous_exercise(current_name: str) -> Optional[Exercise]:
    """Return the previous exercise in the curriculum before the specified exercise."""
    current = get_exercise_by_name(current_name)
    if current is None:
        return None
    exercises = get_manifest().all_exercises
    try:
        idx = exercises.index(current)
    except ValueError:
        return None
    if idx > 0:
        return exercises[idx - 1]
    return None
