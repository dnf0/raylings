# Chapter 13: Production Observability, Profiling & Tracing

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Ray Dashboard, OpenTelemetry Tracing, Distributed Profiling, and Performance Diagnostics
-   :material-play-circle: **Interactive Challenges** &bull; 3 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=13){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

Operating Ray in production requires unified visibility into CPU/GPU utilization, object store memory allocation, task execution timelines, and distributed traces.

```mermaid
flowchart TD
    subgraph TelemetrySources["Distributed Telemetry Sources"]
        HeadDaemon["Head Node (GCS & Autoscaler Telemetry)"]
        Worker1["Worker Node 01 (Raylet & Core Workers)"]
        Worker2["Worker Node 02 (GPU Plasma & CUDA Tasks)"]
    end

    subgraph CollectionPlane["Metrics & Trace Collection Pipeline"]
        Prom["Prometheus Metrics Exporter (Port 44217)"]
        OTel["OpenTelemetry Collector Daemon (gRPC 4317)"]
        LogAgg["FluentBit / Vector Log Shipper"]
    end

    subgraph ObservabilityUI["Observability & Analytics UI"]
        Dashboard["Ray Dashboard UI (Port 8265)<br/>• Node Resource Topology<br/>• Memory Flame Graphs<br/>• Actor & Task State Tables"]
        Grafana["Grafana Cluster Dashboards"]
        Jaeger["Jaeger / Zipkin Distributed Tracing UI"]
    end

    HeadDaemon --> Prom
    Worker1 --> Prom
    Worker2 --> Prom
    Worker1 --> OTel
    Worker2 --> OTel
    Worker1 --> LogAgg
    Worker2 --> LogAgg

    Prom --> Dashboard
    Prom --> Grafana
    OTel --> Jaeger
    LogAgg --> Dashboard

    style TelemetrySources fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style CollectionPlane fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style ObservabilityUI fill:#1e1e38,stroke:#34d399,stroke-width:2px,color:#f8fafc
    style Dashboard fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style Grafana fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style Jaeger fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
```

```mermaid
sequenceDiagram
    autonumber
    participant D as Driver Process
    participant W as Core Worker Task
    participant A as Stateful Actor
    participant OTel as OpenTelemetry Collector
    participant J as Jaeger Trace UI

    Note over D,A: Distributed Context & Span Propagation
    D->>D: Start Root Span: "pipeline_run_01" (TraceID: 0x4f8a)
    D->>W: task.remote() [Injects Trace Context in gRPC Metadata]
    W->>W: Start Child Span: "process_batch" (ParentID: 0x4f8a)
    W->>A: actor.record_event.remote() [Propagate Trace Context]
    A->>A: Start Child Span: "mutate_state"
    A-->>OTel: Export Span: "mutate_state"
    W-->>OTel: Export Span: "process_batch"
    D-->>OTel: Export Span: "pipeline_run_01"
    OTel->>J: Stitch Distributed Flame Graph
```

Ray exports native Prometheus metrics (queue depth, memory spilling, active actors) and integrates with OpenTelemetry for end-to-end distributed span tracing.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from ray.util import tracing

# 1. Initialize Ray with OpenTelemetry tracing integration
ray.init(
    _tracing_startup_hook="ray.util.tracing.setup_type:setup_tracing",
    ignore_reinit_error=True
)

# 2. Trace custom task spans with tracing API
@ray.remote
def monitored_etl_task(batch_id: int) -> dict:
    # Custom tracing span within the distributed worker
    tracer = tracing.get_tracer(__name__)
    with tracer.start_as_current_span("compute_metrics"):
        result = sum(i * i for i in range(100000))
    return {"batch_id": batch_id, "result": result}

# 3. Retrieve cluster memory telemetry
from ray.util.state import summarize_objects
object_summary = summarize_objects()
print(f"Total active objects in memory: {object_summary.get('total_objects', 0)}")
```

---

## 3. Production Best Practices & Hardening Guidelines

1. **Scrape Prometheus Metrics at `/metrics`**: Configure Prometheus to scrape node `raylet` daemons on port 9090 for cluster-wide alerts.
2. **Profile Hot Tasks with Ray Timeline**: Export Chrome tracing JSON via `ray.timeline(filename="timeline.json")` to identify CPU idle gaps.
3. **Trace Cross-Service Inference with OpenTelemetry**: Propagate trace contexts across Ray Serve deployments and downstream databases.
4. **Alert on High Object Spilling**: Set alerts when `ray_object_store_memory{type="spilled"}` increases rapidly.
5. **Monitor GCS Storage Memory**: Track GCS memory usage to prevent metadata thrashing on high-churn clusters.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **High GC Pause Latency**:
   - *Symptom*: Spikes in task execution latency visible on Ray Dashboard flame charts.
   - *Fix*: Enable `py-spy` profiler via Ray Dashboard to inspect Python GIL contention and memory allocation hotspots.
2. **Missing Distributed Traces**:
   - *Symptom*: OTel spans dropped between actor calls.
   - *Fix*: Ensure OpenTelemetry SDK is installed across all cluster worker images and `OTEL_EXPORTER_OTLP_ENDPOINT` is configured.
3. **Dashboard Unresponsive under Heavy Load**:
   - *Symptom*: Dashboard port 8265 times out during 10,000+ task submissions.
   - *Fix*: Increase Dashboard agent scrape interval or use CLI state APIs (`ray summary tasks`).

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `perf01` | Ray Execution Profiling & Chrome Timelines | [**Open Exercise perf01 →**](../playground/index.html?exercise=perf01) |
| `perf02` | Diagnosing Memory Leaks with ray memory | [**Open Exercise perf02 →**](../playground/index.html?exercise=perf02) |
| `perf03` | Ray Metrics & Prometheus Exports | [**Open Exercise perf03 →**](../playground/index.html?exercise=perf03) |
