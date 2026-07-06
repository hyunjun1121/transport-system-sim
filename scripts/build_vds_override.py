"""Build the VDS expressway sensitivity override CSV from the public VDS export.

Reads the gzip+CP949 VDS file under ``data-collections/``, aggregates expressway
observations to a per-class override fragment, and writes
``data/parameters/vds_motorway_overrides.csv`` for use with
``--road-class-overrides-path``. Decision-support sensitivity input, NOT a
calibrated capacity; ``final_study_ready`` stays false.

Usage::

    ./.venv/Scripts/python scripts/build_vds_override.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.vds_calibration import (  # noqa: E402
    aggregate_vds_by_class,
    load_vds_observations,
    vds_observations_to_override_rows,
    write_vds_override_csv,
)

DEFAULT_VDS_PATH = (
    ROOT / "data-collections" / "VDS_VDS지점 교통량_속도_지정체 분석_1일_1일_20260704.zip"
)
DEFAULT_OUTPUT = ROOT / "data" / "parameters" / "vds_motorway_overrides.csv"


def main(argv: list[str] | None = None) -> str:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vds", default=str(DEFAULT_VDS_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)

    rows = load_vds_observations(args.vds)
    observations = aggregate_vds_by_class(rows)
    override_rows = vds_observations_to_override_rows(observations)
    output = write_vds_override_csv(override_rows, args.output)
    print(
        f"wrote {output} ({len(override_rows)} class rows from "
        f"{len(rows)} cleaned observations, {len(observations)} classes)"
    )
    for observation in observations:
        print(
            f"  {observation.highway}: mean_speed={observation.observed_mean_speed_kph:.1f} "
            f"mean_volume={observation.observed_mean_volume_veh_per_hr:.1f} "
            f"n={observation.n_observations} cones={observation.n_vds_cones}"
        )
    return "built"


if __name__ == "__main__":
    main()
