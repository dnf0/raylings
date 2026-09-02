"""Pure-Python in-memory Ray simulation engine for WebAssembly / Pyodide environments.

This module provides a lightweight, zero-dependency emulation of core Ray APIs
(`ray.init`, `@ray.remote`, `ray.put`, `ray.get`, `ray.wait`, `ActorPool`, `ray.data`)
designed to execute interactively inside browser Pyodide/WebAssembly or in sandboxed
environments where C++ Ray binaries and multi-process sockets are unavailable.
"""

from __future__ import annotations

import functools
import hashlib
import inspect
import pickle
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class WasmObjectRef(Generic[T]):
    """Simulated Ray ObjectRef holding a unique hexadecimal object ID."""

    hex_id: str
    _value: T = field(repr=False)
    created_at: float = field(default_factory=time.time, repr=False)

    def __hash__(self) -> int:
        return hash(self.hex_id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, WasmObjectRef):
            return self.hex_id == other.hex_id
        return False


class WasmPlasmaStore:
    """In-memory simulated Plasma Shared Memory Object Store."""

    def __init__(self, max_memory_bytes: int = 100_000_000) -> None:
        self.max_memory_bytes = max_memory_bytes
        self._store: dict[str, Any] = {}
        self._sizes: dict[str, int] = {}
        self._counter: int = 0

    def put(self, value: Any) -> WasmObjectRef[Any]:
        """Store a Python object into the simulated Plasma store."""
        self._counter += 1
        raw_bytes = pickle.dumps(value)
        size = len(raw_bytes)
        hex_id = hashlib.sha256(f"{self._counter}_{time.time()}_{size}".encode()).hexdigest()[:32]
        self._store[hex_id] = value
        self._sizes[hex_id] = size
        return WasmObjectRef(hex_id=hex_id, _value=value)

    def get(self, ref: WasmObjectRef[Any]) -> Any:
        """Retrieve an object from the simulated Plasma store by its ref."""
        if ref.hex_id in self._store:
            return self._store[ref.hex_id]
        return ref._value

    def contains(self, ref: WasmObjectRef[Any]) -> bool:
        """Check if an object exists in the store."""
        return ref.hex_id in self._store

    @property
    def total_used_bytes(self) -> int:
        """Calculate total estimated bytes in the Plasma object store."""
        return sum(self._sizes.values())

    @property
    def object_count(self) -> int:
        """Count total objects in the Plasma store."""
        return len(self._store)

    def clear(self) -> None:
        """Reset the object store."""
        self._store.clear()
        self._sizes.clear()
        self._counter = 0


class WasmActorMethod:
    """Proxy for a method on a simulated stateful Ray actor."""

    def __init__(self, actor_handle: WasmActorHandle, method_name: str) -> None:
        self._actor_handle = actor_handle
        self._method_name = method_name

    def remote(self, *args: Any, **kwargs: Any) -> WasmObjectRef[Any]:
        """Dispatch remote method call synchronously to actor instance and return ObjectRef."""
        method = getattr(self._actor_handle._instance, self._method_name)
        result = method(*args, **kwargs)
        self._actor_handle._task_count += 1
        return self._actor_handle._store.put(result)


class WasmActorHandle:
    """Client handle to a simulated stateful Ray actor."""

    def __init__(self, instance: Any, store: WasmPlasmaStore, actor_id: str) -> None:
        self._instance = instance
        self._store = store
        self._actor_id = actor_id
        self._task_count = 0

    def __getattr__(self, name: str) -> WasmActorMethod:
        if hasattr(self._instance, name) and callable(getattr(self._instance, name)):
            return WasmActorMethod(self, name)
        raise AttributeError(
            f"Actor '{type(self._instance).__name__}' has no callable method '{name}'"
        )


class WasmRemoteFunction(Generic[R]):
    """Wrapper for a distributed remote function in WASM simulation."""

    def __init__(
        self,
        func: Callable[..., R],
        store: WasmPlasmaStore,
        options: dict[str, Any] | None = None,
    ) -> None:
        self._func = func
        self._store = store
        self._options = options or {}
        functools.update_wrapper(cast(Any, self), func)

    def remote(self, *args: Any, **kwargs: Any) -> WasmObjectRef[R]:
        """Invoke the remote function and return a future-like ObjectRef."""
        # Resolve any ObjectRefs passed directly as arguments
        resolved_args = [
            self._store.get(arg) if isinstance(arg, WasmObjectRef) else arg for arg in args
        ]
        resolved_kwargs = {
            k: (self._store.get(v) if isinstance(v, WasmObjectRef) else v)
            for k, v in kwargs.items()
        }
        result = self._func(*resolved_args, **resolved_kwargs)
        return self._store.put(result)

    def options(self, **kwargs: Any) -> WasmRemoteFunction[R]:
        """Return a new remote function with configured execution options."""
        merged_options = {**self._options, **kwargs}
        return WasmRemoteFunction(self._func, self._store, merged_options)


class WasmRemoteClass:
    """Wrapper for a stateful actor class in WASM simulation."""

    def __init__(
        self,
        cls: type,
        store: WasmPlasmaStore,
        options: dict[str, Any] | None = None,
    ) -> None:
        self._cls = cls
        self._store = store
        self._options = options or {}
        functools.update_wrapper(cast(Any, self), cls)

    def remote(self, *args: Any, **kwargs: Any) -> WasmActorHandle:
        """Instantiate the actor class and return an actor handle."""
        resolved_args = [
            self._store.get(arg) if isinstance(arg, WasmObjectRef) else arg for arg in args
        ]
        resolved_kwargs = {
            k: (self._store.get(v) if isinstance(v, WasmObjectRef) else v)
            for k, v in kwargs.items()
        }
        instance = self._cls(*resolved_args, **resolved_kwargs)
        actor_id = hashlib.sha256(f"{self._cls.__name__}_{time.time()}".encode()).hexdigest()[:16]
        return WasmActorHandle(instance, self._store, actor_id)

    def options(self, **kwargs: Any) -> WasmRemoteClass:
        """Return a new remote class with configured actor options."""
        merged_options = {**self._options, **kwargs}
        return WasmRemoteClass(self._cls, self._store, merged_options)


class ActorPool:
    """ActorPool distributes tasks across an array of stateful actor handles."""

    def __init__(self, actors: Sequence[WasmActorHandle]) -> None:
        if not actors:
            raise ValueError("ActorPool must contain at least one actor handle")
        self._actors = list(actors)
        self._index = 0

    def map(
        self, fn: Callable[[WasmActorHandle, Any], WasmObjectRef[Any]], values: Sequence[Any]
    ) -> Iterator[Any]:
        """Map a function over values across the pool of actors and return results."""
        refs = []
        for v in values:
            actor = self._actors[self._index % len(self._actors)]
            self._index += 1
            refs.append(fn(actor, v))
        for ref in refs:
            if isinstance(ref, WasmObjectRef):
                yield ref._value
            else:
                yield ref

    def map_unordered(
        self, fn: Callable[[WasmActorHandle, Any], WasmObjectRef[Any]], values: Sequence[Any]
    ) -> Iterator[Any]:
        """Map a function over values, returning results as they complete."""
        yield from self.map(fn, values)

    def submit(self, fn: Callable[[WasmActorHandle, Any], WasmObjectRef[Any]], value: Any) -> None:
        """Submit a single task to the next available worker in the pool."""
        actor = self._actors[self._index % len(self._actors)]
        self._index += 1
        fn(actor, value)


class WasmDataset:
    """Pure-Python simulated Ray Data Dataset for WASM pipelines."""

    def __init__(self, items: list[Any]) -> None:
        self._items = list(items)

    def count(self) -> int:
        """Return total row count in dataset."""
        return len(self._items)

    def take(self, limit: int = 20) -> list[Any]:
        """Take the first N rows from dataset."""
        return self._items[:limit]

    def take_all(self, limit: int | None = None) -> list[Any]:
        """Return all rows as a list."""
        if limit is not None:
            return self._items[:limit]
        return list(self._items)

    def map(self, fn: Callable[[Any], Any]) -> WasmDataset:
        """Transform each row in dataset."""
        return WasmDataset([fn(item) for item in self._items])

    def filter(self, fn: Callable[[Any], bool]) -> WasmDataset:
        """Filter dataset rows by predicate."""
        return WasmDataset([item for item in self._items if fn(item)])

    def map_batches(
        self,
        fn: Callable[[dict[str, list[Any]] | list[Any]], Any],
        batch_size: int = 4096,
        **kwargs: Any,
    ) -> WasmDataset:
        """Transform rows in batches."""
        transformed: list[Any] = []
        for i in range(0, len(self._items), batch_size):
            chunk = self._items[i : i + batch_size]
            # Convert list of dicts to columnar dict if possible
            if chunk and isinstance(chunk[0], dict):
                columnar = {k: [row[k] for row in chunk] for k in chunk[0]}
                batch_res = fn(columnar)
                if isinstance(batch_res, dict):
                    num_rows = len(next(iter(batch_res.values())))
                    keys = list(batch_res.keys())
                    rows = [{k: batch_res[k][idx] for k in keys} for idx in range(num_rows)]
                    transformed.extend(rows)
                elif isinstance(batch_res, list):
                    transformed.extend(batch_res)
                else:
                    transformed.append(batch_res)
            else:
                batch_res = fn(chunk)
                if isinstance(batch_res, list):
                    transformed.extend(batch_res)
                else:
                    transformed.append(batch_res)
        return WasmDataset(transformed)


class WasmDataModule:
    """Namespace for simulated Ray Data dataset constructors."""

    @staticmethod
    def range(n: int) -> WasmDataset:
        """Create a dataset with rows {'id': 0, 'id': 1, ...}."""
        return WasmDataset([{"id": i} for i in range(n)])

    @staticmethod
    def from_items(items: list[Any]) -> WasmDataset:
        """Create a dataset from an in-memory list."""
        return WasmDataset(items)


class WasmRayModule:
    """Pure-Python Ray Module singleton for WASM execution."""

    def __init__(self) -> None:
        self._store = WasmPlasmaStore()
        self._initialized = False
        self._init_context: dict[str, Any] = {}
        self.data = WasmDataModule()

    def is_initialized(self) -> bool:
        """Check if Ray simulation environment is initialized."""
        return self._initialized

    def init(
        self,
        address: str | None = None,
        ignore_reinit_error: bool = False,
        num_cpus: int = 4,
        num_gpus: int = 0,
        object_store_memory: int = 100_000_000,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Initialize the simulated Ray environment."""
        if self._initialized and not ignore_reinit_error:
            raise RuntimeError("Ray simulation is already initialized.")
        self._initialized = True
        self._init_context = {
            "node_ip_address": "127.0.0.1",
            "raylet_socket_name": "/tmp/ray/session_wasm/sockets/raylet",
            "object_store_socket_name": "/tmp/ray/session_wasm/sockets/plasma_store",
            "num_cpus": num_cpus,
            "num_gpus": num_gpus,
            "object_store_memory": object_store_memory,
            "session_name": f"session_wasm_{int(time.time())}",
        }
        return self._init_context

    def shutdown(self) -> None:
        """Shut down the simulated Ray environment and clear memory."""
        self._initialized = False
        self._init_context.clear()
        self._store.clear()

    def remote(
        self,
        target: Any = None,
        *,
        num_cpus: int = 1,
        num_gpus: int = 0,
        **kwargs: Any,
    ) -> Any:
        """Decorator or function creating a remote function or remote actor class."""
        options = {"num_cpus": num_cpus, "num_gpus": num_gpus, **kwargs}

        def decorator(obj: Any) -> Any:
            if inspect.isclass(obj):
                return WasmRemoteClass(obj, self._store, options)
            return WasmRemoteFunction(obj, self._store, options)

        if target is None:
            return decorator
        return decorator(target)

    def put(self, value: Any) -> WasmObjectRef[Any]:
        """Store a Python object into the simulated Plasma object store."""
        return self._store.put(value)

    def get(self, object_refs: WasmObjectRef[Any] | Sequence[WasmObjectRef[Any]]) -> Any:
        """Resolve one or multiple simulated ObjectRefs."""
        if isinstance(object_refs, WasmObjectRef):
            return self._store.get(object_refs)
        if isinstance(object_refs, (list, tuple)):
            return [
                self._store.get(ref) if isinstance(ref, WasmObjectRef) else ref
                for ref in object_refs
            ]
        return object_refs

    def wait(
        self,
        object_refs: list[WasmObjectRef[Any]],
        *,
        num_returns: int = 1,
        timeout: float | None = None,
    ) -> tuple[list[WasmObjectRef[Any]], list[WasmObjectRef[Any]]]:
        """Partition object refs into ready and unready subsets."""
        ready = object_refs[:num_returns]
        unready = object_refs[num_returns:]
        return ready, unready

    def get_cluster_resources(self) -> dict[str, Any]:
        """Return simulated cluster telemetry and resource utilization."""
        return {
            "CPU": self._init_context.get("num_cpus", 4),
            "GPU": self._init_context.get("num_gpus", 0),
            "object_store_objects": self._store.object_count,
            "object_store_used_bytes": self._store.total_used_bytes,
        }


# Global drop-in singleton mimicking `import ray`
ray = WasmRayModule()
