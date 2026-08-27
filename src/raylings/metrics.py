"""Real-time cluster telemetry, hardware metrics, and resource inspector for Raylings."""

import datetime
import json
import logging
import platform
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any

import ray
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from raylings.daemon import RayDaemon

logger = logging.getLogger("raylings.metrics")


def format_bytes(bytes_count: int | float) -> str:
    """Format a byte quantity into human-readable binary unit string (KB, MB, GB, TB).

    Args:
        bytes_count: Size in bytes.

    Returns:
        Formatted string (e.g. '100.0 MB', '2.5 GB', '0 B').
    """
    if bytes_count <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(bytes_count)
    unit_idx = 0
    while size >= 1024.0 and unit_idx < len(units) - 1:
        size /= 1024.0
        unit_idx += 1

    if unit_idx == 0:
        return f"{int(size)} B"
    return f"{size:.1f} {units[unit_idx]}"


def format_duration(seconds: float) -> str:
    """Format duration in seconds into a clean human-readable string.

    Args:
        seconds: Elapsed time in seconds.

    Returns:
        Formatted duration string (e.g. '45s', '2m 05s', '1h 01m 05s', '1d 02h 00m 00s').
    """
    total_sec = max(0, int(seconds))
    if total_sec < 60:
        return f"{total_sec}s"

    days, remainder = divmod(total_sec, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, sec = divmod(remainder, 60)

    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if days > 0 or hours > 0:
        parts.append(f"{hours:02d}h" if days > 0 else f"{hours}h")
    parts.append(f"{minutes:02d}m" if (days > 0 or hours > 0) else f"{minutes}m")
    parts.append(f"{sec:02d}s")

    return " ".join(parts)


def _format_percentage_bar(percent: float, width: int = 12) -> str:
    """Render a text progress gauge for a percentage value."""
    pct = max(0.0, min(100.0, percent))
    filled = int(round((pct / 100.0) * width))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct:5.1f}%"


@dataclass
class NodeMetrics:
    """Metrics and resource allocation data for an individual Ray cluster node."""

    node_id: str
    node_ip: str
    is_head_node: bool = False
    status: str = "ALIVE"
    cpu_cores_total: float = 0.0
    cpu_cores_used: float = 0.0
    cpu_percent: float = 0.0
    ram_total_bytes: int = 0
    ram_used_bytes: int = 0
    ram_percent: float = 0.0
    object_store_total_bytes: int = 0
    object_store_used_bytes: int = 0
    object_store_percent: float = 0.0
    gpus_total: float = 0.0
    gpus_used: float = 0.0
    custom_resources: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert node metrics to a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class ObjectStoreMetrics:
    """Plasma object store capacity, usage breakdown, and spilling telemetry."""

    total_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0
    usage_percent: float = 0.0
    active_objects: int = 0
    spilled_bytes: int = 0
    spilled_objects: int = 0
    restored_bytes: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert object store metrics to a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class ActorMetrics:
    """State, placement, and lifecycle statistics for an instantiated Ray actor."""

    actor_id: str
    name: str
    class_name: str
    state: str
    pid: int | None = None
    node_ip: str = ""
    node_id: str = ""
    restart_count: int = 0
    job_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert actor metrics to a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class TaskMetrics:
    """Task execution queue and state statistics across the cluster."""

    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    finished_tasks: int = 0
    failed_tasks: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert task metrics to a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class ClusterSnapshot:
    """Complete instantaneous snapshot of Ray cluster state and telemetry."""

    timestamp: float = field(default_factory=time.time)
    timestamp_iso: str = ""
    is_active: bool = False
    ray_version: str = ""
    python_version: str = ""
    cluster_address: str | None = None
    dashboard_url: str | None = None
    uptime_seconds: float = 0.0
    nodes: list[NodeMetrics] = field(default_factory=list)
    object_store: ObjectStoreMetrics = field(default_factory=ObjectStoreMetrics)
    actors: list[ActorMetrics] = field(default_factory=list)
    tasks: TaskMetrics = field(default_factory=TaskMetrics)
    total_cpus: float = 0.0
    used_cpus: float = 0.0
    total_gpus: float = 0.0
    used_gpus: float = 0.0
    error: str | None = None

    def __post_init__(self) -> None:
        if not self.timestamp_iso:
            self.timestamp_iso = datetime.datetime.fromtimestamp(
                self.timestamp, tz=datetime.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> dict[str, Any]:
        """Serialize snapshot to a nested Python dictionary."""
        return {
            "timestamp": self.timestamp,
            "timestamp_iso": self.timestamp_iso,
            "is_active": self.is_active,
            "ray_version": self.ray_version,
            "python_version": self.python_version,
            "cluster_address": self.cluster_address,
            "dashboard_url": self.dashboard_url,
            "uptime_seconds": self.uptime_seconds,
            "total_cpus": self.total_cpus,
            "used_cpus": self.used_cpus,
            "total_gpus": self.total_gpus,
            "used_gpus": self.used_gpus,
            "nodes": [n.to_dict() for n in self.nodes],
            "object_store": self.object_store.to_dict(),
            "actors": [a.to_dict() for a in self.actors],
            "tasks": self.tasks.to_dict(),
            "error": self.error,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize snapshot to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class ClusterMetricsCollector:
    """Telemetry collector that inspects Ray cluster state, nodes, memory, and actors."""

    def __init__(self, daemon: RayDaemon | None = None) -> None:
        """Initialize the metrics collector with optional RayDaemon reference."""
        self.daemon = daemon or RayDaemon()
        self._start_time: float = time.time()

    def _query_objects(self) -> list[Any]:
        """Query active object metadata from Ray state APIs."""
        for mod_name in ("ray.util.state", "ray.experimental.state.api"):
            try:
                mod = sys.modules.get(mod_name)
                if mod is None:
                    import importlib

                    mod = importlib.import_module(mod_name)
                if hasattr(mod, "list_objects"):
                    res = mod.list_objects()
                    return list(res) if res is not None else []
            except Exception as e:
                logger.debug("Query objects from %s failed: %s", mod_name, e)
        return []

    def _query_actors(self) -> list[Any]:
        """Query active actor records from Ray state APIs or private state."""
        for mod_name in ("ray.util.state", "ray.experimental.state.api"):
            try:
                mod = sys.modules.get(mod_name)
                if mod is None:
                    import importlib

                    mod = importlib.import_module(mod_name)
                if hasattr(mod, "list_actors"):
                    res = mod.list_actors()
                    return list(res) if res is not None else []
            except Exception as e:
                logger.debug("Query actors from %s failed: %s", mod_name, e)

        # Fallback to internal actor table if available
        try:
            import ray._private.state

            actors_dict = ray._private.state.actors()
            if isinstance(actors_dict, dict):
                return list(actors_dict.values())
        except Exception as e:
            logger.debug("Query actors from internal state failed: %s", e)

        return []

    def _query_tasks(self) -> list[Any]:
        """Query active and queued tasks from Ray state APIs."""
        for mod_name in ("ray.util.state", "ray.experimental.state.api"):
            try:
                mod = sys.modules.get(mod_name)
                if mod is None:
                    import importlib

                    mod = importlib.import_module(mod_name)
                if hasattr(mod, "list_tasks"):
                    res = mod.list_tasks()
                    return list(res) if res is not None else []
            except Exception as e:
                logger.debug("Query tasks from %s failed: %s", mod_name, e)
        return []

    def collect_snapshot(self) -> ClusterSnapshot:
        """Query active Ray cluster and return a comprehensive ClusterSnapshot.

        Returns:
            ClusterSnapshot instance containing node, memory, actor, and task metrics.
        """
        now = time.time()
        py_ver = platform.python_version()
        ray_ver = getattr(ray, "__version__", "unknown")

        if not ray.is_initialized():
            return ClusterSnapshot(
                timestamp=now,
                is_active=False,
                ray_version=ray_ver,
                python_version=py_ver,
                error="Ray daemon or cluster session is inactive / not running.",
            )

        try:
            ctx = ray.get_runtime_context()
            gcs_addr = getattr(ctx, "gcs_address", None)
            dashboard_url = getattr(ctx, "dashboard_url", None)

            cluster_res = ray.cluster_resources() or {}
            avail_res = ray.available_resources() or {}
            raw_nodes = ray.nodes() or []

            total_cpus = float(cluster_res.get("CPU", 0.0))
            avail_cpus = float(avail_res.get("CPU", total_cpus))
            used_cpus = max(0.0, total_cpus - avail_cpus)

            total_gpus = float(cluster_res.get("GPU", 0.0))
            avail_gpus = float(avail_res.get("GPU", total_gpus))
            used_gpus = max(0.0, total_gpus - avail_gpus)

            total_obj_store = int(cluster_res.get("object_store_memory", 0))
            avail_obj_store = int(avail_res.get("object_store_memory", total_obj_store))
            used_obj_store = max(0, total_obj_store - avail_obj_store)
            obj_pct = (used_obj_store / total_obj_store * 100.0) if total_obj_store > 0 else 0.0

            # Node breakdown
            nodes_list: list[NodeMetrics] = []
            for idx, n in enumerate(raw_nodes):
                n_id = str(n.get("NodeID", f"node-{idx}"))
                n_ip = str(n.get("NodeManagerAddress") or n.get("NodeIP") or "127.0.0.1")
                is_alive = bool(n.get("Alive", True))
                status = "ALIVE" if is_alive else "DEAD"
                is_head = idx == 0

                res = n.get("Resources", {})
                n_cpu_total = float(res.get("CPU", total_cpus))
                n_cpu_used = used_cpus if len(raw_nodes) == 1 else 0.0
                n_cpu_pct = (n_cpu_used / n_cpu_total * 100.0) if n_cpu_total > 0 else 0.0

                n_ram_total = int(res.get("memory", 0))
                n_ram_used = 0
                n_ram_pct = (n_ram_used / n_ram_total * 100.0) if n_ram_total > 0 else 0.0

                n_obj_total = int(res.get("object_store_memory", total_obj_store))
                n_obj_used = used_obj_store if len(raw_nodes) == 1 else 0
                n_obj_pct = (n_obj_used / n_obj_total * 100.0) if n_obj_total > 0 else 0.0

                n_gpu_total = float(res.get("GPU", 0.0))
                n_gpu_used = used_gpus if len(raw_nodes) == 1 else 0.0

                nodes_list.append(
                    NodeMetrics(
                        node_id=n_id,
                        node_ip=n_ip,
                        is_head_node=is_head,
                        status=status,
                        cpu_cores_total=n_cpu_total,
                        cpu_cores_used=n_cpu_used,
                        cpu_percent=round(n_cpu_pct, 1),
                        ram_total_bytes=n_ram_total,
                        ram_used_bytes=n_ram_used,
                        ram_percent=round(n_ram_pct, 1),
                        object_store_total_bytes=n_obj_total,
                        object_store_used_bytes=n_obj_used,
                        object_store_percent=round(n_obj_pct, 1),
                        gpus_total=n_gpu_total,
                        gpus_used=n_gpu_used,
                    )
                )

            # Object store telemetry
            try:
                raw_objects = self._query_objects()
            except Exception as e:
                logger.debug("Failed to query objects: %s", e)
                raw_objects = []
            active_objects = len(raw_objects)
            spilled_bytes = 0
            spilled_objects = 0
            restored_bytes = 0

            obj_store_metrics = ObjectStoreMetrics(
                total_bytes=total_obj_store,
                used_bytes=used_obj_store,
                free_bytes=avail_obj_store,
                usage_percent=round(obj_pct, 1),
                active_objects=active_objects,
                spilled_bytes=spilled_bytes,
                spilled_objects=spilled_objects,
                restored_bytes=restored_bytes,
            )

            # Actor table
            actors_list: list[ActorMetrics] = []
            try:
                raw_actors = self._query_actors()
            except Exception as e:
                logger.debug("Failed to query actors: %s", e)
                raw_actors = []

            for act in raw_actors:
                if isinstance(act, dict):
                    a_id = str(act.get("actor_id", ""))
                    a_name = str(act.get("name") or act.get("class_name") or "Unnamed")
                    a_class = str(act.get("class_name") or a_name)
                    a_state = str(act.get("state", "ALIVE"))
                    a_pid = act.get("pid")
                    a_ip = str(act.get("node_ip_address") or "")
                    a_node_id = str(act.get("node_id") or "")
                    a_restarts = int(act.get("num_restarts") or 0)
                    a_job = str(act.get("job_id") or "")
                else:
                    a_id = getattr(act, "actor_id", "")
                    a_name = getattr(act, "name", "") or getattr(act, "class_name", "Actor")
                    a_class = getattr(act, "class_name", a_name)
                    a_state = getattr(act, "state", "ALIVE")
                    a_pid = getattr(act, "pid", None)
                    a_ip = getattr(act, "node_ip_address", "")
                    a_node_id = getattr(act, "node_id", "")
                    a_restarts = getattr(act, "num_restarts", 0)
                    a_job = getattr(act, "job_id", "")

                actors_list.append(
                    ActorMetrics(
                        actor_id=a_id,
                        name=a_name,
                        class_name=a_class,
                        state=a_state,
                        pid=a_pid,
                        node_ip=a_ip,
                        node_id=a_node_id,
                        restart_count=a_restarts,
                        job_id=a_job,
                    )
                )

            # Task metrics
            task_metrics = TaskMetrics()
            try:
                raw_tasks = self._query_tasks()
            except Exception as e:
                logger.debug("Failed to query tasks: %s", e)
                raw_tasks = []

            task_metrics.total_tasks = len(raw_tasks)
            for t in raw_tasks:
                st = t.get("state", "") if isinstance(t, dict) else getattr(t, "state", "")
                st_upper = str(st).upper()
                if "PENDING" in st_upper:
                    task_metrics.pending_tasks += 1
                elif "RUNNING" in st_upper:
                    task_metrics.running_tasks += 1
                elif "FINISHED" in st_upper:
                    task_metrics.finished_tasks += 1
                elif "FAILED" in st_upper:
                    task_metrics.failed_tasks += 1

            uptime = max(0.0, now - self._start_time)

            return ClusterSnapshot(
                timestamp=now,
                is_active=True,
                ray_version=ray_ver,
                python_version=py_ver,
                cluster_address=gcs_addr,
                dashboard_url=dashboard_url,
                uptime_seconds=uptime,
                nodes=nodes_list,
                object_store=obj_store_metrics,
                actors=actors_list,
                tasks=task_metrics,
                total_cpus=total_cpus,
                used_cpus=used_cpus,
                total_gpus=total_gpus,
                used_gpus=used_gpus,
                error=None,
            )

        except Exception as e:
            logger.exception("Error collecting Ray cluster snapshot")
            return ClusterSnapshot(
                timestamp=now,
                is_active=True,
                ray_version=ray_ver,
                python_version=py_ver,
                error=f"Error querying cluster state: {e}",
            )


def render_metrics_dashboard(
    snapshot: ClusterSnapshot,
    console: Console | None = None,
) -> RenderableType:
    """Render a comprehensive multi-panel Rich dashboard visualizing cluster metrics.

    Args:
        snapshot: ClusterSnapshot containing telemetry.
        console: Optional Console instance.

    Returns:
        Rich Renderable (Panel or Group) suitable for direct printing or Live updating.
    """
    if not snapshot.is_active:
        err_msg = snapshot.error or "Ray cluster session is currently inactive."
        inactive_text = Text()
        inactive_text.append("⚡ Ray Cluster Session: Inactive / Stopped\n\n", style="bold yellow")
        inactive_text.append(f"{err_msg}\n\n", style="white")
        inactive_text.append("Quick Start Instructions:\n", style="bold cyan")
        inactive_text.append(
            "  • Start cluster daemon:  [bold green]raylings daemon start[/bold green]\n",
            style="white",
        )
        inactive_text.append(
            "  • Run an exercise:       [bold green]raylings watch[/bold green] or [bold green]raylings run <exercise>[/bold green]\n",
            style="white",
        )
        inactive_text.append(
            "  • Check health preflight: [bold green]raylings doctor[/bold green]\n", style="white"
        )
        return Panel(
            inactive_text,
            title="[bold yellow]⚡ Ray Cluster Health & Telemetry Inspector[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

    # 1. Header Overview Panel
    cpu_pct = (snapshot.used_cpus / snapshot.total_cpus * 100.0) if snapshot.total_cpus > 0 else 0.0
    header_table = Table.grid(expand=True, padding=(0, 2))
    header_table.add_column("Key", style="bold cyan", width=18)
    header_table.add_column("Val", style="white", width=28)
    header_table.add_column("Key2", style="bold cyan", width=18)
    header_table.add_column("Val2", style="white")

    header_table.add_row(
        "Cluster Status:",
        "[bold green]● Active & Healthy[/bold green]",
        "Cluster Uptime:",
        f"[bold white]{format_duration(snapshot.uptime_seconds)}[/bold white]",
    )
    header_table.add_row(
        "Ray Version:",
        f"v{snapshot.ray_version}",
        "Python Runtime:",
        f"Python {snapshot.python_version}",
    )
    header_table.add_row(
        "GCS Address:",
        str(snapshot.cluster_address or "127.0.0.1:6379"),
        "Active Nodes:",
        f"[bold cyan]{len(snapshot.nodes)}[/bold cyan] node(s)",
    )
    header_table.add_row(
        "Total CPU Cores:",
        f"{snapshot.used_cpus:.1f} / {snapshot.total_cpus:.1f} ({cpu_pct:.1f}%)",
        "Total GPUs:",
        f"{snapshot.used_gpus:.1f} / {snapshot.total_gpus:.1f}",
    )

    header_panel = Panel(
        header_table,
        title="[bold green]⚡ Ray Cluster Telemetry Inspector[/bold green]",
        border_style="bright_blue",
        padding=(0, 1),
    )

    # 2. Node Resources Table
    nodes_table = Table(
        title="Cluster Nodes & Resource Allocation",
        border_style="dim",
        header_style="bold magenta",
        expand=True,
    )
    nodes_table.add_column("Node IP / Host", style="bold cyan", width=18)
    nodes_table.add_column("Role", justify="center", width=10)
    nodes_table.add_column("Status", justify="center", width=10)
    nodes_table.add_column("CPU Usage", justify="left", width=22)
    nodes_table.add_column("Object Store Memory", justify="left", width=24)
    nodes_table.add_column("GPUs", justify="center", width=8)

    for n in snapshot.nodes:
        role_str = "[bold magenta]Head[/bold magenta]" if n.is_head_node else "Worker"
        st_str = (
            "[bold green]ALIVE[/bold green]" if n.status == "ALIVE" else "[bold red]DEAD[/bold red]"
        )
        cpu_gauge = _format_percentage_bar(n.cpu_percent, width=8)
        obj_used_fmt = format_bytes(n.object_store_used_bytes)
        obj_tot_fmt = format_bytes(n.object_store_total_bytes)
        obj_str = f"{obj_used_fmt} / {obj_tot_fmt} ({n.object_store_percent:.1f}%)"
        gpu_str = f"{n.gpus_used:.0f}/{n.gpus_total:.0f}"

        nodes_table.add_row(
            n.node_ip,
            role_str,
            st_str,
            f"{n.cpu_cores_used:.1f}/{n.cpu_cores_total:.1f} {cpu_gauge}",
            obj_str,
            gpu_str,
        )

    # 3. Object Store (Plasma) Panel
    obj = snapshot.object_store
    obj_used_fmt = format_bytes(obj.used_bytes)
    obj_tot_fmt = format_bytes(obj.total_bytes)
    obj_free_fmt = format_bytes(obj.free_bytes)
    obj_gauge = _format_percentage_bar(obj.usage_percent, width=16)

    obj_table = Table.grid(expand=True, padding=(0, 2))
    obj_table.add_column(style="bold cyan", width=22)
    obj_table.add_column(style="white", width=26)
    obj_table.add_column(style="bold cyan", width=22)
    obj_table.add_column(style="white")

    obj_table.add_row(
        "Plasma Allocation:",
        f"{obj_used_fmt} / {obj_tot_fmt}",
        "Active Objects:",
        f"[bold white]{obj.active_objects}[/bold white] in memory",
    )
    obj_table.add_row(
        "Usage Capacity:",
        obj_gauge,
        "Spilled Objects:",
        f"{obj.spilled_objects} ({format_bytes(obj.spilled_bytes)})",
    )
    obj_table.add_row(
        "Available Space:",
        f"[bold green]{obj_free_fmt}[/bold green]",
        "Restored Objects:",
        f"{format_bytes(obj.restored_bytes)}",
    )

    obj_panel = Panel(
        obj_table,
        title="[bold cyan]📦 Plasma Object Store & Memory Telemetry[/bold cyan]",
        border_style="cyan",
        padding=(0, 1),
    )

    # 4. Actor State Table
    actor_table = Table(
        title="Instantiated Actors",
        border_style="dim",
        header_style="bold magenta",
        expand=True,
    )
    actor_table.add_column("Actor ID", style="dim cyan", width=18)
    actor_table.add_column("Class / Name", style="bold white", width=24)
    actor_table.add_column("PID", justify="right", style="yellow", width=8)
    actor_table.add_column("State", justify="center", width=12)
    actor_table.add_column("Node IP", style="dim white", width=16)
    actor_table.add_column("Restarts", justify="right", width=10)

    if snapshot.actors:
        for a in snapshot.actors:
            state_color = (
                "green" if a.state == "ALIVE" else ("yellow" if "RESTART" in a.state else "red")
            )
            st_markup = f"[bold {state_color}]{a.state}[/bold {state_color}]"
            pid_str = str(a.pid) if a.pid is not None else "-"
            actor_table.add_row(
                a.actor_id[:16] if len(a.actor_id) > 16 else a.actor_id,
                a.name or a.class_name,
                pid_str,
                st_markup,
                a.node_ip or "127.0.0.1",
                str(a.restart_count),
            )
    else:
        actor_table.add_row(
            "[dim]None[/dim]",
            "[dim]No active actors in cluster session[/dim]",
            "-",
            "[dim]-[/dim]",
            "-",
            "-",
        )

    return Group(
        header_panel,
        nodes_table,
        obj_panel,
        actor_table,
    )


def run_top_dashboard(
    interval: float = 1.0,
    once: bool = False,
    as_json: bool = False,
    collector: ClusterMetricsCollector | None = None,
    console: Console | None = None,
) -> None:
    """Execute live-updating Ray top telemetry dashboard or output single snapshot.

    Args:
        interval: Refresh period in seconds for live dashboard.
        once: If True, renders single snapshot and returns immediately.
        as_json: If True, prints snapshot as JSON to stdout.
        collector: Optional ClusterMetricsCollector instance.
        console: Optional Rich Console instance.
    """
    col = collector or ClusterMetricsCollector()
    c = console or Console()

    if as_json:
        snapshot = col.collect_snapshot()
        print(snapshot.to_json())
        return

    if once:
        snapshot = col.collect_snapshot()
        c.print(render_metrics_dashboard(snapshot, console=c))
        return

    # Live refresh dashboard loop
    try:
        initial_snap = col.collect_snapshot()
        with Live(
            render_metrics_dashboard(initial_snap, console=c),
            console=c,
            refresh_per_second=max(1, int(1.0 / max(0.1, interval))),
            screen=True,
        ) as live:
            while True:
                time.sleep(interval)
                snapshot = col.collect_snapshot()
                live.update(render_metrics_dashboard(snapshot, console=c))
    except KeyboardInterrupt:
        pass
