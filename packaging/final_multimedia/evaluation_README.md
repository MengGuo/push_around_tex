# Evaluation records accompanying the final manuscript

The numerical records and plotting scripts are retained from the reviewed
second-submission attachment. The final response contains no new experiments
or figures. References to “response figures” in these scripts mean the earlier
second-submission response.

| Final manuscript result | Records |
|---|---|
| Table I, WCCG validation | `wccg_cpp_paper_300/paper_summary.csv`, `raw_results.csv`, `resolved_config.json` |
| Table III density results; Fig. 10 density curves | `density_scaling/summary_scaling_suite.csv`, `raw_results_all.csv`, `trial_plan.csv`, `resolved_config.json` |
| Table III robot-team results | `robot_scaling_modefix/raw_results_all.csv`; `robot_scaling_baselines_postfix/paper_summary.csv`, `raw_results_all.csv`, and configurations |
| Table III mismatch results | `physics_mismatch/summary.csv`, `raw_results.csv`; `baselines_paper_ready/baseline_supplement_data.json` |
| Mode-generation diagnostics from the previous response | `robot_scaling_baselines_postfix/diagnostics.csv` |

`robot_scaling/` contains the earlier, superseded pre-fix records for reference;
use `robot_scaling_modefix/` for the reported PushAround team-size results.
The separate early Table II comparison/ablation suite and the hardware study
are not supplied as per-trial records. These files are not the complete planner.

Table timing averages use successful trials unless otherwise specified.
The Fig. 10 scalability timing curves cap unsuccessful trials at their budgets.
For the mismatch comparison in Sec. IV-A6, the reported 31.5, 229.1 and 18.4 s
planning times average condition-wise successful-trial means over the eight
plus/minus 40% conditions, omitting conditions without a success.

From the extracted attachment directory:

```
python evaluation_data/make_figures.py
python evaluation_data/plot_density_scaling_paper.py
```

The first script regenerates plots of the **second-submission** response;
the second regenerates the paper's Fig. 10. Both write to
`evaluation_data/figures/` and require numpy, pandas and matplotlib.
