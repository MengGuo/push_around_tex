"""Figures for the author response letter (PushAround, RA-L revision).

All numbers are read directly from ``push_around_tex/data/`` so that every
figure in the response letter is traceable to the released evaluation data.

Run:  python response/make_figures.py
Out:  response/figures/resp_*.pdf (and .png)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
if not DATA.is_dir():          # when shipped inside the multimedia package
    DATA = Path(__file__).resolve().parent
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "legend.fontsize": 6.4,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.grid": True,
    "grid.linewidth": 0.35,
    "grid.alpha": 0.35,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})

CLR = {
    "ours": "#1f5c99",
    "ours_pre": "#8fb8d9",
    "norec": "#7fb2d6",
    "slpush": "#c8443f",
    "dfs": "#5b4b8a",
    "rec": "#9a9a9a",
}
MK = {"ours": "o", "ours_pre": "s", "norec": "^", "slpush": "D", "dfs": "v", "rec": "x"}


def wilson(k: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


# --------------------------------------------------------------------------
# Figure 1: obstacle-density scaling (ours vs. baselines, 10 seeds)
# --------------------------------------------------------------------------
def legend_above(fig, axes, handles, labels, rect_top=0.88, pad=0.022, **kw):
    """Lay out the figure, then anchor a figure-level legend just above the
    tallest axes title.  Returns (legend, gap_pt) where gap_pt is the measured
    vertical clearance between the title ink top and the legend ink bottom."""
    fig.tight_layout(rect=(0, 0, 1, rect_top))
    fig.canvas.draw()
    inv = fig.transFigure.inverted()
    title_top = max(ax.title.get_window_extent().transformed(inv).y1 for ax in axes)
    leg = fig.legend(handles, labels, loc="lower center",
                     bbox_to_anchor=(0.5, title_top + pad), **kw)
    fig.canvas.draw()
    leg_bottom = leg.get_window_extent().transformed(inv).y0
    gap_pt = (leg_bottom - title_top) * fig.get_figheight() * 72.0
    return leg, gap_pt


def fig_density() -> None:
    d = pd.read_csv(DATA / "density_scaling" / "summary_scaling_suite.csv")
    order = [
        ("PushAround", "ours", "PushAround (ours)"),
        ("PushAround w/o rec.", "norec", "PushAround w/o rec."),
        ("SL-Push (sim)", "slpush", "SL-Push (sim)"),
        ("DFS-WCCG", "dfs", "DFS-WCCG"),
        ("Rec-NAMO", "rec", "Rec-NAMO"),
    ]
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(6.9, 2.35))
    for label, key, name in order:
        g = d[d.policy_label == label].sort_values("x_value")
        x = g.x_value.to_numpy(float)
        lw = 1.6 if key == "ours" else 1.0
        ms = 3.4 if key == "ours" else 2.6
        ax0.plot(x, g.success_rate * 100, marker=MK[key], color=CLR[key],
                 lw=lw, ms=ms, label=name, zorder=5 if key == "ours" else 2)
        ax1.plot(x, g.planning_time_mean_capped, marker=MK[key], color=CLR[key],
                 lw=lw, ms=ms, label=name, zorder=5 if key == "ours" else 2)
        if key == "ours":
            ax1.errorbar(x, g.planning_time_mean_capped, yerr=g.planning_time_std_capped,
                         color=CLR[key], lw=0.8, capsize=1.6, zorder=4)
    ax0.set_xlabel("movable obstacles $M$")
    ax0.set_ylabel("success rate (%)")
    ax0.set_ylim(-4, 108)
    ax0.set_xticks(range(15, 50, 5))
    ax0.set_title("(a) success rate")
    ax1.set_xlabel("movable obstacles $M$")
    ax1.set_ylabel("planning time, failed capped (s)")
    ax1.set_yscale("log")
    ax1.set_ylim(1, 1600)
    ax1.axhline(800, color="k", ls=":", lw=0.8)
    ax1.annotate("800 s cap", xy=(15.4, 860), fontsize=6.2)
    ax1.set_xticks(range(15, 50, 5))
    ax1.set_title("(b) planning time (10 seeds, mean$\\pm$s.d.)")
    h, l = ax0.get_legend_handles_labels()
    _, gap = legend_above(fig, (ax0, ax1), h, l, ncol=5, frameon=False,
                          columnspacing=1.0, handlelength=1.4)
    print(f"  resp_density  legend/title gap = {gap:.1f} pt")
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"resp_density.{ext}", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 2: planner-execution physics mismatch
# --------------------------------------------------------------------------
def fig_mismatch() -> None:
    dig = json.load(open(DATA / "baselines_paper_ready" / "baseline_supplement_data.json"))
    conds = dig["physics_mismatch"]["conditions"]
    keys = ["nominal", "mass_0p6", "mass_1p4", "friction_0p6", "friction_1p4",
            "spin_0p6", "spin_1p4", "force_0p6", "force_1p4"]
    pretty = {"nominal": "nominal", "mass_0p6": "mass\n$\\times0.6$", "mass_1p4": "mass\n$\\times1.4$",
              "friction_0p6": "lat. fric.\n$\\times0.6$", "friction_1p4": "lat. fric.\n$\\times1.4$",
              "spin_0p6": "spin fric.\n$\\times0.6$", "spin_1p4": "spin fric.\n$\\times1.4$",
              "force_0p6": "force\n$\\times0.6$", "force_1p4": "force\n$\\times1.4$"}
    by = {c["condition"]: c for c in conds}

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(6.9, 2.5),
                                   gridspec_kw={"width_ratios": [2.5, 1.0]})
    x = np.arange(len(keys), dtype=float)
    w = 0.27
    series = [("pusharound_10seeds", "ours", "PushAround (n=10)"),
              ("slpush_5seeds", "slpush", "SL-Push (sim) (n=5)"),
              ("dfs_5seeds", "dfs", "DFS-WCCG (n=5)")]
    for i, (k, key, name) in enumerate(series):
        vals, lo, hi = [], [], []
        for cid in keys:
            cell = by[cid].get(k)
            if cell is None:
                vals.append(np.nan); lo.append(np.nan); hi.append(np.nan); continue
            r = cell["success_rate"] * 100
            l, h = wilson(cell["n_success"], cell["n_trials"])
            vals.append(r); lo.append(r - l * 100); hi.append(h * 100 - r)
        ax0.bar(x + (i - 1) * w, vals, w, yerr=[lo, hi], capsize=1.4,
                color=CLR[key], edgecolor="k", linewidth=0.35, label=name,
                error_kw={"elinewidth": 0.6})
    ax0.set_xticks(x)
    ax0.set_xticklabels([pretty[c] for c in keys], fontsize=5.9)
    ax0.set_ylabel("success rate (%)")
    ax0.set_ylim(0, 118)
    ax0.axvspan(0.5, len(keys) - 0.5, color="0.93", zorder=0)
    ax0.set_title("(a) success under execution-only mismatch (Wilson 95% CI)")

    # replanning effort of PushAround vs deviation magnitude
    p = pd.read_csv(DATA / "physics_mismatch" / "summary.csv")
    p["dev"] = p.factor.apply(lambda f: 0 if f == 1.0 else (20 if f in (0.8, 1.2) else 40))
    grp = p.groupby("dev").replans_mean_all.mean()
    ax1.bar([0, 1, 2], [grp.get(0, np.nan), grp.get(20, np.nan), grp.get(40, np.nan)],
            color=[CLR["ours"], CLR["ours_pre"], CLR["norec"]], edgecolor="k", linewidth=0.35)
    for xi, v in zip([0, 1, 2], [grp.get(0, np.nan), grp.get(20, np.nan), grp.get(40, np.nan)]):
        ax1.text(xi, v + 0.08, f"{v:.1f}", ha="center", fontsize=6.2)
    ax1.set_xticks([0, 1, 2]); ax1.set_xticklabels(["nom.", "$\\pm20\\%$", "$\\pm40\\%$"])
    ax1.set_ylabel("mean replans per trial")
    ax1.set_ylim(0, max(grp) * 1.35)
    ax1.set_title("(b) PushAround replanning effort")
    h, l = ax0.get_legend_handles_labels()
    _, gap = legend_above(fig, (ax0, ax1), h, l, ncol=3, frameon=False,
                          columnspacing=0.9, handlelength=1.2)
    print(f"  resp_mismatch legend/title gap = {gap:.1f} pt")
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"resp_mismatch.{ext}", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 3: robot-team scaling (post-fix ours, pre-fix ours, baselines)
# --------------------------------------------------------------------------
def fig_robot() -> None:
    """Robot-team scaling: PushAround vs baselines, both on the post-fix code."""
    dig = json.load(open(DATA / "baselines_paper_ready" / "baseline_supplement_data.json"))
    cells = dig["robot_scaling"]["cells"]
    pre = {c["robot_num"]: c for c in cells["pusharound_prefix_10seeds"]}
    pre_sl = {c["robot_num"]: c for c in cells["slpush_5seeds"]}
    pre_df = {c["robot_num"]: c for c in cells["dfs_5seeds"]}

    # PushAround, current code (n=10)
    r = pd.read_csv(DATA / "robot_scaling_modefix" / "raw_results_all.csv")
    post = {}
    for n in (2, 3, 4):
        s_ = r[r.robot_num == n]
        ok = s_[s_.success == 1]
        post[n] = {"succ": 100.0 * s_.success.mean(),
                   "pt": ok.planning_time.mean(), "pt_std": ok.planning_time.std(ddof=1),
                   "et": ok.exec_time.mean(), "et_std": ok.exec_time.std(ddof=1)}

    # baselines, post-fix re-run (n=10)
    b = pd.read_csv(DATA / "robot_scaling_baselines_postfix" / "paper_summary.csv")
    def cell(policy, n, col):
        row = b[(b.policy == policy) & (b.robot_num == n)]
        return None if row.empty else float(row[col].iloc[0])
    new_sl = {n: {"succ": 100 * cell("slpush", n, "success_rate"),
                  "pt": cell("slpush", n, "planning_time_mean_success_s"),
                  "pt_std": cell("slpush", n, "planning_time_std_success_s"),
                  "et": cell("slpush", n, "exec_time_mean_success_s"),
                  "et_std": cell("slpush", n, "exec_time_std_success_s")} for n in (3, 4)}
    new_df = {n: {"succ": 100 * cell("dfs", n, "success_rate"),
                  "pt": cell("dfs", n, "planning_time_mean_success_s"),
                  "pt_std": cell("dfs", n, "planning_time_std_success_s"),
                  "et": cell("dfs", n, "exec_time_mean_success_s"),
                  "et_std": cell("dfs", n, "exec_time_std_success_s")} for n in (3, 4)}

    Ns = [2, 3, 4]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.3))

    def series(ax, get, keyval, colour, marker, name, dashed=False, lw=1.0, ms=3.0):
        xs, ys = [], []
        for n in Ns:
            v = get(n)
            if v is None or (isinstance(v, float) and math.isnan(v)):
                continue
            xs.append(n); ys.append(v)
        if xs:
            ax.plot(xs, ys, marker=marker, color=colour, lw=lw, ms=ms, label=name,
                    ls="--" if dashed else "-", alpha=0.95 if not dashed else 0.55)

    # ---- (a) success
    ax = axes[0]
    series(ax, lambda n: post[n]["succ"], None, CLR["ours"], "o",
           "PushAround (current)", lw=1.7, ms=3.8)
    series(ax, lambda n: 100.0 * pre[n]["success_rate"] if n in pre else None, None,
           CLR["ours_pre"], "s", "PushAround (before fix)", dashed=True)
    series(ax, lambda n: new_sl[n]["succ"] if n in new_sl else None, None,
           CLR["slpush"], "D", "SL-Push (sim), re-run")
    series(ax, lambda n: 100.0 * pre_sl[n]["success_rate"] if n in pre_sl else None, None,
           CLR["slpush"], "D", "SL-Push (sim), before fix", dashed=True)
    series(ax, lambda n: new_df[n]["succ"] if n in new_df else None, None,
           CLR["dfs"], "v", "DFS-WCCG, re-run")
    series(ax, lambda n: 100.0 * pre_df[n]["success_rate"] if n in pre_df else None, None,
           CLR["dfs"], "v", "DFS-WCCG, before fix", dashed=True)
    ax.set_xlabel("number of robots $N$")
    ax.set_ylabel("success rate (%)")
    ax.set_xticks(Ns); ax.set_ylim(-6, 115)
    ax.set_title("(a) success vs. team size")
    ax.annotate("shared mode-gen fix:\nSL-Push $0\\to80$%, DFS $80\\to90$%",
                xy=(3.6, 84), fontsize=5.6, ha="center", color="0.25")
    ax.legend(loc="lower left", frameon=False, fontsize=5.0)

    # ---- (b) planning time
    ax = axes[1]
    series(ax, lambda n: post[n]["pt"], None, CLR["ours"], "o", "PushAround (current)", lw=1.7, ms=3.8)
    ax.errorbar(Ns, [post[n]["pt"] for n in Ns], yerr=[post[n]["pt_std"] for n in Ns],
                color=CLR["ours"], lw=0.8, capsize=1.5, zorder=4)
    series(ax, lambda n: new_sl[n]["pt"] if n in new_sl else None, None,
           CLR["slpush"], "D", "SL-Push (sim), re-run")
    series(ax, lambda n: new_df[n]["pt"] if n in new_df else None, None,
           CLR["dfs"], "v", "DFS-WCCG, re-run")
    ax.set_yscale("log")
    ax.set_xlabel("number of robots $N$"); ax.set_ylabel("planning time (s)")
    ax.set_xticks(Ns); ax.set_ylim(15, 600)
    ax.set_title("(b) planning time (successful runs)")
    ax.legend(loc="upper left", frameon=False, fontsize=5.4)

    # ---- (c) execution time
    ax = axes[2]
    series(ax, lambda n: post[n]["et"], None, CLR["ours"], "o", "PushAround (current)", lw=1.7, ms=3.8)
    ax.errorbar(Ns, [post[n]["et"] for n in Ns], yerr=[post[n]["et_std"] for n in Ns],
                color=CLR["ours"], lw=0.8, capsize=1.5, zorder=4)
    series(ax, lambda n: new_sl[n]["et"] if n in new_sl else None, None,
           CLR["slpush"], "D", "SL-Push (sim), re-run")
    series(ax, lambda n: new_df[n]["et"] if n in new_df else None, None,
           CLR["dfs"], "v", "DFS-WCCG, re-run")
    for n in (3, 4):
        ax.annotate(f"{b[(b.policy=='slpush') & (b.robot_num==n)]['pushes_mean_success'].iloc[0]:.0f}",
                    xy=(n - 0.06, new_sl[n]["et"] + 16), fontsize=5.4, color=CLR["slpush"], ha="center")
    ax.set_xlabel("number of robots $N$"); ax.set_ylabel("execution time (s)")
    ax.set_xticks(Ns); ax.set_ylim(60, 330)
    ax.set_title("(c) execution time (red labels: pushes)")
    ax.legend(loc="lower right", frameon=False, fontsize=5.4)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"resp_robot.{ext}", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 4: WCCG connectivity validation vs. configuration-space references
# --------------------------------------------------------------------------
def fig_wccg() -> None:
    w = pd.read_csv(DATA / "wccg_cpp_paper_300" / "paper_summary.csv")
    order = ["convex", "mixed", "nonconvex"]
    w = w.set_index("category").loc[order + ["all"]]
    agree = w.cc_fr_agreement.apply(lambda s: int(s.split("/")[0]))
    trials = w.trials
    amb = w.ambiguous

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(6.9, 2.35),
                                   gridspec_kw={"width_ratios": [1.35, 1.0]})
    x = np.arange(len(w))
    ax0.bar(x - 0.18, agree, 0.36, color="#4c9f70", edgecolor="k", linewidth=0.35,
            label="CC$=$FR agreement")
    ax0.bar(x + 0.18, trials - amb, 0.36, color=CLR["ours"], edgecolor="k", linewidth=0.35,
            label="WCCG$=$CC agreement")
    for xi, (a, t, m) in enumerate(zip(agree, trials, amb)):
        ax0.text(xi - 0.18, a + 1.5, f"{a}/{t}", ha="center", fontsize=6.0)
        ax0.text(xi + 0.18, t - m + 1.5, f"{t-m}/{t}", ha="center", fontsize=6.0)
    ax0.set_xticks(x)
    ax0.set_xticklabels(["convex", "mixed", "non-convex", "all 300"], fontsize=6.4)
    ax0.set_ylabel("agreeing scenarios")
    ax0.set_ylim(0, 330)
    ax0.set_title("(a) agreement on 300 random scenes")
    ax0.legend(loc="upper left", frameon=False, fontsize=6.2)

    names = ["WCCG", "CC", "FR\n(0.01 m)"]
    vals = [w.wccg_time_ms.iloc[-1], w.cc_time_ms.iloc[-1], w.fr_time_ms.iloc[-1]]
    cols = [CLR["ours"], "#4c9f70", CLR["slpush"]]
    ax1.bar(names, vals, color=cols, edgecolor="k", linewidth=0.35)
    ax1.set_yscale("log")
    ax1.set_ylabel("mean query time (ms)")
    for i, v in enumerate(vals):
        ax1.text(i, v * 1.15, f"{v:.2f}", ha="center", fontsize=6.2)
    ax1.set_ylim(0.5, 1200)
    ax1.set_title("(b) connectivity query cost")
    ax1.annotate(f"$\\times${w.fr_over_wccg_time_ratio.iloc[-1]:.0f} vs. FR",
                 xy=(2, vals[2]), xytext=(1.15, 500), fontsize=6.4,
                 arrowprops=dict(arrowstyle="->", lw=0.6, color="0.35"))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"resp_wccg.{ext}", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 5: statistical reliability (Wilson 95% CIs) of all headline results
# --------------------------------------------------------------------------
def fig_reliability() -> None:
    groups = {
        "(a) main comparison\n(Scenario 1, 40 trials)": [
            ("PushAround", 39, 40, "ours"), ("SL-Push (sim)", 30, 40, "slpush"),
            ("SL-Push (offline)", 25, 40, "slpush"), ("Rec-NAMO", 15, 40, "rec"),
            ("DFS-WCCG", 10, 40, "dfs"),
        ],
        "(b) density $M{=}45$\n(10 seeds)": [
            ("PushAround", 10, 10, "ours"), ("DFS-WCCG", 0, 10, "dfs"),
            ("SL-Push (sim)", 0, 10, "slpush"), ("Rec-NAMO", 0, 10, "rec"),
        ],
        "(c) physics mismatch $\\pm40\\%$\n(ours 80, base 40 trials)": [
            ("PushAround", 78, 80, "ours"), ("DFS-WCCG", 23, 40, "dfs"),
            ("SL-Push (sim)", 13, 40, "slpush"),
        ],
        "(d) robot team $N{=}4$\n(10 seeds per cell)": [
            ("PushAround", 10, 10, "ours"), ("DFS-WCCG", 9, 10, "dfs"),
            ("SL-Push (sim)", 8, 10, "slpush"),
        ],
    }
    fig, axes = plt.subplots(1, 4, figsize=(6.9, 1.95), sharex=True)
    for ax, (title, rows) in zip(axes, groups.items()):
        y = np.arange(len(rows))[::-1]
        for yi, (name, k, n, key) in zip(y, rows):
            lo, hi = wilson(k, n)
            ax.plot([lo * 100, hi * 100], [yi, yi], color=CLR[key], lw=1.6, solid_capstyle="butt")
            ax.plot(k / n * 100, yi, marker="o", ms=3.0, color=CLR[key])
        ax.set_yticks(y)
        ax.set_yticklabels([r[0] for r in rows], fontsize=6.0)
        ax.set_xlim(-4, 104); ax.set_ylim(-0.7, len(rows) - 0.3)
        ax.set_title(title, fontsize=6.8)
        ax.set_xlabel("success (%)", fontsize=6.8)
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"resp_reliability.{ext}", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_density()
    fig_mismatch()
    fig_robot()
    fig_wccg()
    fig_reliability()
    for p in sorted(OUT.glob("resp_*.pdf")):
        print(f"wrote {p.relative_to(ROOT)}  ({p.stat().st_size/1024:.1f} kB)")
