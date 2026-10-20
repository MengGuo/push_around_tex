#!/usr/bin/env python3
"""Build the final response and the latest manuscript with selected blue text."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ral_final_submit"


def run(args: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {args}\n{result.stdout[-6000:]}\n{result.stderr}")
    return result.stdout


def compile_tex(folder: Path, job: str, entry: str, bibliography: bool) -> None:
    args = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-jobname={job}", entry]
    run(args, folder)
    if bibliography:
        run(["bibtex", job], folder)
    run(args, folder)
    # Float movement can require another pass for stable labels.
    for _ in range(3):
        log = (folder / f"{job}.log").read_text(errors="replace")
        if not re.search(r"Rerun to get|Please rerun|Label\(s\) may have changed", log):
            break
        run(args, folder)
    log = (folder / f"{job}.log").read_text(errors="replace")
    problems = [line for line in log.splitlines()
                if re.search(r"^!|Overfull|undefined|Rerun to get|Please rerun|Label\(s\) may have changed", line)]
    if problems:
        raise RuntimeError(f"Resolve {folder / (job + '.log')}:\n" + "\n".join(problems))


def optimize_pdf(sources: list[Path], target: Path) -> None:
    run(["gs", "-q", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5",
         "-dNOPAUSE", "-dBATCH", "-dSAFER", "-dEmbedAllFonts=true",
         "-dSubsetFonts=true", "-dCompressFonts=true", "-dDetectDuplicateImages=true",
         "-dPassThroughJPEGImages=true", "-dDownsampleColorImages=false",
         "-dDownsampleGrayImages=false", "-dDownsampleMonoImages=false",
         "-dAutoFilterColorImages=false", "-dColorImageFilter=/DCTEncode",
         "-dAutoFilterGrayImages=false", "-dGrayImageFilter=/FlateEncode", "-dJPEGQ=95",
         f"-sOutputFile={target}", *map(str, sources)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manuscript-built", action="store_true",
                        help="reuse the manuscript just compiled by build_final.sh")
    args = parser.parse_args()
    for program in ["pdflatex", "bibtex", "pdftotext", "pdfinfo", "gs"]:
        if not shutil.which(program):
            raise RuntimeError(f"Required program missing: {program}")
    OUT.mkdir(exist_ok=True)
    manuscript = ROOT / "ral_tex"
    if not args.manuscript_built:
        compile_tex(manuscript, "root", "root.tex", True)
    marked = manuscript / "root.pdf"
    clean = manuscript / "root_clean.pdf"
    if run(["pdftotext", "-layout", str(marked), "-"]) != run(
            ["pdftotext", "-layout", str(clean), "-"]):
        raise RuntimeError("Marked/clean manuscript text differs; rebuild with bash build_final.sh")
    pages = re.search(r"^Pages:\s+(\d+)", run(["pdfinfo", str(marked)]), re.MULTILINE).group(1)
    if int(pages) > 8:
        raise RuntimeError("Marked manuscript exceeds eight pages")
    optimize_pdf([marked], OUT / "root_diff.pdf")
    with tempfile.TemporaryDirectory(prefix="pusharound_final_review_") as temporary:
        work = Path(temporary)
        compile_tex(ROOT / "response", "response", "response.tex", False)
        shutil.copy2(ROOT / "response/response.pdf", OUT / "response.pdf")
        merged = work / "response_and_diff.pdf"
        # Encode the raw marked paper once for each deliverable.
        optimize_pdf([OUT / "response.pdf", marked], merged)
        expected = run(["pdftotext", "-layout", str(OUT / "response.pdf"), "-"]) + run(
            ["pdftotext", "-layout", str(OUT / "root_diff.pdf"), "-"])
        if run(["pdftotext", "-layout", str(merged), "-"]) != expected:
            raise RuntimeError("Merged response/diff text differs from the component PDFs")
        shutil.copy2(merged, OUT / "response_and_diff.pdf")

    for name in ["response.pdf", "root_diff.pdf", "response_and_diff.pdf"]:
        path = OUT / name
        if path.stat().st_size > 5_000_000:
            raise RuntimeError(f"Review PDF exceeds 5 MB: {path}")
        pages = re.search(r"^Pages:\s+(\d+)", run(["pdfinfo", str(path)]), re.MULTILINE).group(1)
        print(f"{path.relative_to(ROOT)}: {pages} pages, {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
