"""Unit tests for the Exercise Scaffolding Engine (scaffolder.py and raylings new command)."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raylings.cli import app
from raylings.scaffolder import ExerciseScaffolder, ScaffoldResult

cli_runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temporary repository structure with sample chapter directories."""
    exercises_dir = tmp_path / "exercises"
    solutions_dir = tmp_path / "solutions"

    # Create dummy chapters
    (exercises_dir / "01_basics").mkdir(parents=True)
    (solutions_dir / "01_basics").mkdir(parents=True)
    (exercises_dir / "15_vllm_and_llms").mkdir(parents=True)
    (solutions_dir / "15_vllm_and_llms").mkdir(parents=True)

    # Add an existing exercise to test duplicate detection
    existing_ex = exercises_dir / "01_basics" / "basics01.py"
    existing_ex.write_text("# Existing exercise\n")
    existing_sol = solutions_dir / "01_basics" / "basics01.py"
    existing_sol.write_text("# Existing solution\n")

    return tmp_path


def test_resolve_chapter_dir_by_number(temp_repo: Path) -> None:
    """Verify chapter directory resolution supports numbers ('1', '01', '15') and full names."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)

    # Resolve by single-digit integer string "1"
    resolved_1 = scaffolder.resolve_chapter_dir("1")
    assert resolved_1.name == "01_basics"

    # Resolve by zero-padded integer string "01"
    resolved_01 = scaffolder.resolve_chapter_dir("01")
    assert resolved_01.name == "01_basics"

    # Resolve by two-digit integer string "15"
    resolved_15 = scaffolder.resolve_chapter_dir("15")
    assert resolved_15.name == "15_vllm_and_llms"

    # Resolve by exact directory name
    resolved_full = scaffolder.resolve_chapter_dir("01_basics")
    assert resolved_full.name == "01_basics"


def test_resolve_chapter_dir_nonexistent(temp_repo: Path) -> None:
    """Verify resolving a nonexistent chapter number or name raises ValueError."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)

    with pytest.raises(ValueError, match="Could not find chapter matching '99'"):
        scaffolder.resolve_chapter_dir("99")

    with pytest.raises(ValueError, match="Could not find chapter matching 'nonexistent_chap'"):
        scaffolder.resolve_chapter_dir("nonexistent_chap")


def test_scaffold_invalid_exercise_name(temp_repo: Path) -> None:
    """Verify invalid or empty exercise names raise ValueError."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)

    with pytest.raises(ValueError, match="Invalid exercise name"):
        scaffolder.scaffold(chapter="01", name="")

    with pytest.raises(ValueError, match="Invalid exercise name"):
        scaffolder.scaffold(chapter="01", name="invalid name with spaces")

    with pytest.raises(ValueError, match="Invalid exercise name"):
        scaffolder.scaffold(chapter="01", name="invalid-dash")

    with pytest.raises(ValueError, match="Invalid exercise name"):
        scaffolder.scaffold(chapter="01", name="123invalid_leading_digit_identifier?")


def test_scaffold_normalizes_py_extension(temp_repo: Path) -> None:
    """Verify .py extension is stripped when providing exercise name."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)
    result = scaffolder.scaffold(
        chapter="01",
        name="basics02.py",
        dry_run=True,
    )
    assert result.exercise_name == "basics02"
    assert result.exercise_path.name == "basics02.py"


def test_scaffold_duplicate_exercise_name(temp_repo: Path) -> None:
    """Verify duplicate exercise name raises FileExistsError."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)

    with pytest.raises(FileExistsError, match="already exists"):
        scaffolder.scaffold(chapter="01", name="basics01", dry_run=False)


def test_scaffold_dry_run_no_disk_writes(temp_repo: Path) -> None:
    """Verify dry-run mode returns ScaffoldResult without creating files on disk."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)
    result = scaffolder.scaffold(
        chapter="01",
        name="dry_exercise",
        title="Dry Run Test",
        description="Testing dry run behavior",
        hints=["Hint 1", "Hint 2"],
        dry_run=True,
    )

    assert isinstance(result, ScaffoldResult)
    assert result.exercise_name == "dry_exercise"
    assert result.chapter_name == "01_basics"
    assert result.title == "Dry Run Test"
    assert result.description == "Testing dry run behavior"
    assert len(result.created_files) == 0

    # Ensure files were not written
    assert not result.exercise_path.exists()
    assert not result.solution_path.exists()

    # Verify manifest snippet
    assert 'name="dry_exercise"' in result.manifest_snippet
    assert 'title="Dry Run Test"' in result.manifest_snippet
    assert 'chapter_name="01_basics"' in result.manifest_snippet
    assert '"Hint 1"' in result.manifest_snippet


def test_scaffold_actual_disk_writes_and_template_formatting(temp_repo: Path) -> None:
    """Verify actual scaffolding creates formatted exercise and solution templates."""
    scaffolder = ExerciseScaffolder(repo_root=temp_repo)
    result = scaffolder.scaffold(
        chapter="15",
        name="vllm02",
        title="KV Cache Paged Attention",
        description="Implement block table allocation for KV caches.",
        hints=["Allocate physical blocks before attention.", "Use ray.get() on worker refs."],
        dry_run=False,
    )

    assert result.exercise_path.exists()
    assert result.solution_path.exists()
    assert len(result.created_files) == 2
    assert result.exercise_path in result.created_files
    assert result.solution_path in result.created_files

    # Check Exercise Content
    ex_content = result.exercise_path.read_text()
    assert 'os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"' in ex_content
    assert "KV Cache Paged Attention" in ex_content
    assert "Implement block table allocation for KV caches." in ex_content
    assert "def verify() -> None:" in ex_content
    assert 'if __name__ == "__main__":' in ex_content
    assert "verify()" in ex_content
    assert "# TODO" in ex_content

    # Check Solution Content
    sol_content = result.solution_path.read_text()
    assert 'os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"' in sol_content
    assert "Reference Solution for vllm02" in sol_content
    assert "def verify() -> None:" in sol_content
    assert 'if __name__ == "__main__":' in sol_content
    assert "verify()" in sol_content


def test_cli_new_command_dry_run() -> None:
    """Verify CLI 'raylings new' in dry-run mode."""
    res = cli_runner.invoke(app, ["new", "01", "cli_test_task", "--dry-run"])
    assert res.exit_code == 0
    assert "DRY RUN" in res.stdout
    assert "01_basics" in res.stdout
    assert "cli_test_task.py" in res.stdout
    assert "Exercise(" in res.stdout


def test_cli_new_command_json_output() -> None:
    """Verify CLI 'raylings new --json' outputs valid JSON schema."""
    res = cli_runner.invoke(app, ["new", "01", "json_test_task", "--dry-run", "--json"])
    assert res.exit_code == 0
    payload = json.loads(res.stdout)
    assert payload["exercise_name"] == "json_test_task"
    assert payload["chapter_name"] == "01_basics"
    assert "exercise_path" in payload
    assert "solution_path" in payload
    assert payload["dry_run"] is True
    assert "manifest_snippet" in payload
    assert payload["created_files"] == []


def test_cli_new_command_invalid_chapter() -> None:
    """Verify CLI 'raylings new' fails gracefully with invalid chapter."""
    res = cli_runner.invoke(app, ["new", "999", "fail_task"])
    assert res.exit_code != 0
    assert "Could not find chapter" in res.stdout or "Error" in res.stdout


def test_cli_new_exercise_alias() -> None:
    """Verify CLI 'raylings new-exercise' alias functions identically."""
    res = cli_runner.invoke(
        app,
        [
            "new-exercise",
            "01",
            "alias_task",
            "--dry-run",
            "-t",
            "Alias Task",
            "-d",
            "Testing alias.",
        ],
    )
    assert res.exit_code == 0
    assert "DRY RUN" in res.stdout
    assert "alias_task" in res.stdout


def test_cli_new_command_json_error() -> None:
    """Verify CLI 'raylings new --json' outputs structured error JSON on failure."""
    res = cli_runner.invoke(app, ["new", "999", "fail_json_task", "--json"])
    assert res.exit_code != 0
    payload = json.loads(res.stdout)
    assert payload["success"] is False
    assert "error" in payload


def test_scaffolder_detect_repo_root() -> None:
    """Verify scaffolder detects repository root directory."""
    scaffolder = ExerciseScaffolder()
    assert scaffolder.repo_root.is_dir()
    assert (scaffolder.repo_root / "exercises").is_dir()
