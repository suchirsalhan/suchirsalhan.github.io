#!/usr/bin/env python3
"""Render the generated parts of research.html from assets/data/publications.json.

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
    <!-- AUTO:projects:start -->     ... <!-- AUTO:projects:end -->
        The five "Selected research" tiles ("featured": 1..5 in the JSON). The
        venue line and paper links come from the JSON; the one-line question,
        project page and visual motif come from PROJECTS below.
    <!-- AUTO:publications:start --> ... <!-- AUTO:publications:end -->
        The count, type tabs, search, "More filters" (year, topic, contribution,
        status), and the full static catalogue as one list, newest first. The
        controls stay hidden until assets/js/publications.js runs.

"themes" in the JSON maps each paper to the four research questions on the page
(learn, language, representations, trust); the Topic filter uses them. The finer
"topics" tags are kept for search.

The primary paper link comes from get_primary_publication_url(): the first
non-null of acl_anthology_url -> arxiv_url -> google_scholar_url. Never invent
anthology or arXiv IDs here: add them to the JSON (or a --merge-links file) only
once they are verified.
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
# The four research questions (theme key, tag label, question, anchor on the page).
THEMES = [
    ("learn", "Learning", "How do models learn?", "q-learn"),
    ("language", "Language", "How does language shape learning?", "q-language"),
    ("representations", "Representations", "What representations emerge?", "q-representations"),
    ("trust", "Trust", "Can we trust small AI?", "q-trust"),
]
THEME_LABEL = {k: l for k, l, _, _ in THEMES}
TYPES = [
    ("conference", "Conference & journal"),
    ("workshop", "Workshop"),
    ("working", "Working papers"),
]
TYPE_LABEL = {"conference": "Conference or journal paper", "workshop": "Workshop paper", "working": "Working paper"}
STATUSES = [("published", "Published"), ("accepted", "Accepted"),
            ("under-review", "Under review"), ("preprint", "Preprint")]
STATUS_LABEL = dict(STATUSES)
YEARS = [("2026", "2026"), ("2025", "2025"), ("2024", "2024"), ("earlier", "Earlier")]
SOURCE_LABEL = {"acl_anthology": "ACL Anthology", "arxiv": "arXiv", "google_scholar": "Google Scholar"}

ARROW = '<span class="arw" aria-hidden="true">&rarr;</span>'

# Selected research tiles. Facts (venue, paper and code links) are read from the JSON.
# "links" lists (label, JSON field) pairs shown under the tile, if the field is set.
PROJECTS = {
    "pub-beetle": {
        "line": "330 open language models for studying how people learn a second language.",
        "page": "beetle.html", "cta": "Project page",
        "links": [("Paper", "primary_url"), ("Framework", "code_url")],
        "motif": "wordmark",
    },
    "pub-babybabellm": {
        "line": "Developmentally plausible language-learning data across 45 languages.",
        "page": "writing/paper-babybabellm.html", "cta": "Five-minute explanation",
        "links": [("Paper", "primary_url"), ("Project site", "project_url")],
        "motif": "languages",
    },
    "pub-bytespan": {
        "line": "Can a model discover meaningful word boundaries from raw bytes?",
        "page": "writing/paper-bytespan.html", "cta": "Five-minute explanation",
        "links": [("Paper", "primary_url")],
        "motif": "bytes",
    },
    "pub-pico": {
        "line": "An experimental framework for investigating how small language models work.",
        "page": "writing/paper-pico.html", "cta": "Five-minute explanation",
        "links": [("Paper", "primary_url"), ("PicoLM", "project_url")],
        "motif": "layers",
    },
    "pub-crosslingual-align": {
        "line": "Do independently trained language models discover shared representations?",
        "page": "writing/paper-crosslingual-alignment.html", "cta": "Five-minute explanation",
        "links": [("Paper", "primary_url")],
        "motif": "align",
        "title": "Cross-Lingual Alignment",
    },
}

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


def link(url, text, sr_suffix="", cls=""):
    """An <a> with descriptive screen-reader context and safe external handling."""
    sr = f'<span class="sr-only">{e(sr_suffix)}</span>' if sr_suffix else ""
    c = f' class="{cls}"' if cls else ""
    if is_external(url):
        return (f'<a{c} href="{e(url)}" target="_blank" rel="noopener noreferrer">{text}{sr}'
                f'<span class="sr-only"> (opens in a new tab)</span></a>')
    return f'<a{c} href="{e(url)}">{text}{sr}</a>'


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


def resource_items(p):
    """Supplementary links (everything except the title link itself)."""
    short = p["short_title"]
    items = []
    src = p["primary_source"]
    ctx = f": {short}"
    if src == "google_scholar":
        items.append(link(p["primary_url"], "Find the paper on Google Scholar", ctx))
    else:
        items.append(link(p["primary_url"], f"Paper ({SOURCE_LABEL[src]})", ctx))
    if src == "acl_anthology" and p.get("arxiv_url"):
        items.append(link(p["arxiv_url"], "arXiv preprint", f" of {short}"))
    doi = p.get("doi")
    others = p.get("other_links") or []
    for o in others:
        items.append(link(o["url"], e(o["label"]), f" for {short}"))
    if doi and not any(doi in o["url"] for o in others):
        items.append(link("https://doi.org/" + doi, "DOI", f" for {short}"))
    if p.get("project_url"):
        items.append(link(p["project_url"], "Project page", f" ({short})"))
    if p.get("code_url"):
        items.append(link(p["code_url"], "Code and models", f" for {short}"))
    if p.get("poster_url"):
        items.append(link(p["poster_url"], "Poster", f" for {short}"))
    if p.get("slides_url"):
        label = "Keynote slides" if "Keynote" in (p.get("slides_label") or "") else "Slides"
        items.append(link(p["slides_url"], label, f" for {short}"))
    if p.get("writeup_url"):
        items.append(link(p["writeup_url"], "Research summary", f" of {short}"))
    if p.get("preview_url"):
        items.append(link(p["preview_url"], e(p.get("preview_label") or "Preview image"), f" of {short}"))
    return items


def search_text(p):
    parts = [p["title"], p["short_title"], p["venue"], p["venue_short"], str(p["year"]),
             STATUS_LABEL[p["status"]], p.get("finding") or "", p.get("takeaway") or "",
             " ".join(a["name"] for a in p["authors"]),
             " ".join(TOPIC_LABEL[t] for t in p["topics"]),
             " ".join(THEME_LABEL[t] for t in p["themes"]),
             " ".join(p.get("keywords") or [])]
    return re.sub(r"\s+", " ", " ".join(parts)).strip().lower()


def article(p, order):
    pid = p["id"]
    short = p["short_title"]
    meta = []
    if p["venue_short"].strip().lower() != STATUS_LABEL[p["status"]].lower():
        meta.append(f'<span class="pub-venue">{e(p["venue_short"])}</span>')
    meta.append(f'<span class="pub-status" data-status="{p["status"]}">{STATUS_LABEL[p["status"]]}</span>')
    if str(p["year"]) not in p["venue_short"]:
        meta.append(f'<span class="pub-year">{p["year"]}</span>')
    meta_html = ' <span class="sep" aria-hidden="true">·</span> '.join(meta)
    if p["first_author"]:
        meta_html += ' <span class="pub-role">First author</span>'
    if p.get("award"):
        meta_html += f' <span class="pub-award">{e(p["award"])}</span>'
    finding = ""
    if p.get("finding"):
        take = f' <span class="pub-take">{e(p["takeaway"])}</span>' if p.get("takeaway") else ""
        finding = f'\n      <p class="pub-finding">{e(p["finding"])}{take}</p>'
    tags = "".join(f'<li>{e(THEME_LABEL[t])}</li>' for t in p["themes"])
    n = len(p["authors"])
    authors = (f'<details class="pub-d pub-authors-d"><summary>Authors <span class="pub-n">({n})</span>'
               f'<span class="sr-only"> of {e(short)}</span><span class="chev" aria-hidden="true"></span></summary>'
               f'<div class="pub-d-body"><p class="pub-authors">{authors_html(p)}</p>'
               f'<p class="pub-venue-full"><span class="sr-only">Venue: </span>{e(p["venue"])}'
               f' <span class="sep" aria-hidden="true">·</span> {TYPE_LABEL[p["type"]]}</p></div></details>')
    items = resource_items(p)
    summary = ""
    if p.get("summary"):
        summary = (f'<div class="pub-summary"><h4>Five-minute summary</h4><p>{e(p["summary"])}</p></div>')
    lis = "".join(f"<li>{i}</li>" for i in items)
    res = "" if len(items) < 2 and not summary else (f'<details class="pub-d pub-res-d"><summary>More resources<span class="sr-only"> for {e(short)}</span>'
           f'<span class="chev" aria-hidden="true"></span></summary><div class="pub-d-body">'
           f'<nav class="pub-links" aria-label="Resources for {e(short)}"><ul>{lis}</ul></nav>{summary}</div></details>')
    attrs = (f'data-topics="{" ".join(p["themes"])}" data-subtopics="{" ".join(p["topics"])}" '
             f'data-type="{p["type"]}" data-year="{p["year"]}" '
             f'data-year-bucket="{year_bucket(p["year"])}" '
             f'data-contribution="{"first" if p["first_author"] else "co"}" data-status="{p["status"]}" '
             f'data-order="{order}" data-title="{e(p["title"].lower())}" data-search="{e(search_text(p))}"')
    title_link = link(p["primary_url"], e(p["title"]))
    return f'''    <li>
    <article class="publication" id="{pid}" aria-labelledby="{pid}-title" {attrs}>
      <h3 class="pub-title" id="{pid}-title">{title_link}</h3>
      <p class="pub-meta">{meta_html}</p>{finding}
      <ul class="pub-tags" aria-label="Topics">{tags}</ul>
      <div class="pub-more">{authors}{res}</div>
    </article>
    </li>'''


def toggle_group(name, legend, options):
    btns = "".join(f'<button type="button" class="pf-btn" data-facet="{name}" data-value="{v}" aria-pressed="false">{e(l)}</button>'
                   for v, l in options)
    return (f'<div class="pf-group" role="group" aria-labelledby="pf-{name}-label">'
            f'<p class="pf-label" id="pf-{name}-label">{legend}</p><div class="pf-btns">{btns}</div></div>')


def render_catalogue(pubs):
    n = len(pubs)
    tabs = ('<button type="button" class="pf-tab" data-facet="type" data-value="" aria-pressed="true">All</button>'
            + "".join(f'<button type="button" class="pf-tab" data-facet="type" data-value="{k}" aria-pressed="false">{e(l)}</button>'
                      for k, l in TYPES))
    controls = f'''<p class="pub-total"><span id="pub-total">{n}</span> papers, newest first.</p>
    <div class="pub-controls" id="pub-controls" hidden>
      <div class="pf-tabs" role="group" aria-label="Publication type">{tabs}</div>
      <div class="pf-row">
        <div class="pf-search">
          <label for="pub-search" class="sr-only">Search publications</label>
          <svg class="pf-search-icon" viewBox="0 0 20 20" width="16" height="16" aria-hidden="true" focusable="false"><circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M13 13l4.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
          <input type="search" id="pub-search" autocomplete="off" spellcheck="false" placeholder="Search titles, authors, keywords" aria-describedby="pub-search-hint">
          <p class="sr-only" id="pub-search-hint">Results update as you type. Matches title, authors, venue, topics and keywords.</p>
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
      <details class="pf-more" id="pf-more">
        <summary>More filters <span class="pf-active" id="pf-active"></span><span class="chev" aria-hidden="true"></span></summary>
        <div class="pf-more-body">
          {toggle_group("year", "Year", YEARS)}
          {toggle_group("topic", "Topic", [(k, q) for k, _, q, _ in THEMES])}
          {toggle_group("contribution", "Contribution", [("first", "First author"), ("co", "Co-author")])}
          {toggle_group("status", "Status", STATUSES)}
        </div>
      </details>
    </div>
    <div class="pub-statusbar">
      <p class="pub-count" id="pub-count" role="status" aria-live="polite">{n} publications.</p>
      <button type="button" class="pf-reset" id="pub-reset" hidden>Reset</button>
    </div>
    <p class="pub-empty" id="pub-empty" hidden>No publications match. Try a different search or use Reset.</p>'''
    order = {p["id"]: i for i, p in enumerate(pubs)}
    items = sorted(pubs, key=lambda p: (-int(p["year"]), order[p["id"]]))
    body = "\n".join(article(p, order[p["id"]]) for p in items)
    return f"\n    {controls}\n    <ol class=\"pub-list\" id=\"pub-list\">\n{body}\n    </ol>\n"


# Small inline-SVG motifs for the project tiles. currentColor is the ink; .ac is the accent.
def motif(kind):
    svg = '<svg viewBox="0 0 200 72" width="200" height="72" aria-hidden="true" focusable="false">{}</svg>'
    if kind == "languages":
        # 45 dots: one per language in BabyBabelLM.
        dots = []
        for i in range(45):
            r, c = divmod(i, 15)
            cls = ' class="ac"' if i in (3, 17, 26, 38, 44) else ""
            dots.append(f'<circle{cls} cx="{10 + c * 12.9:.1f}" cy="{14 + r * 22}" r="3.6"/>')
        return svg.format('<g class="m-dots">' + "".join(dots) + "</g>")
    if kind == "bytes":
        # A row of bytes, grouped into spans by brackets underneath.
        spans, x, out = [3, 2, 4, 3, 2], 6, []
        for j, n in enumerate(spans):
            x0 = x
            for _ in range(n):
                out.append(f'<rect x="{x}" y="14" width="11" height="20" rx="2"/>')
                x += 13
            out.append(f'<path class="ac-stroke" d="M{x0} 44v6h{x - x0 - 2}v-6"/>')
            x += 6
        return svg.format('<g class="m-bytes">' + "".join(out) + "</g>")
    if kind == "layers":
        # A stack of layers with one swapped out: change one component, observe the effect.
        out = []
        for i in range(5):
            y = 8 + i * 12
            if i == 2:
                out.append(f'<rect class="ac" x="26" y="{y}" width="84" height="8" rx="2"/>')
                out.append(f'<rect class="ghost" x="8" y="{y}" width="84" height="8" rx="2"/>')
            else:
                out.append(f'<rect x="8" y="{y}" width="84" height="8" rx="2"/>')
        out.append('<path class="ac-stroke" d="M120 32h20m-6-5 6 5-6 5"/>')
        return svg.format('<g class="m-layers">' + "".join(out) + "</g>")
    if kind == "align":
        # Two independently trained spaces whose points correspond.
        a = [(28, 18), (52, 30), (34, 46), (60, 56), (22, 60)]
        b = [(148, 16), (172, 28), (154, 44), (180, 54), (142, 58)]
        lines = "".join(f'<path class="ac-stroke dash" d="M{x1} {y1}L{x2} {y2}"/>' for (x1, y1), (x2, y2) in zip(a, b))
        pa = "".join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x, y in a)
        pb = "".join(f'<rect x="{x - 4}" y="{y - 4}" width="8" height="8" rx="1"/>' for x, y in b)
        return svg.format(f'<g class="m-align">{lines}{pa}{pb}</g>')
    return ""


def venue_line(p):
    return p["venue"].split(" · ")[0]


def render_projects(pubs):
    feat = sorted([p for p in pubs if p.get("featured")], key=lambda p: p["featured"])
    lis = []
    for p in feat:
        cfg = PROJECTS.get(p["id"])
        if not cfg:
            continue
        name = cfg.get("title") or p["short_title"]
        if cfg["motif"] == "wordmark" and p.get("wordmark"):
            label = f'<img class="beetle-wordmark" src="{e(p["wordmark"])}" alt="{e(name)}" width="520" height="368">'
        else:
            label = e(name)
        title = (f'<h3 class="proj-title"><a class="proj-link" href="{e(cfg["page"])}">{label}'
                 f'<span class="sr-only">: {e(cfg["cta"].lower())}</span></a></h3>')
        links = []
        for lab, field in cfg["links"]:
            if p.get(field):
                links.append(f"<li>{link(p[field], e(lab), f' for {name}')}</li>")
        visual = (f'<div class="proj-visual proj-visual--wordmark">{title}</div>' if cfg["motif"] == "wordmark"
                  else f'<div class="proj-visual" aria-hidden="true">{motif(cfg["motif"])}</div>\n        {title}')
        lis.append(f'''      <li class="proj proj--{cfg["motif"]}">
        {visual}
        <p class="proj-venue">{e(venue_line(p))}</p>
        <p class="proj-line">{e(cfg["line"])}</p>
        <ul class="proj-links" aria-label="Links for {e(name)}">{"".join(links)}</ul>
        <p class="proj-cta" aria-hidden="true">{e(cfg["cta"])} {ARROW}</p>
      </li>''')
    return '\n    <ul class="proj-grid">\n' + "\n".join(lis) + "\n    </ul>\n    "


def replace_block(page, name, content, optional=False):
    pat = re.compile(r"(<!-- AUTO:%s:start -->)(.*?)(<!-- AUTO:%s:end -->)" % (name, name), re.S)
    if not pat.search(page):
        if optional:
            return page
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
        assert p.get("themes") and all(t in THEME_LABEL for t in p["themes"]), p["id"] + ": needs themes"
        assert p["status"] in STATUS_LABEL and p["type"] in TYPE_LABEL, p["id"]
    if not args.check:
        with open(DATA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    page = open(PAGE, encoding="utf-8").read()
    new = replace_block(page, "projects", render_projects(pubs), optional=True)
    new = replace_block(new, "publications", render_catalogue(pubs))
    if args.check:
        sys.exit(0 if new == page else 1)
    if new != page:
        open(PAGE, "w", encoding="utf-8").write(new)
    print(f"rendered {len(pubs)} publications into research.html"
          + ("" if new != page else " (no changes)"))


if __name__ == "__main__":
    main()
