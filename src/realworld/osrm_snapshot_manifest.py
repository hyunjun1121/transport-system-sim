"""OSRM route benchmark snapshot manifest helpers.

The manifest created here describes the optional OSRM benchmark CSV already
cached under ``data/validation``. It improves provenance and repeatability for
reviewers, but it is not validation acceptance and does not turn OSRM into
ground truth.
"""

from __future__ import annotations

import csv
import hashlib
import json
from math import isfinite
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OSRM_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks_osrm.csv"
)
DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_summary.md"
)
DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"
)
DEFAULT_OSRM_RAW_RESPONSE_DIR = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_raw"
)

OSRM_SNAPSHOT_MANIFEST_SCOPE = (
    "osrm_route_benchmark_snapshot_manifest_not_validation_acceptance"
)
SNAP_PASS_MAX_M = 100.0
SNAP_WARN_MAX_M = 500.0


def build_osrm_snapshot_manifest(
    *,
    benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    summary_path: str | Path = DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH,
    raw_response_dir: str | Path = DEFAULT_OSRM_RAW_RESPONSE_DIR,
) -> dict[str, Any]:
    """Return a conservative manifest for a cached OSRM benchmark CSV."""

    benchmark = Path(benchmark_path)
    summary = Path(summary_path)
    raw_dir = Path(raw_response_dir)
    rows = _read_csv_rows(benchmark)
    raw_files = _raw_response_files(raw_dir)
    raw_payloads = _raw_payload_index(raw_files)
    raw_bindings = _raw_response_bindings(rows, raw_payloads)
    status_counts = _counts(row.get("status", "") for row in rows)
    source_class_counts = _counts(row.get("source_class", "") for row in rows)
    reference_version_counts = _counts(
        row.get("reference_version", "") for row in rows
    )
    unpinned_rows = [
        row
        for row in rows
        if "live" in row.get("source_class", "").lower()
        or "unpinned" in row.get("reference_version", "").lower()
    ]
    query_urls = sorted(
        {
            query_url
            for row in rows
            for query_url in [_extract_query_url(row.get("notes", ""))]
            if query_url
        }
    )
    return {
        "schema_version": 1,
        "result_scope": OSRM_SNAPSHOT_MANIFEST_SCOPE,
        "benchmark_artifact_present": benchmark.exists(),
        "summary_artifact_present": summary.exists(),
        "inputs": {
            "benchmark_csv": _display_path(benchmark),
            "summary_markdown": _display_path(summary),
            "raw_response_dir": _display_path(raw_dir),
        },
        "row_count": len(rows),
        "route_check_ids": sorted(
            {row.get("route_check_id", "") for row in rows if row.get("route_check_id")}
        ),
        "benchmark_method_counts": _counts(
            row.get("benchmark_method", "") for row in rows
        ),
        "source_class_counts": source_class_counts,
        "reference_source_counts": _counts(
            row.get("reference_source", "") for row in rows
        ),
        "reference_version_counts": reference_version_counts,
        "status_counts": status_counts,
        "distance_status_counts": _counts(
            row.get("distance_status", "") for row in rows
        ),
        "time_status_counts": _counts(row.get("time_status", "") for row in rows),
        "query_url_count": len(query_urls),
        "query_urls": query_urls,
        "csv_sha256": _sha256(benchmark) if benchmark.exists() else "",
        "summary_sha256": _sha256(summary) if summary.exists() else "",
        "raw_response_file_count": len(raw_files),
        "raw_response_files": [
            {
                "path": _display_path(path),
                "sha256": _sha256(path),
            }
            for path in raw_files
        ],
        "raw_response_binding_count": len(raw_bindings),
        "raw_response_missing_for_row_count": sum(
            1 for item in raw_bindings if not item["raw_payload_present"]
        ),
        "raw_response_binding_mismatch_count": sum(
            1 for item in raw_bindings if item["binding_status"] == "mismatch"
        ),
        "raw_response_unmatched_file_count": max(
            0,
            len(raw_files)
            - len(
                {
                    item["raw_payload_path"]
                    for item in raw_bindings
                    if item["raw_payload_path"]
                }
            ),
        ),
        "snap_pass_max_m": SNAP_PASS_MAX_M,
        "snap_warn_max_m": SNAP_WARN_MAX_M,
        "snap_status_counts": _counts(
            item.get("snap_status", "") for item in raw_bindings
        ),
        "max_waypoint_snap_distance_m": _max_snap_distance(raw_bindings),
        "raw_response_bindings": raw_bindings,
        "unpinned_row_count": len(unpinned_rows),
        "unpinned_reference_versions": sorted(
            {
                row.get("reference_version", "")
                for row in unpinned_rows
                if row.get("reference_version")
            }
        ),
        "publication_ready": False,
        "acceptance_ready": False,
        "review_required": True,
        "claim_boundary": (
            "This manifest records an optional OSRM route benchmark snapshot "
            "for plausibility review only. It is not validation acceptance, "
            "not local traffic evidence, not benchmark ground truth, and "
            "not route-use guidance."
        ),
        "review_items": _review_items(rows, unpinned_rows, raw_files, raw_bindings),
    }


def write_osrm_snapshot_manifest(
    *,
    benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    summary_path: str | Path = DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    raw_response_dir: str | Path = DEFAULT_OSRM_RAW_RESPONSE_DIR,
) -> dict[str, Any]:
    """Write the OSRM snapshot manifest and return its value."""

    manifest = Path(manifest_path)
    value = build_osrm_snapshot_manifest(
        benchmark_path=benchmark_path,
        summary_path=summary_path,
        raw_response_dir=raw_response_dir,
    )
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _extract_query_url(notes: str) -> str:
    marker = "url="
    if marker not in notes:
        return ""
    return notes.split(marker, 1)[1].strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _raw_response_files(path: Path) -> list[Path]:
    if not path.exists() or not path.is_dir():
        return []
    return sorted(item for item in path.glob("*.json") if item.is_file())


def _raw_payload_index(paths: Sequence[Path]) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            route_id = path.stem
            payloads[route_id] = {
                "path": path,
                "readable": False,
                "route_check_id": route_id,
                "errors": ["raw JSON is unreadable"],
            }
            continue
        if not isinstance(value, Mapping):
            route_id = path.stem
            payloads[route_id] = {
                "path": path,
                "readable": False,
                "route_check_id": route_id,
                "errors": ["raw JSON root is not an object"],
            }
            continue
        route_id = str(value.get("route_check_id") or path.stem)
        payloads[route_id] = _raw_payload_summary(path, value)
    return payloads


def _raw_payload_summary(path: Path, value: Mapping[str, Any]) -> dict[str, Any]:
    payload = value.get("payload", {})
    route = {}
    waypoints: Sequence[Any] = ()
    if isinstance(payload, Mapping):
        routes = payload.get("routes", [])
        if isinstance(routes, Sequence) and routes and isinstance(routes[0], Mapping):
            route = dict(routes[0])
        raw_waypoints = payload.get("waypoints", [])
        if isinstance(raw_waypoints, Sequence):
            waypoints = raw_waypoints
    waypoint_distances = [
        parsed
        for waypoint in waypoints
        for parsed in [_finite_float(_mapping_value(waypoint, "distance"))]
        if parsed is not None
    ]
    return {
        "path": path,
        "readable": True,
        "route_check_id": str(value.get("route_check_id", "")),
        "query_url": str(value.get("query_url", "")),
        "snapshot_reference_version": str(
            value.get("snapshot_reference_version", "")
        ),
        "benchmark_distance_m": _finite_float(route.get("distance")),
        "benchmark_duration_min": _duration_seconds_to_min(route.get("duration")),
        "source_snap_distance_m": waypoint_distances[0]
        if waypoint_distances
        else None,
        "target_snap_distance_m": waypoint_distances[-1]
        if waypoint_distances
        else None,
        "max_snap_distance_m": max(waypoint_distances)
        if waypoint_distances
        else None,
        "errors": [],
    }


def _raw_response_bindings(
    rows: Sequence[Mapping[str, str]],
    raw_payloads: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for row in rows:
        route_id = str(row.get("route_check_id", ""))
        payload = raw_payloads.get(route_id)
        if payload is None:
            bindings.append(
                {
                    "route_check_id": route_id,
                    "raw_payload_present": False,
                    "raw_payload_path": "",
                    "raw_payload_sha256": "",
                    "query_url_matches": False,
                    "reference_version_matches": False,
                    "distance_matches": False,
                    "duration_matches": False,
                    "snap_status": "missing",
                    "binding_status": "missing",
                    "mismatch_reasons": ["raw response file is missing for row"],
                }
            )
            continue
        mismatches = _binding_mismatches(row, payload)
        bindings.append(
            {
                "route_check_id": route_id,
                "raw_payload_present": True,
                "raw_payload_path": _display_path(Path(payload["path"])),
                "raw_payload_sha256": _sha256(Path(payload["path"])),
                "query_url": payload.get("query_url", ""),
                "query_url_matches": "query_url" not in mismatches,
                "reference_version_matches": "reference_version" not in mismatches,
                "distance_matches": "distance" not in mismatches,
                "duration_matches": "duration" not in mismatches,
                "source_snap_distance_m": _format_optional_float(
                    payload.get("source_snap_distance_m")
                ),
                "target_snap_distance_m": _format_optional_float(
                    payload.get("target_snap_distance_m")
                ),
                "max_snap_distance_m": _format_optional_float(
                    payload.get("max_snap_distance_m")
                ),
                "snap_status": _snap_status(payload.get("max_snap_distance_m")),
                "binding_status": "match" if not mismatches else "mismatch",
                "mismatch_reasons": mismatches,
            }
        )
    return bindings


def _binding_mismatches(
    row: Mapping[str, str],
    payload: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if not payload.get("readable", False):
        reasons.extend(str(item) for item in payload.get("errors", []))
    row_query = _extract_query_url(row.get("notes", ""))
    if row_query and row_query != payload.get("query_url", ""):
        reasons.append("query_url")
    if row.get("reference_version", "") != payload.get(
        "snapshot_reference_version",
        "",
    ):
        reasons.append("reference_version")
    if not _float_close(
        row.get("benchmark_distance_m", ""),
        payload.get("benchmark_distance_m"),
    ):
        reasons.append("distance")
    if not _float_close(
        row.get("benchmark_duration_min", ""),
        payload.get("benchmark_duration_min"),
    ):
        reasons.append("duration")
    return reasons


def _snap_status(value: Any) -> str:
    parsed = _finite_float(value)
    if parsed is None:
        return "missing"
    if parsed <= SNAP_PASS_MAX_M:
        return "pass"
    if parsed <= SNAP_WARN_MAX_M:
        return "warn"
    return "fail"


def _max_snap_distance(bindings: Sequence[Mapping[str, Any]]) -> str:
    values = [
        parsed
        for item in bindings
        for parsed in [_finite_float(item.get("max_snap_distance_m"))]
        if parsed is not None
    ]
    return _format_optional_float(max(values) if values else None)


def _review_items(
    rows: Sequence[Mapping[str, str]],
    unpinned_rows: Sequence[Mapping[str, str]],
    raw_files: Sequence[Path],
    raw_bindings: Sequence[Mapping[str, Any]],
) -> list[str]:
    items = [
        "review OSRM service terms, attribution, access date, and row-level query URLs before publication use",
        "keep OSRM as a plausibility comparator only; it is not local traffic evidence",
        "record any release-scope benchmark strategy only in data/manifests/validation_acceptance.json after review",
    ]
    if any(item.get("binding_status") == "mismatch" for item in raw_bindings):
        items.insert(0, "resolve OSRM CSV-to-raw-payload mismatches before publication use")
    if any(item.get("binding_status") == "missing" for item in raw_bindings):
        items.insert(0, "retain one raw OSRM payload for every OSRM benchmark row")
    if any(item.get("snap_status") in {"warn", "fail"} for item in raw_bindings):
        items.insert(0, "review OSRM waypoint snap distances before relying on route-comparison wording")
    if not rows:
        items.insert(0, "generate or remove the optional OSRM benchmark CSV before validation review")
    if rows and not raw_files:
        items.insert(0, "retain raw OSRM response payloads before treating the snapshot as cached evidence")
    if unpinned_rows:
        items.insert(0, "replace live/unpinned OSRM rows with a reviewed cached snapshot if release-scope claims depend on them")
    return items


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _mapping_value(value: Any, key: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(key)
    return None


def _duration_seconds_to_min(value: Any) -> float | None:
    parsed = _finite_float(value)
    if parsed is None:
        return None
    return parsed / 60.0


def _finite_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(parsed):
        return None
    return parsed


def _float_close(left: Any, right: Any, *, tolerance: float = 1e-6) -> bool:
    parsed_left = _finite_float(left)
    parsed_right = _finite_float(right)
    if parsed_left is None or parsed_right is None:
        return False
    return abs(parsed_left - parsed_right) <= tolerance


def _format_optional_float(value: Any) -> str:
    parsed = _finite_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.6f}"


__all__ = [
    "DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH",
    "DEFAULT_OSRM_BENCHMARK_PATH",
    "DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH",
    "DEFAULT_OSRM_RAW_RESPONSE_DIR",
    "OSRM_SNAPSHOT_MANIFEST_SCOPE",
    "build_osrm_snapshot_manifest",
    "write_osrm_snapshot_manifest",
]
