# CLAUDE.md — Transport System Simulation

## Project Overview

Wartime reserve force transport micro-simulation: compares **bus-only** vs **rail-bus multimodal** transport for moving ~1,000 reservists from Seoul Songpa-gu to a forward area.

**Environment**: Android Termux (ARM64). Use `pkg` for system packages, `pip` for Python packages.

## Repository Structure

```
main.py                    # CLI entry: --quick, --test, --phase 1|2
config.yaml                # All experiment parameters (network, BPR, DoE grids)
generate_report.py         # Generates report.docx from report_draft.md (python-docx)
report_draft.md            # Korean narrative report source (17K chars)
report.docx                # Generated Word document
microsim_experiment_proposal_v3.docx  # Original proposal (pre-implementation)
src/
  models.py                # BPR travel time, Bernoulli failures, LogNormal delays
  network.py               # Build NetworkX DiGraph from config (6 road + 1 rail link)
  policies.py              # StrictPolicy, GracePolicy(W, theta)
  metrics.py               # MetricsCollector (makespan, success_rate, resource_efficiency)
  scenario.py              # SimPy DES: run_scenario() → dict, _bus_coordinator, _multimodal_coordinator
  experiment/
    doe.py                 # phase1_grid (s x p_fail), phase2_grid (sigma x policy)
    runner.py              # CRN paired execution: run_phase1(), run_phase2()
    analysis.py            # compute_ci(), find_breakeven(), summarize_phase1()
  visualize/
    plots.py               # Heatmaps, pareto curves, breakeven line (matplotlib/seaborn, Agg backend)
tests/
  test_models.py           # 11 unit tests (all passing)
refs/                      # Cloned reference repos (inventory-simulation, HSR_Simulation_SimPy, etc.)
results/                   # CSV outputs and PNG plots from experiment runs
```

## How to Run

```bash
python main.py --test       # Single scenario debug
python main.py --quick      # Smoke test (R=3, reduced grid)
python main.py              # Full experiment (1,590 CRN pairs)
python tests/test_models.py # Unit tests
python3 generate_report.py  # Regenerate report.docx from report_draft.md
```

## Key Models

- **BPR**: `t = t0 × (1 + 0.15 × (s × v/C)^4)` — wartime scaling via `s`
- **Link failure**: `X_e ~ Bernoulli(p_fail × p_fail_scale)` — road links only, rail immune
- **Lateness**: `Y ~ LogNormal(μ=2.0, σ²)` — σ controls long-tail severity
- **STRICT policy**: Depart immediately at scheduled time
- **GRACE policy**: Wait until max W minutes elapsed OR θ% arrived OR bus full
- **CRN pairing**: Same seed for both scenarios in each replication

## Known Issues & Next Steps

These are documented in the report (Section 8.2-8.3) and need implementation:

1. **Bus dispatch tuning** — Scheduled departure time is independent of last arrival; STRICT should leave latecomers for next bus. Currently bus waits for last person in group, making STRICT/GRACE indistinguishable (see `scenario.py:_bus_coordinator` lines 147-163).
2. **Dynamic traffic volume** — BPR currently uses fixed vol=100 for all links. Should track per-link volume during simulation.
3. **Failure model enhancement** — Add "capacity reduction" mode (not just full blockage); extend p_fail_scale range beyond 0.15.
4. **Transfer time modeling** — Multimodal scenario has no explicit transfer penalty (boarding, platform movement).
5. **Policy differentiation** — Phase 2 results show all policies identical because departure policy isn't properly applied.

## Dependencies

```bash
# System (Termux)
pkg install python numpy scipy matplotlib libxml2 libxslt python-lxml
# Python
pip install simpy networkx pandas pyyaml seaborn python-docx
```

## Git

- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`
- Branch: `main`
- Git user: hyunjun1121 / hyunjun1121@users.noreply.github.com

## Conventions

- All code comments and docstrings in English
- Report (report_draft.md, report.docx) in Korean
- Do not add emojis unless explicitly requested
- Keep changes minimal — don't refactor beyond what's asked
