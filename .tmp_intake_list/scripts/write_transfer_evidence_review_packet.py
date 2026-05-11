"""Write the transfer-delay evidence review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.transfer_evidence_review_packet import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    DEFAULT_PARAMETER_SOURCES_PATH,
    DEFAULT_REGION_PATH,
    DEFAULT_SENSITIVITY_DESIGN_PATH,
    DEFAULT_TRANSFER_EVIDENCE_REVIEW_DOC_PATH,
    DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH,
    build_transfer_evidence_review_rows,
    write_transfer_evidence_review_packet,
)
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_transfer_evidence_review_rows(
        config_path=args.config,
        parameter_sources_path=args.parameter_sources,
        sensitivity_design_path=args.sensitivity_design,
        region_path=args.region,
        station_binding_path=args.station_bindings,
    )
    manifest = write_transfer_evidence_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        config_path=args.config,
        parameter_sources_path=args.parameter_sources,
        sensitivity_design_path=args.sensitivity_design,
        region_path=args.region,
        station_binding_path=args.station_bindings,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write transfer-delay review rows. The output is a review aid only; "
            "it is not observed transfer timing or parameter acceptance."
        )
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--parameter-sources",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCES_PATH,
    )
    parser.add_argument(
        "--sensitivity-design",
        type=Path,
        default=DEFAULT_SENSITIVITY_DESIGN_PATH,
    )
    parser.add_argument("--region", type=Path, default=DEFAULT_REGION_PATH)
    parser.add_argument(
        "--station-bindings",
        type=Path,
        default=DEFAULT_RAIL_STATION_BINDING_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_TRANSFER_EVIDENCE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_TRANSFER_EVIDENCE_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument("--doc", type=Path, default=DEFAULT_TRANSFER_EVIDENCE_REVIEW_DOC_PATH)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
