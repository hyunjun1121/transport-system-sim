# deadline_mechanism — G2 censoring/deadline knob diagnosis

> Phase 0.1 (G2) deliverable. Defect-checklist **G2 (deadline/censoring)**: prove which
> knob drives `censored_count`, and separate the simulation horizon from the doctrinal
> success deadline. Quasi-real / decision-support only — not operational, not calibrated.

## 1. The mechanism (verified, file:line)

Three knobs live on `MetricsCollector` (`src/metrics.py`). Their effects:

| Knob | Default | Run value (`pilot_experiments.py:1164`) | Drives |
|---|---|---|---|
| `time_limit` | `1440.0` | **`200.0`** (3.3 h) | `success_count` (L76), `censored_count` (L86-91), `completion_rate` (L94-99), arrival quantiles (L192-194) |
| `late_penalty_min` | `None` → `time_limit` | **`300.0`** | `penalized_makespan` ONLY (L125-143) |
| (observed) `leftover_count` | `0` | runtime | floors `censored_count` (L88-91) |

`censored_count = max(total_personnel − success_count, leftover_count)` where
`success_count` counts arrivals with `t ≤ time_limit`.

`penalized_makespan = max(makespan, time_limit) + censored_count × late_penalty_min`.

**Conclusion: `censored_count` is driven by `time_limit` (the simulation horizon),
NOT by `late_penalty_min`.** `late_penalty_min` is a *post-hoc penalty weight* on
already-censored people — it cannot move `censored_count` or `completion_rate`.

## 2. Proof — `tests/test_metrics_deadline_knobs.py` (direct-exec, all pass)

A fixed population (1000 pax; 840 @150 min, 60 @280, 60 @340, 40 stranded) sweeps
each knob independently:

```
time_limit sweep (late_penalty fixed):  censored 160 -> 100 -> 40
   tl=200 (3.3h): success=840 censored=160 completion=0.84
   tl=300 (5.0h): success=900 censored=100 completion=0.90
   tl=360 (6.0h): success=960 censored= 40 completion=0.96
   makespan invariant = 340 (independent of time_limit)

late_penalty sweep (tl=200 fixed):      censored stays 160
   penalty=300/600/999: censored=160 completion=0.84 (invariant)
   penalized_makespan = 340 + 160*penalty  (only this moves)
```

So: to change completion/censoring, move `time_limit`. Moving `late_penalty_min`
re-scales `penalized_makespan` and nothing else. Confirmed at the metrics layer,
no scenario machinery involved.

## 3. The defect: horizon conflated with deadline

Current run `time_limit = 200 min` (3.3 h) does double duty:

1. It is the **simulation horizon** — how long we observe deliveries; pax not
   delivered in-window are "censored".
2. It is treated as the **decision deadline** — `completion_rate` is reported at
   this single horizon, with no separable doctrinal threshold.

This conflates two distinct things:

- **Capacity-starved** pax — the network physically cannot deliver them even at an
  arbitrarily long horizon (≈ `leftover_count`). This is a *transport-structure*
  signal.
- **Deadline-missed** pax — delivered, but after the standup deadline. This is an
  *operational-readiness* signal.

At `time_limit = 200`, a person who would arrive at 280 min (4.7 h) is counted as
"censored" (indistinguishable from someone the network could never move). That is
the G2 design defect: the horizon and the deadline must be separable knobs.

## 4. Introduced concept: `success_deadline_min` (post-hoc re-aggregation, Phase 5)

Separate two horizons:

- **`time_limit` (simulation horizon)** — run long enough to observe all physically
  deliverable pax (e.g. 12–24 h), so the only true "censoring" is capacity
  starvation, not an artificial early cutoff.
- **`success_deadline_min` (decision deadline, post-hoc)** — a doctrinal standup
  threshold applied *after* the run, by re-aggregating the recorded arrival-time
  distribution. Completion is reported **at each ladder level**, not at one horizon.

Proposed ladder (`high_level_plan.md` Phase 5; values are sensitivity assumptions,
not calibrated):

| Level | `success_deadline_min` | Doctrinal reading (assumption) |
|---|---|---|
| Ld1 | 300 (5 h) | tight local standup |
| Ld2 | 360 (6 h) | baseline local |
| Ld3 | 420 (7 h) | — |
| Ld4 | 480 (8 h) | regional |
| Ld5 | 600 (10 h) | — |
| Ld6 | 720 (12 h) | extended regional |

Post-hoc re-aggregation (no re-run needed — arrivals are already recorded):
`completion_rate@deadline = |{arrivals t ≤ deadline}| / total_personnel`.

This makes the **completion-rate-vs-deadline curve** a first-class output — the
planning-doc "5h ladder" becomes one point on it, not the whole story.

## 5. Reconciliation with the submitted planning doc (84 / 52 / 36 %)

The planning-doc figures (bus-only 84.0 %, multimodal 52.0 %, core-axis blockage
36.0 %) are a **post-hoc 5 h view** = `success_deadline_min = 300` on the reset-
prior codebase. They are **not reproducible** from current code because:

- Current `time_limit = 200` (3.3 h), so completion is reported at 3.3 h, not 5 h.
- The reset moved/severed the code that produced those rows.

Per `high_level_plan.md`, the planning-doc numbers are **not chased**: the
defect-free rebuild regenerates an authoritative completion-vs-deadline curve
(§4), of which 5 h is one level. `final_study_ready = false` throughout.

## 6. Code change landing point (Phase 5, not now)

- Keep `MetricsCollector` semantics (G2-proven) unchanged — `time_limit` stays the
  single censoring driver; `late_penalty_min` stays the `penalized_makespan` weight.
- Phase 5 adds: (a) a longer run `time_limit` (observe full delivery curve), and
  (b) a post-hoc `completion_rate@deadline` re-aggregation over the recorded
  arrival list at each ladder level — reuses `record_arrival` data already present.
- No metrics-layer edit in Phase 0. This memo + the passing knob test satisfy G2:
  the censoring mechanism is proven and documented, and the horizon/deadline split
  is named and parked for Phase 5.

## 7. G2 exit (Phase 0)

- [x] Mechanism verified (`metrics.py:66-143`)
- [x] Knob isolation proven (`tests/test_metrics_deadline_knobs.py`, 4/4 pass)
- [x] `success_deadline_min` concept documented + separated from `time_limit`
- [x] Planning-doc 5h figures reconciled (non-reproducible → superseded)
- [x] Code-change landing point named (Phase 5)

**G2 status: green (mechanism diagnosed + documented; decoupling deferred to Phase 5
by design, not blocked).**
