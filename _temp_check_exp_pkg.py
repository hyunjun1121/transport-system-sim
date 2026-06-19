import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.experiment_package_review_packet import build_experiment_package_review_rows
rows = build_experiment_package_review_rows()
by_id = {r['category_id']: r for r in rows}
print('input_evidence_dependency:', by_id.get('input_evidence_dependency', {}).get('review_status'))
print('all statuses:')
for cid, r in sorted(by_id.items()):
    print(f"  {cid}: {r['review_status']}")
