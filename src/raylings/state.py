"""State tracking and persistence for Raylings exercise progress."""

import json
from pathlib import Path


class StateTracker:
    """Manages persistent tracking of completed exercises in a local workspace state file."""

    STATE_FILENAME = ".raylings_state.json"

    def __init__(self, root_dir: Path | None = None) -> None:
        """Initialize StateTracker with optional root directory."""
        self.root_dir = root_dir if root_dir is not None else Path.cwd()
        self.state_file = self.root_dir / self.STATE_FILENAME

    def _load_state(self) -> dict[str, bool]:
        """Load the state mapping from disk."""
        if not self.state_file.exists():
            return {}
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {k: bool(v) for k, v in data.items()}
            return {}
        except Exception:
            return {}

    def _save_state(self, state: dict[str, bool]) -> None:
        """Save the state mapping to disk."""
        try:
            self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception:
            pass

    def is_completed(self, exercise_name: str) -> bool:
        """Check if an exercise is recorded as completed."""
        state = self._load_state()
        return bool(state.get(exercise_name, False))

    def mark_completed(self, exercise_name: str, completed: bool = True) -> None:
        """Record the completion status of an exercise."""
        state = self._load_state()
        state[exercise_name] = completed
        self._save_state(state)

    def get_completed_set(self) -> set[str]:
        """Get set of all completed exercise names."""
        state = self._load_state()
        return {name for name, done in state.items() if done}

    def reset(self) -> None:
        """Reset all state."""
        if self.state_file.exists():
            try:
                self.state_file.unlink()
            except Exception:
                pass


_global_tracker: StateTracker | None = None


def get_state_tracker(root_dir: Path | None = None) -> StateTracker:
    """Get or create singleton StateTracker instance."""
    global _global_tracker
    if _global_tracker is None or root_dir is not None:
        _global_tracker = StateTracker(root_dir=root_dir)
    return _global_tracker
