compile:
	rm -rf *.aux *.bbl *.blg *.log *.toc
	pdflatex root.tex
	bibtex root
	pdflatex root.tex
	pdflatex root.tex
	pdflatex root.tex

follow:
	latexmk -pvc -pdf -bibtex -pdflatex="pdflatex --shell-escape %O %S" root.tex

wordcount:
	texcount -utf8 -total -sum root.tex

clean:
	rm -f *.aux
	rm -f *.fdb_latexmk
	rm -f *.fls
	rm -f *.log
	rm -f *.bbl
	rm -f *.blg
	rm -f *.out
	rm -f *.brf
	rm -f *.acn
	rm -f *.glg
	rm -f *.glo
	rm -f *.gls
	rm -f *.ist
	rm -f *.lof
	rm -f *.lot
	rm -f *.toc
	rm -f *.bcf
	rm -f *.run.xml
