from src.config.auto_config import autoconfig
from src.config.policy_config.transition_config import (
    PrioritizedMotionConfig,
    TransitionAstarConfig,
    TransitionControllerConfig,
)
from src.config.policy_config.pushing_config import PushingControllerConfig
import numpy as np


@autoconfig
class BasePolicyConfig:
    robot_num = 2
    real_world = False
    random_seed = 0
    open_predict_gui = False
    # 8 workers measured faster than 16 on the 32-thread i9-13900HX benchmark
    # host (rollout batches are per-sim bound; 16+ workers contend for cores,
    # especially under throttled/silent power modes).
    num_parallel_workers = 8
    planning_timeout_sec = 800.0
    # Configuration for contact points
    filter_cps = False
    sample_density = 0.1
    max_point_num = 100
    visualize_contact_points = False
    width_safe_margin = 0.1
    # -------------------------------------------------------
    # Config for MODE GENERATION
    # -------------------------------------------------------
    greedy_opt_max_iter = 300
    risk_dist_to_vertex_concave = 0.05
    risk_dist_to_vertex_convex = 0.05
    IS_VERTEX_POINTS_PUSHABLES = {1: True, 2: True, 3: False, 4: False}
    HETEROGENEITY_CONSIDERED = False
    generalized_force_weight = [1, 1, 1.5]
    multi_direction_weights = {
        1: [10, 0, 0, 0, 0, 0],
        2: [10, 0, 0, 0, 0, 0],
        3: [10, 1, 1, 1, 1, 1],
        4: [10, 1.5, 1.5, 1.5, 1.5, 1.5],
    }
    robust_loss_coeffs = {1: 0.0, 2: 0.0, 3: 0.2, 4: 0.1}
    mode_table_size = 300
    omega_scale = 1.0
    load_mode_table = False
    mode_table_file_dir = None
    mode_table_file_name = None
    mode_gen_via_greedy_opt = True
    mode_gen_via_table_query = False
    mode_gen_min_robot_dist = 0.15
    # Cap the per-call mode-table seed repair loop (default would be
    # max(8, min(40, greedy_opt_max_iter//5))).  8 measured ~30% faster than
    # the 40-iteration default with no success loss in the M=30 sweep.
    table_query_repair_max_iter = 40
    # -------------------------------------------------------
    # Config for TRANS CONTROLLER
    # -------------------------------------------------------
    transition_controller = TransitionControllerConfig()

    # -------------------------------------------------------
    # Config for PUSH CONTROLLER
    # -------------------------------------------------------
    pushing_controller = PushingControllerConfig(
        real_world=real_world,
        robot_num=robot_num,
    )

    # -------------------------------------------------------
    # Config for Sim-in-loop Planning / Prediction
    # -------------------------------------------------------
    max_simsteps = 80
    # predictor will check at 20,25,30,... with window:(10,20],(15,25],(20,30],...)
    sils_push_check_start = 20
    sils_push_check_interval = 5
    sils_push_goal_check_interval = 10
    sils_push_stall_window = 10
    # Earlier stall detection (0.1 instead of 0.05): terminates doomed rollouts
    # sooner, cutting planning sims ~30% with no success loss in the M=30 sweep.
    sils_push_stall_threshold = 5e-2
    
    # Shared nominal speed used by the unified execution manager when it needs
    # to synthesize a fallback / local-replan push velocity for a baseline task.
    search_desired_push_speed = 0.3
    search_desired_transition_speed = 0.5
    push_ref_traj_dt = 0.02

    # -------------------------------------------------------
    # Config for SEQUENTIAL-PUSHING EXECUTION
    # -------------------------------------------------------
    exec_max_time_per_task = 50
    exec_goal_check_interval = 10
    exec_goal_eps = 1e-2

    # Mode search / retry while starting one PushTask.
    max_local_replans = 1
    exec_mode_retry_limit = 5
    exec_mode_risk_scale_start = 1.0
    exec_mode_risk_scale_decay = 0.75
    exec_mode_risk_scale_min = 0.0
    exec_mode_loss_thresh = 0.6


    # Pushing-phase stopping / stagnation checks.
    exec_push_max_steps = 80
    exec_push_check_start = 20
    exec_push_check_interval = 5
    exec_push_stall_window = 10
    exec_push_stall_threshold = 5e-2
    

    # Transition-phase safeguards.
    exec_transition_check_start = 10
    exec_transition_check_interval = 5
    exec_transition_stall_window = 5
    exec_transition_stall_threshold = 1e-2
    exec_transition_max_steps = 1000

    # Type-2 gap-widening progress checks.
    exec_gap_check_interval = 10
    exec_gap_gain_ratio = 1e-3

    exec_video = False
    exec_video_path = None

    @property
    def multi_direction_weight(self):
        key = min(self.robot_num, max(self.multi_direction_weights.keys()))
        return self.multi_direction_weights[key]

    @property
    def robust_loss_coeff(self):
        key = min(self.robot_num, max(self.robust_loss_coeffs.keys()))
        return self.robust_loss_coeffs[key]

    @property
    def is_vertex_pushable(self):
        key = min(self.robot_num, max(self.multi_direction_weights.keys()))
        return self.IS_VERTEX_POINTS_PUSHABLES[key]
