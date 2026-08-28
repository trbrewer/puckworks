"""Make repository-only publishing tools importable under the ``pytest`` console script.

The tools intentionally are not shipped in the puckworks wheel.  ``python -m pytest`` already places
the checkout root on ``sys.path``; CI also invokes the standalone ``pytest`` executable, which does
not.  Keep this path adjustment scoped to publishing-tool tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
