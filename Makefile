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
SRC+=related-work.tex
SRC+=conclusions.tex
SRC+=literature-protocol.tex
SRC+=diagnostics.tex

# The appendix literate program: woven into the article (diagnostics.tex
# above), tangled into the quiz descriptions that canvaslms pushes to Canvas.
NOWEB_SUFFIXES+=	.json

# Weave with syntax highlighting: the dbosk noweb fork's autolang/tominted
# filters typeset each chunk with minted (see the literate-programming
# skill).  The custom lexer keeps chunk references hyperlinked; it must sit
# where LaTeX runs, whitelisted by hash in ~/.config/latexminted.
NOWEAVEFLAGS.tex=	-n -delay -autolang -autodefs python3 -index \
			-filter 'tominted -lexer noweb_lexer.py'
NOWEB_LIB=	$(shell sed -n 's/^LIB=//p' "`command -v noweave`" | head -1)
noweb_lexer.py:
	cp ${NOWEB_LIB}/noweb_lexer.py $@
article.pdf: noweb_lexer.py

QUIZ_TOPICS=	course funcvars conditionals repetitions types classes \
		debugging tracing
QUIZZES=	$(foreach t,${QUIZ_TOPICS},quiz-$(t)-start.json quiz-$(t)-end.json)

.PHONY: programs
programs: ${QUIZZES} analyze_diagnostics.py
quiz-%.json: diagnostics.nw
	${NOTANGLE.json}
analyze_diagnostics.py: diagnostics.nw
	${NOTANGLE.py}
SRC+=problem-solving.tex
SRC+=tools.tex

DEPENDS+=	figs/contrast-color.tikz
DEPENDS+=	figs/generalization-color.tikz
DEPENDS+=	figs/fusion-color.tikz

DEPENDS+=	didactic.sty

article.pdf: article.tex ${SRC} ${DEPENDS}
slides.pdf: slides.tex ${SRC} ${DEPENDS}

# PythonTeX's cus_dep lives in makefiles/latexmkrc (committed in the submodule);
# latexmk loads it via the root `latexmkrc` symlink.  Depend on it so tex.mk
# creates that symlink on a fresh clone -- without it pythontex never runs and the
# PDF shows "?? PythonTeX ??".
article.pdf slides.pdf: latexmkrc

.PHONY: clean
clean:
	latexmk -C
	${RM} article.bbl article.run.xml
	${RM} diagnostics.tex noweb_lexer.py
	${RM} ${QUIZZES} analyze_diagnostics.py

INCLUDE_MAKEFILES?=./makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
INCLUDE_DIDACTIC=./didactic
include ${INCLUDE_DIDACTIC}/didactic.mk
