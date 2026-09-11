PushAround: Collaborative Path Clearing via Physics-Informed Hybrid Search
Multimedia attachment - ReadMe
======================================================================

CONTENTS
--------
video.mp4                     Simulation and hardware experiment video
                              (single video, MP4/H.264, 8.1 MB).

evaluation_data/              Per-trial evaluation records and resolved
                              configuration files of every experiment reported
                              in the revised manuscript and in the author
                              response and diff file (32 files, about 0.9 MB).

evaluation_data/make_figures.py
                              Python script that regenerates all figures of
                              the author response from the records above.

evaluation_data/plot_density_scaling_paper.py
                              Python script that regenerates the
                              obstacle-density figure of the paper (the
                              three-panel density-scaling figure) from the
                              same records and prints it as PDF/PNG.

evaluation_data/README.md     Which file backs which table or figure.

Summary.txt                   Short description of the contents, usage and
                              value of the multimedia material.

ReadMe.txt                    This file.

MINIMUM REQUIREMENTS
--------------------
* video.mp4: any player able to decode MP4/H.264, e.g. VLC media player 3.0 or
  later, Windows Media Player 12, QuickTime Player 10 or later. No additional
  codec, plugin or GPU is required.

* evaluation_data/*.csv: any spreadsheet program or text editor; the files are
  plain comma-separated text.

* evaluation_data/*.json: any text editor; the files are plain JSON text.

* evaluation_data/make_figures.py and
  evaluation_data/plot_density_scaling_paper.py: Python 3.9 or later with the packages
  numpy (tested with 1.24), pandas (tested with 1.5) and matplotlib (tested
  with 3.7). Run it from this directory:

      python evaluation_data/make_figures.py

  The first script writes the response figures into
  evaluation_data/figures/, the second writes the density figure there as well.
  Both only read the CSV/JSON files of this package; they need no network
  access, no simulator, no GPU and no further data.

CONTACT INFORMATION
-------------------
Contact information of the corresponding author is withheld in this version
because the paper is under a double-anonymous review process; it will be
provided in the final version of the paper. Until then, questions about the
multimedia material can be sent through the submission system.
