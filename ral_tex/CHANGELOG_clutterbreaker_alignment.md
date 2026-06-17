# ClutterBreaker/source alignment update

This replacement package updates the RAL LaTeX source to match the current
`src.zip` implementation and the provided density-scaling raw data.

## Method text aligned with code

- `contents/gap.tex` now describes the current node-level exact WCCG presearch:
  embedded face-dual search, local-clearance edge costs, consecutive-gap
discount, weak goal-distance queue heuristic, endpoint-clearance proxy, and
single-best first-gap selection.
- `contents/push.tex` now matches task sampling in `task_sampler.py` and
`local_clearance.py`: robust-min dual-side opening, no fixed side-displacement
ratio, route-aware root-direction grid over jitter angles and angular velocity,
global scoring/deduplication, mode-generation by greedy contact replacement and
ModeTable cache reuse, and the transition/pushing controller logic.
- `contents/simloop.tex` now removes the non-implemented accumulated execution
cost from the queue key. The node value is the normalized presearch cost-to-go
minus accumulated push effect, where push effect combines snapshot obstacle
motion and target-gap breakthrough/widening reward. The algorithm now shows the
lazy root-only / recursive-only expansion logic.
- `contents/experiment.tex` now states the implemented expansion budget of 16
validated children and the exact-presearch/single-best-gap sampling behavior.

## Density-scaling update

- `data/raw_results_all.csv` is included as the raw input.
- `scripts/plot_density_scaling.py` reproduces the source plotting convention:
  every unsuccessful trial is replaced by its `trial_timeout_sec` cap before
  computing planning-time statistics.
- `figures/density_scaling_curve.pdf/png` now contains all baselines from the
  provided raw data: Ours, Ours w/o recursive, SLPush, DFS, and Recursive.
- `data/density_scaling_summary.csv` is regenerated from the raw CSV.
- The script contains a single `KEEP_COUNTS` option so that a density such as
  `N=30` can be removed later without rewriting the plotting logic.

## Compilation

- The revised source compiles to 8 pages.
- Duplicate/undefined label warnings were checked after repeated `pdflatex` runs;
  only the missing-author warning remains from the template.
