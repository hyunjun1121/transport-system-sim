"""Source URL review-packet generation.

This module turns source provenance citations into one URL-level review row per
public reference. Optional live HTTP checks can record reachability, but they do
not certify licenses, attribution duties, source suitability, or final-study
acceptance.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.realworld.source_provenance import (
    DEFAULT_SOURCE_PROVENANCE_PATH,
    SourceProvenanceRecord,
    load_source_provenance_manifest,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_url_review_packet.csv"
)
DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_url_review_manifest.json"
)
DEFAULT_SOURCE_URL_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_url_review_packet.md"
)
SOURCE_URL_REVIEW_SCOPE = (
    "Source URL review packet only; not source acceptance, not license "
    "certification, not calibrated real-world validation, and not operational "
    "routing approval."
)
SOURCE_URL_REVIEW_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "review_status",
    "url_index",
    "url",
    "check_mode",
    "url_status",
    "http_status",
    "final_url",
    "content_type",
    "checked_at",
    "target_acceptance_artifact",
    "requires_reviewer_confirmation",
    "can_support_final_provenance_gate",
    "claim_boundary",
    "notes",
)
URL_PATTERN = re.compile(r"https?://[^\s;,\]\)>\"]+", re.IGNORECASE)


@dataclass(frozen=True)
class UrlCheckResult:
    """HTTP reachability result for one URL."""

    url_status: str
    http_status: str = ""
    final_url: str = ""
    content_type: str = ""
    checked_at: str = ""
    notes: str = ""


UrlChecker = Callable[[str, float], UrlCheckResult]


def build_source_url_review_rows(
    *,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
    live_check: bool = False,
    timeout_sec: float = 8.0,
    checker: UrlChecker | None = None,
) -> list[dict[str, str]]:
    """Return one conservative review row for each URL-like source citation."""

    manifest = load_source_provenance_manifest(provenance_manifest_path)
    rows: list[dict[str, str]] = []
    check_fn = checker or check_url_reachability
    for record in manifest.records:
        urls = extract_urls(record.source_url_or_citation)
        if not urls:
            rows.append(_row_for_record_without_url(record))
            continue
        for index, url in enumerate(urls, start=1):
            result = check_fn(url, timeout_sec) if live_check else _not_checked()
            rows.append(_row_for_url(record, url=url, index=index, result=result))
    return rows


def write_source_url_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown source-URL review artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SOURCE_URL_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in SOURCE_URL_REVIEW_COLUMNS}
            )

    summary = build_source_url_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        provenance_manifest_path=provenance_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(build_source_url_review_markdown(summary, rows=rows), encoding="utf-8")
    return summary


def build_source_url_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Return a non-acceptance manifest for source URL review rows."""

    status_counts = _counts(row.get("url_status", "") for row in rows)
    mode_counts = _counts(row.get("check_mode", "") for row in rows)
    source_count = len({row.get("source_id", "") for row in rows})
    live_check_performed = any(row.get("check_mode") == "live_http" for row in rows)
    not_reachable_count = sum(
        1
        for row in rows
        if row.get("url_status") not in {"not_checked", "reachable", "no_url_detected"}
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            SOURCE_URL_REVIEW_SCOPE
            + " URL reachability is only a reviewer aid and cannot close "
            "data/manifests/provenance_acceptance.json."
        ),
        "result_scope": SOURCE_URL_REVIEW_SCOPE,
        "row_count": len(rows),
        "source_count": source_count,
        "check_mode_counts": mode_counts,
        "url_status_counts": status_counts,
        "live_check_performed": live_check_performed,
        "unreachable_or_error_count": not_reachable_count,
        "requires_reviewer_confirmation_count": sum(
            1 for row in rows if _is_true(row.get("requires_reviewer_confirmation", ""))
        ),
        "provenance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_provenance_manifest": _display_path(Path(provenance_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "open each URL and verify it is the intended official or retained source",
            "record license, attribution, derivative-use, and snapshot decisions outside this packet",
            "cache context-only public sources or exclude them from final claims",
            "treat live reachability as volatile and not as source acceptance",
            "create data/manifests/provenance_acceptance.json only after reviewer decisions",
        ],
        "remaining_blockers": [
            "formal provenance acceptance record is absent",
            "URL reachability does not certify license compatibility or evidence quality",
            "context-only URLs still need cached extracts or explicit exclusion from final claims",
        ],
    }


def build_source_url_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable source URL review packet."""

    lines = [
        "# Source URL Review Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_URL_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- URL rows: {manifest.get('row_count', 0)}",
        f"- Live check performed: `{str(manifest.get('live_check_performed', False)).lower()}`",
        f"- URL statuses: `{manifest.get('url_status_counts', {})}`",
        "",
        "## URL Review Rows",
        "",
        "| Source | URL | Status | HTTP | Required Boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {url} | {status} | {http} | {boundary} |".format(
                source=_cell(row.get("source_id", "")),
                url=_cell(row.get("url", "")),
                status=_cell(row.get("url_status", "")),
                http=_cell(row.get("http_status", "")),
                boundary=_cell(row.get("claim_boundary", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Verify the official source page, license, attribution, and derivative-use constraints.",
            "- Cache retained public data extracts or explicitly exclude context-only URLs from final claims.",
            "- Treat `reachable` as a transient connectivity observation, not acceptance evidence.",
            "- Create `data/manifests/provenance_acceptance.json` only after source-backed review.",
            "",
        ]
    )
    return "\n".join(lines)


def extract_urls(text: str) -> tuple[str, ...]:
    """Extract unique HTTP(S) URLs while preserving order."""

    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return tuple(urls)


def check_url_reachability(url: str, timeout_sec: float = 8.0) -> UrlCheckResult:
    """Return a bounded live HTTP reachability result for a URL."""

    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        request = Request(url, method="HEAD", headers={"User-Agent": "transport-system-sim-source-review/1.0"})
        with urlopen(request, timeout=timeout_sec) as response:
            return UrlCheckResult(
                url_status="reachable",
                http_status=str(response.status),
                final_url=response.geturl(),
                content_type=response.headers.get("content-type", ""),
                checked_at=checked_at,
                notes="HEAD request completed",
            )
    except HTTPError as exc:
        return _fallback_get(
            url,
            timeout_sec=timeout_sec,
            checked_at=checked_at,
            fallback_reason=f"HEAD returned HTTP {exc.code}: {exc.reason}",
        )
    except (OSError, URLError) as exc:
        return UrlCheckResult(
            url_status="network_error",
            checked_at=checked_at,
            notes=str(exc),
        )


def _fallback_get(
    url: str,
    *,
    timeout_sec: float,
    checked_at: str,
    fallback_reason: str,
) -> UrlCheckResult:
    try:
        request = Request(url, method="GET", headers={"User-Agent": "transport-system-sim-source-review/1.0"})
        with urlopen(request, timeout=timeout_sec) as response:
            return UrlCheckResult(
                url_status="reachable",
                http_status=str(response.status),
                final_url=response.geturl(),
                content_type=response.headers.get("content-type", ""),
                checked_at=checked_at,
                notes=f"GET fallback completed after {fallback_reason}",
            )
    except HTTPError as exc:
        return UrlCheckResult(
            url_status="http_error",
            http_status=str(exc.code),
            final_url=exc.url or "",
            content_type=exc.headers.get("content-type", "") if exc.headers else "",
            checked_at=checked_at,
            notes=f"{fallback_reason}; GET returned HTTP {exc.code}: {exc.reason}",
        )
    except (OSError, URLError) as exc:
        return UrlCheckResult(
            url_status="network_error",
            checked_at=checked_at,
            notes=str(exc),
        )


def _row_for_record_without_url(record: SourceProvenanceRecord) -> dict[str, str]:
    return _row_for_url(
        record,
        url="",
        index=0,
        result=UrlCheckResult(
            url_status="no_url_detected",
            notes="source_url_or_citation does not contain an HTTP(S) URL",
        ),
    )


def _row_for_url(
    record: SourceProvenanceRecord,
    *,
    url: str,
    index: int,
    result: UrlCheckResult,
) -> dict[str, str]:
    return {
        "source_id": record.source_id,
        "source_name": record.source_name,
        "source_type": record.source_type,
        "review_status": record.review_status,
        "url_index": str(index),
        "url": url,
        "check_mode": "live_http" if result.checked_at else "not_checked",
        "url_status": result.url_status,
        "http_status": result.http_status,
        "final_url": result.final_url,
        "content_type": result.content_type,
        "checked_at": result.checked_at,
        "target_acceptance_artifact": "data/manifests/provenance_acceptance.json",
        "requires_reviewer_confirmation": "true",
        "can_support_final_provenance_gate": "false",
        "claim_boundary": SOURCE_URL_REVIEW_SCOPE,
        "notes": result.notes or record.notes,
    }


def _not_checked() -> UrlCheckResult:
    return UrlCheckResult(
        url_status="not_checked",
        notes="offline parse-only row; run script with --live to record reachability",
    )


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_SOURCE_URL_REVIEW_DOC_PATH",
    "DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH",
    "DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH",
    "SOURCE_URL_REVIEW_COLUMNS",
    "SOURCE_URL_REVIEW_SCOPE",
    "UrlCheckResult",
    "build_source_url_review_manifest",
    "build_source_url_review_markdown",
    "build_source_url_review_rows",
    "check_url_reachability",
    "extract_urls",
    "write_source_url_review_packet",
]
