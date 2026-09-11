# WCCG 独立开源方案摘要

## 1. 核心定位

WCCG 不应仅定位为快速连通性检测器，而应定位为：

> **面向二维杂乱环境的 manipulation-aware reachability oracle：支持批量目标查询，并将几何不可达转化为可操作的 gap-opening 子目标。**

相较于只返回连通性或路径的 C-space、栅格和 navmesh 方法，WCCG 还输出阻塞 gap 的障碍物对、最近点、宽度、方向及 frontier topology，可直接连接任务规划与操作规划。

建议英文描述：

> **A high-performance 2D clearance-topology engine for batched reachability queries and actionable bottleneck extraction in movable-obstacle environments.**

## 2. 在 TAMP 中的作用

对环境状态 (s)、净空需求 (W) 和目标 (G_k)，WCCG 可实现逻辑谓词：

\[
\mathsf{Reachable}_W(S,G_k;s)
\triangleq
\text{$S$ and $G_k$ belong to the same WCCG free-space component}.
\]

同一障碍物布局和 (W) 下，构图一次即可批量查询多个：

- 工作位置、抓取位姿、观察位姿和装配区域；
- 候选任务目标与任务顺序；
- 机器人起终点组合；
- 携带相同尺寸载荷时的移动目标。

查询失败时，WCCG 返回：

\[
g=(o_i,o_j,p_i,p_j,w_g,n_g),
\]

即 gap 两侧障碍物、最近点、宽度和 opening direction。TAMP 可结合 `movable`、质量、操作类型、接触可达性和禁入区域等属性，决定是否生成 `OpenGap`、`Push`、`Pull` 或 `Relocate` 子任务。操作后更新物体状态、重建 WCCG，再验证原始目标。

WCCG 的职责是确定“应改变哪个几何关系”；下游 manipulation planner 负责确定“如何可靠地实现该改变”。

## 3. 建议的独立 API

```python
import wccg

graph = wccg.build(obstacles, clearance=1.0)

result = graph.query(start, goal)
print(result.connected)
print(result.frontier)

for gap in result.blocking_gaps:
    print(
        gap.obstacle_ids,
        gap.width,
        gap.closest_points,
        gap.opening_normal,
    )
```

建议同时提供：

- `query_many(start, goals)`：批量目标查询；
- `connected_components()`：净空连通分量；
- `blocking_gaps(start, goal)`：不可达原因；
- `obstacle_adjacency()`：障碍物拓扑关系；
- `update_obstacles(...)`：为未来增量更新预留接口；
- Shapely、GeoJSON 和普通 polygon-array 输入适配。

在 PDDLStream/TAMP 中可分别作为：

1. test stream：验证 `Reachable(S,G,W)`；
2. generator stream：生成 `BlockingGap`、相关障碍物和候选 opening direction。

## 4. 潜在应用

- NAMO、物体重排和杂乱环境移动操作；
- TAMP 中的几何可达性谓词和 manipulation subgoal generation；
- 多机器人协同推动与环境清障；
- 携物机器人、可变尺寸机器人和编队的净空查询；
- 仓储 AMR/叉车的 aisle-clearance 与 blocker diagnosis；
- 工厂、物流、建筑、矿区和应急场景的通道瓶颈分析。

## 5. 当前基础

现有实现已包含：

- C++/pybind11/OpenMP 后端；
- convex/non-convex polygon 和 convex decomposition；
- AABB broad phase、确定性 bridge construction；
- gap/bridge metadata、组件查询和 Python 兼容层；
- Python--C++ 严格拓扑回归；
- 300 个 convex/non-convex/mixed 场景的 C-space validation；
- WCCG 与 continuous C-space 在 300/300 场景一致；
- 15--100 障碍物构图相对 Python 约 10.2--33.2 倍加速。

## 6. 能力边界

首个独立版本应明确限定为：

- 二维多边形环境；
- 用标量净空 (W) 表示的平移圆盘等效模型；
- 静态快照或操作后重构；
- 输入具有可靠的 polygon boundary/convex decomposition。

暂不声明支持：

- 非圆形机器人完整 (SE(2)) C-space；
- 3D、动态障碍物或时空连通性；
- 动力学、可控性和操作成功保证；
- 尚未建立的普适拓扑完备性。

gap 是 manipulation candidate/failure certificate，而不是操作可行性的充分证明；接触可达性、碰撞、动力学和执行器能力仍由下游模块验证。

## 7. 开源前最小工作

1. 将 C++ core、Python binding 和 PushAround adapter 解耦；
2. 把完整 face location、frontier 和 gap-sequence query 纳入独立包；
3. 提供 `pip install`、CMake 和常见平台 wheels；
4. 增加退化接触、重合、极窄通道、不同 (W) 和线程确定性测试；
5. 保留 Python reference、C-space validator、benchmark 和可视化示例；
6. 提供一个 TAMP/PDDLStream 风格的 blocker-to-subgoal 示例；
7. 清理 PushAround 专用命名，并明确许可证、引用方式和适用假设。

建议仓库结构：

```text
wccg/
  cpp/          # geometry, builder, graph, query
  python/       # pybind package and high-level API
  adapters/     # Shapely, GeoJSON, PushAround/ROS adapters
  examples/     # batch query and TAMP gap-opening demo
  tests/        # geometry, topology and regression
  benchmarks/   # Python, CC, raster and scaling comparisons
```

## 8. 发布策略

论文双盲返修阶段先完成仓库解耦和文档，接收后正式公开；如返修需要代码，可使用匿名仓库。推荐采用 BSD-3-Clause 或 Apache-2.0 等宽松许可证，并在发布前核查第三方依赖和潜在知识产权要求。

对外宣传应强调：

> **Connectivity plus actionable gap geometry at near-connectivity-query cost.**

不应将其宣传为通用路径规划器或单纯的 Shapely 加速替代品。
