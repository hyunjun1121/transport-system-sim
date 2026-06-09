"""Write fail-closed phase-gate ledger templates and audit outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.phase_gate_ledger import write_phase_gate_ledgers  # noqa: E402


def main() -> int:
    """Write phase-gate ledger artifacts and print the audit manifest."""

    args = _parse_args()
    audit = write_phase_gate_ledgers()
    print(json.dumps(audit, indent=2, sort_keys=True))
    if args.fail_on_blockers and not audit["phase_gate_ledgers_ready"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 unless every phase gate is closed.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
