"""One-generation citation snowball over the catalogue's primary sources.

Backward: every work the seeds reference.  Forward: works citing the
seeds (OpenAlex, up to 200 per seed).  Candidates are deduplicated
against the existing corpus (both .bib files, the systematic review's
retrieved set and its decision log), then keyword-screened for
CS1-misconception relevance; the shortlist is printed with abstracts
for manual screening.
"""
import csv
import json
import re
import time
import urllib.request

MAIL = "daniel@bosk.se"
REPO = "/home/dbosk/devel/edu/research/vt-prog-misconceptions"

# Load-bearing primary misconception studies cited in the catalogue.
SEEDS = {
    "Sleeman1984": None,  # ERIC report, no DOI
    "Kohn2017": "10.1145/3017680.3017724",
    "Plass2015": None,                            # thesis, no DOI
    "GuoMarkelZhang2020": "10.1145/3386527.3406733",
    "Bosse2021": "10.48550/arXiv.2104.12542",
    "Kaczmarczyk2010": "10.1145/1734263.1734299",
    "Eckert2022": "10.1109/FIE56618.2022.9962545",
    "Gobil2009": "10.1109/ICEEI.2009.5254715",
    "KumarVeerasamy2016": "10.1177/0047239515627263",
    "Sekiya2013": "10.1145/2526968.2526978",
    "AltadmriBrown2015": "10.1145/2676723.2677258",
    "Ragonis2005": "10.1080/08993400500224310",
    "Esche2025": "10.1145/3724363.3729065",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"snowball ({MAIL})"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def invert(inv):
    if not inv:
        return ""
    words = {}
    for word, positions in inv.items():
        for p in positions:
            words[p] = word
    return " ".join(words[k] for k in sorted(words))


# The existing corpus, by DOI (lowercased, bare) and by normalised title.
def norm_doi(d):
    d = (d or "").lower().strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


corpus_dois, corpus_titles = set(), set()
for path in ("misconceptions.bib", "theory.bib",
             "literature-review/misconceptions-systematic.retrieved.bib"):
    text = open(f"{REPO}/{path}").read()
    for d in re.findall(r"doi\s*=\s*\{([^}]*)\}", text):
        corpus_dois.add(norm_doi(d))
    for t in re.findall(r"title\s*=\s*\{+([^}]*)\}", text):
        corpus_titles.add(norm_title(t))
for row in csv.DictReader(open(f"{REPO}/literature-review/misconceptions-systematic.decisions.csv")):
    corpus_dois.add(norm_doi(row.get("doi")))
    corpus_titles.add(norm_title(row.get("title")))
corpus_dois.discard("")
corpus_titles.discard("")

backward, forward = {}, {}
seed_ids = {}
stats = {}
for name, doi in SEEDS.items():
    if not doi:
        stats[name] = "no DOI (thesis); skipped"
        continue
    try:
        work = get(f"https://api.openalex.org/works/doi:{doi}?select=id,referenced_works,cited_by_count,title")
    except Exception as e:
        stats[name] = f"lookup failed: {e}"
        continue
    wid = work["id"].rsplit("/", 1)[-1]
    seed_ids[name] = wid
    refs = work.get("referenced_works") or []
    for r in refs:
        backward.setdefault(r.rsplit("/", 1)[-1], set()).add(name)
    # forward: up to 200 citing works
    try:
        citing = get(
            "https://api.openalex.org/works?filter=cites:" + wid
            + "&per-page=200&select=id,doi,title,publication_year,cited_by_count,abstract_inverted_index"
        )
    except Exception as e:
        stats[name] = f"refs {len(refs)}; cited_by fetch failed: {e}"
        continue
    n_cite = citing["meta"]["count"]
    for w in citing["results"]:
        forward.setdefault(w["id"].rsplit("/", 1)[-1], {"work": w, "seeds": set()})["seeds"].add(name)
    stats[name] = f"refs {len(refs)}; cited-by {n_cite} (fetched {len(citing['results'])})"
    time.sleep(0.3)

print("== seed stats ==")
for name, s in stats.items():
    print(f"  {name}: {s}")
print(f"backward pool: {len(backward)} distinct works")
print(f"forward pool:  {len(forward)} distinct works")

# Resolve backward works in batches for titles/DOIs.
back_meta = {}
ids = list(backward)
for i in range(0, len(ids), 50):
    batch = "|".join(ids[i:i + 50])
    try:
        res = get(f"https://api.openalex.org/works?filter=openalex_id:{batch}"
                  "&per-page=50&select=id,doi,title,publication_year,cited_by_count,abstract_inverted_index")
    except Exception as e:
        print("batch failed:", e)
        continue
    for w in res["results"]:
        back_meta[w["id"].rsplit("/", 1)[-1]] = w
    time.sleep(0.3)

KEYWORDS = re.compile(
    r"misconcept|novice|introductory programming|CS1|programming error|"
    r"mental model|notional machine|program comprehension|learn.{0,12}program",
    re.IGNORECASE,
)

candidates = []
for wid, seeds in backward.items():
    w = back_meta.get(wid)
    if not w:
        continue
    candidates.append((w, seeds, "backward"))
for wid, entry in forward.items():
    candidates.append((entry["work"], entry["seeds"], "forward"))

new, dup, offtopic = [], 0, 0
seen_ids = set()
for w, seeds, direction in candidates:
    wid = w["id"].rsplit("/", 1)[-1]
    if wid in seen_ids:
        continue
    seen_ids.add(wid)
    if norm_doi(w.get("doi")) in corpus_dois or norm_title(w.get("title")) in corpus_titles:
        dup += 1
        continue
    text = (w.get("title") or "") + " " + invert(w.get("abstract_inverted_index"))
    if not KEYWORDS.search(text):
        offtopic += 1
        continue
    new.append((w, sorted(seeds), direction))

print(f"\ncandidates: {len(seen_ids)} distinct; already in corpus: {dup}; "
      f"keyword-screened out: {offtopic}; shortlist: {len(new)}")
new.sort(key=lambda x: -(x[0].get("cited_by_count") or 0))
out = []
for w, seeds, direction in new:
    out.append({
        "title": w.get("title"),
        "year": w.get("publication_year"),
        "doi": w.get("doi"),
        "cited_by": w.get("cited_by_count"),
        "via": seeds,
        "direction": direction,
        "abstract": invert(w.get("abstract_inverted_index"))[:600],
    })
json.dump(out, open("/tmp/claude-1000/-home-dbosk-devel-edu-research-vt-prog-misconceptions/cb99ed3a-3b0a-4f53-9322-71881cb09d90/scratchpad/snowball-shortlist.json", "w"), indent=1)
print("shortlist written")
