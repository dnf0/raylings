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
        assert not re.search(r"[┌└├]──", content), f"Guide {guide.name} still contains legacy ASCII box drawings"

        # Check for mermaid block completeness and dual-diagram architecture
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        assert len(mermaid_blocks) >= 2, f"Guide {guide.name} must have at least 2 Mermaid diagrams"

        headers = []
        for b in mermaid_blocks:
            # Catch invalid link syntax (e.g. <==| or <---|)
            assert not re.search(r"<[-=]+\|", b), f"Guide {guide.name} has invalid Mermaid link syntax: <==|"
            first_line = b.strip().splitlines()[0] if b.strip() else ""
            assert re.match(r"^(flowchart|graph|sequenceDiagram|stateDiagram-v2|erDiagram)\b", first_line), (
                f"Guide {guide.name} has invalid Mermaid diagram header: '{first_line}'"
            )
            headers.append(first_line)

        has_flowchart = any(re.match(r"^(flowchart|graph)\b", h) for h in headers)
        has_sequence = any(re.match(r"^sequenceDiagram\b", h) for h in headers)
        assert has_flowchart, f"Guide {guide.name} missing flowchart diagram"
        assert has_sequence, f"Guide {guide.name} missing sequenceDiagram"


def test_overview_and_syllabus_contain_mermaid_diagrams():
    """Verify that index.md and syllabus.md contain Mermaid diagrams and valid headers."""
    for path_str in ["docs/index.md", "docs/syllabus.md"]:
        doc_path = Path(path_str)
        assert doc_path.exists(), f"{path_str} must exist"
        content = doc_path.read_text(encoding="utf-8")
        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        assert len(mermaid_blocks) >= 1, f"{path_str} must contain at least one Mermaid diagram"
        for b in mermaid_blocks:
            assert not re.search(r"<[-=]+\|", b), f"{path_str} has invalid Mermaid link syntax"
            first_line = b.strip().splitlines()[0] if b.strip() else ""
            assert re.match(r"^(flowchart|graph|sequenceDiagram|stateDiagram-v2|erDiagram)\b", first_line), (
                f"{path_str} has invalid Mermaid diagram header: '{first_line}'"
            )

