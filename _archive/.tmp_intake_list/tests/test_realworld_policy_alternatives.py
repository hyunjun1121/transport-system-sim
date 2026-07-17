"""Tests for real-world policy-alternative definitions and config variants."""

from __future__ import annotations

from copy import deepcopy
import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.policy_alternatives import (
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    REQUIRED_COLUMNS,
    REQUIRED_POLICY_IDS,
    PolicyAlternative,
    build_policy_config_variant,
    config_for_policy_alternative,
    get_policy_alternative,
    load_policy_alternatives,
    validate_policy_alternatives,
)


def test_default_policy_table_schema_and_required_coverage() -> None:
    """The committed table should expose the required policy alternatives."""

    alternatives = load_policy_alternatives()
    policy_ids = {alternative.policy_id for alternative in alternatives}

    assert REQUIRED_POLICY_IDS <= policy_ids
    assert len(policy_ids) == len(alternatives)
    assert {"bus_only", "multimodal"} <= {
        alternative.scenario_type for alternative in alternatives
    }
    assert all(alternative.decision_interpretation for alternative in alternatives)
    assert all(alternative.claim_boundary for alternative in alternatives)

    with DEFAULT_POLICY_ALTERNATIVES_PATH.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == REQUIRED_COLUMNS

    print("PASS: policy table schema and required coverage")


def test_schema_validation_rejects_missing_required_column() -> None:
    """Missing CSV columns should fail before experiment code uses the table."""

    with TemporaryDirectory() as directory:
        path = Path(directory) / "bad_policy.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["policy_id", "scenario_type", "decision_interpretation"])
            writer.writerow(["bus_only", "bus_only", "Use direct buses with baseline inputs."])

        _assert_raises(
            ValueError,
            lambda: load_policy_alternatives(path),
            "invalid policy schema",
        )

    print("PASS: schema validation rejects missing columns")


def test_validation_rejects_universal_winner_language() -> None:
    """Policy descriptions should not claim a universal winner."""

    alternatives = load_policy_alternatives()
    bad = [
        _replace_claim(
            alternative,
            "This policy is always superior to every other transport option.",
        )
        if alternative.policy_id == "bus_only"
        else alternative
        for alternative in alternatives
    ]

    _assert_raises(
        ValueError,
        lambda: validate_policy_alternatives(bad),
        "universal winner",
    )

    print("PASS: policy language rejects universal winner claims")


def test_policy_application_does_not_mutate_base_config() -> None:
    """Applying a policy should return a deep-copied variant config."""

    alternatives = load_policy_alternatives()
    base_config = _base_config()
    original = deepcopy(base_config)

    variant = build_policy_config_variant(
        base_config,
        "multimodal_lastmile_redundancy",
        alternatives,
    )

    assert base_config == original
    assert variant.config is not base_config
    assert variant.policy_id == "multimodal_lastmile_redundancy"
    assert variant.scenario_type == "multimodal"
    assert variant.config["multimodal"]["lastmile_fleet_size"] == 6
    assert base_config["multimodal"]["lastmile_fleet_size"] == 4

    print("PASS: policy application is non-mutating")


def test_intended_knob_changes_for_policy_variants() -> None:
    """Each policy row should modify only the intended deterministic knobs."""

    alternatives = load_policy_alternatives()
    base_config = _base_config()

    baseline = config_for_policy_alternative(
        base_config,
        "baseline_multimodal",
        alternatives,
    )
    assert baseline == base_config
    assert baseline is not base_config

    lastmile = config_for_policy_alternative(
        base_config,
        "multimodal_lastmile_redundancy",
        alternatives,
    )
    assert lastmile["multimodal"]["lastmile_fleet_size"] == 6
    assert lastmile["multimodal"]["shuttle_fleet_size"] == 4
    assert lastmile["network"]["rail_link"] == base_config["network"]["rail_link"]

    staggered = config_for_policy_alternative(
        base_config,
        "staggered_or_adaptive_dispatch",
        alternatives,
    )
    assert staggered["multimodal"]["shuttle_dispatch_interval_min"] == 10.0
    assert staggered["multimodal"]["lastmile_dispatch_interval_min"] == 0.0
    assert staggered["multimodal"]["lastmile_fleet_size"] == 4

    bus_redundancy = build_policy_config_variant(
        base_config,
        "bus_corridor_redundancy",
        alternatives,
    )
    assert bus_redundancy.scenario_type == "bus_only"
    assert bus_redundancy.config["network"]["variant"] == "matched_redundancy"
    assert bus_redundancy.config["bus"]["fleet_size"] == 4

    rail_stress = config_for_policy_alternative(
        base_config,
        "rail_delay_or_partial_unavailability",
        alternatives,
    )
    assert rail_stress["network"]["rail_link"][0][2] == 25.0
    assert rail_stress["network"]["rail_link"][0][3] == 15.0
    assert rail_stress["network"]["rail_link"][0][4] == 75

    shortage = config_for_policy_alternative(
        base_config,
        "fleet_shortage_stress",
        alternatives,
    )
    assert shortage["multimodal"]["shuttle_fleet_size"] == 3
    assert shortage["multimodal"]["lastmile_fleet_size"] == 3
    assert shortage["bus"]["fleet_size"] == 4

    print("PASS: policy variants change intended knobs")


def test_lookup_unknown_policy_reports_available_ids() -> None:
    """Unknown IDs should fail clearly for downstream experiment scripts."""

    alternatives = load_policy_alternatives()

    _assert_raises(
        KeyError,
        lambda: get_policy_alternative("not_a_policy", alternatives),
        "available=",
    )

    print("PASS: unknown policy lookup is explicit")


def _replace_claim(alternative: PolicyAlternative, claim: str) -> PolicyAlternative:
    return PolicyAlternative(
        policy_id=alternative.policy_id,
        scenario_type=alternative.scenario_type,
        decision_interpretation=alternative.decision_interpretation,
        claim_boundary=claim,
        notes=alternative.notes,
        knobs=alternative.knobs,
    )


def _base_config() -> dict:
    """Return a small scenario config with all policy-controlled namespaces."""

    return {
        "network": {
            "nodes": ["A", "S", "R", "D"],
            "variant": "baseline",
            "rail_link": [["S", "R", 20.0, 10.0, 100]],
            "road_links": [],
        },
        "bus": {
            "first_departure_min": 0.0,
            "dispatch_interval_min": 5.0,
            "fleet_size": 4,
            "turnaround_min": 5.0,
        },
        "multimodal": {
            "shuttle_first_departure_min": 0.0,
            "shuttle_dispatch_interval_min": 5.0,
            "shuttle_fleet_size": 4,
            "shuttle_turnaround_min": 5.0,
            "transfer_time_min": 5.0,
            "transfer_per_passenger_min": 0.0,
            "rail_first_departure_min": None,
            "lastmile_first_departure_min": None,
            "lastmile_dispatch_interval_min": 5.0,
            "lastmile_fleet_size": 4,
            "lastmile_turnaround_min": 5.0,
            "lastmile_vehicle_capacity": 4,
        },
        "traffic": {
            "background_volume": 100.0,
        },
        "failure": {
            "mode": "blocked",
            "capacity_reduction_factor": 0.5,
        },
    }


def _assert_raises(
    expected: type[BaseException],
    func,
    expected_text: str,
) -> None:
    try:
        func()
    except expected as exc:
        assert expected_text in str(exc)
        return
    raise AssertionError(f"expected {expected.__name__} containing {expected_text!r}")


if __name__ == "__main__":
    test_default_policy_table_schema_and_required_coverage()
    test_schema_validation_rejects_missing_required_column()
    test_validation_rejects_universal_winner_language()
    test_policy_application_does_not_mutate_base_config()
    test_intended_knob_changes_for_policy_variants()
    test_lookup_unknown_policy_reports_available_ids()
    print("\n=== REALWORLD POLICY ALTERNATIVE TESTS PASSED ===")
