This folder contains the material for the revised submission.

FILES
-----

* "root.pdf"              - revised manuscript with all changes of this
                            revision highlighted in blue (8 pages).

* "root_clean.pdf"        - the same revised manuscript with the highlighting
                            removed, for reading and later production (8 pages).

* "response_and_diff.pdf" - the file required by the RA-L guidelines for a
                            "Revise and Resubmit" decision: a single PDF that
                            contains (1) the detailed point-by-point response to
                            the Associate Editor and to Reviewers 3 and 4,
                            followed by (2) the revised paper with the changes
                            highlighted in blue (22 pages in total: 14 + 8).

* "response.pdf"          - the response letter alone, 14 pages (identical to the
                            leading part of "response_and_diff.pdf"), for
                            convenience. Every listed manuscript change is
                            located by page and section, and the figures that
                            changed are shown as original versus revised.

* "PushAround.mp4"        - the experiment video (also included inside
                            "multimedia.zip" as "video.mp4"): corridor clearing in
                            simulation, hardware execution, the planner-execution
                            physical-parameter mismatch study, and robot-number
                            scaling with two, three and four robots.

* "multimedia.zip"        - the multimedia attachment (9.9 MB, below the 50 MB
                            limit of the guidelines). It contains:
                              - video.mp4 (one video, as required),
                              - ReadMe.txt (minimum software requirements and
                                contact information, as required),
                              - Summary.txt (contents, usage and value of the
                                multimedia objects, as required),
                              - evaluation_data/ : the per-trial records and
                                resolved configuration files behind every number
                                of the manuscript and of the response, plus a
                                script that regenerates all response figures from
                                them (datasets and source code are explicitly
                                welcome as RA-L multimedia material; no
                                supplemental text or figures are included).

* "README.txt"            - this file.

* "cover.txt"             - cover letter to the Editor-in-Chief.

NOTES
-----

* Structure of the revision: it adds the WCCG connectivity validation, the
  planner-execution physics-mismatch study, the ten-seed obstacle-density
  statistics and the robot-team scaling study, and clarifies the search
  guarantees, the objective, the hardware force interface, the execution monitor
  and the comparison protocol. All of these changes are marked in blue in
  "root.pdf".

* The paper is 8 pages, which is the maximum allowed length for an RA-L Letter
  (six pages plus up to two extra pages, the latter subject to overlength page
  charges).

* Neither the manuscript nor the response file contains author names,
  affiliations, funding information or links, in accordance with the
  double-anonymous review process. Author contact information is likewise
  withheld inside the multimedia attachment and will be provided in the final
  version.

* The multimedia attachment contains datasets and source code only; it does not
  contain supplemental text or figures, so it does not circumvent the page
  limit.

* All files in this folder are generated, not versioned. Rebuild them from the
  source with ./build.sh (see docs/revision_playbook.md, section 8).
