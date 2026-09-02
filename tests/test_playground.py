"""Unit tests for the WASM Playground asset generator and web interfaces."""

import json
from pathlib import Path

from raylings.playground_assets import (
    export_playground_bundle,
    generate_playground_catalog,
)


def test_generate_playground_catalog():
    """Verify playground catalog extracts all 81 exercises across 18 chapters."""
    catalog = generate_playground_catalog()
    assert isinstance(catalog, list)
    assert len(catalog) == 81, f"Expected 81 exercises, got {len(catalog)}"

    chapters = {ex["chapter"] for ex in catalog}
    assert len(chapters) == 18, f"Expected 18 chapters, got {len(chapters)}"

    first_ex = catalog[0]
    assert "chapter" in first_ex
    assert "chapter_name" in first_ex
    assert "chapter_title" in first_ex
    assert "name" in first_ex
    assert "prompt" in first_ex
    assert "code" in first_ex
    assert "solution" in first_ex
    assert "hint" in first_ex

    for ex in catalog:
        assert ex["name"], "Exercise name must not be empty"
        assert ex["chapter_name"], "Chapter name must not be empty"
        assert ex["chapter_title"], "Chapter title must not be empty"
        assert ex["code"], f"Starter code missing for {ex['name']}"
        assert ex["solution"], f"Solution code missing for {ex['name']}"
        assert ex["prompt"], f"Prompt missing for {ex['name']}"
        assert ex["hint"], f"Hint missing for {ex['name']}"

    # Ensure basics01 is present
    basics01 = next(ex for ex in catalog if ex["name"] == "basics01")
    assert "ray.init" in basics01["code"] or "@ray.remote" in basics01["code"]
    assert "verify" in basics01["code"]


def test_export_playground_bundle(tmp_path: Path):
    """Verify bundle export writes all 81 exercises to valid JSON on disk."""
    out_file = tmp_path / "playground-bundle.json"
    result_path = export_playground_bundle(out_file)

    assert result_path.exists()
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert "version" in data
    assert "chapters" in data
    assert len(data["chapters"]) == 18
    assert "exercises" in data
    assert len(data["exercises"]) == 81
    assert "wasm_compat_code" in data
    assert "class WasmPlasmaStore" in data["wasm_compat_code"]
    assert "class WasmRayModule" in data["wasm_compat_code"]


def test_bundle_structure_and_exercise_details():
    """Verify detailed structure of bundled exercises."""
    from raylings.playground_assets import generate_playground_bundle

    bundle = generate_playground_bundle()
    assert bundle["total_chapters"] == 18
    assert bundle["total_exercises"] == 81

    # Check basics01
    assert "basics01" in bundle["exercises"]
    ex = bundle["exercises"]["basics01"]
    assert ex["id"] == "basics01"
    assert ex["chapter"] == "01_basics"
    assert ex["chapter_number"] == 1
    assert "ray.init" in ex["starter_code"] or "@ray.remote" in ex["starter_code"]
    assert ex["solution_code"]
    assert len(ex["hints"]) >= 1




def test_wasm_simulation_engine():
    """Verify the pure-Python Ray simulation engine executes tasks, actors, datasets, and telemetry correctly."""
    from raylings.wasm_compat import ray

    assert ray.is_initialized() is False
    ray.init()
    assert ray.is_initialized() is True

    # Test remote task
    @ray.remote
    def square(x: int) -> int:
        return x * x

    ref = square.remote(4)
    result = ray.get(ref)
    assert result == 16

    # Test remote actor
    @ray.remote
    class Counter:
        def __init__(self, init_val: int = 0):
            self.val = init_val

        def inc(self, step: int = 1) -> int:
            self.val += step
            return self.val

        def get_val(self) -> int:
            return self.val

    counter = Counter.remote(10)
    inc_ref = counter.inc.remote(5)
    assert ray.get(inc_ref) == 15
    get_ref = counter.get_val.remote()
    assert ray.get(get_ref) == 15

    # Test ray.data
    ds = ray.data.range(5)
    ds2 = ds.map(lambda row: {"id": row["id"] * 2})
    records = ds2.take_all()
    assert records == [{"id": 0}, {"id": 2}, {"id": 4}, {"id": 6}, {"id": 8}]

    # Test cluster stats contract
    stats = ray._get_cluster_stats()
    assert isinstance(stats, dict)
    expected_keys = {"nodes", "cpus", "gpus", "objects_count", "objects_bytes", "actors_count", "tasks_count"}
    assert expected_keys.issubset(set(stats.keys())), f"Missing keys in cluster stats: {expected_keys - set(stats.keys())}"
    assert stats["nodes"] == 1
    assert stats["cpus"] == 4
    assert stats["objects_count"] >= 1
    assert stats["objects_bytes"] >= 0

    ray.shutdown()
    assert ray.is_initialized() is False


def test_mkdocs_build_and_standalone_shell_artifact():
    """Verify that mkdocs build --strict generates site/playground/index.html with the standalone shell intact."""
    import subprocess

    build_res = subprocess.run(["uv", "run", "mkdocs", "build", "--strict"], capture_output=True, text=True)
    assert build_res.returncode == 0, f"mkdocs build failed: {build_res.stderr}"

    site_shell = Path("site/playground/index.html")
    assert site_shell.exists(), "site/playground/index.html must exist after mkdocs build"
    content = site_shell.read_text(encoding="utf-8")
    assert "standalone-playground-root" in content, "Built site/playground/index.html must contain standalone shell"
    assert "playground.css" in content
    assert "playground.js" in content



def test_bundle_drift_and_synchronization():
    """Verify that the static playground bundle on disk matches generate_playground_bundle() without drift."""
    from raylings.playground_assets import BUNDLE_PATH, generate_playground_bundle

    assert BUNDLE_PATH.exists(), "playground-bundle.json must exist"
    disk_bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    memory_bundle = generate_playground_bundle()

    assert disk_bundle["total_chapters"] == memory_bundle["total_chapters"] == 18
    assert disk_bundle["total_exercises"] == memory_bundle["total_exercises"] == 81
    assert len(disk_bundle["chapters"]) == len(memory_bundle["chapters"]) == 18
    assert set(disk_bundle["exercises"].keys()) == set(memory_bundle["exercises"].keys())


def test_javascript_syntax_validity():
    """Verify JavaScript files have valid syntax using Node if available."""
    import shutil
    import subprocess

    node_bin = shutil.which("node")
    if node_bin:
        res = subprocess.run(
            [node_bin, "--check", "docs/assets/playground/playground.js", "docs/assets/playground/playground-worker.js"],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"Node syntax check failed: {res.stderr}"


def test_standardized_playground_architecture():
    """Verify all standardized standalone playground shell and asset files exist and adhere to contracts."""
    index_html = Path("docs/playground/index.html")
    assert index_html.exists(), "docs/playground/index.html must exist"
    index_content = index_html.read_text(encoding="utf-8")
    assert "raylings-playground" in index_content
    assert "standalone-header" in index_content
    assert "theme-toggle-btn" in index_content
    assert "header-nav-btn" in index_content
    assert "playground.css" in index_content
    assert "playground.js" in index_content

    css_file = Path("docs/assets/playground/playground.css")
    assert css_file.exists(), "docs/assets/playground/playground.css must exist"
    css_content = css_file.read_text(encoding="utf-8")
    assert "--pg-bg" in css_content
    assert ".raylings-playground" in css_content
    assert ".playground-split-layout" in css_content
    assert ".cluster-stat-grid" in css_content

    js_file = Path("docs/assets/playground/playground.js")
    assert js_file.exists(), "docs/assets/playground/playground.js must exist"
    js_content = js_file.read_text(encoding="utf-8")
    assert "RaylingsStorage" in js_content
    assert "raylings_learning_state_v1" in js_content
    assert "raylings_playground_v1" in js_content  # Migration support
    assert "loadMonaco" in js_content
    assert "btn-run-exercise" in js_content
    assert "btn-stop-exercise" in js_content
    assert "btn-toggle-hint" in js_content
    assert "btn-toggle-diff" in js_content
    assert "exportBackup" in js_content
    assert "importBackup" in js_content

    worker_file = Path("docs/assets/playground/playground-worker.js")
    assert worker_file.exists(), "docs/assets/playground/playground-worker.js must exist"
    worker_content = worker_file.read_text(encoding="utf-8")
    assert "initPyodide" in worker_content
    assert "RUN_EXERCISE" in worker_content
    assert "raylings.wasm_compat" in worker_content


