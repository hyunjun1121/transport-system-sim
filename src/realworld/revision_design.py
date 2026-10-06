"""Strict, immutable loader for paper-revision experiment design.

The revision manifest is executable research input.  Silent key additions or
unsafe output paths therefore fail at load time instead of being ignored by a
campaign runner.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import math
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any


SUPPORTED_SCHEMA_VERSION = 1
CANONICAL_RESULTS_ROOT = PurePosixPath("results/realworld_pilot_nodelink")
GRAPH_SCOPES = frozenset({"top3", "top5", "top10", "full"})
EXPECTED_CAMPAIGNS = (
    "paired_reanalysis",
    "graph_scope",
    "break_even",
    "break_even_fine",
    "demand_fleet",
    "road_rail_map",
    "random_threat_outer",
    "adaptive_policies",
    "morris",
    "scale_sensitivity",
    "path_interdiction_threat",
)
EXPECTED_MORRIS_FACTORS = (
    "road_longhaul_multiplier",
    "rail_travel_multiplier",
    "demand",
    "road_fleet_total",
    "transfer_time_min",
    "arrival_sigma",
)

_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "design_id",
        "output_root",
        "claim_boundary",
        "canonical_results_read_only",
        "seed_blocks",
        "defaults",
        "campaigns",
    }
)
_SEED_BLOCK_KEYS = frozenset({"arrival", "threat", "bootstrap", "morris"})
_DEFAULT_KEYS = frozenset(
    {
        "graph_scope",
        "corridor_path_count",
        "graph_scope_method",
        "graph_scope_interpretation",
        "departure_policy_id",
        "resource_frame",
        "return_strategy",
        "rail_status",
        "bootstrap_replicates",
        "confidence",
    }
)
_CAMPAIGN_KEYS: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        "paired_reanalysis": frozenset(
            {"purpose", "policies", "resource_frames", "scenario_ids"}
        ),
        "graph_scope": frozenset(
            {
                "purpose",
                "graph_scopes",
                "scenario_ids",
                "freeze_selected_edges_from",
                "smoke_arrival_seed_count",
                "full_arrival_seed_count",
                "full_graph_arrival_seed_count",
            }
        ),
        "break_even": frozenset(
            {
                "purpose",
                "road_multipliers",
                "target_segment",
                "policies",
                "resource_frames",
            }
        ),
        "demand_fleet": frozenset(
            {"purpose", "demand", "road_fleet_total", "resource_frames", "policies"}
        ),
        "road_rail_map": frozenset(
            {
                "purpose",
                "road_multipliers",
                "rail_conditions",
                "policies",
                "resource_frames",
            }
        ),
        "random_threat_outer": frozenset(
            {
                "purpose",
                "threat_draw_count",
                "arrival_seed_count",
                "blocked_edge_count",
                "policies",
            }
        ),
        "adaptive_policies": frozenset(
            {"purpose", "policy_ids", "resource_frames", "rail_conditions"}
        ),
        "morris": frozenset(
            {
                "purpose",
                "trajectories",
                "levels",
                "arrival_seed_count",
                "factors",
                "policies",
            }
        ),
        "break_even_fine": frozenset(
            {
                "purpose",
                "road_multipliers",
                "target_segment",
                "policies",
                "resource_frames",
                "demand_pax",
                "arrival_seed_count",
                "source",
            }
        ),
        "scale_sensitivity": frozenset(
            {
                "purpose",
                "demand_levels",
                "road_multipliers",
                "resource_frames",
                "target_segment",
                "policies",
                "arrival_seed_count",
                "source",
            }
        ),
        "path_interdiction_threat": frozenset(
            {
                "purpose",
                "interdiction_k",
                "road_multipliers",
                "policies",
                "resource_frames",
                "arrival_seed_count",
                "threat_draw_count",
                "source",
            }
        ),
    }
)
_RESOURCE_FRAMES = frozenset({"configured_bundle", "matched_road_fleet"})
_RAIL_STATUSES = frozenset({"available", "degraded", "unavailable"})
_RETURN_STRATEGIES = frozenset({"legacy_none", "reverse_network"})


class RevisionDesignError(ValueError):
    """Raised when revision experiment design is unsafe or malformed."""


@dataclass(frozen=True, slots=True)
class InclusiveSeedRange:
    """Closed integer seed interval."""

    start: int
    stop: int

    def __post_init__(self) -> None:
        _positive_int(self.start, "seed range start")
        _positive_int(self.stop, "seed range stop")
        if self.start > self.stop:
            raise RevisionDesignError("seed range start must not exceed stop")

    @property
    def values(self) -> tuple[int, ...]:
        return tuple(range(self.start, self.stop + 1))

    def __len__(self) -> int:
        return self.stop - self.start + 1


@dataclass(frozen=True, slots=True)
class SeedBlocks:
    """All deterministic seed assignments in revision design."""

    arrival: InclusiveSeedRange
    threat: InclusiveSeedRange
    bootstrap: int
    morris: int


@dataclass(frozen=True, slots=True)
class RevisionExperimentDesign:
    """Validated immutable view of one revision experiment manifest."""

    schema_version: int
    design_id: str
    output_root: Path
    claim_boundary: str
    canonical_results_read_only: Path
    seed_blocks: SeedBlocks
    defaults: Mapping[str, Any]
    campaigns: Mapping[str, Mapping[str, Any]]

    @property
    def arrival_seeds(self) -> tuple[int, ...]:
        return self.seed_blocks.arrival.values

    @property
    def threat_seeds(self) -> tuple[int, ...]:
        return self.seed_blocks.threat.values

    @property
    def bootstrap_seed(self) -> int:
        return self.seed_blocks.bootstrap

    @property
    def morris_seed(self) -> int:
        return self.seed_blocks.morris

    @property
    def confidence(self) -> float:
        return float(self.defaults["confidence"])

    @property
    def bootstrap_replicates(self) -> int:
        return int(self.defaults["bootstrap_replicates"])

    def campaign(self, name: str) -> Mapping[str, Any]:
        """Return named immutable campaign, failing on spelling/schema drift."""

        try:
            return self.campaigns[name]
        except KeyError as exc:
            available = ", ".join(self.campaigns)
            raise KeyError(f"unknown revision campaign {name!r}; available: {available}") from exc


# Short alias for callers that do not need experiment-specific wording.
RevisionDesign = RevisionExperimentDesign


def load_revision_design(path: str | Path) -> RevisionExperimentDesign:
    """Load JSON design, validate full supported schema, and deep-freeze it."""

    source = Path(path)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RevisionDesignError(f"cannot load revision design {source}: {exc}") from exc
    root = _mapping(raw, "design")
    _exact_keys(root, _TOP_LEVEL_KEYS, "design")

    schema_version = _positive_int(root["schema_version"], "schema_version")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise RevisionDesignError(
            f"schema_version must be {SUPPORTED_SCHEMA_VERSION}, got {schema_version}"
        )
    design_id = _string(root["design_id"], "design_id")
    claim_boundary = _string(root["claim_boundary"], "claim_boundary")

    canonical = _safe_relative_path(
        root["canonical_results_read_only"], "canonical_results_read_only"
    )
    canonical_posix = _to_posix(canonical)
    if canonical_posix != CANONICAL_RESULTS_ROOT:
        raise RevisionDesignError(
            "canonical_results_read_only must identify "
            f"{CANONICAL_RESULTS_ROOT.as_posix()}"
        )
    output = _safe_relative_path(root["output_root"], "output_root")
    output_posix = _to_posix(output)
    if output_posix == canonical_posix or canonical_posix in output_posix.parents:
        raise RevisionDesignError(
            "output_root must not target canonical results or its descendants"
        )
    if not output_posix.parts or output_posix.parts[0] != "results":
        raise RevisionDesignError("output_root must be an isolated path under results")
    if output_posix.name != design_id:
        raise RevisionDesignError("output_root leaf must equal design_id")

    seeds = _load_seed_blocks(root["seed_blocks"])
    defaults_raw = _mapping(root["defaults"], "defaults")
    _validate_defaults(defaults_raw)
    campaigns_raw = _mapping(root["campaigns"], "campaigns")
    campaign_names = set(campaigns_raw)
    if campaign_names != set(EXPECTED_CAMPAIGNS):
        missing = sorted(set(EXPECTED_CAMPAIGNS) - campaign_names)
        unknown = sorted(campaign_names - set(EXPECTED_CAMPAIGNS))
        raise RevisionDesignError(
            f"campaign set mismatch; missing={missing}, unknown={unknown}"
        )

    validated_campaigns: dict[str, Mapping[str, Any]] = {}
    for name in EXPECTED_CAMPAIGNS:
        campaign_raw = _mapping(campaigns_raw[name], f"campaigns.{name}")
        _exact_keys(campaign_raw, _CAMPAIGN_KEYS[name], f"campaigns.{name}")
        _validate_campaign(name, campaign_raw, seeds)
        validated_campaigns[name] = _deep_freeze(campaign_raw)

    return RevisionExperimentDesign(
        schema_version=schema_version,
        design_id=design_id,
        output_root=output,
        claim_boundary=claim_boundary,
        canonical_results_read_only=canonical,
        seed_blocks=seeds,
        defaults=_deep_freeze(defaults_raw),
        campaigns=MappingProxyType(validated_campaigns),
    )


def _load_seed_blocks(value: Any) -> SeedBlocks:
    mapping = _mapping(value, "seed_blocks")
    _exact_keys(mapping, _SEED_BLOCK_KEYS, "seed_blocks")
    arrival = _load_seed_range(mapping["arrival"], "seed_blocks.arrival")
    threat = _load_seed_range(mapping["threat"], "seed_blocks.threat")
    if set(arrival.values).intersection(threat.values):
        raise RevisionDesignError("arrival and threat seed ranges must not overlap")
    return SeedBlocks(
        arrival=arrival,
        threat=threat,
        bootstrap=_positive_int(mapping["bootstrap"], "seed_blocks.bootstrap"),
        morris=_positive_int(mapping["morris"], "seed_blocks.morris"),
    )


def _load_seed_range(value: Any, path: str) -> InclusiveSeedRange:
    mapping = _mapping(value, path)
    _exact_keys(mapping, frozenset({"start", "stop"}), path)
    return InclusiveSeedRange(
        start=_positive_int(mapping["start"], f"{path}.start"),
        stop=_positive_int(mapping["stop"], f"{path}.stop"),
    )


def _validate_defaults(defaults: Mapping[str, Any]) -> None:
    _exact_keys(defaults, _DEFAULT_KEYS, "defaults")
    scope = _one_of(defaults["graph_scope"], GRAPH_SCOPES, "defaults.graph_scope")
    count = defaults["corridor_path_count"]
    expected_count = {"top3": 3, "top5": 5, "top10": 10, "full": None}[scope]
    if count != expected_count:
        raise RevisionDesignError(
            "defaults.corridor_path_count must match defaults.graph_scope"
        )
    method = _string(defaults["graph_scope_method"], "defaults.graph_scope_method")
    interpretation = _string(
        defaults["graph_scope_interpretation"],
        "defaults.graph_scope_interpretation",
    )
    if scope in {"top5", "top10"} and method != (
        "exact_top3_plus_deterministic_penalty_diversification"
    ):
        raise RevisionDesignError(
            "expanded default graph scope must use deterministic penalty diversification"
        )
    if scope in {"top5", "top10"} and "not exact global" not in interpretation:
        raise RevisionDesignError(
            "expanded default graph scope interpretation must state not exact global"
        )
    _string(defaults["departure_policy_id"], "defaults.departure_policy_id")
    _one_of(defaults["resource_frame"], _RESOURCE_FRAMES, "defaults.resource_frame")
    _one_of(defaults["return_strategy"], _RETURN_STRATEGIES, "defaults.return_strategy")
    _one_of(defaults["rail_status"], _RAIL_STATUSES, "defaults.rail_status")
    _positive_int(defaults["bootstrap_replicates"], "defaults.bootstrap_replicates")
    confidence = _finite_number(defaults["confidence"], "defaults.confidence")
    if not 0.0 < confidence < 1.0:
        raise RevisionDesignError("defaults.confidence must be between 0 and 1")


def _validate_campaign(
    name: str,
    campaign: Mapping[str, Any],
    seeds: SeedBlocks,
) -> None:
    path = f"campaigns.{name}"
    _string(campaign["purpose"], f"{path}.purpose")

    if name == "paired_reanalysis":
        _string_sequence(campaign["policies"], f"{path}.policies")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        _string_sequence(campaign["scenario_ids"], f"{path}.scenario_ids")
        return

    if name == "graph_scope":
        _validate_graph_scope_campaign(campaign, seeds, path)
        return

    if name == "break_even":
        _multipliers(campaign["road_multipliers"], f"{path}.road_multipliers")
        _string(campaign["target_segment"], f"{path}.target_segment")
        _string_sequence(campaign["policies"], f"{path}.policies")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        return

    if name == "demand_fleet":
        _positive_int_sequence(campaign["demand"], f"{path}.demand")
        _positive_int_sequence(
            campaign["road_fleet_total"], f"{path}.road_fleet_total"
        )
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        _string_sequence(campaign["policies"], f"{path}.policies")
        return

    if name == "road_rail_map":
        _multipliers(campaign["road_multipliers"], f"{path}.road_multipliers")
        _rail_conditions(campaign["rail_conditions"], f"{path}.rail_conditions")
        _string_sequence(campaign["policies"], f"{path}.policies")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        return

    if name == "random_threat_outer":
        draw_count = _positive_int(
            campaign["threat_draw_count"], f"{path}.threat_draw_count"
        )
        if draw_count > len(seeds.threat):
            raise RevisionDesignError(
                f"{path}.threat_draw_count exceeds threat seed count"
            )
        arrival_count = _positive_int(
            campaign["arrival_seed_count"], f"{path}.arrival_seed_count"
        )
        _assert_seed_count(arrival_count, len(seeds.arrival), path)
        _positive_int(campaign["blocked_edge_count"], f"{path}.blocked_edge_count")
        _string_sequence(campaign["policies"], f"{path}.policies")
        return

    if name == "adaptive_policies":
        _string_sequence(campaign["policy_ids"], f"{path}.policy_ids")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        _rail_conditions(campaign["rail_conditions"], f"{path}.rail_conditions")
        return

    if name == "morris":
        _positive_int(campaign["trajectories"], f"{path}.trajectories")
        levels = _positive_int(campaign["levels"], f"{path}.levels")
        if levels < 2:
            raise RevisionDesignError(f"{path}.levels must be at least 2")
        arrival_count = _positive_int(
            campaign["arrival_seed_count"], f"{path}.arrival_seed_count"
        )
        _assert_seed_count(arrival_count, len(seeds.arrival), path)
        _validate_factors(campaign["factors"], f"{path}.factors")
        _string_sequence(campaign["policies"], f"{path}.policies")
        return

    if name == "break_even_fine":
        _multipliers(campaign["road_multipliers"], f"{path}.road_multipliers")
        _string(campaign["target_segment"], f"{path}.target_segment")
        _string_sequence(campaign["policies"], f"{path}.policies")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        _positive_int(campaign.get("demand_pax", 1000), f"{path}.demand_pax")
        _positive_int(
            campaign["arrival_seed_count"], f"{path}.arrival_seed_count"
        )
        return

    if name == "scale_sensitivity":
        _positive_int_sequence(
            campaign["demand_levels"], f"{path}.demand_levels"
        )
        _multipliers(campaign["road_multipliers"], f"{path}.road_multipliers")
        _string_sequence(campaign["policies"], f"{path}.policies")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        _positive_int(
            campaign["arrival_seed_count"], f"{path}.arrival_seed_count"
        )
        return

    if name == "path_interdiction_threat":
        _positive_int_sequence(
            campaign["interdiction_k"], f"{path}.interdiction_k"
        )
        _multipliers(campaign["road_multipliers"], f"{path}.road_multipliers")
        _string_sequence(campaign["policies"], f"{path}.policies")
        _resource_frames(campaign["resource_frames"], f"{path}.resource_frames")
        _positive_int(
            campaign["arrival_seed_count"], f"{path}.arrival_seed_count"
        )
        _positive_int(
            campaign["threat_draw_count"], f"{path}.threat_draw_count"
        )
        return

    raise RevisionDesignError(f"unsupported campaign {name!r}")


def _validate_graph_scope_campaign(
    campaign: Mapping[str, Any], seeds: SeedBlocks, path: str
) -> None:
    scopes = _sequence(campaign["graph_scopes"], f"{path}.graph_scopes")
    expected = {"top3": 3, "top5": 5, "top10": 10, "full": None}
    seen: list[str] = []
    for index, item in enumerate(scopes):
        item_path = f"{path}.graph_scopes[{index}]"
        mapping = _mapping(item, item_path)
        _exact_keys(mapping, frozenset({"id", "corridor_path_count"}), item_path)
        scope = _one_of(mapping["id"], GRAPH_SCOPES, f"{item_path}.id")
        if mapping["corridor_path_count"] != expected[scope]:
            raise RevisionDesignError(
                f"{item_path}.corridor_path_count does not match {scope}"
            )
        seen.append(scope)
    if tuple(seen) != ("top3", "top5", "top10", "full"):
        raise RevisionDesignError(
            "campaigns.graph_scope graph scopes must be top3, top5, top10, full"
        )
    frozen_from = _one_of(
        campaign["freeze_selected_edges_from"],
        GRAPH_SCOPES,
        f"{path}.freeze_selected_edges_from",
    )
    if frozen_from != "top3":
        raise RevisionDesignError(f"{path}.freeze_selected_edges_from must be top3")
    _string_sequence(campaign["scenario_ids"], f"{path}.scenario_ids")
    smoke = _positive_int(
        campaign["smoke_arrival_seed_count"], f"{path}.smoke_arrival_seed_count"
    )
    full = _positive_int(
        campaign["full_arrival_seed_count"], f"{path}.full_arrival_seed_count"
    )
    full_graph = _positive_int(
        campaign["full_graph_arrival_seed_count"],
        f"{path}.full_graph_arrival_seed_count",
    )
    _assert_seed_count(smoke, len(seeds.arrival), path)
    _assert_seed_count(full, len(seeds.arrival), path)
    _assert_seed_count(full_graph, len(seeds.arrival), path)
    if smoke > full:
        raise RevisionDesignError(
            f"{path}.smoke_arrival_seed_count must not exceed full_arrival_seed_count"
        )
    if smoke > full_graph or full_graph > full:
        raise RevisionDesignError(
            f"{path}.full_graph_arrival_seed_count must be between "
            "smoke_arrival_seed_count and full_arrival_seed_count"
        )


def _validate_factors(value: Any, path: str) -> None:
    factors = _mapping(value, path)
    if set(factors) != set(EXPECTED_MORRIS_FACTORS):
        raise RevisionDesignError(
            f"{path} factor set must be {list(EXPECTED_MORRIS_FACTORS)}"
        )
    for name in EXPECTED_MORRIS_FACTORS:
        bounds = _sequence(factors[name], f"{path}.{name}")
        if len(bounds) != 2:
            raise RevisionDesignError(f"{path}.{name} must contain two bounds")
        lower = _finite_number(bounds[0], f"{path}.{name}[0]")
        upper = _finite_number(bounds[1], f"{path}.{name}[1]")
        if lower >= upper:
            raise RevisionDesignError(
                f"{path}.{name} must use strictly increasing bounds"
            )


def _rail_conditions(value: Any, path: str) -> None:
    conditions = _sequence(value, path)
    seen: set[tuple[str, float | None]] = set()
    for index, item in enumerate(conditions):
        item_path = f"{path}[{index}]"
        condition = _mapping(item, item_path)
        _exact_keys(condition, frozenset({"status", "multiplier"}), item_path)
        status = _one_of(condition["status"], _RAIL_STATUSES, f"{item_path}.status")
        multiplier = condition["multiplier"]
        if status == "unavailable":
            if multiplier is not None:
                raise RevisionDesignError(
                    f"{item_path} unavailable rail must use null multiplier"
                )
            normalized = None
        else:
            normalized = _finite_number(multiplier, f"{item_path}.multiplier")
            if normalized < 1.0:
                raise RevisionDesignError(
                    f"{item_path}.multiplier must be at least 1"
                )
            if status == "degraded" and normalized <= 1.0:
                raise RevisionDesignError(
                    f"{item_path} degraded rail multiplier must exceed 1"
                )
        key = (status, normalized)
        if key in seen:
            raise RevisionDesignError(f"{path} contains duplicate condition {key}")
        seen.add(key)


def _multipliers(value: Any, path: str) -> tuple[float, ...]:
    items = _sequence(value, path)
    result = tuple(_finite_number(item, f"{path}[{index}]") for index, item in enumerate(items))
    if any(item < 1.0 for item in result):
        raise RevisionDesignError(f"{path} values must be at least 1")
    if tuple(sorted(result)) != result or len(set(result)) != len(result):
        raise RevisionDesignError(f"{path} must be strictly increasing")
    return result


def _resource_frames(value: Any, path: str) -> tuple[str, ...]:
    frames = _string_sequence(value, path)
    for index, frame in enumerate(frames):
        _one_of(frame, _RESOURCE_FRAMES, f"{path}[{index}]")
    return frames


def _positive_int_sequence(value: Any, path: str) -> tuple[int, ...]:
    items = _sequence(value, path)
    normalized = tuple(
        _positive_int(item, f"{path}[{index}]") for index, item in enumerate(items)
    )
    if len(set(normalized)) != len(normalized):
        raise RevisionDesignError(f"{path} must not contain duplicates")
    return normalized


def _string_sequence(value: Any, path: str) -> tuple[str, ...]:
    items = _sequence(value, path)
    normalized = tuple(_string(item, f"{path}[{index}]") for index, item in enumerate(items))
    if len(set(normalized)) != len(normalized):
        raise RevisionDesignError(f"{path} must not contain duplicates")
    return normalized


def _assert_seed_count(requested: int, available: int, path: str) -> None:
    if requested > available:
        raise RevisionDesignError(
            f"{path} arrival seed count {requested} exceeds available {available}"
        )


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RevisionDesignError(f"{path} must be a mapping")
    if any(not isinstance(key, str) or not key for key in value):
        raise RevisionDesignError(f"{path} keys must be non-empty strings")
    return value


def _sequence(value: Any, path: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise RevisionDesignError(f"{path} must be a non-empty sequence")
    if not value:
        raise RevisionDesignError(f"{path} must be a non-empty sequence")
    return value


def _exact_keys(value: Mapping[str, Any], expected: frozenset[str], path: str) -> None:
    actual = set(value)
    unknown = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unknown or missing:
        raise RevisionDesignError(
            f"{path} schema mismatch; unknown keys={unknown}, missing keys={missing}"
        )


def _positive_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RevisionDesignError(f"{path} must be an integer")
    if value <= 0:
        raise RevisionDesignError(f"{path} must be a positive integer")
    return value


def _finite_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise RevisionDesignError(f"{path} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise RevisionDesignError(f"{path} must be finite")
    return number


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RevisionDesignError(f"{path} must be a non-empty string")
    return value.strip()


def _one_of(value: Any, allowed: frozenset[str], path: str) -> str:
    text = _string(value, path)
    if text not in allowed:
        raise RevisionDesignError(f"{path} must be one of {sorted(allowed)}")
    return text


def _safe_relative_path(value: Any, path: str) -> Path:
    text = _string(value, path).replace("\\", "/")
    candidate = PurePosixPath(text)
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or "." in candidate.parts
        or not candidate.parts
        or ":" in candidate.parts[0]
    ):
        raise RevisionDesignError(f"{path} must be a safe relative path")
    return Path(*candidate.parts)


def _to_posix(value: Path) -> PurePosixPath:
    return PurePosixPath(*value.parts)


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_deep_freeze(item) for item in value)
    return value


__all__ = [
    "CANONICAL_RESULTS_ROOT",
    "EXPECTED_CAMPAIGNS",
    "GRAPH_SCOPES",
    "InclusiveSeedRange",
    "RevisionDesign",
    "RevisionDesignError",
    "RevisionExperimentDesign",
    "SeedBlocks",
    "load_revision_design",
]
