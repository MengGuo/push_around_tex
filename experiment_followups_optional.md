# Optional follow-up experiments (not required for correctness)

**Status of the revision.** All reviewer points are closed and every number in
the manuscript and in the response letter is traceable to `data/`. The two items
below are *optional strengthening* only — they remove caveats that are already
disclosed in the response letter, so the current submission is self-consistent
without them. Execute them only if spare compute is available.

Reference for what a completed re-run looks like: `data/robot_scaling_baselines_postfix/`
(README.md, paper_summary.csv, diagnostics.csv, resolved_config.json,
experiment_repo_commit.txt).

---

## Follow-up A — raise the physics-mismatch baselines from 5 to 10 seeds

**Why.** The mismatch baseline supplements (`SL-Push (sim)`, `DFS-WCCG`) use 5
seeds per condition while PushAround uses 10. This is the only remaining
sample-size asymmetry in the paper, and it is currently labelled
("5-seed baseline subset", "indicative") in both the manuscript and the
response. Filling it to 10 lets us delete the caveat and narrow the Wilson
intervals in `response/figures/resp_mismatch.pdf` and `resp_reliability.pdf`.

**Spec.**

- Base config: copy `data/physics_mismatch/resolved_config.json` verbatim, change
  only `suite_name` → `..._baselines_n10` and `output_dir`.
- `policies`: the two baseline blocks used everywhere else, verbatim
  (`{"base_policy":"slpush","label":"SL-Push (sim)","name":"slpush"}` and
  `{"base_policy":"dfs","label":"DFS-WCCG","name":"dfs"}`).
- `conditions`: the same 17 conditions as PushAround's run (nominal + 4 families
  × factors {0.6, 0.8, 1.2, 1.4}); the baselines were previously run only on
  nominal + the eight ±40% extremes, so at minimum extend those nine to 10
  seeds — ideally run the full 17 for a clean parallel with ours.
- Everything else unchanged: `obstacle_count = 30`, `robot_num = 2`,
  `world 8×8`, `min_mass = 20`, `max_mass = 30`, `trial_timeout_sec = 800`,
  `max_control_steps = 20000`, `num_parallel_workers = 8`, `seeds 0..9`,
  `use_mode_table = false`, `mode_gen_via_greedy_opt = true`, no physics
  perturbation of the planner (execution-side only).
- Run on the current code revision (post `fc857a8`) so that ours and the
  baselines are on the same version — this also makes the mismatch study
  version-consistent with the robot-team study.
- Cost: ≈ 90 trials (9 conditions × 2 policies × 5 extra seeds) for the
  extremes, or ≈ 250 trials (17 conditions × 2 policies × 10 seeds) for the
  full grid.

**Deliverables.** `data/physics_mismatch_baselines_n10/` with
`raw_results_all.csv`, `paper_summary.csv` (success, Wilson CI, PT/ET mean±s.d.,
pushes, replans, failure composition per condition), `resolved_config.json`,
commit hash, and a README digest.

**What I will update afterwards.** Table III's mismatch rows and the
response's mismatch table (n=5 → n=10), the aggregate rows (±40% / all), the
mismatch figure and the reliability figure, and the "Known limitations (i)"
bullet, which can then be deleted.

---

## Follow-up B — re-run density and mismatch on the post-fix code (ours + baselines)

**Why.** The density sweep and the mismatch study predate the mode-generation
refinements; the robot-team study is post-fix. Both sides of each comparison
share a code version, and the pre-fix numbers can only understate PushAround, so
the current text labels them *conservative*. Re-running removes the version
mixing entirely and lets us drop those caveats.

**Spec.** Same two suites as they stand today, only on the current code:

- Density: `data/density_scaling/resolved_config.json`, all five policies, seven
  densities, 10 seeds → 350 trials.
- Mismatch: 17 conditions, PushAround + the two baselines, 10 seeds → ≈ 420
  trials (or 250 + Follow-up A).
- Keep `use_mode_table = true` for the density suite if you want to preserve the
  existing protocol (it is the reason the density `M=30` planning time, 11.7 s,
  differs from the mismatch nominal, 16.8 s); if you instead switch the density
  suite to greedy online mode generation, state the change explicitly, because
  the two numbers will then converge.

**Cost.** ≈ 770 trials in total; this is the expensive option.

**What I will update afterwards.** Table III density and physics rows, the
paper's density figure (Fig. 9) if it is regenerated, and every "conservative /
predates the mode-generation fix" statement in the response letter (which can
then be replaced by a single sentence stating that all studies run on one code
revision).

---

## Explicitly not needed

- **WCCG validation** — already on its own harness with matching data
  (`data/wccg_cpp_paper_300/`), and the measurement scope is now stated in the
  Table I footnote.
- **Robot-team scaling** — already fully re-run on the post-fix code for all
  three policies (`data/robot_scaling_modefix/` + `data/robot_scaling_baselines_postfix/`).
- **Main Scenario-1 comparison (Table II)** — produced by a single suite run;
  both sides share the code version.
