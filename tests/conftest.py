import os
import sys
from pathlib import Path

import matplotlib
import pytest

os.environ.setdefault("MPLBACKEND", "Agg")
matplotlib.use("Agg", force=True)

# Ensure project root is on sys.path so `import procsight...` works when running tests
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _no_show(monkeypatch):
    """Prevent interactive windows from opening during tests."""
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    monkeypatch.setattr(plt, "show", lambda *a, **k: None, raising=False)
