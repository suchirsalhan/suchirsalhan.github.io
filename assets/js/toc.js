/* toc.js — sticky, clickable table of contents for writing article pages.
   Runs only on body.writing-page pages that contain an article.tufte-article.
   Builds the nav from the article's h2/h3 headings, assigns ids where missing,
   smooth-scrolls on click, and highlights the active section on scroll. */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  function slugify(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[‘’“”]/g, '')   // curly quotes
      .replace(/&[a-z]+;/g, '')                       // stray entities
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  ready(function () {
    var body = document.body;
    if (!body || !body.classList.contains('writing-page')) return;

    var article = document.querySelector('article.tufte-article');
    if (!article) return;

    var headings = Array.prototype.slice.call(
      article.querySelectorAll('h2, h3')
    );
    if (headings.length < 2) return; // not worth a ToC

    // Assign ids + scroll offset so headings aren't hidden under the fixed header.
    var used = {};
    headings.forEach(function (h) {
      if (!h.id) {
        var base = slugify(h.textContent) || 'section';
        var id = base, i = 2;
        while (used[id] || document.getElementById(id)) { id = base + '-' + i++; }
        h.id = id;
      }
      used[h.id] = true;
      h.classList.add('toc-target');
    });

    // Build the sidebar.
    var aside = document.createElement('aside');
    aside.className = 'toc';
    aside.setAttribute('aria-label', 'Table of contents');

    var label = document.createElement('div');
    label.className = 'toc-label';
    label.textContent = 'Contents';
    aside.appendChild(label);

    var nav = document.createElement('nav');
    var ul = document.createElement('ul');
    nav.appendChild(ul);
    aside.appendChild(nav);

    var links = [];
    headings.forEach(function (h) {
      var li = document.createElement('li');
      li.className = h.tagName === 'H3' ? 'toc-sub' : 'toc-top';
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.dataset.target = h.id;
      li.appendChild(a);
      ul.appendChild(li);
      links.push(a);
    });

    // Smooth scroll (scroll-margin-top on the heading handles the header offset).
    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        var target = document.getElementById(a.dataset.target);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', '#' + a.dataset.target);
      });
    });

    // Insert the sidebar as a sibling before the article so CSS can lay them out.
    article.parentNode.insertBefore(aside, article);
    body.classList.add('has-toc');

    // Active-section highlighting.
    function setActive(id) {
      links.forEach(function (a) {
        a.classList.toggle('active', a.dataset.target === id);
      });
    }

    if ('IntersectionObserver' in window) {
      var visible = {};
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible[entry.target.id] = true;
          else delete visible[entry.target.id];
        });
        // Choose the topmost visible heading; fall back to nearest above viewport.
        var current = null;
        for (var i = 0; i < headings.length; i++) {
          if (visible[headings[i].id]) { current = headings[i].id; break; }
        }
        if (!current) {
          for (var j = headings.length - 1; j >= 0; j--) {
            if (headings[j].getBoundingClientRect().top < 140) {
              current = headings[j].id; break;
            }
          }
        }
        if (current) setActive(current);
      }, { rootMargin: '-120px 0px -70% 0px', threshold: 0 });

      headings.forEach(function (h) { observer.observe(h); });
    }
  });
})();
