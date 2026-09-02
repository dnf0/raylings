# Chapter 06: Cluster Architecture, Head Nodes & GCS Mechanics

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Global Control Store (GCS), Raylet Node Daemons, Head Nodes, and Worker Lifecycles
-   :material-play-circle: **Interactive Challenges** &bull; 4 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=6){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

A Ray cluster consists of a single **Head Node** and zero or more **Worker Nodes**. Every node runs a local `raylet` daemon composed of a local scheduler and a Plasma object store.

```mermaid
flowchart TD
    subgraph HeadNode["Ray Head Node (Control Plane)"]
        GCS["Global Control Store (GCS Server)<br/>• Node Membership Table<br/>• Actor Registration Table<br/>• Placement Group Registry<br/>• Object Location Directory"]
        Dashboard["Ray Dashboard & Observability Server (Port 8265)"]
        Autoscaler["Cluster Autoscaler Daemon"]
        HeadRaylet["Head Node Raylet & Plasma Store"]
        
        GCS <--> Dashboard
        GCS <--> Autoscaler
    end

    subgraph WorkerNode1["Worker Node 01 (Compute)"]
        subgraph RL1["Raylet Daemon 01"]
            Sched1["Local Scheduler"]
            NM1["Node Manager"]
        end
        PS1["Plasma Object Store (/dev/shm)"]
        WPool1["Core Worker Pool (Python 3.12 Processes)"]
        
        RL1 <--> PS1
        RL1 --> WPool1
    end

    subgraph WorkerNode2["Worker Node 02 (GPU / Accelerators)"]
        subgraph RL2["Raylet Daemon 02"]
            Sched2["Local Scheduler"]
            NM2["Node Manager"]
        end
        PS2["Plasma Object Store (/dev/shm)"]
        WPool2["GPU Worker Pool (PyTorch CUDA Processes)"]
        
        RL2 <--> PS2
        RL2 --> WPool2
    end

    GCS <-->|"gRPC Heartbeats & Membership"| RL1
    GCS <-->|"gRPC Heartbeats & Membership"| RL2
    PS1 <-->|"Zero-Copy Inter-Node Object Transfer (TCP)"| PS2

    style HeadNode fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style WorkerNode1 fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style WorkerNode2 fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style GCS fill:#1e1e38,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style PS1 fill:#1e1e38,stroke:#c084fc,stroke-width:2px,color:#f8fafc
    style PS2 fill:#1e1e38,stroke:#c084fc,stroke-width:2px,color:#f8fafc
```

```mermaid
sequenceDiagram
    autonumber
    participant WN as New Worker Node (Raylet)
    participant GCS as Global Control Store (Head Node)
    participant D as Driver Process
    participant DB as Ray Dashboard

    Note over WN,GCS: Node Join Protocol
    WN->>GCS: RegisterNode(NodeIP, TotalCPUs, TotalGPUs, MemoryBytes)
    GCS->>GCS: Append to Cluster Membership Table
    GCS-->>WN: RegistrationAck(ClusterID, GCSHeartbeatInterval)
    
    loop Periodic Node Health & Resource Broadcast
        WN->>GCS: Heartbeat(AvailableCPUs, PlasmaMemoryUsage, AliveWorkers)
        GCS->>DB: Stream Real-Time Cluster Telemetry
    end

    Note over D,GCS: State Inspection (ray.util.state)
    D->>GCS: list_nodes() / list_actors()
    GCS-->>D: Return Cluster Topology Snapshot
```

The **Global Control Store (GCS)** manages cluster-wide metadata (actor registration, node membership, placement group tables, and object locations), ensuring decentralized task dispatch while maintaining centralized consensus.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from ray.util.state import list_nodes, list_actors, summarize_tasks

# 1. Inspect active cluster topology programmatically
cluster_nodes = list_nodes()
for node in cluster_nodes:
    print(f"Node ID: {node['node_id']} | IP: {node['node_ip_address']} | Alive: {node['is_alive']}")

# 2. Query actor states from GCS
active_actors = list_actors(filters=[("state", "=", "ALIVE")])
print(f"Active GCS Registered Actors: {len(active_actors)}")

# 3. Retrieve task execution summary
task_summary = summarize_tasks()
print(f"Pending tasks: {task_summary.get('PENDING', 0)}")
```

### Key API Parameter Reference

- **`ray.init(address="auto")`**: Connects to an existing running Ray cluster via GCS.
- **`ray.cluster_resources()`**: Returns total CPU, GPU, memory, and custom resources in the cluster.
- **`ray.available_resources()`**: Returns currently unallocated cluster resources.
- **`ray.util.state.list_nodes()`**: Lists physical/virtual node statuses in the cluster.

---

## 3. Production Best Practices & Hardening Guidelines

1. **Protect the GCS from Driver Overload**: Avoid registering millions of tiny actors in GCS; batch actor pools and rely on stateless tasks for massive concurrency.
2. **Configure GCS High Availability**: In production Kubernetes clusters, enable External GCS storage (Redis) or multi-replica GCS fault tolerance.
3. **Set Worker Node Heartbeat Timeouts**: Configure `raylet` heartbeat timeouts to quickly detect and evict dead cloud instances.
4. **Isolate Driver from Heavy Compute**: Run driver scripts on worker nodes or dedicated client pods rather than overburdening the Head Node.
5. **Monitor Object Directory Size**: Use GCS metrics to detect memory leaks in object reference tables.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **Worker Node Marked Dead Unexpectedly**:
   - *Symptom*: Logs report "Node timed out heartbeating to GCS".
   - *Fix*: Check worker node network connectivity, MTU settings, or host CPU starvation.
2. **GCS OOM / Memory Pressure**:
   - *Symptom*: High latency on actor creation and task dispatch.
   - *Fix*: Limit number of distinct named actors and clean up finished placement groups.
3. **Autoscaler Flapping (Thrashing)**:
   - *Symptom*: Nodes repeatedly start and terminate.
   - *Fix*: Increase `idle_timeout_minutes` in autoscaler configuration to prevent premature scale-down.

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `cluster01` | Head Node, Workers & GCS | [**Open Exercise cluster01 →**](../playground/index.html?exercise=cluster01) |
| `cluster02` | Programmatic Cluster Simulation | [**Open Exercise cluster02 →**](../playground/index.html?exercise=cluster02) |
| `cluster03` | Simulating Node Death & Rescheduling | [**Open Exercise cluster03 →**](../playground/index.html?exercise=cluster03) |
| `cluster04` | Ray Job Submission API | [**Open Exercise cluster04 →**](../playground/index.html?exercise=cluster04) |
