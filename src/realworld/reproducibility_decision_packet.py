"""Focused reproducibility decision worksheet.

The reproducibility review packet and smoke manifests expose detailed
reproduction evidence. This module turns their current state into
reproducibility-gate decision rows without creating
``data/manifests/reproducibility_acceptance.json`` or accepting final package
reproducibility.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.clean_checkout_smoke import (
    DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH,
    DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
)
from src.realworld.reproducibility_acceptance import (
    DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
)
from src.realworld.reproducibility_review_packet import (
    DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_PACKAGE_DOC_PATH,
    DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH,
)
from src.realworld.reproducibility_smoke import (
    DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH,
    DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "reproducibility_decision_packet.csv"
)
DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "reproducibility_decision_manifest.json"
)
DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "reproducibility_decision_packet.md"
)
REPRODUCIBILITY_DECISION_SCOPE = (
    "Reproducibility decision packet only; not reproducibility acceptance, not "
    "clean-environment certification, not artifact-regeneration acceptance, not "
    "final-study approval, and not operational routing evidence."
)
REPRODUCIBILITY_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_reproducibility_acceptance",
    "claim_boundary",
)


def build_reproducibility_decision_rows(
    *,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    reproducibility_review_manifest_path: str
    | Path = DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    reproducibility_smoke_manifest_path: str
    | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    clean_checkout_smoke_manifest_path: str
    | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    reproducibility_acceptance_path: str
    | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for reproducibility gate decisions."""

    reproducibility_manifest = _read_json_object(reproducibility_manifest_path)
    review_manifest = _read_json_object(reproducibility_review_manifest_path)
    worktree_smoke = _read_json_object(reproducibility_smoke_manifest_path)
    clean_checkout_smoke = _read_json_object(clean_checkout_smoke_manifest_path)
    acceptance_path = Path(reproducibility_acceptance_path)
    evidence_paths = _evidence_paths(
        reproducibility_manifest_path=reproducibility_manifest_path,
        reproducibility_review_manifest_path=reproducibility_review_manifest_path,
        reproducibility_smoke_manifest_path=reproducibility_smoke_manifest_path,
        clean_checkout_smoke_manifest_path=clean_checkout_smoke_manifest_path,
    )
    manifest_scope = str(reproducibility_manifest.get("scope", "")).strip()
    scaffold_scope = "scaffold" in manifest_scope.lower()
    clean_checkout_blocked = _clean_checkout_scope_blocked(
        review_manifest,
        clean_checkout_smoke,
    )
    artifact_regeneration_blocked = not bool(
        clean_checkout_smoke.get("artifact_regeneration_tested")
    )

    return [
        _row(
            decision_id="reproducibility_manifest_scope_decision",
            decision_topic="Reproducibility manifest scope",
            candidate_decision=(
                "Replace scaffold-only reproduction scope with a reviewed final "
                "package before accepting clean-checkout reproducibility"
            ),
            current_evidence=_manifest_scope_evidence(
                reproducibility_manifest,
                review_manifest,
            ),
            decision_status=(
                "blocked_scaffold_reproducibility_manifest_scope"
                if scaffold_scope
                else "needs_human_review_reproducibility_manifest_scope"
            ),
            blocking_reason=(
                "reproducibility manifest remains scaffold-only"
                if scaffold_scope
                else ""
            ),
            required_reviewer_action=(
                "Review the manifest scope, command ladder, and regenerated "
                "artifact list before formal reproducibility acceptance."
            ),
            followup_artifacts=(
                "data/manifests/reproducibility_manifest.json; "
                "data/manifests/reproducibility_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="validation_command_ladder_decision",
            decision_topic="Validation command ladder",
            candidate_decision=(
                "Accept the command ladder only after reviewer confirms command "
                "coverage, command counts, and artifact regeneration scope"
            ),
            current_evidence=_command_ladder_evidence(review_manifest),
            decision_status="needs_human_review_command_ladder_scope",
            blocking_reason="",
            required_reviewer_action=(
                "Compare manifest command counts with the planned validation "
                "ladder and decide whether additional clean-checkout commands "
                "are required."
            ),
            followup_artifacts=(
                "data/validation/reproducibility_review_packet.csv; "
                "data/manifests/reproducibility_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="clean_checkout_evidence_scope_decision",
            decision_topic="Clean-checkout smoke scope",
            candidate_decision=(
                "Use bounded clean-checkout smoke only as review evidence unless "
                "the reviewer accepts its commit freshness and current-Python "
                "environment limits"
            ),
            current_evidence=_clean_checkout_evidence(
                review_manifest,
                clean_checkout_smoke,
            ),
            decision_status=(
                "blocked_bounded_or_stale_clean_checkout_evidence"
                if clean_checkout_blocked
                else "needs_human_review_clean_checkout_evidence_scope"
            ),
            blocking_reason=(
                "clean-checkout smoke is bounded, stale, or not a full clean-environment reproduction"
                if clean_checkout_blocked
                else ""
            ),
            required_reviewer_action=(
                "Decide whether to rerun clean-checkout smoke at the current "
                "commit and whether a full dependency reinstall is required."
            ),
            followup_artifacts=(
                "data/validation/clean_checkout_reproducibility_smoke_manifest.json; "
                "data/manifests/reproducibility_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="worktree_package_state_decision",
            decision_topic="Git worktree and package state",
            candidate_decision=(
                "Accept package state only after reviewer confirms the committed "
                "tree, untracked artifact scope, and tracked-artifact audit"
            ),
            current_evidence=_worktree_evidence(review_manifest),
            decision_status="needs_human_review_committed_package_state",
            blocking_reason="",
            required_reviewer_action=(
                "Confirm the final package is committed, clean, and contains or "
                "explicitly excludes all required generated artifacts."
            ),
            followup_artifacts=(
                "data/validation/tracked_artifact_audit_manifest.json; "
                "data/manifests/reproducibility_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="runtime_import_boundary_decision",
            decision_topic="Runtime cloned_repo import boundary",
            candidate_decision=(
                "Accept the runtime import boundary only after reviewer confirms "
                "no production, script, or test runtime imports depend on cloned_repo"
            ),
            current_evidence=_import_boundary_evidence(review_manifest),
            decision_status="needs_human_review_runtime_import_boundary",
            blocking_reason="",
            required_reviewer_action=(
                "Review cloned_repo import scan results and preserve cloned_repo "
                "as reference-only context."
            ),
            followup_artifacts=(
                "data/validation/reproducibility_review_packet.csv; "
                "data/manifests/reproducibility_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="artifact_regeneration_decision",
            decision_topic="Artifact regeneration evidence",
            candidate_decision=(
                "Accept artifact regeneration only after clean-checkout or "
                "reviewed package commands regenerate required tables, figures, "
                "manifests, and report outputs"
            ),
            current_evidence=_artifact_regeneration_evidence(
                clean_checkout_smoke,
                worktree_smoke,
            ),
            decision_status=(
                "blocked_artifact_regeneration_not_tested"
                if artifact_regeneration_blocked
                else "needs_human_review_artifact_regeneration"
            ),
            blocking_reason=(
                "clean-checkout artifact regeneration protocol has not been tested"
                if artifact_regeneration_blocked
                else ""
            ),
            required_reviewer_action=(
                "Run or review artifact-regeneration commands before formal "
                "reproducibility acceptance."
            ),
            followup_artifacts=(
                "docs/reproducibility_package.md; "
                "data/manifests/reproducibility_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_reproducibility_acceptance_boundary",
            decision_topic="Formal reproducibility acceptance boundary",
            candidate_decision=(
                "Create reproducibility_acceptance.json only after clean-checkout, "
                "validation-ladder, artifact-regeneration, manifest-path, "
                "import-boundary, command-count, and not-operational review"
            ),
            current_evidence=(
                f"reproducibility_acceptance_present={str(acceptance_path.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_formal_reproducibility_acceptance"
                if acceptance_path.exists()
                else "blocked_missing_reproducibility_acceptance_record"
            ),
            blocking_reason=(
                ""
                if acceptance_path.exists()
                else "data/manifests/reproducibility_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Record formal reproducibility acceptance only after placeholders "
                "are absent and the reviewer accepts the reproduction scope."
            ),
            followup_artifacts="data/manifests/reproducibility_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_reproducibility_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    reproducibility_review_manifest_path: str
    | Path = DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    reproducibility_smoke_manifest_path: str
    | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    clean_checkout_smoke_manifest_path: str
    | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    reproducibility_acceptance_path: str
    | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown reproducibility decision artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPRODUCIBILITY_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in REPRODUCIBILITY_DECISION_COLUMNS
                }
            )

    summary = build_reproducibility_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        reproducibility_manifest_path=reproducibility_manifest_path,
        reproducibility_review_manifest_path=reproducibility_review_manifest_path,
        reproducibility_smoke_manifest_path=reproducibility_smoke_manifest_path,
        clean_checkout_smoke_manifest_path=clean_checkout_smoke_manifest_path,
        reproducibility_acceptance_path=reproducibility_acceptance_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_reproducibility_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_reproducibility_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH,
    reproducibility_manifest_path: str | Path = DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    reproducibility_review_manifest_path: str
    | Path = DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    reproducibility_smoke_manifest_path: str
    | Path = DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    clean_checkout_smoke_manifest_path: str
    | Path = DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    reproducibility_acceptance_path: str
    | Path = DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative reproducibility decision manifest."""

    statuses = _counts(row.get("decision_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked")
    )
    human_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            REPRODUCIBILITY_DECISION_SCOPE
            + " It cannot create or replace data/manifests/reproducibility_acceptance.json."
        ),
        "result_scope": REPRODUCIBILITY_DECISION_SCOPE,
        "row_count": len(rows),
        "decision_status_counts": statuses,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_count,
        "reproducibility_manifest_decision_recorded": False,
        "command_ladder_decision_recorded": False,
        "clean_checkout_scope_decision_recorded": False,
        "artifact_regeneration_decision_recorded": False,
        "reproducibility_decision_recorded": False,
        "reproducibility_acceptance_record_present": Path(
            reproducibility_acceptance_path
        ).exists(),
        "reproducibility_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "reproducibility_manifest": _display_path(
                Path(reproducibility_manifest_path)
            ),
            "reproducibility_review_manifest": _display_path(
                Path(reproducibility_review_manifest_path)
            ),
            "reproducibility_smoke_manifest": _display_path(
                Path(reproducibility_smoke_manifest_path)
            ),
            "clean_checkout_smoke_manifest": _display_path(
                Path(clean_checkout_smoke_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review scaffold-only reproducibility manifest scope",
            "confirm validation command ladder coverage and command counts",
            "decide whether bounded clean-checkout smoke is fresh and sufficient",
            "run or review artifact-regeneration evidence before acceptance",
            "create data/manifests/reproducibility_acceptance.json only after all reproducibility decisions are source-backed",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_reproducibility_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable reproducibility decision packet."""

    lines = [
        "# Reproducibility Decision Packet",
        "",
        str(manifest.get("claim_boundary", REPRODUCIBILITY_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Status counts: `{manifest.get('decision_status_counts', {})}`",
        "",
        "## Decision Rows",
        "",
        "| Decision | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {decision} | {status} | {evidence} | {action} |".format(
                decision=_cell(row.get("decision_id", "")),
                status=_cell(row.get("decision_status", "")),
                evidence=_cell(row.get("current_evidence", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet does not approve reproducibility or final-study completion.",
            "- It does not replace clean-checkout, full clean-environment, artifact-regeneration, or formal acceptance review.",
            "- Keep `data/manifests/reproducibility_acceptance.json` absent until a reviewer accepts the reproduction scope.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    decision_id: str,
    decision_topic: str,
    candidate_decision: str,
    current_evidence: str,
    decision_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "decision_topic": decision_topic,
        "candidate_decision": candidate_decision,
        "current_evidence": current_evidence,
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_reproducibility_acceptance": "false",
        "claim_boundary": REPRODUCIBILITY_DECISION_SCOPE,
    }


def _read_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{json_path} must contain a JSON object")
    return value


def _manifest_scope_evidence(
    manifest: Mapping[str, Any],
    review_manifest: Mapping[str, Any],
) -> str:
    return (
        f"scope={manifest.get('scope', '')}; "
        f"review_scope={review_manifest.get('reproducibility_manifest_scope', '')}; "
        f"review_status_counts={review_manifest.get('status_counts', {})}"
    )


def _command_ladder_evidence(review_manifest: Mapping[str, Any]) -> str:
    return (
        f"command_count={review_manifest.get('command_count', 0)}; "
        f"validation_command_count={review_manifest.get('validation_command_count', 0)}; "
        f"clean_checkout_smoke_command_count={review_manifest.get('clean_checkout_smoke_command_count', 0)}"
    )


def _clean_checkout_evidence(
    review_manifest: Mapping[str, Any],
    clean_checkout_smoke: Mapping[str, Any],
) -> str:
    source = _dict_value(clean_checkout_smoke, "source")
    return (
        f"clean_checkout_test_performed={str(review_manifest.get('clean_checkout_test_performed', False)).lower()}; "
        f"clean_checkout_smoke_passed={str(review_manifest.get('clean_checkout_smoke_passed', False)).lower()}; "
        f"matches_review_head={str(review_manifest.get('clean_checkout_smoke_matches_review_head', False)).lower()}; "
        f"source_commit_relation={review_manifest.get('clean_checkout_smoke_source_commit_relation_to_review_head', '')}; "
        f"source_commit_lag_count={review_manifest.get('clean_checkout_smoke_source_commit_lag_count', '')}; "
        f"full_clean_environment_tested={str(review_manifest.get('full_clean_environment_tested', False)).lower()}; "
        f"dependency_install_tested={str(clean_checkout_smoke.get('dependency_install_tested', False)).lower()}; "
        f"source_commit={source.get('source_commit', '')}"
    )


def _worktree_evidence(review_manifest: Mapping[str, Any]) -> str:
    return (
        f"git_status_line_count={review_manifest.get('git_status_line_count', 0)}; "
        f"git_modified_or_staged_count={review_manifest.get('git_modified_or_staged_count', 0)}; "
        f"git_untracked_count={review_manifest.get('git_untracked_count', 0)}"
    )


def _import_boundary_evidence(review_manifest: Mapping[str, Any]) -> str:
    return (
        f"no_runtime_cloned_repo_imports={str(review_manifest.get('no_runtime_cloned_repo_imports', False)).lower()}; "
        f"runtime_cloned_repo_import_hits={review_manifest.get('runtime_cloned_repo_import_hits', [])}"
    )


def _artifact_regeneration_evidence(
    clean_checkout_smoke: Mapping[str, Any],
    worktree_smoke: Mapping[str, Any],
) -> str:
    return (
        f"clean_checkout_artifact_regeneration_tested={str(clean_checkout_smoke.get('artifact_regeneration_tested', False)).lower()}; "
        f"clean_checkout_dependency_install_tested={str(clean_checkout_smoke.get('dependency_install_tested', False)).lower()}; "
        f"worktree_smoke_passed={str(worktree_smoke.get('smoke_passed', False)).lower()}; "
        f"worktree_smoke_command_count={worktree_smoke.get('command_count', 0)}"
    )


def _clean_checkout_scope_blocked(
    review_manifest: Mapping[str, Any],
    clean_checkout_smoke: Mapping[str, Any],
) -> bool:
    return (
        not bool(review_manifest.get("clean_checkout_test_performed"))
        or not bool(review_manifest.get("clean_checkout_smoke_passed"))
        or not bool(review_manifest.get("clean_checkout_smoke_matches_review_head"))
        or not bool(review_manifest.get("full_clean_environment_tested"))
        or not bool(clean_checkout_smoke.get("dependency_install_tested"))
    )


def _evidence_paths(
    *,
    reproducibility_manifest_path: str | Path,
    reproducibility_review_manifest_path: str | Path,
    reproducibility_smoke_manifest_path: str | Path,
    clean_checkout_smoke_manifest_path: str | Path,
) -> str:
    paths = [
        Path(reproducibility_manifest_path),
        DEFAULT_REPRODUCIBILITY_PACKAGE_DOC_PATH,
        DEFAULT_REPRODUCIBILITY_REVIEW_PACKET_PATH,
        Path(reproducibility_review_manifest_path),
        Path(reproducibility_smoke_manifest_path),
        DEFAULT_REPRODUCIBILITY_SMOKE_DOC_PATH,
        Path(clean_checkout_smoke_manifest_path),
        DEFAULT_CLEAN_CHECKOUT_SMOKE_DOC_PATH,
    ]
    return "; ".join(dict.fromkeys(_display_path(path) for path in paths))


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked") and reason:
            blockers.append(reason)
    return list(dict.fromkeys(blockers))


def _dict_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH",
    "DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH",
    "DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH",
    "REPRODUCIBILITY_DECISION_COLUMNS",
    "REPRODUCIBILITY_DECISION_SCOPE",
    "build_reproducibility_decision_manifest",
    "build_reproducibility_decision_markdown",
    "build_reproducibility_decision_rows",
    "write_reproducibility_decision_packet",
]
