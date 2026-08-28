from pathlib import Path

from scripts.enrich_all_exercises import enrich_file

# ==================== CHAPTER 01: BASICS ====================

enrich_file(
    Path("exercises/01_basics/basics01.py"),
    topic="Ray Initialization & First Remote Task",
    context_why="""
Ray is an open-source unified framework for scaling AI and Python applications.
At its core, Ray turns standard Python functions into asynchronous, distributed
tasks executed across worker processes managed by local Raylet schedulers and
coordinated by the Global Control Store (GCS).

In standard synchronous Python, function execution blocks the main thread. In distributed
computing, operations should be dispatched asynchronously to maximize core utilization.
Decorating a function with `@ray.remote` transforms it into a task that returns a future
(`ObjectRef`) immediately, enabling non-blocking distributed pipelines.
""",
    instructions=[
        "Initialize Ray using `ray.init(ignore_reinit_error=True)`.",
        "Decorate the `square` function with `@ray.remote`.",
        "Submit the task asynchronously with `square.remote(7)` and retrieve the result via `ray.get()`.",
    ],
    todo_replacements=[
        (
            "# TODO: Decorate this function with @ray.remote",
            "# TODO: Decorate this function with @ray.remote\n# WHY: The @ray.remote decorator registers this function with Ray's core worker engine,\n# allowing it to be scheduled asynchronously across worker processes as an independent task.",
        ),
        (
            "# TODO: Initialize Ray",
            "# TODO: Initialize Ray\n    # WHY: ray.init() bootstraps the Raylet scheduler, Plasma in-memory object store,\n    # and connects the driver process to the GCS.",
        ),
        (
            "# TODO: Invoke the remote task and get the ObjectRef",
            "# TODO: Invoke the remote task and get the ObjectRef\n    # WHY: Calling .remote() dispatches the task asynchronously and returns an ObjectRef;\n    # ray.get() resolves the ObjectRef by reading the value from the shared-memory object store.",
        ),
    ],
)

enrich_file(
    Path("exercises/01_basics/basics02.py"),
    topic="ObjectRefs and ray.get() Batch Retrieval",
    context_why="""
In Ray, calling a remote function does NOT return the computed value directly.
Instead, it immediately returns an `ObjectRef`—a lightweight 28-byte unique identifier
representing a future value stored in Ray's distributed Plasma object store.

Calling `ray.get(ref)` sequentially in a loop blocks the driver on each individual task,
defeating parallelism. Instead, Ray allows passing a list of ObjectRefs to `ray.get([ref1, ref2, ...])`.
This batch retrieval instructs the Ray core worker to wait for all objects in parallel and
deserialize them efficiently in a single operation.
""",
    instructions=[
        "Decorate `multiply` with `@ray.remote`.",
        "Launch 5 parallel tasks calculating `i * 10` for `i` in `range(5)` using list comprehension.",
        "Collect the `ObjectRef`s in a list.",
        "Retrieve all 5 results in parallel with a single `ray.get(refs)` call.",
    ],
    todo_replacements=[
        (
            "# TODO: Decorate multiply with @ray.remote",
            "# TODO: Decorate multiply with @ray.remote\n# WHY: Exposing multiply as a remote function allows Ray to distribute each multiplication across worker processes.",
        ),
        (
            "# TODO: Launch 5 parallel tasks",
            "# TODO: Launch 5 parallel tasks\n    # WHY: List comprehension with .remote() immediately schedules all 5 tasks without blocking the driver.",
        ),
        (
            "# TODO: Get all results at once",
            "# TODO: Get all results at once\n    # WHY: Batch ray.get(refs) is significantly more efficient than individual sequential gets.",
        ),
    ],
)

enrich_file(
    Path("exercises/01_basics/basics03.py"),
    topic="Parallel Pipeline Execution",
    context_why="""
A classic distributed computing anti-pattern is calling `ray.get()` inside a task submission loop:
```python
# ❌ Anti-pattern (Sequential Stall):
for x in data:
    ref = task.remote(x)
    results.append(ray.get(ref))  # Blocks immediately! Destroys concurrency!
```
Calling `ray.get()` synchronously pauses the Python driver process until that specific worker finishes.
To achieve true parallelism across all available CPU cores, you must submit all tasks first to populate
the scheduler's queue, and then wait on the batch of ObjectRefs.
""",
    instructions=[
        "Fix `run_parallel()` so that all tasks are dispatched concurrently before calling `ray.get()`.",
        "Confirm that parallel execution completes significantly faster than sequential execution.",
    ],
    todo_replacements=[
        (
            "# TODO: Refactor this to run all tasks in parallel!",
            "# TODO: Refactor this to run all tasks in parallel!\n    # WHY: Dispatching .remote() across all inputs queues tasks into the Raylet worker pool simultaneously,\n    # allowing multiple CPU cores to compute in parallel before resolving with a single ray.get(refs).",
        )
    ],
)

enrich_file(
    Path("exercises/01_basics/basics04.py"),
    topic="Passing ObjectRefs Directly to Downstream Tasks (DAG Construction)",
    context_why="""
Ray allows constructing dynamic Direct Acyclic Graphs (DAGs) without pulling intermediate data
back to the driver. When you pass an `ObjectRef` directly as an argument to another `@ray.remote` task,
Ray automatically:
1. Infers the data dependency between upstream and downstream tasks.
2. Holds the downstream task in the scheduler until the upstream task completes.
3. Automatically dereferences the `ObjectRef` inside the worker before executing the downstream function.

This avoids transferring megabytes or gigabytes of intermediate data back to the driver node,
preventing memory bottlenecks and high serialization overhead.
""",
    instructions=[
        "Complete `build_pipeline(x, y)` to chain `generate_val`, `add`, and `cube` tasks.",
        "Pass ObjectRefs directly between tasks without calling `ray.get()` in the pipeline builder.",
        "Return the final `ObjectRef`.",
    ],
    todo_replacements=[
        (
            "# TODO: Build the pipeline using ObjectRefs without calling ray.get()",
            "# TODO: Build the pipeline using ObjectRefs without calling ray.get()\n    # WHY: Passing ObjectRefs as arguments creates upstream-downstream task dependencies.\n    # Ray executes the tasks in DAG order and dereferences values directly on worker nodes.",
        )
    ],
)

enrich_file(
    Path("exercises/01_basics/basics05.py"),
    topic="Dynamic Completion Processing with ray.wait()",
    context_why="""
When running heterogeneous distributed tasks with varying runtimes, `ray.get(refs)` blocks until
the slowest task completes. If 99 tasks finish in 10ms and 1 task takes 10s, `ray.get(refs)` forces
the driver to sit idle for 10s before processing any finished data.

`ray.wait(object_refs, num_returns=1, timeout=None)` solves this by returning two lists:
`(ready_refs, unready_refs)` as soon as `num_returns` tasks are completed.
Using a `while unready_refs:` loop enables streaming pipeline architectures, where downstream
processing begins immediately as tasks finish.
""",
    instructions=[
        "Implement `process_as_completed(tasks_config)` using `ray.wait()` inside a `while unready_refs:` loop.",
        "In each iteration, extract completed task IDs from `ready_refs` and update `unready_refs`.",
        "Return task IDs in the order they finished.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement dynamic completion processing using ray.wait()",
            "# TODO: Implement dynamic completion processing using ray.wait()\n    # WHY: ray.wait() returns as soon as num_returns items are ready in the Plasma store,\n    # allowing fast tasks to be handled immediately without waiting for stragglers.",
        )
    ],
)

enrich_file(
    Path("exercises/01_basics/basics06.py"),
    topic="Multiple Return Values in Remote Tasks (num_returns)",
    context_why="""
By default, `@ray.remote` functions return a single `ObjectRef`, even if the Python function
returns a tuple. When downstream tasks only need a subset of the returned data, returning a single
tuple forces all downstream tasks to depend on the entire tuple.

Configuring `@ray.remote(num_returns=N)` instructs Ray to partition the return values into `N`
distinct, independent `ObjectRef`s. Downstream tasks can subscribe to specific return elements,
enabling finer-grained dependency graphs and avoiding unnecessary data transfers.
""",
    instructions=[
        "Configure `split_stats` with `@ray.remote(num_returns=2)`.",
        "Unpack the two returned ObjectRefs: `min_ref, max_ref = split_stats.remote(numbers)`.",
        "Retrieve and verify both values independently.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure split_stats to return 2 ObjectRefs",
            "# TODO: Configure split_stats to return 2 ObjectRefs\n# WHY: Setting num_returns=2 instructs Ray to yield multiple distinct ObjectRefs\n# so downstream workers can depend on individual components independently.",
        )
    ],
)

# ==================== CHAPTER 02: ACTORS ====================

enrich_file(
    Path("exercises/02_actors/actors01.py"),
    topic="Stateful Actor Lifecycle & Remote Classes",
    context_why="""
While Ray tasks are stateless functions, Ray Actors are stateful Python classes.
Decorating a Python class with `@ray.remote` transforms it into a dedicated, long-running
worker process that preserves internal instance state (`self.xxx`) across method calls.

When you call `MyActor.remote(*args)`, Ray provisions a worker process, executes `__init__`,
and returns an `ActorHandle`. Subsequent method invocations `actor.method.remote()` send
messages to the actor's FIFO mailbox and return `ObjectRef` futures.
""",
    instructions=[
        "Decorate `Counter` with `@ray.remote`.",
        "Instantiate `Counter.remote(initial_val=10)` to receive an `ActorHandle`.",
        "Invoke `increment.remote(5)` and `get_count.remote()`, then verify with `ray.get()`.",
    ],
    todo_replacements=[
        (
            "# TODO: Decorate this class with @ray.remote",
            "# TODO: Decorate this class with @ray.remote\n# WHY: Decorating a class with @ray.remote instructs Ray to manage instances as dedicated stateful worker processes.",
        ),
        (
            "# TODO: Instantiate Counter actor",
            "# TODO: Instantiate Counter actor\n    # WHY: Counter.remote(initial_val=10) provisions the worker process and runs __init__ remotely.",
        ),
    ],
)

enrich_file(
    Path("exercises/02_actors/actors02.py"),
    topic="Actor Method Calls & State Mutation",
    context_why="""
In a distributed environment, managing concurrent state safely usually requires complex locking
primitives (mutexes, semaphores). Ray Actors simplify this by executing incoming method calls
sequentially in the exact FIFO order they arrive in the actor's message queue.

Because only one method executes at a time within an actor process, state mutations like
`self.balance += amount` are inherently thread-safe and free from data races without manual locks.
""",
    instructions=[
        "Implement `BankAccount` actor with `deposit`, `withdraw`, `get_balance`, and `get_history` methods.",
        "Perform deposits and withdrawals, and assert accurate final balance and transaction logs.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement the BankAccount actor",
            "# TODO: Implement the BankAccount actor\n# WHY: Ray actors process method calls sequentially, ensuring balance and history remain consistent.",
        )
    ],
)

enrich_file(
    Path("exercises/02_actors/actors03.py"),
    topic="Passing Actor Handles for Distributed Coordination",
    context_why="""
In Ray, `ActorHandle`s are first-class serializable objects that can be passed as arguments
to other remote tasks and actors. Any worker receiving an `ActorHandle` can invoke remote methods
on that shared actor instance.

This pattern is widely used in distributed machine learning for centralized parameter servers,
global metric aggregators, distributed barrier synchronization, and progress tracking.
""",
    instructions=[
        "Define a `MetricTracker` actor that aggregates counts from multiple worker tasks.",
        "Pass the `MetricTracker` handle into multiple concurrent `@ray.remote` tasks.",
        "Verify that all workers successfully reported their progress to the single actor.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement MetricTracker actor and worker task",
            "# TODO: Implement MetricTracker actor and worker task\n# WHY: Passing an ActorHandle across tasks allows decentralized workers to stream state updates to a single coordinator.",
        )
    ],
)

enrich_file(
    Path("exercises/02_actors/actors04.py"),
    topic="Async Actors & Coroutine Concurrency",
    context_why="""
By default, Ray actors execute one method call at a time. If an actor method performs I/O
(e.g., waiting for external REST APIs, database queries, or network requests), the actor sits idle,
blocking all other incoming calls in its mailbox.

Ray solves this with **Async Actors**:
1. Define methods using `async def` and `await`.
2. Configure `@ray.remote(max_concurrency=N)` to allow up to `N` coroutines to run concurrently
   on the actor's single-threaded `asyncio` event loop.
""",
    instructions=[
        "Define an async actor with `@ray.remote(max_concurrency=10)`.",
        "Implement an `async def fetch_data(self, url: str)` method using `await asyncio.sleep(...)`.",
        "Verify that multiple async requests run concurrently with significant speedup over sequential execution.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure AsyncFetcher with max_concurrency",
            "# TODO: Configure AsyncFetcher with max_concurrency\n# WHY: max_concurrency enables Python asyncio coroutines to interleave on a single thread event loop during I/O.",
        )
    ],
)

enrich_file(
    Path("exercises/02_actors/actors05.py"),
    topic="Threaded Actors for Blocking Synchronous I/O",
    context_why="""
While `async def` works for non-blocking coroutines, legacy Python libraries and C-extensions
often make synchronous blocking calls (e.g. OpenCV image processing, blocking DB drivers, `time.sleep`).

Ray supports **Threaded Actors**:
If you define standard synchronous `def` methods (without `async`) AND specify
`@ray.remote(max_concurrency=N)`, Ray provisions an internal `ThreadPool` inside the actor process
to handle up to `N` synchronous invocations concurrently across multiple OS threads.
""",
    instructions=[
        "Define `@ray.remote(max_concurrency=4) class ThreadedComputeActor:`.",
        "Implement synchronous `blocking_task` using `time.sleep(duration)`.",
        "Verify that 4 concurrent tasks execute in parallel on the threaded actor.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure ThreadedComputeActor with max_concurrency",
            "# TODO: Configure ThreadedComputeActor with max_concurrency\n# WHY: Specifying max_concurrency with synchronous def methods spawns a thread pool for concurrent blocking calls.",
        )
    ],
)

enrich_file(
    Path("exercises/02_actors/actors06.py"),
    topic="Detached Named Actors for Cross-Job State",
    context_why="""
Normally, an actor's lifecycle is bound to the driver job that created it. When the driver script exits
or the `ActorHandle` is garbage collected, Ray terminates the actor process.

For persistent infrastructure like shared caches, centralized model registries, or long-lived services,
Ray provides **Named Detached Actors**:
- `Actor.options(name="my_service", lifetime="detached").remote()` creates an actor that outlives the driver.
- Any subsequent client can look up the handle with `ray.get_actor("my_service")`.
""",
    instructions=[
        "Define `GlobalConfigRegistry` actor.",
        'Instantiate it with `options(name="app_config_registry", lifetime="detached")`.',
        'Retrieve the actor by name using `ray.get_actor("app_config_registry")` and verify values.',
    ],
    todo_replacements=[
        (
            "# TODO: Create named detached actor",
            '# TODO: Create named detached actor\n    # WHY: lifetime="detached" decouples actor lifecycle from driver process, registering it in GCS by name.',
        )
    ],
)

enrich_file(
    Path("exercises/02_actors/actors07.py"),
    topic="ActorPool Dynamic Load Balancing",
    context_why="""
When you have multiple worker actors (e.g., loaded neural networks, inference engines) and a batch of
tasks to process, manually tracking which actor is busy and which is idle is complex.

`ray.util.ActorPool` manages an elastic pool of actors, automatically routing each new work item
to whichever actor becomes idle first. This maximizes resource utilization and prevents worker starvation.
""",
    instructions=[
        "Create a list of 3 `Worker` actor handles.",
        "Wrap them in `ray.util.ActorPool(actors)`.",
        "Use `pool.map()` to process a list of inputs and collect transformed outputs.",
    ],
    todo_replacements=[
        (
            "# TODO: Initialize ActorPool and map tasks",
            "# TODO: Initialize ActorPool and map tasks\n    # WHY: ActorPool dynamically balances items across available actor instances as they finish.",
        )
    ],
)

# ==================== CHAPTER 03: OBJECT STORE ====================

enrich_file(
    Path("exercises/03_object_store/object_store01.py"),
    topic="Zero-Copy Plasma Shared Memory Reads",
    context_why="""
Ray features an in-memory shared-memory object store called **Plasma**.
When large NumPy arrays, PyArrow tables, or tensors are stored in Plasma, worker processes on the
same physical machine can read them via memory-mapped shared buffers with **zero memory copies**
and zero deserialization overhead.

This allows multiple worker tasks to read a 10GB dataset concurrently without consuming 10GB RAM per worker.
""",
    instructions=[
        "Allocate a NumPy array and store it in the Plasma object store via `ray.put(arr)`.",
        "Pass the `ObjectRef` to a worker task and verify that the worker receives a read-only view of the data.",
    ],
    todo_replacements=[
        (
            "# TODO: Put array into object store",
            "# TODO: Put array into object store\n    # WHY: ray.put() serializes the array directly into Plasma shared memory for zero-copy access.",
        )
    ],
)

enrich_file(
    Path("exercises/03_object_store/object_store02.py"),
    topic="ray.put() vs Implicit Parameter Serialization",
    context_why="""
When you pass a large Python object (e.g. 50MB array) as a raw argument to 100 remote tasks,
Ray implicitly serializes and copies that 50MB object 100 separate times!

Calling `ref = ray.put(large_data)` once, and then passing `ref` to the 100 tasks, stores the object
in Plasma **exactly once**. All 100 tasks receive lightweight references, reducing network/memory overhead from 5GB to 50MB.
""",
    instructions=[
        "Use `ray.put(large_matrix)` to pre-allocate shared memory before launching multiple worker tasks.",
        "Pass the resulting `ObjectRef` to all tasks.",
    ],
    todo_replacements=[
        (
            "# TODO: Pre-allocate with ray.put()",
            "# TODO: Pre-allocate with ray.put()\n    # WHY: Pre-allocating with ray.put() stores the payload once in Plasma instead of repeating serialization per task.",
        )
    ],
)

enrich_file(
    Path("exercises/03_object_store/object_store03.py"),
    topic="Object Immutability & Safe Buffer Copies",
    context_why="""
To ensure data consistency across concurrent readers without lock contention, objects stored in
Ray's Plasma store are strictly **immutable**. NumPy arrays retrieved from Plasma have their
`flags.writeable` set to `False`.

Attempting to mutate an in-place Plasma buffer directly (`arr[0] = 99`) raises a `ValueError`.
To modify data, workers must explicitly create a mutable copy via `arr.copy()`.
""",
    instructions=[
        "Retrieve an array from Plasma and observe that in-place mutation fails.",
        "Create an explicit copy via `.copy()` before performing mutations.",
    ],
    todo_replacements=[
        (
            "# TODO: Create a safe copy before mutating",
            "# TODO: Create a safe copy before mutating\n    # WHY: Plasma buffers are strictly read-only to prevent concurrent data corruption across worker processes.",
        )
    ],
)

enrich_file(
    Path("exercises/03_object_store/object_store04.py"),
    topic="Plasma Object Spilling & Bounded Capacity",
    context_why="""
The Plasma object store operates in a pre-allocated shared memory partition (typically 30% of system RAM).
When total active objects exceed available Plasma memory, Ray's object manager automatically
**spills** cold objects to local NVMe disk or cloud storage (e.g. S3), restoring them transparently when requested.

Understanding object references and avoiding leaked `ObjectRef`s prevents excessive disk thrashing.
""",
    instructions=[
        "Configure object spilling parameters or observe object lifecycle behavior.",
        "Verify that Ray handles objects larger than individual worker memory seamlessly.",
    ],
    todo_replacements=[
        (
            "# TODO: Handle object store lifecycle",
            "# TODO: Handle object store lifecycle\n    # WHY: Ray automatically manages memory pressure by spilling unpinned objects to secondary storage.",
        )
    ],
)

enrich_file(
    Path("exercises/03_object_store/object_store05.py"),
    topic="Resolving Nested ObjectRefs",
    context_why="""
When a remote task returns another `ObjectRef` (e.g. dynamic task spawning), Ray creates a nested
future: `ObjectRef[ObjectRef[T]]`.

Calling `ray.get()` once only unpacks the outer reference, returning an inner `ObjectRef`.
To obtain the final value, Ray provides automatic dereferencing or double-get patterns.
""",
    instructions=[
        "Implement nested task execution.",
        "Unpack nested `ObjectRef`s to retrieve the underlying payload.",
    ],
    todo_replacements=[
        (
            "# TODO: Resolve nested ObjectRefs",
            "# TODO: Resolve nested ObjectRefs\n    # WHY: Nested ObjectRefs occur when tasks dynamically return futures from other tasks.",
        )
    ],
)

enrich_file(
    Path("exercises/03_object_store/object_store06.py"),
    topic="Custom Object Serializers with ray.util",
    context_why="""
Ray uses PyArrow and Cloudpickle to serialize objects. For complex domain objects, custom C++ types,
or network handles, default pickling can be slow or unsupported.

`ray.util.register_serializer` allows defining custom, highly optimized serialization and deserialization
hooks, ensuring fast transfers and compact memory footprints.
""",
    instructions=[
        "Register a custom serializer and deserializer for a domain data class.",
        "Pass instances through Ray tasks and verify exact reconstruction.",
    ],
    todo_replacements=[
        (
            "# TODO: Register custom serializer",
            "# TODO: Register custom serializer\n    # WHY: Custom serializers bypass generic pickle overhead for domain-specific data structures.",
        )
    ],
)

# ==================== CHAPTER 04: SCHEDULING ====================

enrich_file(
    Path("exercises/04_scheduling_resources/scheduling01.py"),
    topic="Fractional CPUs and Custom Hardware Resources",
    context_why="""
Ray's scheduler treats physical resources as logical quotas. You can specify fractional CPU requirements
(`num_cpus=0.25`), allowing 4 tasks to share a single CPU core, or request custom named resources
(e.g., `resources={"accelerator": 1}`).

This enables fine-grained multi-tenancy, co-locating light I/O workers on shared cores while reserving
dedicated hardware for heavy compute tasks.
""",
    instructions=[
        "Configure a task with fractional CPU requirements (`num_cpus=0.5`).",
        "Launch multiple concurrent tasks and verify that Ray schedules them efficiently.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure fractional resource request",
            "# TODO: Configure fractional resource request\n# WHY: Fractional resources allow packing multiple lightweight workers onto a single core.",
        )
    ],
)

enrich_file(
    Path("exercises/04_scheduling_resources/scheduling02.py"),
    topic="Node Affinity Scheduling Strategy",
    context_why="""
In heterogeneous multi-node clusters, specific nodes may possess specialized hardware (local NVMe scratch,
high-bandwidth networking, or InfiniBand interconnects).

`NodeAffinitySchedulingStrategy` allows pinning tasks or actors to specific cluster nodes by node ID,
or specifying soft affinity preferences.
""",
    instructions=[
        "Retrieve the current node ID via `ray.get_runtime_context().get_node_id()`.",
        "Schedule an actor specifically on that target node using `NodeAffinitySchedulingStrategy`.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure NodeAffinitySchedulingStrategy",
            "# TODO: Configure NodeAffinitySchedulingStrategy\n    # WHY: Node affinity forces the scheduler to dispatch tasks to a designated physical host.",
        )
    ],
)

enrich_file(
    Path("exercises/04_scheduling_resources/scheduling03.py"),
    topic="Placement Groups: STRICT_SPREAD Strategy",
    context_why="""
Placement groups allow reserving compute bundles atomically across cluster nodes.
The `STRICT_SPREAD` strategy guarantees that each bundle in the placement group is placed
on a **completely distinct physical node**.

This is crucial for high-availability services and fault-tolerant replicated systems where no two
worker replicas should share the same fault domain.
""",
    instructions=[
        'Create a placement group with `strategy="STRICT_SPREAD"`.',
        "Schedule worker actors across the placement group bundles.",
    ],
    todo_replacements=[
        (
            "# TODO: Create STRICT_SPREAD placement group",
            "# TODO: Create STRICT_SPREAD placement group\n    # WHY: STRICT_SPREAD guarantees that bundles are physically isolated on separate nodes for failure resilience.",
        )
    ],
)

enrich_file(
    Path("exercises/04_scheduling_resources/scheduling04.py"),
    topic="Placement Groups: STRICT_PACK Strategy",
    context_why="""
Conversely, the `STRICT_PACK` strategy guarantees that all bundles in the placement group are
co-located on the **same physical node**.

This minimizes network latency and maximizes shared-memory Plasma throughput for tightly-coupled
collaborative tasks (e.g. multi-GPU model parallel forward passes).
""",
    instructions=[
        'Create a placement group with `strategy="STRICT_PACK"`.',
        "Schedule actors into the co-located bundles.",
    ],
    todo_replacements=[
        (
            "# TODO: Create STRICT_PACK placement group",
            "# TODO: Create STRICT_PACK placement group\n    # WHY: STRICT_PACK guarantees zero-network IPC latency by packing workers onto the identical physical machine.",
        )
    ],
)

enrich_file(
    Path("exercises/04_scheduling_resources/scheduling05.py"),
    topic="Gang Scheduling with Multi-Bundle Placement Groups",
    context_why="""
Distributed training algorithms (e.g. PyTorch DDP, Ring All-Reduce) require all $N$ workers to be
ready simultaneously before training begins. If only $N-1$ workers are scheduled, the job deadlocks.

Ray's placement groups provide **gang scheduling**: `ray.util.placement_group(...)` waits until ALL
bundles can be reserved atomically before allowing any worker to start, preventing resource deadlock.
""",
    instructions=[
        "Define a multi-bundle placement group and wait for readiness using `pg.ready()`.",
        "Schedule gang workers into the reserved bundles.",
    ],
    todo_replacements=[
        (
            "# TODO: Wait for placement group readiness",
            "# TODO: Wait for placement group readiness\n    # WHY: Gang scheduling ensures all distributed worker slots are atomically secured before execution starts.",
        )
    ],
)

enrich_file(
    Path("exercises/04_scheduling_resources/scheduling06.py"),
    topic="Dynamic Runtime Environments (runtime_env)",
    context_why="""
Different tasks or actors in the same cluster may require conflicting third-party packages, environment
variables, or local directory dependencies.

Ray `runtime_env` dynamically provisions isolated virtual environments, installs pip packages on the fly,
and syncs files to worker nodes before executing the task.
""",
    instructions=[
        'Configure `@ray.remote(runtime_env={"env_vars": {...}})`.',
        "Verify that worker processes execute with the custom environment variables.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure runtime_env on remote task",
            "# TODO: Configure runtime_env on remote task\n# WHY: runtime_env isolates environment variables and dependencies dynamically per task or actor.",
        )
    ],
)

# ==================== CHAPTER 05: FAULT TOLERANCE ====================

enrich_file(
    Path("exercises/05_fault_tolerance/fault01.py"),
    topic="Automatic Task Retries & Idempotency",
    context_why="""
Transient hardware glitches, spot instance interruptions, or network drops can cause remote tasks to fail.
Ray provides built-in task retries:
`@ray.remote(max_retries=3, retry_exceptions=True)` instructs Ray to automatically resubmit failed tasks.

Tasks must be **idempotent** (producing the same result when executed multiple times without side-effects).
""",
    instructions=[
        "Configure `max_retries=3` on an unreliable task.",
        "Verify that transient worker exceptions are caught and retried until successful.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure max_retries on task",
            "# TODO: Configure max_retries on task\n# WHY: max_retries enables automatic fault-tolerant retries for transient failures without driver crashes.",
        )
    ],
)

enrich_file(
    Path("exercises/05_fault_tolerance/fault02.py"),
    topic="Actor Restarts & State Recovery",
    context_why="""
Unlike stateless tasks, when a stateful actor process crashes, its in-memory state is lost.
Configuring `@ray.remote(max_restarts=2)` instructs Ray to automatically restart the actor process.

Actors can recover state by loading checkpoints from persistent storage inside their `__init__` method.
""",
    instructions=[
        "Configure `max_restarts=2` on a stateful actor.",
        "Simulate worker process failure and verify that Ray restarts the actor.",
    ],
    todo_replacements=[
        (
            "# TODO: Configure max_restarts on actor",
            "# TODO: Configure max_restarts on actor\n# WHY: max_restarts instructs GCS to restart the actor process if its underlying worker node crashes.",
        )
    ],
)

enrich_file(
    Path("exercises/05_fault_tolerance/fault03.py"),
    topic="Lineage Reconstruction of Lost Objects",
    context_why="""
If a cluster node fails and its Plasma object store memory is destroyed, Ray does not necessarily
fail the entire job. Ray tracks the **lineage DAG** (the graph of tasks that produced the object).

Ray automatically re-executes the upstream task graph to reconstruct the missing `ObjectRef` transparently!
""",
    instructions=[
        "Understand Ray's lineage recomputation mechanics.",
        "Verify that lost object references are reconstructed on demand.",
    ],
    todo_replacements=[
        (
            "# TODO: Verify lineage reconstruction",
            "# TODO: Verify lineage reconstruction\n    # WHY: Lineage tracking enables automatic recomputation of lost intermediate objects upon node failure.",
        )
    ],
)

enrich_file(
    Path("exercises/05_fault_tolerance/fault04.py"),
    topic="Spot Instance Preemption & Graceful Draining",
    context_why="""
In cloud environments, spot/preemptible instances can be terminated with minimal notice (e.g. 30 seconds).
Ray intercepts SIGTERM signals and coordinates graceful node draining, evicting actors and flushing
object caches before node shutdown.
""",
    instructions=[
        "Implement a preemption-aware actor with clean shutdown handlers.",
    ],
    todo_replacements=[
        (
            "# TODO: Implement preemption handling",
            "# TODO: Implement preemption handling\n    # WHY: Intercepting preemption signals allows workers to checkpoint state before node termination.",
        )
    ],
)

# ==================== CHAPTER 06: CLUSTER ARCHITECTURE ====================

enrich_file(
    Path("exercises/06_cluster_architecture/cluster01.py"),
    topic="Head Node vs Worker Node Architecture & GCS",
    context_why="""
A Ray cluster consists of one **Head Node** and zero or more **Worker Nodes**.
The Head node hosts the Global Control Store (GCS), which manages metadata, actor registration,
and cluster-wide heartbeat monitoring. Every node runs a **Raylet** (local scheduler and Plasma store).
""",
    instructions=[
        "Query cluster state using `ray.nodes()`.",
        "Inspect node IP addresses, alive status, and available compute resources.",
    ],
    todo_replacements=[
        (
            "# TODO: Inspect cluster node table",
            "# TODO: Inspect cluster node table\n    # WHY: ray.nodes() queries the GCS to discover all registered head and worker nodes in the cluster.",
        )
    ],
)

enrich_file(
    Path("exercises/06_cluster_architecture/cluster02.py"),
    topic="Multi-Node Testing with Cluster Utils",
    context_why="""
Testing distributed edge cases (network partitions, multi-node scheduling, cross-node serialization)
locally on a single machine can be challenging.

`ray.cluster_utils.Cluster` allows starting simulated multi-node Ray clusters directly inside
Python test processes, adding and removing worker nodes programmatically.
""",
    instructions=[
        "Instantiate a simulated 2-node cluster with `ray.cluster_utils.Cluster`.",
        "Verify task distribution across the simulated nodes.",
    ],
    todo_replacements=[
        (
            "# TODO: Launch simulated multi-node cluster",
            "# TODO: Launch simulated multi-node cluster\n    # WHY: Cluster utils provide high-fidelity multi-node simulation for unit and integration testing.",
        )
    ],
)

enrich_file(
    Path("exercises/06_cluster_architecture/cluster03.py"),
    topic="Ray Job Submission API",
    context_why="""
In production, machine learning jobs are submitted to remote Ray clusters using the **Job Submission API**
(`ray.job_submission.JobSubmissionClient`).

This client allows submitting scripts, packaging dependencies via `runtime_env`, streaming remote logs,
and monitoring job status via REST over HTTP (port 8265).
""",
    instructions=[
        "Submit a job programmatically using `JobSubmissionClient`.",
        "Poll job status until success and inspect execution logs.",
    ],
    todo_replacements=[
        (
            "# TODO: Submit job via JobSubmissionClient",
            "# TODO: Submit job via JobSubmissionClient\n    # WHY: The Job Submission API provides standard REST submission for production ML orchestrators (Airflow, Kubeflow).",
        )
    ],
)

enrich_file(
    Path("exercises/06_cluster_architecture/cluster04.py"),
    topic="Cross-Node Object Transfers & Networking",
    context_why="""
When a worker task on Node B accesses an `ObjectRef` created on Node A, Ray's object manager
automatically initiates an asynchronous point-to-point network transfer between Plasma stores.

Understanding cross-node transfer overhead is critical for designing latency-sensitive distributed algorithms.
""",
    instructions=[
        "Measure and observe cross-node object transfer dynamics.",
    ],
    todo_replacements=[
        (
            "# TODO: Measure object transfer",
            "# TODO: Measure object transfer\n    # WHY: Object managers stream data across nodes asynchronously over high-speed TCP/gRPC channels.",
        )
    ],
)

print("Chapters 01 to 06 enriched successfully!")
