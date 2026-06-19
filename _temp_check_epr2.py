import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.experiment_package_review_packet import build_experiment_package_review_rows
rows = build_experiment_package_review_rows()
by_cat = {r['category_id']: r for r in rows}
r = by_cat['formal_experiment_acceptance_requirement']
print(f"artifact_present={r['artifact_present']}")
print(f"review_status={r['review_status']}")
print(f"review_action={r['review_action']}")
