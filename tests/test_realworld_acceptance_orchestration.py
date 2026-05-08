"""Tests for sub-agent acceptance orchestration."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_orchestration import (  # noqa: E402
    REVIEW_AGENT_DEFINITIONS,
    build_acceptance_record,
    summarize_acceptance_orchestration_manifest,
    write_acceptance_orchestration_outputs,
)
from src.realworld.acceptance_records import load_acceptance_record  # noqa: E402
from src.realworld.final_study_readiness import audit_final_study_readiness  # noqa: E402


def test_acceptance_orchestration_defines_required_review_agents() -> None:
    names = {agent.role_name for agent in REVIEW_AGENT_DEFINITIONS}
    assert "Pilot Region & Privacy Review Agent" in names
    assert "OSM / Source / License / Provenance Review Agent" in names
    assert "Graph Scale Method Review Agent" in names
    assert "Road / Rail / Parameter Evidence Agent" in names
    assert "Validation Benchmark Strategy Agent" in names
    assert "Sensitivity Analysis Review Agent" in names
    assert "Full Experiment Package Agent" in names
    assert "Paper / Report Claim Alignment Agent" in names
    assert "Clean-Checkout Reproducibility Agent" in names
    assert "Final Independent Audit Agent" in names


def test_review_agents_point_at_current_readiness_packets() -> None:
    """Reviewer intake should include current blocker-classification packets."""

    agents = {agent.agent_id: agent for agent in REVIEW_AGENT_DEFINITIONS}

    graph_agent = agents["graph_scale_method_review_agent"]
    assert (
        "data/validation/graph_scale_strategy_readiness_packet.csv"
        in graph_agent.review_packet_paths
    )
    assert (
        "data/validation/full_graph_runtime_readiness_packet.csv"
        in graph_agent.review_packet_paths
    )
    assert "data/validation/graph_scale_manifest_audit.csv" in (
        graph_agent.review_packet_paths
    )

    evidence_agent = agents["road_rail_parameter_evidence_agent"]
    assert (
        "data/parameters/parameter_source_readiness_packet.csv"
        in evidence_agent.review_packet_paths
    )
    assert "data/road/road_source_readiness_packet.csv" in (
        evidence_agent.review_packet_paths
    )
    assert "data/rail/rail_fetch_readiness_packet.csv" in (
        evidence_agent.review_packet_paths
    )

    validation_agent = agents["validation_benchmark_strategy_agent"]
    assert (
        "data/validation/validation_strategy_readiness_packet.csv"
        in validation_agent.review_packet_paths
    )
    assert (
        "data/validation/validation_benchmark_readiness_packet.csv"
        in validation_agent.review_packet_paths
    )

    sensitivity_agent = agents["sensitivity_analysis_review_agent"]
    assert (
        "data/validation/sensitivity_strategy_readiness_packet.csv"
        in sensitivity_agent.review_packet_paths
    )

    experiment_agent = agents["full_experiment_package_agent"]
    assert "data/manifests/experiment_strategy_readiness_packet.csv" in (
        experiment_agent.review_packet_paths
    )

    reproducibility_agent = agents["clean_checkout_reproducibility_agent"]
    assert "data/validation/tracked_artifact_audit.csv" in (
        reproducibility_agent.review_packet_paths
    )


def test_acceptance_orchestration_blocks_nonready_gate_without_completion() -> None:
    audit = audit_final_study_readiness()
    gate_map = {gate["gate_id"]: gate for gate in audit["gates"]}
    pilot_agent = next(
        agent
        for agent in REVIEW_AGENT_DEFINITIONS
        if agent.agent_id == "pilot_region_privacy_review_agent"
    )
    record = build_acceptance_record(
        pilot_agent,
        gate_map["pilot_region_accepted"],
        "2026-05-04T00:00:00+00:00",
    )
    assert record.status == "needs_human_review"
    assert record.can_mark_complete is False
    assert record.required_actions
    assert record.risks


def test_acceptance_orchestration_writes_records_and_manifest() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = write_acceptance_orchestration_outputs(
            output_dir=root / "agent_reviews",
            review_packet_dir=root / "review_packets",
            manifest_path=root / "acceptance_orchestration_manifest.json",
            agent_definition_path=root / "agents.json",
            agent_doc_path=root / "agents.md",
            schema_path=root / "schema.json",
        )
        assert manifest["final_study_ready"] is False
        assert manifest["record_count"] >= 10
        assert manifest["blocked_or_review_record_count"] >= 1
        assert manifest["can_mark_complete_count"] == 0
        assert (root / "acceptance_orchestration_manifest.json").exists()
        assert (root / "review_packets" / "acceptance_review_index.md").exists()

        first_record_path = Path(manifest["records"][0]["record_path"])
        if not first_record_path.is_absolute():
            first_record_path = ROOT / first_record_path
        # The manifest stores project-relative paths for normal runs. In this
        # tempfile run, validate by opening the real file directly from output_dir.
        generated_records = sorted((root / "agent_reviews").glob("*.json"))
        assert generated_records
        loaded = load_acceptance_record(generated_records[0])
        assert loaded.status in {"blocked", "needs_human_review"}


def test_acceptance_orchestration_summary_reports_absent_manifest() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        summary = summarize_acceptance_orchestration_manifest(
            Path(tmpdir) / "missing.json"
        )
    assert summary["manifest_present"] is False
    assert summary["remaining_blockers"]


if __name__ == "__main__":
    test_acceptance_orchestration_defines_required_review_agents()
    test_review_agents_point_at_current_readiness_packets()
    test_acceptance_orchestration_blocks_nonready_gate_without_completion()
    test_acceptance_orchestration_writes_records_and_manifest()
    test_acceptance_orchestration_summary_reports_absent_manifest()
    print("PASS: acceptance orchestration")
