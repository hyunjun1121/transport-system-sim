"""Generate a non-acceptance completion audit for the active plan goal."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.realworld.acceptance_orchestration import (
    summarize_acceptance_orchestration_manifest,
)
from src.realworld.acceptance_decision_templates import (
    summarize_acceptance_decision_templates,
)
from src.realworld.acceptance_blocker_queue import (
    summarize_acceptance_blocker_queue,
)
from src.realworld.acceptance_task_assignments import (
    summarize_acceptance_task_assignments,
)
from src.realworld.formal_acceptance_evidence_matrix import (
    summarize_formal_acceptance_evidence_matrix,
)
from src.realworld.formal_acceptance_pre_review import (
    summarize_formal_acceptance_pre_review,
)
from src.realworld.agent_review_path_audit import audit_agent_review_paths
from src.realworld.final_study_readiness import audit_final_study_readiness
from src.realworld.formal_acceptance_guard import (
    audit_formal_acceptance_artifacts,
)
from src.realworld.formal_evidence_path_audit import (
    audit_formal_evidence_paths,
)
from src.realworld.formal_acceptance_package import (
    build_formal_acceptance_package_summary,
)
from src.realworld.clean_checkout_smoke import summarize_clean_checkout_smoke
from src.realworld.reproducibility_smoke import summarize_reproducibility_smoke
from src.realworld.tracked_artifact_audit import summarize_tracked_artifact_audit


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GOAL_COMPLETION_AUDIT_PATH = (
    PROJECT_ROOT / "docs" / "current_goal_completion_audit.md"
)

ACTIVE_OBJECTIVE = (
    "Implement every requirement planned in plan.md for the final real-world or "
    "quasi-real regional transport-resilience study."
)

NON_ACCEPTANCE_BOUNDARY = (
    "This document is a current-state completion gap audit. It is not "
    "docs/final_study_audit.md, not an acceptance record, not calibrated "
    "real-world validation, and not operational routing approval."
)

FINAL_ACCEPTANCE_ARTIFACTS = (
    "data/manifests/pilot_acceptance.json",
    "data/manifests/graph_scale_acceptance.json",
    "data/manifests/provenance_acceptance.json",
    "data/parameters/parameter_acceptance.csv",
    "data/parameters/road_class_overrides.csv",
    "data/manifests/validation_acceptance.json",
    "data/manifests/sensitivity_acceptance.json",
    "data/manifests/experiment_acceptance.json",
    "data/manifests/manuscript_acceptance.json",
    "data/manifests/reproducibility_acceptance.json",
    "docs/final_study_audit.md",
    "data/manifests/final_audit_acceptance.json",
)


def build_goal_completion_audit_markdown(
    audit: dict[str, Any] | None = None,
) -> str:
    """Return a markdown prompt-to-artifact audit for the active objective."""

    audit = audit or audit_final_study_readiness()
    orchestration = summarize_acceptance_orchestration_manifest()
    decision_templates = summarize_acceptance_decision_templates()
    blocker_queue = summarize_acceptance_blocker_queue()
    task_assignments = summarize_acceptance_task_assignments()
    evidence_matrix = summarize_formal_acceptance_evidence_matrix()
    pre_review = summarize_formal_acceptance_pre_review()
    agent_review_paths = audit_agent_review_paths()
    formal_guard = audit_formal_acceptance_artifacts()
    formal_evidence_paths = audit_formal_evidence_paths()
    formal_package = build_formal_acceptance_package_summary()
    reproducibility_smoke = summarize_reproducibility_smoke()
    clean_checkout_smoke = summarize_clean_checkout_smoke()
    tracked_artifacts = summarize_tracked_artifact_audit()
    ready_gate_ids = list(audit.get("ready_gate_ids", []))
    blocked_gate_ids = list(audit.get("blocked_gate_ids", []))
    lines: list[str] = [
        "# Current Goal Completion Audit",
        "",
        "Audit date: 2026-05-04",
        "",
        "## Objective",
        "",
        ACTIVE_OBJECTIVE,
        "",
        "## Completion Verdict",
        "",
        f"- Final-study ready: `{str(audit.get('final_study_ready', False)).lower()}`",
        f"- Verdict: `{audit.get('verdict', '')}`",
        f"- Ready gates: {len(ready_gate_ids)} / {audit.get('gate_count', 0)}",
        f"- Blocked gates: {len(blocked_gate_ids)} / {audit.get('gate_count', 0)}",
        "",
        NON_ACCEPTANCE_BOUNDARY,
        "",
        "## Concrete Success Criteria",
        "",
        "The active objective is complete only when every final-study gate below is ready, every acceptance artifact is reviewed, and the final audit gate confirms that no proxy signal was treated as completion.",
        "",
        "## Prompt-To-Artifact Checklist",
        "",
        "| Gate | Current Status | Evidence Inspected | Missing Or Weak Requirement |",
        "| --- | --- | --- | --- |",
    ]
    for gate in audit.get("gates", []):
        lines.append(_gate_table_row(gate))

    lines.extend(
        [
            "",
            "## Named Acceptance Artifacts",
            "",
            "These files are required before final completion can be claimed. Missing files are expected in the current scaffold unless a reviewed acceptance decision has been made.",
            "",
            "| Artifact | Current State |",
            "| --- | --- |",
        ]
    )
    for relative_path in FINAL_ACCEPTANCE_ARTIFACTS:
        exists = (PROJECT_ROOT / relative_path).exists()
        state = "present" if exists else "missing or intentionally absent"
        lines.append(f"| `{relative_path}` | {state} |")

    lines.extend(
        [
            "",
            "## Sub-Agent Acceptance Orchestration",
            "",
            "The orchestration records below are review aids. They do not replace formal acceptance artifacts and cannot mark the final study complete by themselves.",
            "",
            f"- Manifest present: `{str(orchestration.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{orchestration.get('path', '')}`",
            f"- Review record count: {orchestration.get('record_count', 0)}",
            f"- Status counts: `{orchestration.get('status_counts', {})}`",
            f"- Can-mark-complete records: {orchestration.get('can_mark_complete_count', 0)}",
            f"- Blocked or human-review records: {orchestration.get('blocked_or_review_record_count', 0)}",
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Acceptance Decision Templates",
            "",
            "The generated templates are copy/edit worksheets for reviewers. They intentionally keep `accepted: false` and do not replace the formal acceptance artifacts listed above.",
            "",
            f"- Manifest present: `{str(decision_templates.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{decision_templates.get('path', '')}`",
            f"- JSON template count: {decision_templates.get('json_template_count', 0)}",
            f"- Parameter template rows: {decision_templates.get('parameter_template_row_count', 0)}",
            f"- Can mark complete: `{str(decision_templates.get('can_mark_complete', False)).lower()}`",
            f"- Formal acceptance created: `{str(decision_templates.get('formal_acceptance_created', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Human Acceptance Runbook",
            "",
            "`docs/human_acceptance_runbook.md` gives reviewers the gate-by-gate workflow for inspecting review packets, converting non-approval templates into formal artifacts only after source-backed decisions, and rerunning package audits. It is instructional only and does not close any gate.",
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Acceptance Blocker Queue",
            "",
            "The blocker queue converts the formal package blockers into one CSV row per unresolved reviewer action. It is a work queue only and cannot close any gate.",
            "",
            f"- Manifest present: `{str(blocker_queue.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{blocker_queue.get('path', '')}`",
            f"- Queue rows: {blocker_queue.get('row_count', 0)}",
            f"- Formal acceptance ready: `{str(blocker_queue.get('formal_acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(blocker_queue.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Acceptance Task Assignments",
            "",
            "The task assignment table maps each unresolved formal blocker to a deterministic review-agent role. It is a work-assignment aid only and cannot approve evidence or close any gate.",
            "",
            f"- Manifest present: `{str(task_assignments.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{task_assignments.get('path', '')}`",
            f"- Task rows: {task_assignments.get('task_count', 0)}",
            f"- Assigned agents: {task_assignments.get('assigned_agent_count', 0)}",
            f"- Human-review tasks: {task_assignments.get('requires_human_review_count', 0)}",
            f"- Formal acceptance ready: `{str(task_assignments.get('formal_acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(task_assignments.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Acceptance Evidence Matrix",
            "",
            "The evidence matrix joins each required formal target with its assigned review agent, template or worksheet, review packets, current blockers, and validation command. It is an intake index only and cannot approve evidence or close any gate.",
            "",
            f"- Manifest present: `{str(evidence_matrix.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{evidence_matrix.get('path', '')}`",
            f"- Matrix rows: {evidence_matrix.get('row_count', 0)}",
            f"- Formal gates: {evidence_matrix.get('formal_gate_count', 0)}",
            f"- Human decisions required: {evidence_matrix.get('human_decision_required_count', 0)}",
            f"- Formal acceptance ready: `{str(evidence_matrix.get('formal_acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(evidence_matrix.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Acceptance Pre-Review",
            "",
            "The pre-review package classifies each remaining formal target as a draft recommendation for human reviewers. It is deliberately stored under `data/manifests/draft_acceptance/` and cannot approve evidence or close any gate.",
            "",
            f"- Manifest present: `{str(pre_review.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{pre_review.get('path', '')}`",
            f"- Draft records: {pre_review.get('record_count', 0)}",
            f"- Recommendation counts: `{pre_review.get('recommendation_counts', {})}`",
            f"- Human decisions required: {pre_review.get('human_decision_required_count', 0)}",
            f"- Formal approval made: `{str(pre_review.get('formal_approval', False)).lower()}`",
            f"- Final-study ready: `{str(pre_review.get('final_study_ready', False)).lower()}`",
            f"- Can mark complete: `{str(pre_review.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Agent Review Path Hygiene",
            "",
            "This audit checks whether sub-agent records cite existing local review inputs or explicit formal acceptance targets. It is path hygiene only and cannot approve any gate.",
            "",
            f"- Review records: {agent_review_paths.get('record_count', 0)}",
            f"- Missing required paths: {agent_review_paths.get('missing_required_path_count', 0)}",
            f"- Missing formal targets: {agent_review_paths.get('missing_formal_target_count', 0)}",
            f"- Agent review paths ready: `{str(agent_review_paths.get('agent_review_paths_ready', False)).lower()}`",
            f"- Can mark complete: `{str(agent_review_paths.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Acceptance Artifact Guard",
            "",
            "The guard checks that formal acceptance paths do not contain copied templates, placeholders, draft overrides, or current-state audit text masquerading as final approval.",
            "",
            f"- Formal artifact count: {formal_guard.get('artifact_count', 0)}",
            f"- Present formal artifacts: {formal_guard.get('present_count', 0)}",
            f"- Missing formal artifacts: {formal_guard.get('missing_count', 0)}",
            f"- Template or placeholder artifacts detected: {formal_guard.get('template_or_placeholder_count', 0)}",
            f"- Formal acceptance ready: `{str(formal_guard.get('formal_acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(formal_guard.get('can_mark_complete', False)).lower()}`",
            "",
            formal_guard.get("claim_boundary", ""),
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Evidence Path Hygiene",
            "",
            "The evidence-path audit checks reviewer-supplied formal artifacts for missing local evidence, unresolved placeholders, empty evidence records, and external references that still require source/license review. It is necessary hygiene only and cannot certify evidence sufficiency.",
            "",
            f"- Formal artifact paths checked: {formal_evidence_paths.get('artifact_count', 0)}",
            f"- Present formal artifacts checked: {formal_evidence_paths.get('present_artifact_count', 0)}",
            f"- Evidence items found: {formal_evidence_paths.get('evidence_item_count', 0)}",
            f"- Missing local evidence paths: {formal_evidence_paths.get('missing_local_evidence_count', 0)}",
            f"- Placeholder evidence values: {formal_evidence_paths.get('placeholder_evidence_count', 0)}",
            f"- Empty evidence records: {formal_evidence_paths.get('empty_evidence_record_count', 0)}",
            f"- Formal evidence paths ready: `{str(formal_evidence_paths.get('formal_evidence_paths_ready', False)).lower()}`",
            f"- Can mark complete: `{str(formal_evidence_paths.get('can_mark_complete', False)).lower()}`",
            "",
            formal_evidence_paths.get("claim_boundary", ""),
            "",
        ]
    )

    lines.extend(
        [
            "## Formal Acceptance Package Intake",
            "",
            "The package intake validates reviewer-supplied formal acceptance artifacts as a group. It does not create approvals and cannot override missing source-backed evidence.",
            "",
            f"- Formal package gates: {formal_package.get('gate_count', 0)}",
            f"- Ready formal package gates: {formal_package.get('ready_gate_count', 0)}",
            f"- Blocked formal package gates: {formal_package.get('blocked_gate_count', 0)}",
            f"- Invalid formal package gates: {formal_package.get('invalid_gate_count', 0)}",
            f"- Formal package ready: `{str(formal_package.get('formal_acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(formal_package.get('can_mark_complete', False)).lower()}`",
            "",
            formal_package.get("claim_boundary", ""),
            "",
        ]
    )

    lines.extend(
        [
            "## Current-Worktree Reproducibility Smoke",
            "",
            "The smoke manifest records bounded validation commands run in the current worktree. It is useful execution evidence, but it is not clean-checkout reproduction and cannot close the reproducibility gate.",
            "",
            f"- Manifest present: `{str(reproducibility_smoke.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{reproducibility_smoke.get('path', '')}`",
            f"- Result scope: `{reproducibility_smoke.get('result_scope', '')}`",
            f"- Commands passed: {reproducibility_smoke.get('passed_count', 0)} / {reproducibility_smoke.get('command_count', 0)}",
            f"- Smoke passed: `{str(reproducibility_smoke.get('smoke_passed', False)).lower()}`",
            f"- Clean checkout tested: `{str(reproducibility_smoke.get('clean_checkout_test_performed', False)).lower()}`",
            f"- Can mark complete: `{str(reproducibility_smoke.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Bounded Clean-Checkout Smoke",
            "",
            "This smoke manifest records a fresh clone of the committed source tree and a minimal evidence profile run with the current Python environment. It is useful source-checkout evidence, but it is not a clean-environment dependency reinstall, full artifact-regeneration run, or formal reproducibility acceptance.",
            "",
            f"- Manifest present: `{str(clean_checkout_smoke.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{clean_checkout_smoke.get('path', '')}`",
            f"- Result scope: `{clean_checkout_smoke.get('result_scope', '')}`",
            f"- Commands passed: {clean_checkout_smoke.get('passed_count', 0)} / {clean_checkout_smoke.get('command_count', 0)}",
            f"- Smoke passed: `{str(clean_checkout_smoke.get('smoke_passed', False)).lower()}`",
            f"- Clean checkout tested: `{str(clean_checkout_smoke.get('clean_checkout_test_performed', False)).lower()}`",
            f"- Full clean environment tested: `{str(clean_checkout_smoke.get('full_clean_environment_tested', False)).lower()}`",
            f"- Can mark complete: `{str(clean_checkout_smoke.get('can_mark_complete', False)).lower()}`",
            "",
            "## Tracked Artifact Packaging Audit",
            "",
            "This audit lists changed reproducibility artifacts that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded. It is packaging hygiene only and cannot close the reproducibility gate.",
            "",
            f"- Manifest present: `{str(tracked_artifacts.get('manifest_present', False)).lower()}`",
            f"- Manifest path: `{tracked_artifacts.get('path', '')}`",
            f"- Changed reproducibility artifacts: {tracked_artifacts.get('row_count', 0)}",
            f"- Blocking changed artifacts: {tracked_artifacts.get('blocking_change_count', 0)}",
            f"- Untracked artifacts: {tracked_artifacts.get('untracked_count', 0)}",
            f"- Modified or staged artifacts: {tracked_artifacts.get('modified_or_staged_count', 0)}",
            f"- Clean-checkout reproducibility ready: `{str(tracked_artifacts.get('clean_checkout_reproducibility_ready', False)).lower()}`",
            f"- Can mark complete: `{str(tracked_artifacts.get('can_mark_complete', False)).lower()}`",
            "",
        ]
    )

    lines.extend(
        [
            "",
            "## Proxy Signals Rejected",
            "",
            "- Passing tests are necessary but do not close evidence, review, acceptance, or calibration gates.",
            "- Generated CSV, JSON, figure, and report artifacts are scaffold evidence unless their claim scope is accepted.",
            "- OSRM and fallback router checks are plausibility snapshots, not ground truth.",
            "- OSM-derived road data are not by themselves calibrated traffic, capacity, or disruption evidence.",
            "- The regenerated Korean report and English paper draft must stay in scaffold scope until manuscript acceptance is reviewed.",
            "",
            "## Commands To Re-Run Before Final Completion",
            "",
            "```powershell",
            ".\\.venv\\Scripts\\python scripts\\audit_plan_artifacts.py",
            ".\\.venv\\Scripts\\python scripts\\run_acceptance_audit.py",
            ".\\.venv\\Scripts\\python scripts\\run_acceptance_audit.py --live-source-url-checks --source-url-timeout-sec 12",
            ".\\.venv\\Scripts\\python scripts\\write_source_url_remediation_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_rail_fetch_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_source_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_acceptance_task_assignments.py",
            ".\\.venv\\Scripts\\python scripts\\write_formal_acceptance_evidence_matrix.py",
            ".\\.venv\\Scripts\\python scripts\\write_formal_acceptance_pre_review.py",
            ".\\.venv\\Scripts\\python scripts\\audit_agent_review_paths.py",
            ".\\.venv\\Scripts\\python scripts\\audit_tracked_artifacts.py",
            ".\\.venv\\Scripts\\python scripts\\audit_formal_acceptance_artifacts.py",
            ".\\.venv\\Scripts\\python scripts\\audit_formal_evidence_paths.py",
            ".\\.venv\\Scripts\\python scripts\\validate_formal_acceptance_package.py --fail-on-blockers",
            ".\\.venv\\Scripts\\python scripts\\run_reproducibility_smoke.py",
            ".\\.venv\\Scripts\\python scripts\\run_clean_checkout_smoke.py",
            ".\\.venv\\Scripts\\python scripts\\audit_publication_readiness.py --fail-on-blockers",
            ".\\.venv\\Scripts\\python scripts\\audit_final_study_readiness.py --fail-on-blockers",
            "Get-ChildItem tests\\test_*.py | ForEach-Object { .\\.venv\\Scripts\\python $_.FullName }",
            "rg -n \"(^|\\s)(from|import)\\s+cloned_repo\" src tests scripts",
            "git diff --check",
            "```",
            "",
            "## Next Required Input",
            "",
            "The remaining work cannot be honestly completed by code alone. It requires reviewed pilot, provenance, graph-scale, road, rail, parameter, validation, sensitivity, experiment, manuscript, reproducibility, and final-audit acceptance decisions.",
            "",
        ]
    )
    return "\n".join(lines)


def write_goal_completion_audit(
    path: Path = DEFAULT_GOAL_COMPLETION_AUDIT_PATH,
) -> dict[str, Any]:
    """Write the current goal-completion audit and return the source audit."""

    audit = audit_final_study_readiness()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_goal_completion_audit_markdown(audit), encoding="utf-8")
    return audit


def _gate_table_row(gate: dict[str, Any]) -> str:
    label = _cell_text(str(gate.get("label", gate.get("gate_id", ""))))
    status = "ready" if gate.get("ready") else "blocked"
    evidence = _summarize_list(gate.get("evidence", []), max_items=4)
    blockers = _summarize_list(gate.get("blockers", []), max_items=3)
    if not blockers:
        blockers = "none for current gate scope"
    return f"| {label} | {status} | {evidence} | {blockers} |"


def _summarize_list(items: object, *, max_items: int) -> str:
    if not isinstance(items, list) or not items:
        return "none recorded"
    rendered = [_cell_text(str(item)) for item in items[:max_items]]
    if len(items) > max_items:
        rendered.append(f"+{len(items) - max_items} more")
    return "<br>".join(rendered)


def _cell_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


__all__ = [
    "ACTIVE_OBJECTIVE",
    "DEFAULT_GOAL_COMPLETION_AUDIT_PATH",
    "FINAL_ACCEPTANCE_ARTIFACTS",
    "NON_ACCEPTANCE_BOUNDARY",
    "build_goal_completion_audit_markdown",
    "write_goal_completion_audit",
]
