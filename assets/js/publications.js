/* publications.js: research.html behaviour.
   1. Catalogue: type tabs, instant search, "More filters" (year, topic, contribution,
      status), sort and reset. Reads data-* attributes from the statically rendered
      <article class="publication"> elements (see scripts/build_publications.py).
      Facets: OR within a facet, AND across facets; the search must match too.
      Without JS the full list shows and the controls stay hidden.
   2. Theme links: "Explore all papers in this theme" sets the Topic filter and
      scrolls to the catalogue. ?topic=learn (or type=workshop, q=...) in the URL
      does the same on load, so a filtered view can be shared.
   3. Opening a research question when its #q-* anchor is followed, and marking the
      current section in the sticky on-page nav.
   Filtering never moves focus. No dependencies. */
(function (root) {
  "use strict";

  var FACETS = ["topic", "type", "year", "contribution", "status"];

  function emptyState() {
    var s = { query: "" };
    FACETS.forEach(function (f) { s[f] = []; });
    return s;
  }

  /* item: {topics:[], type, yearBucket, contribution, status, search} */
  function matches(item, state) {
    var q = (state.query || "").trim().toLowerCase();
    if (q) {
      var terms = q.split(/\s+/);
      for (var i = 0; i < terms.length; i++) {
        if (item.search.indexOf(terms[i]) === -1) return false;
      }
    }
    if (state.topic.length && !state.topic.some(function (t) { return item.topics.indexOf(t) !== -1; })) return false;
    if (state.type.length && state.type.indexOf(item.type) === -1) return false;
    if (state.year.length && state.year.indexOf(item.yearBucket) === -1) return false;
    if (state.contribution.length && state.contribution.indexOf(item.contribution) === -1) return false;
    if (state.status.length && state.status.indexOf(item.status) === -1) return false;
    return true;
  }

  function comparator(mode) {
    if (mode === "oldest") return function (a, b) { return (a.year - b.year) || (a.order - b.order); };
    if (mode === "title") return function (a, b) { return a.title.localeCompare(b.title) || (a.order - b.order); };
    return function (a, b) { return (b.year - a.year) || (a.order - b.order); };
  }

  function summary(shown, total) {
    if (shown === total) return "Showing all " + total + " publications.";
    return "Showing " + shown + " of " + total + " publication" + (total === 1 ? "" : "s") + ".";
  }

  var api = { matches: matches, comparator: comparator, summary: summary, emptyState: emptyState };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  root.PubFilter = api;

  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function reducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  /* ---------- catalogue ---------- */
  function initCatalogue() {
    var controls = document.getElementById("pub-controls");
    if (!controls) return null;
    var list = document.getElementById("pub-list");
    var items = $all("article.publication").map(function (a) {
      return {
        el: a, li: a.parentElement,
        topics: (a.getAttribute("data-topics") || "").split(/\s+/).filter(Boolean),
        type: a.getAttribute("data-type"),
        yearBucket: a.getAttribute("data-year-bucket"),
        year: parseInt(a.getAttribute("data-year"), 10) || 0,
        contribution: a.getAttribute("data-contribution"),
        status: a.getAttribute("data-status"),
        order: parseInt(a.getAttribute("data-order"), 10) || 0,
        title: a.getAttribute("data-title") || "",
        search: a.getAttribute("data-search") || ""
      };
    });
    var search = document.getElementById("pub-search");
    var sort = document.getElementById("pub-sort");
    var reset = document.getElementById("pub-reset");
    var count = document.getElementById("pub-count");
    var empty = document.getElementById("pub-empty");
    var more = document.getElementById("pf-more");
    var activeBadge = document.getElementById("pf-active");
    var tabs = $all(".pf-tab", controls);
    var buttons = $all(".pf-btn", controls);
    var state = emptyState();
    var announceTimer = null;

    controls.hidden = false;

    function syncButtons() {
      tabs.forEach(function (t) {
        var v = t.getAttribute("data-value");
        var on = v === "" ? state.type.length === 0 : state.type.indexOf(v) !== -1;
        t.setAttribute("aria-pressed", on ? "true" : "false");
      });
      buttons.forEach(function (b) {
        var on = state[b.getAttribute("data-facet")].indexOf(b.getAttribute("data-value")) !== -1;
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      var n = ["year", "topic", "contribution", "status"].reduce(function (s, f) { return s + state[f].length; }, 0);
      activeBadge.textContent = n ? "(" + n + " on)" : "";
      reset.hidden = !(n || state.type.length || state.query.trim() || sort.value !== "newest");
    }

    function apply(announceNow) {
      var shown = 0;
      items.forEach(function (it) {
        var ok = matches(it, state);
        it.li.hidden = !ok;
        if (ok) shown++;
      });
      empty.hidden = shown !== 0;
      syncButtons();
      var msg = shown === 0 ? "No publications match. " + summary(0, items.length) : summary(shown, items.length);
      clearTimeout(announceTimer);
      if (announceNow) count.textContent = msg;
      else announceTimer = setTimeout(function () { count.textContent = msg; }, 400);
    }

    function resort() {
      items.slice().sort(comparator(sort.value)).forEach(function (it) { list.appendChild(it.li); });
    }

    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        var v = t.getAttribute("data-value");
        state.type = v ? [v] : [];
        apply(true);
      });
    });
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        var arr = state[b.getAttribute("data-facet")], value = b.getAttribute("data-value");
        var i = arr.indexOf(value);
        if (i === -1) arr.push(value); else arr.splice(i, 1);
        apply(true);
      });
    });
    search.addEventListener("input", function () { state.query = search.value; apply(false); });
    search.addEventListener("search", function () { state.query = search.value; apply(true); });
    sort.addEventListener("change", function () { resort(); apply(true); });

    function clearAll() {
      state = emptyState();
      search.value = "";
      if (sort.value !== "newest") { sort.value = "newest"; resort(); }
    }
    reset.addEventListener("click", function () {
      clearAll();
      apply(true);
      if (history.replaceState && location.search) history.replaceState(null, "", location.pathname + location.hash);
      search.focus();
    });

    /* Set one topic (from a theme link or ?topic=) and show it. */
    function setFilters(opts) {
      clearAll();
      if (opts.topic) state.topic = [opts.topic];
      if (opts.type) state.type = [opts.type];
      if (opts.q) { state.query = opts.q; search.value = opts.q; }
      if (state.topic.length && more) more.open = true;
      apply(true);
    }

    /* Make sure a linked publication is visible before jumping to it. */
    function reveal(id) {
      var t = document.getElementById(id);
      if (t && t.classList.contains("publication") && t.parentElement.hidden) { clearAll(); apply(true); }
      return t;
    }

    syncButtons();
    count.textContent = summary(items.length, items.length);
    return { setFilters: setFilters, reveal: reveal, valid: function (facet, v) {
      return $all('[data-facet="' + facet + '"]', controls).some(function (b) { return v && b.getAttribute("data-value") === v; });
    } };
  }

  function scrollToEl(el) {
    el.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
  }

  /* ---------- page wiring ---------- */
  function init() {
    var cat = initCatalogue();

    /* Theme links: set the topic filter, then go to the catalogue. */
    $all("[data-set-topic]").forEach(function (a) {
      a.addEventListener("click", function (ev) {
        if (!cat) return;
        ev.preventDefault();
        var topic = a.getAttribute("data-set-topic");
        cat.setFilters({ topic: topic });
        if (history.replaceState) history.replaceState(null, "", "?topic=" + encodeURIComponent(topic) + "#publications");
        var target = document.getElementById("publications");
        scrollToEl(target);
        var h = document.getElementById("publications-h");
        if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
      });
    });

    /* Links to a publication reset filters that would hide it. */
    $all('a[href^="#pub-"]').forEach(function (a) {
      a.addEventListener("click", function () { if (cat) cat.reveal(a.getAttribute("href").slice(1)); });
    });

    /* Research questions: open the theme when its anchor is followed. */
    function openTheme(id) {
      var d = id && document.getElementById(id);
      if (d && d.tagName === "DETAILS" && d.classList.contains("theme")) d.open = true;
    }
    $all("[data-open-theme]").forEach(function (a) {
      a.addEventListener("click", function () { openTheme(a.getAttribute("data-open-theme")); });
    });
    function onHash() {
      var id = location.hash.slice(1);
      if (!id) return;
      openTheme(id);
      if (cat && id.indexOf("pub-") === 0) {
        var t = cat.reveal(id);
        if (t) t.scrollIntoView();
      }
    }
    window.addEventListener("hashchange", onHash);

    /* Filters from the URL (?topic=learn&type=workshop&q=bilingual). */
    if (cat && window.URLSearchParams && location.search) {
      var p = new URLSearchParams(location.search);
      var opts = {};
      if (cat.valid("topic", p.get("topic"))) opts.topic = p.get("topic");
      if (cat.valid("type", p.get("type"))) opts.type = p.get("type");
      if (p.get("q")) opts.q = p.get("q");
      if (opts.topic || opts.type || opts.q) cat.setFilters(opts);
    }
    if (location.hash) {
      onHash();
      var t = document.getElementById(location.hash.slice(1));
      if (t && t.tagName === "DETAILS") t.scrollIntoView();
    }

    /* Sticky nav: sit directly under the fixed site header, whatever its height. */
    var nav = document.getElementById("rp-nav");
    var header = document.getElementById("header");
    if (nav && header) {
      var pending = false;
      var place = function () {
        pending = false;
        var b = Math.max(0, Math.round(header.getBoundingClientRect().bottom));
        document.documentElement.style.setProperty("--rp-top", b + "px");
      };
      var queue = function () { if (!pending) { pending = true; requestAnimationFrame(place); } };
      place();
      window.addEventListener("scroll", queue, { passive: true });
      window.addEventListener("resize", queue);
      header.addEventListener("transitionend", queue);
      if ("ResizeObserver" in window) new ResizeObserver(queue).observe(header);
    }

    /* Sticky nav: mark the section in view. */
    if (nav && "IntersectionObserver" in window) {
      var links = $all("a", nav);
      var map = {};
      links.forEach(function (l) { map[l.getAttribute("href").slice(1)] = l; });
      var secs = Object.keys(map).map(function (id) { return document.getElementById(id); }).filter(Boolean);
      var visible = {};
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
        var current = null;
        secs.forEach(function (s) { if (visible[s.id] && !current) current = s.id; });
        if (!current) return;
        links.forEach(function (l) {
          if (map[current] === l) l.setAttribute("aria-current", "true");
          else l.removeAttribute("aria-current");
        });
      }, { rootMargin: "-140px 0px -55% 0px" });
      secs.forEach(function (s) { io.observe(s); });
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})(this);
