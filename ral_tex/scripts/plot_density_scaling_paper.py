"""Obstacle-density scaling figure for the manuscript (three panels).

Panel (a): success rate.
Panel (b): mean planning time with unsuccessful trials capped at the per-trial
           timeout, on a logarithmic axis.
Panel (c): mean execution time of successful trials.

All statistics are computed from ``data/density_scaling/summary_scaling_suite.csv``
(7 densities x 5 policies x 10 independent seeds) so that the figure is exactly
reproducible; error bars are one standard deviation over the seeds.

The figure is generated at its final print size (3.30 in wide), so the fonts are
legible when placed with \\includegraphics[width=0.95\\columnwidth].

Run:  python ral_tex/scripts/plot_density_scaling_paper.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# When the script is shipped inside the multimedia package (evaluation_data/),
# the records live next to it; inside the repository they live under data/.
_pkg = HERE / "density_scaling" / "summary_scaling_suite.csv"
if _pkg.is_file():
    DATA = _pkg
    OUT_DIR = HERE / "figures"
else:
    DATA = ROOT / "data" / "density_scaling" / "summary_scaling_suite.csv"
    OUT_DIR = ROOT / "ral_tex" / "figures"
OUT_PDF = OUT_DIR / "density_comparison.pdf"
OUT_PNG = OUT_DIR / "density_comparison.png"

SERIES = [
    ("PushAround",           "#1f5c99", "o", 1.5, 2.6, "PushAround"),
    ("PushAround w/o rec.",  "#7fb0d4", "^", 1.0, 2.2, "w/o rec."),
    ("SL-Push (sim)",        "#c8443f", "D", 1.0, 2.2, "SL-Push (sim)"),
    ("DFS-WCCG",             "#5b4b8a", "v", 1.0, 2.2, "DFS-WCCG"),
    ("Rec-NAMO",             "#8d8d8d", "x", 1.0, 2.4, "Rec-NAMO"),
]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 6.0,
    "axes.labelsize": 5.8,
    "axes.titlesize": 6.0,
    "legend.fontsize": 5.2,
    "xtick.labelsize": 5.4,
    "ytick.labelsize": 5.4,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "xtick.major.size": 2.0,
    "ytick.major.size": 2.0,
})


def build():
    """Create the figure and return (fig, [ax_a, ax_b, ax_c])."""
    d = pd.read_csv(DATA)

    # Layout: (a) spans the full column width, (b) and (c) sit side by side
    # below it.  This keeps every panel wide enough for its labels at the final
    # print size (0.95 columnwidth of a two-column IEEE paper).
    fig = plt.figure(figsize=(3.30, 1.70))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.68, 1.0],
                          hspace=0.31, wspace=0.26)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])
    axes = [ax_a, ax_b, ax_c]

    for label, colour, marker, lw, ms, name in SERIES:
        g = d[d.policy_label == label].sort_values("x_value")
        x = g.x_value.to_numpy(float)
        z = 6 if name == "PushAround" else 2
        eb = dict(color=colour, lw=0.0, elinewidth=0.45, capsize=0.9,
                  alpha=0.5, zorder=z - 1)

        ax_a.plot(x, g.success_rate * 100, marker=marker, color=colour,
                  lw=lw, ms=ms, label=name, zorder=z)

        ax_b.plot(x, g.planning_time_mean_capped, marker=marker, color=colour,
                  lw=lw, ms=ms, zorder=z)
        ax_b.errorbar(x, g.planning_time_mean_capped,
                      yerr=g.planning_time_std_capped, **eb)

        ax_c.plot(x, g.exec_time_mean_success, marker=marker, color=colour,
                  lw=lw, ms=ms, zorder=z)
        ax_c.errorbar(x, g.exec_time_mean_success,
                      yerr=g.exec_time_std_success, **eb)

    for ax in axes:
        ax.grid(True, linewidth=0.28, alpha=0.30)
        ax.set_xticks(range(15, 50, 5))
        ax.tick_params(pad=1.2)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)

    # only the bottom row carries the shared x-axis label
    ax_b.set_xlabel("number of obstacles", labelpad=1.0)
    ax_c.set_xlabel("number of obstacles", labelpad=1.0)
    ax_a.set_ylabel("success (%)", labelpad=1.0)
    ax_a.set_ylim(-6, 110)
    ax_a.set_yticks([0, 50, 100])

    ax_b.set_ylabel("planning (s)", labelpad=1.0)
    ax_b.set_yscale("log")
    ax_b.set_ylim(1.2, 1600)
    ax_b.set_yticks([1, 10, 100, 1000])
    ax_b.axhline(800, color="k", ls=":", lw=0.65)
    ax_b.annotate("cap", xy=(24.0, 800), xytext=(24.0, 950), fontsize=4.4,
                  ha="left", va="bottom")

    ax_c.set_ylabel("execution (s)", labelpad=1.0)
    ax_c.set_ylim(0, 500)
    ax_c.set_yticks([0, 100, 200, 300, 400, 500])

    # panel labels inside the axes, top-left corner (no horizontal titles)
    for ax, lab in zip(axes, ("(a)", "(b)", "(c)")):
        ax.text(0.015, 0.90, lab, transform=ax.transAxes, fontsize=6.0,
                fontweight="bold", va="top", ha="left", zorder=10)

    handles, labels = ax_a.get_legend_handles_labels()
    # The legend is anchored just above the top axes (top=0.90 in figure
    # coordinates) so that no empty band appears between the legend and (a);
    # with a legend height of about 0.055 in figure units its top edge is ~0.965.
    fig.legend(handles, labels, loc="upper center", ncol=5, frameon=False,
               bbox_to_anchor=(0.5, 1.00), columnspacing=0.7,
               handlelength=1.2, handletextpad=0.35)
    fig.subplots_adjust(left=0.115, right=0.995, top=0.90, bottom=0.135)
    return fig, axes


def report_overlaps(fig, axes, tol: float = 0.5) -> int:
    """Report every pair of text elements whose bounding boxes overlap.

    This is the automated check for the "labels collide" failure mode: it draws
    the figure and compares the rendered bboxes (in pixels) of all tick labels,
    axis labels, the in-panel (a)/(b)/(c) labels, the legend entries and the
    annotations.
    """
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    items = []
    for ax in axes:
        items.append(("ylabel", ax.yaxis.label, ax))
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            if t.get_text():
                items.append(("tick", t, ax))
        for t in ax.texts:
            items.append(("note", t, ax))
    leg = fig.legends[0] if fig.legends else None
    if leg is not None:
        for t in leg.get_texts():
            items.append(("legend", t, None))

    boxes = [(kind, t.get_text(), t.get_window_extent(rend), ax) for kind, t, ax in items]
    bad = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            k1, s1, b1, a1 = boxes[i]
            k2, s2, b2, a2 = boxes[j]
            # skip labels of different axes (they are separated by design) only
            # when they belong to different panels and the same panel otherwise
            if not b1.overlaps(b2):
                continue
            ov_w = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
            ov_h = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
            if ov_w > tol and ov_h > tol:
                bad += 1
                print(f"  OVERLAP {k1} {s1!r} vs {k2} {s2!r} "
                      f"({ov_w:.1f} x {ov_h:.1f} px)")
    print(f"overlap check: {bad} colliding text pair(s) among {len(boxes)} text objects")
    return bad


def report_geometry(fig, axes) -> None:
    """Print the exact spacing (in points) between the legend and panel (a),
    and between the two panel rows, together with the figure size."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    scale = 72.0 / fig.dpi                       # display px -> pt
    leg = fig.legends[0].get_window_extent(rend) if fig.legends else None
    a, b = axes[0].get_window_extent(rend), axes[1].get_window_extent(rend)
    top_ink = max(t.get_window_extent(rend).y1 for t in axes[0].texts) if axes[0].texts else a.y1
    w, h = fig.get_size_inches()
    print(f"figure: {w:.2f} x {h:.2f} in")
    if leg is not None:
        print(f"  panel (a) top -> legend bottom : {(leg.y0 - a.y1) * scale:.1f} pt "
              f"({(leg.y0 - a.y1) * scale / 2.8346:.2f} mm)")
    print(f"  panel (a) bottom -> row 2 top  : {(a.y0 - b.y1) * scale:.1f} pt "
          f"({(a.y0 - b.y1) * scale / 2.8346:.2f} mm)")
    print(f"  panel (a) height               : {a.height * scale:.1f} pt   "
          f"row 2 height: {b.height * scale:.1f} pt")


def main() -> None:
    fig, axes = build()
    report_overlaps(fig, axes)
    report_geometry(fig, axes)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    # bbox_inches="tight" is required: the shared legend sits above the axes
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT_PNG, dpi=600, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("wrote", OUT_PDF.relative_to(ROOT), "and", OUT_PNG.name)


if __name__ == "__main__":
    main()
