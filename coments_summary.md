The reviewers acknowledge the contribution of the paper, however, they
have some concerns that need to be addressed.
--------------------------
This paper presents PushAround, a physics-informed hybrid search
framework for collaborative path clearing in environments containing
multiple movable obstacles. The problem is formulated within NAMO, but
specifically considers a team of mobile robots that actively rearrange
obstacles to create a corridor with sufficient clearance for a larger
external vehicle.

Strengths:
- Coherent end-to-end framework; The integration of WCCG, gap ranking,
pushing-mode generation, and physics validation is well designed. The
method jointly considers which obstacle to move and how to push it,
while validating candidate actions through simulation.

- Recursive pushing; The planner can first clear movable blockers in
the swept region and then return to the original gap-opening task. Good
feature!

- Scalability: The method is evaluated with up to 45 movable obstacles,
which is a useful demonstration of scalability in dense clutter. The
reported success remains at 100% at 45 obstacles, although the
experiment uses five seeds per density.

- Strong simulation results and real-world validation: The proposed
method substantially outperforms the reported baselines in simulation
and is also demonstrated with two real robots.

Weaknesses:
- Physics-model robustness is insufficiently characterized: The method
relies heavily on simulation-based feasibility validation, but
sensitivity to uncertainty in mass, friction, force limits, contact
dynamics etc. is not systematically evaluated. 

- Limited evaluation of more complex scenarios: Although the method is
tested with up to 45 movable obstacles, the number of independent
trials is limited.

Interesting follow-up questions:
- The experiments primarily use two robots. What happens when the
number of robots increases with the complexity of the task? How does
the search and the contact/force formulation scale to larger robot
teams?

- What guarantees, if any, does the hybrid search provide regarding
solution quality?

- The objective includes the total duration T and the control-effort
cost J. Is the time needed for the final vehicle to actually traverse
the cleared corridor included in this objective, or is the objective
only concerned with clearing the obstacles? Similarly, does J only
capture the robots' effort in moving the obstacles?

- The paper demonstrates online replanning when the real execution
differs from the simulation, How can simple pushing robots evaluate
this discrepancy?

Conclusion:
Overall, this is a good contribution to the field and a well-written
paper. The combination of geometric reasoning, recursive pushing, and
physics-informed search is interesting, and the real-world validation
strengthens the contribution.
--------------------------
This paper presents PushAround, a physics-informed hybrid search method
for collaborative path clearing. The method uses a W-clearance
connectivity graph to identify blocking gaps, ranks these gaps, and
generates multi-robot pushing actions that are checked using
short-horizon physics simulation. The paper includes simulation
comparisons, ablation studies, scalability tests, and hardware
experiments.

Overall, I think the paper addresses an interesting problem and the
proposed framework is practical. The combination of geometric reasoning
and physics simulation is useful, and the experimental results are
encouraging. I would support acceptance after revision, but I think a
few parts of the method need some clarification.

First, the WCCG connectivity condition is important since it is used
throughout the search and also determines termination. The intuition is
reasonably clear, but I think the paper would benefit from a little
more justification here, or perhaps a comparison with a standard
configuration-space connectivity check. This seems especially relevant
when the obstacles are non-convex.

Second, I was a little confused about the relationship between Eq. (5)
and the actual search procedure. Eq. (5) is written as an optimization
problem, while the implementation uses sampled pushing directions,
limited lookahead, and a heuristic best-first search that terminates
once a feasible solution is found. The authors should clarify whether
any optimality or completeness claim is intended. If not, it may be
better to describe Eq. (5) as the objective used to guide the search.

Third, it is not completely clear how the optimized contact forces are
used on the hardware. The pushing mode includes both contact points and
forces, but the execution section mainly describes moving the robots to
the contact configuration and then following the desired pushing
direction. It would be useful to briefly explain the low-level
controller and whether these forces are actually commanded or are
mainly used to check feasibility. Related to this, I am also not sure
whether coupled motion between multiple objects, such as in the second
hardware experiment, is explicitly considered during planning or is
mostly handled by the physics simulation.

The experiments are generally convincing. The paper already mentions
that the baselines use the same W-clearance criterion, object
distribution, and execution simulator. However, a few more
implementation details, such as robot reachability checks, timeout
limits, and computation budget, would make the comparison easier to
interpret. I would also suggest adding error bars or standard
deviations, particularly for the scalability experiment where only five
seeds are used for each obstacle density.

Overall, I think the approach is technically reasonable and the
experiments support the proposed method. My comments are mainly about
clarification rather than major technical concerns, and I would support
acceptance after these revisions.


我已经把手稿和 decision package 中的两份审稿意见逐项对照看了一遍。整体判断是：**这是一轮明显偏正面的返修，审稿人已经基本认可问题价值、方法框架和实验结果，目前没有看到“核心创新性不成立”或“方法需要推倒重做”式的意见。** 后续修改的重点应当是把几个理论/实现接口讲严谨，并用少量有针对性的补充实验消除 physics-model robustness 和统计充分性方面的疑虑。

手稿当前的主线实际上已经比较完整：WCCG → frontier-gap ranking → direct/recursive pushing → contact/force mode generation → simulation validation → hybrid search → online replanning，并且已有 40-trial 主实验、最高 45 obstacles 的 scalability，以及 20 次实机运行。 因此这轮更适合**精准补强**，而不是扩大文章 scope。

## 1. 两位审稿人的整体态度

**Reviewer 3：明显正面，但希望增强“physics-informed”这一核心卖点的可信度。**

他首先主动列出了四项 strengths：

* end-to-end framework coherent；
* WCCG、gap ranking、pushing mode、physics validation 的结合设计合理；
* **recursive pushing 被单独点名为 “Good feature!”**；
* 45 obstacles scalability 是有价值的；
* simulation results 和 two-robot hardware validation 都较强。

结尾也是：

> “Overall, this is a good contribution to the field and a well-written paper.”

所以 R3 并没有质疑论文是否有贡献。他真正抓住的 weakness 主要只有两个：

1. **physics-model robustness 没有系统验证**；
2. 高复杂度场景虽然做到 45 obstacles，但 independent trials 较少。

其余诸如更多机器人、solution quality guarantee、objective 定义、如何检测 sim-real discrepancy，都被放在了 “Interesting follow-up questions” 下，严格说其严重程度低于前两个 weakness。

---

**Reviewer 4：态度更积极，几乎明确给出了 accept-after-revision。**

他的原话非常关键：

> “I would support acceptance after revision”

以及结尾：

> “My comments are mainly about clarification rather than major technical concerns.”

这意味着 R4 基本已经接受了：

* problem 本身有意义；
* geometric reasoning + physics simulation 的组合有价值；
* 实验总体 convincing；
* technical approach reasonable。

他的关注点主要是**论文当前有几个逻辑接口没有解释完整**，而不是要求重新设计算法。

因此综合来看，我会把当前状态理解为：

> **方法和贡献已经过关，revision 的关键是让审稿人确信：数学表述没有过度 claim，WCCG 判据有充分依据，physics model 与真实执行之间的接口是清楚且鲁棒的，实验统计也足以支持现有结论。**

---

# 2. 审稿意见可以归纳成五组

## A. Physics model 与真实执行之间的可信度

这是我认为**整轮 revision 最重要的问题**。

R3 明确指出：

> sensitivity to uncertainty in mass, friction, force limits, contact dynamics etc. is not systematically evaluated.

而现在手稿中，push mode 通过 contact point 和 force 描述，Eq. (10)–(11) 又显式优化 wrench feasibility；随后 EvalSim 用 short-horizon simulation 决定 candidate 是否进入搜索树。

因此“physics-informed”实际上是 PushAround 最核心的 distinguishing factor。审稿人自然会问：

> 如果 simulator 的 mass/friction/contact model 不准，所谓 physics validation 还有多少意义？

同时 R4 从另一个角度问到了相同问题：

* optimized contact forces 到底如何用于 hardware？
* forces 是实际 command，还是只是 feasibility assessment？
* 多物体 simultaneous/contact-induced motion 是 planner 显式建模，还是 simulator 自己产生的？

现在硬件部分只说机器人到达 contact configuration 后沿 desired direction push，并通过 replanning 处理 drift、slippage 等误差。 这个解释对当前审稿人来说还不够闭环。

### 我建议的修改

这部分值得增加一个**非常针对性的 model-mismatch robustness experiment**，不需要重新做大规模硬件。

例如固定测试场景，在 planner simulation 中使用 nominal parameters，执行环境中扰动：

* obstacle mass：例如 ±20%、±40%；
* friction coefficient：例如 ±20%、±40%；
* robot force capability：例如 80%、100%、120% nominal；
* 可选再加入 contact/slip perturbation。

指标只需要：

* success rate；
* replanning count；
* planning/execution time 或 pushes。

甚至可以把多个误差统一成一个 parameter perturbation level，例如：

[
0,\ 10%,\ 20%,\ 30%,\ 40%.
]

这样一个小图就可以正面回答 R3，而且非常契合论文核心卖点。

同时正文必须明确：

**规划层的 force 不一定是 low-level force setpoint。**

如果你们目前硬件实际上是 velocity/pose-controlled Mecanum robots，那么最好明确写成：

> contact force optimization is used to determine whether the selected contact configuration can generate the required object wrench within the robots' actuation limits; hardware execution tracks the corresponding contact poses and pushing velocities rather than directly commanding the optimized forces.

这一点会同时解决 R4 的 confusion。

---

# 3. Eq. (5) 与 PIHS 搜索之间的数学关系必须收紧

这是**理论表述上优先级最高**的问题。

当前 Problem Statement 把问题写成：

[
\min_\pi T+\alpha\sum J(\cdot),
]

但实际 Alg. 1 是：

* sampled pushing directions；
* bounded recursive task generation；
* limited gap lookahead；
* heuristic best-first priority；
* 找到第一条 feasible W-clearance solution 就停止。



所以 Reviewer 4 很准确地指出：

> Eq. (5) 看起来像一个 optimization problem，但实现并不求 global optimum。是否 intended to claim optimality or completeness？

Reviewer 3 也从 solution-quality guarantees 角度问了同样的问题。

### 这里我建议不要试图证明 optimality

没有必要，也很可能证明不了。

最好主动明确：

> Eq. (5) defines the planning objective, rather than implying that the proposed finite-sampling search globally solves the underlying continuous hybrid optimization.

并区分三个层次：

1. **Underlying problem**：continuous hybrid optimization；
2. **PIHS search space**：由 sampled directions/contact modes 构成的有限候选空间；
3. **Algorithm**：heuristic best-first feasible search，不 claim global optimality/completeness。

甚至可以在 Sec. III-D 增加一句非常明确的话：

> PIHS is designed as a feasibility-oriented heuristic search and does not claim global optimality or completeness with respect to (5).

这样反而更严谨，不会削弱论文。

同时把 “optimization” 类措辞略微收紧，例如：

> “the objective guiding the search”

而不是让人理解成 Alg. 1 正在严格求解 Eq. (5)。

这个修改成本极低，但非常重要。

---

# 4. WCCG connectivity criterion 需要补一个真正有说服力的 justification

Reviewer 4 对 Eq. (7) 的关注也很合理，因为：

* WCCG 不只是 heuristic；
* 它用于 connectivity 判断；
* 它还直接决定 search termination。

当前正文说 bridge–bridge edge with width below (W) 表示不可通过 bottleneck，因此 start/goal 在同一 face 就得到 W-clear connectivity。

但对 non-convex obstacles，这个结论目前写得略快。

### 推荐做法

我不建议花很多篇幅搞复杂 theorem，但至少做两件事。

第一，给出**明确 assumptions + proposition/remark**：

* obstacle boundaries are decomposed into convex components/segments；
* all clearance-critical closest-point pairs are represented；
* WCCG edges with distance (<W) correspond to barriers in the disk-inflated configuration space；
* hence faces correspond to connected free-space regions under those assumptions。

换句话说，要把它和 Minkowski inflation / configuration-space connectivity 建立明确关系。

第二，按照 Reviewer 4 的建议，做一个**轻量 sanity check**：

> compare WCCG connectivity against a conventional configuration-space occupancy/connectivity query over a large random set of scenes.

这项实验甚至不用进入主结果表。可以一句话：

> Across (X) randomly generated configurations including non-convex objects, WCCG connectivity agreed with a high-resolution C-space reference in (100%) of cases.

如果确实能做到 100%，这个 reviewer comment 基本就完全封死了。

这项修改的重要性我会排得非常高，因为 WCCG 是整个算法的几何基础。

---

# 5. 实验统计和 baseline fairness 需要补齐，但不需要大改实验体系

R4 要求：

* robot reachability checks；
* timeout limits；
* computation budget；
* scalability error bars/std。

R3 也认为 45-obstacle scalability 每个 density 只有五个 seeds，independent trials 偏少。

现在手稿中主比较其实已经有 **40 randomized trials**，这是不错的；真正比较弱的是 Fig. 10 scalability，因为每个 density 是 5 seeds。

### 最推荐的修改方式

如果计算成本允许，我会把 scalability：

**5 seeds → 10 seeds**，最好 **20 seeds**。

因为这类纯仿真实验的 reviewer expectation 不高，增加 seed 非常便宜，却可以消掉一个明确 weakness。

而且由于你们现在采用 nested-density construction，即同一个 seed 下：

[
15\rightarrow20\rightarrow\cdots\rightarrow45
]

逐渐增加障碍物，那么最好在正文中明确：

> each seed defines an independent base scene sequence, while increasing densities within the same seed are generated incrementally.

然后：

* success rate：binomial CI 或直接 error bar；
* PT/ET：mean ± std 或 median/IQR。

Reviewer 明确要 error bars/std，因此建议直接满足，不必争论。

同时补充 baseline 统一设置：

* same timeout；
* same max search/computation budget；
* same execution simulator；
* same collision/reachability test；
* same success criterion；
* unsuccessful runs 如何计入 PT。

你们当前 manuscript 已经写了 failed/timeout-pruned trials 对 PT 赋 400 s cap，这是正确方向。 只需把公平性条件写得更集中、更明确。

---

# 6. 多机器人 scalability：建议回答，但不用把论文改成“robot-number scaling paper”

Reviewer 3 问：

> What happens when the number of robots increases ... How does the search and contact/force formulation scale to larger robot teams?

这是一个合理问题，因为 Eq. (10) 的 contact tuple dimension 和 (N) 有直接关系，而当前实验几乎都是 two robots。

但注意：R3 把它放在 **Interesting follow-up questions**，不是 formal weakness。

因此我不建议为这条投入大量硬件实验。

### 性价比最高的处理

增加一个小型 simulation：

[
N_R = 1,2,3,4
]

或者：

[
N_R=2,3,4.
]

选择固定的 moderately heavy obstacle / representative clutter，报告：

* success；
* mode-generation time；
* total planning time；
* perhaps average feasible-contact combinations。

目的不是证明 arbitrarily scalable，而是说明：

> More robots enlarge the admissible wrench set but increase the combinatorial contact-assignment space; the greedy contact replacement avoids exhaustive (K^N) enumeration.

这样足够回答 reviewer。

如果版面有限，这甚至可以放 supplementary，正文只放一句结论。

---

# 7. 另外几个 clarification 都属于“小修但必须回答干净”

### Objective 是否包括最终 vehicle traversal

R3 问得很具体。

当前 Eq. (5) 中 (T=\sum\Delta t_k)，schedule 本身只有 robot pushing tasks，所以从当前 formulation 来看，**最终大车 traversing corridor 的时间并没有包含进去**；目标实际是 clearing process 的 duration + pushing effort。

应该直接明确：

> The optimization concerns the clearance operation only. Vehicle traversal is the terminal feasibility condition and is not included in (T).

同样：

> (J) measures the robots' manipulation/control effort associated with obstacle clearing.

如果你们本来就是这个意思，不需要改算法，只需补一句。

---

### 如何检测 simulation–execution discrepancy

当前写了：

> replanning is triggered when ... realized motion deviates from simulation, a push fails, ...



但 Reviewer 3 问“simple pushing robots 怎么知道 deviates”。

硬件中用了 motion capture，所以其实很好回答：

* observe object pose；
* compare measured pose displacement/twist with predicted successor；
* threshold exceed → replan。

仿真/未来 onboard sensing 则可以由 state estimator 提供同类 object state。

应该给一个具体定义，例如：

[
|x_m^{\rm obs}-x_m^{\rm pred}|>\epsilon_x
\quad\text{or}\quad
|\psi_m^{\rm obs}-\psi_m^{\rm pred}|>\epsilon_\psi.
]

不一定非得放公式，但阈值机制一定要说清。

---

### Coupled multi-object pushing

R4 特别注意到了 hardware Scenario 2 中，一个被推物体同时带动邻近 T-shaped obstacle。

这其实是你们方法一个可以**顺势加强的优点**。

答案应该明确：

> coupled inter-object motion is not represented by a separately enumerated analytical contact mode; it emerges during EvalSim because all movable rigid bodies and their contacts are simulated jointly.

也就是说：

* high-level task selects target obstacle/contact action；
* simulator propagates all object–object contacts；
* resulting full scene state (s') is returned；
* WCCG/search then operates on this resulting configuration。

这反而正好解释为什么 simulation-in-the-loop 有价值。

建议在 Eq. (12) 后面加一句，把这个逻辑明确写出来。

---

# 8. 按重要性排序，我建议这样组织 revision

| 优先级    | 修改事项                                                          | 原因                                 | 是否建议补实验            |
| ------ | ------------------------------------------------------------- | ---------------------------------- | ------------------ |
| **P0** | Physics/model mismatch robustness                             | R3 唯一最实质性的技术 weakness，直接关系核心 claim | **强烈建议**           |
| **P0** | 澄清 Eq. (5) 与 heuristic PIHS，无 optimality/completeness claim   | R3+R4 同时问到，属于理论严谨性                 | 不需要                |
| **P0** | WCCG connectivity justification，尤其 non-convex                 | R4 指出其决定搜索和 termination            | **建议小实验验证**        |
| **P1** | hardware force/controller interface + coupled-object dynamics | R4 明确 confusion，当前正文确实缺接口说明        | 不需新硬件              |
| **P1** | scalability 增加 seeds + error bars/std                         | R3/R4 同时涉及                         | **建议 10–20 seeds** |
| **P1** | baseline fairness：timeout、reachability、budget                 | 容易修，而且增强实验可信度                      | 不一定                |
| **P2** | robot-number scaling                                          | R3 follow-up，不是核心 weakness         | 小型仿真即可             |
| **P2** | objective 中 T/J 的物理意义                                         | 纯 clarification                    | 不需要                |
| **P2** | sim-real discrepancy detection                                | 纯 implementation clarification     | 不需要                |

---

# 9. 我认为最合理的“最小但充分”新增实验包

如果目标是**尽可能提高接受概率，同时控制工作量**，我不会扩展很多实验。最值得做的是三个：

1. **Physics uncertainty robustness**

   * mass/friction/force-limit perturbation；
   * success + replanning/time。

2. **Scalability statistics strengthening**

   * 5 seeds → 至少 10，最好 20；
   * error bars/std。

3. **一个很轻量的 WCCG validation 或 robot-number scaling**

   * 两者如果篇幅只能选一个，我优先 **WCCG validation**；
   * robot-number scaling 可以 supplementary 或 response 中解释复杂度。

实际上做到这三项，再把正文 clarification 补齐，我认为已经足够完整。

---

# 10. 对本轮结果的总体评价

从 RA-L revision 的角度，这轮结果是**相当不错的**。

尤其有三个积极信号：

**第一，没有 reviewer 在攻击 novelty。**
没人说 WCCG + pushing 是 incremental、缺乏贡献，反而 R3 明确认可 recursive pushing 和 integrated framework。

**第二，没有 reviewer 认为实验结论不成立。**
R4 直接说 “experiments are generally convincing”，R3 也认可 simulation + real-world validation。主要要求只是 robustness 和 statistics 更完善。

**第三，Reviewer 4 已经直接表态支持 revision 后接受。**
这通常意味着只要逐项、明确、没有回避地回答，其意见很容易关闭。

因此这轮返修的核心策略不应是继续堆新模块，而应是：

> **守住当前主线，减少过度 claim；强化 physics robustness；把 WCCG、force execution、simulation coupling 和 replanning detection 这几个逻辑接口完全闭合；最后补足统计呈现。**

如果这些处理得好，我会认为后续进入接受的概率是比较高的，尤其不像需要“重大算法重构”的 revision。
