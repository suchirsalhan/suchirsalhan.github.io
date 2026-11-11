/* publications.js: search, filter and sort for the catalogue on research.html.
   Reads data-* attributes from the statically rendered <article class="publication">
   elements (see scripts/build_publications.py). No dependencies. Without JS the full
   list shows and the controls stay hidden. Filtering never moves focus.
   Facets: OR within a facet, AND across facets; the search must match too. */
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

  /* ---------- DOM wiring ---------- */
  function init() {
    var controls = document.getElementById("pub-controls");
    if (!controls) return;
    var articles = Array.prototype.slice.call(document.querySelectorAll("article.publication"));
    var items = articles.map(function (a) {
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
    var groups = Array.prototype.slice.call(document.querySelectorAll(".pub-group"));
    var search = document.getElementById("pub-search");
    var sort = document.getElementById("pub-sort");
    var reset = document.getElementById("pub-reset");
    var count = document.getElementById("pub-count");
    var empty = document.getElementById("pub-empty");
    var buttons = Array.prototype.slice.call(controls.querySelectorAll(".pf-btn"));
    var state = emptyState();
    var announceTimer = null;

    controls.hidden = false;

    function apply(announceNow) {
      var shown = 0;
      items.forEach(function (it) {
        var ok = matches(it, state);
        it.li.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) {
        g.hidden = !g.querySelector(".pub-list > li:not([hidden])");
      });
      empty.hidden = shown !== 0;
      var msg = shown === 0 ? "No publications match. " + summary(0, items.length) : summary(shown, items.length);
      clearTimeout(announceTimer);
      if (announceNow) count.textContent = msg;
      else announceTimer = setTimeout(function () { count.textContent = msg; }, 400);
    }

    function resort() {
      var cmp = comparator(sort.value);
      groups.forEach(function (g) {
        var list = g.querySelector(".pub-list");
        items.filter(function (it) { return it.li.parentElement === list; })
          .sort(cmp)
          .forEach(function (it) { list.appendChild(it.li); });
      });
    }

    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        var facet = b.getAttribute("data-facet"), value = b.getAttribute("data-value");
        var on = b.getAttribute("aria-pressed") !== "true";
        b.setAttribute("aria-pressed", on ? "true" : "false");
        var arr = state[facet], i = arr.indexOf(value);
        if (on && i === -1) arr.push(value);
        if (!on && i !== -1) arr.splice(i, 1);
        apply(true);
      });
    });
    search.addEventListener("input", function () { state.query = search.value; apply(false); });
    search.addEventListener("search", function () { state.query = search.value; apply(true); });
    sort.addEventListener("change", function () { resort(); count.textContent = "Sorted: " + sort.options[sort.selectedIndex].text + ". " + count.textContent.replace(/^Sorted: [^.]*\. /, ""); });
    reset.addEventListener("click", function () {
      state = emptyState();
      search.value = "";
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
      if (sort.value !== "newest") { sort.value = "newest"; resort(); }
      apply(true);
    });

    count.textContent = summary(items.length, items.length);

    /* If the URL targets a publication, make sure it is visible. */
    window.addEventListener("hashchange", function () {
      var t = location.hash && document.getElementById(location.hash.slice(1));
      if (t && t.classList.contains("publication") && t.parentElement.hidden) { reset.click(); t.scrollIntoView(); }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})(this);
