# Re-run spec: robot-scaling baselines with the current (post mode-generation-fix) code

**Owner:** experiment agent · **Repo:** `push_around_tex` (paper repo; the simulator/suite code lives in the experiment repo) · **Priority:** high, small, self-contained

---

## 1. One-paragraph context

We are finalizing an RAL revision of the paper *PushAround: Collaborative Path Clearing via Physics-Informed Hybrid Search*. Two reviewer-requested studies — **physics-model mismatch** and **robot-team scaling** — now include baseline comparisons (SL-Push (sim), DFS-WCCG). Between the two runs we landed an algorithmic improvement to **mode generation**: commit `fc857a8` introduced (a) *bounded backtracking contact assignment* (removes the robot-order sensitivity of the legacy greedy replacement) and (b) a *temporary per-task robot release* fallback (when no full-team contact assignment exists for a push task, one robot is released for that single push, charged a penalty during ranking, and the full team is re-activated afterwards). This improvement raised PushAround's 4-robot success rate from 70% to 100% over 10 seeds.

**The problem:** the improvement is a **code-level default in the shared mode-generation module**, not a PushAround-only policy flag. Proof: `data/robot_scaling/resolved_config.json` (pre-fix) and `data/robot_scaling_modefix/resolved_config.json` (post-fix) are **byte-identical except for `output_dir` and `suite_name`** — no `mode_gen_subset_*` / `mode_gen_assignment_backtrack` keys exist in either. Consequently:

- PushAround robot-scaling numbers = **post-fix** (new code);
- robot-scaling **baseline** numbers = **pre-fix** (old code), taken before/around the fix.

So the paper's current N=3/N=4 comparison is literally *new code (ours) vs old code (baselines)* on a **shared** component. That is exactly the kind of fairness issue Reviewer 4 raised (same timeout, budget, reachability, simulator). **This re-run removes the only mixed-version comparison in the paper.**

---

## 2. Scope — do exactly this, nothing else

**IN SCOPE:** re-run the **robot-team-scaling baselines only** — `SL-Push (sim)` and `DFS-WCCG` at `robot_num ∈ {3, 4}` (optionally also `2`), with the **current code**, same scene/protocol as the PushAround post-fix run.

**OUT OF SCOPE (do NOT re-run):**

| Study | Why it is fine as-is |
|---|---|
| Main comparison (Scenario 1, 40 trials) | ours and baselines from the same suite run — consistent |
| Density scaling (M=15…45, 10 seeds) | ours and baselines from the same suite run — consistent (all pre-fix; our results are already 100%, i.e. conservative) |
| Physics mismatch | ours **and** baselines are both pre-fix → apples-to-apples; only a wording caveat ("conservative") is needed |
| WCCG validation | does not involve mode generation |

**Optional, low priority (only if spare compute):** re-run the *physics-mismatch* study post-fix (ours + baselines, ~250 trials) so the "these numbers predate the mode-generation fix" caveat can be deleted. Not required for correctness.

---

## 3. Exact experiment specification

### 3.1 Base configuration — copy and modify only two fields

Copy `data/robot_scaling_modefix/resolved_config.json` **verbatim**, then change only:

```jsonc
{
  "suite_name": "revision_robot_scaling_baselines_postfix",
  "common": {
    // ...everything else unchanged from data/robot_scaling_modefix/resolved_config.json
    "output_dir": "outputs/revision/robot_scaling_baselines_postfix"
  }
}
```

Resulting run parameters (must match the PushAround post-fix run exactly):

| Parameter | Value |
|---|---|
| `experiments.robot_scaling.type` | `robot_scaling` |
| `obstacle_count` | `30` |
| `world_width` / `world_height` | `8.0` / `8.0` |
| `reserve_robot_slots` | `4` |
| `robot_nums` | `[3, 4]` (add `2` if you want the full row) |
| `common.seeds` | `[0,1,2,3,4,5,6,7,8,9]` |
| `common.trial_timeout_sec` | `800` |
| `common.max_control_steps` | `20000` |
| `common.num_parallel_workers` | `8` |
| `common.env_overrides` | `{"min_mass": 20.0, "max_mass": 30.0}` |
| `common.policy_overrides` | unchanged: `load_mode_table:false`, `mode_gen_via_greedy_opt:true`, `mode_gen_via_table_query:false`, `planning_timeout_sec:800` |
| `common.use_mode_table` / `ensure_mode_table` | `false` |
| `python_exe` | `python` |

**No physics perturbation** in this suite (`physics_condition` empty, all `*_exec` scales = 1.0).

### 3.2 Policies — use these blocks verbatim

These are the **exact** baseline definitions used in the main density suite; do not add overrides, do not "improve" the baselines.

```json
"policies": [
  { "base_policy": "slpush", "label": "SL-Push (sim)", "name": "slpush" },
  { "base_policy": "dfs",    "label": "DFS-WCCG",     "name": "dfs"    }
]
```

### 3.3 Code version — critical

Run at **commit `fc857a8` or later**, i.e. with the mode-generation refinements active (bounded backtracking contact assignment + subset-mode robot release). If these are behind any flag in the current code, leave the flags at their **defaults** — the point is that the baselines receive exactly the same shared mode generator that PushAround used in `data/robot_scaling_modefix`.

**Sanity check before launching:** confirm in the resolved config / code that no baseline-specific override disables the new contact-assignment backtracking or the release fallback. If the baselines do not go through this module at all, that is a *valid finding* — report it (see §6).

---

## 4. Reference numbers

### 4.1 PushAround, post-fix (target of the comparison; from `data/robot_scaling_modefix/raw_results_all.csv`, n=10)

| N | Succ. | PT (s, mean±std) | ET (s, mean±std) | #pushes | #sims |
|---|---|---|---|---|---|
| 2 | 10/10 (100%) | 23.9 ± 10.9 | 105.0 ± 35.9 | 11.7 | 81 |
| 3 | 10/10 (100%) | 30.0 ± 12.7 | 97.3 ± 42.1 | 11.1 | 66 |
| 4 | 10/10 (100%) | 29.2 ± 8.9 | 110.1 ± 33.1 | 10.0 | 59 |

### 4.2 Baselines currently in the paper — **pre-fix, n=5**, to be superseded

| Policy | N | Succ. | PT (s) | ET (s) | failures |
|---|---|---|---|---|---|
| SL-Push (sim) | 3 | 4/5 (80%) | 61.7 | 196.7 | 1 plan_fail |
| SL-Push (sim) | 4 | 0/5 (0%) | — | — | 5 plan_fail |
| DFS-WCCG | 3 | 3/5 (60%) | 164.6 | 199.8 | 2 timeout |
| DFS-WCCG | 4 | 4/5 (80%) | 131.0 | 190.9 | 1 plan_fail |

---

## 5. Deliverables

Write to `data/robot_scaling_baselines_postfix/`:

1. **`raw_results_all.csv`** — same schema as `data/robot_scaling_modefix/raw_results_all.csv` (must include: `suite_name, experiment, policy, policy_variant, policy_label, x_name, x_value, seed, scale_mode, trial_timeout_sec, max_control_steps, obstacle_count, world_width, world_height, min_mass, max_mass, robot_num, status, reason, success, control_steps, wall_clock_sec, planning_time, exec_time, total_expanded, total_visited, total_sims, mode_generation_time, mode_generation_calls, planning_iterations, global_replans, local_replans, replans_total, push_tasks_executed`).
2. **`summary.csv`** and a **`paper_summary.csv`** with one row per `(policy, robot_num)`:
   - `n_trials, n_success, success_rate, success_ci95_low/high` (Wilson);
   - `planning_time_mean_success_s ± std`, `exec_time_mean_success_s ± std` (over successful trials, `ddof=1`);
   - `pushes_mean_success`, `replans_mean_all`, `total_sims_mean_success`;
   - `failure_reasons` breakdown (counts of `task_done / plan_fail / timeout / error / other`).
3. **`resolved_config.json`** actually used, plus the **git commit hash** of the experiment repo.
4. **`README.md` digest** (mirroring `data/baselines_paper_ready/baseline_supplement_readme.md`), stating:
   - seeds and n per cell; same-scene/same-protocol confirmation vs `data/robot_scaling_modefix`;
   - the code commit and an explicit statement that the baselines now inherit the shared mode-generation refinements;
   - **diagnostics:** from the trial logs, how often the release/backtracking path triggered for each `(policy, robot_num)` (grep the logs for the release / subset-mode / backtracking messages). This is what tells us whether the fix is PushAround-specific or shared. If the path is not logged, say so explicitly.

---

## 6. Acceptance criteria / interpretation

- [ ] Same scene, same seeds, same budgets as the PushAround post-fix run; only `policies` differ.
- [ ] Ran with post-fix code (commit ≥ `fc857a8`), verified no flag disables the shared mode-gen improvements.
- [ ] 10 seeds per `(policy, N)` cell (or 5 if compute-limited — state it).
- [ ] Summary reports success + Wilson CI + PT/ET mean±std + failure reasons.
- [ ] Diagnostics on whether the release/backtracking path triggered for the baselines.

**Two outcomes, both acceptable — report either honestly:**

- **(a) Baselines improve** (e.g. SL-Push N=4 > 0%, DFS N=4 > 80%): the improvement is partly shared; the paper's baseline sentence must be updated, and PushAround's advantage is then carried mainly by success-at-lower-cost (100% at ≈29 s PT vs DFS ≈131–165 s).
- **(b) Baselines barely change**: the improvement is effectively PushAround-specific; keep the current narrative and cite the re-run as evidence of a fair comparison.

Either way the re-run must be reported as the source of the robot-scaling baseline numbers, replacing the pre-fix cells.

---

## 7. What the paper currently claims (so you know the stake)

`ral_tex/contents/experiment.tex`, Scalability section, item **(2) Robot-team size**:

> "...This local fallback, which leaves global planning unchanged, raised $N{=}4$ from $70\%$ to $100\%$. Both baselines degrade with team size: SL-Push (sim) reaches $80\%$ at $N{=}3$ but fails to plan on every $N{=}4$ run, while DFS-WCCG reaches $60\%$/$80\%$ with $131$–$165$\,s of planning versus $24$–$30$\,s for PushAround."

and the `tab:generalization` **Robot-team size** group:

```
N=3 & 10 & 100 & 30.0±12.7 & 97.3±42.1
N=4 & 10 & 100 & 29.2±8.9  & 110.1±33.1
```

The baseline sentences in item (2) will be rewritten from your results; the PushAround rows in the table will not change. If you also report baselines as table rows (optional), give me the numbers in the same column format (`Trials, Succ.(%), PT±std, ET±std`).

---

## 8. Reference paths

**In this repo (paper repo):**
- `data/robot_scaling_modefix/resolved_config.json` — **the template to copy**
- `data/robot_scaling_modefix/raw_results_all.csv` — PushAround post-fix results (schema reference)
- `data/robot_scaling/resolved_config.json` — pre-fix config (proves the byte-identical configs)
- `data/density_scaling/resolved_config.json` — source of the canonical `slpush` / `dfs` policy blocks
- `data/baselines_paper_ready/baseline_supplement_readme.md` + `baseline_supplement_data.json` — current (pre-fix, n=5) baseline digest
- `data/baselines_paper_ready/baseline_supplement_data.json` → `robot_scaling.cells.{slpush_5seeds, dfs_5seeds}` — the numbers to replace

**In the experiment repo (from the digest's provenance notes):**
- `outputs/revision/robot_scaling_modefix/raw_results_all.csv` (post-fix, ours)
- `outputs/revision/robot_scaling_baselines/{raw_results_all,summary}.csv, NOTES.md` (pre-fix baselines)
- `outputs/revision/modefix_eval.json` (pre/post comparison)
- commit `fc857a8` = mode-generation fix
