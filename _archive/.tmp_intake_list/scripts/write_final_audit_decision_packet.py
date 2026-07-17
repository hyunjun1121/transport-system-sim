"""Write the final-audit decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.final_audit_acceptance import (  # noqa: E402
    DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
)
from src.realworld.final_audit_decision_packet import (  # noqa: E402
    DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
    DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
    DEFAULT_FINAL_STUDY_AUDIT_PATH,
    DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH,
    DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH,
    build_final_audit_decision_rows,
    write_final_audit_decision_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_final_audit_decision_rows(
        goal_completion_audit_path=args.goal_completion_audit,
        formal_package_audit_path=args.formal_package_audit,
        evidence_matrix_manifest_path=args.evidence_matrix_manifest,
        acceptance_orchestration_manifest_path=args.acceptance_orchestration_manifest,
        final_study_audit_path=args.final_study_audit,
        final_audit_acceptance_path=args.final_audit_acceptance,
    )
    manifest = write_final_audit_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        goal_completion_audit_path=args.goal_completion_audit,
        formal_package_audit_path=args.formal_package_audit,
        evidence_matrix_manifest_path=args.evidence_matrix_manifest,
        acceptance_orchestration_manifest_path=args.acceptance_orchestration_manifest,
        final_study_audit_path=args.final_study_audit,
        final_audit_acceptance_path=args.final_audit_acceptance,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for pre-final gate closure, formal "
            "acceptance artifact, final-study audit document, proxy-signal, "
            "handoff, and final-audit acceptance-boundary decisions."
        )
    )
    parser.add_argument(
        "--goal-completion-audit",
        type=Path,
        default=DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH,
    )
    parser.add_argument(
        "--formal-package-audit",
        type=Path,
        default=DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH,
    )
    parser.add_argument(
        "--evidence-matrix-manifest",
        type=Path,
        default=DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH,
    )
    parser.add_argument(
        "--acceptance-orchestration-manifest",
        type=Path,
        default=DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--final-study-audit",
        type=Path,
        default=DEFAULT_FINAL_STUDY_AUDIT_PATH,
    )
    parser.add_argument(
        "--final-audit-acceptance",
        type=Path,
        default=DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
