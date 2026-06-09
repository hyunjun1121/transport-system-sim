"""Offline tests for route plausibility validation scaffolding."""

import csv
import os
import sys
from pathlib import Path

import networkx as nx
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld import build_simulator_graph, load_graphml
from src.realworld.plausibility import (
    BENCHMARK_CLAIM_SCOPE,
    BENCHMARK_CSV_FIELDS,
    CLAIM_SCOPE,
    CSV_FIELDS,
    DEFAULT_FALLBACK_BENCHMARK_METHOD,
    DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS,
    DEFAULT_OSRM_BASE_URL,
    FAIL,
    OSRM_BENCHMARK_METHOD,
    OSRM_BENCHMARK_SOURCE_CLASS,
    PASS,
    WARN,
    ExternalRouteBenchmark,
    RouteCheck,
    benchmark_records_to_csv_rows,
    benchmark_status_counts,
    build_fallback_route_benchmarks,
    build_osrm_route_benchmarks,
    classify_value,
    evaluate_external_route_benchmarks,
    evaluate_connector_checks,
    evaluate_graph_plausibility,
    evaluate_route_check,
    records_to_csv_rows,
    status_counts,
)


ROOT = Path(__file__).resolve().parents[1]
REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
CSV_PATH = ROOT / "data" / "validation" / "route_plausibility.csv"
BENCHMARK_CSV_PATH = ROOT / "data" / "validation" / "external_route_benchmarks.csv"
SUMMARY_PATH = ROOT / "data" / "validation" / "validation_summary.md"


def test_classify_value_returns_pass_warn_fail() -> None:
    """Nested bounds should distinguish pass, warn, fail, and invalid values."""

    kwargs = {"pass_min": 1.0, "pass_max": 10.0, "warn_min": 0.0, "warn_max": 20.0}

    assert classify_value(5.0, **kwargs) == PASS
    assert classify_value(15.0, **kwargs) == WARN
    assert classify_value(25.0, **kwargs) == FAIL
    assert classify_value(float("nan"), **kwargs) == FAIL

    print("PASS: classify_value returns pass, warn, and fail")


def test_route_distance_check_can_pass_warn_and_fail() -> None:
    """Route distance checks should flag implausibly circuitous paths."""

    route = RouteCheck("synthetic_route", "A", "D", "synthetic direct route")

    pass_records = evaluate_route_check(
        synthetic_route_graph(length_m=1_200.0),
        route,
        region_id="synthetic",
    )
    warn_records = evaluate_route_check(
        synthetic_route_graph(length_m=5_000.0),
        route,
        region_id="synthetic",
    )
    fail_records = evaluate_route_check(
        synthetic_route_graph(length_m=7_000.0),
        route,
        region_id="synthetic",
    )

    assert record_by_id(pass_records, "synthetic_route_distance").status == PASS
    assert record_by_id(warn_records, "synthetic_route_distance").status == WARN
    assert record_by_id(fail_records, "synthetic_route_distance").status == FAIL

    print("PASS: route distance checks can pass, warn, and fail")


def test_connector_checks_can_pass_warn_and_fail() -> None:
    """Connector snap distances should produce actionable status levels."""

    graph = nx.DiGraph()
    graph.graph["region_id"] = "connector_fixture"
    graph.add_node("A", connector_distance_m=100.0)
    graph.add_node("D", connector_distance_m=500.0)
    graph.add_node("S", connector_distance_m=2_000.0)

    records = evaluate_connector_checks(
        graph,
        connector_points=("A", "D", "S"),
        region_id="connector_fixture",
    )

    assert record_by_id(records, "connector_A_distance").status == PASS
    assert record_by_id(records, "connector_D_distance").status == WARN
    assert record_by_id(records, "connector_S_distance").status == FAIL

    print("PASS: connector checks can pass, warn, and fail")


def test_unavailable_route_fails_without_live_services() -> None:
    """Missing road-mode routes should fail deterministically and offline."""

    graph = synthetic_route_graph(length_m=1_200.0)
    graph.remove_edge("A", "D")
    route = RouteCheck("missing_route", "A", "D", "synthetic missing route")

    records = evaluate_route_check(graph, route, region_id="synthetic")

    assert len(records) == 1
    assert record_by_id(records, "missing_route_available").status == FAIL
    assert record_by_id(records, "missing_route_available").observed_value == 0.0

    print("PASS: unavailable routes fail deterministically")


def test_fallback_route_benchmarks_are_executable_offline() -> None:
    """Fallback benchmarks should use coordinates and assumptions only."""

    graph = synthetic_route_graph(length_m=1_200.0)
    route = RouteCheck("synthetic_route", "A", "D", "synthetic direct route")
    benchmarks = build_fallback_route_benchmarks(
        graph,
        routes=(route,),
        route_assumptions={
            "synthetic_route": {"detour_factor": 1.40, "speed_kph": 35.0}
        },
    )

    assert len(benchmarks) == 1
    benchmark = benchmarks[0]
    assert benchmark.method == DEFAULT_FALLBACK_BENCHMARK_METHOD
    assert benchmark.source_class == DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS
    assert 1_000.0 < benchmark.benchmark_distance_m < 1_600.0
    assert benchmark.benchmark_duration_min > 0.0

    records = evaluate_external_route_benchmarks(
        graph,
        benchmarks,
        region_id="synthetic",
    )
    assert len(records) == 1
    assert records[0].benchmark_method == DEFAULT_FALLBACK_BENCHMARK_METHOD
    assert records[0].source_class == DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS
    assert records[0].claim_scope == BENCHMARK_CLAIM_SCOPE

    print("PASS: fallback route benchmarks execute offline")


def test_external_benchmark_comparison_can_pass_warn_and_fail() -> None:
    """Benchmark ratio checks should produce actionable status levels."""

    route = RouteCheck("synthetic_route", "A", "D", "synthetic direct route")
    benchmark = ExternalRouteBenchmark(
        benchmark_id="synthetic_benchmark",
        route=route,
        benchmark_distance_m=1_000.0,
        benchmark_duration_min=1.8,
        method="cached_osrm_fixture",
        source_class="cached_external_router_fixture",
        reference_source="unit_test_fixture",
    )

    pass_record = evaluate_external_route_benchmarks(
        synthetic_route_graph(length_m=1_050.0),
        (benchmark,),
        region_id="synthetic",
    )[0]
    warn_record = evaluate_external_route_benchmarks(
        synthetic_route_graph(length_m=1_200.0),
        (benchmark,),
        region_id="synthetic",
    )[0]
    fail_record = evaluate_external_route_benchmarks(
        synthetic_route_graph(length_m=1_300.0),
        (benchmark,),
        region_id="synthetic",
    )[0]

    assert pass_record.status == PASS
    assert warn_record.status == WARN
    assert warn_record.distance_status == WARN
    assert fail_record.status == FAIL
    assert fail_record.distance_status == FAIL

    print("PASS: external benchmark comparisons can pass, warn, and fail")


def test_osrm_route_benchmark_builder_uses_injected_fetcher() -> None:
    """OSRM benchmark construction should be testable without live network calls."""

    graph = synthetic_route_graph(length_m=1_200.0)
    route = RouteCheck("synthetic_route", "A", "D", "synthetic direct route")
    seen_urls: list[str] = []
    captured_payloads: list[tuple[str, str, float]] = []

    def fake_fetch(url: str, timeout_s: float):
        seen_urls.append(url)
        assert timeout_s == 7.0
        return {"routes": [{"distance": 1234.5, "duration": 210.0}]}

    def payload_callback(route: RouteCheck, url: str, payload: dict) -> None:
        captured_payloads.append(
            (
                route.check_id,
                url,
                float(payload["routes"][0]["distance"]),
            )
        )

    benchmarks = build_osrm_route_benchmarks(
        graph,
        routes=(route,),
        base_url=DEFAULT_OSRM_BASE_URL,
        timeout_s=7.0,
        fetch_json=fake_fetch,
        payload_callback=payload_callback,
    )

    assert len(benchmarks) == 1
    assert len(seen_urls) == 1
    assert "/route/v1/driving/" in seen_urls[0]
    assert benchmarks[0].method == OSRM_BENCHMARK_METHOD
    assert benchmarks[0].source_class == OSRM_BENCHMARK_SOURCE_CLASS
    assert benchmarks[0].benchmark_distance_m == 1234.5
    assert benchmarks[0].benchmark_duration_min == 3.5
    assert captured_payloads == [("synthetic_route", seen_urls[0], 1234.5)]

    print("PASS: OSRM benchmark builder supports injected offline fetcher")


def test_shipped_pilot_csv_matches_current_scaffold() -> None:
    """The committed CSV should match deterministic checks for the pilot cache."""

    expected_rows = list(records_to_csv_rows(current_pilot_records()))
    with CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(CSV_FIELDS)
    assert rows == expected_rows
    assert len(rows) == 21
    assert {row["status"] for row in rows} == {PASS, WARN}
    assert {row["claim_scope"] for row in rows} == {CLAIM_SCOPE}
    assert {"route", "connector", "edge_attributes"} <= {row["category"] for row in rows}

    counts = status_counts(current_pilot_records())
    assert counts == {PASS: 19, WARN: 2, FAIL: 0}

    print("PASS: shipped route plausibility CSV matches current pilot scaffold")


def test_shipped_external_benchmark_csv_matches_current_scaffold() -> None:
    """The committed benchmark CSV should match deterministic fallback checks."""

    expected_rows = list(benchmark_records_to_csv_rows(current_pilot_benchmark_records()))
    with BENCHMARK_CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(BENCHMARK_CSV_FIELDS)
    assert rows == expected_rows
    assert len(rows) == 3
    assert {row["status"] for row in rows} == {PASS, WARN, FAIL}
    assert {row["claim_scope"] for row in rows} == {BENCHMARK_CLAIM_SCOPE}
    assert {row["source_class"] for row in rows} == {
        DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS
    }

    counts = benchmark_status_counts(current_pilot_benchmark_records())
    assert counts == {PASS: 1, WARN: 1, FAIL: 1}

    print("PASS: shipped external benchmark CSV matches current pilot scaffold")


def test_validation_summary_labels_scaffold_sanity_evidence() -> None:
    """The summary should keep calibration and ground-truth claims bounded."""

    text = SUMMARY_PATH.read_text(encoding="utf-8")
    lower_text = text.lower()

    assert "songpa_public_demo" in text
    assert "route_plausibility.csv" in text
    assert "external_route_benchmarks.csv" in text
    assert "scaffold/sanity evidence" in lower_text
    assert "documented fallback" in lower_text
    assert "not calibrated" in lower_text
    assert "not ground truth" in lower_text
    assert "live osm" in lower_text
    assert "external routing services" in lower_text
    assert "osrm" in lower_text
    assert "Valhalla" in text

    print("PASS: validation summary labels scaffold sanity evidence")


def synthetic_route_graph(*, length_m: float) -> nx.DiGraph:
    """Return a tiny simulator-style graph with a roughly 1 km straight line."""

    graph = nx.DiGraph()
    graph.graph["region_id"] = "synthetic"
    graph.add_node("A", x=0.0, y=0.0, connector_distance_m=0.0)
    graph.add_node("D", x=0.009, y=0.0, connector_distance_m=0.0)
    graph.add_edge(
        "A",
        "D",
        length_m=length_m,
        t0=length_m / (40.0 * 1000.0 / 60.0),
        capacity=1_000.0,
        base_p_fail=0.0,
        p_fail=0.0,
        mode="road",
        source="synthetic",
        speed_kph=40.0,
        highway="secondary",
    )
    return graph


def current_pilot_records():
    """Build the current adapted pilot graph and return validation records."""

    with REGION_PATH.open("r", encoding="utf-8") as handle:
        region = yaml.safe_load(handle)
    road_graph = load_graphml(CACHE_PATH, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    return evaluate_graph_plausibility(
        simulator_graph,
        region_id=region["region_id"],
    )


def current_pilot_benchmark_records():
    """Build the current adapted pilot graph and return benchmark records."""

    with REGION_PATH.open("r", encoding="utf-8") as handle:
        region = yaml.safe_load(handle)
    road_graph = load_graphml(CACHE_PATH, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    benchmarks = build_fallback_route_benchmarks(simulator_graph)
    return evaluate_external_route_benchmarks(
        simulator_graph,
        benchmarks,
        region_id=region["region_id"],
    )


def record_by_id(records, check_id: str):
    """Return one validation record by check ID."""

    for record in records:
        if record.check_id == check_id:
            return record
    raise AssertionError(f"missing record {check_id!r}")


if __name__ == "__main__":
    test_classify_value_returns_pass_warn_fail()
    test_route_distance_check_can_pass_warn_and_fail()
    test_connector_checks_can_pass_warn_and_fail()
    test_unavailable_route_fails_without_live_services()
    test_fallback_route_benchmarks_are_executable_offline()
    test_external_benchmark_comparison_can_pass_warn_and_fail()
    test_osrm_route_benchmark_builder_uses_injected_fetcher()
    test_shipped_pilot_csv_matches_current_scaffold()
    test_shipped_external_benchmark_csv_matches_current_scaffold()
    test_validation_summary_labels_scaffold_sanity_evidence()
    print("\n=== REALWORLD PLAUSIBILITY TESTS PASSED ===")
