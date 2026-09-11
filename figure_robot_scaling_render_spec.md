# Render spec: four robot-scaling panels for the 2x4 composite figure

**Objective.** The paper's dense-clutter figure (Fig. 8, `ral_tex/figures/dense.png`)
is a **2 rows x 4 columns** montage (2020 x 1008 px). It will be recomposed so
that the **left two columns** keep the obstacle-density panels (M = 45, 2
robots; recomposed by the authors from their own montage, no re-rendering
needed) and the **right two columns** show the new **robot-team scaling** study
(M = 30, **N = 4** robots, with the current code). The overall footprint stays
2 x 4, so no page-space change is involved.

**Deliverable: exactly four PNG panels** for the right-hand 2 x 2 block.

---

## 1. Panel content (2 rows x 2 columns)

| panel | file suffix | content |
|---|---|---|
| top-left | `R1_init`  | **Global, t = 0.** Whole 8 x 8 m workspace: 30 movable objects, the immovable bar obstacles, the 4 robots at their initial poses, start and goal marked, the W-clearance disk of the external vehicle drawn, and the WCCG overlay with the start face in blue. |
| top-right | `R2_final` | **Global, final.** Same camera and orientation as `R1_init`, at the moment the W-clear path is established: the cleared corridor, the enlarged blue start face now containing the goal (caption will state the time). |
| bottom-left | `R3_pre` | **Local, pre-contact.** Tight crop (field of view about 2.5-3 m) around the robots and the object of one representative push task, captured just before contact. |
| bottom-right | `R4_push` | **Local, during the push.** Same camera and same field of view as `R3_pre`, at the moment of maximum contact/object motion of the same task, so the two frames read as a before/after pair. |

Rules:

* The two global panels must share one camera; the two local panels must share
  another. Do not change the world orientation between panels.
* In the local panels keep the whole robot bodies and the pushed object inside
  the frame; annotate the contact points, the push direction and the target gap.
* Optional and encouraged: re-run the chosen seed once with
  `DEBUG_MODEGEN_DIAG=1` in `child_env` (it enables prints only, it does not
  change behaviour - the flag used for
  `data/robot_scaling_baselines_postfix/`). If a **per-task robot release** is
  located, use that task for `R3`/`R4` and show **three of the four robots in
  contact** (the fourth holding its pose). That single pair then illustrates the
  mechanism described in Sec. III-C2. Report whether this was used.

## 2. Geometry to match (measured from the existing density montage)

The density panels of `dense.png` are:

* montage 2020 x 1008 px, 4 columns of about **480 px** and 2 rows of about
  **500 px**;
* therefore one panel is about **480 x 500 px**, i.e. nearly square
  (height/width ~ 0.96).

**The robot panels must match this panel geometry**, so the composite is
seamless:

* deliver **square-ish panels with height/width ~ 0.96** (480 x 500 aspect);
* deliver them at a higher resolution of the same aspect, e.g.
  **1440 x 1500 px** (or 960 x 1000 px minimum), PNG, no border, no title, no
  caption burned in;
* use the same rendering style as the existing density panels: same PyBullet
  camera style and view angle, same floor/object/robot colours, same WCCG
  overlay style. Reuse whatever rendering function produced `dense.png`.

## 3. Legibility constraint (important)

In the paper the montage is placed at 0.8 column width, i.e. about 2.7 in wide,
so **each panel is only about 0.68 in wide** (about 17 mm). Consequences:

* crop the local panels **very tightly** - the robots and the pushed object
  should fill the frame; do not show more than roughly 3 m of world width;
* annotate with symbols and one- or two-word labels only (`R1`...`R4`, `gap`,
  `start`, `goal`); no sentences inside the images;
* use thick arrows and high-contrast colours (colourblind-safe: avoid
  red-on-green), because thin lines vanish at this size;
* the same panels may also be reused if the figure is later enlarged to full
  width, so keeping the resolution high costs nothing.

## 4. Which run to render

PushAround (ours), **N = 4**, M = 30, 8 x 8 m, nominal physics, **post-fix code**
(commit `43c8d62` or later, i.e. with the shared mode-generation refinements).

Representative trial, not a best case: **seed 4**
(`data/robot_scaling_modefix/raw_results_all.csv`: planning 21.4 s, execution
105.5 s, 10 push tasks, 4372 control steps). Alternative: **seed 9**
(planning 31.2 s, execution 137.3 s), which is closest to the reported mean
execution time of 110.1 s. All ten N = 4 seeds succeed, so the choice only
affects timing; the caption will state the seed that is used.

## 5. Deliverables and what to report back

Deliver to a folder of your choice (e.g. `data/robot_scaling_figures/`):

```
fig_N4_seed<k>_R1_init.png      1440 x 1500 px
fig_N4_seed<k>_R2_final.png     1440 x 1500 px
fig_N4_seed<k>_R3_pre.png       1440 x 1500 px
fig_N4_seed<k>_R4_push.png      1440 x 1500 px
notes.md
```

`notes.md` must state, for the caption:

* seed, M, N, code revision;
* simulation time (and/or control step) of each of the four frames;
* the index of the push task shown in `R3`/`R4`, and its target object;
* total number of push tasks and the execution time of the run;
* the world coordinates and the extent (in metres) of the local crop;
* whether the per-task robot release was active in the shown task;
* confirmation that both globals share one camera and both locals share another.
