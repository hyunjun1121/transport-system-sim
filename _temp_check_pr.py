import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.parameter_review_packet import build_parameter_review_rows, write_parameter_review_packet
from tempfile import TemporaryDirectory
from pathlib import Path
rows = build_parameter_review_rows()
weak_true = sum(1 for r in rows if r['weak_for_final_claim'] == 'true')
print(f'count: {len(rows)}, weak_for_final_claim=true: {weak_true}')
with TemporaryDirectory() as td:
    d = Path(td)
    m = write_parameter_review_packet(str(d / 'packet.csv'), str(d / 'manifest.json'), str(d / 'doc.md'))
    print('manifest weak_for_final_claim_count:', m.get('weak_for_final_claim_count'))
    print('publication_ready:', m.get('publication_ready'))
    print('blocking_review_count:', m.get('blocking_review_count'))
    print('human_review_count:', m.get('human_review_count'))
