"""Composable multi-service pipeline tests (Phase 2.3-2.6).

Exercises the generalized service engine with a NON-rail mode (sea) to prove
the composable pipeline (``_run_service_alternative`` / ``_run_fixed_headway_service``)
runs any fixed-headway service uniformly, and that non-rail modes populate the
additive ``service_breakdown`` metrics while rail stays on legacy train_*.

Direct-executable (no pytest): ``python tests/test_composable_service_pipeline.py``.
"""

import copy
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.pilot_experiments import (  # noqa: E402
    apply_pilot_demand_fleet_profiles,
    load_pilot_inputs,
    make_pilot_base_config,
)
from src.scenario import ServiceSpec, run_scenario  # noqa: E402
from src.policies import StrictPolicy  # noqa: E402

REGION = "data/regions/goseong_mobilization.yaml"
# Phase 2: must stay in lockstep with scripts/generate_phase23_oracle.py::CACHE
# (both = the 표준노드링크 canonical cache). If they diverge, the oracle holds
# nodelink KPIs while this test re-runs on a different graph -> mismatch.
CACHE = "data/cache/goseong_nodelink_road.graphml"
OVERRIDES = "data/parameters/road_class_overrides.csv"


def _base_config():
    inputs = load_pilot_inputs(
        region_path=REGION,
        cache_path=CACHE,
        road_class_overrides_path=OVERRIDES,
    )
    # Canonical pilot base config — must match the frozen oracle
    # (results/_phase23_baseline/oracle.json). make_pilot_base_config sets
    # experiment.time_limit=1440 (24h wartime mobilization window); do NOT
    # override it or the byte-identity sha drifts. road_class_overrides_path
    # must match the
    # oracle generator so the test graph and the oracle share the same evidenced
    # road inputs. See test_byte_identity_against_oracle.
    base = apply_pilot_demand_fleet_profiles(make_pilot_base_config(inputs.region))[0]
    return inputs, base


def test_service_spec_value_object_is_frozen() -> None:
    spec = ServiceSpec(
        mode="sea",
        access_id="S",
        egress_id="R",
        travel_time_min=200.0,
        headway_min=60.0,
        capacity=300,
    )
    assert spec.mode == "sea"
    assert spec.first_departure_min is None
    try:
        spec.mode = "air"  # type: ignore[misc]
        raise AssertionError("ServiceSpec must be frozen")
    except AttributeError:
        pass
    print("PASS: ServiceSpec is a frozen value object")


def test_sea_service_alternative_runs_and_populates_service_breakdown() -> None:
    """A sea-mode multimodal run must complete and write sea service counters."""

    inputs, base = _base_config()
    cfg = copy.deepcopy(base)
    # Reuse the real graph's S (rail access) and R (rail egress) road
    # connectivity, but run the service leg as a sea ferry (mode='sea').
    cfg["multimodal"]["service_mode"] = "sea"
    cfg["multimodal"]["service"] = {
        "access_id": "S",
        "egress_id": "R",
        "travel_time_min": 200.0,
        "headway_min": 60.0,
        "capacity": 300,
    }
    result = run_scenario(
        G=inputs.graph,
        config=cfg,
        scenario_type="multimodal",
        policy=StrictPolicy(),
        params={"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75},
        seed=1101,
    )
    breakdown = result["service_breakdown"]
    assert "sea" in breakdown, f"expected sea in service_breakdown, got {breakdown}"
    assert breakdown["sea"]["trips"] > 0, f"expected sea trips>0, got {breakdown}"
    # structural invariant: each sea trip records exactly travel_time_min minutes
    # (catches a minutes-recording regression that trips>0 alone would miss).
    assert breakdown["sea"]["minutes"] == breakdown["sea"]["trips"] * 200.0, (
        f"sea minutes must equal trips x travel_time (200): "
        f"got {breakdown['sea']}"
    )
    # rail legacy counters must NOT be touched by a sea run
    assert result["train_trips"] == 0, f"sea run must not write train_trips, got {result['train_trips']}"
    assert result["completion_rate"] > 0.0
    # NOTE: this proves the generic fixed-headway engine runs under a non-rail
    # label; it does NOT model a sea network (no sea graph edges) — that is
    # Phase 3. The service leg is pure timing arithmetic, not routing.
    print(
        f"PASS: sea service alternative runs ({breakdown['sea']['trips']} sea trips, "
        f"completion={result['completion_rate']:.2f}, train_trips=0)"
    )


def test_rail_default_stays_on_legacy_counters() -> None:
    """Default multimodal (no service_mode) stays on rail / train_* counters."""

    inputs, base = _base_config()
    result = run_scenario(
        G=inputs.graph,
        config=copy.deepcopy(base),
        scenario_type="multimodal",
        policy=StrictPolicy(),
        params={"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75},
        seed=1101,
    )
    assert result["train_trips"] > 0
    assert result["service_breakdown"] == {}, (
        f"rail run must leave service_breakdown empty, got {result['service_breakdown']}"
    )
    print(f"PASS: rail default stays on train_* (trips={result['train_trips']}, breakdown empty)")


def test_byte_identity_against_oracle() -> None:
    """Full-key rail/bus identity vs the frozen oracle (invariant #1).

    Pins invariant #1: the Phase 2 contract widening must not perturb the
    legacy rail/bus result dict. Loads ``results/_phase23_baseline/oracle.json``
    and asserts, on the 6 frozen runs (bus_only / multimodal x seeds 1101-1103):

      (a) the oracle is present + internally consistent — its ``runs_sha256``
          matches a sha256 of its own ``runs`` block, so a hand-edit to any KPI
          value (the silent-regeneration attack) is detected;
      (b) the re-built base config hashes to ``base_config_sha256`` (config
          drift guard);
      (c) every run reproduces the FULL ``MetricsCollector.as_dict()`` key set
          (shrink/add detection: the oracle cannot be weakened by dropping a
          key, nor grow a key the engine no longer emits) AND every value
          matches (numeric ``abs < 1e-9``; nested dicts like
          ``service_breakdown`` by equality).

    The oracle is the single source of truth and is committed (regenerate only
    via ``scripts/generate_phase23_oracle.py`` on a legitimate baseline change).
    """

    import json

    from src.realworld.pilot_experiments import _json_sha256

    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_phase23_oracle import ORACLE_RUN_SPECS  # noqa: E402

    oracle_path = ROOT / "results" / "_phase23_baseline" / "oracle.json"
    if not oracle_path.exists():
        raise AssertionError(
            f"missing oracle {oracle_path}; regenerate with "
            "'python scripts/generate_phase23_oracle.py' (the byte-identity "
            "guard cannot run without the committed oracle)"
        )
    oracle = json.loads(oracle_path.read_text(encoding="utf-8"))

    # (a) oracle integrity: runs_sha256 must match the runs block, else the
    # committed oracle was hand-edited (silent-regeneration attack).
    runs = oracle["runs"]
    runs_sha = _json_sha256(runs)
    assert runs_sha == oracle["runs_sha256"], (
        "oracle runs_sha256 mismatch: the committed oracle's runs block no "
        f"longer matches its stamp ({runs_sha[:8]}... vs "
        f"{oracle['runs_sha256'][:8]}...). If the baseline changed "
        "intentionally, regenerate via scripts/generate_phase23_oracle.py."
    )

    inputs, base = _base_config()
    # (b) base config must match the frozen oracle sha (config drift guard).
    actual_sha = _json_sha256(base)
    assert actual_sha == oracle["base_config_sha256"], (
        "base config sha drift: the pilot base config no longer matches the "
        f"frozen oracle ({actual_sha[:8]}... vs "
        f"{oracle['base_config_sha256'][:8]}...)"
    )

    # Run specs are the SINGLE SOURCE (shared with the generator) so the test
    # re-runs exactly the frozen set: 6 clean baseline + 2 road-damage runs.
    assert set(runs.keys()) == {spec["key"] for spec in ORACLE_RUN_SPECS}, (
        "oracle run keys do not match ORACLE_RUN_SPECS; regenerate the oracle"
    )
    for spec in ORACLE_RUN_SPECS:
        cfg = copy.deepcopy(base)
        failure = spec.get("failure")
        if failure:
            cfg["failure"] = copy.deepcopy(failure)
        params = {
            "s": 1.0,
            "p_fail_scale": spec.get("p_fail_scale", 0.0),
            "sigma": 0.75,
        }
        result = run_scenario(
            G=inputs.graph,
            config=cfg,
            scenario_type=spec["scenario_type"],
            policy=StrictPolicy(),
            params=params,
            seed=spec["seed"],
        )
        key = spec["key"]
        expected = runs[key]
        # (c) full key-set identity: oracle weakened (drop) OR engine changed a
        # key (add/rename) both fail loudly here.
        assert set(result.keys()) == set(expected.keys()), (
            f"{key}: result key set {sorted(result)} != oracle key set "
            f"{sorted(expected)} (oracle shrink or as_dict drift)"
        )
        for kpi, want in expected.items():
            got = result[kpi]
            if isinstance(want, dict):
                assert got == want, f"{key}.{kpi} dict mismatch: {got!r} vs {want!r}"
            else:
                assert abs(float(got) - float(want)) < 1e-9, (
                    f"{key}.{kpi} drift: got {got!r}, oracle {want!r}"
                )
    print(
        f"PASS: full-key identity vs oracle holds "
        f"({len(runs)} runs x {len(next(iter(runs.values())))} keys; runs_sha {runs_sha[:8]}..., "
        f"cfg {actual_sha[:8]}...)"
    )


def test_non_rail_service_mode_without_service_config_raises() -> None:
    """A non-rail service_mode without a service mapping must fail loudly."""

    inputs, base = _base_config()
    cfg = copy.deepcopy(base)
    cfg["multimodal"]["service_mode"] = "air"
    # no config['multimodal']['service']
    try:
        run_scenario(
            G=inputs.graph,
            config=cfg,
            scenario_type="multimodal",
            policy=StrictPolicy(),
            params={"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75},
            seed=1101,
        )
        raise AssertionError("expected ValueError for air mode without service config")
    except ValueError as exc:
        assert "service_mode" in str(exc) and "multimodal.service" in str(exc), (
            f"unexpected error: {exc!r}"
        )
    print("PASS: non-rail service_mode without service config raises ValueError")


def test_unsupported_service_mode_raises() -> None:
    """A service_mode outside {rail, sea, air} must raise, not silently run."""

    inputs, base = _base_config()
    cfg = copy.deepcopy(base)
    cfg["multimodal"]["service_mode"] = "bus"
    try:
        run_scenario(
            G=inputs.graph,
            config=cfg,
            scenario_type="multimodal",
            policy=StrictPolicy(),
            params={"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75},
            seed=1101,
        )
        raise AssertionError("expected ValueError for unsupported service_mode 'bus'")
    except ValueError as exc:
        assert "service_mode" in str(exc) and "not a supported service mode" in str(exc), (
            f"unexpected error: {exc!r}"
        )
    print("PASS: unsupported service_mode raises ValueError (no silent breakdown write)")


def test_empty_rail_link_raises_clean_value_error() -> None:
    """A rail-default multimodal config with no rail_link must raise ValueError."""

    from src.scenario import _service_spec_from_legacy_rail

    try:
        _service_spec_from_legacy_rail({"network": {"rail_link": []}, "multimodal": {}})
        raise AssertionError("expected ValueError for empty rail_link")
    except ValueError as exc:
        assert "rail_link" in str(exc) or "service_mode" in str(exc)
    # missing key entirely must also raise ValueError (not KeyError/IndexError)
    try:
        _service_spec_from_legacy_rail({"network": {}, "multimodal": {}})
        raise AssertionError("expected ValueError for missing rail_link")
    except ValueError:
        pass
    print("PASS: empty/missing rail_link raises clean ValueError (not IndexError)")


def test_sea_only_region_simulator_node_ids_is_rail_optional() -> None:
    """A sea-only region (no rail) must expose simulator_node_ids without raising."""

    from src.realworld import (
        BoundarySpec,
        PortPointSpec,
        RegionServiceSpec,
        RegionSpec,
        ZoneSpec,
    )

    sea = RegionServiceSpec(
        mode="sea",
        access=PortPointSpec(id="sea_acc", lat=37.2, lon=127.2),
        egress=PortPointSpec(id="sea_egr", lat=37.7, lon=127.7),
        travel_time_min=200.0,
        headway_min=60.0,
        capacity_pax_per_unit=300,
    )
    region = RegionSpec(
        region_id="sea_only_probe",
        name="Sea Only Probe",
        boundary=BoundarySpec(type="bbox", north=38.0, south=37.0, east=128.0, west=127.0),
        assembly_zones=(ZoneSpec(id="A", lat=37.1, lon=127.1),),
        destination_zones=(ZoneSpec(id="D", lat=37.8, lon=127.8),),
        region_services=(sea,),
    )
    nodes = region.simulator_node_ids
    assert nodes == {
        "assembly": "A",
        "destination": "D",
        "sea_access": "sea_acc",
        "sea_egress": "sea_egr",
    }, f"unexpected sea-only simulator_node_ids: {nodes}"
    assert "rail_access" not in nodes and "rail_egress" not in nodes
    print("PASS: sea-only region simulator_node_ids is rail-optional (no rail keys)")


if __name__ == "__main__":
    test_service_spec_value_object_is_frozen()
    test_sea_service_alternative_runs_and_populates_service_breakdown()
    test_rail_default_stays_on_legacy_counters()
    test_byte_identity_against_oracle()
    test_non_rail_service_mode_without_service_config_raises()
    test_unsupported_service_mode_raises()
    test_empty_rail_link_raises_clean_value_error()
    test_sea_only_region_simulator_node_ids_is_rail_optional()
    print("\n=== COMPOSABLE SERVICE PIPELINE TESTS PASSED ===")
