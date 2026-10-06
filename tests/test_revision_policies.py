"""Direct-executable tests for paper-revision policy decisions."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.revision_policies import (
    POLICY_DEFINITIONS,
    PassengerAllocation,
    RailStatus,
    ResourceFrameId,
    RevisionPolicyId,
    RoadFleetAllocation,
    get_policy_definition,
    resolve_passenger_allocation,
    resolve_road_fleet,
)


def test_policy_catalog_has_required_ids_and_thresholds() -> None:
    assert tuple(POLICY_DEFINITIONS) == tuple(RevisionPolicyId)
    assert set(RevisionPolicyId) == {
        RevisionPolicyId.BUS_ONLY,
        RevisionPolicyId.STATIC_MULTIMODAL,
        RevisionPolicyId.PRECHECK_SWITCH,
        RevisionPolicyId.SPLIT_600_400,
        RevisionPolicyId.STATION_FALLBACK_30,
        RevisionPolicyId.STATION_FALLBACK_60,
        RevisionPolicyId.STATION_FALLBACK_90,
    }
    assert get_policy_definition("station_fallback_30").fallback_after_min == 30.0
    assert get_policy_definition("station_fallback_60").fallback_after_min == 60.0
    assert get_policy_definition("station_fallback_90").fallback_after_min == 90.0
    assert get_policy_definition("bus_only").fallback_after_min is None

    _assert_raises(ValueError, lambda: get_policy_definition("missing"), "policy_id")
    print("PASS: revision policy catalog")


def test_configured_bundle_allocations() -> None:
    assert resolve_road_fleet("bus_only", "configured_bundle") == RoadFleetAllocation(
        direct_bus=23,
    )
    assert resolve_road_fleet(
        "static_multimodal", "configured_bundle"
    ) == RoadFleetAllocation(feeder_shuttle=23, last_mile_bus=23)
    assert resolve_road_fleet(
        "precheck_switch", "configured_bundle"
    ) == RoadFleetAllocation(feeder_shuttle=23, last_mile_bus=23)
    assert resolve_road_fleet(
        "station_fallback_30", "configured_bundle"
    ) == RoadFleetAllocation(
        feeder_shuttle=23,
        last_mile_bus=23,
        fallback_bus=23,
    )
    assert resolve_road_fleet(
        "split_600_400", "configured_bundle"
    ) == RoadFleetAllocation(direct_bus=23, feeder_shuttle=23, last_mile_bus=23)
    print("PASS: configured resource bundle")


def test_matched_road_fleet_allocations_total_23() -> None:
    expected_multimodal = RoadFleetAllocation(feeder_shuttle=12, last_mile_bus=11)
    assert resolve_road_fleet(
        RevisionPolicyId.BUS_ONLY,
        ResourceFrameId.MATCHED_ROAD_FLEET,
    ) == RoadFleetAllocation(direct_bus=23)

    for policy_id in ("static_multimodal", "precheck_switch"):
        allocation = resolve_road_fleet(policy_id, "matched_road_fleet")
        assert allocation == expected_multimodal
        assert allocation.total_road_vehicles == 23

    for policy_id in (
        "station_fallback_30",
        "station_fallback_60",
        "station_fallback_90",
    ):
        allocation = resolve_road_fleet(policy_id, "matched_road_fleet")
        assert allocation == RoadFleetAllocation(
            feeder_shuttle=8,
            last_mile_bus=8,
            fallback_bus=7,
        )
        assert allocation.total_road_vehicles == 23

    split = resolve_road_fleet("split_600_400", "matched_road_fleet")
    assert split == RoadFleetAllocation(
        direct_bus=6,
        feeder_shuttle=9,
        last_mile_bus=8,
    )
    assert split.total_road_vehicles == 23
    print("PASS: matched road fleet")


def test_bus_static_and_precheck_passenger_decisions() -> None:
    assert resolve_passenger_allocation(
        "bus_only", 1000, rail_status="unavailable"
    ) == PassengerAllocation(demand=1000, direct_bus=1000)

    assert resolve_passenger_allocation(
        "static_multimodal", 1000, rail_status=RailStatus.AVAILABLE
    ) == PassengerAllocation(demand=1000, rail=1000)
    assert resolve_passenger_allocation(
        "static_multimodal", 1000, rail_status="degraded"
    ) == PassengerAllocation(demand=1000, rail=1000)
    assert resolve_passenger_allocation(
        "static_multimodal", 1000, rail_status="unavailable"
    ) == PassengerAllocation(demand=1000, incomplete=1000)

    assert resolve_passenger_allocation(
        "precheck_switch", 1000, rail_status="available"
    ) == PassengerAllocation(demand=1000, rail=1000)
    assert resolve_passenger_allocation(
        "precheck_switch", 1000, rail_status="unavailable"
    ) == PassengerAllocation(demand=1000, direct_bus=1000)
    print("PASS: bus, static, and precheck decisions")


def test_split_passenger_allocation_is_exact_and_conservative() -> None:
    available = resolve_passenger_allocation(
        "split_600_400", 1000, rail_status="available"
    )
    assert available == PassengerAllocation(demand=1000, direct_bus=400, rail=600)
    assert available.accounted_passengers == available.demand

    unavailable = resolve_passenger_allocation(
        "split_600_400", 1000, rail_status="unavailable"
    )
    assert unavailable == PassengerAllocation(
        demand=1000,
        direct_bus=400,
        incomplete=600,
    )
    assert unavailable.accounted_passengers == unavailable.demand

    odd_demand = resolve_passenger_allocation(
        "split_600_400", 7, rail_status="available"
    )
    assert odd_demand == PassengerAllocation(demand=7, direct_bus=3, rail=4)
    print("PASS: split allocation")


def test_station_fallback_threshold_boundary() -> None:
    before = resolve_passenger_allocation(
        "station_fallback_30",
        1000,
        rail_status="unavailable",
        station_wait_min=29.999,
    )
    at_threshold = resolve_passenger_allocation(
        "station_fallback_30",
        1000,
        rail_status="unavailable",
        station_wait_min=30.0,
    )
    rail_operating = resolve_passenger_allocation(
        "station_fallback_30",
        1000,
        rail_status="degraded",
        station_wait_min=90.0,
    )

    assert before == PassengerAllocation(demand=1000, station_waiting=1000)
    assert at_threshold == PassengerAllocation(demand=1000, station_bus=1000)
    assert rail_operating == PassengerAllocation(demand=1000, rail=1000)

    for policy_id, threshold in (
        ("station_fallback_30", 30.0),
        ("station_fallback_60", 60.0),
        ("station_fallback_90", 90.0),
    ):
        assert resolve_passenger_allocation(
            policy_id,
            45,
            rail_status="unavailable",
            station_wait_min=threshold,
        ).station_bus == 45
    print("PASS: station fallback boundary")


def test_allocations_reject_invalid_values_and_are_deterministic() -> None:
    _assert_raises(ValueError, lambda: RoadFleetAllocation(direct_bus=-1), "non-negative")
    _assert_raises(
        ValueError,
        lambda: PassengerAllocation(demand=10, direct_bus=9),
        "equal demand",
    )
    _assert_raises(
        ValueError,
        lambda: resolve_passenger_allocation("bus_only", True),
        "integer",
    )
    _assert_raises(
        ValueError,
        lambda: resolve_passenger_allocation(
            "station_fallback_30",
            10,
            rail_status="unavailable",
            station_wait_min=-0.1,
        ),
        "non-negative",
    )

    first = resolve_passenger_allocation(
        "station_fallback_60",
        1000,
        rail_status="unavailable",
        station_wait_min=60.0,
    )
    second = resolve_passenger_allocation(
        "station_fallback_60",
        1000,
        rail_status="unavailable",
        station_wait_min=60.0,
    )
    assert first == second
    print("PASS: allocation guards and determinism")


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
    test_policy_catalog_has_required_ids_and_thresholds()
    test_configured_bundle_allocations()
    test_matched_road_fleet_allocations_total_23()
    test_bus_static_and_precheck_passenger_decisions()
    test_split_passenger_allocation_is_exact_and_conservative()
    test_station_fallback_threshold_boundary()
    test_allocations_reject_invalid_values_and_are_deterministic()
    print("\n=== REVISION POLICY TESTS PASSED ===")
