"""Policy-alternative table loader and config variant helpers.

The helpers in this module keep policy definitions as data and apply them to a
base scenario config without mutating the caller's input. They do not run the
simulation; downstream experiment scripts should pass the returned
``scenario_type`` and config to ``run_scenario(...)``.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_ALTERNATIVES_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "policy_alternatives.csv"
)

SCENARIO_TYPES = frozenset({"bus_only", "multimodal"})
REQUIRED_POLICY_IDS = frozenset(
    {
        "bus_only",
        "baseline_multimodal",
        "multimodal_lastmile_redundancy",
        "staggered_or_adaptive_dispatch",
    }
)

METADATA_COLUMNS = (
    "policy_id",
    "scenario_type",
    "decision_interpretation",
    "claim_boundary",
)
NOTES_COLUMN = "notes"

_FORBIDDEN_CLAIM_PHRASES = (
    "always superior",
    "always best",
    "guaranteed winner",
    "guaranteed to win",
    "dominates all",
    "proves superiority",
)


@dataclass(frozen=True)
class _KnobSpec:
    operation: str
    value_type: str
    target: tuple[str, ...] = ()
    rail_index: int | None = None
    min_value: float | None = None
    max_value: float | None = None
    min_inclusive: bool = True
    allowed_values: frozenset[str] | None = None
    allowed_scenarios: frozenset[str] = field(default_factory=lambda: SCENARIO_TYPES)


BUS_ONLY = frozenset({"bus_only"})
MULTIMODAL_ONLY = frozenset({"multimodal"})

_KNOB_SPECS: dict[str, _KnobSpec] = {
    "network_variant": _KnobSpec("set", "str", ("network", "variant")),
    "bus_fleet_size": _KnobSpec(
        "set",
        "int",
        ("bus", "fleet_size"),
        min_value=1,
        allowed_scenarios=BUS_ONLY,
    ),
    "bus_fleet_multiplier": _KnobSpec(
        "multiply_int",
        "float",
        ("bus", "fleet_size"),
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=BUS_ONLY,
    ),
    "bus_dispatch_interval_min": _KnobSpec(
        "set",
        "float",
        ("bus", "dispatch_interval_min"),
        min_value=0,
        allowed_scenarios=BUS_ONLY,
    ),
    "bus_first_departure_min": _KnobSpec(
        "set",
        "float",
        ("bus", "first_departure_min"),
        min_value=0,
        allowed_scenarios=BUS_ONLY,
    ),
    "bus_turnaround_min": _KnobSpec(
        "set",
        "float",
        ("bus", "turnaround_min"),
        min_value=0,
        allowed_scenarios=BUS_ONLY,
    ),
    "multimodal_shuttle_fleet_size": _KnobSpec(
        "set",
        "int",
        ("multimodal", "shuttle_fleet_size"),
        min_value=1,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_shuttle_fleet_multiplier": _KnobSpec(
        "multiply_int",
        "float",
        ("multimodal", "shuttle_fleet_size"),
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_shuttle_dispatch_interval_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "shuttle_dispatch_interval_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_shuttle_first_departure_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "shuttle_first_departure_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_shuttle_turnaround_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "shuttle_turnaround_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_transfer_time_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "transfer_time_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_transfer_time_delta_min": _KnobSpec(
        "delta_float",
        "float",
        ("multimodal", "transfer_time_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_transfer_per_passenger_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "transfer_per_passenger_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_rail_first_departure_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "rail_first_departure_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_fleet_size": _KnobSpec(
        "set",
        "int",
        ("multimodal", "lastmile_fleet_size"),
        min_value=1,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_fleet_multiplier": _KnobSpec(
        "multiply_int",
        "float",
        ("multimodal", "lastmile_fleet_size"),
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_dispatch_interval_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "lastmile_dispatch_interval_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_first_departure_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "lastmile_first_departure_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_turnaround_min": _KnobSpec(
        "set",
        "float",
        ("multimodal", "lastmile_turnaround_min"),
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_vehicle_capacity": _KnobSpec(
        "set",
        "int",
        ("multimodal", "lastmile_vehicle_capacity"),
        min_value=1,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "multimodal_lastmile_vehicle_capacity_multiplier": _KnobSpec(
        "multiply_int",
        "float",
        ("multimodal", "lastmile_vehicle_capacity"),
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "rail_travel_time_multiplier": _KnobSpec(
        "rail_multiply_float",
        "float",
        rail_index=2,
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "rail_travel_time_delta_min": _KnobSpec(
        "rail_delta_float",
        "float",
        rail_index=2,
        min_value=0,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "rail_headway_multiplier": _KnobSpec(
        "rail_multiply_float",
        "float",
        rail_index=3,
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "rail_capacity_multiplier": _KnobSpec(
        "rail_multiply_int",
        "float",
        rail_index=4,
        min_value=0,
        min_inclusive=False,
        allowed_scenarios=MULTIMODAL_ONLY,
    ),
    "traffic_background_volume_multiplier": _KnobSpec(
        "multiply_float",
        "float",
        ("traffic", "background_volume"),
        min_value=0,
        min_inclusive=False,
    ),
    "failure_mode": _KnobSpec(
        "set",
        "str",
        ("failure", "mode"),
        allowed_values=frozenset({"blocked", "capacity_reduction"}),
    ),
    "failure_capacity_reduction_factor": _KnobSpec(
        "set",
        "float",
        ("failure", "capacity_reduction_factor"),
        min_value=0,
        max_value=1,
        min_inclusive=False,
    ),
}

KNOB_COLUMNS = tuple(_KNOB_SPECS)
REQUIRED_COLUMNS = METADATA_COLUMNS + KNOB_COLUMNS + (NOTES_COLUMN,)


@dataclass(frozen=True)
class PolicyAlternative:
    """One row from the policy-alternative table."""

    policy_id: str
    scenario_type: str
    decision_interpretation: str
    claim_boundary: str
    notes: str
    knobs: tuple[tuple[str, str], ...] = ()

    def knob(self, column: str) -> str | None:
        """Return a configured knob value by CSV column name."""

        return dict(self.knobs).get(column)


@dataclass(frozen=True)
class PolicyConfigVariant:
    """A config copy plus the scenario mode selected by one policy row."""

    policy_id: str
    scenario_type: str
    config: dict[str, Any]


def load_policy_alternatives(
    path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
) -> list[PolicyAlternative]:
    """Load and validate policy alternatives from a CSV file."""

    csv_path = Path(path)
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _validate_schema(reader.fieldnames, csv_path)
        alternatives = [
            _policy_from_row(row, line_number)
            for line_number, row in enumerate(reader, start=2)
            if _row_has_content(row)
        ]

    validate_policy_alternatives(alternatives)
    return alternatives


def validate_policy_alternatives(alternatives: Sequence[PolicyAlternative]) -> None:
    """Validate policy rows and required Workstream 8 coverage."""

    if not alternatives:
        raise ValueError("policy alternatives table must contain at least one row")

    seen: set[str] = set()
    for index, alternative in enumerate(alternatives, start=1):
        _validate_policy(alternative, line_label=f"row {index}")
        if alternative.policy_id in seen:
            raise ValueError(f"duplicate policy_id: {alternative.policy_id!r}")
        seen.add(alternative.policy_id)

    missing = sorted(REQUIRED_POLICY_IDS - seen)
    if missing:
        raise ValueError(f"missing required policy alternatives: {missing}")


def get_policy_alternative(
    policy_id: str,
    alternatives: Sequence[PolicyAlternative] | None = None,
) -> PolicyAlternative:
    """Return one policy alternative by ID."""

    rows = load_policy_alternatives() if alternatives is None else list(alternatives)
    for alternative in rows:
        if alternative.policy_id == policy_id:
            return alternative
    available = sorted(alternative.policy_id for alternative in rows)
    raise KeyError(f"unknown policy_id {policy_id!r}; available={available}")


def config_for_policy_alternative(
    base_config: Mapping[str, Any],
    alternative: PolicyAlternative | str,
    alternatives: Sequence[PolicyAlternative] | None = None,
) -> dict[str, Any]:
    """Return a deep-copied config with one policy's deterministic knobs applied."""

    resolved = _resolve_alternative(alternative, alternatives)
    _validate_policy(resolved, line_label=resolved.policy_id)
    run_config = deepcopy(dict(base_config))

    for column, raw_value in resolved.knobs:
        spec = _KNOB_SPECS[column]
        value = _parse_knob_value(raw_value, spec, column)
        _apply_knob(run_config, spec, value, column)

    return run_config


def build_policy_config_variant(
    base_config: Mapping[str, Any],
    alternative: PolicyAlternative | str,
    alternatives: Sequence[PolicyAlternative] | None = None,
) -> PolicyConfigVariant:
    """Return the scenario type and config copy for a policy alternative."""

    resolved = _resolve_alternative(alternative, alternatives)
    return PolicyConfigVariant(
        policy_id=resolved.policy_id,
        scenario_type=resolved.scenario_type,
        config=config_for_policy_alternative(base_config, resolved),
    )


def _resolve_alternative(
    alternative: PolicyAlternative | str,
    alternatives: Sequence[PolicyAlternative] | None,
) -> PolicyAlternative:
    if isinstance(alternative, PolicyAlternative):
        return alternative
    return get_policy_alternative(str(alternative), alternatives)


def _validate_schema(fieldnames: Sequence[str] | None, path: Path) -> None:
    if fieldnames is None:
        raise ValueError(f"{path} is missing a CSV header")

    actual = tuple(fieldnames)
    missing = [column for column in REQUIRED_COLUMNS if column not in actual]
    extra = [column for column in actual if column not in REQUIRED_COLUMNS]
    if missing or extra:
        raise ValueError(
            f"{path} has invalid policy schema; missing={missing}, extra={extra}"
        )


def _row_has_content(row: Mapping[str | None, str | None]) -> bool:
    return any((value or "").strip() for key, value in row.items() if key is not None)


def _policy_from_row(row: Mapping[str | None, str | None], line_number: int) -> PolicyAlternative:
    if None in row:
        raise ValueError(f"row {line_number} has more values than header columns")

    stripped = {
        str(column): (value or "").strip()
        for column, value in row.items()
    }
    alternative = PolicyAlternative(
        policy_id=stripped["policy_id"],
        scenario_type=stripped["scenario_type"],
        decision_interpretation=stripped["decision_interpretation"],
        claim_boundary=stripped["claim_boundary"],
        notes=stripped[NOTES_COLUMN],
        knobs=tuple(
            (column, stripped[column])
            for column in KNOB_COLUMNS
            if stripped.get(column, "") != ""
        ),
    )
    _validate_policy(alternative, line_label=f"row {line_number}")
    return alternative


def _validate_policy(alternative: PolicyAlternative, *, line_label: str) -> None:
    _validate_policy_id(alternative.policy_id, line_label)
    if alternative.scenario_type not in SCENARIO_TYPES:
        raise ValueError(
            f"{line_label}: scenario_type must be one of {sorted(SCENARIO_TYPES)}, "
            f"got {alternative.scenario_type!r}"
        )
    _validate_required_text(
        alternative.decision_interpretation,
        f"{line_label}: decision_interpretation",
    )
    _validate_required_text(alternative.claim_boundary, f"{line_label}: claim_boundary")
    _validate_claim_language(alternative, line_label=line_label)

    seen_columns: set[str] = set()
    for column, raw_value in alternative.knobs:
        if column in seen_columns:
            raise ValueError(f"{line_label}: duplicate knob column {column!r}")
        seen_columns.add(column)

        try:
            spec = _KNOB_SPECS[column]
        except KeyError as exc:
            raise ValueError(f"{line_label}: unknown knob column {column!r}") from exc

        if alternative.scenario_type not in spec.allowed_scenarios:
            raise ValueError(
                f"{line_label}: {column!r} is not valid for "
                f"{alternative.scenario_type!r} policies"
            )
        _parse_knob_value(raw_value, spec, column)


def _validate_policy_id(policy_id: str, line_label: str) -> None:
    if not policy_id:
        raise ValueError(f"{line_label}: policy_id is required")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    if any(character not in allowed for character in policy_id):
        raise ValueError(
            f"{line_label}: policy_id must use lowercase letters, digits, and underscores"
        )


def _validate_required_text(value: str, label: str) -> None:
    if len(value.strip()) < 20:
        raise ValueError(f"{label} must contain clear plain-language text")


def _validate_claim_language(alternative: PolicyAlternative, *, line_label: str) -> None:
    combined = " ".join(
        [
            alternative.decision_interpretation,
            alternative.claim_boundary,
            alternative.notes,
        ]
    ).lower()
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            raise ValueError(
                f"{line_label}: policy language implies an unsupported universal winner "
                f"with phrase {phrase!r}"
            )


def _parse_knob_value(raw_value: str, spec: _KnobSpec, column: str) -> Any:
    value = raw_value.strip()
    if value == "":
        raise ValueError(f"{column}: blank knob values should be omitted")

    if spec.value_type == "str":
        if spec.allowed_values is not None and value not in spec.allowed_values:
            raise ValueError(
                f"{column} must be one of {sorted(spec.allowed_values)}, got {value!r}"
            )
        return value

    number = _parse_finite_float(value, column)
    _validate_numeric_range(number, spec, column)

    if spec.value_type == "int":
        if not number.is_integer():
            raise ValueError(f"{column} must be an integer, got {value!r}")
        return int(number)
    if spec.value_type == "float":
        return float(number)

    raise ValueError(f"{column}: unsupported value_type {spec.value_type!r}")


def _parse_finite_float(value: str, column: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"{column} must be numeric, got {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{column} must be finite, got {value!r}")
    return number


def _validate_numeric_range(number: float, spec: _KnobSpec, column: str) -> None:
    if spec.min_value is not None:
        if spec.min_inclusive and number < spec.min_value:
            raise ValueError(f"{column} must be at least {spec.min_value}")
        if not spec.min_inclusive and number <= spec.min_value:
            raise ValueError(f"{column} must be greater than {spec.min_value}")
    if spec.max_value is not None and number > spec.max_value:
        raise ValueError(f"{column} must be at most {spec.max_value}")


def _apply_knob(
    run_config: dict[str, Any],
    spec: _KnobSpec,
    value: Any,
    column: str,
) -> None:
    operation = spec.operation
    if operation == "set":
        _set_config_value(run_config, spec.target, value)
    elif operation == "multiply_float":
        current = _get_numeric_config_value(run_config, spec.target, column)
        _set_config_value(run_config, spec.target, current * float(value))
    elif operation == "multiply_int":
        current = _get_numeric_config_value(run_config, spec.target, column)
        _set_config_value(run_config, spec.target, _scaled_int(current, float(value)))
    elif operation == "delta_float":
        current = _get_numeric_config_value(run_config, spec.target, column)
        updated = current + float(value)
        if updated < 0:
            raise ValueError(f"{column} would make {'.'.join(spec.target)} negative")
        _set_config_value(run_config, spec.target, updated)
    elif operation.startswith("rail_"):
        _apply_rail_knob(run_config, spec, float(value), column)
    else:
        raise ValueError(f"{column}: unsupported knob operation {operation!r}")


def _set_config_value(config: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current: dict[str, Any] = config
    for key in path[:-1]:
        child = current.get(key)
        if child is None:
            child = {}
            current[key] = child
        if not isinstance(child, dict):
            raise ValueError(f"config path {'.'.join(path)} expects mapping at {key!r}")
        current = child
    current[path[-1]] = value


def _get_numeric_config_value(
    config: Mapping[str, Any],
    path: tuple[str, ...],
    column: str,
) -> float:
    current: Any = config
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            raise ValueError(f"{column} requires existing config path {'.'.join(path)}")
        current = current[key]
    return _coerce_existing_number(current, column, ".".join(path))


def _apply_rail_knob(
    run_config: dict[str, Any],
    spec: _KnobSpec,
    value: float,
    column: str,
) -> None:
    if spec.rail_index is None:
        raise ValueError(f"{column}: rail knob is missing rail_index")

    rail_link = _mutable_first_rail_link(run_config, column)
    if len(rail_link) <= spec.rail_index:
        raise ValueError(f"{column} requires rail_link index {spec.rail_index}")

    current = _coerce_existing_number(
        rail_link[spec.rail_index],
        column,
        f"network.rail_link[0][{spec.rail_index}]",
    )
    if spec.operation == "rail_multiply_float":
        updated: float | int = current * value
    elif spec.operation == "rail_delta_float":
        updated = current + value
    elif spec.operation == "rail_multiply_int":
        updated = _scaled_int(current, value)
    else:
        raise ValueError(f"{column}: unsupported rail operation {spec.operation!r}")

    if isinstance(updated, float) and updated <= 0:
        raise ValueError(f"{column} would make rail_link value non-positive")
    rail_link[spec.rail_index] = updated


def _mutable_first_rail_link(run_config: dict[str, Any], column: str) -> list[Any]:
    network = run_config.get("network")
    if not isinstance(network, dict):
        raise ValueError(f"{column} requires config.network")
    rail_links = network.get("rail_link")
    if isinstance(rail_links, (str, bytes)) or not isinstance(rail_links, Sequence):
        raise ValueError(f"{column} requires config.network.rail_link")
    if not rail_links:
        raise ValueError(f"{column} requires at least one rail link")

    mutable_links = [list(link) for link in rail_links]
    network["rail_link"] = mutable_links
    return mutable_links[0]


def _coerce_existing_number(value: Any, column: str, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{column} requires numeric {label}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{column} requires finite {label}")
    return number


def _scaled_int(current: float, multiplier: float) -> int:
    return max(1, int(math.ceil(current * multiplier)))


__all__ = [
    "DEFAULT_POLICY_ALTERNATIVES_PATH",
    "KNOB_COLUMNS",
    "PolicyAlternative",
    "PolicyConfigVariant",
    "REQUIRED_COLUMNS",
    "REQUIRED_POLICY_IDS",
    "build_policy_config_variant",
    "config_for_policy_alternative",
    "get_policy_alternative",
    "load_policy_alternatives",
    "validate_policy_alternatives",
]
