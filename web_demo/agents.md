# Web Demo Handoff Context

This directory is reserved for an outsourced web demo for the transport-system
simulation project. The demo should make the existing Python research prototype
understandable to evaluators of the 2026 Defense AI Idea Competition.

## Project Summary

The parent repository implements a disrupted regional personnel-transport
simulation. The current baseline compares two transport strategies for moving
approximately 1,000 people from an assembly context to a destination zone:

- `bus_only`: people assemble at `A` and travel by road to `D`.
- `multimodal`: people shuttle from `A` to rail access point `S`, ride rail
  from `S` to `R`, then complete the last mile by road from `R` to `D`.

The project started from a reserve-force transport use case, but the current
framing is broader and more appropriate for public-sector and defense planning:
an AI-assisted, simulation-based decision-support framework for emergency
personnel movement, disrupted regional mobility, and contingency transport
planning.

The demo must present the system as a decision-support and resilience-evaluation
tool. It must not present the current prototype as an operational route plan,
real-world forecast, command-and-control system, or deployment-ready military
system.

## Competition Context

The target competition topic is:

> AI-assisted fast and accurate decision-support methods.

The relevant judging dimensions are:

- Planning fit: whether the proposal fits the purpose of defense AI adoption.
- Originality: whether it avoids copying commercial products/services or
  infringing copyrights.
- Completeness: whether it covers the planning, development, and operation
  process rather than merely introducing a product.
- Plagiarism: proposals above the stated plagiarism threshold can be excluded.
- Scored review categories: creativity, feasibility, military effectiveness,
  and completeness.

The demo should therefore prove that this is not just a slide idea. It should
show a concrete, already-started prototype with scenario inputs, policy
comparison, simulation outputs, evidence boundaries, and a roadmap toward a
military MVP.

## Product Positioning

Recommended English product name for the web demo:

**AI Emergency Transport Decision-Support Simulator**

Working proposal title, translated:

**AI-Based Emergency Transport Decision-Support Simulator**

One-sentence pitch:

> The system compares transport alternatives under road disruption, congestion,
> delayed assembly, fleet constraints, and multimodal transfer uncertainty, then
> summarizes which options are faster, safer, and more robust for planning.

The demo should emphasize:

- Simulation-based comparison, not static route search.
- Uncertainty-aware decision support, not deterministic navigation.
- Policy and scenario comparison, not a single "best route" answer.
- Existing Python implementation, tests, generated figures, and review
  artifacts, not a speculative concept only.
- Human-in-the-loop command decision support, not automated orders.

## Existing Repository Context

Important parent-repository files and folders:

- `main.py`: CLI entry point for abstract experiments.
- `config.yaml`: scenario and model configuration.
- `src/`: core simulator implementation.
- `src/realworld/`: real-world or quasi-real input pipeline and review aids.
- `scripts/`: experiment, audit, packaging, reproducibility, figure-generation,
  and review-packet scripts.
- `tests/`: Python test suite.
- `results/`: generated experiment outputs and figures.
- `results/report_figures/`: ready-to-use report figures.
- `paper/paper_draft.md`: English manuscript scaffold.
- `report_draft.md`: Korean report source.
- `README.md`, `status.md`, `plan.md`, `IMPLEMENTATION_PLAN.md`: project
  status, boundaries, implementation notes, and planned work.
- Competition-specific working folder at the repository root: contains the
  Korean competition application template, official-info memo, and proposal
  writing-frame notes.

Known existing report figures:

- `results/report_figures/figure0_pipeline_overview.png`
- `results/report_figures/figure1_time_efficiency_summary.png`
- `results/report_figures/figure2_undelivered_risk.png`
- `results/report_figures/figure3_decision_lens.png`

These can be copied into the web demo only if the main repository owner asks
for that. If copied, preserve source attribution in the demo code comments or
asset manifest.

## Current Research and Acceptance Status

The current repository is a strong prototype and review package, but it is not a
final accepted operational study.

Current status from the parent project:

- `final_study_ready=false`
- Final-study gates: 3 ready, 12 blocked
- Formal acceptance readiness: 0/12
- Formal acceptance artifacts are intentionally absent until source-backed human
  reviewer decisions exist.
- Validation, graph-scale, sensitivity, experiment, reproducibility, and final
  audit packets are review aids only.

The demo must keep these boundaries visible. It may say:

- "research prototype"
- "decision-support demo"
- "simulation-based comparison"
- "planning and training aid"
- "requires military data, security review, and validation before deployment"

The demo must not say:

- "operationally validated"
- "deployment-ready"
- "real-time battlefield forecast"
- "automatic command recommendation"
- "guaranteed optimal route"
- "final accepted study"
- "rail-bus is always better than bus-only"

## Implemented Model Concepts to Explain Visually

The web demo should explain these concepts in a compact, evaluator-friendly
way:

- People arrive at an assembly point with uncertainty.
- Road links can be normal, degraded, or blocked.
- Road travel time is affected by congestion using BPR-style travel time.
- Bus-only and rail-bus multimodal strategies can be run under the same
  scenario conditions.
- Vehicles have finite fleet size and turnaround constraints.
- Rail uses fixed-headway service in the current abstraction.
- Transfers add fixed and passenger-dependent delay.
- Metrics include makespan, completion rate, success rate, censored passenger
  count, leftover people, and penalized makespan.
- Common-random-number style paired comparison helps compare policies under
  matched stochastic conditions.
- Sensitivity analysis identifies which uncertain inputs change the strategy
  decision most.

## Recommended Demo Scope

Keep the first outsourced version static or mostly static. The goal is to make
the proposal credible, not to rebuild the full simulator in the browser.

Recommended scope:

1. A single-page or two-page responsive web app.
2. Scenario selector with 3-4 preset cases:
   - Normal road conditions
   - Road disruption
   - Delayed assembly
   - Multimodal transfer stress
3. Policy comparison view:
   - Bus-only
   - Rail-bus multimodal
   - Optional future policy: redundant last-mile or staggered dispatch
4. KPI cards:
   - Completion rate
   - Penalized makespan
   - Undelivered or censored people
   - Risk note
5. Visual narrative:
   - Pipeline diagram
   - Strategy comparison chart
   - Risk/undelivered chart
   - Decision lens panel
6. Claim-boundary banner:
   - "Research prototype / planning demo only"
   - "Not an operational route plan"

Avoid overbuilding:

- Do not implement a full GIS system for the first version.
- Do not claim live military data integration.
- Do not attempt real routing unless explicitly scoped later.
- Do not require a backend unless the owner requests live simulation runs.

## Suggested UX Structure

The UI should feel like a quiet operational planning dashboard, not a marketing
landing page.

Recommended first screen:

- Header: "AI Emergency Transport Decision-Support Simulator"
- Short subtitle: "Compare bus-only and rail-bus alternatives under disruption,
  congestion, delayed assembly, and fleet constraints."
- A compact status badge: "Research prototype - not operational routing"
- Scenario controls on the left or top.
- KPI comparison cards.
- Main chart or map-style schematic.
- Decision explanation panel.

Recommended sections:

1. Scenario Setup
   - Personnel count
   - Disruption level
   - Congestion level
   - Assembly delay
   - Transfer stress

2. Strategy Comparison
   - Bus-only vs rail-bus multimodal
   - Completion, delay, undelivered risk, and bottleneck summary

3. Decision Lens
   - "When bus-only is preferable"
   - "When rail-bus multimodal is preferable"
   - "When evidence is insufficient"

4. Implementation Evidence
   - Python simulation already exists
   - Model includes disruption, finite fleet, rail headway, transfer delay,
     completion-aware metrics, and paired comparisons
   - Tests, scripts, data, results, and review packets exist in the parent repo

5. Deployment Roadmap
   - Prototype cleanup
   - Military MVP with anonymized/aggregated data
   - Closed-network pilot
   - Training and planning integration
   - Region template expansion

## Visual Design Direction

Use a restrained defense-planning dashboard style:

- Dense but readable layout.
- Neutral background with high-contrast cards and charts.
- Use color semantically:
  - Green/blue for completed or robust
  - Amber for caution
  - Red for blocked/high risk
  - Gray for unavailable/not accepted
- Avoid flashy gradients, decorative blobs, or marketing-style hero sections.
- Keep text concise and operationally grounded.
- Do not use oversized claims or "AI magic" phrasing.

Charts and visuals that fit the project:

- Sankey or flow diagram: `A -> D` bus-only vs `A -> S -> R -> D` multimodal.
- Side-by-side KPI cards.
- Bar chart for completion rate or undelivered people.
- Line or heatmap for disruption/congestion sensitivity.
- Simple node-edge schematic for disrupted links and rail trunk.
- Pipeline diagram: data -> simulator -> AI analysis -> decision dashboard.

## Data Strategy for First Demo

First version may use static demo data derived from the repository narrative and
existing figures. If using synthetic numbers, label them clearly as illustrative
demo data.

Recommended data contract:

```json
{
  "scenario_id": "road_disruption",
  "scenario_label": "Road disruption",
  "policies": [
    {
      "policy": "bus_only",
      "completion_rate": 0.0,
      "penalized_makespan_min": 0.0,
      "undelivered_count": 0,
      "risk_level": "medium",
      "decision_note": "Illustrative placeholder until linked to generated results."
    }
  ],
  "claim_boundary": "Illustrative demo data, not operational routing."
}
```

If the owner later requests live integration, the backend can call existing
Python scripts rather than reimplementing simulation logic in TypeScript.

## Web Implementation Recommendation

Recommended stack for outsourced demo:

- Static HTML/CSS/TypeScript, Vite + React, or Next.js static export.
- No backend for v1 unless live simulation is explicitly requested.
- Charts: Recharts, Plotly, ECharts, or D3 depending on contractor preference.
- Icons: use a standard icon set such as lucide-react if React is used.
- Assets: local PNG/SVG assets only; avoid external runtime dependencies for
  sensitive demos.

For a first proposal/demo package, a static build that opens locally or can be
hosted on a simple static server is sufficient.

## Required Demo Copy Guardrails

Use:

- "AI-assisted decision support"
- "simulation-based policy comparison"
- "planning and training aid"
- "research prototype"
- "scenario and sensitivity exploration"
- "human-in-the-loop decision support"
- "requires validation before operational use"

Avoid:

- "autonomous command"
- "real-time operational routing"
- "battlefield guarantee"
- "fully validated"
- "official military system"
- "best route command"
- "always superior"

## Suggested Demo Text Blocks

Hero/title area:

> AI-assisted emergency transport decision support for disrupted regional
> mobility.

Short explanation:

> The prototype compares bus-only and rail-bus multimodal transport strategies
> under congestion, disrupted links, delayed personnel assembly, fleet limits,
> rail headway, and transfer delay. It helps planners see which option is more
> robust under a given scenario and where the evidence is still uncertain.

Boundary note:

> This is a planning and research demo. It is not an operational route plan, a
> real-world forecast, or an automated command system.

Decision lens:

> The tool does not ask "which mode is always best?" It asks "under this
> disruption, demand, and resource profile, which alternative has better
> completion, delay, and risk behavior?"

## Suggested File/Folder Layout

If the contractor implements the demo inside this folder, use:

```text
web_demo/
  agents.md
  README.md
  package.json
  index.html
  src/
    App.tsx
    main.tsx
    data/
      scenarios.ts
    components/
      ScenarioControls.tsx
      KpiCards.tsx
      FlowDiagram.tsx
      DecisionLens.tsx
      EvidencePanel.tsx
  public/
    figures/
      figure0_pipeline_overview.png
      figure1_time_efficiency_summary.png
      figure2_undelivered_risk.png
      figure3_decision_lens.png
```

Do not move parent-repository files unless explicitly requested. If figures are
needed inside `web_demo/public/figures`, copy them and document the source.

## Acceptance Criteria for the Outsourced Web Demo

The demo is acceptable when:

- It can run locally from `web_demo` with documented commands.
- It presents the project as decision support, not operational routing.
- It includes at least one visual comparison between bus-only and rail-bus
  multimodal strategies.
- It includes at least one disruption or uncertainty control.
- It includes KPI cards for completion/risk/delay-style metrics.
- It includes a clear claim-boundary banner.
- It includes a concise implementation-evidence panel.
- It is readable on desktop and mobile.
- It does not expose private or sensitive military data.
- It does not claim formal acceptance, final validation, or deployment readiness.

## Notes for Contractors

Before editing the parent repository, read this file and the parent `README.md`.
Keep demo work localized under `web_demo/` unless the repository owner gives a
specific instruction to modify shared project files.

The strongest story is not "we will build an AI dashboard someday." The strongest
story is:

> A Python simulation and audit-oriented research prototype already exists. The
> web demo makes its decision logic visible: scenario inputs, alternative
> policies, stochastic uncertainty, outcome metrics, and claim boundaries.
