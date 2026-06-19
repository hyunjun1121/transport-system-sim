import sys, os
import csv
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from tests.test_realworld_graph_scale_diagnostics import (
    current_pilot_graph_scale_records,
    graph_scale_records_to_csv_rows,
    current_pilot_graph_scale_alternate_records,
    graph_scale_alternate_records_to_csv_rows,
    current_pilot_graph_scale_multi_corridor_records,
)

# Check pilot CSV columns
print("=== Pilot CSV columns ===")
shipped = list(csv.DictReader(open('data/validation/graph_scale_route_comparison.csv')))
print('shipped columns:', shipped[0].keys() if shipped else 'empty')
expected = list(graph_scale_records_to_csv_rows(current_pilot_graph_scale_records()))
print('expected columns:', expected[0].keys() if expected else 'empty')

print("\n=== Alternate CSV columns ===")
shipped_alt = list(csv.DictReader(open('data/validation/graph_scale_alternate_route_comparison.csv')))
print('shipped columns:', shipped_alt[0].keys() if shipped_alt else 'empty')
expected_alt = list(graph_scale_alternate_records_to_csv_rows(current_pilot_graph_scale_alternate_records()))
print('expected columns:', expected_alt[0].keys() if expected_alt else 'empty')

print("\n=== Multi corridor columns ===")
shipped_mc = list(csv.DictReader(open('data/validation/graph_scale_multi_corridor_route_comparison.csv')))
print('shipped columns:', shipped_mc[0].keys() if shipped_mc else 'empty')
expected_mc = list(graph_scale_alternate_records_to_csv_rows(current_pilot_graph_scale_multi_corridor_records()))
print('expected columns:', expected_mc[0].keys() if expected_mc else 'empty')
