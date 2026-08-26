try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

from pathlib import Path


def test_package_import():
    import raylings

    assert hasattr(raylings, "__version__")
    assert raylings.__version__ == "0.1.0"


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
