"""Exercise Scaffolding Engine for generating new Raylings curriculum exercises."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScaffoldResult:
    """Encapsulates the result of scaffolding a new exercise."""

    exercise_path: Path
    solution_path: Path
    chapter_name: str
    exercise_name: str
    title: str
    description: str
    manifest_snippet: str
    created_files: list[Path] = field(default_factory=list)

    def to_dict(self, dry_run: bool = False) -> dict[str, Any]:
        """Convert result to JSON-serializable dictionary."""
        return {
            "exercise_path": str(self.exercise_path),
            "solution_path": str(self.solution_path),
            "chapter_name": self.chapter_name,
            "exercise_name": self.exercise_name,
            "title": self.title,
            "description": self.description,
            "manifest_snippet": self.manifest_snippet,
            "created_files": [str(f) for f in self.created_files],
            "dry_run": dry_run,
        }


class ExerciseScaffolder:
    """Engine for resolving chapter paths, generating boilerplate, and scaffolding exercises."""

    def __init__(self, repo_root: Path | None = None) -> None:
        if repo_root is not None:
            self.repo_root = Path(repo_root).resolve()
        else:
            self.repo_root = self._detect_repo_root()

    def _detect_repo_root(self) -> Path:
        """Detect repository root directory by looking for exercises directory or pyproject.toml."""
        cwd = Path.cwd().resolve()
        for candidate in [cwd, *cwd.parents]:
            if (candidate / "exercises").is_dir() and (candidate / "src" / "raylings").is_dir():
                return candidate
        return cwd

    def resolve_chapter_dir(self, chapter_query: str, repo_root: Path | None = None) -> Path:
        """Resolve chapter directory from query string (e.g. '1', '01', '15', '01_basics').

        Args:
            chapter_query: Chapter number or name query.
            repo_root: Optional repository root path override.

        Returns:
            Path to the resolved chapter directory under exercises/.

        Raises:
            ValueError: If no matching chapter directory can be found.
        """
        root = Path(repo_root).resolve() if repo_root else self.repo_root
        exercises_dir = root / "exercises"

        if not exercises_dir.exists():
            raise ValueError(f"Exercises directory not found at: {exercises_dir}")

        chapter_dirs = sorted([d for d in exercises_dir.iterdir() if d.is_dir()])

        # 1. Exact match on directory name
        for d in chapter_dirs:
            if d.name.lower() == chapter_query.lower():
                return d

        # 2. Match by integer / numeric prefix
        if chapter_query.isdigit():
            target_num = int(chapter_query)
            for d in chapter_dirs:
                prefix = d.name.split("_")[0]
                if prefix.isdigit() and int(prefix) == target_num:
                    return d

        # 3. Match by name substring or prefix
        clean_query = chapter_query.lower().strip()
        matches = [
            d
            for d in chapter_dirs
            if d.name.lower().startswith(clean_query) or clean_query in d.name.lower()
        ]
        if len(matches) == 1:
            return matches[0]

        available = [d.name for d in chapter_dirs]
        raise ValueError(
            f"Could not find chapter matching '{chapter_query}'. Available chapters: {available}"
        )

    def validate_exercise_name(self, name: str) -> str:
        """Validate and normalize exercise identifier.

        Args:
            name: Raw exercise identifier string.

        Returns:
            Normalized exercise name without .py extension.

        Raises:
            ValueError: If name is empty or not a valid Python identifier.
        """
        normalized = name.strip()
        if normalized.endswith(".py"):
            normalized = normalized[:-3]

        if not normalized or not normalized.isidentifier():
            raise ValueError(
                f"Invalid exercise name '{name}'. Exercise name must be a valid non-empty Python identifier (e.g. 'basics02', 'vllm05')."
            )

        return normalized

    def generate_manifest_snippet(
        self,
        name: str,
        title: str,
        chapter_name: str,
        hints: list[str] | None = None,
    ) -> str:
        """Generate manifest python code snippet for registering the exercise."""
        if not hints:
            hints = [
                "Initialize Ray using ray.init(ignore_reinit_error=True).",
                "Complete the exercise task and ensure assertions pass.",
            ]

        hints_lines = "\n".join(f'        "{h}",' for h in hints)
        return (
            f"Exercise(\n"
            f'    name="{name}",\n'
            f'    title="{title}",\n'
            f'    path="exercises/{chapter_name}/{name}.py",\n'
            f'    chapter_name="{chapter_name}",\n'
            f"    hints=[\n"
            f"{hints_lines}\n"
            f"    ],\n"
            f"),"
        )

    def scaffold(
        self,
        chapter: str,
        name: str,
        title: str | None = None,
        description: str | None = None,
        hints: list[str] | None = None,
        dry_run: bool = False,
        repo_root: Path | None = None,
    ) -> ScaffoldResult:
        """Scaffold a new exercise and reference solution template.

        Args:
            chapter: Chapter number or name.
            name: Exercise identifier.
            title: Optional human-readable exercise title.
            description: Optional summary description.
            hints: Optional list of guidance hints.
            dry_run: When True, previews generation without writing to disk.
            repo_root: Optional repository root path override.

        Returns:
            ScaffoldResult containing paths, metadata, and manifest snippet.

        Raises:
            ValueError: If chapter or exercise name is invalid.
            FileExistsError: If target exercise or solution file already exists.
        """
        root = Path(repo_root).resolve() if repo_root else self.repo_root
        chapter_dir = self.resolve_chapter_dir(chapter, repo_root=root)
        chapter_name = chapter_dir.name
        exercise_name = self.validate_exercise_name(name)

        # Derive human-friendly title and description if not provided
        if not title:
            # e.g., 'vllm05' -> 'Vllm05', 'paged_attention' -> 'Paged Attention'
            words = exercise_name.replace("_", " ").split()
            title = " ".join(w.capitalize() for w in words)

        if not description:
            description = f"Hands-on exercise implementing {title}."

        # Derive chapter human title
        chapter_title = (
            chapter_name.split("_", 1)[1].replace("_", " ").title()
            if "_" in chapter_name
            else chapter_name
        )
        chapter_num_str = chapter_name.split("_")[0]
        chapter_num = int(chapter_num_str) if chapter_num_str.isdigit() else 1

        exercise_path = root / "exercises" / chapter_name / f"{exercise_name}.py"
        solution_path = root / "solutions" / chapter_name / f"{exercise_name}.py"

        if exercise_path.exists() or solution_path.exists():
            existing = exercise_path if exercise_path.exists() else solution_path
            raise FileExistsError(
                f"Exercise or solution file already exists at '{existing}'. Cannot overwrite."
            )

        manifest_snippet = self.generate_manifest_snippet(
            name=exercise_name,
            title=title,
            chapter_name=chapter_name,
            hints=hints,
        )

        exercise_content = (
            f'"""Chapter {chapter_num}: {chapter_title} - Exercise: {title}.\n\n'
            f"{description}\n\n"
            f"Key Concepts:\n"
            f"- Concept 1: Distributed Ray execution primitives.\n"
            f"- Concept 2: Object lifecycle and task scheduling.\n\n"
            f"Your Task:\n"
            f"- Implement the required Ray tasks/actors.\n"
            f"- Ensure verify() completes without assertion failures.\n"
            f'"""\n\n'
            f"import os\n\n"
            f'os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"\n'
            f"import ray\n\n\n"
            f"# TODO: Implement your remote task or actor here\n"
            f"def example_task() -> int:\n"
            f"    # TODO: Add logic\n"
            f"    pass\n\n\n"
            f"def verify() -> None:\n"
            f"    ray.init(ignore_reinit_error=True)\n\n"
            f"    # TODO: Invoke task and verify results\n"
            f"    # result = ray.get(...)\n"
            f"    # assert result is not None\n\n"
            f'    print("✓ {exercise_name} verified successfully!")\n'
            f"    ray.shutdown()\n\n\n"
            f'if __name__ == "__main__":\n'
            f"    verify()\n"
        )

        solution_content = (
            f'"""Chapter {chapter_num}: {chapter_title} - Reference Solution for {exercise_name}.\n\n'
            f"{description}\n"
            f'"""\n\n'
            f"import os\n\n"
            f'os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"\n'
            f"import ray\n\n\n"
            f"def example_task() -> int:\n"
            f"    return 42\n\n\n"
            f"def verify() -> None:\n"
            f"    ray.init(ignore_reinit_error=True)\n\n"
            f"    result = example_task()\n"
            f'    assert result == 42, f"Expected 42, got {{result}}"\n\n'
            f'    print("✓ {exercise_name} solution verified successfully!")\n'
            f"    ray.shutdown()\n\n\n"
            f'if __name__ == "__main__":\n'
            f"    verify()\n"
        )

        created_files: list[Path] = []
        if not dry_run:
            exercise_path.parent.mkdir(parents=True, exist_ok=True)
            solution_path.parent.mkdir(parents=True, exist_ok=True)
            exercise_path.write_text(exercise_content, encoding="utf-8")
            solution_path.write_text(solution_content, encoding="utf-8")
            created_files = [exercise_path, solution_path]

        return ScaffoldResult(
            exercise_path=exercise_path,
            solution_path=solution_path,
            chapter_name=chapter_name,
            exercise_name=exercise_name,
            title=title,
            description=description,
            manifest_snippet=manifest_snippet,
            created_files=created_files,
        )
