try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from pathlib import Path


def test_package_import():
    import raylings

    assert hasattr(raylings, "__version__")
    assert isinstance(raylings.__version__, str)
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        data = tomllib.loads(pyproject_path.read_text())
        assert raylings.__version__ == data["project"]["version"]


def test_pyproject_structure():
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists()
    data = tomllib.loads(pyproject_path.read_text())
    assert data["project"]["name"] == "raylings"
    deps = data["project"]["dependencies"]
    assert any("ray" in d for d in deps)
    assert "raylings" in data["project"]["scripts"]


def test_gitignore_ignores_agent_state():
    gitignore_path = Path(".gitignore")
    assert gitignore_path.exists()
    content = gitignore_path.read_text()
    assert ".agents/" in content
    assert ".superpowers/" in content
    assert ".venv/" in content
    assert ".env" in content


def test_all_curriculum_syntax_and_markers():
    """Statically verify every exercise and solution without subprocess overhead."""
    import ast

    from raylings.manifest import get_manifest
    from raylings.runner import NOT_DONE_MARKER

    manifest = get_manifest()
    assert len(manifest.all_exercises) == 81

    for ex in manifest.all_exercises:
        # Check skeleton (clean Python, valid syntax)
        assert ex.file_path.exists(), f"Missing exercise skeleton: {ex.file_path}"
        code_skel = ex.file_path.read_text(encoding="utf-8")
        assert NOT_DONE_MARKER not in code_skel, (
            f"Exercise {ex.name} unexpectedly contains legacy '{NOT_DONE_MARKER}'"
        )
        ast.parse(code_skel, filename=str(ex.file_path))

        # Check solution (clean Python, valid syntax, NO marker)
        assert ex.solution_path.exists(), f"Missing solution: {ex.solution_path}"
        code_sol = ex.solution_path.read_text(encoding="utf-8")
        assert NOT_DONE_MARKER not in code_sol, (
            f"Solution {ex.name} unexpectedly contains '{NOT_DONE_MARKER}'"
        )
        ast.parse(code_sol, filename=str(ex.solution_path))
