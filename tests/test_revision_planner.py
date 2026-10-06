"""Direct tests for deterministic paper-revision campaign planning."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.revision_design import EXPECTED_CAMPAIGNS, load_revision_design
from src.realworld.revision_planner import plan_campaign_conditions


DESIGN_PATH = ROOT / "data" / "manifests" / "paper_revision_experiment_design.json"
FULL_COUNTS = {
    "paired_reanalysis": 2 * 2 * 21 * 30,
    "graph_scope": (3 * 7 * 2 * 30) + (1 * 7 * 2 * 5),
    "break_even": 16 * 2 * 2 * 30,
    "break_even_fine": 17 * 2 * 2 * 30,
    "demand_fleet": 4 * 4 * 2 * 2 * 30,
    "road_rail_map": 6 * 5 * 2 * 2 * 30,
    "random_threat_outer": 100 * 30 * 2,
    "adaptive_policies": 7 * 2 * 3 * 30,
    "morris": 20 * (6 + 1) * 2 * 5,
    "scale_sensitivity": 4 * 1 * 30 * 2,
    "path_interdiction_threat": 2 * 10 * 2 * 2 * 30,
}
SMOKE_COUNTS = {
    "paired_reanalysis": 2 * 2 * 3 * 2,
    "graph_scope": 4 * 7 * 2 * 2,
    "break_even": 3 * 2 * 2 * 2,
    "break_even_fine": 4 * 2 * 2,
    "demand_fleet": 2 * 2 * 2 * 2 * 2,
    "road_rail_map": 2 * 2 * 2 * 2 * 2,
    "random_threat_outer": 2 * 2 * 2,
    "adaptive_policies": 7 * 2 * 3 * 2,
    "morris": 2 * (6 + 1) * 2 * 2,
    "scale_sensitivity": 2 * 2 * 2 * 2,
    "path_interdiction_threat": 1 * 2 * 2 * 2 * 2,
}


def test_full_and_smoke_matrix_counts_match_manifest_dimensions() -> None:
    design = load_revision_design(DESIGN_PATH)
    assert tuple(EXPECTED_CAMPAIGNS) == tuple(FULL_COUNTS)

    for campaign_id in EXPECTED_CAMPAIGNS:
        full = plan_campaign_conditions(design, campaign_id, stage="full")
        smoke = plan_campaign_conditions(design, campaign_id, stage="smoke")
        assert len(full) == FULL_COUNTS[campaign_id], campaign_id
        assert len(smoke) == SMOKE_COUNTS[campaign_id], campaign_id

    assert sum(FULL_COUNTS.values()) == 24_630
    assert sum(SMOKE_COUNTS.values()) == 420
    print("PASS: full and smoke campaign counts match manifest dimensions")


def test_planning_is_deterministic_unique_and_parameters_are_immutable() -> None:
    design = load_revision_design(DESIGN_PATH)
    for campaign_id in EXPECTED_CAMPAIGNS:
        first = plan_campaign_conditions(design, campaign_id, stage="smoke")
        second = plan_campaign_conditions(design, campaign_id, stage="smoke")
        assert first == second, campaign_id
        identities = {
            (
                item.configuration_id,
                item.policy_id,
                item.arrival_seed,
                item.threat_seed,
                item.threat_draw,
            )
            for item in first
        }
        assert len(identities) == len(first), campaign_id
        assert all(item.campaign_id == campaign_id for item in first)

    condition = plan_campaign_conditions(
        design, "break_even", stage="smoke"
    )[0]
    try:
        condition.parameters["road_multiplier"] = 99.0
    except TypeError:
        pass
    else:
        raise AssertionError("planned parameters must be immutable")
    print("PASS: planning is deterministic, unique, and immutable")


def test_paired_campaigns_share_exogenous_configuration_and_seed() -> None:
    design = load_revision_design(DESIGN_PATH)
    for campaign_id in (
        "paired_reanalysis",
        "break_even",
        "road_rail_map",
        "random_threat_outer",
    ):
        conditions = plan_campaign_conditions(design, campaign_id, stage="smoke")
        grouped: dict[tuple[object, ...], set[str]] = defaultdict(set)
        for item in conditions:
            key = (
                item.configuration_id,
                item.arrival_seed,
                item.threat_seed,
                item.threat_draw,
            )
            grouped[key].add(item.policy_id)
        assert grouped, campaign_id
        assert all(
            policies == {"bus_only", "static_multimodal"}
            for policies in grouped.values()
        ), campaign_id

    random_conditions = plan_campaign_conditions(
        design, "random_threat_outer", stage="smoke"
    )
    assert {item.threat_draw for item in random_conditions} == {1, 2}
    assert {item.threat_seed for item in random_conditions} == {5101, 5102}
    print("PASS: policy alternatives retain paired seeds and configurations")


def test_graph_scope_and_morris_plans_preserve_required_metadata() -> None:
    design = load_revision_design(DESIGN_PATH)
    graph = plan_campaign_conditions(design, "graph_scope", stage="smoke")
    assert {
        (item.graph_scope, item.corridor_path_count) for item in graph
    } == {("top3", 3), ("top5", 5), ("top10", 10), ("full", None)}
    assert all(item.parameters["freeze_selected_edges_from"] == "top3" for item in graph)
    assert {item.scenario_id for item in graph} == set(
        design.campaign("graph_scope")["scenario_ids"]
    )

    graph_full = plan_campaign_conditions(design, "graph_scope", stage="full")
    seeds_by_scope = defaultdict(set)
    for item in graph_full:
        seeds_by_scope[item.graph_scope].add(item.arrival_seed)
    assert len(seeds_by_scope["top3"]) == 30
    assert len(seeds_by_scope["top5"]) == 30
    assert len(seeds_by_scope["top10"]) == 30
    assert len(seeds_by_scope["full"]) == 5

    morris = plan_campaign_conditions(design, "morris", stage="smoke")
    point_ids = {item.parameters["morris_point"] for item in morris}
    assert point_ids == set(range(14))
    assert all(len(item.parameters["factor_values"]) == 6 for item in morris)
    print("PASS: graph-scope and Morris metadata are complete")


def test_main_campaigns_use_top10_and_both_required_resource_frames() -> None:
    design = load_revision_design(DESIGN_PATH)
    for campaign_id in EXPECTED_CAMPAIGNS:
        if campaign_id == "graph_scope":
            continue
        conditions = plan_campaign_conditions(design, campaign_id, stage="smoke")
        assert {item.graph_scope for item in conditions} == {"top10"}, campaign_id
        assert {item.corridor_path_count for item in conditions} == {10}, campaign_id

    for campaign_id in ("break_even", "road_rail_map"):
        conditions = plan_campaign_conditions(design, campaign_id, stage="smoke")
        assert {item.resource_frame for item in conditions} == {
            "configured_bundle",
            "matched_road_fleet",
        }
        paired = defaultdict(set)
        for item in conditions:
            key = (
                item.configuration_id,
                item.resource_frame,
                item.arrival_seed,
                item.rail_status,
            )
            paired[key].add(item.policy_id)
        assert all(
            policies == {"bus_only", "static_multimodal"}
            for policies in paired.values()
        )
    print("PASS: main campaigns use top10 and required resource frames")


def test_unknown_campaign_and_stage_fail_closed() -> None:
    design = load_revision_design(DESIGN_PATH)
    for campaign_id, stage in (("unknown", "smoke"), ("break_even", "quick")):
        try:
            plan_campaign_conditions(design, campaign_id, stage=stage)
        except (KeyError, ValueError):
            pass
        else:
            raise AssertionError((campaign_id, stage))
    print("PASS: unknown campaigns and stages fail closed")


TESTS = [
    test_full_and_smoke_matrix_counts_match_manifest_dimensions,
    test_planning_is_deterministic_unique_and_parameters_are_immutable,
    test_paired_campaigns_share_exogenous_configuration_and_seed,
    test_graph_scope_and_morris_plans_preserve_required_metadata,
    test_main_campaigns_use_top10_and_both_required_resource_frames,
    test_unknown_campaign_and_stage_fail_closed,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== REVISION PLANNER TESTS PASSED ===")
