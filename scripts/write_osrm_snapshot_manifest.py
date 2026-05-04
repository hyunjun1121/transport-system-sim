"""Write a non-acceptance manifest for the optional OSRM benchmark CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.osrm_snapshot_manifest import (  # noqa: E402
    DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    DEFAULT_OSRM_BENCHMARK_PATH,
    DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH,
    write_osrm_snapshot_manifest,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    manifest = write_osrm_snapshot_manifest(
        benchmark_path=args.benchmark,
        summary_path=args.summary,
        manifest_path=args.manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_PATH,
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_SUMMARY_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
