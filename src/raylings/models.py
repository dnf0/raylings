"""Data models for Raylings exercises, chapters, and curriculum manifest."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ExerciseStatus(str, Enum):
    """Represents the progress status of an exercise in the learning lifecycle."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Exercise:
    """Represents an individual exercise unit in the Raylings curriculum."""

    name: str
    title: str
    path: str
    chapter_name: str
    hints: list[str] = field(default_factory=list)
    requires_cluster: bool = False

    @property
    def file_path(self) -> Path:
        """Return the filesystem Path to the exercise source file."""
        return Path(self.path)

    @property
    def solution_path(self) -> Path:
        """Return the filesystem Path to the reference solution file."""
        return Path(self.path.replace("exercises/", "solutions/", 1))


@dataclass
class Chapter:
    """Represents a thematic curriculum chapter containing a collection of exercises."""

    number: int
    name: str
    title: str
    description: str
    exercises: list[Exercise] = field(default_factory=list)


@dataclass
class Manifest:
    """The master curriculum manifest containing all chapters and exercises."""

    chapters: list[Chapter] = field(default_factory=list)

    @property
    def all_exercises(self) -> list[Exercise]:
        """Return a flattened list of all exercises across all chapters in curriculum order."""
        res: list[Exercise] = []
        for ch in self.chapters:
            res.extend(ch.exercises)
        return res
