"""Generate the density-scaling figure used in the PushAround RAL manuscript.

The timing statistic follows src.evaluate.scalability.plot_scaling_suite:
every unsuccessful trial is replaced by the per-trial timeout budget
(`trial_timeout_sec`) before averaging. This prevents plan-fail rows from being
plotted as artificially short planning times.
"""
from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_results_all.csv"
SUMMARY = ROOT / "data" / "density_scaling_summary.csv"
OUT_PDF = ROOT / "figures" / "density_scaling_curve.pdf"
OUT_PNG = ROOT / "figures" / "density_scaling_curve.png"

POLICY_ORDER = ["ours", "ours_no_recursive", "slpush", "dfs", "recursive"]
LABELS = {
    "ours": "Ours",
    "ours_no_recursive": "Ours w/o recursive",
    "slpush": "SLPush",
    "dfs": "DFS",
    "recursive": "Recursive",
}
# Set this to a subset such as [15, 20, 25, 35, 40, 45] if one density is later
# removed from the paper. None keeps all densities in the raw CSV.
KEEP_COUNTS = None


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _trial_timeout_caps(group: pd.DataFrame) -> np.ndarray:
    caps = _safe_numeric(group.get("trial_timeout_sec", pd.Series(np.nan, index=group.index))).to_numpy(float)
    finite = caps[np.isfinite(caps) & (caps > 0)]
    fallback = float(np.nanmax(finite)) if finite.size else float("nan")
    if math.isfinite(fallback):
        caps = np.where(np.isfinite(caps) & (caps > 0), caps, fallback)
    return caps


def _cap_unsuccessful(values: np.ndarray, success_mask: np.ndarray, caps: np.ndarray) -> np.ndarray:
    out = np.asarray(values, dtype=float).copy()
    failed = ~np.asarray(success_mask, dtype=bool)
    valid = failed & np.isfinite(caps) & (caps > 0)
    out[valid] = caps[valid]
    return out


def summarize(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    if KEEP_COUNTS is not None:
        df = df[df["obstacle_count"].isin(KEEP_COUNTS)].copy()
    for col in ["success", "planning_time", "trial_timeout_sec", "obstacle_count"]:
        df[col] = _safe_numeric(df[col])
    rows = []
    for (variant, label, n), group in df.groupby(["policy_variant", "policy_label", "obstacle_count"], sort=False):
        success = group["success"].fillna(0).to_numpy(float) > 0.5
        capped = _cap_unsuccessful(
            group["planning_time"].to_numpy(float),
            success,
            _trial_timeout_caps(group),
        )
        succ_times = group.loc[success, "planning_time"].to_numpy(float)
        rows.append({
            "policy_variant": str(variant),
            "policy_label": str(label),
            "num_obstacles": int(n),
            "num_trials": int(len(group)),
            "num_success": int(success.sum()),
            "success_rate_pct": 100.0 * float(np.mean(success)) if len(success) else float("nan"),
            "planning_time_capped_mean_s": float(np.nanmean(capped)) if len(capped) else float("nan"),
            "planning_time_capped_std_s": float(np.nanstd(capped, ddof=1)) if len(capped) > 1 else 0.0,
            "planning_time_success_mean_s": float(np.nanmean(succ_times)) if len(succ_times) else float("nan"),
        })
    out = pd.DataFrame(rows)
    order = {p: i for i, p in enumerate(POLICY_ORDER)}
    out["_order"] = out["policy_variant"].map(order).fillna(999)
    out = out.sort_values(["_order", "num_obstacles"]).drop(columns=["_order"])
    return out


def make_plot(summary: pd.DataFrame) -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.4,
        "ytick.labelsize": 6.4,
        "legend.fontsize": 5.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    counts = sorted(summary["num_obstacles"].unique())
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(3.40, 2.70), sharex=True)
    for variant in POLICY_ORDER:
        g = summary[summary["policy_variant"] == variant].sort_values("num_obstacles")
        if g.empty:
            continue
        label = LABELS.get(variant, str(g["policy_label"].iloc[0]))
        x = g["num_obstacles"].to_numpy(int)
        succ = g["success_rate_pct"].to_numpy(float)
        t = g["planning_time_capped_mean_s"].to_numpy(float)
        terr = g["planning_time_capped_std_s"].to_numpy(float)
        ax0.plot(x, succ, marker="o", linewidth=1.2, markersize=2.7, label=label)
        ax1.errorbar(x, t, yerr=terr, marker="o", linewidth=1.05, markersize=2.6,
                     capsize=1.6, elinewidth=0.6, label=label)
    ax0.set_ylabel("Success rate (%)")
    ax0.set_ylim(-3, 103)
    ax0.set_yticks([0, 20, 40, 60, 80, 100])
    ax0.grid(True, linewidth=0.35, alpha=0.35)
    ax1.set_xlabel("Number of movable obstacles")
    ax1.set_ylabel("Planning time (s)")
    ax1.set_ylim(0, 1000)
    ax1.set_yticks([0, 200, 400, 600, 800, 1000])
    ax1.set_xticks(counts)
    ax1.grid(True, linewidth=0.35, alpha=0.35)
    for ax in (ax0, ax1):
        ax.spines["top"].set_linewidth(0.7)
        ax.spines["right"].set_linewidth(0.7)
        ax.spines["bottom"].set_linewidth(0.7)
        ax.spines["left"].set_linewidth(0.7)
        ax.tick_params(width=0.7, length=2.5)
    handles, labels = ax0.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.035), columnspacing=0.65, handlelength=1.25)
    fig.tight_layout(rect=(0, 0, 1, 0.91), h_pad=0.35)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight")
    fig.savefig(OUT_PNG, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    raw = pd.read_csv(RAW)
    summary = summarize(raw)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY, index=False)
    make_plot(summary)


if __name__ == "__main__":
    main()
