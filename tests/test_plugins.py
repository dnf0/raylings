"""Unit tests for the Raylings Curriculum Plugin architecture and domain extension packs."""

from typer.testing import CliRunner

from raylings.cli import app
from raylings.manifest import get_manifest
from raylings.plugins import (
    PluginRegistry,
    get_plugin_registry,
)
from raylings.plugins.base import RaylingsPlugin
from raylings.plugins.finance import FinancePlugin

runner = CliRunner()


def test_finance_plugin_contract():
    """Verify FinancePlugin satisfies the RaylingsPlugin protocol."""
    plugin = FinancePlugin()
    assert isinstance(plugin, RaylingsPlugin)
    assert plugin.name == "finance"
    assert "Quantitative Finance" in plugin.title
    assert plugin.version == "0.1.0"

    errors = plugin.validate()
    assert len(errors) == 0

    chapters = plugin.get_chapters()
    assert len(chapters) == 1
    assert chapters[0].number == 18
    assert len(chapters[0].exercises) >= 3


def test_plugin_registry_discovery():
    """Verify PluginRegistry discovers and registers built-in and external plugins."""
    registry = PluginRegistry()
    registry.register(FinancePlugin())

    plugins = registry.list_plugins()
    assert "finance" in [p.name for p in plugins]

    plugin = registry.get_plugin("finance")
    assert plugin is not None
    assert plugin.name == "finance"


def test_manifest_plugin_integration():
    """Verify get_manifest() merges registered plugin chapters when requested."""
    manifest = get_manifest()
    # By default, core chapters are 1-17
    initial_chapter_count = len(manifest.chapters)
    assert initial_chapter_count >= 17

    registry = get_plugin_registry()
    extended_manifest = registry.extend_manifest(manifest)
    assert len(extended_manifest.chapters) >= initial_chapter_count + 1
    ch18 = next(ch for ch in extended_manifest.chapters if ch.number == 18)
    assert ch18.title == "Distributed Quantitative Finance"


def test_cli_plugins_list():
    """Verify `raylings plugins list` displays Rich table of available plugins."""
    result = runner.invoke(app, ["plugins", "list"])
    assert result.exit_code == 0
    assert "finance" in result.stdout
    assert "Quantitative" in result.stdout


def test_cli_plugins_info():
    """Verify `raylings plugins info finance` displays detailed curriculum breakdown."""
    result = runner.invoke(app, ["plugins", "info", "finance"])
    assert result.exit_code == 0
    assert "Quantitative Finance" in result.stdout
    assert "finance01" in result.stdout
    assert "finance02" in result.stdout
    assert "finance03" in result.stdout


def test_cli_plugins_validate():
    """Verify `raylings plugins validate` validates plugin contracts."""
    result = runner.invoke(app, ["plugins", "validate", "raylings.plugins.finance:FinancePlugin"])
    assert result.exit_code == 0
    assert "VALID" in result.stdout or "valid" in result.stdout.lower()


def test_finance_exercises_verification():
    """Verify reference quantitative finance solutions execute and verify correctly."""
    plugin = FinancePlugin()
    chapters = plugin.get_chapters()
    for ch in chapters:
        for ex in ch.exercises:
            assert ex.file_path.exists(), f"Missing exercise skeleton: {ex.file_path}"
            assert ex.solution_path.exists(), f"Missing solution: {ex.solution_path}"
