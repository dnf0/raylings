# Chapter 02: Stateful Actors, Concurrency Groups & Lifecycle

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; `@ray.remote` Classes, Persistent State, Concurrency Groups, and Actor Lifecycles
-   :material-play-circle: **Interactive Challenges** &bull; 7 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=2){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

Unlike stateless remote tasks, **Actors** are stateful worker processes instantiated via `@ray.remote` class declarations. Each actor runs in a dedicated worker process, maintaining its internal state between method invocations.

```mermaid
flowchart LR
    Driver["Driver Program<br/><code>actor = Counter.remote()</code>"] -->|"1. Direct gRPC Call"| Mailbox["FIFO Mailbox<br/>(Ordered Queue)"]
    Mailbox -->|"2. Process Sequential Calls"| State[("Actor In-Memory State<br/><code>self.value += 1</code>")]
    State -->|"3. Write Return Value"| Plasma["Plasma Object Store<br/>(/dev/shm)"]
    Plasma -.->|"4. Resolve Future"| ObjectRef["ObjectRef Future"]

    style Driver fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style Mailbox fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style State fill:#0f172a,stroke:#34d399,stroke-width:2px,color:#f8fafc
    style Plasma fill:#1e1e38,stroke:#c084fc,stroke-width:2px,color:#f8fafc
    style ObjectRef fill:#0f172a,stroke:#818cf8,stroke-width:1px,stroke-dasharray: 5 5,color:#f8fafc
```

> **Diagram Walkthrough & Core Concepts:**
> - **Direct Point-to-Point Invocations**: After initialization, method calls from callers bypass the centralized scheduler and communicate directly with the actor process via point-to-point gRPC.
> - **FIFO Mailbox & Race-Free State**: Incoming method calls are queued into a sequential FIFO mailbox, ensuring that mutations to `self.value` are deterministic and free of race conditions without requiring manual lock management.
> - **Persistent In-Memory State**: The actor worker process stays alive across multiple remote method invocations, preserving warm state (such as neural network weights, database connections, or accumulators).

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from typing import Dict

@ray.remote(num_cpus=1, max_concurrency=10)
class MetricsTracker:
    """Stateful actor aggregating metrics across distributed workers."""
    def __init__(self, cluster_name: str) -> None:
        self.cluster_name = cluster_name
        self.counters: Dict[str, int] = {}

    def record_event(self, event_name: str, count: int = 1) -> int:
        """Atomically updates event count in the actor state."""
        self.counters[event_name] = self.counters.get(event_name, 0) + count
        return self.counters[event_name]

    def get_summary(self) -> Dict[str, int]:
        """Returns snapshot of current event counters."""
        return dict(self.counters)

# 1. Instantiate the actor on a dedicated worker
tracker = MetricsTracker.remote("prod-cluster-01")

# 2. Invoke stateful methods asynchronously
f1 = tracker.record_event.remote("requests", 10)
f2 = tracker.record_event.remote("errors", 1)

# 3. Retrieve final state
print(ray.get(tracker.get_summary.remote()))
```

### Key API Parameter Reference

- **`@ray.remote(max_concurrency=N)`**: Enables multi-threaded / asyncio execution of up to `N` concurrent method calls within the same actor.
- **`actor = ActorClass.remote(*init_args)`**: Instantiates the actor worker and executes its `__init__`.
- **`actor.method.remote(*args)`**: Submits a method call to the actor's task queue.
- **`ray.kill(actor)`**: Forces immediate termination of the actor worker process.

---

## 3. Production Best Practices & Hardening Guidelines

1. **Avoid Hotspot Bottlenecks**: Do not route millions of high-frequency calls to a single actor; use actor pools or sharded routers to distribute throughput.
2. **Use `async def` for I/O Bound Actors**: If an actor makes HTTP or database calls, declare methods with `async def` and set `max_concurrency`.
3. **Manage Actor Lifecycle Explicitly**: Kill idle or temporary actors with `ray.kill(actor)` to reclaim cluster memory and CPU slots.
4. **Decouple Heavy Compute from State**: For intensive calculations, dispatch stateless remote tasks from within the actor rather than blocking the actor's event loop.
5. **Implement Named Detached Actors Carefully**: Use `ray.get_actor(name)` for persistent services, but ensure cleanup routines handle orphaned instances.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **Actor Deadlock**:
   - *Symptom*: Method calls hang indefinitely.
   - *Fix*: Avoid circular invocations between two synchronous actors. Use `max_concurrency > 1` or `async def` if actors must communicate bidirectionally.
2. **Actor Worker Out-of-Memory (`ActorDiedError`)**:
   - *Symptom*: Ray raises `ActorDiedError` when sending requests.
   - *Fix*: Check for unbounded list growth in actor attributes; configure `memory` resource limits on the `@ray.remote` decorator.
3. **Slow Method Dispatch**:
   - *Symptom*: High latency on actor invocations.
   - *Fix*: Profile actor queue depth using Ray dashboard metrics; split high-volume read queries from state mutation calls.

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `actors01` | Stateful Actor Lifecycle | [**Open Exercise actors01 →**](../playground/index.html?exercise=actors01) |
| `actors02` | Actor Method Calls & State Mutation | [**Open Exercise actors02 →**](../playground/index.html?exercise=actors02) |
| `actors03` | Passing Actor Handles | [**Open Exercise actors03 →**](../playground/index.html?exercise=actors03) |
| `actors04` | Async Actors & Concurrency | [**Open Exercise actors04 →**](../playground/index.html?exercise=actors04) |
| `actors05` | Threaded Actors for Blocking I/O | [**Open Exercise actors05 →**](../playground/index.html?exercise=actors05) |
| `actors06` | Detached Named Actors | [**Open Exercise actors06 →**](../playground/index.html?exercise=actors06) |
| `actors07` | ActorPool Dynamic Load Balancing | [**Open Exercise actors07 →**](../playground/index.html?exercise=actors07) |
