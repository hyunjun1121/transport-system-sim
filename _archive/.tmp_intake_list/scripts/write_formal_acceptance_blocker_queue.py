"""Compatibility command for writing the formal acceptance blocker queue.

The implementation lives in ``scripts/write_acceptance_blocker_queue.py``.
This wrapper keeps the plan validation ladder runnable under the more explicit
formal-acceptance command name.
"""

from __future__ import annotations

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    runpy.run_path(
        str(ROOT / "scripts" / "write_acceptance_blocker_queue.py"),
        run_name="__main__",
    )
