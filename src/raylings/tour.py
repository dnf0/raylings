"""Interactive onboarding tour engine and step definitions for Raylings."""

from dataclasses import asdict, dataclass
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from raylings.ui import console as default_console


@dataclass
class TourStep:
    """Represents a single step in the Raylings onboarding tour."""

    step_number: int
    title: str
    summary: str
    content: str
    command_hint: str | None = None
    action_label: str | None = None


class TourEngine:
    """Engine managing the 5-step interactive onboarding tour for Raylings learners."""

    def __init__(self) -> None:
        self.steps: list[TourStep] = [
            TourStep(
                step_number=1,
                title="Welcome to Raylings & Distributed Ray Primitives",
                summary="Introduction to the hands-on Ray curriculum and core distributed primitives.",
                content=(
                    "Ray is an open-source unified framework for scaling AI and Python applications.\n"
                    "Raylings guides you through tasks, actors, objects, placement groups, Ray Train,\n"
                    "Ray Data, Ray Serve, and advanced distributed patterns through 78 hands-on exercises."
                ),
                command_hint="raylings list",
                action_label="View Curriculum",
            ),
            TourStep(
                step_number=2,
                title="Environment & Preflight Diagnostics",
                summary="Verify your Python and Ray environment, dependencies, and cluster health.",
                content=(
                    "Ensure Python 3.10+, Ray, PyTorch, and required dependencies are properly configured.\n"
                    "Raylings includes a built-in preflight diagnostic tool (`raylings doctor`) and a\n"
                    "background daemon to automatically monitor local Ray cluster health."
                ),
                command_hint="raylings doctor",
                action_label="Run Preflight Diagnostics",
            ),
            TourStep(
                step_number=3,
                title="Solving Your First Exercise (basics01)",
                summary="Start your journey with exercises/01_basics/basics01.py and @ray.remote.",
                content=(
                    "Open `exercises/01_basics/basics01.py` in your editor. Transform standard Python\n"
                    "functions into distributed tasks using the `@ray.remote` decorator and invoke them\n"
                    "with `.remote()`. Complete the TODO tasks and verify your solution."
                ),
                command_hint="raylings run exercises/01_basics/basics01.py",
                action_label="Run First Exercise",
            ),
            TourStep(
                step_number=4,
                title="Watcher & Keystroke Navigation",
                summary="Continuous auto-compilation, real-time feedback, and instant keyboard controls.",
                content=(
                    "Run `raylings watch` to start the live file watcher. Raylings monitors changes,\n"
                    "executes the current exercise on save, and provides interactive keyboard navigation:\n"
                    "  [n] Next exercise  |  [p] Previous  |  [r] Rerun  |  [h] Hint  |  [q] Quit"
                ),
                command_hint="raylings watch",
                action_label="Start Interactive Watcher",
            ),
            TourStep(
                step_number=5,
                title="VS Code & IDE Experience",
                summary="Native IDE extension with exercise tree view, auto-run on save, and status bar.",
                content=(
                    "Install the Raylings VS Code extension (`editors/vscode`) to browse curriculum chapters\n"
                    "directly from the sidebar tree view, trigger auto-evaluations on save, inspect cluster\n"
                    "health in the status bar, and reveal progressive hints without leaving your editor."
                ),
                command_hint="code .",
                action_label="Open in VS Code",
            ),
        ]

    def get_steps(self) -> list[TourStep]:
        """Return the ordered list of all tour steps."""
        return list(self.steps)

    def get_step(self, step_number: int) -> TourStep | None:
        """Retrieve a specific tour step by its 1-indexed step number."""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None

    def to_json_dict(self) -> dict[str, Any]:
        """Serialize the tour metadata and all steps into a JSON-compatible dictionary."""
        return {
            "title": "Raylings Interactive Onboarding Tour",
            "total_steps": len(self.steps),
            "steps": [asdict(step) for step in self.steps],
        }

    def render_step(self, step: TourStep, console: Console | None = None) -> None:
        """Render a formatted Rich panel displaying the tour step.

        Args:
            step: The TourStep instance to render.
            console: Optional Rich console instance. Defaults to raylings.ui.console.
        """
        c = console if console is not None else default_console
        total = len(self.steps)

        body = Text()
        body.append(f"{step.summary}\n\n", style="bold yellow")
        body.append(f"{step.content}\n", style="white")

        if step.command_hint:
            body.append("\nSuggested Command:\n", style="bold cyan")
            body.append(f"  $ {step.command_hint}\n", style="bold green")

        if step.action_label:
            body.append(f"\nAction: {step.action_label}\n", style="dim magenta")

        panel_title = f"[bold cyan]🚀 Raylings Tour: Step {step.step_number}/{total} - {step.title}[/bold cyan]"
        c.print(
            Panel(
                body,
                title=panel_title,
                border_style="bright_blue",
                padding=(1, 2),
            )
        )


_global_tour_engine: TourEngine | None = None


def get_tour_engine() -> TourEngine:
    """Return a shared or new TourEngine instance."""
    global _global_tour_engine
    if _global_tour_engine is None:
        _global_tour_engine = TourEngine()
    return _global_tour_engine
