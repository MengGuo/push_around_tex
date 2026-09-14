# Robot-scaling baselines, post mode-generation fix (fc857a8) — digest

Re-run of the robot-team-scaling **baselines only** so that ours and the baselines are evaluated on the **same code**, removing the last mixed-version comparison in the paper.

## Protocol / provenance

- Code: experiment repo at `43c8d62a269241159e4e41eaebfd8a130ef73d64` (descends from `fc857a8`, the shared mode-generation fix).
- Config used (copy of the PushAround robot-scaling config, only `suite_name`/`output_dir`/`policies`/`robot_nums` changed): `robot_scaling_baselines_postfix.json`; resolved copy in this directory.
- Scene/protocol identical to the PushAround post-fix run: M=30 movable obstacles, 8x8 m, mass 20-30 kg, `reserve_robot_slots=4`, 800 s / 20 000 control steps, 8 parallel workers, no physics perturbation.
- Mode generation is the shared online path for every policy (`table_query=False greedy_online=True load_table=False`), so the baselines inherit the same mode generator PushAround used.
- Seeds 0-9 (n=10) for every (policy, N_R) cell.
- `DEBUG_MODEGEN_DIAG=1` was set in `child_env` **only to enable the rescue-path logging below**; it toggles prints, not behaviour.

## 1. Results (n=10 per cell)

| policy | N_R | Succ. | Success 95% CI (Wilson) | PT (s, mean±std) | ET (s, mean±std) | pushes | replans | sims | failures |
|---|---|---|---|---|---|---|---|---|---|
| dfs | 3 | 10/10 (100%) | [0.7225, 1.0] | 142.58 ± 183.08 | 178.13 ± 72.09 | 13.9 | 1.5 | 761.6 | task_done=10 |
| dfs | 4 | 9/10 (90%) | [0.5958, 0.9821] | 101.93 ± 103.93 | 175.87 ± 113.55 | 14.33 | 2.9 | 497.78 | task_done=9; timeout=1 |
| slpush | 3 | 8/10 (80%) | [0.4902, 0.9433] | 30.01 ± 46.25 | 193.29 ± 111.28 | 31.12 | 2.1 | 62.25 | task_done=8; plan_fail=1; timeout=1 |
| slpush | 4 | 8/10 (80%) | [0.4902, 0.9433] | 23.38 ± 18.21 | 171.72 ± 61.23 | 20.5 | 2.5 | 41.0 | task_done=8; timeout=2 |

## 2. Diagnostics — is the fc857a8 improvement shared or PushAround-specific?

Counts are summed over all trial logs of each cell (10 seeds). `subset_fallback_release` is route A of `fc857a8` (the temporary per-task robot release); `backtracking_*` is route B (bounded backtracking contact assignment).

| policy | N_R | trial logs | seq_greedy_fail | subset_fallback_release | backtracking_assignment | backtracking_rescued |
|---|---|---|---|---|---|---|
| dfs | 3 | 10 | 7370 | 2192 | 4414 | 178 |
| dfs | 4 | 10 | 10570 | 2946 | 5128 | 533 |
| slpush | 3 | 10 | 962 | 356 | 431 | 7 |
| slpush | 4 | 10 | 1988 | 523 | 931 | 21 |

**Headline:** the shared rescue paths fire on the baselines **6017 times** (subset/robot-release) and **11643 times** (backtracking). The improvement is therefore a property of the shared mode generator, **not** a PushAround-only behaviour.

## 3. Pre-fix vs post-fix baselines

| policy | N_R | pre-fix (n=5, superseded) | post-fix (n=10, this run) |
|---|---|---|---|
| slpush | 3 | 4/5 (80%) (PT 61.7, ET 196.7, 1 plan_fail) | 8/10 (80%) (PT 30.01 ± 46.25, ET 193.29 ± 111.28, task_done=8; plan_fail=1; timeout=1) |
| slpush | 4 | 0/5 (0%) (PT —, ET —, 5 plan_fail) | 8/10 (80%) (PT 23.38 ± 18.21, ET 171.72 ± 61.23, task_done=8; timeout=2) |
| dfs | 3 | 3/5 (60%) (PT 164.6, ET 199.8, 2 timeout) | 10/10 (100%) (PT 142.58 ± 183.08, ET 178.13 ± 72.09, task_done=10) |
| dfs | 4 | 4/5 (80%) (PT 131.0, ET 190.9, 1 plan_fail) | 9/10 (90%) (PT 101.93 ± 103.93, ET 175.87 ± 113.55, task_done=9; timeout=1) |

PushAround post-fix reference (unchanged, from the paper's robot-scaling suite):

| N_R | Succ. | PT (s) | ET (s) |
|---|---|---|---|
| 2 | 10/10 (100%) | 23.9 ± 10.9 | 105.0 ± 35.9 |
| 3 | 10/10 (100%) | 30.0 ± 12.7 | 97.3 ± 42.1 |
| 4 | 10/10 (100%) | 29.2 ± 8.9 | 110.1 ± 33.1 |

## 4. Files

- `raw_results_all.csv` — raw per-trial results (schema identical to the other suites).
- `summary.csv` — suite-generated summary (via `plot_scaling_suite`).
- `paper_summary.csv` — the table above, machine-readable.
- `diagnostics.csv` — the rescue-path counts above.
- `resolved_config.json` — config actually used.
- `experiment_repo_commit.txt` — experiment-repo commit hash.
- `trial_logs/` — per-trial logs (source of the diagnostic counts).
