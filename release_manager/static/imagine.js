/* Imagine page: builds the request from the panel, shows the exact prompt for free, and only
   generates after an explicit confirm with the estimated cost. */
(function () {
    var root = document.getElementById('im');
    if (!root) return;
    var csrf = root.dataset.csrf, release = root.dataset.release;
    var kind = 'cover', preset = 'draft';
    function post(url, body) {
        return fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf}, body: JSON.stringify(body)})
            .then(function (r) { return r.json().then(function (j) { j._status = r.status; return j; }); });
    }
    function pick(groupId, attr, onPick) {
        document.querySelectorAll('#' + groupId + ' [data-' + attr + ']').forEach(function (b) {
            b.addEventListener('click', function () {
                document.querySelectorAll('#' + groupId + ' [data-' + attr + ']').forEach(function (x) { x.classList.toggle('active', x === b); });
                onPick(b.dataset[attr]);
            });
        });
    }
    pick('im-kind', 'kind', function (k) {
        kind = k;
        document.getElementById('im-light-dir').hidden = k !== 'background';
        if (k === 'texture') document.getElementById('im-title').value = 'none';
    });
    pick('im-preset', 'preset', function (p) { preset = p; });
    document.querySelectorAll('#im-motifs input, #im-brief-motifs input').forEach(function (cb) {
        cb.addEventListener('change', function () {
            var box = cb.closest('.im-checks'), on = box.querySelectorAll('input:checked');
            if (on.length > 2) cb.checked = false;                  // two motifs at most: few elements
        });
    });

    function request() {
        var choice = {};
        document.querySelectorAll('[data-opt]').forEach(function (s) { choice[s.dataset.opt] = s.value; });
        choice.motif = Array.prototype.map.call(document.querySelectorAll('#im-motifs input:checked'), function (c) { return c.value; });
        var refs = Array.prototype.map.call(document.querySelectorAll('#im-refs input:checked'), function (c) { return {scope: c.dataset.scope, file: c.dataset.file}; });
        return {release: release, kind: kind, subject: document.getElementById('im-subject').value, choice: choice,
                title_area: document.getElementById('im-title').value, light_direction: document.getElementById('im-light').value,
                refs: refs, preset: preset, size: document.getElementById('im-size').value, n: +document.getElementById('im-n').value};
    }
    var promptBox = document.getElementById('im-prompt'), note = document.getElementById('im-note');
    function showPrompt(j) {
        document.getElementById('im-prompt-text').textContent = j.prompt;
        document.getElementById('im-est').textContent = j.model + ', ' + j.quality + ', ' + j.size + ', ' + j.n + ' image(s): about $' +
            j.estimate.total.toFixed(3) + ' (' + j.estimate.basis + ')' + (j.sent_refs ? ', ' + j.sent_refs + ' reference image(s) sent' : '');
        promptBox.hidden = false;
    }
    document.getElementById('im-prompt-close').addEventListener('click', function () { promptBox.hidden = true; });
    document.getElementById('im-show').addEventListener('click', function () {
        post('/imagine/prompt', request()).then(function (j) { if (!j.ok) { note.textContent = j.error; return; } showPrompt(j); });
    });

    var gen = document.getElementById('im-generate');
    gen.addEventListener('click', function () {
        var body = request();
        post('/imagine/prompt', body).then(function (j) {
            if (!j.ok) { note.textContent = j.error; return; }
            showPrompt(j);
            if (!confirm('Generate ' + j.n + ' image(s) with ' + j.model + ' (' + j.quality + ') for about $' + j.estimate.total.toFixed(3) + '?\nThis is AI and it costs money. The prompt is shown below.')) return;
            body.confirmed = true;
            gen.disabled = true; gen.textContent = 'Generating... (up to 2 minutes)';
            post('/imagine/generate', body).then(function (r) {
                if (!r.ok) { note.textContent = r.error; return; }
                note.textContent = 'Made ' + r.images.length + '. Rate them: Keep, Reject, or Anchor.';
                var empty = document.getElementById('im-empty'); if (empty) empty.remove();
                var g = document.getElementById('im-gallery');
                r.images.forEach(function (im) { g.insertAdjacentHTML('afterbegin', card(im)); });
                wire();
                // Machine-22: drafts are reviewed by Claude right away, before any paid final
                r.images.forEach(function (im) {
                    if (im.quality !== 'low' || im.kind === 'composite') return;
                    var c = document.querySelector('.im-card[data-id="' + im.id + '"]');
                    if (c) runReview(c);
                });
                document.getElementById('im-spend').innerHTML = 'This month <strong>$' + r.spend.usd.toFixed(2) + '</strong> &middot; ' + r.spend.images + ' images';
            }).catch(function () { note.textContent = 'The request failed.'; })
              .then(function () { gen.disabled = false; gen.textContent = 'Generate'; });
        });
    });
    function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
    function card(im) {
        return '<figure class="im-card" data-id="' + im.id + '" data-decision=""><a href="' + im.url + '" target="_blank" data-lb data-lb-src="' + im.url + '" data-lb-title="' +
            esc(im.model.replace('gpt-image-', '') + ' · ' + im.quality) + '"><img src="' + im.url + '" alt=""></a>' +
            '<figcaption><span class="im-decide"><button type="button" data-d="anchor">&#9733; Anchor</button><button type="button" data-d="keep">Keep</button><button type="button" data-d="reject">Reject</button></span>' +
            '<span class="im-pill"></span><details class="im-more"><summary>details</summary>' +
            '<span class="brand-muted">' + im.model.replace('gpt-image-', '') + ' &middot; ' + im.quality + ' &middot; $' + (im.cost_usd || 0).toFixed(3) + ' &middot; now</span>' +
            (im.step > 1 ? '<span class="brand-muted im-round">step ' + im.step + ' &middot; ' + esc(CLOSE[im.closeness] || im.closeness) + ' &middot; after ' + esc(im.parent) + '</span>' : '') +
            '<span class="im-links"><a href="' + im.edit + '">Edit a copy</a> <button type="button" class="im-asref">Use as reference</button></span>' +
            (im.kind === 'background' ? COMP : '') +
            (im.kind === 'composite' ? '<span class="brand-muted">local composite of ' + esc(im.photo) + '</span>' : '') +
            (im.kind !== 'composite' ? '<div class="im-review" data-review="{}" data-review2="{}"></div>' : '') +
            '<details><summary>prompt</summary><pre>' + esc(im.prompt) + '</pre></details></details></figcaption></figure>';
    }
    var COMP = '<details class="im-comp"><summary>Put my photo on it (local, free)</summary><span class="im-comp-row">' +
        '<input type="text" placeholder="out-152" class="im-comp-photo"><select class="im-comp-pos"><option value="center">centre</option>' +
        '<option value="left">left</option><option value="right">right</option></select><select class="im-comp-scale">' +
        '<option value="0.6">small</option><option value="0.78" selected>medium</option><option value="0.95">large</option></select>' +
        '<button type="button" class="im-comp-go">Make it</button></span><span class="brand-muted">Cut out on your Mac; your photo is not sent anywhere.</span></details>';
    // ---- Machine-23: Claude sharpens the subject (suggestion only; nothing is rendered)
    var sharpBtn = document.getElementById('im-sharpen'), sharpOut = document.getElementById('im-sharp-out');
    if (sharpBtn) sharpBtn.addEventListener('click', function () {
        var subj = document.getElementById('im-subject');
        if (!subj.value.trim()) { subj.focus(); return; }
        sharpBtn.disabled = true; sharpBtn.textContent = 'Sharpening...';
        post('/imagine/sharpen', request()).then(function (j) {
            sharpOut.hidden = false;
            limitPopup(j);
            if (!j.ok) { sharpOut.innerHTML = '<span class="im-rv-err">' + esc(j.error || 'The rewrite failed.') + '</span>'; return; }
            sharpOut.innerHTML = '<div class="im-sharp-text">' + esc(j.subject) + '</div>' +
                '<span class="brand-muted">' + esc(j.why || '') + '</span>' +
                '<span class="im-sharp-acts"><button type="button" class="im-sharp-use">Use it</button> <button type="button" class="im-sharp-keep">Keep mine</button></span>';
            sharpOut.querySelector('.im-sharp-use').addEventListener('click', function () { subj.value = j.subject; sharpOut.hidden = true; });
            sharpOut.querySelector('.im-sharp-keep').addEventListener('click', function () { sharpOut.hidden = true; });
        }).catch(function () { sharpOut.hidden = false; sharpOut.innerHTML = '<span class="im-rv-err">The rewrite request failed.</span>'; })
          .then(function () { sharpBtn.disabled = false; sharpBtn.textContent = 'Sharpen with Claude'; });
    });
    // ---- Machine-22: Claude draft review (no re-render; Amir decides)
    var AREA = {'text': 'Text', 'anatomy': 'Anatomy', 'palette': 'Palette', 'never-list': 'Never list',
                'composition': 'Composition', 'brief': 'Brief', 'ai-look': 'AI look', 'technical': 'Technical'};
    // Machine-26: GPT (OpenAI) reviews the same draft next to Claude, same checklist; a marker says
    // whether they agree. Both run together; each fills its own half when it answers.
    var WHO = {claude: 'Claude', openai: 'GPT'}, KEY = {claude: 'review', openai: 'review2'};
    function storedReview(c, who) {
        var rv = {}; try { rv = JSON.parse(c.querySelector('.im-review').dataset[KEY[who || 'claude']] || '{}'); } catch (e) {}
        return rv;
    }
    function oneReview(who, rv, st) {
        if (st.busy[who]) return '<div class="im-rv-one"><span class="brand-muted">' + WHO[who] + ' is reviewing this draft...</span></div>';
        var h = '';
        if (rv && rv.verdict) {
            h = '<div class="im-rv-head"><span class="im-rv-who">' + WHO[who] + '</span> <strong class="im-rv-' + (rv.verdict === 'pass' ? 'pass' : 'fix') + '">' +
                (rv.verdict === 'pass' ? 'Ready for a final' : 'Fix before a final') + '</strong> ' + esc(rv.summary || '') + '</div>';
            if (rv.issues && rv.issues.length) h += '<ul class="im-rv-issues">' + rv.issues.map(function (i) {
                return '<li><span class="brand-muted">' + esc(AREA[i.area] || i.area) + ':</span> ' + esc(i.note) + '</li>'; }).join('') + '</ul>';
            if (rv.prompt_fix) h += '<div class="im-rv-next"><span class="brand-muted">Try next:</span> ' + esc(rv.prompt_fix) + '</div>';
        }
        if (st.err[who]) h += '<span class="im-rv-err">' + WHO[who] + ': ' + esc(st.err[who]) + '</span>';
        return h ? '<div class="im-rv-one">' + h + '</div>' : '';
    }
    function renderReview(c) {
        var box = c.querySelector('.im-review'); if (!box) return;
        var st = c._rv || (c._rv = {busy: {}, err: {}});
        var a = storedReview(c, 'claude'), b = storedReview(c, 'openai'), html = '';
        if (a.verdict && b.verdict && !st.busy.claude && !st.busy.openai) {
            var same = a.verdict === b.verdict;
            html += '<div class="im-rv-agree im-rv-' + (same ? (a.verdict === 'pass' ? 'pass' : 'fix') : 'differ') + '">' +
                (same ? (a.verdict === 'pass' ? 'Both say ready for a final' : 'Both say fix it first') :
                        'They differ: Claude says ' + (a.verdict === 'pass' ? 'ready' : 'fix') + ', GPT says ' + (b.verdict === 'pass' ? 'ready' : 'fix')) + '</div>';
        }
        html += oneReview('claude', a, st) + oneReview('openai', b, st);
        if (a.verdict || b.verdict) html += TRY;      // under every review: a fix prefilled, or your own change
        var busy = st.busy.claude || st.busy.openai;
        if (!busy) html += ' <button type="button" class="im-rv-go">' + (a.verdict || b.verdict ? 'Review again' : 'Review with Claude and GPT') + '</button>';
        box.innerHTML = html;
        var pill = c.querySelector('.im-pill'), va = a.verdict || b.verdict, vb = b.verdict || a.verdict;
        if (pill) {
            pill.className = 'im-pill' + (va ? ' im-pill-' + (va === vb ? (va === 'pass' ? 'pass' : 'fix') : 'differ') : '');
            pill.textContent = busy ? 'reviewing...' : (va ? (va === vb ? (va === 'pass' ? 'ready' : 'fix first') : 'reviews differ') : '');
        }
        var go = box.querySelector('.im-rv-go');
        if (go) go.addEventListener('click', function () { runReview(c); });
        wireTry(c);
    }
    var limitShown = false;
    function limitPopup(j) {                      // the monthly Claude API limit (claude_api.LIMIT_USD): one pop-up
        if (j && j.limit_note && !limitShown) { limitShown = true; alert(j.limit_note); }
    }
    function runReview(c) {
        var st = c._rv || (c._rv = {busy: {}, err: {}});
        ['claude', 'openai'].forEach(function (who) {
            st.busy[who] = true; st.err[who] = '';
        });
        renderReview(c);
        ['claude', 'openai'].forEach(function (who) {
            post('/imagine/review', {id: c.dataset.id, who: who}).then(function (j) {
                if (who === 'claude') limitPopup(j);
                st.busy[who] = false;
                if (j.ok) c.querySelector('.im-review').dataset[KEY[who]] = JSON.stringify(j.review);
                else st.err[who] = j.error || 'The review failed.';   // the last review stays on screen
                renderReview(c);
            }).catch(function () { st.busy[who] = false; st.err[who] = 'The review request failed.'; renderReview(c); });
        });
    }
    // ---- Machine-25: Try the fix. Three real stops, not a fake 0-100: whether the previous draft is sent
    // as the image to redraw, and how strict the wording is. Every round is one click with the cost confirmed.
    var CLOSE = {keep: 'Keep it', mostly: 'Mostly keep', free: 'Free'}, STOPS = ['free', 'mostly', 'keep'];
    var TRY = '<div class="im-try"><textarea class="im-try-fix" rows="2" placeholder="What should change in this draft?"></textarea>' +
        '<label class="im-try-slider"><span class="brand-muted">Closeness to this draft</span>' +
        '<input type="range" min="0" max="2" step="1" value="1" class="im-try-range"><strong class="im-try-stop">Mostly keep</strong></label>' +
        '<span class="brand-muted im-try-what"></span><button type="button" class="im-try-go">Try the fix</button></div>';
    var WHAT = {keep: 'This draft goes in as the image; only the fix changes.',
                mostly: 'This draft goes in as the image; subject and layout stay, light and detail may change.',
                free: 'No image sent; a new picture from the fixed prompt.'};
    function wireTry(c) {
        var box = c.querySelector('.im-try'); if (!box || box._wired) return; box._wired = true;
        var fa = storedReview(c, 'claude').prompt_fix || '', fb = storedReview(c, 'openai').prompt_fix || '';
        var fix = box.querySelector('.im-try-fix'), range = box.querySelector('.im-try-range');
        fix.value = fa || fb;
        if (fa && fb) {                                // both want a change: let him pick whose words go in
            var pick = document.createElement('span'); pick.className = 'im-try-pick';
            pick.innerHTML = '<span class="brand-muted">Use the fix from</span> <button type="button" data-f="a" class="active">Claude</button> <button type="button" data-f="b">GPT</button>';
            fix.parentNode.insertBefore(pick, fix);
            pick.querySelectorAll('button').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    fix.value = btn.dataset.f === 'a' ? fa : fb;
                    pick.querySelectorAll('button').forEach(function (x) { x.classList.toggle('active', x === btn); });
                });
            });
        }
        function stop() { return STOPS[+range.value]; }
        function show() { box.querySelector('.im-try-stop').textContent = CLOSE[stop()]; box.querySelector('.im-try-what').textContent = WHAT[stop()]; }
        range.addEventListener('input', show); show();
        var go = box.querySelector('.im-try-go');
        go.addEventListener('click', function () {
            var body = {id: c.dataset.id, fix: fix.value, closeness: stop(), preset: preset === 'final' ? 'final' : 'draft', n: 1};
            if (!body.fix.trim()) { fix.focus(); return; }
            post('/imagine/round', body).then(function (j) {
                if (!j.ok) { alert(j.error); return; }
                showPrompt(j);
                if (!confirm('Try the fix: 1 image with ' + j.model + ' (' + j.quality + ', ' + CLOSE[body.closeness] + ') for about $' + j.estimate.total.toFixed(3) + '?\nThis is AI and it costs money. The prompt is shown below.')) return;
                body.confirmed = true;
                go.disabled = true; go.textContent = 'Drawing... (up to 2 minutes)';
                post('/imagine/round', body).then(function (r) {
                    go.disabled = false; go.textContent = 'Try the fix';
                    limitPopup(r);
                    if (!r.ok) { alert(r.error); return; }
                    var g = document.getElementById('im-gallery');
                    r.images.forEach(function (im) { g.insertAdjacentHTML('afterbegin', card(im)); });
                    wire();
                    r.images.forEach(function (im) { var nc = document.querySelector('.im-card[data-id="' + im.id + '"]'); if (nc) runReview(nc); });
                    document.getElementById('im-spend').innerHTML = 'This month <strong>$' + r.spend.usd.toFixed(2) + '</strong> &middot; ' + r.spend.images + ' images';
                    window.scrollTo({top: 0, behavior: 'smooth'});
                }).catch(function () { go.disabled = false; go.textContent = 'Try the fix'; alert('The request failed.'); });
            });
        });
    }
    function wire() {
        document.querySelectorAll('.im-card').forEach(function (c) {
            if (c._wired) return; c._wired = true;
            if (c.querySelector('.im-review')) renderReview(c);
            c.querySelectorAll('[data-d]').forEach(function (b) {
                b.addEventListener('click', function () {
                    var d = c.dataset.decision === b.dataset.d ? '' : b.dataset.d;
                    post('/imagine/decision', {id: c.dataset.id, decision: d}).then(function (j) { if (j.ok) c.dataset.decision = j.decision || ''; });
                });
            });
            var go = c.querySelector('.im-comp-go');
            if (go) go.addEventListener('click', function () {
                var photo = c.querySelector('.im-comp-photo').value.trim();
                if (!photo) { c.querySelector('.im-comp-photo').focus(); return; }
                go.disabled = true; go.textContent = 'Cutting out...';
                post('/imagine/composite', {id: c.dataset.id, photo: photo, position: c.querySelector('.im-comp-pos').value,
                                            scale: c.querySelector('.im-comp-scale').value}).then(function (j) {
                    go.disabled = false; go.textContent = 'Make it';
                    if (!j.ok) { alert(j.error); return; }
                    document.getElementById('im-gallery').insertAdjacentHTML('afterbegin', card(j.image)); wire();
                });
            });
            var asref = c.querySelector('.im-asref');
            if (asref) asref.addEventListener('click', function () {
                var role = prompt('Take what from it? style, palette, light, composition, texture or mood', 'style');
                if (!role) return;
                post('/imagine/as-reference', {id: c.dataset.id, role: role.trim(), scope: release || 'brand'}).then(function (j) {
                    asref.textContent = j.ok ? 'Added as ' + j.ref.role + ' reference' : (j.error || 'Could not add');
                });
            });
        });
    }
    wire();

    var ts = document.getElementById('im-testset');
    if (ts) ts.addEventListener('click', function () {
        if (!confirm('Run the 5 test prompts at draft quality for about $' + (+ts.dataset.est).toFixed(3) + '?\nThis is AI and it costs money.')) return;
        ts.disabled = true; ts.textContent = 'Running the test set... (a few minutes)';
        post('/imagine/test-set', {confirmed: true, preset: 'draft'}).then(function (j) {
            if (!j.ok) { alert(j.error); ts.disabled = false; ts.textContent = 'Run the test set'; return; }
            location.reload();
        });
    });

    var bs = document.getElementById('im-brief-save');
    if (bs) bs.addEventListener('click', function () {
        post('/imagine/brief', {release: release, mood: document.getElementById('im-brief-mood').value,
            motifs: Array.prototype.map.call(document.querySelectorAll('#im-brief-motifs input:checked'), function (c) { return c.value; }),
            concept: document.getElementById('im-brief-concept').value, never: document.getElementById('im-brief-never').value})
            .then(function (j) { bs.textContent = j.ok ? 'Saved' : (j.error || 'Could not save'); setTimeout(function () { bs.textContent = 'Save brief'; }, 1600); });
    });

    var rf = document.getElementById('im-refform');
    if (rf) rf.addEventListener('submit', function (e) {
        e.preventDefault();
        fetch('/imagine/reference', {method: 'POST', headers: {'X-CSRFToken': csrf}, body: new FormData(rf)})
            .then(function (r) { return r.json(); }).then(function (j) { if (j.ok) location.reload(); else alert(j.error); });
    });
})();
