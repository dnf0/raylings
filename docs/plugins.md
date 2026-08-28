# Curriculum Plugin & Extension Pack Architecture

Raylings features an open, pluggable curriculum architecture enabling domain specialists, research groups, and organizations to author, distribute, and register custom chapters and exercises using standard Python packaging mechanisms.

---

## Overview

Raylings plugins allow you to:
- Package custom domain curricula (e.g. Quantitative Finance, Bio-Informatics, Robotics, Geospatial Analytics).
- Distribute extension packs via PyPI or internal Git repositories.
- Automatically discover installed plugins via Python Entry Points (`raylings.plugins`).
- Seamlessly integrate custom exercises into the CLI (`raylings list`, `raylings run`, `raylings verify`, `raylings watch`, `raylings tui`).

---

## Plugin Contract: `RaylingsPlugin`

All plugins inherit from [`RaylingsPlugin`](file:///Users/danielfisher/repos/raylings/src/raylings/plugins/base.py):

```python
from raylings.models import Chapter, Exercise
from raylings.plugins.base import RaylingsPlugin


class CustomPackPlugin(RaylingsPlugin):
    name: str = "robotics"
    title: str = "Distributed Robotics & Sim-to-Real RL"
    version: str = "0.1.0"
    description: str = "Distributed physics simulation and multi-agent robotics with Ray."
    author: str = "Robotics Special Interest Group"

    def get_chapters(self) -> list[Chapter]:
        return [
            Chapter(
                number=19,
                name="19_robotics",
                title="Distributed Robotics Simulation",
                description="Simulate parallel physics environments using Ray actors.",
                exercises=[
                    Exercise(
                        name="robotics01",
                        title="Parallel Isaac Sim Actor Environment",
                        path="exercises/19_robotics/robotics01.py",
                        chapter_name="19_robotics",
                        hints=[
                            "Instantiate headless simulation worker actors.",
                            "Batch observations using ray.get().",
                        ],
                    ),
                ],
            )
        ]
```

---

## Packaging & Entry Points

To make your plugin discoverable by Raylings, register an entry point under the `raylings.plugins` group in your package's `pyproject.toml`:

```toml
[project]
name = "raylings-robotics"
version = "0.1.0"
dependencies = [
    "raylings>=0.5.0",
]

[project.entry-points."raylings.plugins"]
robotics = "raylings_robotics.plugin:CustomPackPlugin"
```

Once installed into your virtual environment (`pip install raylings-robotics` or `uv add raylings-robotics`), Raylings automatically discovers and loads the plugin.

---

## CLI Management & Inspection

Raylings provides a dedicated `plugins` CLI group:

### 1. List Installed Plugins
```bash
raylings plugins list
```

Displays an overview table of all installed plugins, version numbers, authors, and chapter counts.

### 2. Inspect Plugin Details
```bash
raylings plugins info finance
```

Displays metadata and lists all chapters and exercises provided by the plugin.

### 3. Validate Plugin Contract
```bash
raylings plugins validate raylings.plugins.finance:FinancePlugin
```

Validates that your plugin satisfies the `RaylingsPlugin` protocol, checks chapter numbering, verifies exercise file paths, and ensures no duplicate exercise identifiers exist.

---

## Reference Plugin: Chapter 18 (Distributed Quantitative Finance)

Raylings includes a built-in reference plugin [`raylings.plugins.finance.FinancePlugin`](file:///Users/danielfisher/repos/raylings/src/raylings/plugins/finance.py):

- **Exercise 1 (`finance01`)**: Distributed Monte Carlo European Option Pricing with Actor Pool.
- **Exercise 2 (`finance02`)**: Distributed Multi-Asset Portfolio Value-at-Risk (VaR) & CVaR.
- **Exercise 3 (`finance03`)**: Streaming High-Frequency Market Tick Analytics & VWAP with Ray Data.
