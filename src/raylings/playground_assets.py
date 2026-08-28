"""Asset generation and catalog bundling for the interactive WASM / Pyodide Playground."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raylings.manifest import get_manifest


def generate_playground_catalog() -> list[dict[str, Any]]:
    """Extract exercises and reference solutions for the web playground.

    Returns:
        list[dict[str, Any]]: Array of exercise payloads with metadata, code, hints, and solutions.
    """
    manifest = get_manifest()
    catalog: list[dict[str, Any]] = []

    for chapter in manifest.chapters:
        for ex in chapter.exercises:
            code_str = ""
            if ex.file_path.exists():
                code_str = ex.file_path.read_text(encoding="utf-8")

            sol_str = ""
            if ex.solution_path.exists():
                sol_str = ex.solution_path.read_text(encoding="utf-8")

            # Extract docstring description from exercise code
            prompt = ex.title
            if code_str.strip().startswith('"""'):
                end_idx = code_str.find('"""', 3)
                if end_idx != -1:
                    prompt = code_str[3:end_idx].strip()

            hint_str = (
                " ".join(ex.hints)
                if ex.hints
                else "Read the docstrings carefully and implement the missing logic."
            )

            catalog.append(
                {
                    "chapter": chapter.number,
                    "chapter_name": chapter.title,
                    "name": ex.name,
                    "title": ex.title,
                    "path": ex.path,
                    "prompt": prompt,
                    "hint": hint_str,
                    "code": code_str,
                    "solution": sol_str,
                }
            )

    return catalog


def export_playground_bundle(output_path: Path | str) -> Path:
    """Export the playground exercise catalog as JSON to the specified path.

    Args:
        output_path: Destination path for the exported JSON catalog.

    Returns:
        Path: Path to written catalog file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    catalog = generate_playground_catalog()
    path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return path
