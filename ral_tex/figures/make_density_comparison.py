"""Manuscript Fig. 10: obstacle-density scaling (budget-capped times).

Run:  python ral_tex/figures/make_density_comparison.py

Writes the manuscript figure and the copy used by the response letter's
"original versus revised" pair, so that both always show the same plot.

Conventions (see the manuscript's Setup paragraph):
  * planning time:  unsuccessful trials are charged the $800$ s planning cap;
  * execution time: unsuccessful trials are charged the $500$ s execution cap
                    ($20{,}000$ control steps at the $40$ Hz control rate).
No successful trial exceeds either budget (max observed execution 482.6 s).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "density_scaling"
OUT_MAN = Path(__file__).resolve().parent / "density_comparison.pdf"
OUT_LET = ROOT / "response" / "figures" / "new_density.pdf"

CAP_PT, CAP_ET = 800.0, 500.0

plt.rcParams.update({
    "font.family": "serif", "font.size": 7, "axes.labelsize": 7,
    "legend.fontsize": 5.7, "xtick.labelsize": 5.8, "ytick.labelsize": 5.8,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.grid": True, "grid.linewidth": 0.35, "grid.alpha": 0.35,
    "axes.spines.top": False, "axes.spines.right": False,
})

CLR = {"ours": "#1f5c99", "norec": "#7fb2d6", "slpush": "#c8443f",
       "dfs": "#5b4b8a", "rec": "#9a9a9a"}
MK = {"ours": "o", "norec": "^", "slpush": "D", "dfs": "v", "rec": "x"}
ORDER = [("PushAround", "ours"), ("PushAround w/o rec.", "norec"),
         ("SL-Push (sim)", "slpush"), ("DFS-WCCG", "dfs"), ("Rec-NAMO", "rec")]

raw = pd.read_csv(DATA / "raw_results_all.csv")
summ = pd.read_csv(DATA / "summary_scaling_suite.csv")
ok = (raw.status == "TERMINATED") & (raw.reason == "task_done")

et = []
for label, _ in ORDER:
    for m, g in raw[raw.policy_label == label].groupby("x_value"):
        vals = np.where(ok[g.index], g.exec_time.to_numpy(float), CAP_ET)
        et.append({"policy_label": label, "x_value": float(m),
                   "mean": float(np.mean(vals)), "std": float(np.std(vals, ddof=1))})
et = pd.DataFrame(et)

fig, axes = plt.subplots(1, 3, figsize=(3.50, 1.56))
fig.subplots_adjust(left=0.082, right=0.985, bottom=0.205, top=0.815, wspace=0.34)
for label, key in ORDER:
    g = summ[summ.policy_label == label].sort_values("x_value")
    ge = et[et.policy_label == label].sort_values("x_value")
    lw, ms = (1.6, 3.4) if key == "ours" else (1.0, 2.6)
    z = 5 if key == "ours" else 2
    x = g.x_value.to_numpy(float)
    short = {"ours": "PushAround", "norec": "w/o rec.", "slpush": "SL-Push (sim)",
             "dfs": "DFS-WCCG", "rec": "Rec-NAMO"}[key]
    axes[0].plot(x, g.success_rate * 100, marker=MK[key], color=CLR[key], lw=lw, ms=ms,
                 zorder=z, label=short)
    axes[1].plot(x, g.planning_time_mean_capped, marker=MK[key], color=CLR[key], lw=lw, ms=ms, zorder=z)
    axes[1].errorbar(x, g.planning_time_mean_capped, yerr=g.planning_time_std_capped,
                     color=CLR[key], lw=0.7, capsize=1.4, zorder=z - 1)
    axes[2].plot(ge.x_value, ge["mean"], marker=MK[key], color=CLR[key], lw=lw, ms=ms, zorder=z)
    axes[2].errorbar(ge.x_value, ge["mean"], yerr=ge["std"], color=CLR[key], lw=0.7,
                     capsize=1.4, zorder=z - 1)

for ax, letter, title in zip(axes, "abc",
                               ("success (%)", "planning time (s)", "execution time (s)")):
    ax.set_title(f"({letter}) {title}", loc="left", fontsize=6.0, pad=2.2)
    ax.set_xticks([15, 25, 35, 45])
    ax.set_xlim(13.4, 46.6)

axes[0].set_ylim(-4, 108)
axes[1].set_yscale("log")
axes[1].set_ylim(1, 1900)
axes[1].axhline(CAP_PT, color="k", ls=":", lw=0.8, zorder=1)
axes[1].annotate("cap", xy=(15.4, 780), fontsize=5.2)
axes[2].set_ylim(0, 610)
axes[2].axhline(CAP_ET, color="k", ls=":", lw=0.8, zorder=1)
axes[2].annotate("cap", xy=(15.4, 520), fontsize=5.2)
for ax in axes:
    ax.set_xlabel("number of obstacles $M$", fontsize=6.0, labelpad=1.2)

h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.885), ncol=5,
           frameon=False, columnspacing=0.8, handlelength=1.1,
           handletextpad=0.35, borderaxespad=0.0)
for out in (OUT_MAN, OUT_LET):
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    print(f"  wrote {out.relative_to(ROOT)}")
plt.close(fig)
