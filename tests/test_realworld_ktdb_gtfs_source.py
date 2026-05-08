"""Tests for KTDB GTFS source-metadata extraction."""

from __future__ import annotations

import csv
from io import StringIO
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stderr
from urllib.error import URLError


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.ktdb_gtfs_source import (  # noqa: E402
    KTDB_GTFS_COLUMNS,
    KTDB_GTFS_SOURCE_SCOPE,
    build_ktdb_gtfs_extract,
    load_ktdb_gtfs_extract,
    write_ktdb_gtfs_cache,
)
from scripts import cache_ktdb_gtfs_source as cache_script  # noqa: E402


NOTICE_HTML = """
<html><body>
<h1>공지사항</h1>
<h2>(안내) 2024년 3월 기준 GTFS 기반정보 제공 안내</h2>
<p>구분 : 알림</p>
<p>작성일 : 2025.11.28</p>
<p>대중교통 GTFS 기반정보(2024년 3월 기준)를 아래와 같이 제공합니다.</p>
<p>- 대중교통 GTFS 기반정보(2025년 11월 28일(금)부터 제공) : 전국 대중교통 운행시각표</p>
<p>① 기준시점 : 2024년 3월 평일 ② 제공범위 : 전국(도서지역 포함)</p>
<p>③ 교통수단 : 시내/마을버스, 도시철도, 일반철도 ④ 제공자료 : 정차지정보, 노선기본정보</p>
<p>⑤ 제공경로 : 국가교통DB 홈페이지 &gt; 정보공개 &gt; 자료신청 ⑥ 주의사항 : 파일럿 자료임</p>
<p>SNS로 해당 게시물을 이동하실 수 있습니다.</p>
</body></html>
"""

LIST_HTML = """
<html><body>
<h1>자료목록</h1>
<p>교통망 GIS DB 교통망 GIS DB &gt; 대중교통 &gt; 대중교통 대중교통 GTFS</p>
<p>TM-PT-GTFS-00 2025, 2024, 2023, 2022 곽명신 044-211-3050</p>
</body></html>
"""


def test_ktdb_gtfs_source_fields_are_parsed() -> None:
    """KTDB notice and list pages should produce review metadata fields."""

    row = build_ktdb_gtfs_extract(
        notice_html=NOTICE_HTML,
        list_html=LIST_HTML,
        fetched_at_utc="2026-05-08T00:00:00+00:00",
    )

    assert row["source_id"] == "ktdb_public_transport_gtfs_context"
    assert row["notice_title"] == "(안내) 2024년 3월 기준 GTFS 기반정보 제공 안내"
    assert row["notice_posted_date"] == "2025.11.28"
    assert row["baseline_date"] == "2024년 3월 평일"
    assert row["coverage_scope"] == "전국(도서지역 포함)"
    assert row["dataset_code"] == "TM-PT-GTFS-00"
    assert row["years_available"] == "2025, 2024, 2023, 2022"
    assert row["contact_phone"] == "044-211-3050"
    assert row["review_status"] == "cached_ktdb_metadata_pending_review"
    assert row["claim_boundary"] == KTDB_GTFS_SOURCE_SCOPE

    print("PASS: KTDB GTFS source metadata fields are parsed")


def test_ktdb_gtfs_source_cache_writes_raw_pages_and_extract() -> None:
    """Writer should emit raw KTDB pages and a loadable extract."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        notice_raw = root / "notice.html"
        list_raw = root / "list.html"
        extract = root / "extract.csv"
        row = write_ktdb_gtfs_cache(
            notice_html=NOTICE_HTML,
            list_html=LIST_HTML,
            notice_raw_output_path=notice_raw,
            list_raw_output_path=list_raw,
            extract_output_path=extract,
            fetched_at_utc="2026-05-08T00:00:00+00:00",
        )

        assert notice_raw.read_text(encoding="utf-8") == NOTICE_HTML
        assert list_raw.read_text(encoding="utf-8") == LIST_HTML
        with extract.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            assert tuple(reader.fieldnames or ()) == KTDB_GTFS_COLUMNS
        rows = load_ktdb_gtfs_extract(extract)

    assert rows == [row]

    print("PASS: KTDB GTFS source metadata cache writes raw pages and extract")


def test_ktdb_gtfs_cache_script_reports_fetch_failures() -> None:
    """CLI should report remote fetch failures without a traceback."""

    original_fetch = cache_script.fetch_ktdb_gtfs_html

    def failing_fetch(**_: object) -> tuple[str, str]:
        raise URLError("connection reset during test")

    try:
        cache_script.fetch_ktdb_gtfs_html = failing_fetch
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = cache_script.main([])
    finally:
        cache_script.fetch_ktdb_gtfs_html = original_fetch

    message = stderr.getvalue()
    assert exit_code == 1
    assert "failed to fetch KTDB GTFS source metadata" in message
    assert "target GTFS cache remains absent" in message
    assert "Traceback" not in message

    print("PASS: KTDB GTFS cache script reports fetch failures")


if __name__ == "__main__":
    test_ktdb_gtfs_source_fields_are_parsed()
    test_ktdb_gtfs_source_cache_writes_raw_pages_and_extract()
    test_ktdb_gtfs_cache_script_reports_fetch_failures()
    print("\n=== REALWORLD KTDB GTFS SOURCE TESTS PASSED ===")
