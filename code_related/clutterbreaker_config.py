import numpy as np
from typing import Dict, Optional
from src.config.auto_config import autoconfig
from src.config.policy_config.base_policy_config import BasePolicyConfig

@autoconfig
class ClutterBreaker_Config(BasePolicyConfig):
    robot_num = 2
    real_world = False
    random_seed = 0

    # Search
    search_debug = True
    search_heuristic_weight = 5.0
    search_max_depth = 50
    search_presearch_beam_width = 100
    search_presearch_max_depth = 50
    search_open_queue_cap = 2048
    search_max_children_per_expand = 16
    search_gap_sample_temperature = 0
    search_state_hash_xy_resolution = 0.1
    search_state_hash_yaw_resolution = 0.1
    # When False, the search deduplicates nodes by obstacle distribution only,
    # ignoring robot positions/yaws.  Children that fail to move any obstacle
    # then collapse onto their parent's state key and are pruned, preventing the
    # search from looping on stuck pushes at a local difficulty point.
    search_state_hash_include_robots = False
    search_heuristic_inf_fallback = 1e6
    search_desired_push_speed = 0.3
    search_desired_transition_speed = 0.5
    search_gap_sample_count = 1
    search_push_effect_scale = 1
    # Dynamic push-effect weight.  When the search stalls at a local difficulty
    # point (repeatedly popping nodes that neither improve cost-to-go nor
    # accumulate push effect), the effective push-effect scale is multiplied by
    # search_push_effect_scale_boost_factor, capped at
    # search_push_effect_scale_max, once per
    # search_push_effect_stagnation_threshold consecutive non-progress pops.
    search_push_effect_dynamic_scale_enabled = True
    search_push_effect_scale_boost_factor = 2.0
    search_push_effect_scale_max = 64.0
    search_push_effect_stagnation_threshold = 20
    # Threshold for triggering lazy evaluation of search nodes. 
    search_lazy_progress_threshold = 0.4
    # Gap progress effect
    search_gap_break_bonus = 10.0
    search_gap_progress_scale = 1.0
    search_gap_progress_cap = float("inf")
    search_gap_break_eps = 1e-3

    # Local Clearance recursive depth
    recursive_depth_presearch = 0
    recursive_depth_task_sample = 2

    # Local-clearance debug visualization (matplotlib gap/split figures in the
    # task sampler / endpoint sampler).  Keep False for headless benchmark
    # trials: True opens Tk figures that crash in subprocesses and adds CPU
    # overhead per candidate plan.  Intended only for interactive debugging.
    local_clearance_debug = False

    # ------------------------------------------------------------------
    # Task-richness knobs (introduced with the 5bd74a7 scene tuning).
    # Per-scene overridable via "policy_overrides" in the benchmark JSON.
    # ------------------------------------------------------------------
    # LocalClearanceConfig field overrides for the SILS task sampler (keys
    # are LocalClearanceConfig field names, e.g. "direction_jitter_deg",
    # "adaptive_direction_jitter_max_deg").  None keeps the fast benchmark
    # defaults baked into _make_sils_local_cfg.
    local_clearance_overrides: Optional[Dict] = None
    # LocalClearanceConfig field overrides for the per-node WccgPresearch
    # cost estimate.  None keeps the default LocalClearanceConfig.
    presearch_local_clearance_overrides: Optional[Dict] = None
    # Root task variation: multiply opening-primitive probes around each root
    # direction.  Required for task success in dense scenes (M >= 30); keep
    # True to preserve the paper benchmark behavior (5bd74a7+).
    enable_root_task_variation: bool = True
    root_task_variations_per_side: int = 2
    root_task_variation_angle_deg: float = 30.0
    # Random angular-velocity jitter on rotated opening primitives.  Adds task
    # diversity but injects run-to-run variance in benchmark planning.
    opening_omega_jitter: bool = True
    # Mode-generation contact assignment: when the legacy fixed-order residual
    # greedy fails (a robot's candidates all violate the pairwise pusher-distance
    # constraint), fall back to a bounded backtracking search over robots and
    # candidates.  Essential for N_R>=4 in cluttered scenes.
    mode_gen_assignment_backtrack: bool = True
    mode_gen_backtrack_budget: int = 2000
    # Subset ("temporarily drop a robot for this push task") fallback.  Used when
    # no full-team contact assignment exists, e.g. N_R=4 on small faces / tight
    # pusher spacing.  Excluded robots hold position for that task only.
    mode_gen_subset_fallback: bool = True
    mode_gen_subset_max_drop: int = 1
    mode_gen_subset_penalty: float = 0.5
    
    # Direction sampler
    direction_loss_thresh = 1.0
    direction_open_rate_thresh = 0.0
    direction_temperature = 0.1
    direction_topk = 8
    direction_omega_penalty = 0.05




    