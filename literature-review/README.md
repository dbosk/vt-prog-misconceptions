# Literature review artifacts

Archived artifacts from the **systematic phase** of the misconceptions literature
review (the protocol is documented in `literature-protocol.tex`, the appendix of
the paper). These make the review auditable and reproducible.

The systematic phase used the [`scholar`](https://github.com/dbosk/scholar) tool:
a multi-database search with LLM-assisted screening against explicit
inclusion/exclusion criteria.

## Files

| File | What it is |
|------|------------|
| `misconceptions-systematic.session.json` | The authoritative `scholar` review session: every query, retrieved paper, and screening decision. Restore with `scholar`. |
| `misconceptions-systematic.decisions.csv` | Human-readable export of all retrieved papers with status (`kept`/`discarded`), abstracts, providers, and screening reasons. |
| `misconceptions-systematic.retrieved.bib` | BibTeX of all retrieved papers. |

## Summary

- Providers searched: OpenAlex, arXiv, Web of Science, Scopus, IEEE Xplore
  (Semantic Scholar and DBLP were configured but unproductive in this run — see
  the limitations in `literature-protocol.tex`).
- Retrieved: 117 unique papers (after de-duplication).
- Screened (LLM-assisted): 24 kept, 93 discarded.
- Of the kept set, 23 were new relative to the manual (baseline) review; the one
  overlap is the field survey `MisconceptionsSurvey2017`.

## Reproducing

The exact queries and criteria are listed in `literature-protocol.tex`. To
re-run or extend the session:

```sh
# Inspect / re-export the archived session (after importing it into scholar):
scholar sessions list
scholar sessions export misconceptions-systematic -f all

# Re-run a query (appends to the named session):
scholar search "misconceptions introductory programming" \
  -p s2 -p openalex -p dblp -p arxiv -p wos -p ieee -p scopus \
  -n misconceptions-systematic
```

Per-citation provenance (how each cited reference was found and the verbatim
passage that supports it) lives in the provenance comment blocks in
`../misconceptions.bib`, validated by the `backing-claims` skill's
`check_provenance.py`.
