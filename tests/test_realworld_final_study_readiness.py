"""Tests for plan-level final-study readiness auditing."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.final_study_readiness import (  # noqa: E402
    FINAL_GATE_IDS,
    _data_provenance_gate,
    _experiment_count_blockers,
    _experiment_scope_is_blocked,
    _final_audit_count_blockers,
    _final_audit_gate,
    _full_experiment_gate,
    _graph_scale_gate,
    _manuscript_report_gate,
    _reproducibility_count_blockers,
    _reproducibility_gate,
    _sensitivity_count_blockers,
    _sensitivity_gate,
    _sensitivity_scope_is_blocked,
    _validation_gate,
    _validation_summary_scope_is_blocked,
    audit_final_study_readiness,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT_PATH = ROOT / "scripts" / "audit_final_study_readiness.py"


def test_current_final_study_readiness_is_blocked() -> None:
    """The current scaffold must not satisfy final plan gates."""

    summary = audit_final_study_readiness()
    gate_map = {gate["gate_id"]: gate for gate in summary["gates"]}

    assert summary["final_study_ready"] is False
    assert summary["verdict"] == "final_real_world_study_blocked"
    assert summary["gate_count"] == len(FINAL_GATE_IDS)
    assert summary["missing_gate_ids"] == []
    assert set(gate_map) == set(FINAL_GATE_IDS)
    assert gate_map["structured_disruptions"]["ready"] is True
    assert gate_map["policy_alternatives"]["ready"] is True
    assert gate_map["real_input_smoke"]["ready"] is True
    assert gate_map["pilot_region_accepted"]["ready"] is False
    assert (
        gate_map["cached_osm_input"]["details"][
            "source_readiness_source_url_or_citation_present_count"
        ]
        == 5
    )
    assert (
        gate_map["cached_osm_input"]["details"][
            "source_readiness_required_external_input_present_count"
        ]
        == 5
    )
    assert gate_map["cached_osm_input"]["details"][
        "source_readiness_region_ids"
    ] == ["songpa_public_demo"]
    assert any(
        "road source readiness: reviewed road_class_overrides.csv is absent"
        in item
        for item in gate_map["cached_osm_input"]["blockers"]
    )
    assert gate_map["graph_scale_strategy"]["ready"] is False
    assert any(
        "graph_scale_acceptance.json is absent" in item
        for item in gate_map["graph_scale_strategy"]["details"][
            "strategy_readiness_remaining_blockers"
        ]
    )
    assert any(
        "graph-scale strategy readiness: graph_scale_acceptance.json is absent"
        in item
        for item in gate_map["graph_scale_strategy"]["blockers"]
    )
    assert gate_map["parameter_evidence"]["ready"] is False
    assert (
        gate_map["parameter_evidence"]["details"][
            "source_readiness_source_url_or_citation_present_count"
        ]
        == 6
    )
    assert (
        gate_map["parameter_evidence"]["details"][
            "source_readiness_required_external_input_present_count"
        ]
        == 6
    )
    assert gate_map["parameter_evidence"]["details"][
        "source_readiness_region_ids"
    ] == ["songpa_public_demo"]
    assert (
        gate_map["parameter_evidence"]["details"][
            "parameter_evidence_priority_artifacts_present"
        ]
        is True
    )
    assert (
        gate_map["parameter_evidence"]["details"][
            "parameter_evidence_priority_row_count"
        ]
        == 6
    )
    assert (
        gate_map["parameter_evidence"]["details"][
            "parameter_evidence_priority_blocking_priority_count"
        ]
        == 1
    )
    assert (
        gate_map["parameter_evidence"]["details"][
            "parameter_evidence_priority_high_priority_parameter_count"
        ]
        == 6
    )
    assert (
        gate_map["parameter_evidence"]["details"][
            "parameter_evidence_priority_medium_priority_parameter_count"
        ]
        == 14
    )
    assert any(
        "parameter source readiness: all rows require human review" in item
        for item in gate_map["parameter_evidence"]["blockers"]
    )
    assert any(
        "parameter evidence priority: transfer-delay source evidence is absent"
        in item
        for item in gate_map["parameter_evidence"]["blockers"]
    )
    assert gate_map["rail_evidence"]["ready"] is False
    assert (
        gate_map["rail_evidence"]["details"][
            "fetch_readiness_source_url_or_citation_present_count"
        ]
        == 5
    )
    assert (
        gate_map["rail_evidence"]["details"][
            "fetch_readiness_required_external_input_present_count"
        ]
        == 5
    )
    assert gate_map["rail_evidence"]["details"]["fetch_readiness_region_ids"] == [
        "songpa_public_demo"
    ]
    assert (
        gate_map["rail_evidence"]["details"][
            "rail_evidence_priority_artifacts_present"
        ]
        is True
    )
    assert (
        gate_map["rail_evidence"]["details"]["rail_evidence_priority_row_count"] == 6
    )
    assert (
        gate_map["rail_evidence"]["details"][
            "rail_evidence_priority_blocking_priority_count"
        ]
        == 3
    )
    assert (
        gate_map["rail_evidence"]["details"][
            "rail_evidence_priority_human_review_priority_count"
        ]
        == 2
    )
    assert (
        gate_map["rail_evidence"]["details"][
            "rail_evidence_priority_timing_closure_candidate_count"
        ]
        == 1
    )
    assert any(
        "reviewed-GTFS rows require external reviewer-provided inputs" in item
        for item in gate_map["rail_evidence"]["details"][
            "fetch_readiness_remaining_blockers"
        ]
    )
    assert any(
        "rail timing cache files are absent" in item
        for item in gate_map["rail_evidence"]["blockers"]
    )
    assert any(
        "rail fetch readiness: API-key and reviewed-GTFS rows require external"
        in item
        for item in gate_map["rail_evidence"]["blockers"]
    )
    assert gate_map["validation_package"]["ready"] is False
    assert gate_map["validation_package"]["details"]["review_packet_row_count"] == 7
    assert (
        gate_map["validation_package"]["details"][
            "route_road_evidence_exposure_row_count"
        ]
        == 76
    )
    assert (
        gate_map["validation_package"]["details"][
            "review_packet_acceptance_gate_closure_candidate_count"
        ]
        == 0
    )
    assert (
        gate_map["validation_package"]["details"][
            "review_packet_osrm_manifest_present"
        ]
        is True
    )
    assert (
        gate_map["validation_package"]["details"][
            "review_packet_osrm_unpinned_row_count"
        ]
        == 0
    )
    assert gate_map["validation_package"]["details"]["osrm_unpinned_row_count"] == 0
    assert (
        gate_map["validation_package"]["details"]["osrm_raw_response_file_count"]
        == 3
    )
    assert not any(
        "raw OSRM response payloads" in item
        for item in gate_map["validation_package"]["details"][
            "strategy_readiness_remaining_blockers"
        ]
    )
    assert not any(
        "live/unpinned" in item
        for item in gate_map["validation_package"]["details"][
            "strategy_readiness_remaining_blockers"
        ]
    )
    assert not any(
        "raw OSRM response payloads" in item
        for item in gate_map["validation_package"]["blockers"]
    )
    assert not any(
        "Validation Package: validation strategy readiness: retained raw OSRM response payloads"
        in item
        for item in summary["remaining_blockers"]
    )
    assert gate_map["sensitivity_analysis"]["ready"] is False
    assert any(
        "Morris-vs-Sobol method decision" in item
        for item in gate_map["sensitivity_analysis"]["details"][
            "strategy_readiness_remaining_blockers"
        ]
    )
    assert any(
        "sensitivity strategy readiness: Morris-vs-Sobol method decision"
        in item
        for item in gate_map["sensitivity_analysis"]["blockers"]
    )
    assert gate_map["full_experiment_output"]["ready"] is False
    assert any(
        "graph method that is not accepted" in item
        for item in gate_map["full_experiment_output"]["details"][
            "strategy_readiness_remaining_blockers"
        ]
    )
    assert any(
        "experiment strategy readiness: full-pilot outputs depend on a graph method"
        in item
        for item in gate_map["full_experiment_output"]["blockers"]
    )
    assert gate_map["manuscript_report_alignment"]["ready"] is False
    assert (
        gate_map["manuscript_report_alignment"]["details"][
            "claim_alignment_overclaim_candidate_count"
        ]
        == 108
    )
    assert (
        gate_map["manuscript_report_alignment"]["details"][
            "claim_alignment_review_status_counts"
        ]["requires_revision_or_acceptance"]
        == 108
    )
    assert any(
        "claim-alignment rows are review aids" in item
        for item in gate_map["manuscript_report_alignment"]["details"][
            "claim_alignment_remaining_blockers"
        ]
    )
    assert any(
        "claim alignment: claim-alignment rows are review aids" in item
        for item in gate_map["manuscript_report_alignment"]["blockers"]
    )
    assert gate_map["final_audit"]["ready"] is False
    assert summary["remaining_blockers"]

    print("PASS: final-study readiness audit blocks scaffold-level completion")


def test_audit_script_reports_final_blockers_without_default_failure() -> None:
    """The script should be usable in default validation without failing."""

    module = _load_audit_script()
    summary = module.audit_final_study_readiness()

    assert summary["final_study_ready"] is False
    assert "final-study gates" in summary["claim_boundary"]

    print("PASS: final-study readiness script reports blockers")


def test_graph_scale_gate_requires_manifest_even_with_acceptance() -> None:
    """Acceptance without a result manifest should not close graph-scale readiness."""

    gate = _graph_scale_gate(None, _accepted_graph_scale_summary())

    assert gate["ready"] is False
    assert any("pilot full manifest" in item for item in gate["blockers"])

    print("PASS: graph-scale gate requires pilot manifest")


def test_graph_scale_gate_requires_matching_counts() -> None:
    """Graph-scale acceptance must match source and analysis graph counts."""

    manifest = _pilot_manifest(graph_nodes=119)
    gate = _graph_scale_gate(manifest, _accepted_graph_scale_summary())

    assert gate["ready"] is False
    assert any("counts must match" in item for item in gate["blockers"])

    print("PASS: graph-scale gate blocks stale acceptance counts")


def test_validation_summary_scope_blocks_scaffold_language() -> None:
    """Scaffold validation language should keep the validation gate blocked."""

    assert _validation_summary_scope_is_blocked("scaffold/sanity evidence") is True
    assert _validation_summary_scope_is_blocked("not calibrated route check") is True
    assert _validation_summary_scope_is_blocked("accepted benchmark validation") is False

    print("PASS: validation summary scope blocks scaffold language")


def test_data_provenance_gate_requires_acceptance_and_final_manifest() -> None:
    """Acceptance alone should not close scaffold-scoped provenance."""

    gate = _data_provenance_gate(
        _reproducibility_manifest(),
        _accepted_provenance_summary(),
        _source_provenance_summary(),
    )

    assert gate["ready"] is False
    assert any("scaffold-only" in item for item in gate["blockers"])

    print("PASS: data provenance gate requires final manifest scope")


def test_data_provenance_gate_requires_acceptance_record() -> None:
    """A final-scoped manifest still requires explicit provenance acceptance."""

    gate = _data_provenance_gate(
        _reproducibility_manifest(scope="accepted real-world pilot package", remaining=[]),
        _missing_provenance_summary(),
        _source_provenance_summary(),
    )

    assert gate["ready"] is False
    assert any("provenance acceptance" in item for item in gate["blockers"])

    print("PASS: data provenance gate requires acceptance record")


def test_data_provenance_gate_requires_source_provenance_manifest() -> None:
    """A final-scoped manifest and acceptance still require source provenance diagnostics."""

    gate = _data_provenance_gate(
        _reproducibility_manifest(scope="accepted real-world pilot package", remaining=[]),
        _accepted_provenance_summary(),
        _missing_source_provenance_summary(),
    )

    assert gate["ready"] is False
    assert any("source provenance" in item for item in gate["blockers"])

    print("PASS: data provenance gate requires source provenance diagnostics")


def test_data_provenance_gate_reports_source_url_review_details() -> None:
    """Source URL review and remediation evidence should stay non-accepting."""

    gate = _data_provenance_gate(
        _reproducibility_manifest(),
        _missing_provenance_summary(),
        _source_provenance_summary(),
        {
            "live_check_performed": True,
            "url_status_counts": {"reachable": 2, "http_error": 1},
            "unreachable_or_error_count": 1,
            "publication_ready": False,
            "can_mark_complete": False,
        },
        {
            "row_count": 3,
            "remediation_status_counts": {
                "blocked_unreachable_or_http_error": 1,
                "reachable_needs_license_review": 2,
            },
            "blocking_issue_count": 1,
            "live_check_required_count": 0,
            "publication_ready": False,
            "can_mark_complete": False,
        },
    )

    assert gate["ready"] is False
    assert gate["details"]["source_url_live_check_performed"] is True
    assert gate["details"]["source_url_status_counts"] == {
        "reachable": 2,
        "http_error": 1,
    }
    assert gate["details"]["source_url_unreachable_or_error_count"] == 1
    assert gate["details"]["source_url_publication_ready"] is False
    assert gate["details"]["source_url_can_mark_complete"] is False
    assert gate["details"]["source_url_remediation_row_count"] == 3
    assert gate["details"]["source_url_remediation_blocking_issue_count"] == 1
    assert gate["details"]["source_url_remediation_live_check_required_count"] == 0
    assert (
        gate["details"]["source_url_remediation_status_counts"][
            "blocked_unreachable_or_http_error"
        ]
        == 1
    )
    assert gate["details"]["source_url_remediation_publication_ready"] is False
    assert gate["details"]["source_url_remediation_can_mark_complete"] is False

    print("PASS: data provenance gate reports source URL review details")


def test_validation_gate_requires_acceptance_and_final_summary_scope() -> None:
    """Acceptance alone should not close a scaffold validation summary."""

    gate = _validation_gate(_accepted_validation_summary())

    assert gate["ready"] is False
    assert any("validation summary" in item for item in gate["blockers"])

    print("PASS: validation gate requires final validation summary scope")


def test_sensitivity_scope_blocks_scaffold_language() -> None:
    """Scaffold sensitivity language should keep the sensitivity gate blocked."""

    assert _sensitivity_scope_is_blocked("Pilot scaffold output") is True
    assert _sensitivity_scope_is_blocked("not calibrated result") is True
    assert _sensitivity_scope_is_blocked("accepted sensitivity output") is False

    print("PASS: sensitivity scope blocks scaffold language")


def test_sensitivity_gate_requires_acceptance_and_final_scope() -> None:
    """Acceptance alone should not close scaffold-scoped Morris outputs."""

    manifest = _morris_manifest()
    gate = _sensitivity_gate(manifest, _accepted_sensitivity_summary())

    assert gate["ready"] is False
    assert any("scaffold-level" in item for item in gate["blockers"])

    print("PASS: sensitivity gate requires final sensitivity scope")


def test_sensitivity_count_blockers_detect_stale_acceptance() -> None:
    """Sensitivity acceptance counts must match the manifest counts."""

    manifest = _morris_manifest(row_count=3781)
    blockers = _sensitivity_count_blockers(manifest, _accepted_sensitivity_summary())

    assert blockers
    assert "row_count" in blockers[0]

    print("PASS: sensitivity gate blocks stale acceptance counts")


def test_experiment_scope_blocks_pending_or_uncalibrated_language() -> None:
    """Pending or uncalibrated experiment manifests should stay blocked."""

    assert _experiment_scope_is_blocked("accepted output", "pending_input_review") is True
    assert _experiment_scope_is_blocked("not calibrated output", "accepted") is True
    assert _experiment_scope_is_blocked("accepted experiment output", "accepted") is False

    print("PASS: experiment scope blocks pending or uncalibrated language")


def test_full_experiment_gate_requires_acceptance_and_final_scope() -> None:
    """Acceptance alone should not close pending full experiment outputs."""

    manifest = _pilot_full_manifest()
    gate = _full_experiment_gate(manifest, _accepted_experiment_summary())

    assert gate["ready"] is False
    assert any("input validation" in item for item in gate["blockers"])

    print("PASS: full experiment gate requires final output scope")


def test_experiment_count_blockers_detect_stale_acceptance() -> None:
    """Experiment acceptance counts must match the pilot full manifest."""

    manifest = _pilot_full_manifest(row_count=1891)
    blockers = _experiment_count_blockers(manifest, _accepted_experiment_summary())

    assert blockers
    assert "row_count" in blockers[0]

    print("PASS: full experiment gate blocks stale acceptance counts")


def test_manuscript_gate_requires_acceptance_and_final_scope() -> None:
    """Acceptance alone should not close scaffold figure/report scope."""

    gate = _manuscript_report_gate(
        _figure_manifest(),
        _claim_alignment_manifest(),
        _publication_audit(ready=True),
        _accepted_manuscript_summary(),
    )

    assert gate["ready"] is False
    assert any("scaffold" in item for item in gate["blockers"])

    print("PASS: manuscript/report gate requires final claim scope")


def test_manuscript_gate_requires_publication_ready_evidence() -> None:
    """Manuscript acceptance cannot bypass evidence gates."""

    gate = _manuscript_report_gate(
        _figure_manifest(claim_boundary="Accepted study scope."),
        _claim_alignment_manifest(),
        _publication_audit(ready=False),
        _accepted_manuscript_summary(),
    )

    assert gate["ready"] is False
    assert any("evidence gates" in item for item in gate["blockers"])

    print("PASS: manuscript/report gate requires publication-ready evidence")


def test_reproducibility_gate_requires_acceptance_and_final_manifest() -> None:
    """Acceptance alone should not close scaffold reproducibility scope."""

    gate = _reproducibility_gate(
        _reproducibility_manifest_for_gate(),
        _accepted_reproducibility_summary(),
        _reproducibility_review_manifest_for_gate(),
        _reproducibility_smoke_manifest_for_gate(),
    )

    assert gate["ready"] is False
    assert any("clean-checkout" in item for item in gate["blockers"])
    assert gate["details"]["review_packet_present"] is True
    assert gate["details"]["review_packet_row_count"] == 8
    assert gate["details"]["current_worktree_smoke_present"] is True
    assert gate["details"]["current_worktree_smoke_passed"] is True
    assert gate["details"]["clean_checkout_smoke_present"] is None

    print("PASS: reproducibility gate requires final manifest scope")


def test_reproducibility_count_blockers_detect_stale_acceptance() -> None:
    """Reproducibility acceptance command counts must match the manifest."""

    blockers = _reproducibility_count_blockers(
        ["cmd1", "cmd2"],
        _accepted_reproducibility_summary(expected_validation_command_count=3),
    )

    assert blockers
    assert "command count" in blockers[0]

    print("PASS: reproducibility gate blocks stale command counts")


def test_final_audit_gate_requires_all_pre_final_gates_ready() -> None:
    """Final audit acceptance cannot bypass blocked pre-final gates."""

    gates = [
        _fake_gate("pilot_region_accepted", ready=True),
        _fake_gate("rail_evidence", ready=False),
    ]
    gate = _final_audit_gate(gates, _accepted_final_audit_summary())

    assert gate["ready"] is False
    assert any("pre-final gates" in item for item in gate["blockers"])

    print("PASS: final-audit gate requires all pre-final gates ready")


def test_final_audit_count_blockers_detect_stale_gate_lists() -> None:
    """Final audit reviewed gates must match the current gate list."""

    blockers = _final_audit_count_blockers(
        [_fake_gate("pilot_region_accepted", ready=True)],
        _accepted_final_audit_summary(expected_gate_count=2),
    )

    assert blockers
    assert "expected_gate_count" in blockers[0]

    print("PASS: final-audit gate blocks stale gate lists")


def _load_audit_script():
    spec = importlib.util.spec_from_file_location(
        "audit_final_study_readiness", AUDIT_SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_final_study_readiness"] = module
    spec.loader.exec_module(module)
    return module


def _accepted_graph_scale_summary() -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/graph_scale_acceptance.json",
        "graph_scale_decision": "corridor_abstraction",
        "source_graph_nodes": 4608,
        "source_graph_edges": 9148,
        "analysis_graph_nodes": 118,
        "analysis_graph_edges": 174,
        "remaining_blockers": [],
    }


def _pilot_manifest(*, graph_nodes: int = 118) -> dict[str, object]:
    return {
        "graph_scale": {"source": "fixture"},
        "analysis_graph_reduced": True,
        "analysis_graph_strategy": "fixture corridor",
        "source_graph_nodes": 4608,
        "source_graph_edges": 9148,
        "graph_nodes": graph_nodes,
        "graph_edges": 174,
    }


def _accepted_validation_summary() -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/validation_acceptance.json",
        "benchmark_strategy": "cached_osrm_snapshot",
        "remaining_blockers": [],
    }


def _accepted_provenance_summary() -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/provenance_acceptance.json",
        "region_id": "songpa_public_demo",
        "remaining_blockers": [],
    }


def _missing_provenance_summary() -> dict[str, object]:
    return {
        "acceptance_ready": False,
        "record_present": False,
        "path": "data/manifests/provenance_acceptance.json",
        "remaining_blockers": [
            "create an explicit provenance acceptance record after source review"
        ],
    }


def _source_provenance_summary() -> dict[str, object]:
    return {
        "diagnostics_ready": True,
        "manifest_present": True,
        "path": "data/manifests/source_provenance_manifest.json",
        "record_count": 10,
        "review_status_counts": {
            "cached_snapshot_pending_review": 3,
            "context_only_not_cached": 3,
            "repository_input_pending_review": 4,
        },
        "remaining_blockers": [],
    }


def _missing_source_provenance_summary() -> dict[str, object]:
    return {
        "diagnostics_ready": False,
        "manifest_present": False,
        "path": "data/manifests/source_provenance_manifest.json",
        "record_count": 0,
        "remaining_blockers": ["create source provenance manifest"],
    }


def _reproducibility_manifest(
    *,
    scope: str = "scaffold-only real-world pilot package",
    remaining: list[str] | None = None,
) -> dict[str, object]:
    return {
        "scope": scope,
        "remaining_upgrades": ["reviewed OSM-derived snapshot"]
        if remaining is None
        else remaining,
    }


def _accepted_sensitivity_summary() -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/sensitivity_acceptance.json",
        "sensitivity_method": "salib_morris",
        "expected_row_count": 4320,
        "expected_summary_row_count": 7056,
        "sobol_requirement_decision": "not_required",
        "remaining_blockers": [],
    }


def _morris_manifest(*, row_count: int = 4320) -> dict[str, object]:
    return {
        "method": "salib_morris",
        "row_count": row_count,
        "summary_row_count": 7056,
        "result_scope": "Pilot scaffold SALib Morris sensitivity output; not calibrated.",
    }


def _accepted_experiment_summary() -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/experiment_acceptance.json",
        "run_profile": "full_pilot",
        "expected_row_count": 1890,
        "expected_summary_row_count": 63,
        "policy_count": 7,
        "scenario_count": 9,
        "seed_count": 30,
        "remaining_blockers": [],
    }


def _pilot_full_manifest(*, row_count: int = 1890) -> dict[str, object]:
    return {
        "run_profile": "full_pilot",
        "row_count": row_count,
        "summary_row_count": 63,
        "design_status": "accepted_full_profile_pending_input_validation",
        "result_scope": "Pilot full output; not calibrated real-world results.",
        "scenario_policy_seed_design": {
            "policy_count": 7,
            "scenario_count": 9,
            "seed_count": 30,
        },
    }


def _accepted_manuscript_summary() -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/manuscript_acceptance.json",
        "region_id": "songpa_public_demo",
        "remaining_blockers": [],
    }


def _figure_manifest(
    *,
    claim_boundary: str = "Scaffold-only figure/table package.",
) -> dict[str, object]:
    return {"claim_boundary": claim_boundary}


def _claim_alignment_manifest(
    *,
    overclaim_candidate_count: int = 0,
) -> dict[str, object]:
    return {
        "row_count": 1,
        "overclaim_candidate_count": overclaim_candidate_count,
        "guardrail_language_count": 0,
        "review_status_counts": {
            "requires_revision_or_acceptance": overclaim_candidate_count,
        },
        "claim_category_counts": {"validation_claim": overclaim_candidate_count},
        "gate_dependency_counts": {"validation_package": overclaim_candidate_count},
        "remaining_blockers": [
            "claim-alignment rows are review aids and do not approve manuscript claims",
        ],
        "publication_ready": False,
    }


def _publication_audit(*, ready: bool) -> dict[str, object]:
    return {"publication_ready": ready}


def _accepted_reproducibility_summary(
    *,
    expected_validation_command_count: int = 2,
) -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/reproducibility_acceptance.json",
        "expected_validation_command_count": expected_validation_command_count,
        "remaining_blockers": [],
    }


def _reproducibility_manifest_for_gate(
    *,
    scope: str = "scaffold-only real-world pilot package",
    remaining: list[str] | None = None,
) -> dict[str, object]:
    return {
        "scope": scope,
        "remaining_upgrades": ["clean checkout pending"]
        if remaining is None
        else remaining,
        "validation_commands": ["cmd1", "cmd2"],
    }


def _reproducibility_review_manifest_for_gate() -> dict[str, object]:
    return {
        "row_count": 8,
        "clean_checkout_test_performed": False,
        "git_status_line_count": 3,
        "git_untracked_count": 1,
        "no_runtime_cloned_repo_imports": True,
    }


def _reproducibility_smoke_manifest_for_gate() -> dict[str, object]:
    return {
        "manifest_present": True,
        "result_scope": "current_worktree_smoke_not_clean_checkout",
        "command_count": 17,
        "passed_count": 17,
        "failed_count": 0,
        "smoke_passed": True,
        "clean_checkout_test_performed": False,
        "can_mark_complete": False,
    }


def _accepted_final_audit_summary(
    *,
    expected_gate_count: int = 2,
) -> dict[str, object]:
    return {
        "acceptance_ready": True,
        "record_present": True,
        "path": "data/manifests/final_audit_acceptance.json",
        "expected_gate_count": expected_gate_count,
        "reviewed_gate_ids": ["pilot_region_accepted", "rail_evidence"],
        "ready_gate_ids": ["pilot_region_accepted"],
        "blocked_gate_ids": ["rail_evidence"],
        "remaining_blockers": [],
    }


def _fake_gate(gate_id: str, *, ready: bool) -> dict[str, object]:
    return {
        "gate_id": gate_id,
        "label": gate_id,
        "ready": ready,
        "artifact_present": True,
        "evidence": [],
        "blockers": [] if ready else ["blocked"],
        "details": {},
    }


if __name__ == "__main__":
    test_current_final_study_readiness_is_blocked()
    test_audit_script_reports_final_blockers_without_default_failure()
    test_graph_scale_gate_requires_manifest_even_with_acceptance()
    test_graph_scale_gate_requires_matching_counts()
    test_validation_summary_scope_blocks_scaffold_language()
    test_data_provenance_gate_requires_acceptance_and_final_manifest()
    test_data_provenance_gate_requires_acceptance_record()
    test_data_provenance_gate_requires_source_provenance_manifest()
    test_data_provenance_gate_reports_source_url_review_details()
    test_validation_gate_requires_acceptance_and_final_summary_scope()
    test_sensitivity_scope_blocks_scaffold_language()
    test_sensitivity_gate_requires_acceptance_and_final_scope()
    test_sensitivity_count_blockers_detect_stale_acceptance()
    test_experiment_scope_blocks_pending_or_uncalibrated_language()
    test_full_experiment_gate_requires_acceptance_and_final_scope()
    test_experiment_count_blockers_detect_stale_acceptance()
    test_manuscript_gate_requires_acceptance_and_final_scope()
    test_manuscript_gate_requires_publication_ready_evidence()
    test_reproducibility_gate_requires_acceptance_and_final_manifest()
    test_reproducibility_count_blockers_detect_stale_acceptance()
    test_final_audit_gate_requires_all_pre_final_gates_ready()
    test_final_audit_count_blockers_detect_stale_gate_lists()
    print("\n=== REALWORLD FINAL STUDY READINESS TESTS PASSED ===")
