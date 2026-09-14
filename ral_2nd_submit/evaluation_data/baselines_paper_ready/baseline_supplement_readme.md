# PushAround vs baselines — supplementary generalization data (paper-ready digest)

**Authoritative machine-readable data:** `baseline_supplement_data.json` (same numbers, per-cell fields incl. Wilson CI, mean±std of PT/ET, failure reasons). This file is a human/agent digest only.

## Scene & protocol (common to all runs)

- workspace 8x8 m, M=30 movable obstacles, mass 20-30 kg; trial budget 800 s / 20 000 control steps; same simulator/success criterion.

- PushAround main runs: seeds 0-9 (n=10). Baseline supplements (this task): seeds 0-4 (n=5) — Wilson CIs are still wide, treat as indicative.

- Baseline policies SL-Push (sim) and DFS-WCCG are the exact configs used in the main density suite (density resolved_config policies).


## 1. Physics-mismatch robustness (execution-only perturbation; nominal planning)

Success rate by condition; PushAround n=10, baselines n=5.

| condition (family x factor) | PushAround | SL-Push | DFS-WCCG |
|---|---|---|---|
| nominal | 100% (n=10) | 60% (n=5) | 60% (n=5) |
| mass_0p6 | 100% (n=10) | 60% (n=5) | 60% (n=5) |
| mass_1p4 | 100% (n=10) | 20% (n=5) | 20% (n=5) |
| friction_0p6 | 90% (n=10) | 60% (n=5) | 60% (n=5) |
| friction_1p4 | 100% (n=10) | 0% (n=5) | 40% (n=5) |
| force_0p6 | 90% (n=10) | 0% (n=5) | 40% (n=5) |
| force_1p4 | 100% (n=10) | 60% (n=5) | 80% (n=5) |
| spin_0p6 | 100% (n=10) | 20% (n=5) | 60% (n=5) |
| spin_1p4 | 100% (n=10) | 40% (n=5) | 100% (n=5) |

Headline: SL-Push collapses to 0% under many +-40% perturbations; DFS-WCCG is weaker overall and slow; PushAround stays >=90-100% across the subset (full grid 10 seeds: >=90%).

## 2. Robot-team scaling (M=30 nominal)

| policy | N=2 | N=3 | N=4 |
|---|---|---|---|
| PushAround (n=10) | 100% (n=10) | 100% (n=10) | 100% (n=10) |
| SL-Push (n=5) | - | 80% (n=5) | 0% (n=5) |
| DFS-WCCG (n=5) | - | 60% (n=5) | 80% (n=5) |

N>2 support (measured): DFS-WCCG completes trials at N=3 and N=4; SL-Push runs N=4 planning but fails (plan_fail). PushAround N=4 exceeds both baselines.

## 3. Caveats / notes for the paper writer

- Baseline supplement n=5 seeds (0-4) per cell; Wilson CIs wide - indicative only.
- N>2 support (measured): SL-Push runs with N=4 but plan_fail; DFS-WCCG supports N=3 and N=4.
- Replanning caveat: baseline rows show non-zero replan counters yet collapse under +/-40% execution perturbations -> their replanning is not perturbation-aware (inference from results; verify a failure log before asserting in text).
- PushAround physics-mismatch numbers predate the mode-generation fix and were NOT re-run (scale): they are conservative for PushAround.
- PushAround robot-scaling numbers are POST-fix (commit fc857a8) and replace the earlier N=4 = 70% row; the superseded pre-fix cells are kept as `robot_scaling.cells.pusharound_prefix_10seeds`.
- Raw provenance: outputs/revision/physics_mismatch/{raw_results,summary}.csv ; outputs/revision/robot_scaling_modefix/raw_results_all.csv ; outputs/revision/robot_scaling/{raw_results_all,summary}.csv (pre-fix reference) ; outputs/revision/physics_baselines_subset/{slpush,dfs}/ ; outputs/revision/robot_scaling_baselines/ ; outputs/revision/modefix_eval.json

## 4. Mechanism note: temporary robot release (subset modes)

- Trigger: No full-team contact-mode assignment exists for a push task (small pushable faces and/or the pairwise pusher-clearance constraint rejects every remaining candidate of one robot).
- Behaviour: Up to mode_gen_subset_max_drop robots are excluded for that single push task only; the remaining robots execute the push and the released robots hold their pose. The full team is available again for every later task.
- Cost: The excluded robots are charged mode_gen_subset_penalty per released robot when ranking candidate modes, so full-team modes are preferred whenever feasible.
- Scope: Local, per-task execution mechanism inside mode generation; global planning, task sampling and the search tree are unchanged.
- Measured effect (robot scaling, 10 seeds): N_R=2 8/10 -> 10/10, N_R=3 10/10 -> 10/10, N_R=4 7/10 -> 10/10.
- Enabled together with bounded backtracking contact assignment (`mode_gen_assignment_backtrack`), which removes the legacy greedy's robot-order sensitivity; both are mode-generation-local and leave global planning unchanged.

**Ready-to-adapt sentence (EN):** When no contact mode exists for the full team on a given push task - typically on small faces or under the pairwise pusher-clearance constraint - PushAround temporarily releases one robot for that single push (the released robot holds its pose) and re-activates the full team for subsequent tasks; this purely local fallback raised the 4-robot success rate from 70% to 100% over ten seeds while leaving the 2- and 3-robot cases unchanged or better.

## 4. Provenance
- JSON + raw: see `meta`/notes; raw CSVs under `outputs/revision/` (physics_mismatch, physics_baselines_subset, robot_scaling, robot_scaling_baselines).
