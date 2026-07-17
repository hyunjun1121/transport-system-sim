"""Write the non-approval formal acceptance evidence matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_evidence_matrix import (  # noqa: E402
    DEFAULT_EVIDENCE_MATRIX_DOC_PATH,
    DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH,
    DEFAULT_EVIDENCE_MATRIX_PATH,
    write_formal_acceptance_evidence_matrix,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_EVIDENCE_MATRIX_PATH))
    parser.add_argument("--manifest", default=str(DEFAULT_EVIDENCE_MATRIX_MANIFEST_PATH))
    parser.add_argument("--doc", default=str(DEFAULT_EVIDENCE_MATRIX_DOC_PATH))
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return non-zero while formal gates still require human decisions.",
    )
    args = parser.parse_args()

    summary = write_formal_acceptance_evidence_matrix(
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and int(summary["human_decision_required_count"]) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
