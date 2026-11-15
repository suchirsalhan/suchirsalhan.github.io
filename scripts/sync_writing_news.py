#!/usr/bin/env python3
"""Add new writing/ posts to the homepage News list.

A post is picked up when its <head> has
    <meta property="article:published_time" content="YYYY-MM-DD">
Its title comes from og:title (falling back to <title>), and its kind
(Essay, Paper write-up, ...) from the second field of the `.meta` line,
e.g. `<div class="meta"><time ...>15 November 2026</time> · Essay · ...`.

The generated items live between the AUTO:writing-news markers at the top
of `ul.news` in index.html, newest first. Hand-written news items below the
markers are left alone. Re-running is idempotent.

Usage:
    python3 scripts/sync_writing_news.py          # rewrite index.html
    python3 scripts/sync_writing_news.py --check  # exit 1 if out of date
"""
import datetime
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
START = "<!-- AUTO:writing-news -->"
END = "<!-- /AUTO:writing-news -->"
INDENT = "          "


def meta(s, prop):
    m = re.search(r'<meta\s+property="%s"\s+content="([^"]*)"' % re.escape(prop), s)
    return html.unescape(m.group(1)).strip() if m else None


def posts():
    out = []
    for path in glob.glob(os.path.join(ROOT, "writing", "*.html")):
        if os.path.basename(path) == "index.html":
            continue
        s = open(path, encoding="utf-8").read()
        date = meta(s, "article:published_time")
        if not date:
            continue
        d = datetime.date.fromisoformat(date[:10])
        title = meta(s, "og:title")
        if not title:
            t = re.search(r"<title>(.*?)</title>", s, re.S)
            title = html.unescape(t.group(1)).split(" · ")[0].strip() if t else os.path.basename(path)
        kind = "post"
        m = re.search(r'class="meta">(.*?)</div>', s, re.S)
        if m:
            parts = [re.sub(r"<[^>]+>", "", p).strip() for p in m.group(1).split("·")]
            if len(parts) > 1 and parts[1]:
                kind = parts[1].lower()
        out.append((d, kind, title, "writing/" + os.path.basename(path)))
    return sorted(out, reverse=True)


def render(items):
    lines = [INDENT + START]
    for d, kind, title, href in items:
        lines.append(
            '%s<li><span class="d">%s</span><span>New %s: <a href="%s">%s</a></span></li>'
            % (INDENT, d.strftime("%b %Y"), kind, href, html.escape(title, quote=False))
        )
    lines.append(INDENT + END)
    return "\n".join(lines)


def main():
    s = open(INDEX, encoding="utf-8").read()
    items = posts()
    block = render(items)
    if START in s:
        new = re.sub(r"[ \t]*" + re.escape(START) + r".*?" + re.escape(END), block, s, flags=re.S)
    else:
        m = re.search(r'<ul class="plain news">\n', s)
        if not m:
            sys.exit("index.html: no <ul class=\"plain news\"> found")
        # Drop hand-written items that the block now generates.
        for _, _, _, href in items:
            s = re.sub(r'[ \t]*<li><span class="d">[^<]*</span><span>New [^<]*<a href="%s">.*?</li>\n' % re.escape(href), "", s)
        m = re.search(r'<ul class="plain news">\n', s)
        new = s[: m.end()] + block + "\n" + s[m.end():]
    if "--check" in sys.argv:
        if new != s:
            sys.exit("index.html news is out of date; run scripts/sync_writing_news.py")
        print("news up to date (%d posts)" % len(items))
        return
    if new != s:
        open(INDEX, "w", encoding="utf-8").write(new)
    print("news synced: %d post(s)" % len(items))


if __name__ == "__main__":
    main()
