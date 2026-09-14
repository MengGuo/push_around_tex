import os
import sys
from typing import List, Dict, Tuple, Optional, Any
from copy import deepcopy
import numpy as np
import time

sys.path.append(os.getcwd())

from src.env.object import ReducedObjectState
from src.env.env import EnvBase
from src.config.policy_config.clutterbreaker_config import ClutterBreaker_Config 
from src.policy.clutterbreaker_policy.common_structures import *
from src.policy.clutterbreaker_policy.collaborative_pusher.arc_transition import *
from src.policy.clutterbreaker_policy.collaborative_pusher.cost_estimator import CostEstimator
from src.policy.clutterbreaker_policy.collaborative_pusher.mode_table import ModeTable
from src.utils.polygon_minimal_distance import shape_min_distance

INF = 1e10

_DIAG = os.environ.get("DEBUG_MODEGEN_DIAG") == "1"


def _diag(msg: str) -> None:
    """Env-gated mode-generation diagnostics (no-op unless DEBUG_MODEGEN_DIAG=1)."""
    if _DIAG:
        print(f"[ModeGenDiag] {msg}", flush=True)

# ====== 如果你的 Mode 类没有 is_equal_to，可加一个mixin或替代实现 ======
def _mode_equal(m1: Mode, m2: Mode, tol: float = 1e-6) -> bool:
    """宽松比较两个模式是否等价：逐机器人接触点坐标近似相等"""
    if m1 is None or m2 is None:
        return False
    if set(m1.contact_points.keys()) != set(m2.contact_points.keys()):
        return False
    for rid, p1 in m1.contact_points.items():
        p2 = m2.contact_points.get(rid, None)
        if p2 is None:
            return False
        if np.linalg.norm(np.asarray(p1) - np.asarray(p2)) > tol:
            return False
    return True

def _safe_norm(v, eps=1e-9):
    n = float(np.linalg.norm(v))
    return n if n > eps else eps

def _gen_force_vec(p_local: np.ndarray, n_local: np.ndarray) -> np.ndarray:
    """广义力向量 g = (nx, ny, tau_z), tau = (r x n)_z"""
    # p_local: [rx, ry], n_local: [nx, ny]
    tau = np.cross(np.append(p_local, 0.0), np.append(n_local, 0.0))[2]
    return np.array([n_local[0], n_local[1], tau], dtype=float)

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (_safe_norm(a) * _safe_norm(b)))


class ModeGenerator:
    
    def __init__(   self,
                    config: ClutterBreaker_Config,
                    group: TaskObjectGroup =None,
                    scenario_name: str = "base",):

        self.group = group
        self.config = config
        

        self.cost_estimator = CostEstimator(
            group=self.group,
            config=self.config
        )

        self.mode_table = ModeTable(
            config = self.config,
            group = group,
            scenario_name = scenario_name
        )
        self.local_start_state: Optional[ReducedObjectState] = None
        self.local_goal_state: Optional[ReducedObjectState] = None
        self.disabled_mode_list: Optional[List[Mode]] = None

        self.set_task_object_group(group)
    
    def set_task_object_group(self, group:TaskObjectGroup):

        if group is not None:
            self.target_obs = group.target_obs  
            self.robots: List[Robot] = list(group.robot_dict.values())
            self.robot_dict: Dict[int,Robot] = group.robot_dict
            self.rob_num = len(self.robots)
        else:
            self.target_obs = None
            self.robots = None
            self.robot_dict = None
            self.rob_num = None
        
        self.cost_estimator.set_task_object_group(group)
        self.mode_table.set_task_objects(group) 

    def _prepare_cand_cps(self, push_vel):
        robot_cand_cps = {}
        raw_n = {}
        for r in self.robots:
            if r.num_id < 0:
                continue
            cand_cps = r.reachable_contact_points.get(self.target_obs.num_id, None)
            robot_cand_cps[r.num_id] = cand_cps
            raw_n[r.num_id] = 0 if cand_cps is None else len(cand_cps)

        # ---- 根据 push_vel 进行候选接触点筛选（法向与期望速度夹角 < 90°）----
        vx, vy, w = float(push_vel[0]), float(push_vel[1]), float(push_vel[2])
        v_lin = np.array([vx, vy], dtype=float)
        COS_EPS = 1e-8          # 防止除零
        SPEED_MIN = 1e-6        # 期望速度太小的点直接丢弃（也可以选择保留）
        
        for rid, cands in list(robot_cand_cps.items()):
            if cands is None:
                # 没有候选可用
                robot_cand_cps[rid] = None
                continue
            filtered_cands = []
            for cand_cp in cands:
                pL = cand_cp.get("point_local", None)
                nL = cand_cp.get("normal_local", None)

                # 期望接触点速度（物体系）
                # omega x r_local = [-w*r_y, w*r_x]
                v_cp = v_lin + np.array([-w * pL[1], w * pL[0]], dtype=float)

                # 速度过小：可选跳过（也可以放宽，这里保守些）
                if np.linalg.norm(v_cp) < SPEED_MIN:
                    continue

                # 若没有法向，跳过（也可用 nearest-edge 估计，这里只做筛选不补齐）
                if nL is None or np.linalg.norm(nL) < COS_EPS:
                    continue

                # 夹角 < 90° <=> dot(n, v_cp) > 0
                if float(np.dot(nL, v_cp)) > 0.0:
                    filtered_cands.append(cand_cp)

            robot_cand_cps[rid] = filtered_cands
        if _DIAG:
            _diag(f"obs={None if self.target_obs is None else self.target_obs.num_id} "
                  f"rob_num={self.rob_num} push_vel={np.round(np.asarray(push_vel, float), 3).tolist()} "
                  f"candidates(raw->normal-filtered): "
                  + ", ".join(f"r{rid}:{raw_n.get(rid, 0)}->{len(c) if c else 0}"
                              for rid, c in robot_cand_cps.items()))
        return robot_cand_cps   

    # ----------------- 小工具：统一禁用模式判定 -----------------
    def _check_disabled(self, mode: Mode) -> bool:
        if not self.disabled_mode_list:
            return False
        for stuck_mode in self.disabled_mode_list:
            if hasattr(mode, "is_equal_to"):
                if mode.is_equal_to(stuck_mode):
                    return True
            else:
                if _mode_equal(mode, stuck_mode):
                    return True
        return False

    # ---------- 工具：是否可达 ----------
    def _cp_reachable(self, rid: int, p_local: np.ndarray) -> bool:
        cands = self.robot_dict[rid].reachable_contact_points.get(self.target_obs.num_id, None)
        if not cands:
            return False
        for c in cands:
            pl = np.asarray(c["point_local"], float)
            if np.allclose(pl, p_local, atol=1e-2) :
                return True
        return False

    # ---------- 工具：与既有接触点避免碰撞/过近 ----------
    def _ok_wrt_selected(self,  candidate_p: np.ndarray, 
                                candidate_n: np.ndarray,
                                selected: Dict[int, np.ndarray], 
                                selected_normals: Dict[int, np.ndarray],
                                min_dist: float) -> bool:
        max_pusher_len = max([r.pusher_len for r in self.robots])

        for r_id, p in selected.items():
            candidate_r_center = candidate_p - candidate_n * max_pusher_len
            selected_r_center = p - selected_normals[r_id] * max_pusher_len
            if np.linalg.norm(candidate_r_center - selected_r_center) < min_dist:
                return False
        return True

    def _candidate_ok_wrt_selected_exact(
        self,
        robot: Robot,
        candidate_p: np.ndarray,
        candidate_n: np.ndarray,
        selected: Dict[int, np.ndarray],
        selected_normals: Dict[int, np.ndarray],
        min_dist: float,
    ) -> bool:
        """Check that a candidate contact does not duplicate/conflict selected ones.

        Contact points are local to the target object, but the existing code
        evaluates pusher shapes in the same local frame.  This helper keeps
        that convention and uses each robot's own pusher length instead of the
        approximate max-length test in ``_ok_wrt_selected``.
        """
        duplicate_tol = float(getattr(self.config, "mode_gen_duplicate_cp_tol", 1e-3))
        candidate_p = np.asarray(candidate_p, dtype=float)
        candidate_n = np.asarray(candidate_n, dtype=float)

        cand_center = candidate_p - candidate_n * float(robot.pusher_len)
        cand_yaw = float(np.arctan2(candidate_n[1], candidate_n[0]))
        cand_shape = robot.shape_info_gf(ReducedObjectState(cand_center, cand_yaw))

        for other_rid, other_p in selected.items():
            other_p = np.asarray(other_p, dtype=float)
            if np.linalg.norm(candidate_p - other_p) < duplicate_tol:
                return False

            other_n = np.asarray(selected_normals[other_rid], dtype=float)
            other_r = self.robot_dict[other_rid]
            other_center = other_p - other_n * float(other_r.pusher_len)
            other_yaw = float(np.arctan2(other_n[1], other_n[0]))
            other_shape = other_r.shape_info_gf(ReducedObjectState(other_center, other_yaw))

            d, _, _ = shape_min_distance(cand_shape, other_shape)
            if float(d) < float(min_dist):
                return False
        return True

    def _mode_contact_geometry_ok(self, mode: Mode, min_dist: Optional[float] = None) -> bool:
        """Return True if a complete mode has unique and non-overlapping pushers."""
        if mode is None:
            return False
        if min_dist is None:
            min_dist = float(getattr(self.config, "mode_gen_min_robot_dist", 0.1))

        selected_points: Dict[int, np.ndarray] = {}
        selected_normals: Dict[int, np.ndarray] = {}
        for rid, p in mode.contact_points.items():
            if mode.contact_normals is None or rid not in mode.contact_normals:
                return False
            if rid not in self.robot_dict:
                return False
            n = mode.contact_normals[rid]
            if not self._candidate_ok_wrt_selected_exact(
                self.robot_dict[rid],
                np.asarray(p, dtype=float),
                np.asarray(n, dtype=float),
                selected_points,
                selected_normals,
                float(min_dist),
            ):
                return False
            selected_points[rid] = np.asarray(p, dtype=float)
            selected_normals[rid] = np.asarray(n, dtype=float)
        return True
    
    # ----------------- 小工具：碰撞检查占位（按需替换） -----------------
    def _collision_ok(self, mode: Mode) -> bool:
        """占位：检查机器人在该接触点是否无自碰/无与障碍冲突等。此处默认True。"""
        return True

    # ----------------- 工具：单位法向力对应的广义力 -----------------
    @staticmethod
    def _unit_push(pl: np.ndarray, nl: np.ndarray) -> np.ndarray:
        """Generalized unit push (nx, ny, torque) with torque = rx*ny - ry*nx."""
        return np.array([nl[0], nl[1], float(pl[0] * nl[1] - pl[1] * nl[0])], dtype=float)

    # ----------------- 初始成组 1/2：顺序贪心（原语义） -----------------
    def _assign_contacts_sequential(self, *, robot_cand_cps, res_push_force, min_dist,
                                    allow_robots=None):
        """Original fixed-order residual-greedy initial assignment.

        Returns ``(contact_points, contact_normals)`` or ``None`` when any robot
        has no candidate (or none of its candidates satisfies the pairwise
        pusher-distance constraint).
        """
        selected_points: Dict[int, np.ndarray] = {}
        selected_normals: Dict[int, np.ndarray] = {}

        robots = [r for r in self.robots if r.num_id >= 0]
        if allow_robots is not None:
            allowed = {int(x) for x in allow_robots}
            robots = [r for r in robots if int(r.num_id) in allowed]

        for r in robots:
            cands = robot_cand_cps.get(r.num_id, None)
            if not cands:
                _diag(f"seq greedy fail: robot {r.num_id} has ZERO candidates after normal filter "
                      f"(obs={self.target_obs.num_id}, rob_num={self.rob_num})")
                return None

            max_score = -INF
            best_pl, best_nl, best_unit_push = None, None, None
            for c in cands:
                pl = np.asarray(c["point_local"], dtype=float)
                nl = np.asarray(c["normal_local"], dtype=float)
                if not self._candidate_ok_wrt_selected_exact(
                    r, pl, nl, selected_points, selected_normals, float(min_dist),
                ):
                    continue
                unit_push = self._unit_push(pl, nl)
                denom = norm(unit_push) * norm(res_push_force) + 1e-8
                cos_angle = float(np.dot(unit_push, res_push_force) / denom)
                if cos_angle > max_score:
                    max_score = cos_angle
                    best_pl, best_nl, best_unit_push = pl, nl, unit_push

            if best_pl is None:
                _diag(f"seq greedy fail: robot {r.num_id}: all {len(cands)} candidates rejected by "
                      f"pairwise pusher-distance >= {min_dist} (obs={self.target_obs.num_id})")
                return None

            selected_points[r.num_id] = best_pl
            selected_normals[r.num_id] = best_nl
            fnmax = float(r.fnmax)
            denom = (norm(best_unit_push) ** 2 + 1e-8)
            res_proj = float(np.dot(res_push_force, best_unit_push) / denom)
            res_proj = max(0.0, min(res_proj, fnmax))
            res_push_force = res_push_force - res_proj * best_unit_push

        return selected_points, selected_normals

    # ----------------- 初始成组 2/2：有界回溯（换序 + 逐机器人候选回退） -----------------
    def _assign_contacts_backtracking(self, *, robot_cand_cps, target_force,
                                      min_dist, budget: int, allow_robots=None):
        """Feasibility-first assignment search used when the sequential greedy fails.

        Unlike the fixed-order greedy this tries *all* robots jointly: robots are
        expanded most-constrained-first (fewest candidates) and every candidate is
        ordered by alignment with the required generalized force, so a robot that
        was blocked by the assignment order can be rescued by backtracking.

        ``allow_robots`` (iterable of robot ids) restricts the assignment to a
        subset of the team, which is what the N-robot fallback in
        ``_greedy_optimization`` uses.  Returns ``(points, normals)`` or ``None``.
        """
        robots = [r for r in self.robots if r.num_id >= 0]
        if allow_robots is not None:
            allowed = {int(x) for x in allow_robots}
            robots = [r for r in robots if int(r.num_id) in allowed]
        if not robots:
            return None

        per_robot = {}
        for r in robots:
            cands = robot_cand_cps.get(r.num_id) or []
            scored = []
            for c in cands:
                pl = np.asarray(c["point_local"], dtype=float)
                nl = np.asarray(c["normal_local"], dtype=float)
                u = self._unit_push(pl, nl)
                denom = norm(u) * norm(target_force) + 1e-8
                scored.append((float(np.dot(u, target_force) / denom), pl, nl))
            if not scored:
                return None
            scored.sort(key=lambda t: -t[0])
            per_robot[r.num_id] = scored

        order = sorted(per_robot.keys(), key=lambda rid: (len(per_robot[rid]), rid))
        nodes = [0]

        def dfs(i, pts, nls):
            if i == len(order):
                return dict(pts), dict(nls)
            rid = order[i]
            r = self.robot_dict[rid]
            for _, pl, nl in per_robot[rid]:
                nodes[0] += 1
                if nodes[0] > int(budget):
                    return None
                if not self._candidate_ok_wrt_selected_exact(r, pl, nl, pts, nls, float(min_dist)):
                    continue
                pts[rid] = pl
                nls[rid] = nl
                got = dfs(i + 1, pts, nls)
                if got is not None:
                    return got
                pts.pop(rid, None)
                nls.pop(rid, None)
            return None

        result = dfs(0, {}, {})
        _diag(f"backtracking assignment: robots={order} nodes={nodes[0]}/{int(budget)} "
              f"-> {'FEASIBLE' if result is not None else 'none'} (obs={self.target_obs.num_id})")
        return result

    # ----------------- 初始成组 3/3：子集兜底（临时丢机） -----------------
    def _assign_contacts_subset_fallback(self, *, robot_cand_cps, target_force,
                                         min_dist, budget, drop_budget, penalty):
        """Try dropping up to ``drop_budget`` robots and keep the cheapest feasible mode.

        This is the "temporarily exclude a robot for this push task" fallback: when no
        assignment exists for the whole team, a (N-k)-robot mode may still be feasible
        (small faces / tight pusher spacing).  The returned mode carries only the active
        robots' contact points; the excluded robots hold position for this task.
        """
        from itertools import combinations

        team = [int(r.num_id) for r in self.robots if r.num_id >= 0]
        best = None  # (loss, points, normals, active, dropped)
        for k in range(1, max(1, int(drop_budget)) + 1):
            for drop in combinations(team, k):
                allow = [t for t in team if t not in drop]
                if not allow:
                    continue
                assignment = self._assign_contacts_sequential(
                    robot_cand_cps=robot_cand_cps,
                    res_push_force=np.array(target_force, dtype=float),
                    min_dist=min_dist,
                    allow_robots=allow,
                )
                if assignment is None:
                    assignment = self._assign_contacts_backtracking(
                        robot_cand_cps=robot_cand_cps,
                        target_force=target_force,
                        min_dist=min_dist,
                        budget=budget,
                        allow_robots=allow,
                    )
                if assignment is None:
                    continue
                pts, nls = assignment
                mode = Mode(robot_num=len(pts), contact_points=pts, contact_normals=nls)
                if (not self._mode_contact_geometry_ok(mode, min_dist)
                        or self._check_disabled(mode)
                        or not self._collision_ok(mode)):
                    continue
                info = self.cost_estimator.run_estimate(self._last_push_vel, mode=mode)
                loss = float(info["total_loss"]) + float(penalty) * len(drop)
                if best is None or loss < best[0]:
                    best = (loss, pts, nls, list(allow), list(drop))
        if best is None:
            return None, None
        _, pts, nls, active, dropped = best
        return (pts, nls), {"active": active, "dropped": dropped,
                            "penalty": float(penalty) * len(dropped)}

    # ----------------- 核心：贪心优化尝试改进当前模式 -----------------
    def _greedy_optimization(self, push_vel: np.ndarray, print_info = False) -> Tuple[Mode, float, Dict]:
        self._last_push_vel = np.asarray(push_vel, dtype=float)
        """
        返回：best_mode, best_loss, trans_cost(此处为0), best_loss_info
        """
        MAX_SEARCH_PER_START = getattr(self.config, "greedy_opt_max_iter", 200)
        MIN_DIST_TOL = float(getattr(self.config, "mode_gen_min_robot_dist", 0.1))
    
        start_time = time.time()
        # --- 候选接触点（含法向） ---
        robot_cand_cps = self._prepare_cand_cps(push_vel)
        '''
        robot_cand_cps[rid] = [
            {
                "point_local": np.ndarray(2,),
                "normal_local": np.ndarray(2,),
                # ... 其他字段
            },
            ...
        ]
        '''
        # 推动方向对应的广义“摩擦需求”
        friction = self.cost_estimator.calc_friction(push_vel)  # (fx, fy, m)
        res_push_force = -friction

        # 初始解：先按原语义做顺序贪心；失败则回退到有界回溯（换序 + 候选回退）
        target_force = np.array(res_push_force, dtype=float)
        assignment = self._assign_contacts_sequential(
            robot_cand_cps=robot_cand_cps,
            res_push_force=np.array(res_push_force, dtype=float),
            min_dist=MIN_DIST_TOL,
        )
        if assignment is None and bool(getattr(self.config, "mode_gen_assignment_backtrack", True)):
            budget = int(getattr(self.config, "mode_gen_backtrack_budget", 2000))
            assignment = self._assign_contacts_backtracking(
                robot_cand_cps=robot_cand_cps,
                target_force=target_force,
                min_dist=MIN_DIST_TOL,
                budget=budget,
            )
            if assignment is not None:
                _diag(f"backtracking rescued full-team mode "
                      f"(obs={self.target_obs.num_id}, rob_num={self.rob_num}, budget={budget})")
        subset_used = None
        if assignment is None and bool(getattr(self.config, "mode_gen_subset_fallback", True)):
            assignment, subset_used = self._assign_contacts_subset_fallback(
                robot_cand_cps=robot_cand_cps,
                target_force=target_force,
                min_dist=MIN_DIST_TOL,
                budget=int(getattr(self.config, "mode_gen_backtrack_budget", 2000)),
                drop_budget=int(getattr(self.config, "mode_gen_subset_max_drop", 1)),
                penalty=float(getattr(self.config, "mode_gen_subset_penalty", 0.5)),
            )
            if assignment is not None:
                _diag(f"subset fallback: active={subset_used['active']} "
                      f"dropped={subset_used['dropped']} penalty={subset_used['penalty']:.3f} "
                      f"(obs={self.target_obs.num_id}, rob_num={self.rob_num})")
        if assignment is None:
            _diag(f"no assignment for obs={self.target_obs.num_id} "
                  f"(rob_num={self.rob_num}, min_dist={MIN_DIST_TOL}, subset fallback exhausted)")
            return None, INF, {}
        selected_points, selected_normals = assignment

        # 当前模式（包含法向）
        opt_mode = Mode(
            robot_num=self.rob_num,
            contact_points=selected_points,
            contact_normals=selected_normals
        )
        if subset_used is not None:
            # Subset ("temporarily drop a robot") mode: record participants so the
            # execution/prediction controllers can command the rest to hold.
            opt_mode.robot_num = len(selected_points)
            opt_mode.active_robot_ids = list(selected_points.keys())
            opt_mode.dropped_robot_ids = list(subset_used["dropped"])

        if (
            not self._mode_contact_geometry_ok(opt_mode, MIN_DIST_TOL)
            or self._check_disabled(opt_mode)
            or not self._collision_ok(opt_mode)
        ):
            _diag(f"greedy fail: assembled mode rejected by post-check "
                  f"(geometry/disabled/collision) obs={self.target_obs.num_id} "
                  f"contacts={list(opt_mode.contact_points.keys())}")
            return None, INF, {}

        # 评估
        opt_loss_info = self.cost_estimator.run_estimate(push_vel, mode=opt_mode)
        opt_loss = float(opt_loss_info["total_loss"])
        est_cnt = 0

        # 局部改进：逐机器人尝试替换为不冲突且更优的候选（点+法向）
        improved = True
        active_ids = list(selected_points.keys())
        while improved and est_cnt < MAX_SEARCH_PER_START:
            improved = False
            for rid in active_ids:
                r = self.robot_dict[rid]
                cands = robot_cand_cps.get(rid, [])
                #=================================================
                # 距离过滤，避免与其他已选接触点过近
                #=================================================
                filtered: List[Tuple[np.ndarray, np.ndarray]] = []
                for c in cands:
                    pl = np.asarray(c["point_local"], dtype=float)
                    nl = np.asarray(c["normal_local"], dtype=float)
                    if self._candidate_ok_wrt_selected_exact(
                        r,
                        pl,
                        nl,
                        {k: v for k, v in selected_points.items() if k != rid},
                        {k: v for k, v in selected_normals.items() if k != rid},
                        MIN_DIST_TOL,
                    ):
                        filtered.append((pl, nl))

                # 尝试替换
                for cand_pl, cand_nl in filtered:
                    new_points = deepcopy(selected_points)
                    new_normals = deepcopy(selected_normals)
                    new_points[rid] = cand_pl
                    new_normals[rid] = cand_nl

                    new_mode = Mode(
                        robot_num=self.rob_num,
                        contact_points=new_points,
                        contact_normals=new_normals
                    )
                    # 禁用/碰撞检查
                    if not self._mode_contact_geometry_ok(new_mode, MIN_DIST_TOL):
                        continue
                    if self._check_disabled(new_mode):
                        continue
                    if not self._collision_ok(new_mode):
                        continue
                    # 评估
                    loss_lb = self.cost_estimator.cost_lower_bound(push_vel, new_mode)
                    if loss_lb >= opt_loss:
                        continue
                    loss_info = self.cost_estimator.run_estimate(push_vel, mode=new_mode)
                    hyb_loss = float(loss_info["total_loss"])
                    est_cnt += 1

                    if hyb_loss < opt_loss:
                        opt_loss = hyb_loss
                        opt_loss_info = loss_info
                        selected_points = new_points
                        selected_normals = new_normals
                        opt_mode = new_mode
                        improved = True

                    if est_cnt >= MAX_SEARCH_PER_START:
                        break
                if est_cnt >= MAX_SEARCH_PER_START:
                    break
        if print_info:
            print(  f"[ModeGen] Process {os.getpid()} finished in {time.time()-start_time:.2f} sec, "
                    f"{est_cnt} estimations, best loss {opt_loss:.3f}.")
        
        return opt_mode, opt_loss, opt_loss_info

    def _extract_table_mode_record(
        self,
        entry: Any,
    ) -> Tuple[Optional[Dict[int, np.ndarray]], Optional[Dict[int, np.ndarray]], float]:
        """Normalize one ModeTable query result into int-keyed numpy maps.

        The historical mode table mostly stores records as
        ``{"point_local": ..., "normals": ..., "mode_loss": ...}``, while
        some intermediate versions wrapped this payload inside ``{"mode": ...}``.
        This helper accepts both formats and also tolerates a Mode object.
        """
        if entry is None:
            return None, None, INF

        stored_loss = INF
        raw = entry
        if isinstance(entry, dict):
            stored_loss = float(entry.get("mode_loss", INF))
            raw = entry.get("mode", entry)

        if isinstance(raw, Mode):
            p_src = raw.contact_points
            n_src = raw.contact_normals
        elif isinstance(raw, dict):
            stored_loss = float(raw.get("mode_loss", stored_loss))
            p_src = raw.get("point_local", raw.get("contact_points", None))
            n_src = raw.get("normals", raw.get("normal_local", raw.get("contact_normals", None)))
        else:
            return None, None, stored_loss

        if p_src is None or n_src is None:
            return None, None, stored_loss

        try:
            p_locals = {int(k): np.asarray(v, dtype=float) for k, v in p_src.items()}
            n_locals = {int(k): np.asarray(v, dtype=float) for k, v in n_src.items()}
        except Exception:
            return None, None, stored_loss

        if set(p_locals.keys()) != set(n_locals.keys()):
            return None, None, stored_loss
        return p_locals, n_locals, stored_loss

    def _match_reachable_contact_candidate(
        self,
        rid: int,
        p_des: np.ndarray,
        n_des: np.ndarray,
        cands: List[Dict],
    ) -> Optional[Dict]:
        """Find the reachable candidate that represents the table contact.

        Reachability is checked on both contact location and normal direction.
        Returning the actual reachable candidate avoids reusing stale numpy/list
        values from the table when the candidate set has been recomputed.
        """
        if not cands:
            return None

        pos_tol = float(getattr(self.config, "table_query_cp_match_tol", 1e-2))
        normal_cos_tol = float(getattr(self.config, "table_query_normal_match_cos", 0.75))
        p_des = np.asarray(p_des, dtype=float)
        n_des = np.asarray(n_des, dtype=float)

        best_cand = None
        best_score = -INF
        for c in cands:
            if "point_local" not in c or "normal_local" not in c:
                continue
            pl = np.asarray(c["point_local"], dtype=float)
            nl = np.asarray(c["normal_local"], dtype=float)
            pos_err = float(np.linalg.norm(pl - p_des))
            if pos_err > pos_tol:
                continue
            normal_cos = _cos(nl, n_des)
            if normal_cos < normal_cos_tol:
                continue
            score = normal_cos - pos_err / max(pos_tol, 1e-9)
            if score > best_score:
                best_score = score
                best_cand = c
        return best_cand

    def _rank_table_repair_candidates(
        self,
        rid: int,
        p_des: np.ndarray,
        n_des: np.ndarray,
        cands: List[Dict],
        selected_points: Dict[int, np.ndarray],
        selected_normals: Dict[int, np.ndarray],
        min_dist: float,
    ) -> List[Tuple[float, Dict]]:
        """Rank reachable substitutes for one infeasible table contact."""
        if not cands:
            return []

        robot = self.robot_dict[rid]
        p_des = np.asarray(p_des, dtype=float)
        n_des = np.asarray(n_des, dtype=float)
        g_target = _gen_force_vec(p_des, n_des)
        dist_scale = max(1.0, float(np.linalg.norm(p_des)))

        ranked: List[Tuple[float, Dict]] = []
        for c in cands:
            if "point_local" not in c or "normal_local" not in c:
                continue
            pl = np.asarray(c["point_local"], dtype=float)
            nl = np.asarray(c["normal_local"], dtype=float)
            if not self._candidate_ok_wrt_selected_exact(
                robot,
                pl,
                nl,
                selected_points,
                selected_normals,
                min_dist,
            ):
                continue

            force_sim = _cos(_gen_force_vec(pl, nl), g_target)
            normal_sim = _cos(nl, n_des)
            pos_penalty = float(np.linalg.norm(pl - p_des)) / dist_scale
            score = 2.0 * force_sim + 0.25 * normal_sim - 0.05 * pos_penalty
            ranked.append((score, c))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return ranked

    def _build_table_seed_mode(
        self,
        p_locals: Dict[int, np.ndarray],
        n_locals: Dict[int, np.ndarray],
        robot_cand_cps: Dict[int, List[Dict]],
        min_dist: float,
    ) -> Tuple[Optional[Mode], int, str]:
        """Build a feasible seed mode from one queried table record.

        If a table contact is still reachable and mutually compatible, it is
        kept. Otherwise, the nearest force-equivalent reachable contact is used
        as a seed; a later lightweight greedy pass then optimizes the repaired
        seed with the actual cost estimator.
        """
        selected_points: Dict[int, np.ndarray] = {}
        selected_normals: Dict[int, np.ndarray] = {}
        repaired_cnt = 0

        robot_ids = sorted([r.num_id for r in self.robots if r.num_id >= 0])
        for rid in robot_ids:
            if rid not in p_locals or rid not in n_locals or rid not in self.robot_dict:
                return None, repaired_cnt, f"missing robot {rid} in table record"

            p_des = np.asarray(p_locals[rid], dtype=float)
            n_des = np.asarray(n_locals[rid], dtype=float)
            cands = robot_cand_cps.get(rid, []) or []
            robot = self.robot_dict[rid]

            matched = self._match_reachable_contact_candidate(rid, p_des, n_des, cands)
            if matched is not None:
                pl = np.asarray(matched["point_local"], dtype=float)
                nl = np.asarray(matched["normal_local"], dtype=float)
                if self._candidate_ok_wrt_selected_exact(
                    robot,
                    pl,
                    nl,
                    selected_points,
                    selected_normals,
                    min_dist,
                ):
                    selected_points[rid] = pl
                    selected_normals[rid] = nl
                    continue

            # The table contact is unreachable or conflicts with already fixed
            # pushers. Use the best reachable force-equivalent candidate only as
            # a seed; the lightweight greedy repair below is responsible for
            # final cost-based optimization.
            ranked = self._rank_table_repair_candidates(
                rid,
                p_des,
                n_des,
                cands,
                selected_points,
                selected_normals,
                min_dist,
            )
            if not ranked:
                return None, repaired_cnt, f"no reachable substitute for robot {rid}"

            _, best_cand = ranked[0]
            selected_points[rid] = np.asarray(best_cand["point_local"], dtype=float)
            selected_normals[rid] = np.asarray(best_cand["normal_local"], dtype=float)
            repaired_cnt += 1

        seed_mode = Mode(
            robot_num=self.rob_num,
            contact_points=selected_points,
            contact_normals=selected_normals,
        )
        if not self._mode_contact_geometry_ok(seed_mode, min_dist):
            return None, repaired_cnt, "seed geometry invalid"
        if self._check_disabled(seed_mode):
            return None, repaired_cnt, "seed disabled"
        if not self._collision_ok(seed_mode):
            return None, repaired_cnt, "seed collision invalid"
        return seed_mode, repaired_cnt, "ok"

    def _light_greedy_repair_from_seed(
        self,
        push_vel: np.ndarray,
        seed_mode: Mode,
        robot_cand_cps: Dict[int, List[Dict]],
        max_iter: Optional[int] = None,
    ) -> Tuple[Optional[Mode], float, Dict]:
        """Run a low-budget local greedy search initialized by a table seed."""
        if seed_mode is None:
            return None, INF, {}

        min_dist = float(getattr(self.config, "mode_gen_min_robot_dist", 0.1))
        if (
            not self._mode_contact_geometry_ok(seed_mode, min_dist)
            or self._check_disabled(seed_mode)
            or not self._collision_ok(seed_mode)
        ):
            return None, INF, {}

        if max_iter is None:
            default_iter = max(8, min(40, int(getattr(self.config, "greedy_opt_max_iter", 200) // 5)))
            max_iter = int(getattr(self.config, "table_query_repair_max_iter", default_iter))
        max_iter = max(0, int(max_iter))
        top_m = max(1, int(getattr(self.config, "table_query_repair_top_m", 12)))
        improve_tol = float(getattr(self.config, "table_query_repair_improve_tol", 1e-6))

        selected_points = deepcopy(seed_mode.contact_points)
        selected_normals = deepcopy(seed_mode.contact_normals)
        opt_mode = Mode(
            robot_num=self.rob_num,
            contact_points=deepcopy(selected_points),
            contact_normals=deepcopy(selected_normals),
        )
        opt_loss_info = self.cost_estimator.run_estimate(push_vel, mode=opt_mode)
        opt_loss = float(opt_loss_info["total_loss"])

        if max_iter == 0:
            return opt_mode, opt_loss, opt_loss_info

        target_force = -self.cost_estimator.calc_friction(push_vel)
        est_cnt = 0
        improved = True

        while improved and est_cnt < max_iter:
            improved = False
            for r in self.robots:
                rid = r.num_id
                if rid < 0:
                    continue
                cands = robot_cand_cps.get(rid, []) or []
                other_points = {k: v for k, v in selected_points.items() if k != rid}
                other_normals = {k: v for k, v in selected_normals.items() if k != rid}

                ranked: List[Tuple[float, np.ndarray, np.ndarray]] = []
                for c in cands:
                    if "point_local" not in c or "normal_local" not in c:
                        continue
                    pl = np.asarray(c["point_local"], dtype=float)
                    nl = np.asarray(c["normal_local"], dtype=float)
                    if rid in selected_points:
                        same_point = np.linalg.norm(pl - np.asarray(selected_points[rid], dtype=float)) < 1e-6
                        same_normal = _cos(nl, np.asarray(selected_normals[rid], dtype=float)) > 1.0 - 1e-6
                        if same_point and same_normal:
                            continue
                    if not self._candidate_ok_wrt_selected_exact(
                        r,
                        pl,
                        nl,
                        other_points,
                        other_normals,
                        min_dist,
                    ):
                        continue
                    score = _cos(_gen_force_vec(pl, nl), target_force)
                    ranked.append((score, pl, nl))

                ranked.sort(key=lambda x: x[0], reverse=True)

                for _, cand_pl, cand_nl in ranked[:top_m]:
                    new_points = deepcopy(selected_points)
                    new_normals = deepcopy(selected_normals)
                    new_points[rid] = cand_pl
                    new_normals[rid] = cand_nl
                    new_mode = Mode(
                        robot_num=self.rob_num,
                        contact_points=new_points,
                        contact_normals=new_normals,
                    )
                    if not self._mode_contact_geometry_ok(new_mode, min_dist):
                        continue
                    if self._check_disabled(new_mode):
                        continue
                    if not self._collision_ok(new_mode):
                        continue

                    loss_lb = self.cost_estimator.cost_lower_bound(push_vel, new_mode)
                    if float(loss_lb) >= opt_loss - improve_tol:
                        continue

                    loss_info = self.cost_estimator.run_estimate(push_vel, mode=new_mode)
                    hyb_loss = float(loss_info["total_loss"])
                    est_cnt += 1

                    if hyb_loss < opt_loss - improve_tol:
                        opt_loss = hyb_loss
                        opt_loss_info = loss_info
                        selected_points = new_points
                        selected_normals = new_normals
                        opt_mode = new_mode
                        improved = True

                    if est_cnt >= max_iter:
                        break
                if est_cnt >= max_iter:
                    break

        if isinstance(opt_loss_info, dict):
            opt_loss_info = dict(opt_loss_info)
            opt_loss_info["table_query_repair_estimations"] = est_cnt
            opt_loss_info["table_query_repair_max_iter"] = max_iter
        return opt_mode, opt_loss, opt_loss_info

    def _limited_greedy_fallback(self, push_vel: np.ndarray, max_iter: int) -> Tuple[Optional[Mode], float, Dict]:
        """Run scratch greedy with a temporary low iteration budget."""
        old_has_attr = hasattr(self.config, "greedy_opt_max_iter")
        old_value = getattr(self.config, "greedy_opt_max_iter", None)
        try:
            setattr(self.config, "greedy_opt_max_iter", int(max_iter))
            return self._greedy_optimization(push_vel=push_vel)
        finally:
            if old_has_attr:
                setattr(self.config, "greedy_opt_max_iter", old_value)
            else:
                try:
                    delattr(self.config, "greedy_opt_max_iter")
                except AttributeError:
                    pass

    def _table_query(self, push_vel: np.ndarray) -> Tuple[Optional[Mode], float, Dict]:
        """
        Query the nearest mode-table entries and return the best feasible mode.

        Main changes from the original implementation:
        1. ``table_query_k`` is used end-to-end: all returned table candidates
           are repaired/evaluated and the lowest estimated loss is selected.
        2. If a table contact is not reachable or conflicts with another
           selected pusher, a low-budget greedy repair is launched from the
           repaired table seed instead of accepting a purely similarity-based
           point replacement.
        """
        query_k = max(1, int(getattr(self.config, "table_query_k", 1)))
        best_modes, matched_dirs = self.mode_table.query_best_matching_modes(
            direction=push_vel,
            query_num=query_k,
        )
        if not best_modes:
            return None, float("inf"), {}

        min_dist = float(getattr(self.config, "mode_gen_min_robot_dist", 0.1))
        default_repair_iter = max(8, min(40, int(getattr(self.config, "greedy_opt_max_iter", 200) // 5)))
        repair_max_iter = int(getattr(self.config, "table_query_repair_max_iter", default_repair_iter))
        refine_feasible = bool(getattr(self.config, "table_query_refine_feasible", False))
        fallback_light_greedy = bool(getattr(self.config, "table_query_fallback_light_greedy", True))

        robot_cand_cps = self._prepare_cand_cps(push_vel)
        evaluated: List[Tuple[float, Mode, Dict]] = []
        failure_reasons: List[str] = []

        for rank, entry in enumerate(best_modes):
            p_locals, n_locals, stored_loss = self._extract_table_mode_record(entry)
            if p_locals is None or n_locals is None:
                failure_reasons.append(f"rank {rank}: malformed table record")
                continue

            seed_mode, repaired_cnt, reason = self._build_table_seed_mode(
                p_locals=p_locals,
                n_locals=n_locals,
                robot_cand_cps=robot_cand_cps,
                min_dist=min_dist,
            )
            if seed_mode is None:
                failure_reasons.append(f"rank {rank}: {reason}")
                continue

            # Fully feasible table modes stay fast: evaluate once. Repaired
            # seeds invoke the lightweight greedy pass to recover usability and
            # reduce the estimator loss under the current reachable set.
            if repaired_cnt > 0 or refine_feasible:
                mode, loss, loss_info = self._light_greedy_repair_from_seed(
                    push_vel=push_vel,
                    seed_mode=seed_mode,
                    robot_cand_cps=robot_cand_cps,
                    max_iter=repair_max_iter,
                )
                source = "table_repaired_light_greedy" if repaired_cnt > 0 else "table_refined_light_greedy"
            else:
                mode = seed_mode
                loss_info = self.cost_estimator.run_estimate(push_vel, mode=mode)
                loss = float(loss_info["total_loss"])
                source = "table_direct"

            if mode is None:
                failure_reasons.append(f"rank {rank}: repair failed")
                continue
            if (
                not self._mode_contact_geometry_ok(mode, min_dist)
                or self._check_disabled(mode)
                or not self._collision_ok(mode)
            ):
                failure_reasons.append(f"rank {rank}: post-check failed")
                continue

            if isinstance(loss_info, dict):
                loss_info = dict(loss_info)
                loss_info["table_query_source"] = source
                loss_info["table_query_rank"] = rank
                loss_info["table_query_k"] = query_k
                loss_info["table_query_repaired_contacts"] = repaired_cnt
                loss_info["table_query_stored_loss"] = stored_loss
                if matched_dirs is not None and rank < len(matched_dirs):
                    loss_info["table_query_matched_direction"] = np.asarray(matched_dirs[rank], dtype=float).tolist()

            evaluated.append((float(loss), mode, loss_info))

        if evaluated:
            evaluated.sort(key=lambda x: x[0])
            return evaluated[0][1], evaluated[0][0], evaluated[0][2]

        # Last-resort behavior remains bounded: this is only used when a table
        # hit exists but all queried records fail under the current reachable set.
        if fallback_light_greedy and repair_max_iter > 0:
            mode, loss, loss_info = self._limited_greedy_fallback(push_vel, repair_max_iter)
            if mode is not None:
                if isinstance(loss_info, dict):
                    loss_info = dict(loss_info)
                    loss_info["table_query_source"] = "table_failed_light_greedy_fallback"
                    loss_info["table_query_k"] = query_k
                    loss_info["table_query_failures"] = failure_reasons
                return mode, loss, loss_info

        return None, float("inf"), {"table_query_failures": failure_reasons}

    # --------------- PUBLIC API ：为给定目标推动方向生成接触模式 ---------------
    def plan(self,
             push_velocity_loc: np.ndarray = None,
             push_velocity_world: np.ndarray = None,
             disabled_mode_list: Optional[List[Mode]] = None
             ) -> Tuple[List[Mode], List[float]]:
        
        # 检查机器人的reachable_contact_points是否准备好
        reachable_cps_prepared = True
        for robot in self.robots:
            if robot.reachable_contact_points is None:
                reachable_cps_prepared = False
        if not reachable_cps_prepared:
            print("[ModeGen] Warning: robots' reachable_contact_points not prepared, running preparation...")
            find_reachable_contact_points(self.group.robot_list,
                                          self.group.obstacle_list, 
                                          self.config)

        assert (push_velocity_loc is not None) ^ (push_velocity_world is not None), \
            "请指定 pvel_loc 或 push_velocity_world 中的一个（另一个留 None）"      
        
        if push_velocity_world is not None:
            R = rotate_mat(self.target_obs.yaw())
            v_local = R.T @ np.array([push_velocity_world[0], push_velocity_world[1]], dtype=float)
            push_vel = np.array([v_local[0], v_local[1], push_velocity_world[2]], dtype=float)
        else:
            push_vel = np.array(push_velocity_loc, dtype=float)

        self.disabled_mode_list = disabled_mode_list or []

        modes: List[Mode] = []
        costs: List[float] = []

        # 1) 表查（快）
        if self.config.mode_gen_via_table_query:
            m_tb, c_tb, info_tb = profiler_wrapper(
                self._table_query, 
                open_profiler=False,
                push_vel=push_vel, 
            )

            if (
                m_tb is not None
                and self._mode_contact_geometry_ok(m_tb)
                and not self._check_disabled(m_tb)
                and self._collision_ok(m_tb)
            ):
                modes.append(m_tb)
                costs.append(c_tb)

        # 2) 贪心（稳）
        if self.config.mode_gen_via_greedy_opt:
            m_gr, c_gr, info_gr = self._greedy_optimization(push_vel=push_vel)
            if (
                m_gr is not None
                and self._mode_contact_geometry_ok(m_gr)
                and not self._check_disabled(m_gr)
                and self._collision_ok(m_gr)
            ):
                modes.append(m_gr)
                costs.append(c_gr)

        if not modes:
            _diag(f"plan(): no mode for obs={self.target_obs.num_id} rob_num={self.rob_num} "
                  f"(table_query={self.config.mode_gen_via_table_query}, "
                  f"greedy={self.config.mode_gen_via_greedy_opt})")
            return [], []

        # 3) 排序去重（按 cost）
        zipped = list(zip(costs, modes))
        zipped.sort(key=lambda x: x[0])
        # 可选：按 contact_points 去重
        uniq = []
        seen = set()
        for c, m in zipped:
            key = tuple(sorted((rid, tuple(np.round(np.asarray(p), 6))) 
                               for rid, p in m.contact_points.items()))
            if key in seen: 
                continue
            seen.add(key)
            uniq.append((c, m))

        costs_out, modes_out = zip(*uniq)
        return list(modes_out), list(costs_out)

import os
import sys
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mc

# ========= 你的工程依赖 =========
sys.path.append(os.getcwd())

from src.env.env import EnvBase
from src.env.object import Robot, Obstacle
from src.policy.clutterbreaker_policy.common_structures import Mode, TaskObjectGroup
from src.config.policy_config.clutterbreaker_config import ClutterBreaker_Config
from src.policy.clutterbreaker_policy.collaborative_pusher.cost_estimator import CostEstimator

# 你刚写的类/函数
from src.policy.clutterbreaker_policy.collaborative_pusher.mode_generator import ModeGenerator
from src.policy.clutterbreaker_policy.collaborative_pusher.reachable_contact_points import find_reachable_contact_points


# ========= 小工具 =========
def _rot2(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s],[s, c]], dtype=float)

def _shape_to_world_edges(obstacle: Obstacle):
    """将 obstacle 的多边形边（物体系）转到世界系，供可视化"""
    shape = obstacle.shape_cmbf  # 物体系几何
    verts = [np.asarray(v, dtype=float) for v in shape.dense_vertex_list]
    R = _rot2(obstacle.yaw())
    t = np.asarray(obstacle.cm_position2d(), dtype=float)
    verts_w = [R @ v + t for v in verts]
    edges = []
    n = len(verts_w)
    for i in range(n):
        edges.append([verts_w[i], verts_w[(i+1) % n]])
    return edges

def _draw_env(ax, obstacles, robots, highlight=None):
    """画障碍（黑边）与机器人位置（橙点）"""
    all_edges = []
    for obs in obstacles:
        all_edges += _shape_to_world_edges(obs)
    if all_edges:
        ax.add_collection(mc.LineCollection(all_edges, colors="#444", linewidths=1.6, zorder=1))

    # 机器人
    for r in robots:
        p = r.cm_position2d()
        ax.plot([p[0]],[p[1]], "o", color="#ff7f0e", ms=6, zorder=4)
        ax.text(p[0], p[1], f" r{r.num_id}", color="#ff7f0e", fontsize=9,
                va="bottom", ha="left", zorder=5)

    # 高亮目标
    if highlight is not None:
        ed = _shape_to_world_edges(highlight)
        if ed:
            ax.add_collection(mc.LineCollection(ed, colors="#0077ff", linewidths=2.2,
                                                linestyles="solid", alpha=0.9, zorder=2))

def _draw_mode(ax, target_obs: Obstacle, mode: Mode, color="#d62728"):
    """画出 Mode 中每个机器人的接触点(世界系)与法向（物体系计算后转世界）"""
    R = _rot2(target_obs.yaw())
    t = np.asarray(target_obs.cm_position2d(), dtype=float)

    # 用“最近边”法补一补接触法/切向
    shape = target_obs.shape_cmbf
    picks_world = []
    arrows = []

    for rid, p_local in mode.contact_points.items():
        p_local = np.asarray(p_local, dtype=float)
        p_world = R @ p_local + t
        n_loc, tau_loc = shape.calc_contact_vector_via_nearest_contact_point(p_local, return_edge=False)
        if n_loc is None:  # 兜底
            tau_loc = np.array([1.0, 0.0], dtype=float)
            n_loc = np.array([-tau_loc[1], tau_loc[0]], dtype=float)
        n_world = R @ n_loc

        picks_world.append(p_world)
        arrows.append((p_world, p_world + 0.3 * n_world))  # 法向箭头

        ax.plot([p_world[0]], [p_world[1]], "o", color=color, ms=6, zorder=6)
        ax.text(p_world[0], p_world[1], f"  cp(r{rid})", color=color, fontsize=9,
                va="center", ha="left", zorder=7)
        ax.arrow(p_world[0], p_world[1], 0.3*n_world[0], 0.3*n_world[1],
                 head_width=0.07, head_length=0.12, fc=color, ec=color, zorder=7)

import numpy as np
from matplotlib.patches import Polygon as MplPolygon

def _draw_push_direction(ax, target_obs: Obstacle, push_vel: np.ndarray):
    """把 (vx, vy, omega) 画在目标质心处；角速度用一段圆弧表示并在末端加箭头"""
    c = np.asarray(target_obs.cm_position2d(), dtype=float)
    v = np.asarray(push_vel[:2], dtype=float)
    w = float(push_vel[2])

    # 平动箭头
    ax.arrow(c[0], c[1], v[0], v[1],
             head_width=0.15, head_length=0.25,
             fc="#00aa55", ec="#00aa55", zorder=5)
    ax.text(c[0] + v[0], c[1] + v[1] + 0.1,
            f"  push v=({v[0]:.2f},{v[1]:.2f})",
            color="#00aa55", fontsize=9, va="bottom", ha="left", zorder=5)

    # 角速度弧线
    radius = 1.0
    if abs(w) > 1e-6:
        ts = np.linspace(0.0, w, 20)
        arc = np.stack([c[0] + radius*np.cos(ts), c[1] + radius*np.sin(ts)], axis=1)
        ax.plot(arc[:, 0], arc[:, 1], "-", color="#00aa55", lw=2.0, zorder=5)

        # 角速度文字
        ax.text(c[0] + radius, c[1],
                f" ω={w:.2f}",
                color="#00aa55", fontsize=9, va="center", ha="left")

        # —— 在弧线末端添加三角箭头（顺着弧线的切向）——
        theta = w  # 末端角度
        p_end = np.array([c[0] + radius*np.cos(theta),
                          c[1] + radius*np.sin(theta)], dtype=float)

        # 弧线的切向量：d/dθ [cosθ, sinθ] = [-sinθ, cosθ]
        # 正 w 逆时针、负 w 顺时针；沿着参数增长方向给箭头方向
        sign = 1.0 if w > 0 else -1.0
        t_vec = sign * np.array([-np.sin(theta), np.cos(theta)], dtype=float)
        t_hat = t_vec / (np.linalg.norm(t_vec) + 1e-12)
        n_hat = np.array([-t_hat[1], t_hat[0]], dtype=float)

        # 三角箭头的尺寸
        L = 0.2  # 箭头长度
        B = 0.15  # 箭头底边宽

        base_center = p_end - L * t_hat
        p_left  = base_center + 0.5 * B * n_hat
        p_right = base_center - 0.5 * B * n_hat
        tri = np.vstack([p_end, p_left, p_right])

        ax.add_patch(MplPolygon(tri, closed=True,
                                facecolor="#00aa55", edgecolor="#00aa55", zorder=6))
    else:
        # w≈0 时不画弧线，仅标注数值
        ax.text(c[0] + radius, c[1], " ω≈0",
                color="#00aa55", fontsize=9, va="center", ha="left")

def _reset_ax(ax):
    ax.cla()

# ========= 一个极简 Env 容器 =========
class _MiniEnv:
    """只需要 robot_list / obstacle_list；其它不动"""
    def __init__(self, robots, obstacles):
        self.robot_list = robots
        self.obstacle_list = obstacles
from src.env.scenarios.base_scenario import BaseScenario

# ========= 主测试 =========
def run_mode_generator_demo(
    scenario_class=None,
    scenario_kwargs={},
    policy_cfg=None,
    seeds = list(range(100, 200)),
    draw=True
):
    plt.ion()
    fig, ax = plt.subplots(figsize=(9, 7))
    # 1) 造场景
    scenario:BaseScenario = scenario_class(**scenario_kwargs)
    robots = scenario.create_robots()
    obstacles = scenario.create_obstacles()  
    # 2) 配置参数
    cfg = policy_cfg or ClutterBreaker_Config()
    cfg.mode_table_file_name =  f"{scenario.name}_mode_table.json"

    # 2) 构 Env，并计算每个机器人的 reachable contact points
    env = _MiniEnv(robots=robots, obstacles=obstacles)
    find_reachable_contact_points(env.robot_list, env.obstacle_list, cfg)  # 结果写回 robot.reachable_contact_points

    for seed in seeds:

        random.seed(seed)
        np.random.seed(seed)

        # 3) 随机选“一个真实障碍物”作为目标（num_id >= 0）
        real_obstacles = [o for o in obstacles if o.num_id >= 0]
        assert len(real_obstacles) > 0, "没有可用的真实障碍物用于测试。"
        target_obs = random.choice(real_obstacles)

        # 4) 构 TaskObjectGroup（按你项目的字段名适配）
        robot_dict = {r.num_id: r for r in robots if r.num_id >= 0}
        group = TaskObjectGroup(target_obs=target_obs,
                                obstacle_dict={o.num_id: o for o in obstacles},
                                robot_dict=robot_dict)
        
        # 5) 配置 + 生成 ModeGenerator
        # 可按需设置 cfg.w_mode, cfg.w_trans, cfg.max_search_per_start, cfg.min_cp_distance 等
        mg = ModeGenerator(group=group, config=cfg)

        # 6) 随机生成一个“推动方向”（vx, vy, omega）
        vxy = np.random.uniform(-1.0, 1.0, size=2)
        if np.linalg.norm(vxy) < 1e-6:
            vxy = np.array([1.0, 0.0])
        vxy = vxy / np.linalg.norm(vxy)
        omega = np.random.uniform(-0.8, 0.8)
        push_vel = np.array([vxy[0], vxy[1], omega], dtype=float)

        # 7) 将推动方向变换到局部坐标系
        R_t = _rot2(-target_obs.yaw())  # 世界系到物体系
        vxy_local = R_t @ vxy
        pvel_loc = np.array([vxy_local[0], vxy_local[1], omega], dtype=float)
        pvel_loc = pvel_loc / np.linalg.norm(pvel_loc)  # 归一化
        
        # 7) 运行规划
        start_time = time.time()
        modes, costs = mg.plan(push_velocity_loc=pvel_loc)
        print(f"[ModeGen] 规划耗时 {time.time() - start_time:.3f} 秒")
        if not modes:
            print("[ModeGen] 未找到模式（可能是可达接触点为空/冲突过滤导致）。")
            return

        opt_mode = modes[0]
        print(f"[ModeGen] 成功得到模式，cost={costs[0]:.3f}, 机器人数={len(opt_mode.contact_points)}")
        print(opt_mode)
        
        # 8) 可视化
        if draw:
            x0, y0, x1, y1 = scenario.world_aabb
            _reset_ax(ax)
            _draw_env(ax, obstacles, robots, highlight=target_obs)
            _draw_mode(ax, target_obs, opt_mode, color="#d62728")
            _draw_push_direction(ax, target_obs, push_vel)

            ax.set_aspect("equal", adjustable="box")
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            ax.set_title("Greedy contact-mode for a random push direction")
            plt.show()
            plt.pause(0.1)

if __name__ == "__main__":
    if False:
        scenario_kwargs = {
            "seeds" : [43],
            "n_robots" : 2,
            "n_shapes" : 10,
            "world_aabb" : [0, 0, 8, 5], # x0, y0, x1, y1
        }
        from src.env.scenarios.scenario_random import Scenario
        seeds = list(range(000, 200))
    if True:
        scenario_kwargs = {}
        from src.env.scenarios.scenario_5x5_4obs_2rob import Scenario

    cfg = ClutterBreaker_Config(
            mode_gen_via_greedy_opt=True,
            mode_gen_via_table_query=False,
        )
    run_mode_generator_demo(
        scenario_class=Scenario,
        scenario_kwargs=scenario_kwargs,
        policy_cfg=cfg,
    )

