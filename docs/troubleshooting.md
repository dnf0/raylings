# Troubleshooting & Common Pitfalls 🛠️

This guide covers common errors, edge cases, and diagnostic recipes when working with Python Ray and the Raylings learning environment.

---

## ⚡ Quick Diagnostic Checklist

When encountering unexpected behavior:

1. Run `raylings doctor` to verify environment health.
2. Run `raylings daemon status` or `raylings daemon restart` to reset cluster state.
3. Review the troubleshooting recipes below for your specific symptom.

---

## 🛑 Problem Recipes

### 1. Ray Port Conflicts (Ports 6379, 8265, 10001)

#### Symptom
```text
RuntimeError: Ray head failed to start: Port 6379 already in use.
```
or
```text
ValueError: Failed to bind Ray dashboard to 127.0.0.1:8265.
```

#### Cause
A previous Ray session, Docker container, local Redis instance, or stale background worker was not cleanly shut down and is still holding onto Ray's default networking ports (6379 for GCS, 8265 for Dashboard, 10001 for Ray Client).

#### Solution

=== "Step 1: Terminate Stale Ray Processes"

    ```bash
    # Kill all local Ray processes across the user account
    ray stop --force
    ```

=== "Step 2: Inspect & Kill Bound Ports"

    ```bash
    # Identify what process is listening on port 6379 or 8265
    lsof -i :6379
    lsof -i :8265

    # Terminate the offending process
    kill -9 <PID>
    ```

=== "Step 3: Restart Raylings Daemon"

    ```bash
    raylings daemon restart
    ```

---

### 2. GCS (Global Control Store) Connection Failures

#### Symptom
```text
ray.exceptions.ClusterUnavailableError: Could not connect to Ray cluster at 127.0.0.1:6379.
```

#### Cause
The driver script attempted to connect to an existing Ray cluster that was either shut down, running in a different network namespace, or blocked by local firewall/loopback restrictions.

#### Solution
- In standalone exercises, ensure you call `ray.init(ignore_reinit_error=True)` rather than connecting to an explicit remote IP address unless testing cluster features.
- If using `raylings watch`, allow the watcher to manage the daemon session automatically.
- Check loopback interface accessibility:
  ```bash
  ping -c 1 127.0.0.1
  ```

---

### 3. Plasma Object Store Spilling & Out-Of-Memory (OOM)

#### Symptom
```text
ray.exceptions.RaySystemError: Object store full: Failed to put object in Plasma store.
```
or excessive warnings:
```text
(raylet) Object spilling threshold reached. Spilled 1420 MiB to disk.
```

#### Cause
The shared-memory Plasma store (typically allocated ~30% of system RAM by default) has been exhausted because too many uncollected `ObjectRef` references are held in memory, or very large tensors/arrays are being repeatedly serialized with `ray.put()`.

#### Solution

- **Explicit Scoping & Garbage Collection**: Ensure you do not retain references to `ObjectRef`s in global variables. Use `del ref` or wrap processing inside functions to allow Ray's distributed reference counting to reclaim memory:
  ```python
  # Good practice: Let refs fall out of scope
  def process_batch():
      refs = [expensive_task.remote() for _ in range(100)]
      results = ray.get(refs)
      return aggregate(results)  # refs are garbage collected
  ```
- **Reuse ObjectRefs with `ray.put()`**: Pass a single `ray.put(large_data)` reference to 50 tasks instead of passing the raw Python object 50 times (which forces 50 redundant serializations).
- **Configure Custom Object Store Bounds**: In memory-constrained environments:
  ```python
  ray.init(object_store_memory=200 * 1024 * 1024)  # 200 MB
  ```

---

### 4. Multi-Worker Ray Train DDP Deadlocks

#### Symptom
`TorchTrainer` hangs indefinitely during `torch.distributed.init_process_group` or at the first `loss.backward()` / `all_reduce` step without throwing an error.

#### Cause
1. **Asymmetric Data Iteration**: One worker reaches the end of its dataset shard earlier than other workers, causing other workers to wait forever on collective synchronization barriers.
2. **Resource Starvation**: `ScalingConfig(num_workers=4)` was requested on a machine with only 2 available CPU cores, preventing all worker actors from launching concurrently.
3. **Mismatched Barrier Invocations**: Calling `ray.train.report()` inside a conditional block executed by rank 0 only.

#### Solution
- Ensure all collective calls (`prepare_model`, `prepare_data_loader`, `ray.train.report`) are called uniformly by **all workers** in the training loop:
  ```python
  # CORRECT: All workers report metrics together
  ray.train.report({"loss": loss.item()})

  # INCORRECT: Only rank 0 reports, deadlocking other workers
  if ray.train.get_context().get_world_rank() == 0:
      ray.train.report({"loss": loss.item()})
  ```
- Configure `ScalingConfig` to match available logical cores on your machine:
  ```python
  from ray.train import ScalingConfig

  scaling_config = ScalingConfig(
      num_workers=2,  # Keep within local CPU limits
      use_gpu=False,
  )
  ```

---

### 5. KubeRay CRD Verification & Reconciliation Failures

#### Symptom
```text
error: unable to recognize "ray-cluster.yaml": no matches for kind "RayCluster" in version "ray.io/v1"
```
or the Kubernetes cluster status remains in `Pending` indefinitely.

#### Cause
The KubeRay operator is not installed on the Kubernetes cluster, or the CRD API version (`ray.io/v1` vs `ray.io/v1alpha1`) does not match the installed helm chart version.

#### Solution

=== "Step 1: Verify KubeRay CRDs"

    ```bash
    kubectl get crds | grep ray.io
    # Expected output:
    # rayclusters.ray.io
    # rayjobs.ray.io
    # rayservices.ray.io
    ```

=== "Step 2: Inspect KubeRay Operator Logs"

    ```bash
    kubectl logs -n ray-system -l app.kubernetes.io/name=kuberay-operator --tail=100
    ```

=== "Step 3: Validate Pod Scheduling & Resource Quotas"

    ```bash
    kubectl describe raycluster my-ray-cluster
    ```

---

### 6. Daemon Socket & Stale State Cleanup

#### Symptom
The Raylings CLI reports:
```text
Error querying daemon: Broken pipe or stale socket.
```

#### Cause
An abrupt process termination (e.g. `SIGKILL` or system reboot) left an orphaned socket or lockfile.

#### Solution
Clean up stale temporary files:

```bash
# 1. Stop daemon if running
raylings daemon stop

# 2. Clean temporary sockets and session directories
rm -rf /tmp/ray/
rm -f /tmp/raylings_daemon.sock

# 3. Restart daemon
raylings daemon start
```

---

### 7. File Descriptor (`ulimit`) Limits on macOS & Linux

#### Symptom
```text
OSError: [Errno 24] Too many open files
```

#### Cause
Ray spawns multiple worker processes, inter-process communication sockets, and Plasma memory-mapped file descriptors. On macOS, the default `ulimit -n` is often restricted to 256.

#### Solution
Increase the maximum open file descriptors in your terminal shell:

```bash
# Check current limit
ulimit -n

# Increase limit for current session
ulimit -n 65536
```

Add `ulimit -n 65536` to your `~/.zshrc` or `~/.bashrc` for permanent effect.
