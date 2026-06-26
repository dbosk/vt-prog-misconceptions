# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An academic paper, *"Introductory programming through the lens of variation
theory"* (Soori & Bosk), cataloguing introductory-programming misconceptions and
analysing how to teach against them using phenomenography and variation theory.
The source is LaTeX; there is no application code.

## Build

```sh
make            # builds both article.pdf and slides.pdf
make article.pdf
make slides.pdf
make clean      # latexmk -C plus stray bbl/run.xml
```

The build uses `latexmk` with `-shell-escape` and PythonTeX enabled (see the
`LATEXFLAGS`/`TEX_PYTHONTEX` vars in `Makefile`). Build machinery is *not* in this
repo — it comes from the `makefiles/` git submodule (`makefiles/tex.mk`) and the
`didactic/` submodule (`didactic/didactic.mk`). After a fresh clone you must:

```sh
git submodule update --init --recursive
```

LaTeX intermediates and `minted` output go to `ltxobj/` (the `outputdir`);
`article.pdf`/`slides.pdf` at the root are symlinks into `ltxobj/`. Both `ltxobj/`
and the generated `didactic.sty` symlink are gitignored.

Requires a TeX distribution with `minted` (hence Pygments / `-shell-escape`),
`pythontex`, `biber`, and the packages listed in `preamble.tex`.

## Architecture: one source, two outputs

The single most important thing to know: **the content `.tex` files are compiled
twice from the same source** — once as a prose article and once as Beamer slides.

- `article.tex` — loads `beamerarticle` (+`\setjobnamebeamerversion{slides}`), so
  `frame` environments render as normal prose. This is the paper/handout.
- `slides.tex` — `\documentclass{beamer}`, the slide deck.
- Both `\input` the **same** preamble (`preamble.tex`) and the **same** content
  files (`introduction.tex`, `background.tex`, `method.tex`,
  `functions-variables.tex`, `debugging.tex`, `conditionals.tex`,
  `repetitions.tex`, `types.tex`, `classes.tex`, `findings.tex`, …).

Consequences when editing any content file:
- `\mode*` at the top of a file and `\mode<all>{\input{...}}` in the drivers
  control what appears in which output — preserve them.
- Material inside `\begin{frame}…\end{frame}` is slide content (shown inline in
  the article via `beamerarticle`); prose outside frames is article-only context.
- Overlay specs (`<1-3>`, `\pause`, `<+>`) are Beamer overlays — harmless in the
  article, meaningful in slides.
- The driver file lists (`article.tex`, `slides.tex`) and the `SRC+=` list in
  `Makefile` must stay in sync when adding/removing a content file.

`abstract.tex` is shared by both drivers. The appendix sections (with
`problem-solving.tex`, `tools.tex`) are article-only; in `slides.tex` they are
commented out.

## Content conventions

- **One content file per topic area** of misconceptions. Each typically alternates
  prose explanation, a `frame` stating the misconception (with citations), and a
  variation-theory analysis (critical aspects, dimensions of variation, contrast
  /generalisation/fusion patterns).
- **Citations** use `biblatex` (biber backend, authoryear-comp). The default cite
  command is `\parencite` (set via `\SetCiteCommand`); `\footcite`/`\textcite` are
  also used. Bibliography lives in `misconceptions.bib` and `theory.bib`.
- **The `didactic` package** (`\usepackage{didactic}`, from the submodule) provides
  semantic theorem-like environments used throughout (`misconception`-style
  blocks, `assumption`, `remark`, `exercise`, `activity`, `question`) plus macros
  for side-by-side code+output and the `\ltnote` instructor-note command. It is
  colour-coded under Beamer and renders as plain blocks under `beamerarticle`.
- **Code listings**: `minted` (and `listings`) for static code; `pythontex` for
  code whose output is executed and embedded. Runnable example snippets live in
  `examples/` (Python, one C++); `pythontex` working dir is the parent (`..`).
- **Quotes/refs**: `csquotes` — use `\enquote{...}`, not raw quotes;
  `\textcquote`/`\blockcquote` for cited quotations. `cleveref` — use `\cref{}`.
- **Variation-theory figures** are TikZ in `figs/` (`contrast-color.tikz`,
  `generalization-color.tikz`, `fusion-color.tikz`, `vt-terms.*`), listed as
  `DEPENDS` in `Makefile`.

## Submodules

- `makefiles/` → https://github.com/dbosk/makefiles.git — the build system
  (`tex.mk` etc.). The `.nw` files there are noweb literate sources; the `.mk`
  files are the tangled output actually included.
- `didactic/` → https://github.com/dbosk/didactic.git — the LaTeX package; `make`
  in this repo builds `didactic.sty` from it.

Treat both as upstream: change them in their own repos, not here.
