"""Unit tests for the WASM Playground asset generator and web interfaces."""

import json
from pathlib import Path

from raylings.playground_assets import (
    export_playground_bundle,
    generate_playground_catalog,
)


def test_generate_playground_catalog():
    """Verify playground catalog extracts exercises and solutions cleanly."""
    catalog = generate_playground_catalog()
    assert isinstance(catalog, list)
    assert len(catalog) > 0

    first_ex = catalog[0]
    assert "chapter" in first_ex
    assert "chapter_name" in first_ex
    assert "name" in first_ex
    assert "prompt" in first_ex
    assert "code" in first_ex
    assert "solution" in first_ex
    assert "hint" in first_ex

    # Ensure basics01 is present
    basics01 = next(ex for ex in catalog if ex["name"] == "basics01")
    assert "ray.init" in basics01["code"] or "@ray.remote" in basics01["code"]
    assert "verify" in basics01["code"]


def test_export_playground_bundle(tmp_path: Path):
    """Verify bundle export writes valid JSON/JS to disk."""
    out_file = tmp_path / "playground_catalog.json"
    result_path = export_playground_bundle(out_file)

    assert result_path.exists()
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 20


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
