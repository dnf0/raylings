from pathlib import Path

from raylings.manifest import (
    build_manifest,
    get_exercise_by_name,
    get_manifest,
    get_next_exercise,
    get_previous_exercise,
)
from raylings.models import Chapter, Exercise, ExerciseStatus, Manifest


def test_manifest_loads_all_chapters():
    manifest = get_manifest()
    assert isinstance(manifest, Manifest)
    assert len(manifest.chapters) == 14
    assert all(isinstance(ch, Chapter) for ch in manifest.chapters)
    assert len(manifest.all_exercises) >= 55
    first = manifest.all_exercises[0]
    assert first.name == "basics01"
    assert first.chapter_name == "01_basics"


def test_unique_exercise_names_and_sequential_chapters():
    manifest = get_manifest()
    # Ensure sequential chapter numbering 1..14
    chapter_numbers = [ch.number for ch in manifest.chapters]
    assert chapter_numbers == list(range(1, 15))

    # Ensure all exercise names are unique
    exercise_names = [ex.name for ex in manifest.all_exercises]
    assert len(exercise_names) == len(set(exercise_names))

    # Ensure all exercise paths are unique
    exercise_paths = [ex.path for ex in manifest.all_exercises]
    assert len(exercise_paths) == len(set(exercise_paths))


def test_get_exercise_by_name():
    # By short name
    ex = get_exercise_by_name("basics01")
    assert ex is not None
    assert ex.name == "basics01"
    assert ex.path.endswith("basics01.py")

    # By filename
    ex_by_filename = get_exercise_by_name("basics01.py")
    assert ex_by_filename is not None
    assert ex_by_filename.name == "basics01"

    # By relative path
    ex_by_path = get_exercise_by_name("exercises/01_basics/basics01.py")
    assert ex_by_path is not None
    assert ex_by_path.name == "basics01"

    # By path suffix
    ex_by_suffix = get_exercise_by_name("01_basics/basics01.py")
    assert ex_by_suffix is not None
    assert ex_by_suffix.name == "basics01"

    # Chapter 14 exercise lookup
    kuberay_ex = get_exercise_by_name("kuberay01")
    assert kuberay_ex is not None
    assert kuberay_ex.chapter_name == "14_kuberay"

    # Non-existent exercise
    assert get_exercise_by_name("non_existent_exercise") is None


def test_get_next_exercise():
    next_ex = get_next_exercise("basics01")
    assert next_ex is not None
    assert next_ex.name == "basics02"

    # By path
    next_ex_by_path = get_next_exercise("exercises/01_basics/basics01.py")
    assert next_ex_by_path is not None
    assert next_ex_by_path.name == "basics02"

    # Last exercise has no next exercise
    manifest = get_manifest()
    last_ex = manifest.all_exercises[-1]
    assert get_next_exercise(last_ex.name) is None

    # Unknown exercise returns None
    assert get_next_exercise("unknown_exercise") is None


def test_get_previous_exercise():
    prev_ex = get_previous_exercise("basics02")
    assert prev_ex is not None
    assert prev_ex.name == "basics01"

    # By path
    prev_ex_by_path = get_previous_exercise("exercises/01_basics/basics02.py")
    assert prev_ex_by_path is not None
    assert prev_ex_by_path.name == "basics01"

    # First exercise has no previous exercise
    assert get_previous_exercise("basics01") is None

    # Unknown exercise returns None
    assert get_previous_exercise("unknown_exercise") is None


def test_exercise_solution_path():
    ex = Exercise(
        name="basics01",
        title="Ray Init & First Remote Task",
        path="exercises/01_basics/basics01.py",
        chapter_name="01_basics",
    )
    assert ex.file_path == Path("exercises/01_basics/basics01.py")
    assert ex.solution_path == Path("solutions/01_basics/basics01.py")


def test_exercise_status_enum():
    assert ExerciseStatus.NOT_STARTED == "not_started"
    assert ExerciseStatus.IN_PROGRESS == "in_progress"
    assert ExerciseStatus.COMPLETED == "completed"
    assert ExerciseStatus.FAILED == "failed"


def test_all_exercise_paths_valid_format():
    manifest = get_manifest()
    for ex in manifest.all_exercises:
        assert ex.path.startswith("exercises/")
        assert ex.path.endswith(".py")
        assert ex.solution_path == Path(ex.path.replace("exercises/", "solutions/", 1))
        assert len(ex.hints) >= 1, f"Exercise {ex.name} should have at least 1 hint"
        assert ex.chapter_name in ex.path


def test_build_manifest_creates_fresh_copy():
    manifest1 = build_manifest()
    manifest2 = build_manifest()
    assert manifest1 is not manifest2
    assert len(manifest1.chapters) == len(manifest2.chapters)
