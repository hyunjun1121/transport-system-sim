"""VDS expressway traffic-observation sensitivity fragment.

Reads a Korean expressway VDS (Vehicle Detector System) export — a gzip-compressed,
CP949-encoded CSV with per-cone, per-hour 교통량 (traffic volume) and 평균속도
(average speed) — and aggregates it to a per-class sensitivity fragment expressed
as ``road_class_overrides.csv`` rows.

This is a DECISION-SUPPORT SENSITIVITY INPUT, not a calibrated capacity. VDS cones
cover expressways (고속도로) only; the mobilization corridor's non-expressway bus
legs (assembly -> rail-access urban arterial, rail-egress -> destination national /
local road) have no VDS coverage and remain literature-derived. See the notes column
of every emitted row. final_study_ready=false.
"""

from __future__ import annotations

import csv
import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.attributes import HIGHWAY_DEFAULTS
from src.realworld.road_overrides import REQUIRED_COLUMNS


VDS_SENTINELS = frozenset({-1, "-1", "-1.0", "-1.00"})
VDS_TRAFFIC_COLUMN = "교통량"
VDS_SPEED_COLUMN = "평균속도"
VDS_ROUTE_COLUMN = "노선번호"
VDS_ROUTE_NAME_COLUMN = "도로명"
VDS_CONE_COLUMN = "VDS_ID"

DEFAULT_EXPRESSWAY_HIGHWAY = "motorway"
SPEED_FLOOR_KPH = 10.0
SPEED_CEIL_KPH = 120.0

# No reserved claim adjectives here: the override CSV is not a claim-language scan
# target, but keeping this string free of reserved terms lets the test suite assert
# the emitted wording discipline directly.
CLAIM_BOUNDARY_NOTE = (
    "Decision-support sensitivity input from public VDS expressway observations "
    "(1 day, public data). VDS cones cover expressways only; the corridor "
    "non-expressway bus legs (urban arterial, national and local road) have no VDS "
    "coverage and stay literature-derived. Observed mean flow is a capacity-class "
    "sensitivity proxy, not a design value."
)


@dataclass(frozen=True)
class VDSClassObservation:
    """Per-highway-class aggregate of cleaned VDS observations."""

    highway: str
    observed_mean_speed_kph: float
    observed_mean_volume_veh_per_hr: float
    n_observations: int
    n_vds_cones: int
    expressway_codes: tuple[str, ...]


def _is_sentinel(value: Any) -> bool:
    """Return true when a VDS cell is a missing-data sentinel or blank."""

    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return True
        try:
            return float(stripped) < 0
        except ValueError:
            return True
    try:
        return float(value) < 0
    except (TypeError, ValueError):
        return True


def load_vds_observations(path: str | Path) -> list[dict[str, Any]]:
    """Load a gzip+CP949 VDS CSV, dropping missing-data sentinel rows.

    Returns one dict per surviving row with typed ``교통량`` (int) and ``평균속도``
    (float), plus the route code/name and VDS cone id.
    """

    observations: list[dict[str, Any]] = []
    with gzip.open(path, "rt", encoding="cp949", errors="replace") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            volume_raw = row.get(VDS_TRAFFIC_COLUMN)
            speed_raw = row.get(VDS_SPEED_COLUMN)
            if _is_sentinel(volume_raw) or _is_sentinel(speed_raw):
                continue
            try:
                volume = int(float(volume_raw))
                speed = float(speed_raw)
            except (TypeError, ValueError):
                continue
            observations.append(
                {
                    VDS_ROUTE_COLUMN: (row.get(VDS_ROUTE_COLUMN) or "").strip(),
                    VDS_ROUTE_NAME_COLUMN: (row.get(VDS_ROUTE_NAME_COLUMN) or "").strip(),
                    VDS_CONE_COLUMN: (row.get(VDS_CONE_COLUMN) or "").strip(),
                    VDS_TRAFFIC_COLUMN: volume,
                    VDS_SPEED_COLUMN: speed,
                }
            )
    return observations


def aggregate_vds_by_class(
    rows: Sequence[Mapping[str, Any]],
    *,
    expressway_to_highway: Mapping[str, str] | None = None,
) -> list[VDSClassObservation]:
    """Aggregate cleaned VDS rows to per-highway-class observed means.

    ``expressway_to_highway`` maps a 노선번호 (expressway route code) to an OSM
    highway class. Unmapped (or all, when None) routes fall back to
    ``DEFAULT_EXPRESSWAY_HIGHWAY`` ("motorway"), because every VDS cone sits on an
    expressway.
    """

    mapping = expressway_to_highway or {}
    buckets: dict[str, dict[str, Any]] = {}
    for row in rows:
        route = str(row.get(VDS_ROUTE_COLUMN) or "").strip()
        highway = mapping.get(route, DEFAULT_EXPRESSWAY_HIGHWAY)
        bucket = buckets.setdefault(
            highway,
            {"speeds": [], "volumes": [], "cones": set(), "routes": set()},
        )
        bucket["speeds"].append(float(row[VDS_SPEED_COLUMN]))
        bucket["volumes"].append(int(row[VDS_TRAFFIC_COLUMN]))
        cone = str(row.get(VDS_CONE_COLUMN) or "").strip()
        if cone:
            bucket["cones"].add(cone)
        if route:
            bucket["routes"].add(route)

    observations: list[VDSClassObservation] = []
    for highway in sorted(buckets):
        bucket = buckets[highway]
        speeds = bucket["speeds"]
        volumes = bucket["volumes"]
        observations.append(
            VDSClassObservation(
                highway=highway,
                observed_mean_speed_kph=sum(speeds) / len(speeds),
                observed_mean_volume_veh_per_hr=sum(volumes) / len(volumes),
                n_observations=len(speeds),
                n_vds_cones=len(bucket["cones"]),
                expressway_codes=tuple(sorted(bucket["routes"])),
            )
        )
    return observations


def _bound_speed_kph(kph: float) -> float:
    return max(SPEED_FLOOR_KPH, min(SPEED_CEIL_KPH, kph))


def vds_observations_to_override_rows(
    observations: Sequence[VDSClassObservation],
    *,
    citation: str = "Korea public VDS expressway traffic observations (1 day, gzip/CP949)",
    source_name: str = "Public VDS expressway observations (고속도로 VDS)",
) -> list[dict[str, str]]:
    """Emit ``road_class_overrides.csv`` rows, one per observed highway class.

    ``speed_kph`` = observed mean speed bounded to [10, 120]; ``capacity_veh_per_hr``
    = observed mean flow per cone-hour (a sensitivity proxy, not a design capacity);
    ``base_p_fail`` carried from ``HIGHWAY_DEFAULTS`` for the class (VDS carries no
    disruption signal).
    """

    rows: list[dict[str, str]] = []
    for observation in observations:
        defaults = HIGHWAY_DEFAULTS[observation.highway]
        speed = _bound_speed_kph(observation.observed_mean_speed_kph)
        rows.append(
            {
                "highway": observation.highway,
                "speed_kph": f"{speed:.1f}",
                "capacity_veh_per_hr": f"{observation.observed_mean_volume_veh_per_hr:.1f}",
                "base_p_fail": f"{defaults.base_p_fail:.3f}",
                "source_class": "public-data-derived",
                "source_name": source_name,
                "source_url_or_citation": citation,
                "notes": CLAIM_BOUNDARY_NOTE,
                "speed_source_class": "public-data-derived",
                "speed_source_name": source_name,
                "speed_source_url_or_citation": citation,
                "capacity_source_class": "public-data-derived",
                "capacity_source_name": source_name,
                "capacity_source_url_or_citation": citation,
                "base_p_fail_source_class": "literature-derived",
                "base_p_fail_source_name": "HIGHWAY_DEFAULTS class base rate",
                "base_p_fail_source_url_or_citation": "src/realworld/attributes.py HIGHWAY_DEFAULTS",
            }
        )
    return rows


_OVERRIDE_FIELDNAMES: tuple[str, ...] = REQUIRED_COLUMNS + (
    "speed_source_class",
    "speed_source_name",
    "speed_source_url_or_citation",
    "capacity_source_class",
    "capacity_source_name",
    "capacity_source_url_or_citation",
    "base_p_fail_source_class",
    "base_p_fail_source_name",
    "base_p_fail_source_url_or_citation",
)


def write_vds_override_csv(rows: Sequence[Mapping[str, str]], path: str | Path) -> Path:
    """Write VDS override rows as a road_class_overrides-compatible CSV (utf-8-sig)."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(_OVERRIDE_FIELDNAMES))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in _OVERRIDE_FIELDNAMES})
    return output


__all__ = [
    "VDSClassObservation",
    "VDS_SENTINELS",
    "CLAIM_BOUNDARY_NOTE",
    "DEFAULT_EXPRESSWAY_HIGHWAY",
    "load_vds_observations",
    "aggregate_vds_by_class",
    "vds_observations_to_override_rows",
    "write_vds_override_csv",
]
