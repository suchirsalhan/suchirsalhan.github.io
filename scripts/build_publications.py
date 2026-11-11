#!/usr/bin/env python3
"""Render the publication catalogue on research.html from assets/data/publications.json.

Usage (from the repository root; Python 3 standard library only):

    python3 scripts/build_publications.py
        Re-render research.html from the JSON. Idempotent: running it twice
        produces identical output.

    python3 scripts/build_publications.py --merge-links verified.json
        First merge verified paper URLs into publications.json, then re-render.
        verified.json is an object keyed by publication id ("pub-beetle", ...):
            {"pub-beetle": {"acl_anthology_url": "...", "arxiv_url": null,
                            "google_scholar_url": "...", "doi": "..."}}
        Only non-null values overwrite; each merged entry gets "verified": true.

    python3 scripts/build_publications.py --check
        Render in memory and exit 1 if research.html is out of date.

What it writes (everything else in research.html is hand-written):
    <!-- AUTO:start-here:start -->   ... <!-- AUTO:start-here:end -->
        The five featured papers ("featured": 1..5 in the JSON).
    <!-- AUTO:publications:start --> ... <!-- AUTO:publications:end -->
        Search/filter controls (hidden until assets/js/publications.js runs)
        and the full static catalogue, grouped by type, newest first.

The primary paper link comes from get_primary_publication_url(): the first
non-null of acl_anthology_url -> arxiv_url -> google_scholar_url. The title link
and the "Read the paper" link both use it. Project, code, poster, slides and
write-up links are kept separate. Never invent anthology or arXiv IDs here: add
them to the JSON (or a --merge-links file) only once they are verified.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "publications.json")
PAGE = os.path.join(ROOT, "research.html")
ME = "Suchir Salhan"

TOPICS = [
    ("devinterp", "Learning dynamics & developmental interpretability"),
    ("sample-efficient", "Sample-efficient learning"),
    ("multilingual", "Multilingual & bilingual AI"),
    ("tokenisation", "Tokenisation & adaptive computation"),
    ("representations", "Representation convergence & model merging"),
    ("linguistics", "Linguistics & cognitive science"),
    ("evaluation", "Evaluation, safety & alignment"),
]
TOPIC_LABEL = dict(TOPICS)
TYPES = [
    ("conference", "Conference & journal", "Peer-reviewed conference and journal publications", "conference-papers"),
    ("workshop", "Workshop", "Peer-reviewed workshop publications", "workshop-papers"),
    ("working", "Working paper", "Working papers", "working-papers"),
]
STATUSES = [("published", "Published"), ("accepted", "Accepted"),
            ("under-review", "Under review"), ("preprint", "Preprint")]
STATUS_LABEL = dict(STATUSES)
YEARS = [("2026", "2026"), ("2025", "2025"), ("2024", "2024"), ("earlier", "Earlier")]
SOURCE_LABEL = {"acl_anthology": "ACL Anthology", "arxiv": "arXiv", "google_scholar": "Google Scholar"}

e = lambda s: html.escape(str(s), quote=True)


def scholar_url(title):
    return "https://scholar.google.com/scholar?q=" + urllib.parse.quote_plus(title)


def get_primary_publication_url(paper):
    """Return the primary URL for a paper and record which source it came from.

    Order: ACL Anthology -> arXiv -> Google Scholar search (always available)."""
    if not paper.get("google_scholar_url"):
        paper["google_scholar_url"] = scholar_url(paper["title"])
    for key, source in (("acl_anthology_url", "acl_anthology"),
                        ("arxiv_url", "arxiv"),
                        ("google_scholar_url", "google_scholar")):
        if paper.get(key):
            paper["primary_url"] = paper[key]
            paper["primary_source"] = source
            return paper[key]
    return None  # unreachable: google_scholar_url is always filled


def year_bucket(y):
    return str(y) if int(y) >= 2024 else "earlier"


def is_external(url):
    return url.startswith("http://") or url.startswith("https://")


def link(url, text, sr_suffix=""):
    """An <a> with descriptive screen-reader context and safe external handling."""
    sr = f'<span class="sr-only">{e(sr_suffix)}</span>' if sr_suffix else ""
    if is_external(url):
        return (f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{text}{sr}'
                f'<span class="sr-only"> (opens in a new tab)</span></a>')
    return f'<a href="{e(url)}">{text}{sr}</a>'


def authors_html(p):
    out = []
    for a in p["authors"]:
        if a.get("me"):
            s = f"<strong>{e(a['name'])}</strong>"
            if a.get("equal_contribution"):
                s += '<span class="eq" aria-hidden="true">*</span><span class="sr-only"> (equal contribution)</span>'
            out.append(s)
        else:
            out.append(e(a["name"]))
    return ", ".join(out)


def resources(p):
    short = p["short_title"]
    ctx = f": {short} ({p['venue_short']})" if p["venue_short"] != "under review" else f": {short}"
    items = []
    src = p["primary_source"]
    if src == "google_scholar":
        items.append(link(p["primary_url"], "Find the paper on Google Scholar", ctx))
    else:
        items.append(link(p["primary_url"], f"Read the paper ({SOURCE_LABEL[src]})", ctx))
    if src == "acl_anthology" and p.get("arxiv_url"):
        items.append(link(p["arxiv_url"], "arXiv preprint", f" of {short}"))
    doi = p.get("doi")
    others = p.get("other_links") or []
    for o in others:
        items.append(link(o["url"], e(o["label"]), f" for {short}"))
    if doi and not any(doi in o["url"] for o in others):
        items.append(link("https://doi.org/" + doi, "DOI", f" for {short}"))
    if p.get("project_url"):
        items.append(link(p["project_url"], "Explore the project", f" ({short})"))
    if p.get("code_url"):
        items.append(link(p["code_url"], "Code and models", f" for {short}"))
    if p.get("poster_url"):
        items.append(link(p["poster_url"], "View the poster", f" for {short}"))
    if p.get("slides_url"):
        label = "View the keynote slides" if "Keynote" in (p.get("slides_label") or "") else "View the slides"
        items.append(link(p["slides_url"], label, f" for {short}"))
    if p.get("writeup_url"):
        items.append(link(p["writeup_url"], "Read the research summary", f" of {short}"))
    if p.get("preview_url"):
        items.append(link(p["preview_url"], e(p.get("preview_label") or "Preview image"), f" of {short}"))
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<nav class="pub-links" aria-label="Resources for {e(short)}"><ul>{lis}</ul></nav>'


def search_text(p):
    parts = [p["title"], p["short_title"], p["venue"], p["venue_short"], str(p["year"]),
             STATUS_LABEL[p["status"]], p.get("finding") or "", p.get("takeaway") or "",
             " ".join(a["name"] for a in p["authors"]),
             " ".join(TOPIC_LABEL[t] for t in p["topics"]),
             " ".join(p.get("keywords") or [])]
    return re.sub(r"\s+", " ", " ".join(parts)).strip().lower()


def article(p, order):
    pid = p["id"]
    meta = [f'<span class="pub-venue">{e(p["venue"])}</span>'] if p["venue"].strip().lower() != STATUS_LABEL[p["status"]].lower() else []
    meta += [f'<span class="pub-status">{STATUS_LABEL[p["status"]]}</span>',
             f'<span class="pub-year">{p["year"]}</span>']
    if p["first_author"]:
        meta.append('<span class="pub-role">First author</span>')
    if p.get("award"):
        meta.append(f'<span class="pub-award">{e(p["award"])}</span>')
    finding = ""
    if p.get("finding"):
        take = f' <span class="pub-take">{e(p["takeaway"])}</span>' if p.get("takeaway") else ""
        finding = f'\n      <p class="pub-finding">{e(p["finding"])}{take}</p>'
    topics = " · ".join(e(TOPIC_LABEL[t]) for t in p["topics"])
    summary = ""
    if p.get("summary"):
        summary = (f'\n      <details class="more pub-summary"><summary>Read the five-minute summary'
                   f'<span class="sr-only"> of {e(p["short_title"])}</span></summary>'
                   f'<div class="body"><p>{e(p["summary"])}</p></div></details>')
    attrs = (f'data-topics="{" ".join(p["topics"])}" data-type="{p["type"]}" data-year="{p["year"]}" '
             f'data-year-bucket="{year_bucket(p["year"])}" '
             f'data-contribution="{"first" if p["first_author"] else "co"}" data-status="{p["status"]}" '
             f'data-order="{order}" data-title="{e(p["title"].lower())}" data-search="{e(search_text(p))}"')
    title_link = link(p["primary_url"], e(p["title"]))
    return f'''    <li>
    <article class="publication" id="{pid}" aria-labelledby="{pid}-title" {attrs}>
      <h4 class="pub-title" id="{pid}-title">{title_link}</h4>
      <p class="pub-authors"><span class="sr-only">Authors: </span>{authors_html(p)}</p>
      <p class="pub-meta">{' <span class="sep" aria-hidden="true">·</span> '.join(meta)}</p>{finding}
      <p class="pub-topics"><span class="sr-only">Topics: </span>{topics}</p>
      {resources(p)}{summary}
    </article>
    </li>'''


def toggle_group(name, legend, options):
    btns = "".join(f'<button type="button" class="pf-btn" data-facet="{name}" data-value="{v}" aria-pressed="false">{e(l)}</button>'
                   for v, l in options)
    return (f'<div class="pf-group" role="group" aria-labelledby="pf-{name}-label">'
            f'<p class="pf-label" id="pf-{name}-label">{legend}</p><div class="pf-btns">{btns}</div></div>')


def render_catalogue(pubs):
    n = len(pubs)
    controls = f'''<div class="pub-controls" id="pub-controls" hidden>
      <div class="pf-row">
        <div class="pf-search">
          <label for="pub-search">Search publications</label>
          <input type="search" id="pub-search" autocomplete="off" spellcheck="false" aria-describedby="pub-search-hint">
          <p class="pf-hint" id="pub-search-hint">Matches title, authors, venue, topics and keywords.</p>
        </div>
        <div class="pf-sort">
          <label for="pub-sort">Sort</label>
          <select id="pub-sort">
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="title">Title (A to Z)</option>
          </select>
        </div>
      </div>
      {toggle_group("topic", "Topic", TOPICS)}
      {toggle_group("type", "Type", [(k, l) for k, l, _, _ in TYPES])}
      {toggle_group("year", "Year", YEARS)}
      {toggle_group("contribution", "Contribution", [("first", "First author"), ("co", "Co-author")])}
      {toggle_group("status", "Status", STATUSES)}
      <p class="pf-actions"><button type="button" class="pf-reset" id="pub-reset">Reset filters</button></p>
    </div>
    <p class="pub-count" id="pub-count" role="status" aria-live="polite">{n} publications.</p>
    <p class="pub-empty" id="pub-empty" hidden>No publications match these filters. Try removing a filter or use Reset filters.</p>'''
    order = {p["id"]: i for i, p in enumerate(pubs)}
    groups = []
    for key, _, heading, gid in TYPES:
        items = [p for p in pubs if p["type"] == key]
        items.sort(key=lambda p: (-int(p["year"]), order[p["id"]]))
        body = "\n".join(article(p, order[p["id"]]) for p in items)
        groups.append(f'''  <section class="pub-group" data-group="{key}" aria-labelledby="{gid}">
    <h3 id="{gid}">{heading} <span class="count">({len(items)})</span></h3>
    <ol class="pub-list">
{body}
    </ol>
  </section>''')
    return "\n    " + controls + "\n" + "\n".join(groups) + "\n"


def render_start_here(pubs):
    feat = sorted([p for p in pubs if p.get("featured")], key=lambda p: p["featured"])
    lis = []
    for p in feat:
        role = " · First author" if p["first_author"] else ""
        lis.append(f'''      <li>
        <h3 class="sh-title"><a href="#{p["id"]}">{(f'<img class="beetle-wordmark" src="{e(p["wordmark"])}" alt="{e(p["short_title"])}" width="520" height="368">' if p.get("wordmark") else e(p["short_title"]))}</a></h3>
        <p class="sh-meta">{e(p["venue_short"])} · {STATUS_LABEL[p["status"]]}{role}</p>
        <p class="sh-finding">{e(p.get("featured_finding") or p.get("finding") or "")} {link(p["primary_url"], "Read the paper", f": {p['short_title']}")}</p>
      </li>''')
    return '\n    <ol class="start-list">\n' + "\n".join(lis) + "\n    </ol>\n    "


def replace_block(page, name, content):
    pat = re.compile(r"(<!-- AUTO:%s:start -->)(.*?)(<!-- AUTO:%s:end -->)" % (name, name), re.S)
    if not pat.search(page):
        if name == "start-here":
            return page  # optional block
        sys.exit(f"Marker AUTO:{name} not found in research.html")
    return pat.sub(lambda m: m.group(1) + content + m.group(3), page, count=1)


def merge_links(data, path):
    verified = json.load(open(path, encoding="utf-8"))
    by_id = {p["id"]: p for p in data["publications"]}
    unknown = [k for k in verified if k not in by_id]
    if unknown:
        print("warning: ids not in publications.json:", ", ".join(unknown), file=sys.stderr)
    for pid, fields in verified.items():
        p = by_id.get(pid)
        if not p:
            continue
        for key in ("acl_anthology_url", "arxiv_url", "google_scholar_url", "doi"):
            if fields.get(key):
                p[key] = fields[key]
        p["verified"] = True
    return sum(1 for k in verified if k in by_id)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--merge-links", metavar="PATH", help="JSON of verified links keyed by pub id")
    ap.add_argument("--check", action="store_true", help="exit 1 if research.html is stale")
    args = ap.parse_args()

    data = json.load(open(DATA, encoding="utf-8"))
    pubs = data["publications"]
    if args.merge_links:
        print(f"merged links for {merge_links(data, args.merge_links)} publications")
    ids = [p["id"] for p in pubs]
    assert len(ids) == len(set(ids)), "duplicate publication ids"
    for p in pubs:
        get_primary_publication_url(p)
        assert all(t in TOPIC_LABEL for t in p["topics"]), p["id"]
        assert p["status"] in STATUS_LABEL and p["type"] in {t[0] for t in TYPES}, p["id"]
    if not args.check:
        with open(DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    page = open(PAGE, encoding="utf-8").read()
    new = replace_block(page, "start-here", render_start_here(pubs))
    new = replace_block(new, "publications", render_catalogue(pubs))
    if args.check:
        sys.exit(0 if new == page else 1)
    if new != page:
        open(PAGE, "w", encoding="utf-8").write(new)
    print(f"rendered {len(pubs)} publications into research.html"
          + ("" if new != page else " (no changes)"))


if __name__ == "__main__":
    main()
