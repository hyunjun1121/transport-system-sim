"""Direct-execution tests for the VDS expressway sensitivity fragment."""

from __future__ import annotations

import csv
import gzip
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.attributes import HIGHWAY_DEFAULTS  # noqa: E402
from src.realworld.claim_language_guard import RESERVED_TERM_PATTERNS  # noqa: E402
from src.realworld.road_overrides import (  # noqa: E402
    load_road_class_overrides,
)
from src.realworld.vds_calibration import (  # noqa: E402
    CLAIM_BOUNDARY_NOTE,
    aggregate_vds_by_class,
    load_vds_observations,
    vds_observations_to_override_rows,
    write_vds_override_csv,
)


_VDS_HEADER = [
    "기준시간", "기준시", "기준일", "VDS_ID", "요일명", "지점이장", "노드명",
    "도로이장", "노선번호", "도로명", "교통량", "평균속도", "",
]


def _write_gzip_vds(path: Path, data_rows: list[list[str]]) -> None:
    with gzip.open(path, "wt", encoding="cp949", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(_VDS_HEADER)
        for row in data_rows:
            writer.writerow(row)


def test_load_vds_observations_drops_sentinels() -> None:
    """Rows with -1/blank volume or speed must be dropped; valid rows survive."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "vds.csv.gz"
        _write_gzip_vds(
            path,
            [
                # 2 valid rows (both survive)
                ["00", "0000", "20260704", "VDE001", "토요일", "1.0", "X", "1.0", "0500", "영동선", "100", "90.0", ""],
                ["01", "0100", "20260704", "VDE001", "토요일", "1.0", "X", "1.0", "0500", "영동선", "200", "95.0", ""],
                # sentinel volume (-1) -> dropped
                ["02", "0200", "20260704", "VDE002", "토요일", "2.0", "Y", "2.0", "0650", "동해선", "-1", "80.0", ""],
                # sentinel speed (-1) -> dropped
                ["03", "0300", "20260704", "VDE003", "토요일", "3.0", "Z", "3.0", "0600", "서울양양선", "150", "-1", ""],
                # blank volume -> dropped
                ["04", "0400", "20260704", "VDE004", "토요일", "4.0", "W", "4.0", "0500", "영동선", "", "90", ""],
                # blank speed -> dropped
                ["05", "0500", "20260704", "VDE005", "토요일", "5.0", "V", "5.0", "0500", "영동선", "120", "", ""],
            ],
        )
        rows = load_vds_observations(path)

    assert len(rows) == 2
    assert all(row["교통량"] > 0 for row in rows)
    assert all(row["평균속도"] > 0 for row in rows)
    assert {row["노선번호"] for row in rows} == {"0500"}
    print("PASS: load_vds_observations drops sentinel rows")


def test_aggregate_vds_by_class_groups_expressway_only() -> None:
    """Aggregation groups by highway class and computes means/counts correctly."""

    rows = [
        {"노선번호": "0500", "도로명": "영동선", "VDS_ID": "A", "교통량": 100, "평균속도": 90.0},
        {"노선번호": "0500", "도로명": "영동선", "VDS_ID": "A", "교통량": 200, "평균속도": 100.0},
        {"노선번호": "0650", "도로명": "동해선", "VDS_ID": "B", "교통량": 60, "평균속도": 80.0},
        {"노선번호": "0600", "도로명": "서울양양선", "VDS_ID": "C", "교통량": 40, "평균속도": 70.0},
    ]
    observations = aggregate_vds_by_class(
        rows,
        expressway_to_highway={"0500": "motorway", "0650": "trunk", "0600": "trunk"},
    )

    by_class = {obs.highway: obs for obs in observations}
    assert set(by_class) == {"motorway", "trunk"}
    motorway = by_class["motorway"]
    assert motorway.n_observations == 2
    assert motorway.observed_mean_speed_kph == 95.0
    assert motorway.observed_mean_volume_veh_per_hr == 150.0
    assert motorway.n_vds_cones == 1
    assert motorway.expressway_codes == ("0500",)
    trunk = by_class["trunk"]
    assert trunk.n_observations == 2
    assert trunk.expressway_codes == ("0600", "0650")
    assert trunk.n_vds_cones == 2
    # Non-expressway classes never appear: VDS is expressway-only.
    assert "primary" not in by_class and "residential" not in by_class
    print("PASS: aggregate_vds_by_class groups expressway rows into motorway/trunk only")


def test_vds_observations_to_override_rows_schema_and_round_trip() -> None:
    """Emitted rows carry the override schema, public-data source class, and round-trip."""

    rows = [
        {"노선번호": "0500", "도로명": "영동선", "VDS_ID": "A", "교통량": 100, "평균속도": 95.0},
        {"노선번호": "0650", "도로명": "동해선", "VDS_ID": "B", "교통량": 60, "평균속도": 80.0},
    ]
    observations = aggregate_vds_by_class(
        rows, expressway_to_highway={"0500": "motorway", "0650": "trunk"}
    )
    override_rows = vds_observations_to_override_rows(observations)

    assert {row["highway"] for row in override_rows} == {"motorway", "trunk"}
    for row in override_rows:
        assert row["source_class"] == "public-data-derived"
        assert row["highway"] in {"motorway", "trunk"}
        assert 10.0 <= float(row["speed_kph"]) <= 120.0
        assert float(row["capacity_veh_per_hr"]) > 0
        assert 0.0 <= float(row["base_p_fail"]) <= 1.0
        assert float(row["base_p_fail"]) == HIGHWAY_DEFAULTS[row["highway"]].base_p_fail
        assert "non-expressway" in row["notes"]

    # Round-trip: the fragment must be consumable by the real override loader.
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "vds_overrides.csv"
        write_vds_override_csv(override_rows, path)
        loaded = load_road_class_overrides(path)
    assert {override.highway for override in loaded} == {"motorway", "trunk"}
    motorway = next(override for override in loaded if override.highway == "motorway")
    assert motorway.speed_kph == 95.0
    assert motorway.capacity_veh_per_hr == 100.0
    print("PASS: vds override rows have schema, public-data source class, and round-trip")


def test_vds_override_rows_carry_no_reserved_claim_terms() -> None:
    """Emitted string fields must contain no reserved claim adjective."""

    rows = [
        {"노선번호": "0500", "도로명": "영동선", "VDS_ID": "A", "교통량": 100, "평균속도": 95.0},
    ]
    observations = aggregate_vds_by_class(rows)
    override_rows = vds_observations_to_override_rows(observations)

    checked_fields = (
        "notes", "source_name", "source_url_or_citation",
        "speed_source_name", "capacity_source_name", "base_p_fail_source_name",
        "base_p_fail_source_url_or_citation",
    )
    for row in override_rows:
        for field_name in checked_fields:
            text = row.get(field_name, "")
            for term, pattern in RESERVED_TERM_PATTERNS:
                assert pattern.search(text) is None, (
                    f"reserved term {term!r} found in {field_name}: {text!r}"
                )
    # Sanity: the constant note itself is clean.
    for term, pattern in RESERVED_TERM_PATTERNS:
        assert pattern.search(CLAIM_BOUNDARY_NOTE) is None, (term, CLAIM_BOUNDARY_NOTE)
    print("PASS: vds override rows carry no reserved claim terms")


if __name__ == "__main__":
    test_load_vds_observations_drops_sentinels()
    test_aggregate_vds_by_class_groups_expressway_only()
    test_vds_observations_to_override_rows_schema_and_round_trip()
    test_vds_override_rows_carry_no_reserved_claim_terms()
    print("\n=== VDS CALIBRATION TESTS PASSED ===")
