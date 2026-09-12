/* ============================================================
   explore.js — progressive-disclosure engine
   Powers: inline expandable concepts (.ex), depth tabs (.depth),
   sidenotes (.sn-ref), theme toggle, and the "surprise me" random link.
   Vanilla, no dependencies, event-delegated.
   ============================================================ */
(function () {
  "use strict";

  /* ---- Theme (light/dark) with persistence + no-flash ---- */
  var root = document.documentElement;
  function currentTheme() {
    return root.getAttribute("data-theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("theme", t); } catch (e) {}
  }
  window.__toggleTheme = function () {
    setTheme(currentTheme() === "dark" ? "light" : "dark");
  };

  /* ---- Inline expandable concepts ----
     Markup:
       <span class="ex" data-more="… continuation, may contain more .ex …">alignment</span>
     Click reveals the continuation inline, right after the trigger word.
     Chainable: continuations can themselves contain .ex spans. */
  function openEx(el) {
    if (el.classList.contains("is-open")) return;
    var more = el.getAttribute("data-more");
    if (more == null) return;
    var span = document.createElement("span");
    span.className = "ex-more";
    span.innerHTML = " " + more;
    el.classList.add("is-open");
    el.insertAdjacentElement("afterend", span);
    // animate in: left-to-right wipe
    requestAnimationFrame(function () { span.classList.add("ex-in"); });
  }
  function closeEx(el) {
    // remove the revealed continuation (and anything nested inside it)
    var next = el.nextElementSibling;
    if (next && next.classList.contains("ex-more")) next.remove();
    el.classList.remove("is-open");
  }
  function toggleEx(el) {
    if (el.classList.contains("is-open")) closeEx(el); else openEx(el);
  }

  document.addEventListener("click", function (e) {
    /* concept expansion (click to reveal, click again to hide) */
    var ex = e.target.closest ? e.target.closest(".ex") : null;
    if (ex) { e.preventDefault(); toggleEx(ex); return; }

    /* theme switch */
    if (e.target.closest && e.target.closest(".theme-switch")) {
      e.preventDefault(); window.__toggleTheme(); return;
    }

    /* depth tabs */
    var tab = e.target.closest ? e.target.closest(".depth-tab") : null;
    if (tab) {
      e.preventDefault();
      var wrap = tab.closest(".depth");
      var idx = Array.prototype.indexOf.call(tab.parentNode.children, tab);
      wrap.querySelectorAll(".depth-tab").forEach(function (t, i) {
        t.setAttribute("aria-selected", i === idx ? "true" : "false");
      });
      wrap.querySelectorAll(".depth-panel").forEach(function (p, i) {
        if (i === idx) { p.removeAttribute("hidden"); } else { p.setAttribute("hidden", ""); }
      });
      return;
    }

    /* sidenote toggle (mobile) */
    var sn = e.target.closest ? e.target.closest(".sn-ref") : null;
    if (sn) {
      e.preventDefault();
      var note = sn.parentNode.querySelector(".sidenote");
      if (note) note.hidden = !note.hidden;
      return;
    }

    /* surprise-me / random link */
    var rnd = e.target.closest ? e.target.closest(".random-btn") : null;
    if (rnd) {
      e.preventDefault();
      var pool = (rnd.getAttribute("data-pool") || "").split("|").filter(Boolean);
      if (pool.length) window.location.href = pool[Math.floor(Math.random() * pool.length)];
      return;
    }
  });

  /* ---- Init depth widgets (select first panel) ---- */
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".depth").forEach(function (wrap) {
      var tabs = wrap.querySelectorAll(".depth-tab");
      var panels = wrap.querySelectorAll(".depth-panel");
      if (!tabs.length) return;
      tabs.forEach(function (t, i) { t.setAttribute("aria-selected", i === 0 ? "true" : "false"); });
      panels.forEach(function (p, i) { if (i === 0) p.removeAttribute("hidden"); else p.setAttribute("hidden", ""); });
    });
    /* default-hide sidenotes on small screens */
    if (window.matchMedia("(max-width: 760px)").matches) {
      document.querySelectorAll(".sidenote").forEach(function (n) { n.hidden = true; });
    }
  });
})();
