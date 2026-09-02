# Chapter 11: Hyperparameter Optimization with Ray Tune & ASHA

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Ray Tune, Search Spaces, ASHA Early-Stopping Schedulers, and Bayesian Optimization
-   :material-play-circle: **Interactive Challenges** &bull; 3 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=11){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

**Ray Tune** executes scalable, distributed hyperparameter search across hundreds of concurrent trials. It couples state-of-the-art search algorithms (Bayesian, Optuna, HyperOpt) with early-stopping trial schedulers like **ASHA (Asynchronous Successive Halving Algorithm)**.

```mermaid
flowchart TD
    subgraph TunerDriver["Ray Tune Orchestration Plane"]
        TunerObj["Tuner.fit()"] --> TrialRunner["TrialRunner Coordinator Actor"]
        SearchAlg["Search Algorithm<br/>(Bayesian / Optuna / HyperOpt)"] -->|"Generate Configs"| TrialRunner
        ASHASched["ASHA Scheduler Engine<br/>(Asynchronous Successive Halving)"] <-->|"Pruning & Promotion Decisions"| TrialRunner
    end

    subgraph Rungs["ASHA Successive Halving Rungs"]
        subgraph Rung0["Rung 0 (1 Epoch Evaluation)"]
            T0["Trial 0 (lr=0.01)"]
            T1["Trial 1 (lr=0.5) ❌ (KILLED)"]
            T2["Trial 2 (lr=0.001)"]
            T3["Trial 3 (lr=0.05) ❌ (KILLED)"]
        end

        subgraph Rung1["Rung 1 (4 Epochs Evaluation - Top 50%)"]
            T0_p["Trial 0 (Promoted)"]
            T2_p["Trial 2 (Promoted)"]
        end

        subgraph Rung2["Rung 2 (Final High Resource Evaluation)"]
            T0_win["Trial 0 (Optimal Result 🎉)"]
        end

        T0 --> T0_p
        T2 --> T2_p
        T0_p --> T0_win
    end

    TrialRunner --> Rung0

    style TunerDriver fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc
    style Rungs fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    style ASHASched fill:#1e1e38,stroke:#f59e0b,stroke-width:2px,color:#f8fafc
    style Rung0 fill:#1e293b,stroke:#34d399,stroke-width:1px,color:#f8fafc
    style Rung1 fill:#1e293b,stroke:#c084fc,stroke-width:1px,color:#f8fafc
    style Rung2 fill:#1e293b,stroke:#38bdf8,stroke-width:1px,color:#f8fafc
```

```mermaid
sequenceDiagram
    autonumber
    participant D as Tuner Driver
    participant TR as TrialRunner Coordinator
    participant ASHA as ASHA Scheduler
    participant T0 as Trial Worker 0 (lr=0.01)
    participant T1 as Trial Worker 1 (lr=0.5)

    Note over D,T1: Trial Execution & Early Stopping Protocol
    TR->>T0: Spawn Trial(lr=0.01, Epoch=1)
    TR->>T1: Spawn Trial(lr=0.5, Epoch=1)
    T0->>TR: tune.report(val_loss=0.35, epoch=1)
    T1->>TR: tune.report(val_loss=1.85, epoch=1)
    TR->>ASHA: EvaluateTrialMetrics(T0, T1)
    ASHA-->>TR: T0 in Top 50% -> Action: CONTINUE / PROMOTE
    ASHA-->>TR: T1 in Bottom 50% -> Action: STOP (Kill Trial)
    TR->>T1: Terminate Worker Process & Reclaim GPU Resources
    TR->>T0: Continue Training to Rung 1 (Epoch=4)
```

ASHA dynamically prunes underperforming configurations early in their training trajectory, freeing node CPU/GPU slots to evaluate new configurations asynchronously.

---

## 2. Annotated Python Code Anatomy & API Reference

```python
import ray
from ray import tune
from ray.tune.schedulers import ASHAScheduler

# 1. Define objective function
def evaluation_objective(config: dict):
    lr = config["lr"]
    momentum = config["momentum"]
    
    for epoch in range(10):
        # Simulated validation loss curve
        val_loss = (1.0 - (lr * 10)) ** 2 + (0.5 - momentum) ** 2 + (1.0 / (epoch + 1))
        # Report metric to Tune scheduler
        tune.report({"val_loss": val_loss, "epoch": epoch})

# 2. Define search space and ASHA early-stopping scheduler
search_space = {
    "lr": tune.loguniform(1e-4, 1e-1),
    "momentum": tune.uniform(0.1, 0.9),
}

scheduler = ASHAScheduler(
    metric="val_loss",
    mode="min",
    max_t=10,
    grace_period=2,
    reduction_factor=3
)

# 3. Launch tuner
tuner = tune.Tuner(
    evaluation_objective,
    param_space=search_space,
    tune_config=tune.TuneConfig(num_samples=20, scheduler=scheduler)
)
results = tuner.fit()
best_result = results.get_best_result(metric="val_loss", mode="min")
print(f"Best config: {best_result.config} | Loss: {best_result.metrics['val_loss']}")
```

---

## 3. Production Best Practices & Hardening Guidelines

1. **Use ASHA for Iterative Deep Learning**: ASHA outperforms random and grid search by 5–10x by aggressively terminating unpromising trials.
2. **Define Log-Uniform Spaces for Learning Rates**: Use `tune.loguniform(min, max)` rather than linear uniform for parameters spanning multiple orders of magnitude.
3. **Limit Max Concurrent Trials**: Set `tune.TuneConfig(max_concurrent_trials=N)` to prevent overloading available cluster GPU slots.
4. **Use Checkpoints for Early Stopping & Resuming**: Save trial state with `train.report(..., checkpoint=...)` to allow paused trials to resume.
5. **Track Experiments with MLflow / Wandb**: Attach `WandbLoggerCallback` or `MLflowLoggerCallback` to `tune.Tuner(run_config=...)`.

---

## 4. Troubleshooting & Diagnostic Workflows

1. **Trials Terminating Immediately with Error**:
   - *Symptom*: All trials fail on step 0.
   - *Fix*: Check trial error logs in `results.errors`; verify input data path is accessible to all worker nodes.
2. **Scheduler Metric Direction Inverted**:
   - *Symptom*: Best trial selected has highest loss instead of lowest.
   - *Fix*: Verify `mode="min"` for loss minimization or `mode="max"` for accuracy metrics.
3. **Resource Starvation**:
   - *Symptom*: Only 1 trial runs at a time.
   - *Fix*: Check trial resource requests in `tune.with_resources(objective, {"cpu": 1, "gpu": 0.5})`.

---

## 5. Hands-on Practice Exercises

| Exercise ID | Goal / Topic | Playground Link |
| :--- | :--- | :--- |
| `tune01` | Tune Search Spaces & Distributed Trials | [**Open Exercise tune01 →**](../playground/index.html?exercise=tune01) |
| `tune02` | ASHA / HyperBand Schedulers | [**Open Exercise tune02 →**](../playground/index.html?exercise=tune02) |
| `tune03` | Population-Based Training (PBT) | [**Open Exercise tune03 →**](../playground/index.html?exercise=tune03) |
