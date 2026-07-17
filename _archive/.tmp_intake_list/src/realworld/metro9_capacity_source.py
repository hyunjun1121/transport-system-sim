"""Metro Line 9 rolling-stock capacity source extraction.

This module extracts a small review table from the Seoul Metro Line 9
rolling-stock overview page. The output is source-review evidence only: it
does not accept train capacity, certify terms, or close rail/provenance gates.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import re
import urllib.request
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRO9_CAPACITY_URL = "https://www.metro9.co.kr/eng/sub03_02_01.do"
DEFAULT_METRO9_CAPACITY_RAW_PATH = (
    PROJECT_ROOT / "data" / "rail" / "metro9_capacity_source_raw.html"
)
DEFAULT_METRO9_CAPACITY_EXTRACT_PATH = (
    PROJECT_ROOT / "data" / "rail" / "metro9_capacity_source_extract.csv"
)
METRO9_CAPACITY_SOURCE_SCOPE = (
    "Metro 9 rolling-stock source extract for human review only; not rail "
    "capacity acceptance, not license certification, not provenance gate "
    "closure, and not operational routing evidence."
)
METRO9_CAPACITY_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_url",
    "fetched_at_utc",
    "raw_html_sha256",
    "configuration",
    "max_running_speed_kmh_overview",
    "number_of_cars",
    "train_sets",
    "manufacturer",
    "width_mm",
    "length_mm",
    "height_mm",
    "track_gauge_mm",
    "seats_6_cars",
    "standing_6_cars",
    "total_capacity_6_cars",
    "max_speed_kmh_system_performance",
    "review_status",
    "claim_boundary",
)


def fetch_metro9_capacity_html(
    *,
    url: str = DEFAULT_METRO9_CAPACITY_URL,
    timeout_s: float = 30.0,
) -> str:
    """Fetch the Metro 9 rolling-stock overview HTML."""

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


def build_metro9_capacity_extract(
    html_text: str,
    *,
    source_url: str = DEFAULT_METRO9_CAPACITY_URL,
    fetched_at_utc: str | None = None,
) -> dict[str, str]:
    """Return one conservative source-review row from Metro 9 HTML."""

    text = _html_to_text(html_text)
    fetched = fetched_at_utc or datetime.now(timezone.utc).isoformat()
    return {
        "source_id": "metro9_capacity_context",
        "source_name": "Seoul Metro Line 9 rolling stock overview",
        "source_url": source_url,
        "fetched_at_utc": fetched,
        "raw_html_sha256": _sha256_text(html_text),
        "configuration": _match_text(
            text,
            r"Configuration\s+(.*?)\s+Max Running Speed",
        ),
        "max_running_speed_kmh_overview": _match_number(
            text,
            r"Max Running Speed\s+(\d+)\s*km/h",
        ),
        "number_of_cars": _match_number(
            text,
            r"Number of Cars\s+(\d+)\s+Cars",
        ),
        "train_sets": _match_number(
            text,
            r"Number of Cars\s+\d+\s+Cars\((\d+)\s+Train Sets",
        ),
        "manufacturer": _match_text(
            text,
            r"Manufacturer\s+(.*?)\s+Image:",
            fallback_pattern=r"Manufacturer\s+(.*?)\s+Specifications",
        ),
        "width_mm": _match_number(text, r"Width\s*:\s*([\d,]+)\s*mm"),
        "length_mm": _match_number(text, r"Length\s*:\s*([\d,]+)\s*mm"),
        "height_mm": _match_number(text, r"Height\s*:\s*([\d,]+)\s*mm"),
        "track_gauge_mm": _match_number(text, r"Track Gage\s*:\s*([\d,.]+)\s*mm"),
        "seats_6_cars": _match_number(text, r"Seats\s*:\s*(\d+)\(6 cars\)"),
        "standing_6_cars": _match_number(text, r"Standing\s*:\s*(\d+)\(6 cars\)"),
        "total_capacity_6_cars": _match_number(
            text,
            r"Total Capacity\s*:\s*(\d+)\(6 cars\)",
        ),
        "max_speed_kmh_system_performance": _match_number(
            text,
            r"Max\. Speed\s*:\s*(\d+)\s*km/h",
        ),
        "review_status": "cached_operator_page_pending_review",
        "claim_boundary": METRO9_CAPACITY_SOURCE_SCOPE,
    }


def write_metro9_capacity_cache(
    *,
    html_text: str,
    raw_output_path: str | Path = DEFAULT_METRO9_CAPACITY_RAW_PATH,
    extract_output_path: str | Path = DEFAULT_METRO9_CAPACITY_EXTRACT_PATH,
    source_url: str = DEFAULT_METRO9_CAPACITY_URL,
    fetched_at_utc: str | None = None,
) -> dict[str, str]:
    """Write raw HTML and one-row CSV source extract."""

    raw_path = Path(raw_output_path)
    extract_path = Path(extract_output_path)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    extract_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(html_text, encoding="utf-8")
    row = build_metro9_capacity_extract(
        html_text,
        source_url=source_url,
        fetched_at_utc=fetched_at_utc,
    )
    write_metro9_capacity_extract([row], extract_path)
    load_metro9_capacity_extract(extract_path)
    return row


def write_metro9_capacity_extract(
    rows: Sequence[Mapping[str, str]],
    path: str | Path = DEFAULT_METRO9_CAPACITY_EXTRACT_PATH,
) -> Path:
    """Write Metro 9 capacity source-review rows."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METRO9_CAPACITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: str(row.get(column, "")) for column in METRO9_CAPACITY_COLUMNS})
    return output


def load_metro9_capacity_extract(
    path: str | Path = DEFAULT_METRO9_CAPACITY_EXTRACT_PATH,
) -> list[dict[str, str]]:
    """Load and validate a Metro 9 capacity source-review extract."""

    extract_path = Path(path)
    with extract_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != METRO9_CAPACITY_COLUMNS:
            raise ValueError(f"{extract_path} has unexpected columns")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError(f"{extract_path} must contain at least one row")
    for index, row in enumerate(rows, start=1):
        _validate_row(row, row_number=index, path=extract_path)
    return rows


def _validate_row(row: Mapping[str, str], *, row_number: int, path: Path) -> None:
    required = (
        "source_id",
        "source_url",
        "fetched_at_utc",
        "raw_html_sha256",
        "configuration",
        "total_capacity_6_cars",
        "review_status",
        "claim_boundary",
    )
    missing = [field for field in required if not str(row.get(field, "")).strip()]
    if missing:
        raise ValueError(
            f"{path} row {row_number} missing required fields: {', '.join(missing)}"
        )
    if row.get("claim_boundary") != METRO9_CAPACITY_SOURCE_SCOPE:
        raise ValueError(f"{path} row {row_number} has unsupported claim boundary")


def _html_to_text(html_text: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>", " ", html_text)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _match_text(
    text: str,
    pattern: str,
    *,
    fallback_pattern: str | None = None,
) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None and fallback_pattern:
        match = re.search(fallback_pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _match_number(text: str, pattern: str) -> str:
    value = _match_text(text, pattern)
    return value.replace(",", "").replace(".", "") if value else ""


def _sha256_text(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


__all__ = [
    "DEFAULT_METRO9_CAPACITY_EXTRACT_PATH",
    "DEFAULT_METRO9_CAPACITY_RAW_PATH",
    "DEFAULT_METRO9_CAPACITY_URL",
    "METRO9_CAPACITY_COLUMNS",
    "METRO9_CAPACITY_SOURCE_SCOPE",
    "build_metro9_capacity_extract",
    "fetch_metro9_capacity_html",
    "load_metro9_capacity_extract",
    "write_metro9_capacity_cache",
    "write_metro9_capacity_extract",
]
