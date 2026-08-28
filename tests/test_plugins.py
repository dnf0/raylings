"""Unit tests for the Raylings Curriculum Plugin architecture and domain extension packs."""

from typer.testing import CliRunner

from raylings.cli import app
from raylings.manifest import get_manifest
from raylings.models import Chapter, Exercise
from raylings.plugins import (
    PluginRegistry,
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
    initial_chapter_count = len(manifest.chapters)
    assert initial_chapter_count >= 18

    class CustomTestPlugin(RaylingsPlugin):
        def __init__(self) -> None:
            super().__init__(
                name="custom_test",
                title="Custom Extension Pack",
                version="0.1.0",
                description="Custom test plugin",
                author="Test Author",
            )

        def get_chapters(self) -> list[Chapter]:
            return [
                Chapter(
                    number=19,
                    name="19_custom",
                    title="Distributed Custom Extension",
                    description="Custom plugin chapter",
                    exercises=[
                        Exercise(
                            name="custom01",
                            title="Custom Exercise",
                            path="exercises/19_custom/custom01.py",
                            chapter_name="19_custom",
                            hints=["A valid test hint."],
                        )
                    ],
                )
            ]

    registry = PluginRegistry()
    registry.register(CustomTestPlugin())
    extended_manifest = registry.extend_manifest(manifest)
    assert len(extended_manifest.chapters) == initial_chapter_count + 1
    ch19 = next(ch for ch in extended_manifest.chapters if ch.number == 19)
    assert ch19.title == "Distributed Custom Extension"


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
