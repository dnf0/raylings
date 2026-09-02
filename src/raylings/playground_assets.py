"""Asset generation and catalog bundling for the interactive WASM / Pyodide Playground."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raylings import __version__
from raylings.manifest import get_manifest

BUNDLE_PATH = Path("docs/assets/playground/playground-bundle.json")


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
                "\n".join(f"• {h}" for h in ex.hints)
                if ex.hints
                else "Read the docstrings carefully and implement the missing logic."
            )

            catalog.append(
                {
                    "chapter": chapter.number,
                    "chapter_name": chapter.name,
                    "chapter_title": chapter.title,
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


def generate_playground_bundle(repo_root: Path | None = None) -> dict[str, Any]:
    """Generate structured playground bundle matching Kubelings architecture.

    Returns:
        dict[str, Any]: Bundle with chapters, exercises map, wasm_compat_code, and metadata.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    wasm_compat_path = repo_root / "src" / "raylings" / "wasm_compat.py"
    wasm_compat_code = ""
    if wasm_compat_path.exists():
        wasm_compat_code = wasm_compat_path.read_text(encoding="utf-8")

    manifest = get_manifest()
    chapters_data: list[dict[str, Any]] = []
    exercises_data: dict[str, Any] = {}
    catalog = generate_playground_catalog()

    for chapter in manifest.chapters:
        ch_exercise_ids = [ex.name for ex in chapter.exercises]
        chapters_data.append(
            {
                "number": chapter.number,
                "name": chapter.name,
                "title": chapter.title,
                "description": chapter.description,
                "exercise_ids": ch_exercise_ids,
            }
        )

        for ex in chapter.exercises:
            starter_code = ex.file_path.read_text(encoding="utf-8") if ex.file_path.exists() else ""
            solution_code = (
                ex.solution_path.read_text(encoding="utf-8") if ex.solution_path.exists() else ""
            )

            prompt = ex.title
            if starter_code.strip().startswith('"""'):
                end_idx = starter_code.find('"""', 3)
                if end_idx != -1:
                    prompt = starter_code[3:end_idx].strip()

            exercises_data[ex.name] = {
                "id": ex.name,
                "title": ex.title,
                "chapter": ex.chapter_name,
                "chapter_number": chapter.number,
                "chapter_title": chapter.title,
                "filename": ex.file_path.name,
                "hints": ex.hints,
                "requires_cluster": ex.requires_cluster,
                "starter_code": starter_code,
                "solution_code": solution_code,
                "prompt": prompt,
            }

    return {
        "version": __version__,
        "wasm_compat_code": wasm_compat_code,
        "chapters": chapters_data,
        "exercises": exercises_data,
        "catalog": catalog,
        "total_chapters": len(chapters_data),
        "total_exercises": len(exercises_data),
    }


def export_playground_bundle(output_path: Path | str | None = None) -> Path:
    """Export the playground bundle as JSON to the specified path.

    Args:
        output_path: Destination path for the exported JSON catalog/bundle.

    Returns:
        Path: Path to written bundle file.
    """
    path = Path(output_path) if output_path else BUNDLE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    bundle = generate_playground_bundle()
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    # Also export legacy flat catalog path if needed
    legacy_path = Path("docs/assets/playground_catalog.json")
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(json.dumps(bundle["catalog"], indent=2), encoding="utf-8")
    return path

