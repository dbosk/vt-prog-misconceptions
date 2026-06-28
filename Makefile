LATEXFLAGS=		-shell-escape
TEX_PYTHONTEX=	yes

.PHONY: all
all: article.pdf slides.pdf

SRC+=theory.bib
SRC+=misconceptions.bib
SRC+=preamble.tex

SRC+=introduction.tex
SRC+=background.tex
SRC+=method.tex

SRC+=results-overview.tex

SRC+=functions-variables.tex
SRC+=debugging.tex

SRC+=conditionals.tex
SRC+=repetitions.tex
SRC+=types.tex
SRC+=classes.tex
SRC+=findings.tex
SRC+=literature-protocol.tex
SRC+=problem-solving.tex
SRC+=tools.tex

DEPENDS+=	figs/contrast-color.tikz
DEPENDS+=	figs/generalization-color.tikz
DEPENDS+=	figs/fusion-color.tikz

DEPENDS+=	didactic.sty

article.pdf: article.tex ${SRC} ${DEPENDS}
slides.pdf: slides.tex ${SRC} ${DEPENDS}

# PythonTeX needs latexmk to load `latexmkrc` (a symlink to makefiles/latexmkrc),
# which provides the pytxcode->pytxmcr cus_dep.  Without it pythontex never runs
# and the PDF shows "?? PythonTeX ??".  makefiles/latexmkrc is committed in the
# submodule, but as a fallback we tangle it if a checkout lacks it -- existence
# only (no .nw prerequisite), so a committed copy is never re-tangled.  Depending
# on the symlink makes tex.mk create it on a fresh clone.
makefiles/latexmkrc:
	notangle -R'[[latexmkrc]]' makefiles/tex.mk.nw > $@

article.pdf slides.pdf: latexmkrc
latexmkrc: | makefiles/latexmkrc

.PHONY: clean
clean:
	latexmk -C
	${RM} article.bbl article.run.xml

INCLUDE_MAKEFILES?=./makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
INCLUDE_DIDACTIC=./didactic
include ${INCLUDE_DIDACTIC}/didactic.mk
