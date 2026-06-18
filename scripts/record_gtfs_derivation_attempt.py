"""Record the cached-GTFS derivation attempt result as a JSON manifest.

This script attempts to load the cached KTDB GTFS source extract as a GTFS
feed and records the outcome. The current cached extract is a metadata-only
CSV, not a GTFS feed, so the attempt documents an honest "feed absent"
result. It does not create rail evidence and does not close any gate.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_gtfs import REQUIRED_GTFS_FILES, load_cached_gtfs_feed  # noqa: E402
from src.realworld.source_artifacts import file_sha256  # noqa: E402


DEFAULT_INPUT_PATH = ROOT / "data" / "rail" / "ktdb_gtfs_source_extract.csv"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "rail" / "gtfs_derivation_attempt_manifest.json"

REQUIRED_GTFS_FILENAMES = frozenset(REQUIRED_GTFS_FILES)

CLAIM_BOUNDARY = (
    "GTFS derivation attempt record only; not rail timing evidence, not "
    "GTFS validation, not rail-service calibration, not provenance gate "
    "closure, and not operational routing evidence."
)


def main(argv: list[str] | None = None) -> int:
    """Record the GTFS derivation attempt result."""

    args = _parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output)

    manifest = build_attempt_manifest(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def build_attempt_manifest(input_path: Path) -> dict:
    """Return a manifest recording whether the cached extract is a GTFS feed."""

    sha256 = file_sha256(input_path) if input_path.is_file() else ""
    input_is_gtfs_feed = False
    failure_reason = ""
    feed_files_present: list[str] = []

    if input_path.is_dir():
        feed_files_present = sorted(
            filename
            for filename in REQUIRED_GTFS_FILENAMES
            if (input_path / filename).is_file()
        )
        if feed_files_present == sorted(REQUIRED_GTFS_FILENAMES):
            input_is_gtfs_feed = True
    elif input_path.is_file() and _is_zip(input_path):
        import zipfile

        with zipfile.ZipFile(input_path, "r") as archive:
            names = set(archive.namelist())
            feed_files_present = sorted(
                filename for filename in REQUIRED_GTFS_FILENAMES if filename in names
            )
        if feed_files_present == sorted(REQUIRED_GTFS_FILENAMES):
            input_is_gtfs_feed = True

    if not input_is_gtfs_feed:
        try:
            load_cached_gtfs_feed(input_path)
        except ValueError as exc:
            failure_reason = str(exc)
        else:
            failure_reason = "load succeeded but required GTFS files are incomplete"

    if input_is_gtfs_feed:
        conclusion = (
            "cached input is a GTFS feed; derivation may proceed after "
            "reviewed stop, route, service-window, and validator-report choices"
        )
    else:
        conclusion = (
            "GTFS derivation attempted; cached KTDB extract is metadata only, "
            "not a GTFS feed; rail timing evidence via GTFS remains blocked"
        )

    return {
        "schema_version": 1,
        "claim_boundary": CLAIM_BOUNDARY,
        "attempt_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": _display_path(input_path),
        "input_sha256": sha256,
        "input_is_gtfs_feed": input_is_gtfs_feed,
        "required_gtfs_files": list(sorted(REQUIRED_GTFS_FILENAMES)),
        "gtfs_feed_files_present": feed_files_present,
        "failure_reason": failure_reason,
        "conclusion": conclusion,
        "can_close_rail_evidence_gate": False,
        "publication_ready": False,
    }


def _is_zip(path: Path) -> bool:
    import zipfile

    return path.is_file() and zipfile.is_zipfile(path)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Record the cached-GTFS derivation attempt result. This command "
            "does not create rail evidence and does not call live APIs."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Cached source extract path (default: KTDB GTFS metadata extract).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
