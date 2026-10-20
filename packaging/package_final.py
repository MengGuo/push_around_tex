#!/usr/bin/env python3
"""Assemble production archives without modifying the frozen second submission."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
import difflib
import hashlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ral_final_submit"


def run(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.STDOUT)


def archive(folder, target, limit):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(folder))
    assert target.stat().st_size < limit, f"{target.name} exceeds upload limit"
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
    print(target.name, target.stat().st_size, "bytes")


with tempfile.TemporaryDirectory(prefix="pusharound-final-") as tmp:
    tmp = Path(tmp)
    src = tmp / "source"
    src.mkdir()
    # Include only inputs actually referenced by the manuscript.
    pending = ["root.tex"]
    seen = set()
    figures = set()
    while pending:
        rel = pending.pop()
        if rel in seen:
            continue
        seen.add(rel)
        text = (ROOT / "ral_tex" / rel).read_text()
        active = re.sub(r"(?<!\\)%[^\n]*", "", text)
        pending.extend(re.findall(r"\\input\{([^}]+)\}", active))
        figures.update(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", active))
        # Production entry point always compiles without revision colors.
        if rel == "root.tex":
            text = "\\def\\CLEANCOPY{}\n" + text
        for figure in figures:
            if figure.endswith(".png"):
                text = text.replace("{" + figure + "}", "{" + figure[:-4] + ".pdf}")
        dest = src / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
    (src / "figures").mkdir(exist_ok=True)
    for figure in sorted(figures):
        original = ROOT / "ral_tex" / figure
        if original.suffix == ".png":
            # pdfTeX embeds PNG pixels losslessly, including alpha masks;
            # standalone gives an image-only PDF with the same aspect ratio.
            conv = tmp / original.stem
            conv.mkdir()
            shutil.copy2(original, conv / "image.png")
            (conv / "image.tex").write_text(
                "\\documentclass[border=0pt]{standalone}\n"
                "\\usepackage{graphicx}\n"
                "\\begin{document}\\includegraphics{image.png}\\end{document}\n"
            )
            run("pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                "image.tex", cwd=conv)
            shutil.copy2(conv / "image.pdf", src / Path(figure).with_suffix(".pdf"))
        else:
            shutil.copy2(original, src / figure)
    shutil.copy2(ROOT / "ral_tex/contents/references.bib", src / "contents/references.bib")
    for filename in ("IEEEtran.cls", "IEEEtran.bst"):
        shutil.copy2(run("kpsewhich", filename).decode().strip(), src / filename)
    (src / "README.txt").write_text(
        "PushAround - RA-L 26-3602 final production source\n"
        "Entry point: root.tex (clean publication copy; no revision highlighting).\n"
        "Build with a complete TeX Live installation:\n"
        "  pdflatex root.tex\n  bibtex root\n  pdflatex root.tex\n  pdflatex root.tex\n"
        "All 11 figures are included as PDF. Raster figures are embedded losslessly,\n"
        "without resampling. References are supplied as both .bib and .bbl.\n"
        "Corresponding author: Meng Guo, meng.guo@pku.edu.cn\n"
    )
    # Build in a separate directory so the archive stays free of auxiliary files.
    check = tmp / "source-check"
    shutil.copytree(src, check)
    run("pdflatex", "-interaction=nonstopmode", "-halt-on-error", "root.tex", cwd=check)
    run("bibtex", "root", cwd=check)
    for _ in range(2):
        run("pdflatex", "-interaction=nonstopmode", "-halt-on-error", "root.tex", cwd=check)
    log = (check / "root.log").read_text()
    assert not re.search(r"^!|Overfull|undefined", log, re.M), "Resolve source build warnings"
    packaged_text = run("pdftotext", "-layout", str(check / "root.pdf"), "-").decode()
    # Compare before Ghostscript optimization: font coordinate rounding during
    # optimization can change pdftotext's ordering of mathematical accents.
    final_text = run("pdftotext", "-layout", str(ROOT / "ral_tex/root_clean.pdf"), "-").decode()
    if packaged_text != final_text:
        print("".join(difflib.unified_diff(final_text.splitlines(True),
                                          packaged_text.splitlines(True)))[:8000])
        raise AssertionError("Packaged source differs from publication PDF")
    shutil.copy2(check / "root.bbl", src / "root.bbl")
    archive(src, OUT / "source.zip", 10_000_000)
    print("Independent source build matches final PDF text and pagination.")

    media = tmp / "multimedia"
    media.mkdir()
    shutil.copytree(ROOT / "ral_2nd_submit/multimedia_src/evaluation_data",
                    media / "evaluation_data")
    for name in ("ReadMe.txt", "Summary.txt"):
        shutil.copy2(ROOT / "packaging/final_multimedia" / name, media / name)
    shutil.copy2(ROOT / "packaging/final_multimedia/evaluation_README.md",
                 media / "evaluation_data/README.md")
    shutil.copy2(OUT / "PushAround.mp4", media / "PushAround.mp4")
    archive(media, OUT / "multimedia.zip", 50_000_000)
    with zipfile.ZipFile(OUT / "multimedia.zip") as z:
        assert z.read("PushAround.mp4") == (OUT / "PushAround.mp4").read_bytes()
    print("Updated video preserved byte-for-byte; reviewed evaluation records retained.")

files = ("root.pdf", "source.zip", "multimedia.zip", "response.pdf",
         "root_diff.pdf", "response_and_diff.pdf", "PushAround.mp4")
(OUT / "SHA256SUMS.txt").write_text("".join(
    hashlib.sha256((OUT / name).read_bytes()).hexdigest() + "  " + name + "\n"
    for name in files
))
