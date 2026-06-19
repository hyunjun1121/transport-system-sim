import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.parameter_review_packet import build_parameter_review_rows, write_parameter_review_packet
from tempfile import TemporaryDirectory
from pathlib import Path

rows = build_parameter_review_rows()
with TemporaryDirectory() as td:
    d = Path(td)
    manifest = write_parameter_review_packet(
        rows=rows,
        output_path=d / "packet.csv",
        manifest_path=d / "manifest.json",
    )
    print("publication_ready:", manifest.get("publication_ready"))
    print("weak_for_final_claim_count:", manifest.get("weak_for_final_claim_count"))
    print("blocking_review_count:", manifest.get("blocking_review_count"))
    print("human_review_count:", manifest.get("human_review_count"))
