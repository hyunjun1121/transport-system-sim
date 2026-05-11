"""Generate a non-acceptance completion audit for the active plan goal."""

from __future__ import annotations

from datetime import datetime, timezone
import json
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
from src.realworld.review_package_handoff import build_expert_review_handoff_summary
from src.realworld.review_package_path_audit import audit_review_package_paths
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
from src.realworld.experiment_statistical_plan import (
    DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH,
)
from src.realworld.deterministic_rerun_audit import (
    DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GOAL_COMPLETION_AUDIT_PATH = (
    PROJECT_ROOT / "docs" / "current_goal_completion_audit.md"
)
DEFAULT_GOAL_COMPLETION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "current_goal_completion_audit.json"
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
    review_package_paths = audit_review_package_paths()
    review_handoff = build_expert_review_handoff_summary()
    formal_guard = audit_formal_acceptance_artifacts()
    formal_evidence_paths = audit_formal_evidence_paths()
    formal_package = build_formal_acceptance_package_summary()
    experiment_statistical_plan = _read_json_object(
        DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH
    )
    deterministic_rerun = _read_json_object(
        DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST
    )
    reproducibility_smoke = summarize_reproducibility_smoke()
    clean_checkout_smoke = summarize_clean_checkout_smoke()
    tracked_artifacts = summarize_tracked_artifact_audit()
    ready_gate_ids = list(audit.get("ready_gate_ids", []))
    blocked_gate_ids = list(audit.get("blocked_gate_ids", []))
    audit_date = datetime.now(timezone.utc).date().isoformat()
    lines: list[str] = [
        "# Current Goal Completion Audit",
        "",
        f"Audit date: {audit_date}",
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

    region_scope_rows = _region_scope_rows(audit)
    lines.extend(
        [
            "",
            "## Region-Scope Review Metadata",
            "",
            "These rows copy region-scope metadata from final-study gate details. They help detect mixed-region review packets, but they do not approve a region, source, or acceptance gate.",
            "",
            "| Gate | Source-Readiness Region IDs |",
            "| --- | --- |",
            *region_scope_rows,
            "",
        ]
    )

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
            "## Review Package Path Hygiene",
            "",
            "This audit opens `required_deliverables.zip` and checks that packaged sub-agent review records do not cite missing non-formal local paths. It is package hygiene only and cannot approve any gate.",
            "",
            f"- ZIP present: `{str(review_package_paths.get('zip_present', False)).lower()}`",
            f"- ZIP valid: `{str(review_package_paths.get('zip_valid', False)).lower()}`",
            f"- ZIP file count: {review_package_paths.get('zip_file_count', 0)}",
            f"- Review records in ZIP: {review_package_paths.get('record_count', 0)}",
            f"- Path references in ZIP records: {review_package_paths.get('path_reference_count', 0)}",
            f"- Missing package paths: {review_package_paths.get('missing_package_path_count', 0)}",
            f"- Missing formal targets: {review_package_paths.get('missing_formal_target_count', 0)}",
            f"- Review package paths ready: `{str(review_package_paths.get('review_package_paths_ready', False)).lower()}`",
            f"- Can mark complete: `{str(review_package_paths.get('can_mark_complete', False)).lower()}`",
            "",
            review_package_paths.get("claim_boundary", ""),
            "",
        ]
    )

    handoff_zip = review_handoff.get("zip", {})
    handoff_mirror = review_handoff.get("mirror_zip", {})
    handoff_formal = review_handoff.get("formal_status", {})
    lines.extend(
        [
            "## Expert Review Handoff",
            "",
            "The handoff sidecar records the final ZIP checksum and send-list outside the ZIP so checksum reporting does not mutate the reviewed package. It is review logistics only and cannot approve any gate.",
            "",
            f"- ZIP path: `{handoff_zip.get('path', '')}`",
            f"- ZIP file count: {handoff_zip.get('file_count', 0)}",
            "- ZIP SHA256: recorded in `review_packages/expert_review_handoff_20260510.md` and `review_packages/expert_review_handoff_20260510.json` outside the ZIP",
            f"- Mirror ZIP matches: `{str(handoff_mirror.get('matches_zip', False)).lower()}`",
            f"- Formal acceptance ready: `{str(handoff_formal.get('formal_acceptance_ready', False)).lower()}`",
            f"- Missing formal targets: {handoff_formal.get('missing_formal_target_count', 0)} / {handoff_formal.get('formal_target_count', 0)}",
            f"- Can mark complete: `{str(review_handoff.get('can_mark_complete', False)).lower()}`",
            "",
            review_handoff.get("claim_boundary", ""),
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
            "## Experiment Statistical Analysis Plan",
            "",
            "The statistical-analysis plan records the current scenario-policy-seed design, candidate primary metrics, candidate primary policy contrast, CRN review dependencies, replication adequacy review items, and multiple-comparison boundary. It is planning evidence only and cannot accept experiment outputs.",
            "",
            f"- Manifest present: `{str(bool(experiment_statistical_plan)).lower()}`",
            f"- Manifest path: `{_display_path(DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH)}`",
            f"- Selected profile: `{experiment_statistical_plan.get('selected_profile_id', '')}`",
            f"- Statistical plan ready for review: `{str(experiment_statistical_plan.get('statistical_plan_ready_for_review', False)).lower()}`",
            f"- Blocking checks: {experiment_statistical_plan.get('blocking_check_count', 0)}",
            f"- Human-review checks: {experiment_statistical_plan.get('needs_human_review_count', 0)}",
            f"- Acceptance ready: `{str(experiment_statistical_plan.get('acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(experiment_statistical_plan.get('can_mark_complete', False)).lower()}`",
            "",
            experiment_statistical_plan.get("claim_boundary", ""),
            "",
        ]
    )

    lines.extend(
        [
            "## Deterministic Rerun Audit",
            "",
            "The deterministic rerun audit executes a bounded pilot profile twice with identical inputs and compares canonical result and summary hashes. It is repeatability support only and cannot accept CRN design or experiment outputs.",
            "",
            f"- Manifest present: `{str(bool(deterministic_rerun)).lower()}`",
            f"- Manifest path: `{_display_path(DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST)}`",
            f"- Deterministic rerun structurally ready: `{str(deterministic_rerun.get('deterministic_rerun_structurally_ready', False)).lower()}`",
            f"- Row hashes match: `{str(deterministic_rerun.get('row_hashes_match', False)).lower()}`",
            f"- Summary hashes match: `{str(deterministic_rerun.get('summary_hashes_match', False)).lower()}`",
            f"- Blocking checks: {deterministic_rerun.get('blocking_check_count', 0)}",
            f"- Deterministic blocking checks: {deterministic_rerun.get('deterministic_blocking_check_count', 0)}",
            f"- Human-review checks: {deterministic_rerun.get('needs_human_review_count', 0)}",
            f"- Acceptance ready: `{str(deterministic_rerun.get('acceptance_ready', False)).lower()}`",
            f"- Can mark complete: `{str(deterministic_rerun.get('can_mark_complete', False)).lower()}`",
            "",
            deterministic_rerun.get("claim_boundary", ""),
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
            ".\\.venv\\Scripts\\python scripts\\audit_source_provenance.py",
            ".\\.venv\\Scripts\\python scripts\\write_source_license_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_source_url_review_packet.py --preserve-existing-live",
            ".\\.venv\\Scripts\\python scripts\\write_source_url_remediation_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_source_provenance_priority_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_source_context_cache_request_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_source_context_cache_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\audit_rail_evidence.py",
            ".\\.venv\\Scripts\\python scripts\\write_rail_evidence_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_rail_timing_source_request_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_rail_fetch_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_rail_evidence_priority_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_rail_source_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\audit_rail_station_bindings.py",
            ".\\.venv\\Scripts\\python scripts\\audit_road_evidence.py",
            ".\\.venv\\Scripts\\python scripts\\audit_road_evidence_diagnostics.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_capacity_evidence.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_speed_evidence.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_evidence_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_evidence_source_request_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_source_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_evidence_priority_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_source_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_road_class_override_template.py --output data\\parameters\\road_class_overrides_draft.csv --overwrite",
            ".\\.venv\\Scripts\\python scripts\\audit_parameter_evidence.py",
            ".\\.venv\\Scripts\\python scripts\\write_parameter_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_transfer_evidence_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_parameter_evidence_source_request_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_parameter_source_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_parameter_evidence_priority_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_parameter_source_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\run_full_graph_smoke.py",
            ".\\.venv\\Scripts\\python scripts\\run_graph_scale_diagnostics.py",
            ".\\.venv\\Scripts\\python scripts\\write_full_graph_runtime_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_graph_scale_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_graph_scale_strategy_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_graph_scale_method_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_graph_scale_result_comparison.py",
            ".\\.venv\\Scripts\\python scripts\\audit_graph_scale_manifests.py",
            ".\\.venv\\Scripts\\python scripts\\write_pilot_privacy_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_pilot_region_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_source_provenance_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\run_plausibility_validation.py",
            ".\\.venv\\Scripts\\python scripts\\run_accessibility_loss_analysis.py",
            ".\\.venv\\Scripts\\python scripts\\write_osrm_snapshot_manifest.py",
            ".\\.venv\\Scripts\\python scripts\\write_route_road_evidence_exposure.py",
            ".\\.venv\\Scripts\\python scripts\\write_osm_graph_snapshot_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_validation_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_validation_strategy_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_validation_benchmark_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_validation_benchmark_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_integrated_evidence_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --sample",
            ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --staged",
            ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --multi-corridor",
            ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --multi-corridor-full",
            ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --full",
            ".\\.venv\\Scripts\\python scripts\\run_sensitivity.py --sample",
            ".\\.venv\\Scripts\\python scripts\\run_sensitivity.py --method morris --all",
            ".\\.venv\\Scripts\\python scripts\\audit_sensitivity_diagnostics.py",
            ".\\.venv\\Scripts\\python scripts\\write_sensitivity_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_sensitivity_index_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_sensitivity_strategy_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_sensitivity_method_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_experiment_package_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_experiment_strategy_readiness_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_experiment_design_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_experiment_statistical_plan.py",
            ".\\.venv\\Scripts\\python scripts\\audit_deterministic_rerun.py",
            ".\\.venv\\Scripts\\python scripts\\make_pilot_statistics.py",
            ".\\.venv\\Scripts\\python scripts\\make_pilot_statistics.py --input results\\realworld_pilot\\pilot_multi_corridor_results.csv --source-manifest results\\realworld_pilot\\pilot_multi_corridor_manifest.json --output-prefix pilot_multi_corridor",
            ".\\.venv\\Scripts\\python scripts\\make_pilot_statistics.py --input results\\realworld_pilot\\pilot_multi_corridor_full_results.csv --source-manifest results\\realworld_pilot\\pilot_multi_corridor_full_manifest.json --output-prefix pilot_multi_corridor_full",
            ".\\.venv\\Scripts\\python scripts\\make_pilot_figures.py",
            ".\\.venv\\Scripts\\python scripts\\write_figure_table_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_claim_alignment_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_manuscript_report_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_reproducibility_review_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_reproducibility_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_final_audit_decision_packet.py",
            ".\\.venv\\Scripts\\python scripts\\write_acceptance_decision_templates.py",
            ".\\.venv\\Scripts\\python scripts\\write_formal_acceptance_blocker_queue.py",
            ".\\.venv\\Scripts\\python scripts\\write_acceptance_task_assignments.py",
            ".\\.venv\\Scripts\\python scripts\\write_formal_acceptance_evidence_matrix.py",
            ".\\.venv\\Scripts\\python scripts\\write_formal_acceptance_pre_review.py",
            ".\\.venv\\Scripts\\python scripts\\audit_agent_review_paths.py",
            ".\\.venv\\Scripts\\python scripts\\audit_review_package_paths.py --fail-on-missing",
            ".\\.venv\\Scripts\\python scripts\\write_expert_review_handoff.py --fail-on-zip-mismatch",
            ".\\.venv\\Scripts\\python scripts\\audit_tracked_artifacts.py",
            ".\\.venv\\Scripts\\python scripts\\audit_formal_acceptance_artifacts.py",
            ".\\.venv\\Scripts\\python scripts\\audit_formal_evidence_paths.py",
            ".\\.venv\\Scripts\\python scripts\\validate_formal_acceptance_package.py --fail-on-blockers",
            ".\\.venv\\Scripts\\python scripts\\run_reproducibility_smoke.py",
            ".\\.venv\\Scripts\\python scripts\\run_clean_checkout_smoke.py",
            ".\\.venv\\Scripts\\python scripts\\audit_publication_readiness.py --fail-on-blockers",
            ".\\.venv\\Scripts\\python scripts\\audit_final_study_readiness.py --fail-on-blockers",
            ".\\.venv\\Scripts\\python scripts\\write_goal_completion_audit.py",
            ".\\.venv\\Scripts\\python generate_report.py",
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


def build_goal_completion_audit_manifest(
    audit: dict[str, Any] | None = None,
    *,
    markdown_path: Path = DEFAULT_GOAL_COMPLETION_AUDIT_PATH,
    manifest_path: Path = DEFAULT_GOAL_COMPLETION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a machine-readable current-goal completion gap audit."""

    audit = audit or audit_final_study_readiness()
    review_package_paths = audit_review_package_paths()
    review_handoff = build_expert_review_handoff_summary()
    experiment_statistical_plan = _read_json_object(
        DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH
    )
    deterministic_rerun = _read_json_object(
        DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST
    )
    ready_gate_ids = list(audit.get("ready_gate_ids", []))
    blocked_gate_ids = list(audit.get("blocked_gate_ids", []))
    acceptance_artifacts = [
        {
            "path": relative_path,
            "present": (PROJECT_ROOT / relative_path).exists(),
        }
        for relative_path in FINAL_ACCEPTANCE_ARTIFACTS
    ]
    missing_acceptance_artifacts = [
        row["path"] for row in acceptance_artifacts if not row["present"]
    ]
    checklist = [_gate_checklist_item(gate) for gate in audit.get("gates", [])]
    return {
        "schema_version": 1,
        "audit_date": datetime.now(timezone.utc).date().isoformat(),
        "objective": ACTIVE_OBJECTIVE,
        "result_scope": (
            "current_goal_completion_gap_audit_not_final_acceptance"
        ),
        "claim_boundary": NON_ACCEPTANCE_BOUNDARY,
        "outputs": {
            "markdown": _display_path(markdown_path),
            "manifest": _display_path(manifest_path),
        },
        "final_study_ready": bool(audit.get("final_study_ready", False)),
        "verdict": audit.get("verdict", ""),
        "gate_count": audit.get("gate_count", 0),
        "ready_gate_count": len(ready_gate_ids),
        "blocked_gate_count": len(blocked_gate_ids),
        "status_counts": {
            "blocked": len(blocked_gate_ids),
            "missing_acceptance_artifact": len(missing_acceptance_artifacts),
            "ready": len(ready_gate_ids),
        },
        "ready_gate_ids": ready_gate_ids,
        "blocked_gate_ids": blocked_gate_ids,
        "prompt_to_artifact_checklist": checklist,
        "named_acceptance_artifacts": acceptance_artifacts,
        "present_acceptance_artifact_count": (
            len(acceptance_artifacts) - len(missing_acceptance_artifacts)
        ),
        "missing_acceptance_artifact_count": len(missing_acceptance_artifacts),
        "missing_acceptance_artifacts": missing_acceptance_artifacts,
        "review_package_path_audit": {
            "zip_present": review_package_paths.get("zip_present", False),
            "zip_valid": review_package_paths.get("zip_valid", False),
            "zip_file_count": review_package_paths.get("zip_file_count", 0),
            "record_count": review_package_paths.get("record_count", 0),
            "path_reference_count": review_package_paths.get(
                "path_reference_count", 0
            ),
            "missing_package_path_count": review_package_paths.get(
                "missing_package_path_count", 0
            ),
            "missing_formal_target_count": review_package_paths.get(
                "missing_formal_target_count", 0
            ),
            "review_package_paths_ready": review_package_paths.get(
                "review_package_paths_ready", False
            ),
            "can_mark_complete": review_package_paths.get(
                "can_mark_complete", False
            ),
        },
        "expert_review_handoff": {
            "zip_path": review_handoff.get("zip", {}).get("path", ""),
            "zip_file_count": review_handoff.get("zip", {}).get("file_count", 0),
            "zip_sha256_location": (
                "review_packages/expert_review_handoff_20260510.md"
            ),
            "handoff_manifest_location": (
                "review_packages/expert_review_handoff_20260510.json"
            ),
            "mirror_zip_matches": review_handoff.get("mirror_zip", {}).get(
                "matches_zip", False
            ),
            "missing_formal_target_count": review_handoff.get(
                "formal_status", {}
            ).get("missing_formal_target_count", 0),
            "formal_target_count": review_handoff.get("formal_status", {}).get(
                "formal_target_count", 0
            ),
            "can_mark_complete": review_handoff.get("can_mark_complete", False),
        },
        "experiment_statistical_analysis_plan": {
            "manifest_present": bool(experiment_statistical_plan),
            "path": _display_path(DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH),
            "selected_profile_id": experiment_statistical_plan.get(
                "selected_profile_id", ""
            ),
            "statistical_plan_ready_for_review": experiment_statistical_plan.get(
                "statistical_plan_ready_for_review", False
            ),
            "blocking_check_count": experiment_statistical_plan.get(
                "blocking_check_count", 0
            ),
            "needs_human_review_count": experiment_statistical_plan.get(
                "needs_human_review_count", 0
            ),
            "acceptance_ready": experiment_statistical_plan.get(
                "acceptance_ready", False
            ),
            "can_mark_complete": experiment_statistical_plan.get(
                "can_mark_complete", False
            ),
        },
        "deterministic_rerun_audit": {
            "manifest_present": bool(deterministic_rerun),
            "path": _display_path(DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST),
            "deterministic_rerun_structurally_ready": deterministic_rerun.get(
                "deterministic_rerun_structurally_ready", False
            ),
            "row_hashes_match": deterministic_rerun.get("row_hashes_match", False),
            "summary_hashes_match": deterministic_rerun.get(
                "summary_hashes_match", False
            ),
            "blocking_check_count": deterministic_rerun.get(
                "blocking_check_count", 0
            ),
            "deterministic_blocking_check_count": deterministic_rerun.get(
                "deterministic_blocking_check_count", 0
            ),
            "needs_human_review_count": deterministic_rerun.get(
                "needs_human_review_count", 0
            ),
            "acceptance_ready": deterministic_rerun.get("acceptance_ready", False),
            "can_mark_complete": deterministic_rerun.get(
                "can_mark_complete", False
            ),
        },
        "proxy_signals_rejected": [
            "passing tests do not close evidence, review, acceptance, or calibration gates",
            "generated CSV, JSON, figure, and report artifacts remain scaffold evidence unless accepted",
            "OSRM and fallback router checks are plausibility snapshots, not ground truth",
            "OSM-derived road data are not calibrated traffic, capacity, or disruption evidence by themselves",
            "paper and report drafts remain scaffold scope until manuscript acceptance is reviewed",
        ],
        "next_required_input": (
            "reviewed pilot, provenance, graph-scale, road, rail, parameter, "
            "validation, sensitivity, experiment, manuscript, reproducibility, "
            "and final-audit acceptance decisions"
        ),
        "can_mark_complete": bool(audit.get("final_study_ready", False))
        and not blocked_gate_ids
        and not missing_acceptance_artifacts,
    }


def write_goal_completion_audit(
    path: Path = DEFAULT_GOAL_COMPLETION_AUDIT_PATH,
    manifest_path: Path = DEFAULT_GOAL_COMPLETION_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write the current goal-completion audit and return the source audit."""

    audit = audit_final_study_readiness()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_goal_completion_audit_markdown(audit), encoding="utf-8")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            build_goal_completion_audit_manifest(
                audit,
                markdown_path=path,
                manifest_path=manifest_path,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return audit


def _read_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    try:
        value = json.loads(filepath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _gate_checklist_item(gate: dict[str, Any]) -> dict[str, Any]:
    gate_id = str(gate.get("gate_id", ""))
    ready = bool(gate.get("ready", False))
    evidence = gate.get("evidence", [])
    blockers = gate.get("blockers", [])
    return {
        "gate_id": gate_id,
        "label": str(gate.get("label", gate_id)),
        "current_status": "ready" if ready else "blocked",
        "ready": ready,
        "evidence_inspected": evidence if isinstance(evidence, list) else [],
        "missing_or_weak_requirements": (
            blockers if isinstance(blockers, list) else []
        ),
    }


def _gate_table_row(gate: dict[str, Any]) -> str:
    label = _cell_text(str(gate.get("label", gate.get("gate_id", ""))))
    status = "ready" if gate.get("ready") else "blocked"
    evidence = _summarize_list(gate.get("evidence", []), max_items=4)
    blockers = _summarize_list(gate.get("blockers", []), max_items=3)
    if not blockers:
        blockers = "none for current gate scope"
    return f"| {label} | {status} | {evidence} | {blockers} |"


def _region_scope_rows(audit: dict[str, Any]) -> list[str]:
    fields = {
        "cached_osm_input": "source_readiness_region_ids",
        "parameter_evidence": "source_readiness_region_ids",
        "rail_evidence": "fetch_readiness_region_ids",
    }
    labels = {
        str(gate.get("gate_id", "")): str(gate.get("label", gate.get("gate_id", "")))
        for gate in audit.get("gates", [])
        if isinstance(gate, dict)
    }
    details = {
        str(gate.get("gate_id", "")): gate.get("details", {})
        for gate in audit.get("gates", [])
        if isinstance(gate, dict)
    }
    rows: list[str] = []
    for gate_id, field in fields.items():
        value = details.get(gate_id, {})
        region_ids = value.get(field, []) if isinstance(value, dict) else []
        rows.append(
            "| {gate} | {regions} |".format(
                gate=_cell_text(labels.get(gate_id, gate_id)),
                regions=_summarize_list(region_ids, max_items=4),
            )
        )
    return rows


def _summarize_list(items: object, *, max_items: int) -> str:
    if not isinstance(items, list) or not items:
        return "none recorded"
    rendered = [_cell_text(str(item)) for item in items[:max_items]]
    if len(items) > max_items:
        rendered.append(f"+{len(items) - max_items} more")
    return "<br>".join(rendered)


def _cell_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


__all__ = [
    "ACTIVE_OBJECTIVE",
    "DEFAULT_GOAL_COMPLETION_AUDIT_PATH",
    "DEFAULT_GOAL_COMPLETION_MANIFEST_PATH",
    "FINAL_ACCEPTANCE_ARTIFACTS",
    "NON_ACCEPTANCE_BOUNDARY",
    "build_goal_completion_audit_manifest",
    "build_goal_completion_audit_markdown",
    "write_goal_completion_audit",
]
