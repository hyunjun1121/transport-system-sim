"""KTDB public-transport GTFS source metadata extraction.

This module caches and extracts a small review table from public KTDB pages
that describe the GTFS dataset. The output is source-metadata review evidence
only: it is not a GTFS feed, not license certification, not rail timing
evidence, and not provenance acceptance.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
from html import unescape
from pathlib import Path
import re
import urllib.request
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KTDB_GTFS_NOTICE_URL = (
    "https://www.ktdb.go.kr/www/selectBbsNttView.do?bbsNo=2&key=45&nttNo=3785"
)
DEFAULT_KTDB_GTFS_LIST_URL = (
    "https://www.ktdb.go.kr/www/selectPbldataChargerWebList.do?"
    "key=12&searchClStepCode=106"
)
DEFAULT_KTDB_GTFS_NOTICE_RAW_PATH = (
    PROJECT_ROOT / "data" / "rail" / "ktdb_gtfs_notice_raw.html"
)
DEFAULT_KTDB_GTFS_LIST_RAW_PATH = (
    PROJECT_ROOT / "data" / "rail" / "ktdb_gtfs_dataset_list_raw.html"
)
DEFAULT_KTDB_GTFS_EXTRACT_PATH = (
    PROJECT_ROOT / "data" / "rail" / "ktdb_gtfs_source_extract.csv"
)
KTDB_GTFS_SOURCE_SCOPE = (
    "KTDB GTFS source-metadata extract for human review only; not a GTFS "
    "feed cache, not rail timing evidence, not license certification, not "
    "provenance gate closure, and not operational routing evidence."
)
KTDB_GTFS_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "notice_url",
    "list_url",
    "fetched_at_utc",
    "notice_raw_html_sha256",
    "notice_raw_file_sha256",
    "list_raw_html_sha256",
    "list_raw_file_sha256",
    "notice_title",
    "notice_posted_date",
    "baseline_date",
    "provided_from_date",
    "coverage_scope",
    "transport_modes",
    "provided_data",
    "access_route",
    "notice_caveat",
    "dataset_category",
    "dataset_name",
    "dataset_code",
    "years_available",
    "contact_name",
    "contact_phone",
    "review_status",
    "claim_boundary",
)


def fetch_ktdb_gtfs_html(
    *,
    notice_url: str = DEFAULT_KTDB_GTFS_NOTICE_URL,
    list_url: str = DEFAULT_KTDB_GTFS_LIST_URL,
    timeout_s: float = 30.0,
) -> tuple[str, str]:
    """Fetch KTDB notice and dataset-list HTML."""

    return (
        _fetch_html(notice_url, timeout_s=timeout_s),
        _fetch_html(list_url, timeout_s=timeout_s),
    )


def build_ktdb_gtfs_extract(
    *,
    notice_html: str,
    list_html: str,
    notice_url: str = DEFAULT_KTDB_GTFS_NOTICE_URL,
    list_url: str = DEFAULT_KTDB_GTFS_LIST_URL,
    fetched_at_utc: str | None = None,
) -> dict[str, str]:
    """Return one conservative source-metadata review row from KTDB pages."""

    notice_text = _html_to_text(notice_html)
    list_text = _html_to_text(list_html)
    fetched = fetched_at_utc or datetime.now(timezone.utc).isoformat()
    return {
        "source_id": "ktdb_public_transport_gtfs_context",
        "source_name": "KTDB public transport GTFS dataset metadata",
        "notice_url": notice_url,
        "list_url": list_url,
        "fetched_at_utc": fetched,
        "notice_raw_html_sha256": _sha256_text(notice_html),
        "notice_raw_file_sha256": _sha256_bytes(notice_html.encode("utf-8")),
        "list_raw_html_sha256": _sha256_text(list_html),
        "list_raw_file_sha256": _sha256_bytes(list_html.encode("utf-8")),
        "notice_title": _extract_notice_title(notice_text),
        "notice_posted_date": _match_text(notice_text, r"작성일\s*:\s*([0-9.]+)"),
        "baseline_date": _match_text(notice_text, r"①\s*기준시점\s*:\s*(.*?)\s*②"),
        "provided_from_date": _match_text(
            notice_text,
            r"기반정보\((.*?)부터 제공\)",
        ),
        "coverage_scope": _match_text(notice_text, r"②\s*제공범위\s*:\s*(.*?)\s*③"),
        "transport_modes": _match_text(notice_text, r"③\s*교통수단\s*:\s*(.*?)\s*④"),
        "provided_data": _match_text(notice_text, r"④\s*제공자료\s*:\s*(.*?)\s*⑤"),
        "access_route": _match_text(notice_text, r"⑤\s*제공경로\s*:\s*(.*?)\s*⑥"),
        "notice_caveat": _match_text(
            notice_text,
            r"⑥\s*주의사항\s*:\s*(.*?)\s*SNS로",
        ),
        "dataset_category": _match_text(
            list_text,
            r"교통망 GIS DB\s+(교통망 GIS DB\s*>\s*대중교통\s*>\s*대중교통)\s+대중교통 GTFS",
        ),
        "dataset_name": _match_text(
            list_text,
            r"교통망 GIS DB\s*>\s*대중교통\s*>\s*대중교통\s+(대중교통 GTFS)\s+TM-PT-GTFS-00",
        ),
        "dataset_code": _match_text(list_text, r"(TM-PT-GTFS-00)"),
        "years_available": _match_text(
            list_text,
            r"TM-PT-GTFS-00\s+([0-9,\s]+)\s+\S+\s+[\d-]+",
        ),
        "contact_name": _match_text(
            list_text,
            r"TM-PT-GTFS-00\s+[0-9,\s]+\s+(\S+)\s+[\d-]+",
        ),
        "contact_phone": _match_text(
            list_text,
            r"TM-PT-GTFS-00\s+[0-9,\s]+\s+\S+\s+([\d-]+)",
        ),
        "review_status": "cached_ktdb_metadata_pending_review",
        "claim_boundary": KTDB_GTFS_SOURCE_SCOPE,
    }


def write_ktdb_gtfs_cache(
    *,
    notice_html: str,
    list_html: str,
    notice_raw_output_path: str | Path = DEFAULT_KTDB_GTFS_NOTICE_RAW_PATH,
    list_raw_output_path: str | Path = DEFAULT_KTDB_GTFS_LIST_RAW_PATH,
    extract_output_path: str | Path = DEFAULT_KTDB_GTFS_EXTRACT_PATH,
    notice_url: str = DEFAULT_KTDB_GTFS_NOTICE_URL,
    list_url: str = DEFAULT_KTDB_GTFS_LIST_URL,
    fetched_at_utc: str | None = None,
) -> dict[str, str]:
    """Write raw KTDB HTML pages and one-row source metadata extract."""

    notice_path = Path(notice_raw_output_path)
    list_path = Path(list_raw_output_path)
    extract_path = Path(extract_output_path)
    notice_path.parent.mkdir(parents=True, exist_ok=True)
    list_path.parent.mkdir(parents=True, exist_ok=True)
    extract_path.parent.mkdir(parents=True, exist_ok=True)
    notice_path.write_text(notice_html, encoding="utf-8")
    list_path.write_text(list_html, encoding="utf-8")
    row = build_ktdb_gtfs_extract(
        notice_html=notice_html,
        list_html=list_html,
        notice_url=notice_url,
        list_url=list_url,
        fetched_at_utc=fetched_at_utc,
    )
    row["notice_raw_file_sha256"] = _hash_file(notice_path)
    row["list_raw_file_sha256"] = _hash_file(list_path)
    write_ktdb_gtfs_extract([row], extract_path)
    load_ktdb_gtfs_extract(extract_path)
    return row


def write_ktdb_gtfs_extract(
    rows: Sequence[Mapping[str, str]],
    path: str | Path = DEFAULT_KTDB_GTFS_EXTRACT_PATH,
) -> Path:
    """Write KTDB GTFS source-metadata rows."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=KTDB_GTFS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in KTDB_GTFS_COLUMNS}
            )
    return output


def load_ktdb_gtfs_extract(
    path: str | Path = DEFAULT_KTDB_GTFS_EXTRACT_PATH,
) -> list[dict[str, str]]:
    """Load and validate a KTDB GTFS source-metadata extract."""

    extract_path = Path(path)
    with extract_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != KTDB_GTFS_COLUMNS:
            raise ValueError(f"{extract_path} has unexpected columns")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError(f"{extract_path} must contain at least one row")
    for index, row in enumerate(rows, start=1):
        _validate_row(row, row_number=index, path=extract_path)
    return rows


def audit_ktdb_gtfs_raw_hashes(
    *,
    extract_path: str | Path = DEFAULT_KTDB_GTFS_EXTRACT_PATH,
    notice_raw_path: str | Path = DEFAULT_KTDB_GTFS_NOTICE_RAW_PATH,
    list_raw_path: str | Path = DEFAULT_KTDB_GTFS_LIST_RAW_PATH,
) -> dict[str, object]:
    """Check that extract raw-file hashes match the cached HTML byte payloads."""

    rows = load_ktdb_gtfs_extract(extract_path)
    row = rows[0]
    notice_path = Path(notice_raw_path)
    list_path = Path(list_raw_path)
    notice_hash = _hash_file(notice_path)
    list_hash = _hash_file(list_path)
    notice_match = bool(
        notice_hash
        and row.get("notice_raw_file_sha256", "").lower() == notice_hash
    )
    list_match = bool(
        list_hash and row.get("list_raw_file_sha256", "").lower() == list_hash
    )
    blockers: list[str] = []
    if not notice_match:
        blockers.append("KTDB notice raw-file SHA256 mismatch or missing raw file")
    if not list_match:
        blockers.append("KTDB dataset-list raw-file SHA256 mismatch or missing raw file")
    return {
        "source_id": row["source_id"],
        "result_scope": KTDB_GTFS_SOURCE_SCOPE,
        "extract_path": str(Path(extract_path)),
        "notice_raw_path": str(notice_path),
        "list_raw_path": str(list_path),
        "row_count": len(rows),
        "notice_recorded_raw_file_sha256": row.get("notice_raw_file_sha256", ""),
        "notice_raw_file_sha256": notice_hash,
        "notice_raw_file_sha256_matches": notice_match,
        "list_recorded_raw_file_sha256": row.get("list_raw_file_sha256", ""),
        "list_raw_file_sha256": list_hash,
        "list_raw_file_sha256_matches": list_match,
        "raw_file_integrity_ready": notice_match and list_match,
        "publication_ready": False,
        "can_mark_complete": False,
        "remaining_blockers": blockers,
        "claim_boundary": (
            "Raw-file hash match is source-context integrity only; it is not "
            "a reviewed GTFS feed, rail timing evidence, provenance "
            "acceptance, or rail-service calibration."
        ),
    }


def _validate_row(row: Mapping[str, str], *, row_number: int, path: Path) -> None:
    required = (
        "source_id",
        "notice_url",
        "list_url",
        "fetched_at_utc",
        "notice_raw_html_sha256",
        "notice_raw_file_sha256",
        "list_raw_html_sha256",
        "list_raw_file_sha256",
        "notice_title",
        "dataset_code",
        "years_available",
        "review_status",
        "claim_boundary",
    )
    missing = [field for field in required if not str(row.get(field, "")).strip()]
    if missing:
        raise ValueError(
            f"{path} row {row_number} missing required fields: {', '.join(missing)}"
        )
    if row.get("claim_boundary") != KTDB_GTFS_SOURCE_SCOPE:
        raise ValueError(f"{path} row {row_number} has unsupported claim boundary")


def _fetch_html(url: str, *, timeout_s: float) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "transport-system-sim source-review cache "
                "(non-operational research reproducibility)"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _html_to_text(html_text: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>", " ", html_text)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _match_text(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _extract_notice_title(text: str) -> str:
    gtfs_index = text.find("GTFS")
    if gtfs_index < 0:
        return _match_text(text, r"공지사항\s+(.*?)\s+구분")
    title_start = text.rfind("(", 0, gtfs_index)
    label_end = text.find(" : ", gtfs_index)
    if title_start < 0 or label_end < 0:
        return _match_text(text, r"공지사항\s+(.*?)\s+구분")
    candidate = text[title_start:label_end].strip()
    if "GTFS" not in candidate:
        return _match_text(text, r"공지사항\s+(.*?)\s+구분")
    return candidate.rsplit(" ", 1)[0].strip()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes()) if path.exists() else ""


__all__ = [
    "DEFAULT_KTDB_GTFS_EXTRACT_PATH",
    "DEFAULT_KTDB_GTFS_LIST_RAW_PATH",
    "DEFAULT_KTDB_GTFS_LIST_URL",
    "DEFAULT_KTDB_GTFS_NOTICE_RAW_PATH",
    "DEFAULT_KTDB_GTFS_NOTICE_URL",
    "KTDB_GTFS_COLUMNS",
    "KTDB_GTFS_SOURCE_SCOPE",
    "audit_ktdb_gtfs_raw_hashes",
    "build_ktdb_gtfs_extract",
    "fetch_ktdb_gtfs_html",
    "load_ktdb_gtfs_extract",
    "write_ktdb_gtfs_cache",
    "write_ktdb_gtfs_extract",
]
