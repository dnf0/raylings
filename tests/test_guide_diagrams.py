"""Tests verifying all architectural guides contain rich, valid Mermaid diagrams."""
import re
from pathlib import Path


def test_all_18_guides_contain_rich_mermaid_diagrams():
    """Verify that each of the 18 chapter guides contains rich Mermaid diagrams and no legacy ASCII boxes."""
    guides_dir = Path("docs/guides")
    assert guides_dir.is_dir(), "docs/guides directory must exist"
    guide_files = sorted(guides_dir.glob("*.md"))
    assert len(guide_files) == 18, f"Expected 18 chapter guides, got {len(guide_files)}"

    for guide in guide_files:
        content = guide.read_text(encoding="utf-8")
        assert "```mermaid" in content, f"Guide {guide.name} must contain at least one mermaid diagram"
        assert "┌──" not in content, f"Guide {guide.name} still contains legacy ASCII box drawings"
        assert "│" not in content.split("```text")[1] if "```text" in content else True

        # Check for mermaid block completeness and dual-diagram architecture
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        assert len(mermaid_blocks) >= 2, f"Guide {guide.name} must have at least 2 Mermaid diagrams (Flowchart + Sequence)"
        has_flowchart = any("flowchart" in b or "graph" in b for b in mermaid_blocks)
        has_sequence = any("sequenceDiagram" in b for b in mermaid_blocks)
        assert has_flowchart, f"Guide {guide.name} missing flowchart diagram"
        assert has_sequence, f"Guide {guide.name} missing sequenceDiagram"


def test_overview_and_syllabus_contain_mermaid_diagrams():
    """Verify that index.md and syllabus.md contain Mermaid diagrams."""
    index_md = Path("docs/index.md")
    assert index_md.exists()
    assert "```mermaid" in index_md.read_text(encoding="utf-8"), "docs/index.md must contain Mermaid diagram"

    syllabus_md = Path("docs/syllabus.md")
    assert syllabus_md.exists()
    assert "```mermaid" in syllabus_md.read_text(encoding="utf-8"), "docs/syllabus.md must contain Mermaid diagram"
