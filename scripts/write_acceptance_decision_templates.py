"""Write non-approval templates for formal acceptance decisions."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_decision_templates import (  # noqa: E402
    write_acceptance_decision_templates,
)


def main() -> int:
    """Write templates and print their manifest."""

    manifest = write_acceptance_decision_templates()
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
