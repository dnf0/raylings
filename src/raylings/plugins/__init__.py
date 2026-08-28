"""Curriculum plugin discovery, registry, and manifest integration for Raylings."""

from __future__ import annotations

import importlib
import importlib.metadata
import logging

from raylings.models import Manifest
from raylings.plugins.base import RaylingsPlugin
from raylings.plugins.finance import FinancePlugin

logger = logging.getLogger("raylings.plugins")


class PluginRegistry:
    """Manages discovery and lifecycle of Raylings curriculum extension plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, RaylingsPlugin] = {}
        self._register_builtins()
        self.discover_entrypoints()

    def _register_builtins(self) -> None:
        """Register first-party built-in plugins."""
        self.register(FinancePlugin())

    def register(self, plugin: RaylingsPlugin) -> None:
        """Register a plugin instance."""
        errors = plugin.validate()
        if errors:
            logger.warning("Plugin '%s' failed validation: %s", plugin.name, ", ".join(errors))
            return
        self._plugins[plugin.name] = plugin

    def discover_entrypoints(self) -> None:
        """Discover third-party plugins declared under 'raylings.plugins' entry-point group."""
        try:
            entry_points = importlib.metadata.entry_points()
            # Compatible with Python 3.10, 3.11, 3.12 entry points API
            plugin_eps = (
                entry_points.select(group="raylings.plugins")
                if hasattr(entry_points, "select")
                else entry_points.get("raylings.plugins", [])  # type: ignore[attr-defined]
            )
            for ep in plugin_eps:
                try:
                    plugin_cls = ep.load()
                    if callable(plugin_cls):
                        instance = plugin_cls()
                        if isinstance(instance, RaylingsPlugin):
                            self.register(instance)
                except Exception as err:
                    logger.warning("Failed to load plugin entry point '%s': %s", ep.name, err)
        except Exception as e:
            logger.debug("Plugin discovery error: %s", e)

    def list_plugins(self) -> list[RaylingsPlugin]:
        """Return all registered plugins."""
        return list(self._plugins.values())

    def get_plugin(self, name: str) -> RaylingsPlugin | None:
        """Retrieve a registered plugin by name."""
        return self._plugins.get(name)

    def extend_manifest(self, base_manifest: Manifest) -> Manifest:
        """Merge all registered plugin chapters into the active curriculum manifest."""
        existing_chapter_numbers = {ch.number for ch in base_manifest.chapters}
        merged_chapters = list(base_manifest.chapters)

        for plugin in self._plugins.values():
            for ch in plugin.get_chapters():
                if ch.number not in existing_chapter_numbers:
                    merged_chapters.append(ch)
                    existing_chapter_numbers.add(ch.number)

        merged_chapters.sort(key=lambda c: c.number)
        return Manifest(chapters=merged_chapters)


_GLOBAL_REGISTRY: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    """Return the global singleton PluginRegistry."""
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = PluginRegistry()
    return _GLOBAL_REGISTRY
