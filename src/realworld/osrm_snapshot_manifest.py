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

OSRM_SNAPSHOT_MANIFEST_SCOPE = (
    "osrm_route_benchmark_snapshot_manifest_not_validation_acceptance"
)


def build_osrm_snapshot_manifest(
    *,
    benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    summary_path: str | Path = DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for a cached OSRM benchmark CSV."""

    benchmark = Path(benchmark_path)
    summary = Path(summary_path)
    rows = _read_csv_rows(benchmark)
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
            "not calibrated traffic evidence, not benchmark ground truth, and "
            "not operational routing guidance."
        ),
        "review_items": _review_items(rows, unpinned_rows),
    }


def write_osrm_snapshot_manifest(
    *,
    benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    summary_path: str | Path = DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write the OSRM snapshot manifest and return its value."""

    manifest = Path(manifest_path)
    value = build_osrm_snapshot_manifest(
        benchmark_path=benchmark_path,
        summary_path=summary_path,
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


def _review_items(
    rows: Sequence[Mapping[str, str]],
    unpinned_rows: Sequence[Mapping[str, str]],
) -> list[str]:
    items = [
        "review OSRM service terms, attribution, access date, and row-level query URLs before publication use",
        "keep OSRM as a plausibility comparator only; it is not calibrated local traffic evidence",
        "record any final benchmark strategy only in data/manifests/validation_acceptance.json after review",
    ]
    if not rows:
        items.insert(0, "generate or remove the optional OSRM benchmark CSV before validation review")
    if unpinned_rows:
        items.insert(0, "replace live/unpinned OSRM rows with a reviewed cached snapshot if final claims depend on them")
    return items


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH",
    "DEFAULT_OSRM_BENCHMARK_PATH",
    "DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH",
    "OSRM_SNAPSHOT_MANIFEST_SCOPE",
    "build_osrm_snapshot_manifest",
    "write_osrm_snapshot_manifest",
]
