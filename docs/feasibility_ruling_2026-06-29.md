# feasibility_ruling_2026-06-29 — per-defect fundamental-resolution + realism audit

> Phase-0 exit follow-up. Answers two questions for the Phase-1+ roadmap: (1) is each
> identified defect *fundamentally* resolvable, and (2) is the overall goal realistic?
> Grounded in a 4-agent parallel audit (`defect-feasibility-audit` workflow) that read
> the actual code. Decision-support / quasi-real framing only. `final_study_ready = false`.

## 1. One-line ruling

**All four defect clusters are fundamentally resolvable; the overall goal is realistic.
The single binding constraint is D-GOSEONG** (a one-time live OSM extraction + a
corridor-buffer strategy). Everything else is small, offline, and partly *derived* from
D-GOSEONG — fix the graph and they clarify/unblock on their own.

## 2. Per-defect verdict matrix

| Defect | Verdict | Complexity | Offline-ok | Security-ok | Effort | Binding? |
|---|---|---|---|---|---|---|
| **D-GOSEONG** real Goseong graph | fundamentally_resolvable | **large** | **no** (1× live opt-in) | yes | 1.5–3 days eng | **YES — sole binding constraint** |
| **D-PARAM** BPR α / lateness / 1.67× / fleet | needs_user_decision | small | yes | yes | 0.5–1 day | no (modeling choices, not code) |
| **D-ML** 4-class + KMeans + SHAP + NL | fundamentally_resolvable | moderate | yes | yes | 3–4 days code | derived from D-GOSEONG |
| **D-CLAIM** false-green gate + ledger #5 | fundamentally_resolvable | small | yes | yes | ~15 min doc (+opt 1–2h hardening) | derived from D-GOSEONG |

## 3. D-GOSEONG — the linchpin (with a correction)

**Correction to the Phase-0 memo:** the road cache `goseong_corridor_road.graphml` edges
are **not** near-zero. They are 4.5–89 km (mean 31.8 km, total 1652 km) — straight-line
great-circle segments between named city centroids. The near-zero values (A→D 700 m,
A→S 100 m, R→D 300 m) come from the **adapter connector edges** (`MIN_CONNECTOR_T0_MIN`
in `zones.py`) that collapse when zones snap to co-located synthetic nodes. So the defect
is **two parts**: (a) a synthetic straight-line skeleton (no real roads, no OSM tags, no
intersections, no alternate routes), and (b) connector-length collapse.

**Root cause (verified):**
1. `scripts/build_goseong_corridor.py` deliberately built a synthetic 20-node / 52-edge
   waypoint skeleton (`source='synthetic_corridor'`) — **not** a failed extraction.
2. The working real-OSM path that produced `pilot_region_road.graphml` (28 947 edges,
   `source='osm_overpass'`, reviewer-accepted) is `scripts/build_pilot_cache.py
   --source overpass` — but it is **hardcoded to `pilot_region.yaml`** and a 4.5×5.3 km
   bbox; nothing routes Goseong through it.
3. `osmnx` is **not installed and not in requirements** → `osm_network.extract_bbox_graph`
   is dead code. The only working live path is raw Overpass via `urllib`.
4. The Goseong bbox in `goseong_mobilization.yaml` is ~100×176 km (~17 600 km²) — a naive
   rectangle over the entire Seoul+Gangwon diagonal. **No corridor-buffer / clip / tile
   logic exists**, so a single Overpass call would timeout at the 60 s budget.

**Fundamental fix:** replicate the proven `build_pilot_cache.py --source overpass` pattern
for Goseong, but with a **corridor-buffered extraction** (2–5 km buffer around the
Songpa→Cheongnyangni→Chuncheon→Hongcheon→Gangneung→Goseong polyline, or per-segment tiles
stitched) so it does not pull all of Seoul+Gangwon. Write a reviewer manifest mirroring
`pilot_region_road_manifest.json`. Re-run `apply_road_overrides_to_cache.py`. Separately
fix connector collapse in `zones.py`. All coordinates stay public admin centroids
(`coordinate_class=public`).

**Residual risks / open wrinkles:**
- Live Overpass is rate-limited / timeout-prone on a large corridor → tiling needed, with
  edge-continuity stitching at tile boundaries.
- `data/scenarios/goseong_disruption_scenarios.csv` may reference edges that exist only in
  the synthetic skeleton (betweenness-blockage targets) → **must re-validate** when real
  topology lands.
- Real lengths change absolute KPI magnitudes; planning-doc figures stay unreproducible
  until regenerated (already declared superseded).

## 4. D-PARAM — traceability, not engine

Three failure modes, all local:
- **Hardcoded shadow** in `make_pilot_base_config` (`pilot_experiments.py`): α=0.50/β=4.0,
  lateness μ=1.2/σ=0.25, noise 0.05/0.2 — these actually drive runs.
- **Doc-only claim drift**: α=0.36 (Korean-calibration), delay-correction 1.67×, fleet 0.75
  — grep proves **none** exists in executable BPR / sampler / fleet code. Simulator runs
  without them.
- **Function-default fallback**: α=0.15 (FHWA) in `models.py:19`, `traffic.py:48` — silent
  if config omits `bpr.alpha`.

Rail 114/30/600 is the one **correctly sourced** chain (yaml → `realworld_network_config`
→ rail edge) — no fix needed.

**Fix = consolidate each scalar to one sourced value.** Either reconcile code to the
documented value (α→0.36, lateness→2.45/0.75, implement 1.67×, add fleet 0.75) **or** relabel
docs to match the executed value. The bulk is human modeling decisions, not coding.

**Noise (decision #1) is non-blocking:** `scenario.py:62-65` only creates the
road_noise/turnaround RNG streams when σ/λ > 0, so deterministic-baseline=0 is a clean
option, and CRN pairing holds for any noise level.

## 5. D-ML — the 4th class is missing *inputs*, not logic

**Key correction:** the labeling logic **is already 4-class**
(`_risk_label` → normal/watch/risk/failure, asserted by
`test_realworld_ml_analysis.py:34-39`). But the input `completion_rate` is degenerate
({0, 0.33, 0.67, 1.0}, zero rows in the 0.80–0.95 "watch" band) → the model trains on 3
populated classes → `ml_baseline_v1.json` reports 3. The 4th class is not missing code; it
is missing realistic inputs.

- KMeans: fully absent (sklearn 1.9.0 present, KMeans imports cleanly) — ~80–120 lines.
- SHAP: not installed; wrap existing booster with `TreeExplainer` — ~60–100 lines + dep.
- NL summary: no generator — moderate, must be templated to pass the claim guard.
- `CLAUDE.md:52,130-132` still over-claim (kci_redesign already corrected) — trivial doc fix.
- Methodology note: current `index%5` split (line 276) is non-stratified — flag for
  imbalanced multi-class.

**Discrepancy to verify:** the D-ML agent recorded input `graph_source =
pilot_region_road.graphml` (the *real* OSM demo graph), not the Goseong stub. So the ML
baseline may be real-OSM-but-wrong-region rather than stub-poisoned. Re-baseline should run
on Goseong case-study results (→ D-GOSEONG).

## 6. D-CLAIM — make the record match reality

- **False-green `real_input_smoke`:** `_real_input_smoke_gate()`
  (`final_study_readiness.py:848-864`) checks only that policy IDs exist in the manifest —
  never the graph. Doc-only re-block (`status.md`, `agents.md` "3/15"→"2/15", ~15 min), or
  optional durable hardening (require a plausibility pass, ~1–2 h).
- **Decision #5 (ledger authority):** already resolved structurally — `FINAL_GATE_IDS`
  (15) and `FINAL_ACCEPTANCE_ARTIFACTS` (12) are code tuples; `final_study_ready = all
  gates ready AND no missing gates AND no missing artifacts`. No conflicting count. Close
  by recording the ruling in docs. The claim guard is fail-closed (`final_study_ready`
  hardwired false) — no ledger edit can flip it green.
- **84/52/36 figures:** internal docs consistently carry the superseded caveat; only the
  frozen competition 기획서 states them uncaveated (expected).

## 7. Realism ruling

**Realistic.** ~1–2 weeks of focused work total, gated on two user inputs:
1. Authorize the one-time **live Overpass extraction** for Goseong (offline-default
   opt-in).
2. Choose a **corridor-buffer strategy** (2–5 km buffer vs per-segment tiles).

Plus the D-PARAM modeling decisions (which α, which μ/σ, 1.67× in-scope, fleet 0.75).

Once D-GOSEONG lands, D-PARAM / D-ML / D-CLAIM all become small offline work and several
resolve automatically (4th ML class populates, `real_input_smoke` legitimately re-greens,
param values finally match a real corridor).

## 8. Open decisions (consolidated, for user)

1. **D-GOSEONG:** authorize 1× live Overpass extraction + corridor strategy?
2. **D-PARAM:** α = 0.15 / 0.36 / 0.50? lateness 1.2/0.25 vs 2.45/0.75? 1.67× apply vs
   drop? fleet 0.75 add vs retract?
3. **D-ML:** NL-summary scope? KMeans feature basis?
4. **#5:** confirm 15-gate phase ledger as authority (doc ruling)?
5. **#1 (noise):** deterministic baseline 0 vs keep 0.05/0.2 exploratory? (CRN-irrelevant)
