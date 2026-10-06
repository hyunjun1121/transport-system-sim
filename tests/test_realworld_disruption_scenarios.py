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
    DEFAULT_RECOVERY_PROFILE,
    DEFAULT_SCENARIO_PATH,
    DEFAULT_TEMPORAL_SCOPE,
    build_disruption_scenario_manifest,
    REQUIRED_FAMILIES,
    SCENARIO_EDGE_ATTRS,
    DisruptionScenario,
    assert_required_family_coverage,
    build_scenario_disruption_map,
    build_scenario_edge_map,
    hybrid_corridor_candidate_paths,
    load_disruption_scenarios,
    mark_scenario_edges,
    scenario_family_coverage,
    select_candidate_edges,
    select_corridor_time_band_edges,
    select_shortest_path_time_band_edges,
    write_disruption_scenario_manifest,
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


def time_band_graph() -> nx.DiGraph:
    """Return a route whose edge midpoints land on and around 20--80%."""

    graph = nx.DiGraph(region_id="synthetic_region")
    for node in ("A", "n1", "n2", "n3", "n4", "n5", "D"):
        graph.add_node(node)
    durations = (2.0, 1.0, 2.0, 2.0, 1.0, 2.0)
    nodes = ("A", "n1", "n2", "n3", "n4", "n5", "D")
    for index, (u, v) in enumerate(zip(nodes, nodes[1:]), start=1):
        _add_road_edge(graph, u, v, f"band-{index}", t0=durations[index - 1])
    return graph


def test_shortest_path_time_band_boundaries_and_determinism() -> None:
    """Central-trunk selector includes midpoint boundaries and preserves direction."""

    graph = time_band_graph()
    first = select_shortest_path_time_band_edges(
        graph,
        source="A",
        target="D",
        lower_fraction=0.2,
        upper_fraction=0.8,
    )
    second = select_shortest_path_time_band_edges(
        graph,
        source="A",
        target="D",
        lower_fraction=0.2,
        upper_fraction=0.8,
    )

    # Total t0=10. Edge midpoints are 1, 2.5, 4, 6, 7.5, 9 minutes.
    # Thus the inclusive 20--80% band selects edges 2--5, in A->D direction.
    expected = (
        ("n1", "n2"),
        ("n2", "n3"),
        ("n3", "n4"),
        ("n4", "n5"),
    )
    assert first == expected
    assert second == expected

    # Connectors can participate in routing but are never physical damage targets.
    graph.edges["n2", "n3"].update(
        source="connector", highway="connector", length_m=0.0
    )
    assert select_shortest_path_time_band_edges(
        graph, source="A", target="D", lower_fraction=0.2, upper_fraction=0.8
    ) == (("n1", "n2"), ("n3", "n4"), ("n4", "n5"))

    # Exact 20% and 80% midpoint boundaries are included.
    boundary = nx.DiGraph(region_id="synthetic_region")
    for node in ("A", "b1", "b2", "b3", "b4", "D"):
        boundary.add_node(node)
    for index, (u, v, t0) in enumerate(
        (
            ("A", "b1", 1.0),
            ("b1", "b2", 2.0),
            ("b2", "b3", 4.0),
            ("b3", "b4", 2.0),
            ("b4", "D", 1.0),
        ),
        start=1,
    ):
        _add_road_edge(boundary, u, v, f"boundary-{index}", t0=t0)
    # Midpoints: 0.5, 2.0, 5.0, 8.0, 9.5. Both boundaries are included.
    assert select_shortest_path_time_band_edges(
        boundary, source="A", target="D", lower_fraction=0.2, upper_fraction=0.8
    ) == (("b1", "b2"), ("b2", "b3"), ("b3", "b4"))

    print("PASS: shortest-path time-band boundaries and deterministic order are fixed")


def test_shortest_path_time_band_rejects_invalid_or_missing_paths() -> None:
    """Central-trunk selector fails closed for invalid bands and road paths."""

    graph = time_band_graph()
    assert_raises_value_error(
        lambda: select_shortest_path_time_band_edges(
            graph, source="A", target="D", lower_fraction=0.8, upper_fraction=0.2
        ),
        "0 <= lower_fraction < upper_fraction <= 1",
    )
    assert_raises_value_error(
        lambda: select_shortest_path_time_band_edges(
            graph, source="D", target="A", lower_fraction=0.2, upper_fraction=0.8
        ),
        "has no road path",
    )
    graph.edges["A", "n1"]["t0"] = 0.0
    assert_raises_value_error(
        lambda: select_shortest_path_time_band_edges(
            graph, source="A", target="D", lower_fraction=0.2, upper_fraction=0.8
        ),
        "positive finite t0",
    )

    print("PASS: shortest-path time-band selector rejects invalid/no-path inputs")


def test_corridor_time_band_covers_each_preserved_candidate() -> None:
    """A corridor-wide target covers central bands on every preserved A->D path."""

    graph = nx.DiGraph(
        region_id="synthetic_region",
        corridor_path_count=2,
    )
    for node in ("A", "p1", "p2", "p3", "q1", "q2", "q3", "D", "S", "R"):
        graph.add_node(node)
    for index, (u, v) in enumerate(
        (("A", "p1"), ("p1", "p2"), ("p2", "p3"), ("p3", "D")),
        start=1,
    ):
        _add_road_edge(graph, u, v, f"p-{index}", t0=1.0)
    for index, (u, v) in enumerate(
        (("A", "q1"), ("q1", "q2"), ("q2", "q3"), ("q3", "D")),
        start=1,
    ):
        _add_road_edge(graph, u, v, f"q-{index}", t0=1.1)

    first = select_corridor_time_band_edges(graph, source="A", target="D")
    second = select_corridor_time_band_edges(graph, source="A", target="D")
    expected = {
        ("p1", "p2"),
        ("p2", "p3"),
        ("q1", "q2"),
        ("q2", "q3"),
    }
    assert set(first) == expected
    assert second == first

    print("PASS: corridor time band covers every preserved A->D candidate")


def test_shared_hybrid_candidate_builder_accepts_exact_seed_paths() -> None:
    """Graph-scope builder and target selector share one route algorithm."""

    graph = nx.DiGraph()
    for node in ("A", "p", "q", "D"):
        graph.add_node(node)
    _add_road_edge(graph, "A", "p", "ap", t0=1.0)
    _add_road_edge(graph, "p", "D", "pd", t0=1.0)
    _add_road_edge(graph, "A", "q", "aq", t0=1.2)
    _add_road_edge(graph, "q", "D", "qd", t0=1.2)

    automatic = hybrid_corridor_candidate_paths(
        graph,
        source="A",
        target="D",
        path_count=2,
    )
    seeded = hybrid_corridor_candidate_paths(
        graph,
        source="A",
        target="D",
        seed_paths=automatic[:1],
        path_count=2,
    )
    assert seeded == automatic

    print("PASS: one hybrid candidate builder serves both call paths")


def test_longhaul_scenario_requires_canonical_time_band_target() -> None:
    """Long-haul family cannot regress to one route or an S->R target."""

    assert_raises_value_error(
        lambda: make_scenario(
            "bad_longhaul",
            "long_haul",
            "corridor_time_band",
            "S->R",
        ),
        "A_to_D_corridor_time_band_20_80",
    )

    scenario = make_scenario(
        "central_longhaul",
        "long_haul",
        "corridor_time_band",
        "A_to_D_corridor_time_band_20_80",
    )
    selected = select_candidate_edges(time_band_graph(), scenario)
    assert tuple(item.edge for item in selected) == (
        ("n1", "n2"),
        ("n2", "n3"),
        ("n3", "n4"),
        ("n4", "n5"),
    )
    assert {item.reason_category for item in selected} == {
        "long_haul:A_to_D_corridor_time_band_20_80"
    }

    print("PASS: long-haul family is locked to canonical A->D central time band")


def test_csv_schema_validation_and_family_coverage() -> None:
    """The committed scenario table should cover every Workstream 7 family."""

    scenarios = load_disruption_scenarios(
        "data/scenarios/goseong_disruption_scenarios.csv",
        region_id="goseong_mobilization",
    )
    assert_required_family_coverage(scenarios, REQUIRED_FAMILIES)
    coverage = scenario_family_coverage(scenarios)

    assert coverage["random"] == 2
    assert coverage["critical_link"] == 1
    assert coverage["access_road"] == 6
    assert coverage["long_haul"] == 3
    assert coverage["last_mile"] == 5
    assert coverage["rail_station_access"] == 1
    assert coverage["spatial_hazard_overlay"] == 5
    assert coverage["rail_service"] == 1
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


def test_mark_scenario_edges_records_travel_time_multiplier() -> None:
    """mark_scenario_edges should annotate selected edges with the direct-slowdown
    multiplier symmetric with disruption_capacity_factor (provenance: a damaged road's
    time penalty must be recorded on the edge, not only the capacity factor)."""

    graph = synthetic_simulator_graph()
    scenario = DisruptionScenario(
        scenario_id="synthetic_damage_mark",
        region_id="synthetic_region",
        family="access_road",
        label="access damage marking test",
        selection_method="shortest_path",
        target_segment="A->S",
        disruption_mode="capacity_reduction",
        capacity_factor=1.0,
        p_fail_scale=1.0,
        road_travel_time_multiplier=3.0,
        max_edges=3,
        evidence_class="scenario_based",
        observed_disaster_data=False,
    )

    assert "disruption_travel_time_multiplier" in SCENARIO_EDGE_ATTRS
    marked = mark_scenario_edges(graph, scenario)
    selected = select_candidate_edges(graph, scenario)
    assert selected, "fixture should select access A->S edges"
    for picked in selected:
        edge_data = marked.edges[picked.edge]
        assert edge_data["disruption_capacity_factor"] == 1.0
        assert edge_data["disruption_travel_time_multiplier"] == 3.0

    print("PASS: mark_scenario_edges records travel_time_multiplier symmetric with capacity_factor")


def test_blocked_mode_maps_to_blocked_edge_disruption() -> None:
    """Blocked scenarios should produce blocked simulator disruption states."""

    graph = synthetic_simulator_graph()
    scenario = DisruptionScenario(
        scenario_id="synthetic_blocked",
        region_id="synthetic_region",
        family="critical_link",
        label="Synthetic blocked critical link",
        selection_method="edge_betweenness",
        target_segment="all_road",
        disruption_mode="blocked",
        capacity_factor=0.0,
        p_fail_scale=1.0,
        max_edges=1,
        evidence_class="scenario_based",
        observed_disaster_data=False,
    )
    disruption_map = build_scenario_disruption_map(graph, scenario)

    assert len(disruption_map) == 1
    disruption = next(iter(disruption_map.values()))
    assert disruption.status == "blocked"
    assert disruption.capacity_factor == 0.0
    assert scenario.recovery_profile == DEFAULT_RECOVERY_PROFILE
    assert scenario.temporal_scope == DEFAULT_TEMPORAL_SCOPE

    print("PASS: blocked scenario maps to blocked edge disruption")


def test_road_travel_time_multiplier_threads_through_loader_and_property() -> None:
    """road_travel_time_multiplier: CSV column -> DisruptionScenario -> edge_disruption.

    Direct-slowdown lever for damaged roads (wartime BPR no-op complement). A blank
    cell resolves to None and the edge_disruption property defaults to 1.0
    (no effect); a value threads into the degraded EdgeDisruption consumed by
    build_scenario_disruption_map.
    """
    from src.realworld.disruption_scenarios import _scenario_from_row

    assert "road_travel_time_multiplier" in CSV_COLUMNS

    base_row = {col: "" for col in CSV_COLUMNS}
    base_row.update(
        {
            "scenario_id": "synthetic_damage",
            "region_id": "synthetic_region",
            "family": "critical_link",
            "label": "damage test",
            "selection_method": "edge_betweenness",
            "target_segment": "all_road",
            "disruption_mode": "capacity_reduction",
            "capacity_factor": "1.0",
            "p_fail_scale": "1.0",
            "evidence_class": "scenario_based",
            "observed_disaster_data": "false",
            "road_travel_time_multiplier": "2.0",
        }
    )
    scenario = _scenario_from_row(base_row, row_number=2)
    assert scenario.road_travel_time_multiplier == 2.0
    assert scenario.edge_disruption.travel_time_multiplier == 2.0
    assert scenario.edge_disruption.status == "degraded"

    # blank cell -> None -> property resolves to 1.0
    base_row["road_travel_time_multiplier"] = ""
    scenario_default = _scenario_from_row(base_row, row_number=2)
    assert scenario_default.road_travel_time_multiplier is None
    assert scenario_default.edge_disruption.travel_time_multiplier == 1.0

    print("PASS: road_travel_time_multiplier threads through loader + edge_disruption property")


def test_goseong_segment_damage_rows_parse() -> None:
    """Committed goseong CSV carries SEGMENT-TARGETED road-damage rows.

    Replaces the retired globally-targeted (edge_betweenness/all_road) damage
    ladder, which was multimodal-inert because the betweenness edges fell off the
    rail-bound corridor. The new rows target the multimodal road legs directly:
    Access and last-mile rows use whole shortest paths. Long-haul rows instead
    target only the central 20--80% temporal band of the A->D shortest road path,
    preventing endpoint access/return overlap. All use capacity_factor=1.0 to
    isolate the road_travel_time_multiplier direct-slowdown lever.
    """
    goseong_path = Path("data/scenarios/goseong_disruption_scenarios.csv")
    scenarios = {s.scenario_id: s for s in load_disruption_scenarios(str(goseong_path))}

    # Retired globally-targeted rows must be gone (multimodal-inert artifact).
    for retired in (
        "goseong_road_damage_mild",
        "goseong_road_damage_severe",
        "goseong_road_damage_extreme",
    ):
        assert retired not in scenarios, f"retired betweenness row still present: {retired}"

    # (scenario_id, family, target_segment, multiplier)
    expected = [
        ("goseong_access_road_damage_mild", "access_road", "A->S", 1.5),
        ("goseong_access_road_damage_severe", "access_road", "A->S", 3.0),
        ("goseong_access_road_damage_extreme", "access_road", "A->S", 8.0),
        ("goseong_last_mile_damage_mild", "last_mile", "R->D", 1.5),
        ("goseong_last_mile_damage_severe", "last_mile", "R->D", 3.0),
        ("goseong_last_mile_damage_extreme", "last_mile", "R->D", 8.0),
        (
            "goseong_long_haul_damage_severe",
            "long_haul",
            "A_to_D_corridor_time_band_20_80",
            3.0,
        ),
        (
            "goseong_long_haul_damage_mild",
            "long_haul",
            "A_to_D_corridor_time_band_20_80",
            1.2,
        ),
        (
            "goseong_long_haul_damage_moderate",
            "long_haul",
            "A_to_D_corridor_time_band_20_80",
            1.5,
        ),
    ]
    for sid, family, target_segment, mult in expected:
        assert sid in scenarios, f"missing segment-damage scenario {sid}"
        scenario = scenarios[sid]
        assert scenario.family == family, f"{sid} family={scenario.family!r} want {family!r}"
        expected_method = (
            "corridor_time_band" if family == "long_haul" else "shortest_path"
        )
        assert scenario.selection_method == expected_method, (
            f"{sid} method={scenario.selection_method!r}"
        )
        assert scenario.target_segment == target_segment, f"{sid} target={scenario.target_segment!r}"
        assert scenario.disruption_mode == "capacity_reduction"
        assert scenario.capacity_factor == 1.0
        assert scenario.road_travel_time_multiplier == mult
        assert scenario.edge_disruption.travel_time_multiplier == mult
        assert scenario.edge_disruption.status == "degraded"
        assert not scenario.edge_disruption.is_blocked
    print("PASS: goseong segment-targeted damage rows parse + thread multiplier")


def test_goseong_segment_damage_targets_canonical_paths() -> None:
    """Actual top3 guard: central trunk is stable and endpoint-leg disjoint."""
    goseong_path = Path("data/scenarios/goseong_disruption_scenarios.csv")
    inputs = load_pilot_inputs(
        region_path="data/regions/goseong_mobilization.yaml",
        cache_path="data/cache/goseong_nodelink_road.graphml",
        road_class_overrides_path="data/parameters/road_class_overrides.csv",
    )
    graph = inputs.graph
    scenarios = {s.scenario_id: s for s in load_disruption_scenarios(str(goseong_path))}

    # Whole-path access and last-mile selectors retain their endpoint contract.
    checks = [
        ("goseong_access_road_damage_severe", "A", "S", 3.0),
        ("goseong_last_mile_damage_severe", "R", "D", 3.0),
    ]
    for sid, start, end, mult in checks:
        scenario = scenarios[sid]
        selected = select_candidate_edges(graph, scenario)
        assert selected, f"{sid} selected no edges"
        assert selected[0].edge[0] == start, f"{sid} path start {selected[0].edge[0]!r} want {start!r}"
        assert selected[-1].edge[1] == end, f"{sid} path end {selected[-1].edge[1]!r} want {end!r}"
        disruption_map = build_scenario_disruption_map(graph, scenario)
        assert disruption_map, f"{sid} built empty disruption map"
        disruption = disruption_map[selected[0].edge]
        assert disruption.status == "degraded"
        assert disruption.travel_time_multiplier == mult
        assert not disruption.is_blocked

    longhaul_ids = (
        "goseong_long_haul_damage_severe",
        "goseong_long_haul_damage_mild",
        "goseong_long_haul_damage_moderate",
    )
    central_edge_sets = []
    for sid in longhaul_ids:
        scenario = scenarios[sid]
        selected = select_candidate_edges(graph, scenario)
        assert selected, f"{sid} selected no central road edges"
        central_edge_sets.append(tuple(item.edge for item in selected))
        assert all(item.source != "connector" for item in selected)
        assert all(graph.edges[item.edge].get("highway") != "connector" for item in selected)
        assert all(float(graph.edges[item.edge].get("length_m", 1.0)) > 0.0 for item in selected)
        disruption_map = build_scenario_disruption_map(graph, scenario)
        assert set(disruption_map) == {item.edge for item in selected}
        assert all(item.status == "degraded" for item in disruption_map.values())
    assert central_edge_sets[0] == central_edge_sets[1] == central_edge_sets[2]

    endpoint_scenarios = (
        make_scenario("fixture_a_s", "access_road", "shortest_path", "A->S"),
        make_scenario("fixture_s_a", "access_road", "shortest_path", "S->A"),
        make_scenario("fixture_r_d", "last_mile", "shortest_path", "R->D"),
        make_scenario("fixture_d_r", "last_mile", "shortest_path", "D->R"),
    )
    # make_scenario uses the fixture region; clone only its selection contract.
    endpoint_edges = set()
    for template in endpoint_scenarios:
        scenario = DisruptionScenario(
            **{
                **template.__dict__,
                "scenario_id": f"actual_{template.scenario_id}",
                "region_id": "goseong_mobilization",
            }
        )
        endpoint_edges.update(item.edge for item in select_candidate_edges(graph, scenario))
    assert set(central_edge_sets[0]).isdisjoint(endpoint_edges)

    print("PASS: goseong central time band is deterministic, physical, and endpoint-disjoint")


def test_committed_pilot_scenarios_map_offline_to_all_families() -> None:
    """Committed Songpa scenarios should map offline on the analysis graph."""

    inputs = load_pilot_inputs()
    scenarios = load_disruption_scenarios(DEFAULT_SCENARIO_PATH, region_id=inputs.region_id)

    first_map = build_scenario_edge_map(inputs.graph, scenarios, region_id=inputs.region_id)
    second_map = build_scenario_edge_map(inputs.graph, scenarios, region_id=inputs.region_id)

    assert set(first_map) == {scenario.scenario_id for scenario in scenarios}
    edge_families = {
        selected.family
        for scenario_edges in first_map.values()
        for selected in scenario_edges
    }
    expected_edge_families = {
        scenario.family for scenario in scenarios if scenario.family != "rail_service"
    }
    assert edge_families == expected_edge_families
    assert {
        scenario_id: [selected.edge for selected in scenario_edges]
        for scenario_id, scenario_edges in first_map.items()
    } == {
        scenario_id: [selected.edge for selected in scenario_edges]
        for scenario_id, scenario_edges in second_map.items()
    }
    non_rail_edges = {
        sid: edges for sid, edges in first_map.items()
        if any(s.family != "rail_service" for s in edges) or len(edges) > 0
    }
    assert all(scenario_edges for scenario_edges in non_rail_edges.values())

    print("PASS: committed pilot disruption scenarios map offline to all families")


def test_disruption_manifest_records_checksums_and_temporal_scope() -> None:
    """The Phase 6 manifest should preserve checksums and claim boundaries."""

    inputs = load_pilot_inputs()
    scenarios = load_disruption_scenarios(DEFAULT_SCENARIO_PATH, region_id=inputs.region_id)
    edge_map = build_scenario_edge_map(inputs.graph, scenarios, region_id=inputs.region_id)

    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_path = Path(temp_dir) / "disruption_scenarios_manifest.json"
        doc_path = Path(temp_dir) / "disruption_scenarios.md"
        manifest = write_disruption_scenario_manifest(
            scenarios,
            scenario_path=DEFAULT_SCENARIO_PATH,
            manifest_path=manifest_path,
            doc_path=doc_path,
            selected_edges=edge_map,
        )

        assert manifest_path.exists()
        assert doc_path.exists()
    assert manifest["row_count"] == 22
    assert manifest["family_counts"] == {
        "access_road": 3,
        "critical_link": 1,
        "last_mile": 1,
        "rail_station_access": 1,
        "random": 2,
        "spatial_hazard_overlay": 6,
        "rail_service": 8,
    }
    assert len(manifest["scenario_table_sha256"]) == 64
    assert {scenario.family for scenario in scenarios} <= set(
        manifest["family_checksums"]
    )
    assert all(len(value) == 64 for value in manifest["family_checksums"].values())
    assert manifest["temporal_scope_counts"] == {
        "metadata_only_not_dynamic_recovery": 22
    }
    assert manifest["recovery_profile_counts"] == {
        "static_full_horizon_no_recovery": 22
    }
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert "not observed disaster data" in manifest["claim_boundary"]
    assert "songpa_critical_link_blockage" in manifest["selected_edges"]
    assert (
        manifest["selected_edges"]["songpa_critical_link_blockage"]["edge_count"]
        > 0
    )
    assert len(
        manifest["selected_edges"]["songpa_critical_link_blockage"][
            "selected_edge_checksum"
        ]
    ) == 64

    # Also verify the pure builder path without writing files.
    manifest = build_disruption_scenario_manifest(
        scenarios,
        scenario_path=DEFAULT_SCENARIO_PATH,
        selected_edges=edge_map,
    )
    assert manifest["row_count"] == 22


if __name__ == "__main__":
    test_shortest_path_time_band_boundaries_and_determinism()
    test_shortest_path_time_band_rejects_invalid_or_missing_paths()
    test_corridor_time_band_covers_each_preserved_candidate()
    test_shared_hybrid_candidate_builder_accepts_exact_seed_paths()
    test_longhaul_scenario_requires_canonical_time_band_target()
    test_csv_schema_validation_and_family_coverage()
    test_spatial_hazard_rows_must_not_claim_observed_data()
    test_deterministic_hash_and_critical_link_mapping()
    test_route_station_spatial_mapping_and_edge_marking()
    test_mark_scenario_edges_records_travel_time_multiplier()
    test_blocked_mode_maps_to_blocked_edge_disruption()
    test_road_travel_time_multiplier_threads_through_loader_and_property()
    test_goseong_segment_damage_rows_parse()
    test_goseong_segment_damage_targets_canonical_paths()
    test_committed_pilot_scenarios_map_offline_to_all_families()
    test_disruption_manifest_records_checksums_and_temporal_scope()
    print("\n=== REALWORLD DISRUPTION SCENARIO TESTS PASSED ===")
