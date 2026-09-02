#!/usr/bin/env python3
"""Build script to bundle Raylings exercises, reference solutions, hints, and WASM compatibility
into a single JSON asset for the Pyodide WebAssembly browser playground.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repository src is prioritized for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from raylings.playground_assets import BUNDLE_PATH, export_playground_bundle, generate_playground_bundle


def main() -> None:
    """Entry point for command line bundle generation."""
    parser = argparse.ArgumentParser(description="Build Raylings Pyodide WebAssembly bundle")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=BUNDLE_PATH,
        help=f"Output bundle destination path (default: {BUNDLE_PATH})",
    )
    args = parser.parse_args()

    out_path = export_playground_bundle(args.output)
    bundle = generate_playground_bundle()
    print(
        f"✓ Successfully built Raylings WebAssembly bundle:\n"
        f"  - Output: {out_path}\n"
        f"  - Total Chapters: {bundle['total_chapters']}\n"
        f"  - Total Exercises: {bundle['total_exercises']}\n"
        f"  - WASM Engine Size: {len(bundle['wasm_compat_code'])} bytes"
    )


if __name__ == "__main__":
    main()
