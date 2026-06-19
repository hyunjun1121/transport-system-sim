import csv, json

print("=== Shipped CSV ===")
rows = list(csv.DictReader(open('data/manifests/figure_table_review_packet.csv')))
for r in rows:
    print(f"  id={r['review_id']} status={r['review_status']}")

print("\n=== Shipped Manifest ===")
m = json.load(open('data/manifests/figure_table_review_manifest.json'))
print(f"  blocking={m.get('blocking_review_count')} human={m.get('human_review_count')} row_count={m.get('row_count')}")

print("\n=== Current Build ===")
import sys
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.figure_table_review_packet import build_figure_table_review_rows
cur = build_figure_table_review_rows()
for r in cur:
    print(f"  id={r['review_id']} status={r['review_status']}")
