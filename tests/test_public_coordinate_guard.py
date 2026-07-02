"""Public-coordinate policy guard tests (Phase 2.0 security precondition).

Mobilization corridors must use only public administrative centroids and public
transport networks. The guard rejects restricted / sensitive / privacy-review
coordinate sources before any sea/air mode or multi-corridor expansion, so no
military unit coordinates, OOB, or movement schedules can enter the simulator.

Direct-executable (no pytest): ``python tests/test_public_coordinate_guard.py``.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld import load_region_spec  # noqa: E402
from src.realworld.types import (  # noqa: E402
    PUBLIC_COORDINATE_LEVELS,
    assert_public_coordinate_policy,
)


def _minimal_region_dict() -> dict:
    """Minimal valid region dict (public-coordinate compliant by default)."""

    return {
        "region_id": "guard_probe",
        "name": "Guard Probe Region",
        "sensitivity_level": "public",
        "boundary": {
            "type": "bbox",
            "north": 37.53,
            "south": 37.49,
            "east": 127.14,
            "west": 127.08,
        },
        "assembly_zones": [{"id": "A", "lat": 37.51, "lon": 127.10}],
        "destination_zones": [{"id": "D", "lat": 37.52, "lon": 127.13}],
        "rail": {
            "access": {"id": "S", "lat": 37.51, "lon": 127.11},
            "egress": {"id": "R", "lat": 37.52, "lon": 127.12},
            "travel_time_min": 40,
            "headway_min": 10,
            "capacity_pax_per_train": 500,
        },
    }


def _region(sensitivity_level: str | None = None, coordinate_class: str | None = None):
    spec = _minimal_region_dict()
    if sensitivity_level is not None:
        spec["sensitivity_level"] = sensitivity_level
    if coordinate_class is not None:
        spec["metadata"] = {"coordinate_class": coordinate_class}
    return load_region_spec(spec)


def _expect_reject(fn, fragment: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), f"expected {fragment!r} in {exc!r}"
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


def test_public_coordinate_levels_pass() -> None:
    """Only public-coordinate sensitivity levels may enter the simulator."""

    assert PUBLIC_COORDINATE_LEVELS == frozenset(
        {"unspecified", "non_sensitive", "public", "synthetic"}
    )
    for level in ("unspecified", "non_sensitive", "public", "synthetic"):
        assert_public_coordinate_policy(_region(level))  # must not raise
    print("PASS: public-coordinate levels pass the guard")


def test_restricted_and_review_levels_rejected() -> None:
    """Restricted / sensitive / privacy-review sources must be rejected."""

    for level in ("restricted", "sensitive_review_required", "privacy_review_required"):
        _expect_reject(
            lambda level=level: assert_public_coordinate_policy(_region(level)),
            "non-public",
        )
    print("PASS: restricted/review coordinate sources rejected")


def test_non_public_coordinate_class_marker_rejected() -> None:
    """An explicit non-public coordinate_class marker is rejected even at public level."""

    _expect_reject(
        lambda: assert_public_coordinate_policy(
            _region("public", coordinate_class="military_unit")
        ),
        "coordinate_class",
    )
    # explicit public marker is fine
    assert_public_coordinate_policy(_region("public", coordinate_class="public"))
    print("PASS: non-public coordinate_class marker rejected, public accepted")


def test_non_public_port_coordinate_class_rejected_at_construction() -> None:
    """A service port with a non-public coordinate_class is rejected at build.

    The security boundary (C1) must reject a ``coordinate_class='military_unit'``
    port at PortPointSpec construction, before any region build or simulator
    entry — no real-unit coordinates, OOB, or movement schedules can enter.
    """

    from src.realworld import PortPointSpec

    spec = _minimal_region_dict()
    spec.pop("rail", None)
    spec["region_services"] = [
        {
            "mode": "rail",
            "access": {
                "id": "S",
                "lat": 37.51,
                "lon": 127.11,
                "coordinate_class": "military_unit",
            },
            "egress": {"id": "R", "lat": 37.52, "lon": 127.12},
            "travel_time_min": 40,
            "headway_min": 10,
            "capacity_pax_per_unit": 500,
        }
    ]
    # loading via the public loader must reject the hostile port at construction
    _expect_reject(lambda: load_region_spec(spec), "coordinate_class")
    # direct construction is also rejected (no bypass via the dataclass)
    try:
        PortPointSpec(id="S", lat=37.51, lon=127.11, coordinate_class="military_unit")
        raise AssertionError("expected ValueError for military_unit port")
    except ValueError as exc:
        assert "coordinate_class" in str(exc), f"unexpected: {exc!r}"
    # synthetic port coordinate_class is permitted (synthetic fixtures)
    PortPointSpec(id="S", lat=37.51, lon=127.11, coordinate_class="synthetic")
    print("PASS: non-public port coordinate_class rejected at construction")


def test_legacy_rail_hostile_coordinate_class_rejected() -> None:
    """A legacy ``rail:`` region with a hostile port coordinate_class is rejected (F1).

    The legacy rail shim forwards coordinate_class to the rebuilt PortPointSpec,
    so a ``rail.access.coordinate_class: military_unit`` region is rejected at
    load — consistent with the region_services path, with NO silent
    normalization to 'public'.
    """

    spec = _minimal_region_dict()
    spec["rail"]["access"]["coordinate_class"] = "military_unit"
    _expect_reject(lambda: load_region_spec(spec), "coordinate_class")
    print("PASS: legacy-rail hostile coordinate_class rejected (no silent normalize)")


def test_restricted_region_rejected_at_construction_not_only_at_guard() -> None:
    """A restricted region is rejected at RegionSpec construction (C4).

    The public-coordinate policy runs in RegionSpec.__post_init__, so every
    public entry path (load_region_spec / registry / get_region_spec /
    build_simulator_graph) enforces it — a restricted region cannot even be
    loaded into a validated record, not merely blocked at a single guard call.
    """

    _expect_reject(lambda: _region("restricted"), "non-public")
    print("PASS: restricted region rejected at construction (all entry paths)")


def test_goseong_case_study_region_passes_guard() -> None:
    """The real Goseong case-study region (public centroids) must pass."""

    import yaml

    spec = yaml.safe_load(
        (ROOT / "data" / "regions" / "goseong_mobilization.yaml").read_text(
            encoding="utf-8"
        )
    )
    region = load_region_spec(spec)
    assert_public_coordinate_policy(region)  # must not raise
    print(
        f"PASS: goseong case-study region passes (sensitivity_level="
        f"{region.sensitivity_level!r})"
    )


if __name__ == "__main__":
    test_public_coordinate_levels_pass()
    test_restricted_and_review_levels_rejected()
    test_non_public_coordinate_class_marker_rejected()
    test_non_public_port_coordinate_class_rejected_at_construction()
    test_legacy_rail_hostile_coordinate_class_rejected()
    test_restricted_region_rejected_at_construction_not_only_at_guard()
    test_goseong_case_study_region_passes_guard()
    print("\n=== PUBLIC COORDINATE GUARD TESTS PASSED ===")
