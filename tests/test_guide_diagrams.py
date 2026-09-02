"""Tests verifying all architectural guides contain streamlined, valid Mermaid diagrams with concept walkthroughs."""
import re
from pathlib import Path


def test_all_18_guides_contain_streamlined_mermaid_diagrams_and_concepts():
    """Verify that each of the 18 chapter guides contains exactly 1 streamlined Mermaid flowchart and an attached concept walkthrough."""
    guides_dir = Path("docs/guides")
    assert guides_dir.is_dir(), "docs/guides directory must exist"
    guide_files = sorted(guides_dir.glob("*.md"))
    assert len(guide_files) == 18, f"Expected 18 chapter guides, got {len(guide_files)}"

    for guide in guide_files:
        content = guide.read_text(encoding="utf-8")
        assert "```mermaid" in content, f"Guide {guide.name} must contain a mermaid diagram"
        assert not re.search(r"[┌└├]──", content), f"Guide {guide.name} still contains legacy ASCII box drawings"

        # Check for attached concept breakdown
        assert "> **Diagram Walkthrough & Core Concepts:**" in content, (
            f"Guide {guide.name} is missing '> **Diagram Walkthrough & Core Concepts:**' callout"
        )

        # Assert exactly one focused Mermaid diagram
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        assert len(mermaid_blocks) == 1, (
            f"Guide {guide.name} should have exactly 1 streamlined Mermaid diagram, found {len(mermaid_blocks)}"
        )

        diagram = mermaid_blocks[0]
        # Check for invalid link syntax
        assert not re.search(r"<[-=]+\|", diagram), f"Guide {guide.name} has invalid Mermaid link syntax"

        first_line = diagram.strip().splitlines()[0] if diagram.strip() else ""
        assert re.match(r"^(flowchart|graph)\b", first_line), (
            f"Guide {guide.name} diagram should be a clean flowchart/graph, got: '{first_line}'"
        )


def test_overview_and_syllabus_contain_mermaid_diagrams():
    """Verify that index.md and syllabus.md contain streamlined Mermaid diagrams and valid headers."""
    for path_str in ["docs/index.md", "docs/syllabus.md"]:
        doc_path = Path(path_str)
        assert doc_path.exists(), f"{path_str} must exist"
        content = doc_path.read_text(encoding="utf-8")
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        assert len(mermaid_blocks) == 1, f"{path_str} must contain exactly one streamlined Mermaid diagram"
        for b in mermaid_blocks:
            assert not re.search(r"<[-=]+\|", b), f"{path_str} has invalid Mermaid link syntax"
            first_line = b.strip().splitlines()[0] if b.strip() else ""
            assert re.match(r"^(flowchart|graph)\b", first_line), (
                f"{path_str} has invalid Mermaid diagram header: '{first_line}'"
            )
        assert "> **Diagram Walkthrough & Core Concepts:**" in content, (
            f"{path_str} is missing '> **Diagram Walkthrough & Core Concepts:**' callout"
        )

