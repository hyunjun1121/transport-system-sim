"""Tests for road-class override draft template generation."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_override_template import (  # noqa: E402
    TEMPLATE_COLUMNS,
    build_road_class_override_template_rows,
    write_road_class_override_template,
)
from src.realworld.road_overrides import load_road_class_overrides  # noqa: E402


def test_template_prioritizes_routeable_weak_classes() -> None:
    """High/medium routeable rows should become draft override rows."""

    diagnostics = {
        "road_class_rows": [
            _row("residential", "high", 100, 0.4),
            _row("primary", "medium", 10, 0.2),
            _row("service", "low", 50, 0.3),
        ]
    }

    rows = build_road_class_override_template_rows(diagnostics, top_n=1)

    assert len(rows) == 1
    assert rows[0]["highway"] == "residential"
    assert rows[0]["source_class"] == "expert assumption"
    assert "DRAFT ONLY" in rows[0]["notes"]

    print("PASS: override template prioritizes routeable weak classes")


def test_template_include_low_priority_flag() -> None:
    """Low-priority routeable rows should be opt-in."""

    diagnostics = {"road_class_rows": [_row("service", "low", 50, 0.3)]}

    assert build_road_class_override_template_rows(diagnostics) == []
    rows = build_road_class_override_template_rows(
        diagnostics,
        include_low_priority=True,
    )

    assert len(rows) == 1
    assert rows[0]["highway"] == "service"

    print("PASS: override template include-low-priority flag works")


def test_template_csv_loads_as_weak_override_table() -> None:
    """The draft table shape should remain compatible with override loading."""

    diagnostics = {"road_class_rows": [_row("primary", "high", 3, 0.7)]}
    rows = build_road_class_override_template_rows(diagnostics)

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "road_class_overrides_draft.csv"
        write_road_class_override_template(path, rows)

        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            assert tuple(reader.fieldnames or ()) == TEMPLATE_COLUMNS

        overrides = load_road_class_overrides(path)

    assert len(overrides) == 1
    assert overrides[0].highway == "primary"
    assert overrides[0].source_class == "expert assumption"

    print("PASS: override template CSV loads as weak override table")


def _row(
    highway: str,
    priority: str,
    routeable_edges: int,
    routeable_share: float,
) -> dict[str, object]:
    return {
        "highway": highway,
        "routeable_edge_count": routeable_edges,
        "routeable_length_km": 1.25,
        "routeable_length_share": routeable_share,
        "review_priority": priority,
        "maxspeed_parseable_rate": 0.0,
        "capacity_explicit_rate": 0.0,
        "base_disruption_explicit_rate": 0.0,
    }


if __name__ == "__main__":
    test_template_prioritizes_routeable_weak_classes()
    test_template_include_low_priority_flag()
    test_template_csv_loads_as_weak_override_table()
    print("\n=== REALWORLD ROAD OVERRIDE TEMPLATE TESTS PASSED ===")
