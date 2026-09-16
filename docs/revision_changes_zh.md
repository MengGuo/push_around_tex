# PushAround 返修：正文改动一览（中文核验版）

> 列出本次返修在正文中**实际生效**的全部 39 处蓝色改动。每条含：文件/小节、`ral_tex/root.pdf`（8 页）中的页码、当前原文与中文翻译。

## 汇总

| 文件 | 处数 |
|---|---|
| `abstract.tex` | 1 |
| `introduction.tex` | 2 |
| `problem.tex` | 4 |
| `gap.tex` | 1 |
| `wccg.tex` | 3 |
| `push.tex` | 5 |
| `simloop.tex` | 4 |
| `overall.tex` | 3 |
| `experiment.tex` | 15 |
| `conclusion.tex` | 1 |


## abstract.tex

### [1] abstract.tex

- **页码**：p1
- **新增原文**：

  > Extensive simulations and hardware experiments validate WCCG against standard connectivity checks and show that PushAround scales to denser clutter and larger teams while remaining robust under simulated execution-side physical-parameter mismatch.

- **中文翻译**：大量仿真与实物实验验证了 WCCG 与标准连通检查的一致性，并表明 PushAround 能扩展到更密的障碍场与更大的机器人团队，同时对物理参数失配保持鲁棒。


## introduction.tex

### [2] introduction.tex

- **页码**：p1
- **新增原文**：

  > These methods nonetheless assume a prescribed target or few objects, and physical realizability is often not validated before execution. Corridor clearing differs: many movable obstacles must be rearranged, and the result must admit a larger vehicle.

- **中文翻译**：但这些方法都假设操作目标是给定的、可动物体很少，且物理可实现性通常在执行前并未被显式验证。清障问题在两点上不同：需要在清障过程中重新布置许多可动物体，且最终构型必须能让更大的车辆通行。

### [3] introduction.tex

- **页码**：p2
- **新增原文**：

  > it demonstrates significant improvements in feasibility, efficiency, and scalability over existing NAMO and collaborative clearing methods, together with robustness to execution-side physical-parameter mismatch.

- **中文翻译**：并证明其在可行性、效率与扩展性上相对现有 NAMO 与协同清障方法有显著提升，同时具备对执行侧物理参数失配的鲁棒性。


## problem.tex

### [4] problem.tex

- **页码**：（见对应小节）
- **新增原文**：

  > an inactive robot carries a null contact $c_i=\varnothing$ with zero force (Sec.~\ref{subsec:push}).

- **中文翻译**：某个机器人可以在某次推挤任务中处于非激活状态：它在 c_m 中用空接触 c_i=∅ 表示，对应力固定为零（见 Sec. III-C）。

### [5] problem.tex

- **页码**：p2
- **新增原文**：

  > The force vector~$\mathbf{u}_m$ serves as a feasibility variable to certify wrench generation under the modeled contact and actuation constraints rather than a directly commanded control input.

- **中文翻译**：力向量 u_m 是用于证明在已建模的接触与驱动约束下能产生所需力旋量的可行性变量，而不是直接下发的控制输入。

### [6] problem.tex

- **页码**：p3
- **新增原文**：

  > where~$T\triangleq\sum_{k=1}^{K}\Delta t_k$ denotes the robotic clearance duration excluding subsequent vehicle traversal, with $\Delta t_k>0$ the duration that the rollout in~(13) returns for the $k$-th push, and~$J(\cdot)$ is the simulation-estimated manipulation cost. Vehicle traversal is considered only through the terminal $W$-clearance condition~\eqref{eq:wclear}. The constraints~\eqref{eq:freespace}--\eqref{eq:transition} enforce valid pushing transitions. Equation~\eqref{eq:problem} defines the realized clearance cost; PIHS samples finitely and does not guarantee global optimality.

- **中文翻译**：其中 T ≜ ΣΔt_k 为机器人清障时长（不含后续车辆通行），Δt_k>0 是 rollout (13) 为第 k 次推挤返回的时长。

### [7] problem.tex

- **页码**：p3
- **新增原文**：

  > The objective couples obstacle selection, pushing-mode generation and switching into one hybrid planning problem, yielding a combinatorial-continuous search space richer than classical NAMO formulations with hand-crafted contact modes~\cite{goyal1989limit,chen2015occlusion,wang2006multi}.

- **中文翻译**：该目标把障碍选择、推挤模式生成与切换耦合为一个混合规划问题，形成比传统（接触模式人为给定）NAMO 表述更丰富的“组合—连续”搜索空间。


## gap.tex

### [8] gap.tex

- **页码**：p4
- **新增原文**：

  > \textbf{Direct} pushing moves a gap-side blocker along a gap-opening direction, whereas \textbf{recursive} pushing first clears movable blockers in the swept region and then returns to the root gap-opening task.

- **中文翻译**：**直接**推挤使 gap 一侧的阻挡物沿开缝方向移动；**递归**推挤先清除扫掠区域内的可动阻挡物，再回到根任务。


## wccg.tex

### [9] wccg.tex

- **页码**：p3
- **新增原文**：

  > Grid- and sampling-based clearance checks typically depend on a chosen grid or sampling resolution and must update their queries when obstacles move~\cite{karaman2011samplingbasedalgorithmsoptimalmotion}. Built from obstacle geometry, the WCCG needs no grid-resolution parameter in these repeated queries.

- **中文翻译**：基于栅格与采样的 clearance 检查通常依赖所选栅格/采样分辨率，并在障碍移动后需要更新查询；WCCG 直接由障碍几何构建，在这些反复查询中不引入栅格分辨率参数。

### [10] wccg.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Core components of the physics-informed hybrid search: WCCG construction, gap ranking, mode generation, and physics validation.

- **中文翻译**：物理信息混合搜索的核心组件：WCCG 构建、gap 排序、模式生成与物理验证。

### [11] wccg.tex

- **页码**：p3
- **新增原文**：

  > where the faces follow the standard configuration-space inflation interpretation: expanding obstacles by a disk of radius $W/2$ turns gaps narrower than $W$ into overlapping barriers, and non-convex obstacles are decomposed into clearance-relevant components, after which WCCG records the separating bottlenecks.

- **中文翻译**：其中各面遵循标准构型空间膨胀解释：把障碍按半径 W/2 膨胀会把窄于 W 的缝隙变成相互重叠的屏障；非凸障碍被分解为与 clearance 相关的分量，随后 WCCG 记录分隔瓶颈。


## push.tex

### [12] push.tex

- **页码**：p4
- **新增原文**：

  > The wrench feasibility encoded in~$\boldsymbol{\xi}$ acts as a screening condition rather than a force setpoint: it certifies that the chosen contact configuration can realize the required object motion within the robots' actuation limits, after which the candidate is passed to the physics rollout for validation.

- **中文翻译**：ξ 中编码的力旋量可行性是筛选条件而非力设定点：它证明所选接触构型能在驱动极限内实现所需物体运动，随后候选交给物理 rollout 验证。

### [13] push.tex

- **页码**：p4
- **新增原文**：

  > If the sequential replacement cannot assign a contact to every robot, a bounded backtracking search over robot--contact combinations (with a fixed budget) attempts the full-team assignment. If no feasible full-team mode is found within this budget --- for instance on small faces or under the pairwise pusher-clearance constraint --- one robot is temporarily left inactive and the assignment is repeated with the remaining team. Reduced-team modes carry a ranking penalty, so a feasible full-team mode is preferred, and the inactive robot returns for the next task.

- **中文翻译**：若顺序替换无法为每个机器人都分配到接触点，则先用固定预算的有界回溯搜索尝试全队指派；若在该预算内找不到可行的全队模式（例如可推面很小、或成对推挤间距约束不允许），则令一个机器人暂时不参与，并用其余机器人重复该指派。减队模式带排序惩罚，因此优先全队模式；被停用的机器人在下一次任务中恢复。

### [14] push.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Reachable contacts are filtered by the desired object twist, assigned to robots, refined by local replacement, and finally validated by simulation.

- **中文翻译**：可达接触先按期望的物体旋量筛选，再指派给机器人、经局部替换精化，最后用仿真验证。

### [15] push.tex

- **页码**：p5
- **新增原文**：

  > The rollout jointly simulates all robots and movable bodies, thereby capturing contact-induced object interactions.

- **中文翻译**：该 rollout 同时仿真所有机器人与可动物体，从而捕捉接触引发的物体间相互作用。

### [16] push.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Sampled push tasks are evaluated via parallel simulation, producing updated states for search expansion.

- **中文翻译**：采样得到的推挤任务通过并行仿真评估，为搜索扩展产生更新后的状态。


## simloop.tex

### [17] simloop.tex

- **页码**：（见对应小节）
- **新增原文**：

  > The search samples a finite candidate set, so neither global optimality nor completeness is guaranteed.

- **中文翻译**：搜索在有限候选集上采样，因此不保证全局最优性与完备性。

### [18] simloop.tex

- **页码**：（见对应小节）
- **新增原文**：

  > The remaining-cost term is a heuristic and is not required to be admissible. The score prioritizes nodes by realized cost and promising future actions, but it does not provide an A* optimality guarantee.

- **中文翻译**：剩余代价项是启发式，不要求可采纳；该评分按已实现代价与有前景的后续动作对节点排序，但不提供 A* 最优性保证。

### [19] simloop.tex

- **页码**：p6
- **新增原文**：

  > Execution and planning alignment in Scenario 1 (\textbf{Left}) and Scenario 2 (\textbf{Right}). \textbf{Top:} simulated snapshots during path clearing. \textbf{Bottom:} corresponding WCCG overlays with the start face in blue. The executed pushes progressively expand the reachable $W$--clearance region until the goal is connected.

- **中文翻译**：Scenario 1（左）与 Scenario 2（右）的执行与规划对齐。上：清障过程仿真快照；下：对应的 WCCG 叠加，起始面为蓝色。已执行的推挤逐步扩大可达的 W-clearance 区域，直到目标连通。

### [20] simloop.tex

- **页码**：p5
- **新增原文**：

  > Thus, the schedule~$\pi$ stored in~$\nu$ is a physics-validated solution under the nominal planning model: it satisfies the terminal clearance condition and the validated pushing transitions, and encodes both the gaps to clear and the strategies that realize them, without implying that~$\mathcal{J}_{\mathrm{clr}}(\pi)$ is globally minimal. The objective covers the clearing phase only, since the vehicle traverses the corridor after clearing completes.

- **中文翻译**：因此 ν 中保存的调度 π 是**名义规划模型下**的物理验证解：满足末端 clearance 条件与已验证的推挤转移，编码了需要清除的 gap 序列及其实施策略，但不意味着 J_clr(π) 全局最小。目标只覆盖清障阶段，因为外部车辆在清障完成后才通行。


## overall.tex

### [21] overall.tex

- **页码**：p5
- **新增原文**：

  > On the hardware the optimized forces certify feasibility rather than being commanded: a mode is kept only if its wrench lies within the actuation limits, and each control interval $\mathsf{EvalSim}$ predicts a short object-motion reference tracked with motion-capture feedback, so every executed push updates the execution state and the WCCG for the next task.

- **中文翻译**：在硬件上，优化得到的力用于证明可行性而非被下发：只有当力旋量落在驱动极限内才保留该模式；每个控制周期 EvalSim 预测一段短时前向物体运动参考，速度级控制器以动捕反馈跟踪，因此每次执行的推挤都会更新执行状态与 WCCG 供下一任务使用。

### [22] overall.tex

- **页码**：（见对应小节）
- **新增原文**：

  > The dominant simulation cost $\mathcal{O}\big(\sum_{g\in\mathsf{Rank}(\nu)}|\Xi_g|\,\big(C_{\mathrm{LP}}+\rho_\nu T_{\mathrm{sim}}/n_{\texttt{w}}\big)\big)$ grows with the number of validated candidates and is reduced by $n_{\texttt{w}}$ parallel workers.

- **中文翻译**：主导的仿真开销 O(Σ_{g∈Rank(ν)}|Ξ_g|(C_LP + ρ_ν T_sim/n_w)) 随被验证候选数增长，并由 n_w 个并行 worker 降低。

### [23] overall.tex

- **页码**：p6
- **新增原文**：

  > Robot-team size mainly affects mode generation: the greedy stage evaluates at most $N|\mathcal{A}|$ single-contact substitutions rather than the exhaustive $|\mathcal{A}|^N$ assignment; if it fails, a bounded backtracking search with budget $B{=}2000$ is tried, then a reduced-team fallback repeats the assignment with one robot inactive. Each candidate is checked by an LP over at most $2N$ contact-force variables.

- **中文翻译**：团队规模主要影响模式生成：贪心阶段最多评估 N|A| 个单接触替换，而非穷举 |A|^N 指派；若失败，先尝试有界回溯，再用减队兜底（一个机器人不参与）重复该指派。每个候选由一个最多 2N 个自由接触力的 LP 检查，而不是逐个枚举 |A|^N 联合元组。


## experiment.tex

### [24] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > WCCG connectivity validation and mean runtime.

- **中文翻译**：WCCG 连通性验证与平均运行时间（表 I 题注）。

### [25] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > \begin{tabular}{ @{} l cc @{\hspace{8pt}} ccc @{} } \toprule & \multicolumn{2}{c}{Validation} & \multicolumn{3}{c}{Runtime (ms)} \\[-0.6ex] \cmidrule(lr){2-3} \cmidrule(lr){4-6} Type & CC $=$ FR & FP/FN$^\dagger$ & CC & FR & WCCG \\ \midrule Convex & 100/100 & 0/0 & 1.23 & 282.9 & \textbf{0.86} \\ Non-convex & 98/100 & 0/0 & 1.51 & 204.1 & \textbf{1.30} \\ Mixed & 98/100 & 0/0 & 1.33 & 242.4 & \textbf{1.05} \\ \midrule Total & 296/300 & \textbf{0/0} & 1.36 & 243.1 & \textbf{1.07} \\ \bottomrule \end{tabular}

- **中文翻译**：表 I 表体：表头为 Type | CC=FR | FP/FN† | CC | FR | WCCG，时间列改为毫秒，类别顺序统一为 凸/非凸/混合/合计。

### [26] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > $^\dagger$WCCG errors relative to the continuous configuration-space reference (CC). All runtimes use the same 300-scene harness with the compiled WCCG backend.

- **中文翻译**：† WCCG 相对连续构型空间参考（CC）的误差。所有运行时间在同一 300 场景测试框架下测得，WCCG 使用其编译后端。

### [27] experiment.tex

- **页码**：p6
- **新增原文**：

  > All methods share the robot footprints, obstacle configurations, collision and reachability checks, and execution simulator, with the same $800$\,s planning cap, $20{,}000$-step ($500$\,s) execution cap and $8$ workers. Unless stated otherwise, times average over successful trials, failures counting only in the success rate; the scalability curves instead cap failures.

- **中文翻译**：所有方法共享机器人足迹、障碍构型、碰撞与可达性检查以及执行仿真器，采用相同的 800 s 规划上限与 20 000 步（500 s）执行上限。除特别说明外，时间在成功 trial 上取平均、失败只计入成功率；可扩展性曲线例外，它把上限记给失败 trial。

### [28] experiment.tex

- **页码**：p6
- **新增原文**：

  > Over the $40$ Scenario~1 trials PushAround succeeds in $97.5\%$ of them at $10.3$\,s of planning and $28.6$\,s of execution, executing $6.0$ pushes on average (Table~\ref{tab:main_ablation}). Fig.~\ref{fig:main_result} shows two such runs: Scenario~1 ($10$ obstacles, two robots) needs a $6$-push plan ($7.4$\,s, executed in $42.3$\,s), while Scenario~2 ($14$ obstacles) needs $9$ pushes ($11.2$\,s, $61.3$\,s). Planning effort lies in validating those pushes: a solved trial spends $121.5$ simulations for $6.0$ executed pushes, and the ablations show that cached modes, quick-pass, gap lookahead and reinsertion change this validation load rather than the plan length. Execution is longer since …… *（长段落，见源码）*

- **中文翻译**：Scenario 1 的 40 次 trial 中成功率为 97.5%，平均规划 10.3 s、执行 28.6 s，平均执行 6.0 次推挤（表 II）。Fig. 7 展示两个这样的 run：Scenario 1（10 个可动物体、2 个机器人）需要 6 次推挤的计划，规划 7.4 s、执行 42.3 s；Scenario 2（14 个物体）需要 9 次推挤，规划 11.2 s、执行 61.3 s。规划开销主要在验证：一个成功 trial 为 6.0 次执行推挤付出 121.5 次仿真；消融表明缓存模式、quick-pass、gap lookahead 与 reinsertion 改变的是这一验证负载而非计划长度。执行阶段更长，因为每次推挤都要真正执行并观测后继状态，而推挤之间的重定位在规划中被抽象为几何可达性检查。

### [29] experiment.tex

- **页码**：p7
- **新增原文**：

  > \subsubsection{WCCG Connectivity Validation} \label{subsec:wccg-validation} WCCG is compared against two references on $300$ random scenes (convex, non-convex and mixed; Table~\ref{tab:wccg-validation}). The continuous reference (CC) resolves collisions geometrically after inflating boundaries by~$W/2$, with no grid discretization~\cite{lozano1983spatial}; the fine-raster reference (FR) discretizes the workspace on a $0.01$\,m occupancy grid. CC and FR disagree in $4$ of $300$ cases, all near narrow contacts and rasterization-related, whereas WCCG matches CC on all $300$ scenes without false positives or negatives. A query costs $1.07$\,ms ($0.67$\,ms query, $0.40$\,ms construction) against …… *（长段落，见源码）*

- **中文翻译**：WCCG 在 300 个随机场景上与两个参考比较：连续参考 CC 按 W/2 膨胀后以几何方式求解碰撞、不做网格离散；fine-raster 参考 FR 以 0.01 m 单元离散化同一工作空间。CC 与 FR 在 300 例中有 4 例不一致，均出现在狭窄接触附近且源于栅格化，而 WCCG 与 CC 在全部 300 场景一致、无假正例与假负例。单次查询 1.07 ms（查询 0.67 ms、构图 0.40 ms），对比 CC 的 1.36 ms 与 FR 的 243 ms，并提供 PIHS 使用的 gap 图；由于每次（仿真或实际执行的）推挤后都会重建，这一几何维护开销相对主导规划时间的物理 rollout 可以忽略。

### [30] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Scalability and robustness.

- **中文翻译**：可扩展性与鲁棒性（表 III 题注）。

### [31] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > \begin{tabular}{ @{} l c c r@{\;}c@{\;}l @{\hspace{10pt}} r@{\;}c@{\;}l @{} } \hline Case & Trials & Succ.(\%) & \multicolumn{3}{c@{\hspace{10pt}}}{$PT$ (s)} & \multicolumn{3}{c}{$ET$ (s)} \\ \hline \multicolumn{9}{l}{ \emph{Obstacle density} (PushAround, $N=2$, nominal) } \\ $M=15$ & 10 & 100 & 2.5 & $\pm$ & 0.9 & 37.1 & $\pm$ & 21.0 \\ $M=30$ & 10 & 100 & 11.7 & $\pm$ & 3.7 & 100.9 & $\pm$ & 34.7 \\ $M=45$ & 10 & 100 & 53.4 & $\pm$ & 24.5 & 272.7 & $\pm$ & 97.4 \\ \hline \multicolumn{9}{l}{ \emph{Robot-team size} ($M=30$, nominal; 10 trials per cell) } \\ PushAround, $N=3$ & 10 & 100 & 30.0 & $\pm$ & 12.7 & 97.3 & $\pm$ & 42.1 \\ PushAround, $N=4$ & 10 & 100 & 29.2 & $\pm$ & 8.9 & 110.1 & …… *（长段落，见源码）*

- **中文翻译**：表 III 表体（新表）：障碍密度块（M=15/30/45）、机器人团队块（PushAround 与两个基线在 N=3/4）、物理失配块（标称/质量/侧向摩擦/自旋摩擦/力上限/全部扰动）。

### [32] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Each perturbed row scales one parameter; the others stay nominal. Times and budget are as in Table~\ref{tab:main_ablation}.

- **中文翻译**：每个扰动行只缩放一个参数，其余保持标称；时间与预算同表 II。

### [33] experiment.tex

- **页码**：p7
- **新增原文**：

  > \subsubsection{Scalability and Robustness Analysis} \label{subsec:generalization} Generalization is further evaluated in an $8\times8$\,m workspace by scaling the obstacle density~$M$, the team size~$N$ and the execution-side physics parameters (Table~\ref{tab:generalization}, Figs.~\ref{fig:scalability_scenes} and \ref{fig:density_scaling}). \textbf{(I) Obstacle density:} with two robots and $10$ trials per density, PushAround keeps $100\%$ success at all tested densities ($M{=}15$ to $45$), planning in $2.5$--$53.4$\,s, whereas at $M{=}45$ no external method solves any trial and the no-recursion ablation solves $7/10$. \textbf{(II) Robot-team size:} at $M{=}30$, PushAround solves all ten …… *（长段落，见源码）*

- **中文翻译**：在同一 8×8 m 工作空间中进一步评估可扩展性——缩放障碍密度 M、团队规模 N 与执行侧物理参数（表 III、图 9、图 10）。(I) 障碍密度：2 机器人、每密度 10 次 trial，PushAround 在所有测试密度（M=15 到 45）保持 100% 成功率，规划 2.5–53.4 s；而 M=45 时外部方法无一成功、无递归消融成功 7/10。(II) 机器人团队规模：M=30 时，PushAround 在 N=2/3/4 均解出全部十次 trial，使用同一套模式生成流程加“全队优先”兜底——无可行全队指派时允许一个机器人临时不参与，并以排序惩罚优先全队模式；N=4 时规划 29.2 s、执行 110.1 s，DFS-WCCG 为 101.9 s 与 175.9 s。碎屑扫描中每次展开的分支数稳定在 6 附近、展开数仅温和增长（3.5→24.5），而候选空间按 |A|^N 增长；一个成功 trial 的中位数为 10 次展开、48 个访问快照、约 60 次仿真（每次约 165 ms），而生成一个模式约 22 ms。团队从 2 增到 4 时搜索结构几乎不变（中位 10 次展开、60–63 次仿真），但跨 worker 的累计模式生成时间约增至三倍（15.8→46.4 s）。(III) 物理失配：规划器保持标称模型，只逐参数扰动执行仿真器；PushAround 在 156/160 次扰动 trial 中成功（97.5%）；相同 ±40% 扰动下 SL-Push (sim) 成功 13/40、DFS-WCCG 成功 23/40，平均规划时间为 31.5 与 229.1 s，而 PushAround 为 18.4 s。

### [34] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Scalability of the clearing process. \textbf{Left:} density scaling ($M{=}45$, two robots): snapshots during clearing (\textbf{top}) and WCCG overlays with the start face in blue (\textbf{bottom}). \textbf{Right:} team scaling ($M{=}30$, four robots): initial and final states (\textbf{top}) and one push before contact and during execution (\textbf{bottom}).

- **中文翻译**：清障过程的可扩展性。左：障碍密度扩展（M=45、2 机器人）的快照（上）与起始面为蓝的 WCCG 叠加（下）。右：机器人团队扩展（M=30、4 机器人）的初始/最终状态（上）与一次推挤在接触前与执行中的放大视图（下）。

### [35] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > Obstacle-density scaling ($8\times 8$\,m, $10$ seeds per density). Times are budget-capped (planning $800$\,s, execution $20{,}000$ steps $=500$\,s; dotted).

- **中文翻译**：障碍密度扩展（8×8 m、每密度 10 个 seed）。时间按预算封顶（规划 800 s、执行 500 s = 20 000 步；虚线），应与成功率面板一起阅读。误差棒为跨 seed 标准差。

### [36] experiment.tex

- **页码**：p8
- **新增原文**：

  > Real-world pushing experiments with execution--planning alignment (over~$20$ runs, $2$ scenarios). \textbf{Top:} two robots pushing obstacles in a \(5{\times}6\,\mathrm{m}\) workspace. \textbf{Bottom:} WCCG overlays with the start face in blue.

- **中文翻译**：真实世界推挤实验与执行—规划对齐（约 20 次运行、2 个场景）。上：两机器人在 5×6 m 工作空间中推动障碍物的快照；下：起始面为蓝色的 WCCG 叠加。

### [37] experiment.tex

- **页码**：p7
- **新增原文**：

  > The UGVs are velocity-controlled, and the optimized contact forces are used only for feasibility evaluation, not for motor control. Motion capture provides robot and object poses, compared with the successor state predicted by $\mathsf{EvalSim}$: replanning triggers only when the position or orientation error exceeds $0.3$\,m or $\pi/4$, tolerating slight over-push.

- **中文翻译**：UGV 为速度控制，优化后的接触力只用于可行性评估、不用于电机控制。动捕给出机器人与物体位姿，并与 EvalSim 预测的后继状态比较：仅当位置误差超过 0.3 m 或姿态误差超过 π/4 时才触发重规划，该阈值较宽松。

### [38] experiment.tex

- **页码**：（见对应小节）
- **新增原文**：

  > This neighboring-object motion is not a separately encoded action but an emergent outcome of the coupled rigid-body rollout in $\mathsf{EvalSim}$, whose snapshot updates the WCCG and execution continues.

- **中文翻译**：这种相邻物体的运动不是单独编码的动作，而是 EvalSim 中耦合刚体 rollout 的涌现结果；其快照被用于更新 WCCG 并继续执行。


## conclusion.tex

### [39] conclusion.tex

- **页码**：p8
- **新增原文**：

  > This work presents PushAround, a multi-robot framework that jointly plans obstacle selection, contacts and forces through a hybrid search, and demonstrates hardware feasibility with state-feedback replanning. Future work targets obstacle-state estimation without external sensing or known masses.

- **中文翻译**：本文提出 PushAround：一个通过混合搜索联合规划障碍选择、接触与力的多机器人框架，并以状态反馈重规划验证了硬件可行性。未来工作面向无外部传感、质量未知的障碍状态估计。
