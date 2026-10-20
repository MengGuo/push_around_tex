PushAround: Collaborative Path Clearing via Physics-Informed Hybrid Search
RA-L 26-3602 - Final multimedia attachment

CONTENTS AND REQUIREMENTS
PushAround.mp4: Single video of simulation, hardware, physical-parameter
mismatch, and robot-team scaling experiments. Approximately 4 minutes 31 seconds,
1920 x 1080; 23.41 MB. Use VLC media player 3.0 or later with MP4 support.
No simulator is needed to view the video.

evaluation_data/: Evaluation records and plotting scripts retained from the
reviewed second-submission attachment. CSV and JSON files can be read with a
text editor; CSV files can also be opened in spreadsheet software.
The included README.md maps the records to the final manuscript.
These are evaluation data and plotting scripts, not the complete planner code.

To regenerate plots, use Python 3.9 or later with numpy, pandas and matplotlib:
  python evaluation_data/make_figures.py
  python evaluation_data/plot_density_scaling_paper.py
Run these commands from the extracted attachment directory. Output is written
to evaluation_data/figures/. The first script reproduces plots from the
second-submission response, not the final response (which has no figures).
No network access, simulator or GPU is required.

Summary.txt: Description of the contents, usage and value.

CONTACT
Meng Guo (corresponding author)
School of Advanced Manufacturing and Robotics
Peking University, Beijing 100871, China
E-mail: meng.guo@pku.edu.cn
