"""Run a bounded deterministic rerun audit for pilot experiment rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.deterministic_rerun_audit import (  # noqa: E402
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV,
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC,
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST,
    write_deterministic_rerun_audit,
)
from src.realworld.pilot_experiments import DEFAULT_SAMPLE_PROFILE_ID  # noqa: E402


def main() -> int:
    """Write deterministic rerun audit artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        default=DEFAULT_SAMPLE_PROFILE_ID,
        help="Pilot experiment design profile to rerun twice.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV),
        help="Output CSV path.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST),
        help="Output JSON manifest path.",
    )
    parser.add_argument(
        "--doc",
        default=str(DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC),
        help="Output Markdown path.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return non-zero when deterministic structural blockers remain.",
    )
    args = parser.parse_args()
    manifest = write_deterministic_rerun_audit(
        run_profile=args.profile,
        output_path=args.output,
        audit_manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_blockers and manifest["blocking_check_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
