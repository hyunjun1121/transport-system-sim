import csv
# alternate
shipped = list(csv.DictReader(open('data/validation/graph_scale_alternate_routes.csv')))
print('alternate columns:', list(shipped[0].keys()))
# multi corridor
shipped_mc = list(csv.DictReader(open('data/validation/graph_scale_multi_corridor_routes.csv')))
print('multi corridor columns:', list(shipped_mc[0].keys()))
# also check route_check_id vs leg_id
print('has route_check_id:', 'route_check_id' in shipped[0])
print('has leg_id:', 'leg_id' in shipped[0])
