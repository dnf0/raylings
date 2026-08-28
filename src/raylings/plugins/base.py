"""Base class and interface definition for Raylings curriculum plugins."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any

from raylings.models import Chapter


@dataclass
class RaylingsPlugin(abc.ABC):
    """Abstract base class for third-party and domain-specific Raylings curriculum plugins."""

    name: str
    title: str
    version: str
    description: str
    author: str = "Community"

    @abc.abstractmethod
    def get_chapters(self) -> list[Chapter]:
        """Return the list of custom curriculum Chapters provided by this plugin.

        Returns:
            list[Chapter]: Ordered collection of chapter specifications.
        """
        raise NotImplementedError

    def get_custom_runners(self) -> dict[str, Any]:
        """Return custom exercise evaluation or verification runners if applicable.

        Returns:
            dict[str, Any]: Mapping of runner identifier to runner instance or callable.
        """
        return {}

    def validate(self) -> list[str]:
        """Validate that this plugin provides a well-formed curriculum.

        Returns:
            list[str]: List of error messages (empty if valid).
        """
        errors = []
        if (
            not self.name
            or not self.name.isalnum()
            and "_" not in self.name
            and "-" not in self.name
        ):
            errors.append(
                f"Plugin name '{self.name}' must be alphanumeric with optional hyphens/underscores."
            )
        if not self.title:
            errors.append("Plugin title cannot be empty.")
        if not self.version:
            errors.append("Plugin version cannot be empty.")

        try:
            chapters = self.get_chapters()
            if not chapters:
                errors.append("Plugin must provide at least one Chapter.")
            for ch in chapters:
                if not ch.title:
                    errors.append(f"Chapter {ch.number} title cannot be empty.")
                if not ch.exercises:
                    errors.append(f"Chapter '{ch.title}' must contain at least one Exercise.")
        except Exception as e:
            errors.append(f"Error invoking get_chapters(): {e}")

        return errors
