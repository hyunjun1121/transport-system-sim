import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.experiment_package_review_packet import build_experiment_package_review_rows
rows = build_experiment_package_review_rows()
for r in rows:
    print(f"  {r['category_id']}: acceptance_ready={r['acceptance_ready']} publication_ready={r['publication_ready']}")
print("all acceptance_ready:", set(r['acceptance_ready'] for r in rows))
print("all publication_ready:", set(r['publication_ready'] for r in rows))
