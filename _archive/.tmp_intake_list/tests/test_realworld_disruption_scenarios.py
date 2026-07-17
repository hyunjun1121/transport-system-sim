"""Offline tests for deterministic real-world disruption scenarios."""

import csv
import os
import sys
import tempfile
from pathlib import Path

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.disruption_scenarios import (
    CSV_COLUMNS,
    DEFAULT_SCENARIO_PATH,
    REQUIRED_FAMILIES,
    DisruptionScenario,
    assert_required_family_coverage,
    build_scenario_disruption_map,
    build_scenario_edge_map,
    load_disruption_scenarios,
    mark_scenario_edges,
    scenario_family_coverage,
    select_candidate_edges,
)
from src.realworld.pilot_experiments import load_pilot_inputs


def _add_node(graph: nx.DiGraph, node, lon: float, lat: float, **attrs) -> None:
    graph.add_node(node, x=lon, y=lat, **attrs)


def _add_road_edge(
    graph: nx.DiGraph,
    u,
    v,
    edge_id: str,
    *,
    t0: float = 1.0,
    source: str = "fixture",
    highway: str = "secondary",
    length_m: float = 100.0,
) -> None:
    graph.add_edge(
        u,
        v,
        t0=t0,
        capacity=1000.0,
        base_p_fail=0.02,
        p_fail=0.02,
        mode="road",
        length_m=length_m,
        speed_kph=40.0,
        highway=highway,
        source=source,
        realworld_edge_id=edge_id,
    )


def synthetic_simulator_graph() -> nx.DiGraph:
    """Return a deterministic graph with canonical simulator points."""

    graph = nx.DiGraph(region_id="synthetic_region")
    _add_node(graph, "A", 0.0, 0.0, snapped_road_node="n_origin")
    _add_node(graph, "S", 2.0, 0.0, snapped_road_node="n_station")
    _add_node(graph, "R", 4.0, 0.0, snapped_road_node="n_egress")
    _add_node(graph, "D", 6.0, 0.0, snapped_road_node="n_dest")
    _add_node(graph, "n_origin", 1.0, 0.0)
    _add_node(graph, "n_station", 2.0, 0.0)
    _add_node(graph, "n_mid", 3.0, 0.0)
    _add_node(graph, "n_egress", 4.0, 0.0)
    _add_node(graph, "n_dest", 5.0, 0.0)
    _add_node(graph, "n_hazard", 3.0, 1.0)

    _add_road_edge(graph, "A", "n_origin", "connector-A", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "n_origin", "A", "connector-A-rev", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "n_station", "S", "connector-S", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "S", "n_station", "connector-S-rev", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "R", "n_egress", "connector-R", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "n_egress", "R", "connector-R-rev", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "n_dest", "D", "connector-D", source="connector", highway="connector", length_m=0.0)
    _add_road_edge(graph, "D", "n_dest", "connector-D-rev", source="connector", highway="connector", length_m=0.0)

    _add_road_edge(graph, "n_origin", "n_station", "e-origin-station", t0=1.0)
    _add_road_edge(graph, "n_origin", "n_mid", "e-origin-mid", t0=1.0)
    _add_road_edge(graph, "n_mid", "n_dest", "e-mid-dest", t0=1.0)
    _add_road_edge(graph, "n_egress", "n_mid", "e-egress-mid", t0=1.0)
    _add_road_edge(graph, "n_station", "n_hazard", "e-station-hazard", t0=1.5)
    _add_road_edge(graph, "n_hazard", "n_dest", "e-hazard-dest", t0=1.5)
    return graph


def make_scenario(
    scenario_id: str,
    family: str,
    selection_method: str,
    target_segment: str,
    *,
    max_edges: int | None = None,
    hazard_bbox=None,
) -> DisruptionScenario:
    """Build a valid synthetic-region scenario for unit tests."""

    return DisruptionScenario(
        scenario_id=scenario_id,
        region_id="synthetic_region",
        family=family,
        label=f"{family} test scenario",
        selection_method=selection_method,
        target_segment=target_segment,
        disruption_mode="capacity_reduction",
        capacity_factor=0.5,
        p_fail_scale=1.0,
        max_edges=max_edges,
        hazard_bbox=hazard_bbox,
        evidence_class="scenario_based",
        observed_disaster_data=False,
    )


def assert_raises_value_error(func, expected: str) -> None:
    """Assert a callable raises ValueError containing expected text."""

    try:
        func()
    except ValueError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_csv_schema_validation_and_family_coverage() -> None:
    """The committed scenario table should cover every Workstream 7 family."""

    scenarios = load_disruption_scenarios(DEFAULT_SCENARIO_PATH, region_id="songpa_public_demo")
    assert_required_family_coverage(scenarios, REQUIRED_FAMILIES)
    coverage = scenario_family_coverage(scenarios)

    assert coverage["random"] == 2
    assert coverage["critical_link"] == 1
    assert coverage["access_road"] == 2
    assert coverage["last_mile"] == 1
    assert coverage["rail_station_access"] == 1
    assert coverage["spatial_hazard_overlay"] == 1
    for scenario in scenarios:
        if scenario.family == "spatial_hazard_overlay":
            assert scenario.evidence_class == "scenario_based"
            assert scenario.observed_disaster_data is False

    print("PASS: disruption scenario CSV schema and family coverage are valid")


def test_spatial_hazard_rows_must_not_claim_observed_data() -> None:
    """Scenario-based spatial overlays must not be labeled as observed disasters."""

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "bad_disruption_scenarios.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerow(
                {
                    "scenario_id": "bad_spatial",
                    "region_id": "synthetic_region",
                    "family": "spatial_hazard_overlay",
                    "label": "Bad spatial label",
                    "selection_method": "bbox_midpoint",
                    "target_segment": "bbox",
                    "disruption_mode": "capacity_reduction",
                    "capacity_factor": "0.5",
                    "p_fail_scale": "1.0",
                    "max_edges": "1",
                    "hazard_bbox_west": "0.0",
                    "hazard_bbox_south": "0.0",
                    "hazard_bbox_east": "1.0",
                    "hazard_bbox_north": "1.0",
                    "evidence_class": "observed_disaster_data",
                    "observed_disaster_data": "true",
                    "notes": "Invalid observed-data claim.",
                }
            )

        assert_raises_value_error(
            lambda: load_disruption_scenarios(path),
            "spatial_hazard_overlay rows must be scenario_based",
        )

    print("PASS: spatial overlays reject observed-disaster labeling")


def test_deterministic_hash_and_critical_link_mapping() -> None:
    """Hash-ranked and critical-link selections should be deterministic."""

    graph = synthetic_simulator_graph()
    random_scenario = make_scenario("synthetic_random", "random", "hash_rank", "all_road", max_edges=3)
    critical_scenario = make_scenario(
        "synthetic_critical",
        "critical_link",
        "edge_betweenness",
        "all_road",
        max_edges=2,
    )

    first_random = select_candidate_edges(graph, random_scenario)
    second_random = select_candidate_edges(graph, random_scenario)
    first_critical = select_candidate_edges(graph, critical_scenario)
    second_critical = select_candidate_edges(graph, critical_scenario)

    assert [edge.edge for edge in first_random] == [edge.edge for edge in second_random]
    assert [edge.edge for edge in first_critical] == [edge.edge for edge in second_critical]
    assert len(first_random) == 3
    assert len(first_critical) == 2
    assert all(edge.source != "connector" for edge in first_random)
    assert all(edge.source != "connector" for edge in first_critical)

    print("PASS: hash-ranked and critical-link scenario mapping is deterministic")


def test_route_station_spatial_mapping_and_edge_marking() -> None:
    """Route, station-access, and bbox selections should mark reason metadata."""

    graph = synthetic_simulator_graph()
    access = make_scenario("synthetic_access", "access_road", "shortest_path", "A->S")
    last_mile = make_scenario("synthetic_last_mile", "last_mile", "shortest_path", "R->D")
    station = make_scenario(
        "synthetic_station",
        "rail_station_access",
        "station_access",
        "S,R",
        max_edges=4,
    )
    spatial = make_scenario(
        "synthetic_spatial",
        "spatial_hazard_overlay",
        "bbox_midpoint",
        "bbox",
        max_edges=3,
        hazard_bbox=(2.5, 0.5, 3.5, 1.5),
    )

    access_edges = select_candidate_edges(graph, access)
    last_mile_edges = select_candidate_edges(graph, last_mile)
    station_edges = select_candidate_edges(graph, station)
    spatial_edges = select_candidate_edges(graph, spatial)
    marked = mark_scenario_edges(graph, station)
    disruption_map = build_scenario_disruption_map(graph, last_mile)

    assert [edge.edge for edge in access_edges] == [
        ("A", "n_origin"),
        ("n_origin", "n_station"),
        ("n_station", "S"),
    ]
    assert [edge.edge for edge in last_mile_edges] == [
        ("R", "n_egress"),
        ("n_egress", "n_mid"),
        ("n_mid", "n_dest"),
        ("n_dest", "D"),
    ]
    assert any(edge.source == "connector" for edge in station_edges)
    assert {edge.reason_category for edge in spatial_edges} == {"scenario_based_hazard_overlay"}
    assert spatial_edges[0].edge == ("n_station", "n_hazard")
    assert "disruption_family" not in graph.edges[station_edges[0].edge]
    assert marked.edges[station_edges[0].edge]["disruption_family"] == "rail_station_access"
    assert set(disruption_map) == {edge.edge for edge in last_mile_edges}
    assert all(disruption.status == "degraded" for disruption in disruption_map.values())

    print("PASS: route, station, spatial, and marking helpers work")


def test_committed_pilot_scenarios_map_offline_to_all_families() -> None:
    """Committed Songpa scenarios should map offline on the analysis graph."""

    inputs = load_pilot_inputs()
    scenarios = load_disruption_scenarios(DEFAULT_SCENARIO_PATH, region_id=inputs.region_id)

    first_map = build_scenario_edge_map(inputs.graph, scenarios, region_id=inputs.region_id)
    second_map = build_scenario_edge_map(inputs.graph, scenarios, region_id=inputs.region_id)

    assert set(first_map) == {scenario.scenario_id for scenario in scenarios}
    assert {
        selected.family
        for scenario_edges in first_map.values()
        for selected in scenario_edges
    } == REQUIRED_FAMILIES
    assert {
        scenario_id: [selected.edge for selected in scenario_edges]
        for scenario_id, scenario_edges in first_map.items()
    } == {
        scenario_id: [selected.edge for selected in scenario_edges]
        for scenario_id, scenario_edges in second_map.items()
    }
    assert all(scenario_edges for scenario_edges in first_map.values())

    print("PASS: committed pilot disruption scenarios map offline to all families")


if __name__ == "__main__":
    test_csv_schema_validation_and_family_coverage()
    test_spatial_hazard_rows_must_not_claim_observed_data()
    test_deterministic_hash_and_critical_link_mapping()
    test_route_station_spatial_mapping_and_edge_marking()
    test_committed_pilot_scenarios_map_offline_to_all_families()
    print("\n=== REALWORLD DISRUPTION SCENARIO TESTS PASSED ===")
