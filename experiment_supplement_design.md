# 补充实验设计：physics mismatch 与 robot scaling 的 baseline 对照

> 目的：现有 physics-mismatch 和 robot-scaling 两组实验只有 PushAround，属于"自证鲁棒/自证扩展"。
> 本设计各加 1–2 个 baseline，把 claim 从"我们稳 / 我们 scale"升级为"我们比 baseline 更稳 / 更 scale"。
> 纯仿真、可复用现成 suite 基础设施，工作量小。

---

## 0. 通用设置（与既有实验完全一致，保证公平）

- **工作区**：`world_width = world_height = 8.0` (m)，$M=30$ 个 movable，质量 `min_mass=20, max_mass=30` (kg)。
- **预算**：`trial_timeout_sec = 800`，`max_control_steps = 20000`；失败/超时 trial 在规划时间统计中按 `800 s` 封顶计入。
- **判据 / 模拟器**：与既有实验一致的 `W-clear 目标判据`、同一 execution simulator、同一 collision / reachability check。
- **seed**：`seeds = [0..9]`，每条件 10 次。
- **baseline policy 定义**：**直接复用 density suite 里已有的 `dfs` / `slpush` / `recursive` 配置**（`data/density_scaling/resolved_config.json` 的 `policies` 列表），不要重新手改，保证与主对比一致。
- **统计口径**：成功率 + Wilson 95% CI；PT / ET / #replans / #pushes 报 `mean±std`（mean 仅基于成功 trial）；结果写 `raw_results.csv` + 汇总表，字段与现有 suite 兼容（`status, reason, success, planning_time, exec_time, replans_total, push_tasks_executed, ...`）。

---

## A. Physics mismatch 加 baseline

**目标**：证明 PushAround 的"名义规划 + 执行侧失配 + 在线 replanning"比 baseline 更稳。

- **条件**：与现有 physics-mismatch 完全一致（`data/physics_mismatch/resolved_config.json` 的 `conditions`）。
  即 `nominal` + 四个 family（`mass / lateral_friction / spinning_friction / robot_force_limit`）× factor `{0.6, 0.8, 1.2, 1.4}`（= ±20% / ±40%），共 17 条件、每条件 10 seed。
- **policy 替换**：把 `ours` 换成 baseline——
  - **必做**：`SL-Push (sim)`（它是 physics-validated 路线，最公平、最能体现差异）。
  - **可选**：`DFS-WCCG`（同为 WCCG/搜索路线）。
- **执行侧扰动**：沿用这些条件里的 `execution_physics_overrides`（`obstacle_mass_scale_exec` / `obstacle_lateral_friction_scale_exec` / `obstacle_spinning_friction_scale_exec` / `robot_force_limit_scale_exec`）。**规划仍用 nominal。**
- **指标**：success rate（+ CI）、PT、ET、#replans、#pushes、失败 reason（`plan_fail` / 各类 `timeout`）。
- **呈现（接入现有 `tab:generalization` 的 Physics mismatch 组）**：
  - 加一列 `SL-Push (sim) Succ.(%)`（与 PushAround 逐行对照），或在正文 (3) 补一句：
    > 在相同的 ±20%/±40% 执行侧失配下，SL-Push (sim) 成功率降至 X%（PushAround 97.5%）——因为 PushAround 通过在线 replanning 吸收失配，而 baseline 无失配感知的重规划。
- **注意**：请标注 baseline 是否有在线 replanning（若无，请在报告中说明，这本身就是结论的一部分：失配感知的 replanning 是差异来源）。

---

## B. Robot scaling 加 baseline

**目标**：判断 N=4 的下降是 PushAround 特有缺陷，还是"多机转移 / 协调"这一通用瓶颈。

- **条件**：`M = 30`（nominal，不扰动物理），`robot_num ∈ {3, 4}`（可选加 `2` 作公平基数）。与现有 robot-scaling 一致。
- **policy 替换**：把 `ours` 换成 baseline——
  - **优先**：`SL-Push (sim)` 或 `DFS-WCCG`（能支持团队）。
  - **注意**：若某 baseline 本身是单机器人（如 `Rec-NAMO` 这类 NAMO），**不强行扩展**，记录"该 baseline 不支持 $N>2$"即可；优先报告支持团队的 baseline。
- **指标**：success（+ CI）、PT、ET、#pushes、#replans、失败 reason。
- **呈现（接入现有 `tab:generalization` 的 Robot-team size 组）**：
  - 给 baseline 在 `N=3 / N=4` 的成功率对照；正文 (2) 补一句：
    > 在 $N=4$ 下 baseline 同样出现成功率下降，说明该下降源于拥挤环境中的多机转移/协调（非完备多机路径规划器），而非 PushAround 特有。
- **预期**：若 baseline 也在 $N=4$ 下降，则强化你的归因（瓶颈在外层 transition planning 的协调成本，而非 PIHS 搜索）。

---

## C. 集成到 `ral_tex/contents/experiment.tex`

1. `tab:generalization` 的 `Physics mismatch` 组与 `Robot-team size` 组各加 baseline 行/列。
2. 正文 (2)、(3) 各补一句 baseline 对照结论。
3. **新增内容一律包 `\change{...}` 标蓝**（新增表/列跨度的 caption 也要标蓝）。
4. **保持 8 页**：若加内容后超页，从其它冗余文字/注释块压缩，**不要**把图片缩到 <0.80 宽。

---

## D. 验收清单

- [ ] 每条件 10 seed（0–9）、预算 800 s / 20000 步。
- [ ] baseline 与 PushAround 使用同一 workspace、M、mass、判据、simulator、reachability、timeout、成功判据。
- [ ] 输出 `raw_results.csv` + 汇总表，字段与现有 suite 兼容（`success, planning_time, exec_time, replans_total, push_tasks_executed, status, reason`）。
- [ ] 给出 success 的 Wilson 95% CI 与 mean±std。
- [ ] 报告 baseline 是否支持 $N>2$、是否有在线 replanning（这两点会影响结论表述，需如实说明）。
- [ ] 回填进 `experiment.tex` 后仍为 8 页、编译无错误/无 Overfull/无未定义引用。

---

## 参考文件（复用现成配置，减少工作量）

- `data/physics_mismatch/resolved_config.json` —— mismatch 的 17 条件与执行侧扰动定义。
- `data/density_scaling/resolved_config.json` —— 里面 `policies` 列表的 `dfs / slpush / recursive` 定义（baseline 直接照搬）。
- `data/robot_scaling/resolved_config.json` —— robot scaling 的 `robot_nums` 与 M=30 设置。
- `data/density_scaling/summary_scaling_suite.csv` / `data/density_scaling/raw_results_all.csv` —— 汇总/原始结果字段格式参照。
