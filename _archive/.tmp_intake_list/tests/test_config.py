"""Configuration schema smoke tests."""

import os
import sys

import yaml
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network import build_network, network_variant_levels, resolve_network_spec


CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml",
)


def load_config() -> dict:
    """Load the repository config."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_operational_namespaces_exist():
    """New operational config namespaces should be present."""
    config = load_config()
    expected = {
        "bus": {
            "first_departure_min",
            "dispatch_interval_min",
            "fleet_size",
            "turnaround_min",
        },
        "multimodal": {
            "shuttle_first_departure_min",
            "shuttle_dispatch_interval_min",
            "shuttle_fleet_size",
            "transfer_time_min",
            "transfer_per_passenger_min",
            "rail_first_departure_min",
            "lastmile_dispatch_interval_min",
            "lastmile_fleet_size",
            "lastmile_turnaround_min",
            "lastmile_vehicle_capacity",
            "lastmile_first_departure_min",
        },
        "traffic": {"volume_window_min", "background_volume"},
        "failure": {
            "mode",
            "capacity_reduction_factor",
            "mode_levels",
            "capacity_reduction_factor_levels",
        },
        "metrics": {"late_penalty_min"},
    }

    for namespace, keys in expected.items():
        assert namespace in config, f"Missing config namespace: {namespace}"
        missing = keys - set(config[namespace])
        assert not missing, f"Missing config keys in {namespace}: {sorted(missing)}"

    print("PASS: Operational namespaces exist")


def test_failure_rate_levels_are_multipliers():
    """failure_rate.levels should be documented as p_fail_scale multipliers."""
    config = load_config()
    failure_rate = config["failure_rate"]

    assert failure_rate["parameter"] == "p_fail_scale"
    assert failure_rate["semantics"] == "multiplier"
    assert all(level >= 0 for level in failure_rate["levels"])

    max_base_p_fail = max(
        link[4]
        for variant in config["network"]["variants"]
        for link in resolve_network_spec(config, variant)["road_links"]
    )
    max_level = max(failure_rate["levels"])
    assert max_base_p_fail * max_level <= 1.0

    print("PASS: Failure-rate levels are multipliers")


def test_network_variants_are_declared_and_routable():
    """Named variants should preserve required bus and multimodal paths."""
    config = load_config()
    required = {
        "baseline",
        "matched_redundancy",
        "multimodal_redundant_lastmile",
        "bus_single_corridor",
    }

    assert required <= set(config["network"]["variants"])
    assert set(network_variant_levels(config)) <= required

    for variant in required:
        G = build_network(config, variant=variant)
        road = _road_subgraph(G)
        assert G.graph["network_variant"] == variant
        assert nx.has_path(road, "A", "D"), f"{variant}: missing bus road path"
        assert nx.has_path(road, "A", "S"), f"{variant}: missing shuttle road path"
        assert G.has_edge("S", "R"), f"{variant}: missing rail link"
        assert nx.has_path(road, "R", "D"), f"{variant}: missing last-mile road path"

    matched = _road_subgraph(build_network(config, variant="matched_redundancy"))
    assert _simple_path_count(matched, "R", "D") >= 2
    single = _road_subgraph(build_network(config, variant="bus_single_corridor"))
    assert _simple_path_count(single, "A", "D") == 1

    print("PASS: Network variants are declared and routable")


def test_failure_sensitivity_levels_are_explicit():
    """Failure sensitivity axes should keep blocked and degraded semantics separate."""
    config = load_config()
    failure = config["failure"]

    assert failure["mode"] in {"blocked", "capacity_reduction"}
    assert set(failure["mode_levels"]) == {"blocked", "capacity_reduction"}
    assert all(0 < factor <= 1 for factor in failure["capacity_reduction_factor_levels"])

    print("PASS: Failure sensitivity levels are explicit")


def test_backward_compatible_legacy_keys_exist():
    """Legacy keys consumed by current code should remain available."""
    config = load_config()

    assert "network" in config
    assert "personnel" in config
    assert "bpr" in config
    assert "congestion_scale" in config
    assert "failure_rate" in config
    assert "lateness" in config
    assert "policies" in config
    assert "experiment" in config
    assert "assembly_time" in config["personnel"]
    assert "levels" in config["failure_rate"]

    print("PASS: Legacy keys remain available")


def test_operational_values_in_valid_ranges():
    """Basic range checks catch invalid values before scenario runs."""
    config = load_config()

    assert config["bus"]["dispatch_interval_min"] >= 0
    assert config["bus"]["first_departure_min"] >= 0
    assert config["bus"]["fleet_size"] >= 1
    assert config["bus"]["turnaround_min"] >= 0
    assert config["multimodal"]["shuttle_first_departure_min"] >= 0
    assert config["multimodal"]["shuttle_dispatch_interval_min"] >= 0
    assert config["multimodal"]["shuttle_fleet_size"] >= 1
    assert config["multimodal"]["transfer_time_min"] >= 0
    assert config["multimodal"]["transfer_per_passenger_min"] >= 0
    rail_first = config["multimodal"]["rail_first_departure_min"]
    assert rail_first is None or rail_first >= 0
    assert config["multimodal"]["lastmile_dispatch_interval_min"] >= 0
    assert config["multimodal"]["lastmile_fleet_size"] >= 1
    assert config["multimodal"]["lastmile_turnaround_min"] >= 0
    assert config["multimodal"]["lastmile_vehicle_capacity"] >= 1
    lastmile_first = config["multimodal"]["lastmile_first_departure_min"]
    assert lastmile_first is None or lastmile_first >= 0
    assert config["traffic"]["volume_window_min"] > 0
    assert config["traffic"]["background_volume"] >= 0
    assert config["failure"]["mode"] in {"blocked", "capacity_reduction"}
    assert set(config["failure"]["mode_levels"]) <= {"blocked", "capacity_reduction"}
    assert 0 < config["failure"]["capacity_reduction_factor"] <= 1
    assert all(
        0 < factor <= 1
        for factor in config["failure"]["capacity_reduction_factor_levels"]
    )
    assert config["metrics"]["late_penalty_min"] >= 0

    print("PASS: Operational values are in valid ranges")


def _road_subgraph(G):
    edges = [
        (u, v)
        for u, v, data in G.edges(data=True)
        if data.get("mode") == "road"
    ]
    return G.edge_subgraph(edges).copy()


def _simple_path_count(G, source, target):
    return sum(1 for _ in nx.all_simple_paths(G, source, target))


if __name__ == "__main__":
    test_operational_namespaces_exist()
    test_failure_rate_levels_are_multipliers()
    test_network_variants_are_declared_and_routable()
    test_failure_sensitivity_levels_are_explicit()
    test_backward_compatible_legacy_keys_exist()
    test_operational_values_in_valid_ranges()
    print("\n=== CONFIG TESTS PASSED ===")
