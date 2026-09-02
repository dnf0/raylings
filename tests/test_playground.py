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
    out_file = tmp_path / "playground_catalog.json"
    result_path = export_playground_bundle(out_file)

    assert result_path.exists()
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 81
    assert data[0]["chapter_title"]


def test_wasm_simulation_engine():
    """Verify the pure-Python Ray simulation engine executes tasks, actors, and objects correctly."""
    html_file = Path("docs/assets/playground.html")
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")
    
    start_tag = "const WASM_COMPAT_SOURCE = `"
    assert start_tag in content
    start_idx = content.find(start_tag) + len(start_tag)
    end_idx = content.find("`;", start_idx)
    assert end_idx != -1
    
    wasm_source = content[start_idx:end_idx]
    
    # Execute the simulation in an isolated environment
    env: dict = {}
    exec(wasm_source, env)
    
    ray = env["ray"]
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
    
    # Test cluster stats
    stats = ray._get_cluster_stats()
    assert stats["nodes"] >= 1
    assert stats["cpus"] == 4
    assert stats["objects_count"] >= 1
    
    ray.shutdown()
    assert ray.is_initialized() is False


def test_playground_docs_and_assets_exist():
    """Verify docs/playground.md and docs/assets/playground.html exist and contain valid markup."""
    docs_md = Path("docs/playground.md")
    assert docs_md.exists(), "docs/playground.md must exist"
    content_md = docs_md.read_text(encoding="utf-8")
    assert "Playground" in content_md

    html_file = Path("docs/assets/playground.html")
    assert html_file.exists(), "docs/assets/playground.html must exist"
    content_html = html_file.read_text(encoding="utf-8")
    assert "pyodide" in content_html.lower()
    assert "monaco" in content_html.lower()

    # Verify zero-backend persistence engine (RaylingsStorage)
    assert "class RaylingsStorage" in content_html
    assert "raylings_playground_v1" in content_html
    assert "exportBackup" in content_html
    assert "importBackup" in content_html
    assert "resetExercise" in content_html
    assert "resetAll" in content_html

    # Verify Split-Pane UI and Cluster Inspector elements
    assert "course-progress-bar" in content_html
    assert "exercise-tree" in content_html
    assert "tab-cluster" in content_html
    assert "stat-objects" in content_html
    assert "btn-fullscreen" in content_html
