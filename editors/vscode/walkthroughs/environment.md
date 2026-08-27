# 🔍 Environment & Preflight Diagnostics

Before diving into distributed exercises, ensure your Python and Ray environment is properly configured.

### ⚙️ Prerequisites
- **Python 3.10+** (Python 3.10, 3.11, or 3.12 recommended)
- **Ray Core** installed and importable in your active environment
- **2+ Logical CPU Cores** recommended for local parallelism

### 🩺 Preflight Diagnostics (`raylings doctor`)
Raylings provides an automated environment diagnostic tool that verifies:
1. Python interpreter version and runtime capabilities.
2. Ray package installation and import integrity.
3. Ray background daemon session status.
4. Exercises directory and manifest integrity.
5. System CPU cores and physical memory capacity.

Click the button below to run preflight diagnostics in an integrated terminal:

[Run Doctor Diagnostics](command:raylings.runDoctor)
