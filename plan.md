# Autonomous Real-World Simulation Completion Plan

## Intent

Finish the transport-simulation implementation through an autonomous evidence harness, without relying on human review as a gate.

The plan should guide the workflow, not prescribe every command. The main objective is to produce a rigorous, real-world-oriented decision-support simulation that is internally tested, claim-bounded, reproducible, and reviewed by GPT-5.5 xhigh sub-agents before closeout.

Do not claim any of the following unless current repository audits independently prove them:

- operational route-command capability (not claimed);
- real-world forecasting accuracy (not claimed);
- publication readiness (not claimed);
- final-study readiness (not claimed);
- formal acceptance (not claimed).

## Local Runtime Assumption

Use an explicit runtime preflight before heavy work:

- detect CPU, RAM, Python, package versions, and GPU availability;
- verify RTX 3090 CUDA use with a small XGBoost or PyTorch-style smoke test when GPU-dependent analysis is planned;
- record whether GPU acceleration is used for ML/post-simulation analysis only;
- keep the simulation-engine acceleration claim separate from ML acceleration.

Current inspected machine context:

- GPU: NVIDIA GeForce RTX 3090, 24GB VRAM;
- CPU: AMD Ryzen 7 5800X3D, 8 cores / 16 logical processors;
- RAM: about 63.9GB.

## Core Workflow

### 1. Reconfirm Repository State

Start every execution pass by reading the current manifests, closeout matrix, plan status, and generated-output inventory. Treat prior state as a hypothesis until rechecked.

Output of this step:

- a short gap list;
- artifacts that already satisfy evidence requirements;
- artifacts that must be regenerated;
- tests that directly cover the gap.

### 2. Build The Autonomous Review Harness

Replace human-review dependency with structured GPT-5.5 xhigh reviewer evidence where the repository plan allows reviewer/sub-agent review.

The harness must:

- define reviewer personas and bounded scopes;
- pass each reviewer concrete artifact paths, manifests, and test outputs;
- require each reviewer to return pass/fail, evidence references, risks, and required fixes;
- write reviewer evidence to repository-local JSON/CSV records;
- never treat reviewer output as formal acceptance, publication approval, or real-world validation by itself.

Recommended reviewer roles:

- Real-World Modeling Reviewer: checks whether inputs, assumptions, and scenario structure support decision-support simulation claims.
- Simulation Correctness Reviewer: checks model logic, stochastic design, CRN/replication handling, and invariants.
- Data/Provenance Reviewer: checks source paths, manifests, cached inputs, hashes, and source-boundary language.
- Figure/Table/Report Reviewer: checks whether outputs match data and avoid overclaiming.
- Package/Reproducibility Reviewer: checks that a clean reviewer package can be rebuilt and audited.

### 3. Execute Work In Sequential Waves

Use sub-agents aggressively, but only after dependencies are clear. Do not run parallel agents on overlapping write scopes.

Wave A: state and dependency discovery

- Main agent reads the current plan, manifests, and test surface.
- Parallel explorer sub-agents inspect independent evidence surfaces: simulation/data, reports/claims, packaging/reproducibility.
- Main agent merges findings into one prioritized implementation queue.

Wave B: bounded implementation

- Split work by disjoint ownership: simulation logic, data/provenance, analysis/ML, figures/reports, package/audits.
- Spawn worker sub-agents only when the write paths are disjoint.
- Main agent keeps critical-path integration local.

Wave C: local verification

- Run targeted unit tests after each changed surface.
- Run compact smoke experiments before full or expensive runs.
- Use RTX 3090 only for ML/runtime checks where the code path actually supports CUDA.
- Record command, input manifest, output manifest, and failure reason.

Wave D: reviewer evaluation

- After local tests pass, send artifacts to GPT-5.5 xhigh reviewers.
- Reviewers judge only their bounded surface.
- Failed reviewer findings become implementation tickets.
- Re-review only the affected surface after fixes.

Wave E: self-refine and closeout

- Main agent performs a closing contradiction pass across code, manifests, figures, reports, and claim language.
- Close rows only when local evidence and reviewer evidence both support the closure.
- Preserve intentionally false readiness flags unless audits prove otherwise.

## Test And Verification Strategy

Prefer small-to-large verification:

- static file/path/hash checks;
- unit tests for changed modules;
- smoke simulation on reduced inputs;
- deterministic rerun or CRN consistency checks;
- compact pilot experiment;
- figure/table regeneration;
- review-package build and path audit;
- claim-language guard;
- readiness audits as status checks, not forced success targets.

Every verification pass should answer:

- what changed;
- what evidence was regenerated;
- what tests passed or failed;
- what claims are still not allowed.

## Sub-Agent Coordination Rules

Use GPT-5.5 xhigh for reviewer and high-risk design judgments. Use smaller or inherited models only for narrow mechanical inspection if appropriate.

Parallelization is allowed only when:

- tasks are independent;
- file write sets do not overlap;
- one task does not depend on another task's pending result;
- the main agent can continue useful local work while sub-agents run.

Sequential ordering is required when:

- a reviewer depends on regenerated artifacts;
- a worker depends on a prior design decision;
- a test depends on an implemented fix;
- package closeout depends on closing artifact paths.

Sub-agents are prohibited from:

- reverting unrelated changes;
- broadening the scope into publication or formal acceptance (not permitted);
- modifying files outside their assigned ownership;
- claiming external validation without repository evidence.

## Claim Boundary

Allowed language:

- decision-support simulation;
- quasi-real or real-world-oriented input pipeline;
- source-backed or cached-input evidence where manifests support it;
- stochastic scenario comparison;
- resilience and sensitivity analysis;
- ML-assisted post-simulation risk classification when runtime evidence supports it.

Disallowed unless independently proven:

- operational route plan (not claimed);
- real-time dispatch command (not claimed);
- calibrated forecast (not claimed);
- field-validated model (not claimed);
- publication-ready study (not claimed);
- closing accepted evidence package (not claimed).

## Stop Conditions

Stop and report when:

- all remaining closeout rows are supported by concrete local evidence and bounded reviewer evidence;
- or a blocker requires missing upstream data, missing source material, destructive recovery, or unavailable external access;
- or a test failure points to a real implementation defect that needs a focused fix.

Closing reporting must list:

- work completed;
- tests and audits actually run;
- sub-agent reviewers used and their verdicts;
- artifacts changed;
- claims still prohibited;
- next highest-value dependency-safe task.
