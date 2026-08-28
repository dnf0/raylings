import re
from pathlib import Path


def enrich_file(
    filepath: Path,
    topic: str,
    context_why: str,
    instructions: list[str],
    todo_replacements: list[tuple[str, str]] = None,
):
    text = filepath.read_text()

    # Extract code below docstring
    doc_match = re.search(r'^(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', text, flags=re.DOTALL)
    if doc_match:
        code_part = text[doc_match.end() :].lstrip()
    else:
        code_part = text.lstrip()

    # Ensure # I AM NOT DONE is at the top of code part
    if "# I AM NOT DONE" in code_part:
        code_part = (
            code_part.replace("# I AM NOT DONE\n", "").replace("# I AM NOT DONE", "").lstrip()
        )

    # Build formatted docstring
    instr_formatted = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(instructions))
    header = f'"""\nExercise: {filepath.as_posix()}\nTopic: {topic}\n\nContext & Why:\n{context_why.strip()}\n\nInstructions:\n{instr_formatted}\n"""\n\n# I AM NOT DONE\n\n'

    # Perform any TODO replacements if provided
    if todo_replacements:
        for old, new in todo_replacements:
            if old in code_part:
                code_part = code_part.replace(old, new)

    new_content = header + code_part
    filepath.write_text(new_content)
    print(f"Enriched: {filepath}")
