"""Tests for Phase 8 pre-compact guardrail tables."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.phase8_precompact_tables import (  # noqa: E402
    BENCHMARK_THRESHOLD_COLUMNS,
    DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH,
    DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH,
    DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH,
    DEFAULT_POLICY_FEASIBILITY_TABLE_PATH,
    PHASE8_PRECOMPACT_SCOPE,
    POLICY_FEASIBILITY_COLUMNS,
    build_benchmark_threshold_rows,
    build_policy_feasibility_rows,
    write_phase8_precompact_tables,
)


def test_policy_feasibility_rows_classify_current_policies() -> None:
    """Every current policy should receive an explicit Phase 8 feasibility row."""

    rows = build_policy_feasibility_rows()
    by_id = {row["policy_id"]: row for row in rows}

    assert len(rows) == 8
    assert set(by_id) == {
        "bus_only",
        "baseline_multimodal",
        "multimodal_lastmile_redundancy",
        "staggered_or_adaptive_dispatch",
        "multimodal_increased_feeder_capacity",
        "bus_corridor_redundancy",
        "rail_delay_or_partial_unavailability",
        "fleet_shortage_stress",
    }
    assert by_id["bus_only"]["feasibility_status"] == (
        "proxy_comparator_ready_for_engineering_compact_only"
    )
    assert by_id["bus_corridor_redundancy"]["feasibility_status"] == (
        "blocked_excluded_until_documented_corridor"
    )
    assert by_id["fleet_shortage_stress"]["feasibility_status"] == (
        "blocked_current_policy_no_effect"
    )
    assert by_id["rail_delay_or_partial_unavailability"]["feasibility_status"] == (
        "stress_sensitivity_only"
    )
    assert by_id["staggered_or_adaptive_dispatch"]["adaptive_label_status"] == (
        "partial_dispatch_only_not_adaptive_route_optimization"
    )
    assert by_id["staggered_or_adaptive_dispatch"][
        "dispatch_adaptation_implemented"
    ].startswith("partial_deterministic_feeder_spacing")
    assert "full_pilot" in by_id["fleet_shortage_stress"]["profile_inclusion"]
    assert by_id["fleet_shortage_stress"]["vehicle_delta_vs_baseline"] == (
        "no_effect_vs_same_mode_baseline"
    )
    assert by_id["fleet_shortage_stress"]["blocking_reason"].startswith(
        "configured knobs do not change"
    )
    assert by_id["baseline_multimodal"]["rerouting_authority_class"] == (
        "no_public_agency_rerouting_authority_recorded"
    )
    assert by_id["baseline_multimodal"]["route_leg_ids"] == "A->S; S->R; R->D"
    assert by_id["baseline_multimodal"]["transfer_delay_location"] == (
        "pre_rail_after_feeder_arrival"
    )
    assert by_id["bus_only"]["route_leg_ids"] == "A->D"
    assert {
        row["service_minute_budget_status"]
        for row in rows
    } == {"missing_predeclared_budget"}
    assert {row["can_support_publication_or_acceptance"] for row in rows} == {"false"}
    assert {row["formal_acceptance_evidence"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {PHASE8_PRECOMPACT_SCOPE}

    print("PASS: policy feasibility rows classify current policies")


def test_benchmark_threshold_rows_predeclare_phase7_thresholds() -> None:
    """Benchmark threshold table should encode Phase 7 pass/warn/fail rules."""

    rows = build_benchmark_threshold_rows()
    by_id = {row["threshold_id"]: row for row in rows}

    assert len(rows) == 11
    assert by_id["road_route_duration_difference"]["pass_rule"] == (
        "pass when absolute difference is <= 20 percent"
    )
    assert by_id["road_route_duration_difference"]["warn_rule"] == (
        "warn when absolute difference is > 20 and <= 40 percent"
    )
    assert by_id["road_route_distance_difference"]["pass_rule"] == (
        "pass when absolute difference is <= 10 percent"
    )
    assert "larger of 10 minutes or 15 percent" in by_id[
        "rail_transit_travel_time_difference"
    ]["pass_rule"]
    assert "post hoc" in by_id["threshold_revision_policy"]["fail_rule"]
    assert by_id["transit_itinerary_time_difference"]["fail_rule"] == (
        "fail outside the warn band or when no itinerary benchmark exists"
    )
    assert by_id["transfer_per_passenger_delay_range"]["unit"] == (
        "minutes_per_passenger"
    )
    assert by_id["benchmark_claim_boundary_presence"]["claim_boundary_on_fail"] == (
        "block compact promotion and report use"
    )
    assert all(row["predeclared_before_compact"] == "true" for row in rows)
    assert all(row["can_support_validation_gate"] == "false" for row in rows)
    assert {row["claim_boundary"] for row in rows} == {PHASE8_PRECOMPACT_SCOPE}
    assert "cached_external_router_snapshot=3" in by_id[
        "benchmark_snapshot_pinning"
    ]["current_source_classification"]

    print("PASS: benchmark threshold rows predeclare Phase 7 thresholds")


def test_phase8_precompact_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = write_phase8_precompact_tables(
            policy_output_path=root / "policy.csv",
            policy_manifest_path=root / "policy_manifest.json",
            policy_doc_path=root / "policy.md",
            benchmark_output_path=root / "thresholds.csv",
            benchmark_manifest_path=root / "thresholds_manifest.json",
            benchmark_doc_path=root / "thresholds.md",
        )

        with (root / "policy.csv").open("r", encoding="utf-8", newline="") as handle:
            policy_reader = csv.DictReader(handle)
            policy_rows = list(policy_reader)
        with (root / "thresholds.csv").open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            threshold_reader = csv.DictReader(handle)
            threshold_rows = list(threshold_reader)
        policy_manifest = json.loads(
            (root / "policy_manifest.json").read_text(encoding="utf-8")
        )
        threshold_manifest = json.loads(
            (root / "thresholds_manifest.json").read_text(encoding="utf-8")
        )
        policy_doc = (root / "policy.md").read_text(encoding="utf-8")
        threshold_doc = (root / "thresholds.md").read_text(encoding="utf-8")

    assert tuple(policy_reader.fieldnames or ()) == POLICY_FEASIBILITY_COLUMNS
    assert tuple(threshold_reader.fieldnames or ()) == BENCHMARK_THRESHOLD_COLUMNS
    assert len(policy_rows) == 8
    assert len(threshold_rows) == 11
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert policy_manifest["phase8_precompact_table_present"] is True
    assert threshold_manifest["validation_gate_closure_candidate_count"] == 0
    assert "Policy Feasibility and Fairness Table" in policy_doc
    assert "Benchmark Threshold Table" in threshold_doc

    print("PASS: Phase 8 precompact writer emits artifacts")


def test_shipped_phase8_precompact_tables_match_current_outputs() -> None:
    """Committed precompact tables should match current source inputs."""

    policy_rows = build_policy_feasibility_rows()
    threshold_rows = build_benchmark_threshold_rows()

    assert DEFAULT_POLICY_FEASIBILITY_TABLE_PATH.exists()
    assert DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH.exists()
    assert DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH.exists()
    assert DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH.exists()

    with DEFAULT_POLICY_FEASIBILITY_TABLE_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_policy_rows = list(csv.DictReader(handle))
    with DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_threshold_rows = list(csv.DictReader(handle))
    policy_manifest = json.loads(
        DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    threshold_manifest = json.loads(
        DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert written_policy_rows == policy_rows
    assert written_threshold_rows == threshold_rows
    assert policy_manifest["row_count"] == len(policy_rows)
    assert threshold_manifest["row_count"] == len(threshold_rows)
    assert policy_manifest["publication_ready"] is False
    assert threshold_manifest["publication_ready"] is False
    assert policy_manifest["formal_acceptance_evidence"] is False
    assert threshold_manifest["formal_acceptance_evidence"] is False

    print("PASS: shipped Phase 8 precompact tables match current outputs")


if __name__ == "__main__":
    test_policy_feasibility_rows_classify_current_policies()
    test_benchmark_threshold_rows_predeclare_phase7_thresholds()
    test_phase8_precompact_writer_outputs_artifacts()
    test_shipped_phase8_precompact_tables_match_current_outputs()
    print("\n=== REALWORLD PHASE 8 PRECOMPACT TABLE TESTS PASSED ===")
