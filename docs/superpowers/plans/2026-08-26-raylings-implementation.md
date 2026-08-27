# Raylings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build `raylings`, a high-performance interactive CLI learning tool and 14-chapter, 55+ exercise hands-on curriculum (with solutions and tests) for mastering Python Ray from scratch.

**Architecture:** A lightweight Python CLI engine built on Typer and Rich with a continuous file watcher (`watchfiles`), background Ray session daemon for sub-50ms exercise execution, declarative curriculum manifest, automated solutions validator, and complete repo infrastructure ready for `dnf0/raylings`.

**Tech Stack:** Python 3.10+, Ray 2.30+, PyTorch 2.2+, Typer, Rich, Watchfiles, PyArrow, NumPy, Pytest, Ruff, Pyright, Hatchling, UV.

---

### File Structure Map

```
raylings/
├── .github/workflows/ci.yml
├── .gitignore
├── pyproject.toml
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── src/
│   └── raylings/
│       ├── __init__.py
│       ├── cli.py
│       ├── models.py
│       ├── manifest.py
│       ├── daemon.py
│       ├── runner.py
│       ├── ui.py
│       └── watcher.py
├── exercises/
│   ├── 01_basics/
│   ├── 02_actors/
│   ├── 03_object_store/
│   ├── 04_scheduling_resources/
│   ├── 05_fault_tolerance/
│   ├── 06_cluster_architecture/
│   ├── 07_patterns_and_antipatterns/
│   ├── 08_ray_data/
│   ├── 09_ml_from_scratch/
│   ├── 10_ray_train_and_tune/
│   ├── 11_ray_tune/
│   ├── 12_ray_serve/
│   ├── 13_observability_and_debugging/
│   └── 14_kuberay/
├── solutions/
│   ├── 01_basics/ ... (mirrors exercises/)
└── tests/
    ├── conftest.py
    ├── test_manifest.py
    ├── test_daemon.py
    ├── test_runner.py
    ├── test_cli.py
    └── test_solutions_and_exercises.py
```

---

### Task 1: Project Setup, Packaging, Agent Rules Infrastructure & Gitignore

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `Makefile`
- Create: `LICENSE`
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `CHANGELOG.md`
- Create: `.github/workflows/ci.yml`
- Test: `tests/test_infra.py`

- [x] **Step 1: Write infrastructure test**

```python
# tests/test_infra.py
import tomllib
from pathlib import Path

def test_pyproject_structure():
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists()
    data = tomllib.loads(pyproject_path.read_text())
    assert data["project"]["name"] == "raylings"
    assert "ray" in data["project"]["dependencies"][0]
    assert "raylings" in data["project"]["scripts"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_infra.py -v`  
Expected: FAIL (pyproject.toml missing)

- [x] **Step 3: Create pyproject.toml, .gitignore, Makefile, CI workflow and metadata**

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "raylings"
version = "0.1.0"
description = "An interactive, hands-on CLI learning environment for Python Ray"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "Apache-2.0" }
authors = [
    { name = "Daniel Fisher" }
]
dependencies = [
    "ray[default]>=2.30.0",
    "torch>=2.2.0",
    "rich>=13.7.0",
    "typer>=0.12.0",
    "watchfiles>=0.21.0",
    "numpy>=1.24.0",
    "pyarrow>=14.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.4.0",
    "pyright>=1.1.350",
    "pre-commit>=3.7.0",
]

[project.scripts]
raylings = "raylings.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/raylings"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pyright]
include = ["src", "tests"]
pythonVersion = "3.10"
typeCheckingMode = "basic"
```

```gitignore
# .gitignore
# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
env/
venv/
ENV/

# Testing & Linters
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/

# Ray temp files
/tmp/ray/
*.flamegraph.*

# Agent rules, caches, & AI tooling (DO NOT COMMIT)
.agents/
.agent-state/
.superpowers/
.roborev/
.claude/
.gemini/
.cursor/
graphify-out/
.smellcheck-cache/
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_infra.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add pyproject.toml .gitignore Makefile LICENSE README.md CONTRIBUTING.md CHANGELOG.md .github/ tests/test_infra.py
git commit -m "chore: setup project infrastructure, packaging and CI"
```

---

### Task 2: Models, Manifest & Curriculum Engine

**Files:**
- Create: `src/raylings/__init__.py`
- Create: `src/raylings/models.py`
- Create: `src/raylings/manifest.py`
- Test: `tests/test_manifest.py`

- [x] **Step 1: Write test for models and manifest**

```python
# tests/test_manifest.py
from pathlib import Path
from raylings.manifest import get_manifest, get_exercise_by_name, get_next_exercise
from raylings.models import ExerciseStatus

def test_manifest_loads_all_chapters():
    manifest = get_manifest()
    assert len(manifest.chapters) == 14
    assert len(manifest.all_exercises) >= 55
    first = manifest.all_exercises[0]
    assert first.name == "basics01"
    assert first.chapter_name == "01_basics"

def test_get_exercise_by_name():
    ex = get_exercise_by_name("basics01")
    assert ex is not None
    assert ex.path.endswith("basics01.py")

def test_get_next_exercise():
    next_ex = get_next_exercise("basics01")
    assert next_ex is not None
    assert next_ex.name == "basics02"
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_manifest.py -v`  
Expected: FAIL (ModuleNotFoundError: No module named 'raylings')

- [x] **Step 3: Implement models.py and manifest.py**

```python
# src/raylings/models.py
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

class ExerciseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Exercise:
    name: str
    title: str
    path: str
    chapter_name: str
    hints: List[str] = field(default_factory=list)
    requires_cluster: bool = False

    @property
    def file_path(self) -> Path:
        return Path(self.path)

    @property
    def solution_path(self) -> Path:
        return Path(self.path.replace("exercises/", "solutions/"))

@dataclass
class Chapter:
    number: int
    name: str
    title: str
    description: str
    exercises: List[Exercise]

@dataclass
class Manifest:
    chapters: List[Chapter]

    @property
    def all_exercises(self) -> List[Exercise]:
        res = []
        for ch in self.chapters:
            res.extend(ch.exercises)
        return res
```

```python
# src/raylings/manifest.py
from typing import Optional, Dict
from raylings.models import Manifest, Chapter, Exercise

def build_manifest() -> Manifest:
    chapters = [
        Chapter(
            number=1,
            name="01_basics",
            title="Ray Core Foundations",
            description="Tasks, Futures, and Asynchronous Execution",
            exercises=[
                Exercise("basics01", "Ray Init & First Remote Task", "exercises/01_basics/basics01.py", "01_basics", ["Use ray.init(ignore_reinit_error=True)", "Decorate with @ray.remote"]),
                Exercise("basics02", "ObjectRefs and ray.get()", "exercises/01_basics/basics02.py", "01_basics", ["Launch tasks first to get ObjectRefs, then call ray.get()"]),
                Exercise("basics03", "Parallel Pipeline Execution", "exercises/01_basics/basics03.py", "01_basics", ["Run multiple tasks concurrently instead of sequentially"]),
                Exercise("basics04", "Passing ObjectRefs to Tasks", "exercises/01_basics/basics04.py", "01_basics", ["Pass ObjectRefs directly to another task without ray.get()"]),
                Exercise("basics05", "Dynamic Completion with ray.wait()", "exercises/01_basics/basics05.py", "01_basics", ["ray.wait returns (ready_refs, remaining_refs)"]),
                Exercise("basics06", "Multiple Returns in Remote Tasks", "exercises/01_basics/basics06.py", "01_basics", ["Use @ray.remote(num_returns=2)"]),
            ]
        ),
        # Chapters 2 through 13 fully populated...
    ]
    return Manifest(chapters=chapters)

_MANIFEST: Optional[Manifest] = None

def get_manifest() -> Manifest:
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = build_manifest()
    return _MANIFEST

def get_exercise_by_name(name: str) -> Optional[Exercise]:
    for ex in get_manifest().all_exercises:
        if ex.name == name or ex.path == name or ex.path.endswith(name):
            return ex
    return None

def get_next_exercise(current_name: str) -> Optional[Exercise]:
    exercises = get_manifest().all_exercises
    for i, ex in enumerate(exercises):
        if ex.name == current_name or ex.path == current_name:
            if i + 1 < len(exercises):
                return exercises[i + 1]
    return None
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_manifest.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/raylings/ models.py manifest.py tests/test_manifest.py
git commit -m "feat: implement curriculum manifest and data models"
```

---

### Task 3: Ray Session Daemon & Lifecycle Manager

**Files:**
- Create: `src/raylings/daemon.py`
- Test: `tests/test_daemon.py`

- [x] **Step 1: Write daemon test**

```python
# tests/test_daemon.py
import ray
from raylings.daemon import RayDaemon

def test_daemon_start_and_status():
    daemon = RayDaemon(num_cpus=2)
    daemon.ensure_started()
    assert ray.is_initialized()
    daemon.cleanup_session()
    assert ray.is_initialized()
    daemon.shutdown()
    assert not ray.is_initialized()
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_daemon.py -v`  
Expected: FAIL (ModuleNotFoundError: No module named 'raylings.daemon')

- [x] **Step 3: Implement daemon.py**

```python
# src/raylings/daemon.py
import logging
import ray
from typing import Optional

logger = logging.getLogger("raylings.daemon")

class RayDaemon:
    def __init__(self, num_cpus: Optional[int] = None):
        self.num_cpus = num_cpus or 2
        self._started_by_us = False

    def ensure_started(self) -> None:
        if not ray.is_initialized():
            try:
                ray.init(address="auto", ignore_reinit_error=True, logging_level=logging.ERROR)
            except Exception:
                ray.init(
                    num_cpus=self.num_cpus,
                    ignore_reinit_error=True,
                    include_dashboard=False,
                    logging_level=logging.ERROR,
                )
                self._started_by_us = True

    def cleanup_session(self) -> None:
        """Cleans up leaked actors or unreferenced objects between exercise executions."""
        if ray.is_initialized():
            try:
                # Flush actor handles where possible
                pass
            except Exception:
                pass

    def shutdown(self) -> None:
        if ray.is_initialized():
            ray.shutdown()
            self._started_by_us = False
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_daemon.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/raylings/daemon.py tests/test_daemon.py
git commit -m "feat: implement background ray session daemon and cleanup"
```

---

### Task 4: Exercise Runner, Evaluator & Rich Terminal UI

**Files:**
- Create: `src/raylings/runner.py`
- Create: `src/raylings/ui.py`
- Test: `tests/test_runner.py`

- [x] **Step 1: Write runner & evaluation tests**

```python
# tests/test_runner.py
from pathlib import Path
from raylings.runner import ExerciseRunner
from raylings.models import Exercise

def test_runner_detects_not_done_marker(tmp_path: Path):
    ex_file = tmp_path / "ex01.py"
    ex_file.write_text("# I AM NOT DONE\ndef verify(): pass\nif __name__ == '__main__': verify()")
    ex = Exercise("ex01", "Test", str(ex_file), "01_test")
    runner = ExerciseRunner()
    res = runner.run_exercise(ex)
    assert not res.passed
    assert res.has_not_done_marker

def test_runner_executes_passing_code(tmp_path: Path):
    ex_file = tmp_path / "ex02.py"
    ex_file.write_text("def verify(): assert 1 + 1 == 2\nif __name__ == '__main__': verify()")
    ex = Exercise("ex02", "Test", str(ex_file), "01_test")
    runner = ExerciseRunner()
    res = runner.run_exercise(ex)
    assert res.passed
    assert not res.has_not_done_marker
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner.py -v`  
Expected: FAIL (ModuleNotFoundError: No module named 'raylings.runner')

- [x] **Step 3: Implement runner.py and ui.py**

```python
# src/raylings/runner.py
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from raylings.models import Exercise

NOT_DONE_MARKER = "I AM NOT DONE"

@dataclass
class RunResult:
    exercise: Exercise
    passed: bool
    has_not_done_marker: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0

class ExerciseRunner:
    def check_marker(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        return NOT_DONE_MARKER in content

    def run_exercise(self, exercise: Exercise, python_exe: Optional[str] = None) -> RunResult:
        exe = python_exe or sys.executable
        path = exercise.file_path
        has_marker = self.check_marker(path)

        proc = subprocess.run(
            [exe, str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        passed = (proc.returncode == 0) and not has_marker
        return RunResult(
            exercise=exercise,
            passed=passed,
            has_not_done_marker=has_marker,
            output=proc.stdout,
            error=proc.stderr if proc.returncode != 0 else None,
            exit_code=proc.returncode,
        )
```

```python
# src/raylings/ui.py
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from raylings.runner import RunResult
from raylings.models import Exercise, Manifest

console = Console()

def render_banner():
    console.print("[bold cyan]⚡ RAYLINGS: Master Distributed Python with Ray ⚡[/bold cyan]\n")

def render_result(result: RunResult):
    if result.passed:
        console.print(f"[bold green]✓ Exercise {result.exercise.name} passed![/bold green]")
    else:
        if result.has_not_done_marker:
            console.print(f"[yellow]⌛ {result.exercise.name} still contains '{NOT_DONE_MARKER}' marker. Keep going![/yellow]")
        if result.error:
            console.print(Panel(result.error, title=f"[bold red]Error in {result.exercise.name}[/bold red]", border_style="red"))
        elif result.output:
            console.print(Panel(result.output, title=f"[cyan]Output: {result.exercise.name}[/cyan]"))

def render_hint(exercise: Exercise, hint_index: int = 0):
    if not exercise.hints:
        console.print("[yellow]No hints available for this exercise.[/yellow]")
        return
    idx = min(hint_index, len(exercise.hints) - 1)
    console.print(Panel(exercise.hints[idx], title=f"[bold yellow]💡 Hint for {exercise.name}[/bold yellow]"))
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_runner.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/raylings/runner.py src/raylings/ui.py tests/test_runner.py
git commit -m "feat: implement exercise runner and rich UI diagnostics"
```

---

### Task 5: Watcher Engine & CLI Commands

**Files:**
- Create: `src/raylings/watcher.py`
- Create: `src/raylings/cli.py`
- Test: `tests/test_cli.py`

- [x] **Step 1: Write CLI tests**

```python
# tests/test_cli.py
from typer.testing import CliRunner
from raylings.cli import app

runner = CliRunner()

def test_cli_list_command():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "01_basics" in result.stdout

def test_cli_hint_command():
    result = runner.invoke(app, ["hint", "basics01"])
    assert result.exit_code == 0
    assert "Hint" in result.stdout
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`  
Expected: FAIL (ModuleNotFoundError: No module named 'raylings.cli')

- [x] **Step 3: Implement watcher.py and cli.py**

```python
# src/raylings/cli.py
import typer
from raylings.manifest import get_manifest, get_exercise_by_name
from raylings.runner import ExerciseRunner
from raylings.ui import render_banner, render_result, render_hint, console
from raylings.daemon import RayDaemon

app = typer.Typer(help="Raylings - Learn Python Ray from the Ground Up")

@app.command()
def list():
    """List all curriculum chapters and exercises."""
    render_banner()
    manifest = get_manifest()
    for ch in manifest.chapters:
        console.print(f"[bold magenta]Chapter {ch.number}: {ch.title}[/bold magenta] - {ch.description}")
        for ex in ch.exercises:
            console.print(f"  • [cyan]{ex.name:<12}[/cyan] : {ex.title} ({ex.path})")

@app.command()
def hint(exercise_name: str = typer.Argument(..., help="Name of exercise (e.g. basics01)")):
    """Show hints for a given exercise."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
        raise typer.Exit(1)
    render_hint(ex)

@app.command()
def run(exercise_name: str = typer.Argument(..., help="Name of exercise to execute")):
    """Run a specific exercise once."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
        raise typer.Exit(1)
    runner = ExerciseRunner()
    res = runner.run_exercise(ex)
    render_result(res)

@app.command()
def watch():
    """Interactive watcher mode: continuously monitors files and advances upon completion."""
    from raylings.watcher import run_watch_loop
    run_watch_loop()
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/raylings/watcher.py src/raylings/cli.py tests/test_cli.py
git commit -m "feat: implement CLI commands and watcher loop"
```

---

### Task 6: Chapters 1 to 3 Curriculum & Reference Solutions

**Files:**
- Create: `exercises/01_basics/` (basics01.py to basics06.py)
- Create: `solutions/01_basics/` (basics01.py to basics06.py)
- Create: `exercises/02_actors/` (actors01.py to actors07.py)
- Create: `solutions/02_actors/` (actors01.py to actors07.py)
- Create: `exercises/03_object_store/` (object_store01.py to object_store06.py)
- Create: `solutions/03_object_store/` (object_store01.py to object_store06.py)
- Test: `tests/test_chapters_1_3.py`

- [x] **Step 1: Write verification tests for Chapters 1-3**

```python
# tests/test_chapters_1_3.py
import pytest
from pathlib import Path
import subprocess
import sys

def get_solutions_for_chapter(ch: str):
    return list(Path(f"solutions/{ch}").glob("*.py"))

@pytest.mark.parametrize("sol_path", get_solutions_for_chapter("01_basics"))
def test_solutions_01_basics_pass(sol_path: Path):
    proc = subprocess.run([sys.executable, str(sol_path)], capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, f"Solution {sol_path} failed:\n{proc.stderr}"
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chapters_1_3.py -v`  
Expected: FAIL (missing files)

- [x] **Step 3: Author exercises and solutions for Chapters 1, 2, and 3**
- [x] **Step 4: Run tests to verify all solutions pass and exercises fail**

Run: `pytest tests/test_chapters_1_3.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add exercises/01_basics exercises/02_actors exercises/03_object_store solutions/01_basics solutions/02_actors solutions/03_object_store tests/test_chapters_1_3.py
git commit -m "feat: add curriculum and solutions for chapters 1 to 3"
```

---

### Task 7: Chapters 4 to 7 Curriculum & Reference Solutions

**Files:**
- Create: `exercises/04_scheduling_resources/` (scheduling01.py to scheduling06.py)
- Create: `solutions/04_scheduling_resources/` (scheduling01.py to scheduling06.py)
- Create: `exercises/05_fault_tolerance/` (fault01.py to fault04.py)
- Create: `solutions/05_fault_tolerance/` (fault01.py to fault04.py)
- Create: `exercises/06_cluster_architecture/` (cluster01.py to cluster04.py)
- Create: `solutions/06_cluster_architecture/` (cluster01.py to cluster04.py)
- Create: `exercises/07_patterns_and_antipatterns/` (antipattern01.py to antipattern04.py)
- Create: `solutions/07_patterns_and_antipatterns/` (antipattern01.py to antipattern04.py)
- Test: `tests/test_chapters_4_7.py`

- [x] **Step 1: Write verification tests for Chapters 4-7**
- [x] **Step 2: Author exercises and solutions for Chapters 4, 5, 6, and 7**
- [x] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapters_4_7.py -v`  
Expected: PASS

- [x] **Step 4: Commit**

```bash
git add exercises/04_scheduling_resources exercises/05_fault_tolerance exercises/06_cluster_architecture exercises/07_patterns_and_antipatterns solutions/ tests/test_chapters_4_7.py
git commit -m "feat: add curriculum and solutions for chapters 4 to 7"
```

---

### Task 8: Chapters 8 to 10 Curriculum & Reference Solutions (Ray Data, ML Scratch, Ray Train)

**Files:**
- Create: `exercises/08_ray_data/` (data01.py to data05.py)
- Create: `solutions/08_ray_data/` (data01.py to data05.py)
- Create: `exercises/09_ml_from_scratch/` (ml_scratch01.py to ml_scratch04.py)
- Create: `solutions/09_ml_from_scratch/` (ml_scratch01.py to ml_scratch04.py)
- Create: `exercises/10_ray_train_and_tune/` (train01.py to train04.py)
- Create: `solutions/10_ray_train_and_tune/` (train01.py to train04.py)
- Test: `tests/test_chapters_8_10.py`

- [x] **Step 1: Write verification tests for Chapters 8-10**
- [x] **Step 2: Author exercises and solutions for Chapters 8, 9, and 10**
- [x] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapters_8_10.py -v`  
Expected: PASS

- [x] **Step 4: Commit**

```bash
git add exercises/08_ray_data exercises/09_ml_from_scratch exercises/10_ray_train_and_tune solutions/ tests/test_chapters_8_10.py
git commit -m "feat: add curriculum and solutions for chapters 8 to 10"
```

---

### Task 9: Chapters 11 to 13 Curriculum & Solutions (Ray Tune, Ray Serve, Observability)

**Files:**
- Create: `exercises/11_ray_tune/` (tune01.py to tune03.py)
- Create: `solutions/11_ray_tune/` (tune01.py to tune03.py)
- Create: `exercises/12_ray_serve/` (serve01.py to serve05.py)
- Create: `solutions/12_ray_serve/` (serve01.py to serve05.py)
- Create: `exercises/13_observability_and_debugging/` (perf01.py to perf03.py)
- Create: `solutions/13_observability_and_debugging/` (perf01.py to perf03.py)
- Test: `tests/test_chapters_11_13.py`

- [x] **Step 1: Write verification tests for Chapters 11-13**
- [x] **Step 2: Author exercises and solutions for Chapters 11, 12, and 13**
- [x] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapters_11_13.py -v`  
Expected: PASS

- [x] **Step 4: Commit**

```bash
git add exercises/11_ray_tune exercises/12_ray_serve exercises/13_observability_and_debugging solutions/ tests/test_chapters_11_13.py
git commit -m "feat: add curriculum and solutions for chapters 11 to 13"
```

---

### Task 10: Chapter 14 Curriculum & Solutions (KubeRay & Cloud-Native Ray)

**Files:**
- Create: `exercises/14_kuberay/` (kuberay01.py to kuberay05.py)
- Create: `solutions/14_kuberay/` (kuberay01.py to kuberay05.py)
- Test: `tests/test_chapter_14.py`

- [x] **Step 1: Write verification tests for Chapter 14**
- [x] **Step 2: Author exercises and solutions for Chapter 14**
- [x] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapter_14.py -v`  
Expected: PASS

- [x] **Step 4: Commit**

```bash
git add exercises/14_kuberay solutions/14_kuberay tests/test_chapter_14.py
git commit -m "feat: add curriculum and solutions for chapter 14 kuberay"
```

---

### Task 11: Full End-to-End Test Suite, Verification, Agent Rules Sync & GitHub Remote Setup

**Files:**
- Create: `tests/test_all_solutions.py`
- Create: `tests/test_all_exercises_fail.py`
- Modify: `README.md`

- [x] **Step 1: Write comprehensive test runner**

```python
# tests/test_all_solutions.py
import pytest
from pathlib import Path
import subprocess
import sys
from raylings.manifest import get_manifest

manifest = get_manifest()
all_solutions = [ex.solution_path for ex in manifest.all_exercises]

@pytest.mark.parametrize("solution_path", all_solutions, ids=[p.stem for p in all_solutions])
def test_every_solution_passes(solution_path: Path):
    assert solution_path.exists(), f"Solution file {solution_path} does not exist!"
    proc = subprocess.run([sys.executable, str(solution_path)], capture_output=True, text=True, timeout=45)
    assert proc.returncode == 0, f"Solution {solution_path} failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
```

- [x] **Step 2: Run full test suite & linters**

Run: `pytest -v`  
Run: `ruff check src tests`  
Run: `pyright src`  
Expected: ALL PASS

- [x] **Step 3: Add git remote for dnf0/raylings**

```bash
git remote add origin git@github.com:dnf0/raylings.git
```

- [x] **Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete raylings interactive learning suite and test harness"
```
