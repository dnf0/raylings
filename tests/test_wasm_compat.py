"""Unit tests for the Raylings WASM / Pyodide compatibility and simulation engine."""

from raylings.wasm_compat import (
    ActorPool,
    WasmActorHandle,
    WasmObjectRef,
    WasmRayModule,
    ray,
)


def test_wasm_ray_lifecycle():
    """Verify WASM Ray init and shutdown lifecycle."""
    wasm_ray = WasmRayModule()
    assert not wasm_ray.is_initialized()

    context = wasm_ray.init(ignore_reinit_error=True, num_cpus=4)
    assert wasm_ray.is_initialized()
    assert context["num_cpus"] == 4
    assert context["node_ip_address"] == "127.0.0.1"

    # Reinit with ignore_reinit_error should succeed
    wasm_ray.init(ignore_reinit_error=True)
    assert wasm_ray.is_initialized()

    wasm_ray.shutdown()
    assert not wasm_ray.is_initialized()


def test_wasm_remote_function():
    """Verify @ray.remote functions execute and return resolvable object refs."""
    wasm_ray = WasmRayModule()
    wasm_ray.init()

    @wasm_ray.remote
    def add(x: int, y: int) -> int:
        return x + y

    ref1 = add.remote(10, 20)
    assert isinstance(ref1, WasmObjectRef)
    assert wasm_ray.get(ref1) == 30

    # Test multiple refs batch resolution
    refs = [add.remote(i, i * 2) for i in range(5)]
    results = wasm_ray.get(refs)
    assert results == [0, 3, 6, 9, 12]

    wasm_ray.shutdown()


def test_wasm_plasma_object_store():
    """Verify ray.put() stores values in simulated Plasma object store."""
    wasm_ray = WasmRayModule()
    wasm_ray.init()

    sample_data = {"weights": [0.1, 0.2, 0.3], "meta": "test"}
    ref = wasm_ray.put(sample_data)

    assert isinstance(ref, WasmObjectRef)
    assert len(ref.hex_id) == 32
    assert wasm_ray.get(ref) == sample_data

    # Store telemetry check
    stats = wasm_ray.get_cluster_resources()
    assert stats["object_store_objects"] == 1
    assert stats["object_store_used_bytes"] > 0

    wasm_ray.shutdown()


def test_wasm_remote_actor():
    """Verify @ray.remote stateful actor classes."""
    wasm_ray = WasmRayModule()
    wasm_ray.init()

    @wasm_ray.remote
    class Counter:
        def __init__(self, start: int = 0) -> None:
            self.value = start

        def increment(self, step: int = 1) -> int:
            self.value += step
            return self.value

        def get_value(self) -> int:
            return self.value

    counter = Counter.remote(start=10)
    assert isinstance(counter, WasmActorHandle)

    inc_ref = counter.increment.remote(5)
    assert wasm_ray.get(inc_ref) == 15

    val_ref = counter.get_value.remote()
    assert wasm_ray.get(val_ref) == 15

    wasm_ray.shutdown()


def test_wasm_actor_pool():
    """Verify ActorPool distribution across simulated WASM actors."""
    wasm_ray = WasmRayModule()
    wasm_ray.init()

    @wasm_ray.remote
    class TransformerWorker:
        def __init__(self, multiplier: int) -> None:
            self.multiplier = multiplier

        def transform(self, x: int) -> int:
            return x * self.multiplier

    workers = [TransformerWorker.remote(2), TransformerWorker.remote(3)]
    pool = ActorPool(workers)

    results = list(pool.map(lambda actor, v: actor.transform.remote(v), [1, 2, 3, 4]))
    assert sorted(results) == [2, 6, 6, 12]

    wasm_ray.shutdown()


def test_wasm_ray_wait():
    """Verify ray.wait splits ready and unready object references."""
    wasm_ray = WasmRayModule()
    wasm_ray.init()

    ref1 = wasm_ray.put(100)
    ref2 = wasm_ray.put(200)

    ready, unready = wasm_ray.wait([ref1, ref2], num_returns=1)
    assert len(ready) == 1
    assert len(unready) == 1
    assert ready[0] in [ref1, ref2]

    wasm_ray.shutdown()


def test_wasm_ray_data_pipeline():
    """Verify pure-Python simulated Ray Data streaming pipeline."""
    wasm_ray = WasmRayModule()
    wasm_ray.init()

    ds = wasm_ray.data.range(20)
    assert ds.count() == 20

    mapped_ds = ds.map(lambda row: {"id": row["id"], "val": row["id"] * 2})
    filtered_ds = mapped_ds.filter(lambda row: row["val"] > 20)
    results = filtered_ds.take_all()

    assert len(results) == 9
    assert results[0] == {"id": 11, "val": 22}
    assert results[-1] == {"id": 19, "val": 38}

    # Test map_batches
    batch_ds = ds.map_batches(
        lambda batch: {"id": batch["id"], "cubed": [x**3 for x in batch["id"]]},
        batch_size=5,
    )
    batch_results = batch_ds.take(3)
    assert len(batch_results) == 3
    assert batch_results[2]["cubed"] == 8

    wasm_ray.shutdown()


def test_global_wasm_ray_singleton():
    """Verify top-level `ray` module instance in wasm_compat."""
    ray.init(ignore_reinit_error=True)
    assert ray.is_initialized()

    @ray.remote
    def multiply(a: int, b: int) -> int:
        return a * b

    ref = multiply.remote(6, 7)
    assert ray.get(ref) == 42
    ray.shutdown()
