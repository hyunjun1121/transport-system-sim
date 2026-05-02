# Local Public Repository Clone Manifest

## Purpose

The `cloned_repo/` directory contains local shallow clones of public
repositories needed as implementation references for the real-world disrupted
regional transport simulation upgrade.

These repositories are **not vendored dependencies**. They are local references
for reading implementation patterns, tests, data schemas, and examples. The
directory is ignored by git through `.gitignore`.

## Clone Status

All repositories below were cloned successfully into `cloned_repo/`.

| Local path | Source URL | Primary use in this project |
|---|---|---|
| `cloned_repo/networkx` | https://github.com/networkx/networkx.git | Graph algorithms, connectivity, shortest paths, critical-link metrics |
| `cloned_repo/osmnx` | https://github.com/gboeing/osmnx.git | OSM road network extraction and NetworkX graph conversion |
| `cloned_repo/geopandas` | https://github.com/geopandas/geopandas.git | Region polygons, spatial joins, clipping, geospatial tabular workflows |
| `cloned_repo/shapely` | https://github.com/shapely/shapely.git | Geometry operations for zones, buffers, intersections, and edge geometry |
| `cloned_repo/pyrosm` | https://github.com/pyrosm/pyrosm.git | Reproducible OSM PBF ingestion for multi-region experiments |
| `cloned_repo/h3-py` | https://github.com/uber/h3-py.git | Zone abstraction and privacy-preserving spatial indexing |
| `cloned_repo/snail` | https://github.com/nismod/snail.git | Vector-raster hazard overlay onto road and rail edges |
| `cloned_repo/open-gira` | https://github.com/nismod/open-gira.git | Infrastructure risk workflow reference for reproducible hazard scenarios |
| `cloned_repo/gtfs_kit` | https://github.com/araichev/gtfs_kit.git | GTFS schedule summaries, service windows, route/headway extraction |
| `cloned_repo/gtfs-validator` | https://github.com/MobilityData/gtfs-validator.git | Static GTFS quality validation before rail/transit assumptions are used |
| `cloned_repo/SALib` | https://github.com/SALib/SALib.git | Morris/Sobol sensitivity analysis |
| `cloned_repo/frictionless-py` | https://github.com/frictionlessdata/frictionless-py.git | CSV schema and reproducible data package validation |
| `cloned_repo/GOSTnets` | https://github.com/worldbank/GOSTnets.git | Accessibility and road-network analysis patterns |
| `cloned_repo/pysal-access` | https://github.com/pysal/access.git | Spatial accessibility metrics |
| `cloned_repo/r5py` | https://github.com/r5py/r5py.git | Multimodal OSM+GTFS travel-time benchmark matrices |
| `cloned_repo/routingpy` | https://github.com/mthh/routingpy.git | Python wrapper patterns for routing-engine plausibility checks |
| `cloned_repo/or-tools` | https://github.com/google/or-tools.git | Fleet assignment, min-cost flow, VRP, and policy-generation reference |
| `cloned_repo/PyVRP` | https://github.com/PyVRP/PyVRP.git | High-performance VRP policy-generation reference |
| `cloned_repo/UXsim` | https://github.com/toruseo/UXsim.git | Python-native mesoscopic traffic benchmark ideas |
| `cloned_repo/transcrit` | https://github.com/bramkaarga/transcrit.git | Transport criticality metric reference |
| `cloned_repo/Path4GMNS` | https://github.com/jdlph/Path4GMNS.git | GMNS, assignment, ODME, and transport-model interoperability reference |
| `cloned_repo/aequilibrae` | https://github.com/AequilibraE/aequilibrae.git | Traffic assignment, skims, OD matrix, and calibration reference |
| `cloned_repo/osrm-backend` | https://github.com/Project-OSRM/osrm-backend.git | Road routing and matrix benchmark reference |
| `cloned_repo/valhalla` | https://github.com/valhalla/valhalla.git | Road and multimodal routing benchmark reference |

## Deliberately Not Cloned In This Pass

The following tools remain useful but were not cloned because they are heavy
full-platform benchmark systems and are not required for the immediate
real-world implementation path:

- SUMO
- MATSim
- OpenTripPlanner

Clone them only after a specific external benchmark experiment is accepted.

## Near-Term Usage Order

1. Read `OSMnx`, `Pyrosm`, `GeoPandas`, `Shapely`, and `h3-py` examples to build
   the real regional network and zone abstraction pipeline.
2. Read `snail` and `open-gira` to implement spatial disruption overlays.
3. Read `gtfs-validator`, `gtfs_kit`, `r5py`, `routingpy`, `OSRM`, and
   `Valhalla` to design validation and plausibility checks.
4. Read `NetworkX`, `GOSTnets`, `pysal/access`, and `transcrit` to implement
   critical-link, accessibility-loss, and bottleneck metrics.
5. Read `OR-Tools` and `PyVRP` to generate optional dispatch and fleet policy
   alternatives.
6. Read `SALib` and `Frictionless` to add sensitivity analysis and result-data
   schema validation.
