"""Direct tests for strict paper-revision experiment-design loading."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.revision_design import (
    EXPECTED_CAMPAIGNS,
    GRAPH_SCOPES,
    RevisionDesignError,
    load_revision_design,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifests" / "paper_revision_experiment_design.json"


def _raw_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _load_mutation(mutator):
    raw = deepcopy(_raw_manifest())
    mutator(raw)
    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "design.json"
        path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        return load_revision_design(path)


def _expect_error(mutator, fragment: str) -> None:
    try:
        _load_mutation(mutator)
    except RevisionDesignError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected RevisionDesignError containing {fragment!r}")


def test_load_committed_manifest() -> None:
    design = load_revision_design(MANIFEST)

    assert design.schema_version == 1
    assert design.design_id == "paper_revision_top10_corridor_v4_20260721"
    assert design.output_root == Path(
        "results/paper_revision_top10_corridor_v4_20260721"
    )
    assert design.canonical_results_read_only == Path(
        "results/realworld_pilot_nodelink"
    )
    assert design.arrival_seeds == tuple(range(3101, 3131))
    assert design.threat_seeds == tuple(range(5101, 5201))
    assert design.bootstrap_seed == 20260721
    assert design.morris_seed == 20260722
    assert design.confidence == 0.95
    assert design.bootstrap_replicates == 10000
    assert tuple(design.campaigns) == EXPECTED_CAMPAIGNS
    assert design.defaults["graph_scope"] == "top10"
    assert design.defaults["corridor_path_count"] == 10
    assert design.defaults["graph_scope_method"] == (
        "exact_top3_plus_deterministic_penalty_diversification"
    )
    assert "not exact global top-10" in design.defaults["graph_scope_interpretation"]

    graph_campaign = design.campaign("graph_scope")
    assert tuple(item["id"] for item in graph_campaign["graph_scopes"]) == (
        "top3",
        "top5",
        "top10",
        "full",
    )
    assert graph_campaign["full_graph_arrival_seed_count"] == 5
    assert len(graph_campaign["scenario_ids"]) == 7
    assert {
        "goseong_access_road_damage_severe",
        "goseong_last_mile_damage_severe",
        "goseong_random_capacity_reduction",
    }.issubset(graph_campaign["scenario_ids"])
    assert tuple(design.campaign("break_even")["resource_frames"]) == (
        "configured_bundle",
        "matched_road_fleet",
    )
    assert design.campaign("break_even")["target_segment"] == (
        "A_to_D_corridor_time_band_20_80"
    )
    assert tuple(design.campaign("road_rail_map")["resource_frames"]) == (
        "configured_bundle",
        "matched_road_fleet",
    )
    assert GRAPH_SCOPES == frozenset({"top3", "top5", "top10", "full"})


def test_loaded_view_is_deeply_immutable() -> None:
    design = load_revision_design(MANIFEST)
    campaign = design.campaign("break_even")

    try:
        campaign["purpose"] = "changed"
    except TypeError:
        pass
    else:
        raise AssertionError("campaign mapping must be immutable")

    try:
        campaign["road_multipliers"][0] = 99.0
    except TypeError:
        pass
    else:
        raise AssertionError("campaign sequence must be immutable")

    try:
        design.campaigns["extra"] = campaign
    except TypeError:
        pass
    else:
        raise AssertionError("campaign registry must be immutable")

    try:
        design.campaign("missing")
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("unknown campaign must fail")


def test_rejects_top_level_and_campaign_schema_drift() -> None:
    _expect_error(lambda raw: raw.__setitem__("unexpected", True), "unknown keys")
    _expect_error(
        lambda raw: raw["campaigns"].pop("morris"),
        "campaign set",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["break_even"].__setitem__(
            "unplanned_field", 1
        ),
        "unknown keys",
    )


def test_rejects_unsafe_output_roots() -> None:
    _expect_error(
        lambda raw: raw.__setitem__(
            "output_root", "results/realworld_pilot_nodelink"
        ),
        "canonical results",
    )
    _expect_error(
        lambda raw: raw.__setitem__(
            "output_root", "results/realworld_pilot_nodelink/revision"
        ),
        "canonical results",
    )
    _expect_error(
        lambda raw: raw.__setitem__("output_root", "../outside"),
        "relative path",
    )


def test_rejects_invalid_seed_ranges_and_counts() -> None:
    _expect_error(
        lambda raw: raw["seed_blocks"]["arrival"].update(
            {"start": 3130, "stop": 3101}
        ),
        "start must not exceed stop",
    )
    _expect_error(
        lambda raw: raw["seed_blocks"]["threat"].__setitem__("start", True),
        "must be an integer",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["random_threat_outer"].__setitem__(
            "threat_draw_count", 101
        ),
        "threat seed count",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["graph_scope"].__setitem__(
            "full_arrival_seed_count", 31
        ),
        "arrival seed count",
    )


def test_rejects_invalid_confidence_bootstrap_and_graph_scopes() -> None:
    _expect_error(
        lambda raw: raw["defaults"].__setitem__("confidence", 1.0),
        "between 0 and 1",
    )
    _expect_error(
        lambda raw: raw["defaults"].__setitem__("bootstrap_replicates", 0),
        "positive integer",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["graph_scope"]["graph_scopes"][1].update(
            {"id": "top7", "corridor_path_count": 7}
        ),
        "must be one of",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["graph_scope"]["graph_scopes"][0].update(
            {"corridor_path_count": 4}
        ),
        "corridor_path_count",
    )


def test_rejects_invalid_factor_bounds_and_rail_conditions() -> None:
    _expect_error(
        lambda raw: raw["campaigns"]["morris"]["factors"].__setitem__(
            "demand", [1000.0, 1000.0]
        ),
        "strictly increasing bounds",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["morris"]["factors"].__setitem__(
            "demand", [float("nan"), 1000.0]
        ),
        "finite",
    )
    _expect_error(
        lambda raw: raw["campaigns"]["road_rail_map"]["rail_conditions"][4].update(
            {"multiplier": 2.0}
        ),
        "must use null multiplier",
    )


if __name__ == "__main__":
    test_load_committed_manifest()
    test_loaded_view_is_deeply_immutable()
    test_rejects_top_level_and_campaign_schema_drift()
    test_rejects_unsafe_output_roots()
    test_rejects_invalid_seed_ranges_and_counts()
    test_rejects_invalid_confidence_bootstrap_and_graph_scopes()
    test_rejects_invalid_factor_bounds_and_rail_conditions()
    print("test_revision_design: all checks passed")
