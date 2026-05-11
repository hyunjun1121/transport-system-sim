"""Write the clean-checkout reproducibility review packet."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.reproducibility_review_packet import (  # noqa: E402
    build_reproducibility_review_rows,
    write_reproducibility_review_packet,
)


def main() -> int:
    """Write the review packet and print the non-acceptance manifest."""

    rows = build_reproducibility_review_rows()
    manifest = write_reproducibility_review_packet(rows=rows)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
