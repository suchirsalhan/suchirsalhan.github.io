/* Teaching page: show one personalised view at a time.
   Without JS every view stays visible. The chosen view is kept in the URL hash
   (so links, deep links and back/forward work) and in sessionStorage for the visit. */
(function () {
  var views = Array.prototype.slice.call(document.querySelectorAll('.tv .view'));
  if (!views.length) return;

  var KEY = 'teaching-view';
  var START = 'start';
  var ids = views.map(function (v) { return v.id; });
  // Older anchors on this page, kept so existing links still land somewhere sensible.
  var aliases = {
    'course-teaching': 'courses', 'portal': 'courses', 'mentorship': 'urop',
    'collaboration': 'collaborate', 'research-supervision': 'mphil-projects'
  };
  var bar = document.getElementById('tv-context');
  var now = document.getElementById('tv-now');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var current = null;

  function store(id) {
    try { if (id === START) sessionStorage.removeItem(KEY); else sessionStorage.setItem(KEY, id); } catch (e) {}
  }
  function stored() {
    try { var v = sessionStorage.getItem(KEY); return ids.indexOf(v) > -1 ? v : null; } catch (e) { return null; }
  }

  // Map a hash to { view, target } where target is an element inside the view to scroll to.
  function resolve(hash) {
    var h = (hash || '').replace(/^#/, '');
    try { h = decodeURIComponent(h); } catch (e) {}
    if (!h) return null;
    if (ids.indexOf(h) > -1) return { view: h, target: null };
    if (aliases[h]) return { view: aliases[h], target: null };
    var el = document.getElementById(h);
    if (el) {
      var v = el.closest('.view');
      if (v) return { view: v.id, target: el };
    }
    return null;
  }

  function show(id, opts) {
    opts = opts || {};
    var view = document.getElementById(id);
    if (!view) return;
    var changed = id !== current;
    views.forEach(function (v) {
      v.hidden = v.id !== id;
      v.classList.remove('is-entering');
    });
    if (changed && current !== null && !reduce) {
      void view.offsetWidth; // restart the fade
      view.classList.add('is-entering');
    }
    current = id;
    store(id);

    if (bar) {
      bar.hidden = id === START;
      if (now) now.textContent = view.getAttribute('data-label') || '';
    }
    document.title = (id === START ? '' : (view.getAttribute('data-label') + ' · ')) + 'Teaching & Supervision · Suchir Salhan';

    if (opts.target) {
      // Deep link to something inside a view: scroll to it once the view is visible.
      requestAnimationFrame(function () {
        opts.target.scrollIntoView({ block: 'start', behavior: reduce ? 'auto' : 'smooth' });
      });
    } else if (changed && !opts.initial) {
      var y = view.getBoundingClientRect().top + window.pageYOffset - 140;
      window.scrollTo(0, y < 240 ? 0 : y);
    } else if (opts.initial) {
      window.scrollTo(0, 0);
    }
    if (opts.focus) {
      var head = view.querySelector('.v-title');
      if (head) head.focus({ preventScroll: true });
    }
  }

  function go(id) {
    if (id === START) {
      if (location.hash) history.pushState(null, '', location.pathname + location.search);
      show(START, { focus: true });
    } else if (location.hash === '#' + id) {
      show(id, { focus: true });
    } else {
      history.pushState(null, '', '#' + id);
      show(id, { focus: true });
    }
  }

  function fromLocation(initial) {
    var r = resolve(location.hash);
    if (r) { show(r.view, { target: r.target, initial: initial, focus: !initial }); return; }
    if (initial) {
      var s = stored();
      if (s) { history.replaceState(null, '', '#' + s); show(s, { initial: true }); return; }
    }
    show(START, { initial: initial, focus: !initial });
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-go]');
    if (t) {
      e.preventDefault();
      go(t.getAttribute('data-go'));
      return;
    }
    // In-page links (e.g. the research themes list) that point into another view.
    var a = e.target.closest('a[href^="#"]');
    if (a && a.closest('.tv')) {
      var r = resolve(a.getAttribute('href'));
      if (r && r.view !== current) {
        e.preventDefault();
        history.pushState(null, '', a.getAttribute('href'));
        show(r.view, { target: r.target, focus: !r.target });
      }
    }
  });

  window.addEventListener('popstate', function () { fromLocation(false); });
  window.addEventListener('hashchange', function () {
    var r = resolve(location.hash);
    if (!r) { if (!location.hash) show(START, { focus: true }); return; }
    if (r.view !== current) show(r.view, { target: r.target, focus: !r.target });
  });

  fromLocation(true);
})();
