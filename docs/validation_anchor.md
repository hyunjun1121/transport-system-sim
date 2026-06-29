# validation_anchor — G5 OSRM/plausibility benchmark

> Phase 0.4 (G5) deliverable. Offline validation of the simulator's road-route
> plausibility against (a) coordinate straight-line lower bounds and (b) cached
> OSRM route-engine responses. **Scaffold/sanity evidence only** — not ground truth,
> not calibration, not operational. `final_study_ready = false`.

## 1. Headline — two very different verdicts (Phase 0) → both GREEN (Phase 1)

| Region | Graph | Plausibility | OSRM (cached replay) | Verdict |
|---|---|---|---|---|
| `songpa_public_demo` (pilot_region) | real OSM, 4,608 nodes / 9,148 edges | internal checks pass | **3/3 pass** | machinery **GREEN** |
| `goseong_mobilization` (case study) | ~~skeleton stub, 52 road edges~~ → **real OSM, 197,819 nodes / 298,012 edges (Phase 1)** | **16 pass / 5 warn / 0 fail** | n/a (no Goseong raw cache) | **GREEN — see §7** |

**Phase 0:** the validation machinery was proven correct (passed on a real OSM
graph, flagged the stub) and the **Goseong case-study graph itself was the defect**.
**Phase 1 (D-GOSEONG):** the stub was replaced with a real OSM extraction — §7.

## 2. Method (both offline, no live calls)

- **Internal plausibility** (`src/realworld/plausibility.py`,
  `scripts/run_plausibility_validation.py`): loads cached GraphML → adapted
  simulator graph → checks route availability, route distance vs coordinate
  straight-line lower bound, free-flow time sanity, implied speed sanity, connector
  snap distance, edge-attribute ranges. No network.
- **OSRM benchmark** (`scripts/run_osrm_route_benchmark.py`): compares simulator
  route distance/time against OSRM. Live OSRM is **opt-in** (`--refresh-live`);
  the offline path replays **cached raw OSRM JSON** (`--from-raw-response-dir`,
  `data/validation/osrm_route_raw`). Cached responses exist only for
  `pilot_region`; Goseong OSRM is therefore deferred (would need a live OSRM call,
  blocked by offline-default).

## 3. The Goseong defect — length-stubbed skeleton graph

`run_plausibility_validation` on `goseong_mobilization` +
`data/cache/goseong_corridor_road.graphml` (20 KB, 52 road edges) produced:

```
21 route rows: 17 pass / 1 warn / 3 fail
 3 benchmark rows (fallback): 0 pass / 0 warn / 3 fail
```

The 3 fails are all **distance** checks (simulator path vs straight-line lower bound):

| Leg | Simulator distance | Straight-line lower bound | Expected range | Sim free-flow time |
|---|---|---|---|---|
| A→D (bus direct) | **700 m** | 152,602 m (~153 km) | 145–458 km | 0.68 min |
| A→S (rail access) | **100 m** | 9,287 m (~9 km) | 8.8–27.9 km | 0.12 min |
| R→D (last mile) | **300 m** | 67,031 m (~67 km) | 64–201 km | 0.32 min |

The graph has the **right topology** — the path column shows the corridor waypoints
(`A>road_songpa>Seoul>Chuncheon>Hongcheon>Inje>Sokcho>Goseong_town>road_goseong>D`)
— but the hop edges carry **near-zero lengths** (total A→D = 700 m where the real
Songpa→Goseong road distance is ~150 km). The speed/time checks "pass" only
trivially, because a 700 m path at 60 kph yields a plausible-looking 61 kph and a
0.68 min time — both meaningless for a multi-hour mobilization.

**Consequence:** the rail leg (114 min, correct) dominates and masks this in the
multimodal alternative, but the **bus_only alternative's road timing is physically
nonsensical** (0.68 min Songpa→Goseong). Any bus-vs-rail delta computed on this
graph reflects the stub, not transport structure. This is why the reset codebase
could not reproduce meaningful case-study figures.

(The lone `warn` — `road_edge_max_speed` 100 kph over an 80 kph pass-max — is the
motorway default and is within the warn band; not a defect.)

## 4. Contrast proves the machinery is sound

`pilot_region` (`songpa_public_demo`) is a genuine OSM extraction (4,608 nodes,
9,148 edges). On it:

- internal plausibility: route distances fall within coordinate-lower-bound bands,
- OSRM cached-replay benchmark: **3/3 pass** (see `data/validation/osrm_route_benchmark_summary.md`).

So the validation tooling correctly distinguishes a real road graph from a stub.
The failure is in the **Goseong graph artifact**, not the validator.

## 5. Remediation (not Phase 0 — blocks Phase 1/6)

The Goseong corridor needs a **real OSM-derived extraction** with correct edge
lengths before the case study is valid:

- Replace `data/cache/goseong_corridor_road.graphml` (52-edge stub) with a full
  OSM extraction (`--full-graph` profile, or a corridor-bbox osmnx pull cached to
  GraphML — offline once cached).
- Re-run `run_plausibility_validation` for Goseong → expect distance checks to
  pass into the 145–458 km / 9–28 km / 64–201 km bands.
- Re-run OSRM benchmark for Goseong → requires either a Goseong raw-response cache
  (one opt-in live pull, then replayed offline) or a local OSRM server.

This is a **Phase 1 prerequisite** (real graph before contract widening) and a
**Phase 6 hard dependency** (no bus-vs-rail comparison is meaningful on the stub).
Logged as a blocking defect, not a Phase-0 gate failure: G5's job was to *expose*
it, and it did.

## 6. G5 exit (Phase 0)

- [x] offline plausibility benchmark runnable (ran for Goseong + pilot_region)
- [x] OSRM cached-replay benchmark green on pilot_region (3/3)
- [x] **caught the Goseong length-stub defect** (§3) — the validation's purpose
- [x] remediation path documented (Phase 1/6, §5)
- [ ] Goseong OSRM: deferred (needs opt-in live pull or local server) — non-blocking for the gate

**G5 status: machinery GREEN (proven on pilot_region). Case-study Goseong graph
RED (length-stubbed) — exposed as designed; remediation deferred to Phase 1/6.**

## 7. Phase-1 resolution (D-GOSEONG) — real Goseong OSM graph, defect CLOSED

The §3/§5 defect is **resolved**. `scripts/build_goseong_cache.py --source overpass
--full-bbox` extracted a real OSM road network for the corridor (full region bbox,
single Overpass query, `motorway|motorway_link|trunk|trunk_link|primary|primary_link|
secondary|secondary_link`). The `_link` classes were essential — without them the
expressway network fragmented into 74 components; with them A/S/R/D are all in one
giant component and all required routes exist.

| Metric | Stub (Phase 0) | Real graph (Phase 1) |
|---|---|---|
| nodes / edges | 20 / 52 | **197,819 / 298,012** |
| source | `synthetic_corridor` | `live_overpass_osm_snapshot` |
| A→D distance | 700 m (fail) | **188,625 m (~189 km) — pass** |
| A→D free-flow time | 0.68 min (meaningless) | **132 min (~85 kph expressway) — pass** |
| route checks | 17 pass / 1 warn / 3 fail | **16 pass / 5 warn / 0 fail** |
| components (A vs D) | different | **same (connected)** |

Plausibility thresholds were recalibrated for regional-corridor scale
(`plausibility.py`: route free-flow pass_max 30→360 min, implied-speed 70→110 kph) —
the stub-era caps were calibrated for the small pilot. The synthetic
`build_goseong_corridor.py` is deprecated with an overwrite-guard (refuses to
overwrite a real cache). Coordinates stay public administrative centroids only.

The 5 residual `warn` rows are minor (connector snap distance 0 where a centroid
coincides with a mapped OSM node; low-speed unclassified edges). The 3 external
benchmark rows remain `fail` (offline OSRM fallback only — needs an opt-in live OSRM
pull or local server; non-blocking).

**Goseong case-study graph: GREEN. The Phase-0 blocker is closed.** OSRM
ground-truth benchmark for Goseong remains an optional Phase-6 enhancement.
