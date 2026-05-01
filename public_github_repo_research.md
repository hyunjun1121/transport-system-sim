# Public GitHub Repository Research for Realistic Regional Simulation

## Purpose

This document summarizes public GitHub repositories and open-source libraries that can help turn the current abstract transport simulation into a more realistic, reusable regional simulation pipeline.

The research was split by feature area and assigned to parallel GPT-5.5 xhigh subagents. Each subagent searched public GitHub/web sources for one implementation area and reported candidate repositories, licenses, reusable functions, fit, complexity, risks, and recommendations.

The goal is not to copy large external frameworks into this project. The goal is to choose a practical stack that improves realism while keeping the current Python/NetworkX simulation maintainable.

## Executive Recommendation

The most practical path is a staged integration:

1. Use **OSMnx + GeoPandas + Shapely** for the first real-road-network prototype.
2. Add **Pyrosm + pinned South Korea OSM PBF snapshots** for repeatable multi-region runs.
3. Use **H3 / h3-py** and zone aggregation for sensitive-location abstraction.
4. Use **partridge** or **gtfs_kit** for rail/GTFS ingestion, with **peartree** as a NetworkX bridge prototype.
5. Use **Path4GMNS** or **AequilibraE** for road assignment and calibration once OSM networks are stable.
6. Use **SALib** for formal sensitivity analysis over scenario assumptions.
7. Use **Ciw**, **OpenMines**, and **FleetPy** mainly as design references for queue/fleet accounting rather than full dependencies.
8. Keep **OTP**, **R5/r5py**, **MOTIS**, **Valhalla**, **GraphHopper**, and **OSRM** as external benchmark or optional routing engines, not first-pass core dependencies.

The short version:

> First build a reusable regional preprocessing pipeline around OSMnx, GeoPandas, Shapely, Pyrosm, H3, and GTFS readers. Then add assignment/calibration and formal sensitivity analysis. Avoid replacing the current simulator with a large external platform too early.

## Feature 1: Regional Road Network Extraction

### Best Candidates

| Repo / library | GitHub URL | License | Main use |
|---|---|---:|---|
| OSMnx | https://github.com/gboeing/osmnx | MIT | Download OSM road networks, simplify topology, build NetworkX graphs, add speeds/travel times |
| Pyrosm | https://github.com/pyrosm/pyrosm | MIT | Read local OSM PBF snapshots into GeoDataFrames and NetworkX-compatible graphs |
| GeoPandas | https://github.com/geopandas/geopandas | BSD-3 | Region polygons, CRS transforms, clipping, spatial joins |
| Shapely | https://github.com/shapely/shapely | BSD-3 | Geometry validation, buffers, intersections, polygon operations |
| NetworkX | https://github.com/networkx/networkx | BSD-3 | Graph representation and path algorithms |
| street-network-models | https://github.com/gboeing/street-network-models | MIT | Batch OSMnx workflow reference for graph generation and caching |
| OSMnx examples | https://github.com/gboeing/osmnx-examples | MIT | Official example notebooks and usage patterns |

### Recommendation

Use **OSMnx** as the graph schema and prototype extraction tool. For repeated Korean regional runs, use **Pyrosm** with a pinned South Korea OSM PBF file so results are reproducible and do not depend on live Overpass API calls.

Use **GeoPandas/Shapely** to manage region boundaries and clipping. Store regional boundaries in a stable registry rather than relying on free-text geocoding.

### Proposed Pipeline

1. Define a `regions` registry with `region_id`, region name, and polygon.
2. For prototypes, call OSMnx with the region polygon.
3. For production/repeated runs, read a fixed South Korea PBF snapshot with Pyrosm and clip by polygon.
4. Normalize OSM edges into simulation-ready fields: length, highway class, free-flow speed, estimated capacity, failure ID.
5. Persist outputs as GraphML plus node/edge GeoPackage.
6. Record PBF date, checksum, and region polygon hash.
7. Validate that origin-destination paths exist and that all required edge attributes are present.

### Key Risks

- OSM data does not directly provide reliable traffic volume or capacity.
- Overpass API can be rate-limited or unstable.
- OSM geocoding by free-text place names can be ambiguous.
- OSM data has attribution and license obligations.
- Large road graphs may be heavy for pure NetworkX if not simplified or bounded.

## Feature 2: Traffic Assignment, Calibration, And Routing

### Best Candidates

| Repo / library | GitHub URL | License | Main use |
|---|---|---:|---|
| Path4GMNS | https://github.com/jdlph/Path4GMNS | Apache-2.0 | Shortest paths, user-equilibrium assignment, DTA after UE, ODME, GMNS I/O |
| AequilibraE | https://github.com/AequilibraE/aequilibrae | MIT with added citation clause | Static traffic assignment, skims, matrices, multi-class assignment |
| OSMnx | https://github.com/gboeing/osmnx | MIT | Road network extraction and free-flow travel-time inputs |
| UXsim | https://github.com/toruseo/UXsim | MIT | Python mesoscopic/macroscopic traffic simulation |
| routingpy | https://github.com/mthh/routingpy | Apache-2.0 | Python wrapper for routing engines such as Valhalla, GraphHopper, OSRM |
| Valhalla | https://github.com/valhalla/valhalla | MIT | OSM routing, time-distance matrices, map matching, multimodal/time-based routing |
| GraphHopper | https://github.com/graphhopper/graphhopper | Apache-2.0 | OSM/GTFS routing, custom profiles, map matching, isochrones |
| OSRM backend | https://github.com/Project-OSRM/osrm-backend | BSD-2-Clause | Fast OSM routing and OD matrices |
| TransportationNetworks | https://github.com/bstabler/TransportationNetworks | Academic-use data terms | Benchmark traffic assignment networks and BPR parameters |

### Recommendation

For the first realistic traffic step:

1. Use OSMnx for network and free-flow travel-time extraction.
2. Add an adapter from this project’s NetworkX/config structure to GMNS-style CSV.
3. Use **Path4GMNS** for user-equilibrium assignment and ODME-style calibration experiments.
4. Keep **AequilibraE** as the mature alternative if matrix/skimming and multi-class assignment become important.
5. Use **routingpy + Valhalla** only when route alternatives or realistic OD matrices are needed from a self-hosted routing engine.

Avoid SUMO, MATSim, and DTALite as first integrations unless the project intentionally shifts into a full traffic-simulation platform.

### Key Risks

- Assignment engines require OD demand matrices that this project does not yet have.
- GMNS conversion adds schema work.
- Routing engines produce route/time estimates, not full disruption-aware wartime simulation by themselves.
- Static assignment does not capture all dynamic queue spillback or signal effects.

## Feature 3: Rail, GTFS, And Multimodal Routing

### Best Candidates

| Repo / library | GitHub URL | License | Main use |
|---|---|---:|---|
| partridge | https://github.com/remix/partridge | MIT | Fast GTFS reader into pandas; service-date filtering |
| gtfs_kit | https://github.com/araichev/gtfs_kit | MIT | GTFS analysis with pandas/GeoPandas |
| peartree | https://github.com/kuanb/peartree | MIT | Convert GTFS schedules into NetworkX directed multigraphs |
| r5py | https://github.com/r5py/r5py | GPL-3.0-or-later OR MIT | Python wrapper around R5; OSM + GTFS travel-time matrices |
| R5 | https://github.com/conveyal/r5 | MIT | OSM + GTFS multimodal accessibility and routing engine |
| OpenTripPlanner | https://github.com/opentripplanner/OpenTripPlanner | LGPL v3+ | Full OSM + GTFS multimodal routing server |
| MOTIS | https://github.com/motis-project/motis | MIT | Multimodal routing server with OSM, GTFS, OpenAPI |
| transit-routing | https://github.com/transnetlab/transit-routing | MIT | RAPTOR, TBTR, CSA algorithm implementations |

### Recommendation

Do not embed OpenTripPlanner, R5, or MOTIS as core simulation code yet. They are powerful but heavy.

Start with:

1. **partridge** or **gtfs_kit** to ingest GTFS feeds.
2. Extract stops, stop times, trips, frequencies, and headways.
3. Map rail schedules into the existing `rail.py`, transfer, and NetworkX model.
4. Prototype **peartree** if a GTFS-to-NetworkX bridge is useful.
5. Use **r5py** as an external benchmark for OSM + GTFS station accessibility and travel-time matrices.

### Key Risks

- GTFS may not exist or may not represent emergency/military rail operations.
- Public timetables may not reflect wartime priority operations.
- Full multimodal routing engines add Java/C++ services and preprocessing pipelines.
- Schedule-based transit routing is not the same as passenger/fleet micro-simulation.

## Feature 4: Fleet Dispatch, Queues, And Discrete-Event Modeling

### Best Candidates

| Repo / library | GitHub URL | License | Main use |
|---|---|---:|---|
| Ciw | https://github.com/CiwPython/Ciw | MIT | Queueing networks, batch arrivals, priorities, server schedules |
| OpenMines | https://github.com/370025263/openmines | MIT | Finite fleet dispatch, load/unload queues, road state/repair |
| FleetPy | https://github.com/TUM-VT/FleetPy | MIT | Agent-based fleet simulation with vehicles, passengers, operators, routing |
| buskit | https://github.com/ywnch/buskit | MIT | Bus/stop/passenger examples, dwell time and headway concepts |
| PyVRP | https://github.com/PyVRP/PyVRP | MIT | Vehicle routing with capacities and time windows |
| pyvroom | https://github.com/VROOM-Project/pyvroom | BSD-2-Clause | VRP wrapper for pickup-delivery, time windows, heterogeneous fleets |
| salabim | https://github.com/salabim/salabim | MIT | Alternative discrete-event simulation engine |

### Recommendation

Keep the current custom SimPy-style domain model rather than replacing it wholesale.

Use external repos as design references:

- **Ciw**: passenger queues, service discipline, batching, and state tracking.
- **OpenMines**: finite fleet task accounting, queue wait estimates, fleet-size experiments.
- **FleetPy**: separation of passenger, vehicle, operator, routing, and logs.
- **PyVRP**: only if adding an offline optimization layer for vehicle assignment.

### Key Risks

- FleetPy and salabim would imply major architecture shifts.
- OpenMines is mining-domain specific.
- VRP solvers optimize schedules but do not simulate disruption and passenger queues by themselves.
- eFLIPS-style electric bus tools have AGPL licensing and domain mismatch, so they are not good first dependencies.

## Feature 5: Scenario Management, Sensitivity, And Reproducibility

### Best Candidates

| Repo / library | GitHub URL | License | Main use |
|---|---|---:|---|
| SALib | https://github.com/SALib/SALib | MIT | Sobol, Morris, FAST, Delta, PAWN sensitivity analysis |
| Hydra | https://github.com/facebookresearch/hydra | MIT | Config composition, CLI overrides, multirun sweeps |
| OmegaConf | https://github.com/omry/omegaconf | BSD-3 | Structured YAML configuration |
| EMAworkbench | https://github.com/quaquel/EMAworkbench | BSD-3 | Exploratory modeling and deep uncertainty analysis |
| UQpy | https://github.com/SURGroup/UQpy | MIT | Broader uncertainty quantification |
| DVC | https://github.com/treeverse/dvc | Apache-2.0 | Versioned params, metrics, plots, pipelines, artifacts |
| signac | https://github.com/glotzerlab/signac | BSD-3 | File-based computational study data spaces |
| Sacred | https://github.com/IDSIA/sacred | MIT | Experiment configs, observers, run tracking |

### Recommendation

Adopt **SALib first**. It gives the most scientific value with the least disruption.

Keep this project’s existing CRN pairing and result schema. Add SALib-backed sampling and analysis around the current runner.

Do not migrate to Hydra/DVC/Sacred immediately. Consider them only if the number of scenarios and artifacts grows enough to justify a workflow change.

### Key Risks

- SALib handles sampling/analysis, not simulation orchestration.
- Hydra would reshape the config and CLI.
- DVC adds workflow overhead.
- MLflow/Sacred-style tracking may be too heavy for a CSV-first research project.

## Feature 6: Geospatial Anonymization, Regional Inputs, And OD Generation

### Best Candidates

| Repo / library | GitHub URL | License | Main use |
|---|---|---:|---|
| GeoPandas | https://github.com/geopandas/geopandas | BSD-3 | Zone polygons, CRS, spatial joins, file I/O |
| Shapely | https://github.com/shapely/shapely | BSD-3 | Geometry operations |
| H3 | https://github.com/uber/h3 | Apache-2.0 | Hierarchical hexagonal zone IDs |
| h3-py | https://github.com/uber/h3-py | Apache-2.0 | Python H3 bindings |
| scikit-mobility | https://github.com/scikit-mobility/scikit-mobility | BSD-3 | OD flows, tessellations, gravity/radiation models |
| MaskMyPy | https://github.com/TheTinHat/MaskMyPy | MIT | Geomasking and k-anonymity/displacement evaluation |
| spopt | https://github.com/pysal/spopt | BSD-3 | Regionalization and facility-location optimization |
| Overture Maps Python | https://github.com/OvertureMaps/overturemaps-py | MIT | Normalized open map data by bbox/type |

### Recommendation

Use **zone aggregation over point geomasking**.

For sensitive military-style locations, do not store or publish exact coordinates unless explicitly required. Prefer:

- zone IDs
- coarse representative points
- OD counts between zones
- minimum-count thresholds
- region-level reporting

Use **GeoPandas + Shapely + h3-py + OSMnx + scikit-mobility** as the first preprocessing stack. Add **MaskMyPy** only as a privacy QA or publication masking tool. Add **spopt** if zones must be merged to meet minimum population or count thresholds.

### Key Risks

- Too-fine H3 cells can reidentify sensitive locations.
- Geomasking is not a privacy proof.
- Spatial operations must use the right CRS.
- Synthetic OD generation depends strongly on assumptions.

## Recommended Integration Roadmap

### Stage 1: Build A Reusable Regional Network Prototype

Target stack:

- OSMnx
- GeoPandas
- Shapely
- NetworkX

Deliverables:

- Region registry
- OSM road extraction for one pilot region
- GraphML/GPKG outputs
- Validation checks
- Mapping from OSM edge attributes to current simulation edge attributes

### Stage 2: Add Regional Reproducibility And Sensitive-Location Abstraction

Target stack:

- Pyrosm
- H3 / h3-py
- GeoPandas
- Shapely

Deliverables:

- Pinned South Korea PBF workflow
- Region polygon clipping
- Zone-level OD input format
- No exact sensitive destination coordinates in public outputs

### Stage 3: Add Real Rail/GTFS Inputs

Target stack:

- partridge or gtfs_kit
- peartree as optional NetworkX bridge
- r5py as optional benchmark

Deliverables:

- GTFS feed reader
- Station candidate extraction
- Headway/schedule extraction
- Rail access and last-mile connection mapping

### Stage 4: Add Assignment And Calibration

Target stack:

- Path4GMNS
- AequilibraE as alternative
- routingpy + Valhalla as optional routing engine

Deliverables:

- NetworkX-to-GMNS adapter
- OD demand matrix format
- Assigned link flows
- calibrated link travel times
- validation against current BPR assumptions

### Stage 5: Add Scientific Sensitivity Analysis

Target stack:

- SALib

Deliverables:

- Formal parameter problem definition
- Sobol or Morris sampling
- Sensitivity indices for completion time, completion rate, censored personnel, and resource efficiency
- Report-ready sensitivity tables and figures

### Stage 6: Improve Fleet And Queue Semantics

Target references:

- Ciw
- OpenMines
- FleetPy

Deliverables:

- More explicit passenger state model
- Per-vehicle task logs
- Queue wait accounting
- Boarding/alighting service time options
- Fleet shortage and driver availability scenarios

## Repos To Avoid As First-Pass Core Dependencies

These repos are useful, but they should not be the first integration target.

| Repo | Why defer |
|---|---|
| SUMO | Too heavy; would become a microscopic traffic co-simulation platform |
| MATSim | Java agent-based paradigm, high migration cost |
| OpenTripPlanner | Excellent routing server, but too heavy as embedded simulation core |
| MOTIS | Strong benchmark server, but overkill for first micro-simulation realism pass |
| DTALite | GPL and C++/GMNS integration complexity |
| OSM2GMNS | Useful but GPL; use only as external/offline tool if acceptable |
| eFLIPS tools | AGPL and electric-bus/depot-specific assumptions |
| GeoPriv QGIS plugin | GPL/QGIS-bound; reference only |

## Proposed Minimal Dependency Set

For the next realistic simulation milestone, the smallest useful stack is:

```text
osmnx
geopandas
shapely
h3
pyrosm
partridge or gtfs_kit
SALib
```

Add later only when needed:

```text
Path4GMNS
AequilibraE
routingpy
Valhalla
r5py
scikit-mobility
Ciw
```

## Final Position

The strongest reusable architecture is:

- **OSMnx/Pyrosm** for regional road networks
- **GeoPandas/Shapely/H3** for region handling and anonymization
- **partridge/gtfs_kit** for rail schedule ingestion
- **Path4GMNS or AequilibraE** for road assignment and calibration
- **SALib** for sensitivity analysis
- current in-repo simulation code for wartime passenger/fleet scenario execution

This preserves the current project’s focused micro-simulation while adding realistic data inputs and scientific validation. It also keeps the work reusable across Songpa-gu and future regions.
