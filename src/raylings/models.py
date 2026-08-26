from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ExerciseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Exercise:
    name: str
    title: str
    path: str
    chapter_name: str
    hints: list[str] = field(default_factory=list)
    requires_cluster: bool = False

    @property
    def file_path(self) -> Path:
        return Path(self.path)

    @property
    def solution_path(self) -> Path:
        return Path(self.path.replace("exercises/", "solutions/"))


@dataclass
class Chapter:
    number: int
    name: str
    title: str
    description: str
    exercises: list[Exercise] = field(default_factory=list)


@dataclass
class Manifest:
    chapters: list[Chapter] = field(default_factory=list)

    @property
    def all_exercises(self) -> list[Exercise]:
        res: list[Exercise] = []
        for ch in self.chapters:
            res.extend(ch.exercises)
        return res
