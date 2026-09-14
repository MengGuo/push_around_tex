# Evaluation data: which file backs which number

This folder contains the per-trial records and resolved configuration files of
the experiments reported in the revised manuscript and in the author response
and diff file. Every table and figure of the response letter is computed from
these files by `make_figures.py`.

## Matching table

| Element of the paper / response | File(s) |
|---|---|
| **Table I** (WCCG connectivity validation: agreement, FP/FN, timings) | `wccg_cpp_paper_300/paper_summary.csv`, `raw_results.csv`, `resolved_config.json` |
| **Table III**, obstacle-density group; **Fig. 9** of the paper; density table and Fig. 1 of the response | `density_scaling/summary_scaling_suite.csv` (aggregates), `raw_results_all.csv` (per trial), `trial_plan.csv` (seeds/instances), `resolved_config.json` |
| **Table III**, robot-team group (all three policies); robot table and Fig. 3 of the response | `robot_scaling_modefix/raw_results_all.csv` (PushAround, current code), `robot_scaling/raw_results_all.csv` (PushAround, pre-fix reference), `robot_scaling_baselines_postfix/paper_summary.csv` and `raw_results_all.csv` (baselines, current code), the corresponding `resolved_config.json` files |
| Mode-generation rescue-path counts quoted in the response (failed greedy replacements, backtracking assignments, per-task robot releases) | `robot_scaling_baselines_postfix/diagnostics.csv` |
| **Table III**, physics-mismatch group; mismatch table and Fig. 2 of the response | `physics_mismatch/summary.csv` (aggregates, 10 seeds), `physics_mismatch/raw_results.csv` (per trial), `baselines_paper_ready/baseline_supplement_data.json` (baseline and PushAround cells with Wilson intervals), `baselines_paper_ready/baseline_supplement_readme.md` |
| Wilson confidence intervals and the reliability figure (Fig. 5 of the response) | recomputed from the `n_success` / `n_trials` columns of the files above |
| Protocol, timeout, control-step budget and parallel-worker count of every study | the `resolved_config.json` of each study |

## Notes

* Column names are self-describing: `success`, `status`, `reason`,
  `planning_time`, `exec_time`, `replans_total`, `push_tasks_executed`,
  `total_sims`, `control_steps`. Planning-time statistics in the paper cap
  unsuccessful trials at the per-trial timeout (`trial_timeout_sec`, 800 s).
* Only relative output paths were used by the evaluation environment, so these
  records contain no host, account or author information.
* The Scenario-1 comparison and ablation study (Table II of the paper) was
  produced by a separate experiment suite; its per-trial records are not part of
  this package, and its aggregate results are the ones listed in Table II of the
  paper. All other tables and figures are fully backed by the files above.
* To regenerate the figures: `python evaluation_data/make_figures.py`
  reproduces every figure of the response letter, and
  `python evaluation_data/plot_density_scaling_paper.py` reproduces the
  three-panel obstacle-density figure of the paper (the latter needs the
  density records only). Both require numpy, pandas and matplotlib and write
  into `evaluation_data/figures/`.
