"""Unit tests for the Raylings onboarding TourEngine and TourStep models."""

import json
from io import StringIO

from rich.console import Console

from raylings.tour import TourEngine, TourStep, get_tour_engine


def test_tour_steps_structure():
    """Verify that TourEngine contains 5 curated steps with correct metadata."""
    engine = TourEngine()
    steps = engine.get_steps()
    assert len(steps) == 5

    for i, step in enumerate(steps, start=1):
        assert isinstance(step, TourStep)
        assert step.step_number == i
        assert step.title.strip() != ""
        assert step.summary.strip() != ""
        assert step.content.strip() != ""

    assert "Welcome" in steps[0].title
    assert (
        "Environment" in steps[1].title
        or "Preflight" in steps[1].title
        or "doctor" in steps[1].title.lower()
    )
    assert "First Exercise" in steps[2].title or "basics01" in steps[2].title
    assert "Watcher" in steps[3].title or "Navigation" in steps[3].title
    assert "VS Code" in steps[4].title or "IDE" in steps[4].title


def test_tour_step_dataclass_defaults():
    """Verify TourStep instantiation and optional fields default to None."""
    step = TourStep(
        step_number=1,
        title="Sample Step",
        summary="A quick summary",
        content="Detailed content here.",
    )
    assert step.step_number == 1
    assert step.title == "Sample Step"
    assert step.summary == "A quick summary"
    assert step.content == "Detailed content here."
    assert step.command_hint is None
    assert step.action_label is None


def test_tour_json_export():
    """Verify that to_json_dict returns a valid JSON-serializable dictionary with expected keys."""
    engine = TourEngine()
    payload = engine.to_json_dict()

    assert "title" in payload
    assert payload["total_steps"] == 5
    assert "steps" in payload
    assert len(payload["steps"]) == 5

    for i, step_dict in enumerate(payload["steps"], start=1):
        assert step_dict["step_number"] == i
        assert "title" in step_dict
        assert "summary" in step_dict
        assert "content" in step_dict
        assert "command_hint" in step_dict
        assert "action_label" in step_dict

    # Ensure it's valid JSON
    json_str = json.dumps(payload)
    assert json_str.startswith("{")


def test_tour_get_step():
    """Verify get_step retrieves specific steps and returns None for invalid step numbers."""
    engine = TourEngine()

    # Valid step retrieval
    step1 = engine.get_step(1)
    assert step1 is not None
    assert step1.step_number == 1

    step3 = engine.get_step(3)
    assert step3 is not None
    assert step3.step_number == 3
    assert "First Exercise" in step3.title or "basics01" in step3.title

    step5 = engine.get_step(5)
    assert step5 is not None
    assert step5.step_number == 5

    # Invalid step numbers
    assert engine.get_step(0) is None
    assert engine.get_step(6) is None
    assert engine.get_step(-1) is None
    assert engine.get_step(99) is None


def test_get_tour_engine_helper():
    """Verify get_tour_engine helper function returns a functioning TourEngine instance."""
    engine = get_tour_engine()
    assert isinstance(engine, TourEngine)
    assert len(engine.get_steps()) == 5


def test_render_step_rich_output():
    """Verify render_step outputs Rich formatted panel containing step information without errors."""
    engine = TourEngine()
    buffer = StringIO()
    test_console = Console(file=buffer, force_terminal=True, width=100)

    for step in engine.get_steps():
        engine.render_step(step, console=test_console)

    output = buffer.getvalue()
    assert "Step 1/5" in output or "Step 1 of 5" in output or "Step 1" in output
    assert "Step 5/5" in output or "Step 5 of 5" in output or "Step 5" in output
    assert "basics01" in output or "raylings" in output


def test_render_step_optional_hints_and_actions():
    """Verify render_step handles steps with or without command_hint and action_label."""
    engine = TourEngine()
    buffer = StringIO()
    test_console = Console(file=buffer, force_terminal=True, width=100)

    step_without_hints = TourStep(
        step_number=1,
        title="Plain Step",
        summary="Summary text",
        content="Content text",
        command_hint=None,
        action_label=None,
    )
    engine.render_step(step_without_hints, console=test_console)
    output = buffer.getvalue()
    assert "Plain Step" in output
    assert "Summary text" in output
    assert "Content text" in output
