"""Write the pilot-region decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.graph_scale_acceptance import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
)
from src.realworld.pilot_acceptance import (  # noqa: E402
    DEFAULT_PILOT_ACCEPTANCE_PATH,
)
from src.realworld.pilot_privacy_review_packet import (  # noqa: E402
    DEFAULT_PILOT_DATA_CARD_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    DEFAULT_PILOT_REGION_PATH,
)
from src.realworld.pilot_region_decision_packet import (  # noqa: E402
    DEFAULT_PILOT_REGION_DECISION_DOC_PATH,
    DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
    DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
    build_pilot_region_decision_rows,
    write_pilot_region_decision_packet,
)
from src.realworld.provenance_acceptance import (  # noqa: E402
    DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_pilot_region_decision_rows(
        region_path=args.region,
        data_card_path=args.data_card,
        privacy_manifest_path=args.privacy_manifest,
        pilot_acceptance_path=args.pilot_acceptance,
        graph_scale_acceptance_path=args.graph_scale_acceptance,
        provenance_acceptance_path=args.provenance_acceptance,
    )
    manifest = write_pilot_region_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        region_path=args.region,
        data_card_path=args.data_card,
        privacy_manifest_path=args.privacy_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for pilot-region scope, privacy, "
            "graph-scale, provenance, and claim-boundary decisions."
        )
    )
    parser.add_argument(
        "--region",
        type=Path,
        default=DEFAULT_PILOT_REGION_PATH,
        help="Pilot region YAML path.",
    )
    parser.add_argument(
        "--data-card",
        type=Path,
        default=DEFAULT_PILOT_DATA_CARD_PATH,
        help="Pilot region data card path.",
    )
    parser.add_argument(
        "--privacy-manifest",
        type=Path,
        default=DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
        help="Pilot privacy review manifest path.",
    )
    parser.add_argument(
        "--pilot-acceptance",
        type=Path,
        default=DEFAULT_PILOT_ACCEPTANCE_PATH,
        help="Formal pilot acceptance JSON path.",
    )
    parser.add_argument(
        "--graph-scale-acceptance",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
        help="Formal graph-scale acceptance JSON path.",
    )
    parser.add_argument(
        "--provenance-acceptance",
        type=Path,
        default=DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
        help="Formal provenance acceptance JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
        help="Pilot-region decision CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
        help="Pilot-region decision manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_PILOT_REGION_DECISION_DOC_PATH,
        help="Pilot-region decision Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
