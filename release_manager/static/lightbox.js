/* Quick picture viewer (gallery mode). Any link with data-lb opens its picture big on a dark
   overlay; arrows or swipe step through the pictures of the same [data-lb-group] (or the page);
   "Open page" goes to the full page. Cmd/Ctrl-click still opens the link normally. */
(function () {
    var box, img, title, text, open, count, list = [], at = 0;
    function build() {
        box = document.createElement('div');
        box.className = 'lb';
        box.innerHTML = '<button class="lb-close" aria-label="Close">×</button>' +
            '<button class="lb-prev" aria-label="Previous">‹</button><button class="lb-next" aria-label="Next">›</button>' +
            '<figure class="lb-fig"><img class="lb-img" alt=""><figcaption class="lb-cap">' +
            '<div class="lb-title"></div><div class="lb-text"></div>' +
            '<div class="lb-foot"><span class="lb-count"></span><a class="lb-open btn btn-secondary btn-sm">Open page →</a></div>' +
            '</figcaption></figure>';
        document.body.appendChild(box);
        img = box.querySelector('.lb-img'); title = box.querySelector('.lb-title'); text = box.querySelector('.lb-text');
        open = box.querySelector('.lb-open'); count = box.querySelector('.lb-count');
        box.querySelector('.lb-close').onclick = close;
        box.querySelector('.lb-prev').onclick = function (e) { e.stopPropagation(); step(-1); };
        box.querySelector('.lb-next').onclick = function (e) { e.stopPropagation(); step(1); };
        box.addEventListener('click', function (e) { if (e.target === box) close(); });
        var x0 = null;
        box.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, {passive: true});
        box.addEventListener('touchend', function (e) {
            if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
            if (Math.abs(dx) > 40) step(dx < 0 ? 1 : -1);
        });
    }
    function show() {
        var a = list[at], d = a.dataset;
        img.src = d.lbSrc; img.alt = d.lbTitle || '';
        title.textContent = d.lbTitle || ''; text.textContent = d.lbText || '';
        title.style.display = d.lbTitle ? '' : 'none'; text.style.display = d.lbText ? '' : 'none';
        if (d.lbHref) { open.href = d.lbHref; open.style.display = ''; } else { open.style.display = 'none'; }
        count.textContent = list.length > 1 ? (at + 1) + ' / ' + list.length : '';
        var n = list[(at + 1) % list.length]; if (n) { var pre = new Image(); pre.src = n.dataset.lbSrc; }
    }
    function step(d) { if (list.length) { at = (at + d + list.length) % list.length; show(); } }
    function close() { box.classList.remove('lb-on'); document.body.classList.remove('lb-lock'); img.src = ''; }
    document.addEventListener('click', function (e) {
        var a = e.target.closest('[data-lb]');
        if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
        e.preventDefault();
        if (!box) build();
        var scope = a.closest('[data-lb-group]') || document;
        list = Array.prototype.filter.call(scope.querySelectorAll('[data-lb]'), function (x) { return x.offsetParent !== null; });
        at = Math.max(0, list.indexOf(a));
        show(); box.classList.add('lb-on'); document.body.classList.add('lb-lock');
    });
    document.addEventListener('keydown', function (e) {
        if (!box || !box.classList.contains('lb-on')) return;
        if (e.key === 'Escape') close();
        else if (e.key === 'ArrowRight') step(1);
        else if (e.key === 'ArrowLeft') step(-1);
        else if (e.key === 'Enter' && open.style.display !== 'none') location.href = open.href;
    });
})();
