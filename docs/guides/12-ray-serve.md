# Chapter 12: Production Model Serving & Autoscaling with Ray Serve

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Ray Serve, `@serve.deployment`, HTTP Ingress, Dynamic Batching, and Autoscaling
-   :material-play-circle: **Interactive Challenges** &bull; 5 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=12){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

**Ray Serve** is a scalable model serving framework designed for complex inference pipelines (combining LLMs, embedding models, and business logic). Serve manages HTTP ingress routers, dynamic request batching, model multiplexing, and replica autoscaling.

```mermaid
flowchart TD
    subgraph IngressPlane["HTTP Traffic Ingress & Routing"]
        Client1["HTTP Client 1 (POST /predict)"] --> Proxy["Ray Serve Ingress HTTP Proxy (FastAPI)"]
        Client2["HTTP Client 2 (POST /predict)"] --> Proxy
        Proxy --> Router["Serve Router & Load Balancer"]
    end

    subgraph ControlPlane["Serve Controller & Autoscaler"]
        Controller["Serve Controller Actor"] <-->|"Metrics & Scale Policies"| Router
    end

    subgraph DeploymentReplicas["Deployment Worker Replicas (Actor Pool)"]
        subgraph Replica1["Replica Actor 01 (GPU: 1)"]
            BatchQ1["Dynamic Batch Queue<br/>(max_batch_size=8, wait=50ms)"]
            Model1["TensorRT / PyTorch Model Instance"]
            BatchQ1 --> Model1
        end

        subgraph Replica2["Replica Actor 02 (GPU: 1)"]
            BatchQ2["Dynamic Batch Queue<br/>(max_batch_size=8, wait=50ms)"]
            Model2["TensorRT / PyTorch Model Instance"]
            BatchQ2 --> Model2
        end

        Router -->|"Direct gRPC Stream"| BatchQ1
        Router -->|"Direct gRPC Stream"| BatchQ2
    end

    style IngressPlane fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style ControlPlane fill:#1e1e38,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style DeploymentReplicas fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style Replica1 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
    style Replica2 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
```

```mermaid
sequenceDiagram
    autonumber
    participant C1 as Client 1 (HTTP)
    participant C2 as Client 2 (HTTP)
    participant P as Serve Ingress Proxy
    participant R as Replica Actor (@serve.batch)
    participant M as GPU Model Forward Pass

    Note over C1,C2: Concurrent HTTP Invocations
    C1->>P: POST /predict {"text": "Alpha"}
    C2->>P: POST /predict {"text": "Beta"}
    P->>R: Enqueue Request 1
    P->>R: Enqueue Request 2
    Note over R: Dynamic Batch Buffer accumulates requests (timeout=50ms / max=8)
    R->>M: ForwardPass(["Alpha", "Beta"]) (Vectorized GPU Matrix Op)
    M-->>R: Returns Batch Predictions [0.95, 0.88]
    R-->>P: Demux Response 1 & 2
    P-->>C1: 200 OK {"category": "Alpha", "score": 0.95}
    P-->>C2: 200 OK {"category": "Beta", "score": 0.88}
```

Serve decouples HTTP routing from model execution, automatically queuing and packing concurrent requests into optimal GPU micro-batches. The Serve Controller monitors request latency and queue backlogs to scale replica actor pools horizontally.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from ray import serve
from fastapi import FastAPI

app = FastAPI()

@serve.deployment(num_replicas=2, ray_actor_options={"num_cpus": 1})
@serve.ingress(app)
class ClassifierDeployment:
    def __init__(self):
        # Load heavy model weights once during replica startup
        self.categories = ["finance", "tech", "health"]

    @app.get("/predict")
    def predict(self, text: str) -> dict:
        category = self.categories[len(text) % len(self.categories)]
        return {"input": text, "category": category, "confidence": 0.95}

    @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.05)
    async def dynamic_batch_predict(self, texts: list[str]) -> list[str]:
        # Micro-batching multiple concurrent HTTP requests into one matrix op
        return [self.categories[len(t) % len(self.categories)] for t in texts]

# Build the deployment handle
entrypoint = ClassifierDeployment.bind()
```

---

## 3. Production Best Practices & Hardening Guidelines

1. **Use `@serve.batch` for GPU Acceleration**: Dynamic batching aggregates requests across concurrent users, boosting GPU inference throughput by 5–10x.
2. **Configure Multi-Stage Pipeline Graphs**: Connect deployments using `DeploymentHandle` rather than making internal HTTP roundtrips.
3. **Set Autoscaling Target Queue Depths**: Configure `autoscaling_config={"target_ongoing_requests": 5, "min_replicas": 1, "max_replicas": 10}`.
4. **Use Model Multiplexing for Multiple LoRA Adapters**: Serve thousands of fine-tuned adapter weights on a single base model pool using `serve.multiplex`.
5. **Implement Health Checks**: Define `check_health()` methods on deployments to allow Serve to restart unresponsive worker replicas.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **High Ingress Latency / Queue Stalls**:
   - *Symptom*: Request timeouts under load.
   - *Fix*: Decrease `batch_wait_timeout_s` or increase `max_replicas` in the autoscaling configuration.
2. **Replica Crash on Startup**:
   - *Symptom*: Serve deployment status shows `DEPLOY_FAILED`.
   - *Fix*: Check replica logs for missing GPU drivers or weights download failure during `__init__`.
3. **Cross-Replica State Leak**:
   - *Symptom*: User data appears in subsequent requests.
   - *Fix*: Avoid storing per-request state on `self` in deployment classes; use local variables inside request handler functions.

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `serve01` | Ray Serve Deployments & HTTP Ingress | [**Open Exercise serve01 →**](../playground/index.html?exercise=serve01) |
| `serve02` | Dynamic Request Batching (@serve.batch) | [**Open Exercise serve02 →**](../playground/index.html?exercise=serve02) |
| `serve03` | Multi-Model Composable Pipelines (DAGs) | [**Open Exercise serve03 →**](../playground/index.html?exercise=serve03) |
| `serve04` | Streaming Responses with FastApi & Generators | [**Open Exercise serve04 →**](../playground/index.html?exercise=serve04) |
| `serve05` | Serve Autoscaling Policies | [**Open Exercise serve05 →**](../playground/index.html?exercise=serve05) |
