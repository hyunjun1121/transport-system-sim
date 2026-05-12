# Project Overview

This directory (`kci`) serves as the central workspace and planning hub for preparing a research manuscript targeted at the KCI-listed journal 한국군사학논집 (Korean Journal of Military Arts and Science). The research focuses on an industrial-engineering simulation evaluating the resilience of bus-only versus rail-bus multimodal transport for reserve-force mobilization along a virtual major-arterial road corridor (Songpa-gu to 72nd Infantry Division).

Currently, this folder contains the planning, auditing, formatting specifications, and execution instructions. The actual simulation code will be bootstrapped from an upstream repository according to the instructions in `plan.md`.

## Key Documents

*   `research_plan.md`: Defines the "WHY" and "WHAT" of the study. It outlines the research questions, scope (virtual corridor, IE methodology), expected contributions, and limitations.
*   `repo_assets_audit.md`: Defines the "WHICH FILES". It contains file-by-file decisions (COPY, ADAPT, EXCLUDE) dictating what to bring into this workspace from the upstream repository.
*   `submission_format.md`: Defines the format constraints extracted from the official journal template. It includes typography rules (Pretendard font), page setups, structural requirements, APA citation rules, and required submission attachments (e.g., security review document).
*   `agents.md`: Serves as the working context and decision log for AI agents operating in this workspace. It documents resolved decisions, binding constraints (e.g., coordinates policy, military framing), and overall workspace conventions.
*   `plan.md`: The actionable "HOW" document. It contains the optimized, phase-by-phase execution plan utilizing Claude Code's Agent Teams feature to run code bootstrapping, network construction, smoke tests, experiment runs, and manuscript drafting in parallel.

## Usage

This directory is intended to be used as an isolated workspace to build, run, and draft the KCI submission. The next primary action is to execute the steps outlined in `plan.md`. 

AI agents interacting with this project should:
1. Always reference `submission_format.md` for any formatting or writing tasks.
2. Follow the parallel execution strategies and prompts laid out in `plan.md`.
3. Consult `agents.md` to understand the established boundaries (e.g., using only publicly available military data, deferring real-world calibration).

## Building and Running
Currently, the directory is in the "planning phase". Once Phase 0 of `plan.md` is executed, the codebase will be bootstrapped here. Standard commands will involve running the Python simulator (e.g., `python main.py --phase 1 --config config.yaml`) as detailed in the execution plan.