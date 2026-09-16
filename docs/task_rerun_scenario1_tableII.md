# Task: re-run the Scenario-1 comparison so that Table II of the RA-L paper is backed by per-trial records

> **STATUS: SUPERSEDED — do not execute unless asked.** The authors decided not to re-run the Scenario-1
> baselines (the surrounding parameters and methods have drifted since that table was produced, so the
> original numbers are not recoverable without disproportionate effort, and no reviewer asked about the
> entry). Table II keeps its `>100.0` / `>500` entries, and the table footnote now defines them explicitly
> as lower bounds on a search time that is not comparable with the other baselines — no budget overrun is
> claimed, so the row no longer contradicts the shared 800 s planning cap.
> This document is retained only as (a) the record of why the entries are untraceable and (b) the exact
> procedure, should a re-run ever become necessary.

**Deliverable owner:** code agent. **Do not edit any manuscript/response LaTeX** — your output is data + a short report; a separate pass updates the paper.

---

## 1. Why this task exists (verified evidence, do not re-litigate)

The paper's Table II (`ral_tex/contents/experiment.tex`, the row `DFS-WCCG`) currently reports:

```latex
DFS-WCCG & 25.0 & $>$100.0 & 51.2 & $>$500 & 8.0 \\
%           Succ.(%)   PT (s)  ET (s)  #Sims  #Pushes
```

with the footnote `DFS-WCCG exceeds the planning budget (PT lower bound)`.

Problems established by reading the code and the repo history:

* There is **no 100 s planning limit and no 500-simulation limit anywhere in the codebase**. The only planning budget is the shared `planning_timeout_sec = 800.0`
  (`src/config/policy_config/base_policy_config.py:21`), which the DFS baseline itself reads
  (`src/policy/dfs_policy/depthfirstsearch_policy.py:106`, `:167`, timeout return at `:221`).
  The Scenario-1 suite config also uses 800 s: `src/evaluate/revision/configs/scenario_main.json:48` (`trial_timeout_sec: 800`) and `:148` (`planning_timeout_sec: 800`), with **no per-policy override for `dfs`**.
* `100.0` / `500.0` appear in the repo only as **paper reference values copied into a reporting script**:
  `src/evaluate/revision/make_scenario_main_report.py:36` (under the comment at `:28`, "Paper reference values ... Table II").
* The same script states that the Scenario-1 baselines were **never re-run** (`:387`: "Baselines were not run for this delivery ... this CSV contains `policy = ours` rows only") and that **no per-trial record of Table II ever existed** (`:241-245`: "`data/scenario_main/` did not exist, no suite runner covered these scenarios").
* `packaging/multimedia/evaluation_data/README.md:27-30` confirms: "The Scenario-1 comparison and ablation study (Table II of the paper) was produced by a separate experiment suite; its per-trial records are not part of this package".
* Git history shows the cell was **hand-edited in a commit that touched no data file**: `41.77` → `41.8` → (`3b2be45`, "final version", .tex only) `>100.0` / `>500` / `8.0`.
* Counter-evidence that the `>` bounds are not budget-derived: recorded DFS-WCCG trials run far past both thresholds inside the 800 s budget
  (e.g. `data/robot_scaling_baselines_postfix/raw_results_all.csv`: `PT = 602.31 s`, `sims = 2528`).

**Therefore:** the baseline columns of Table II cannot be traced to any measurement, and they contradict the manuscript's own "same 800 s planning cap" sentence (`ral_tex/contents/experiment.tex:122`). The goal of this task is to produce the missing records so those cells can be replaced with measured means.

## 2. Scope

**In scope (re-run):** the Scenario-1 main comparison of Table II — Scenario 1 only, 40 seeds, all compared policies.

**Out of scope (do not touch):** the density-scaling, physics-mismatch, robot-team-scaling and WCCG-validation studies. Their per-trial records already exist under `data/` and are correct. Do not change any algorithm parameter, do not tune anything, do not add experiments beyond the Scenario-1 comparison.

## 3. What to run

Use the **archived suite configuration** so that the run matches the protocol the manuscript claims. Do not invent new flags or overrides; the config file is the source of truth:

* suite config: `src/evaluate/revision/configs/scenario_main.json`
  * scenario 1 = `src/env/scenarios/scenario_8x5_complex_2rob`, `M = 10`, `N = 2`, 40 seeds
  * `trial_timeout_sec = 800`, `planning_timeout_sec = 800`, `max_control_steps = 20000` (= 500 s at the 1/40 s control period), `num_parallel_workers = 8`
  * the four policies are declared there, including the DFS baseline (`"name": "dfs"`, `"base_policy": "dfs"`, `"label": "DFS-WCCG"`)
* runner: `python -m src.evaluate.revision.run_scenario_main`
* report/ingest script: `python -m src.evaluate.revision.make_scenario_main_report --suite-dir <outputs> --dest data/scenario_main`

The runner already defaults to that config (`run_scenario_main.py:99`, `--config` default `src/evaluate/revision/configs/scenario_main.json`). Suggested sequence:

```bash
# 1. sanity: print the trial plan and the effective per-policy parameters
python -m src.evaluate.revision.run_scenario_main --dry-run --print-policy-params

# 2. run the Scenario-1 comparison (config supplies scenario, seeds, caps, workers)
python -m src.evaluate.revision.run_scenario_main \
    --scenarios scenario1 --seeds 0:40 \
    --output-dir outputs/revision/scenario_main

# 3. archive the per-trial records next to the other families
python -m src.evaluate.revision.make_scenario_main_report \
    --suite-dir outputs/revision/scenario_main --dest data/scenario_main
```

Notes on flags that exist but must **not** be used to steer this run:
`--use-mode-table` / `--no-mode-table` (the config decides the mode-generation path), `--timeout`, `--max-control-steps` and `--workers` (only if the config is genuinely unusable — if you must pass them, pass the values from §3 and say so).
`--print-policy-params` is the quickest way to *prove* the effective caps (800 s, 20 000 steps, 8 workers) in your report.

If the runner cannot consume the config at all, reproduce **exactly** the values listed above (scenario, 40 seeds, M=10, N=2, 800 s planning cap, 20 000 control steps, 8 workers) and say so explicitly in the report.

**Run PushAround as well, in the same invocation/suite**, so that every row of Table II comes from one harness, one config and one machine session. If PushAround's new numbers differ from the published ones (`97.5 % / 10.3 s / 28.6 s / 121.5 sims / 6.0 pushes`), report both side by side — do **not** silently prefer either.

## 4. Protocol rules the aggregation must follow (they are stated in the paper)

1. Planning and execution times are **means over successful trials only**; unsuccessful trials count only in the success rate.
2. Report `n_trials`, `n_success`, `success_rate`, and the number of trials that ended by the **planning timeout**, by the **execution control-step cap**, and by **plan failure** (separately).
3. `#Sims` counts **all** simulations, including mode generation.
4. Report means **with standard deviations** for PT / ET / #Sims / #Pushes.
5. If any trial hits the 800 s planning cap, say so explicitly and give the count — do **not** report a `>x` lower bound as a substitute for a measurement.

## 5. Required output

1. **Per-trial records**, archived and version-controllable:
   * `data/scenario_main/raw_results.csv` (one row per trial; this is what makes the table traceable)
   * `data/scenario_main/resolved_config.json` (the effective config actually used)
   * `data/scenario_main/README.md` documenting the exact command, machine, worker count, caps and the comparison against the published Table II values (the report script already produces this — keep it factual)
2. **A summary block ready to paste into the paper** (see §6), with one line per policy, values taken directly from the CSV.
3. **A short report in your reply** containing:
   * the exact command(s) you ran;
   * the file paths of the CSV/logs;
   * whether the run reproduced the published PushAround row, and by how much it differs if not;
   * the timeout/failure composition per policy;
   * anything that stopped you (missing module, missing scenario, GUI dependency, etc.).

## 6. Exact cells that will be updated (for reference only — do not edit LaTeX)

`ral_tex/contents/experiment.tex`, Table II, columns `Succ.(%) | PT (s) | ET (s) | #Sims | #Pushes`:

| Policy | Succ.(%) | PT (s) | ET (s) | #Sims | #Pushes |
|---|---|---|---|---|---|
| PushAround | 97.5 | 10.3 | 28.6 | 121.5 | 6.0 |
| SL-Push (offline) | 62.5 | 0.06 | 44.1 | 0.0 | 7.3 |
| SL-Push (sim) | 75.0 | 18.2 | 64.6 | 20.0 | 10.2 |
| **DFS-WCCG** | **25.0** | **>100.0** | **51.2** | **>500** | **8.0** |
| Rec-NAMO | 37.5 | 13.3 | 42.4 | 0.0 | 7.8 |

Your run should give the measured values for the four baseline rows (and for PushAround, as a cross-check). Note that **the success rates of the baseline rows are as untraceable as the DFS-WCCG row** — all four baseline rows come from the same legacy lineage — so run all of them.

Then the manuscript footnote will become (again, for your information only):

```latex
\item[a] Times are averaged over successful trials; failures count in the
success rate only. All methods share the same $800$\,s planning cap; DFS-WCCG
solved $10$ of the $40$ trials, and its row reports means over those $10$
successful trials. \#Sims counts all simulations, including mode generation.
```

## 7. Acceptance criteria

* Every number in Table II's baseline rows is traceable to a row in `data/scenario_main/raw_results.csv`, and the same CSV + config + README are committed to the repository.
* No `>x` lower bounds appear anywhere unless a genuine timeout occurred, in which case the timeout count and the cap value are stated explicitly.
* The scenario, seed count, caps and worker count used match the values in §3, and the report says so explicitly.
* Nothing outside the Scenario-1 comparison is re-run, retuned or modified.
