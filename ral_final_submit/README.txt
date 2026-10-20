PushAround: Collaborative Path Clearing via Physics-Informed Hybrid Search
RA-L manuscript 26-3602 - final submission preparation, October 21, 2026

FILES
-----
root.pdf                 Clean final manuscript with author affiliations: 8 pages, 2.77 MB.
                         Use this as the publication manuscript.

response.pdf             Point-by-point response to the version-2 publication
                         decision: 5 pages. Refers to clean-manuscript page numbers.

root_diff.pdf            Latest manuscript with selected blue marking: 8 pages.
                         Only clarifications addressing the current reviewers'
                         comments are blue. Previous-round edits, publication
                         metadata, and editorial shortening are black. No old
                         text, underlining, or strikeout is displayed. Text and
                         pagination match the clean publication manuscript.

response_and_diff.pdf    Response followed by the marked paper: 13 pages, 2.83 MB.

PushAround.mp4           Author-provided video with the updated cover.
                         Original file retained without transcoding (23.41 MB).

source.zip               Production LaTeX source and 11 PDF figures (9.61 MB).
                         Builds the clean eight-page manuscript.

multimedia.zip           Updated original video, ReadMe.txt, Summary.txt and
                         reviewed evaluation data (22.68 MB).

BUILD
-----
Run `bash build_final.sh` from the repository root to rebuild all four PDFs
and both ZIP archives. To package existing PDFs: python3 packaging/package_final.py.
The script preserves the frozen ral_2nd_submit/ package and the video.

In ral_tex/root.tex, the previous-round `change` wrapper now prints black;
`minorchange` marks the current reviewer-requested clarifications in blue.
The response source is response/response.tex. Its previous contents are preserved in
response/archive/response_before_final_round.tex.

Local publication archives are assembled and validated. Copyright transfer must
be completed through the IEEE Electronic Copyright Form linked by PaperCept.
Author metadata, the final abstract, keywords and page-charge agreement must
be checked in the submission system. No files have been submitted by these scripts.
Only the PaperCept status "Final MS received" confirms completed submission.
See ../docs/final_audit_zh.md for the review audit and the unresolved historical
quick-pass implementation provenance limitation.
