/* The photo editor, live. The same maths as release_manager/photo_edit.py, which makes the saved
   copy from the full-size original. Geometry: quarter turns clockwise, mirror, straighten (zoomed to
   keep the frame covered), crop as fractions of that frame. Tone: exposure, warmth, shadows,
   highlights, contrast, saturation, on 0..1 values. */
(function () {
    var root = document.getElementById('ed');
    if (!root) return;
    var canvas = document.getElementById('ed-canvas'), ctx = canvas.getContext('2d', {willReadFrequently: true});
    var wrap = document.getElementById('ed-wrap'), stage = document.getElementById('ed-stage');
    var cropEl = document.getElementById('ed-crop');
    var TONE = ['exposure', 'contrast', 'shadows', 'highlights', 'saturation', 'warmth'];
    var st = fresh(), mode = 'crop', aspect = 'free', tool = 'exposure', comparing = false, tag = null;
    var img = new Image();

    function fresh() {
        var s = {rot: 0, flip: false, angle: 0, crop: {x: 0, y: 0, w: 1, h: 1}};
        TONE.forEach(function (k) { s[k] = 0; });
        return s;
    }
    function frameSize() { return st.rot % 2 ? [img.naturalHeight, img.naturalWidth] : [img.naturalWidth, img.naturalHeight]; }
    function coverScale(w, h, deg) {
        var a = Math.abs(deg) * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
        return Math.max((w * c + h * s) / w, (w * s + h * c) / h);
    }

    // ---- drawing -----------------------------------------------------------------
    var frame = document.createElement('canvas'), fctx = frame.getContext('2d');
    function drawFrame(s) {                                   // the whole frame at preview size
        var f = frameSize(), W = f[0], H = f[1];
        frame.width = W; frame.height = H;
        fctx.save();
        fctx.translate(W / 2, H / 2);
        fctx.rotate(s.angle * Math.PI / 180);
        var k = coverScale(W, H, s.angle); fctx.scale(k, k);
        if (s.flip) fctx.scale(-1, 1);
        fctx.rotate(s.rot * Math.PI / 2);
        fctx.imageSmoothingQuality = 'high';
        fctx.drawImage(img, -img.naturalWidth / 2, -img.naturalHeight / 2);
        fctx.restore();
    }
    function tone(data, s) {
        var ex = Math.pow(2, s.exposure), wr = 1 + 0.12 * s.warmth, wb = 1 - 0.12 * s.warmth;
        var sh = s.shadows * 0.9, hi = s.highlights * 0.9, ct = 1 + s.contrast, sa = 1 + s.saturation;
        if (!(s.exposure || s.warmth || s.shadows || s.highlights || s.contrast || s.saturation)) return;
        for (var i = 0; i < data.length; i += 4) {
            var r = data[i] / 255 * ex * wr, g = data[i + 1] / 255 * ex, b = data[i + 2] / 255 * ex * wb;
            r = r < 0 ? 0 : r > 1 ? 1 : r; g = g < 0 ? 0 : g > 1 ? 1 : g; b = b < 0 ? 0 : b > 1 ? 1 : b;
            if (sh) { r += sh * r * Math.pow(1 - r, 3); g += sh * g * Math.pow(1 - g, 3); b += sh * b * Math.pow(1 - b, 3); }
            if (hi) { r += hi * r * r * r * (1 - r); g += hi * g * g * g * (1 - g); b += hi * b * b * b * (1 - b); }
            if (ct !== 1) { r = (r - .5) * ct + .5; g = (g - .5) * ct + .5; b = (b - .5) * ct + .5; }
            if (sa !== 1) { var l = .2126 * r + .7152 * g + .0722 * b; r = l + (r - l) * sa; g = l + (g - l) * sa; b = l + (b - l) * sa; }
            data[i] = (r < 0 ? 0 : r > 1 ? 1 : r) * 255 + .5; data[i + 1] = (g < 0 ? 0 : g > 1 ? 1 : g) * 255 + .5; data[i + 2] = (b < 0 ? 0 : b > 1 ? 1 : b) * 255 + .5;
        }
    }
    var lastSaved = JSON.stringify(fresh()) + 'null', saveBtn = document.getElementById('ed-save');
    function syncSave() {                                     // lit when there is something new to save
        var dirty = JSON.stringify(st) + String(tag) !== lastSaved;
        saveBtn.classList.toggle('ed-save-ready', dirty && root.dataset.canSave === '1');
        if (root.dataset.canSave === '1') saveBtn.disabled = !dirty;
    }
    function render() {
        if (!img.naturalWidth) return;
        syncSave();
        var s = comparing ? fresh() : st;
        drawFrame(s);
        var W = frame.width, H = frame.height, c = mode === 'crop' || comparing ? {x: 0, y: 0, w: 1, h: 1} : st.crop;
        var sw = c.w * W, sh = c.h * H;
        var maxW = stage.clientWidth - 24, maxH = stage.clientHeight - 24, z = Math.min(maxW / sw, maxH / sh, 1.5);
        canvas.width = Math.max(1, Math.round(sw * z)); canvas.height = Math.max(1, Math.round(sh * z));
        ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(frame, c.x * W, c.y * H, sw, sh, 0, 0, canvas.width, canvas.height);
        var d = ctx.getImageData(0, 0, canvas.width, canvas.height); tone(d.data, s); ctx.putImageData(d, 0, 0);
        placeCrop();
    }

    // ---- the crop frame --------------------------------------------------------------
    function ratio() {
        var f = frameSize();
        if (aspect === 'free') return null;
        if (aspect === 'original') return f[0] / f[1];
        var p = aspect.split(':'); return +p[0] / +p[1];
    }
    function placeCrop() {
        cropEl.hidden = mode !== 'crop' || comparing;
        if (cropEl.hidden) return;
        var c = st.crop;
        cropEl.style.left = c.x * canvas.width + 'px'; cropEl.style.top = c.y * canvas.height + 'px';
        cropEl.style.width = c.w * canvas.width + 'px'; cropEl.style.height = c.h * canvas.height + 'px';
    }
    function fitAspect() {                                     // the largest crop of that shape, around the current centre
        var r = ratio(); if (!r) return;
        var f = frameSize(), W = f[0], H = f[1], c = st.crop, cx = (c.x + c.w / 2) * W, cy = (c.y + c.h / 2) * H;
        var w = W, h = w / r; if (h > H) { h = H; w = h * r; }
        var x = Math.min(Math.max(cx - w / 2, 0), W - w), y = Math.min(Math.max(cy - h / 2, 0), H - h);
        st.crop = {x: x / W, y: y / H, w: w / W, h: h / H};
    }
    var drag = null;
    cropEl.addEventListener('pointerdown', function (e) {
        e.preventDefault(); cropEl.setPointerCapture(e.pointerId);
        drag = {h: e.target.dataset.h || 'move', x: e.clientX, y: e.clientY, c: JSON.parse(JSON.stringify(st.crop))};
    });
    cropEl.addEventListener('pointermove', function (e) {
        if (!drag) return;
        var f = frameSize(), W = f[0], H = f[1], dx = (e.clientX - drag.x) / canvas.width, dy = (e.clientY - drag.y) / canvas.height;
        var o = drag.c, x0 = o.x, y0 = o.y, x1 = o.x + o.w, y1 = o.y + o.h, min = 0.05;
        if (drag.h === 'move') {
            var nx = Math.min(Math.max(o.x + dx, 0), 1 - o.w), ny = Math.min(Math.max(o.y + dy, 0), 1 - o.h);
            st.crop = {x: nx, y: ny, w: o.w, h: o.h};
        } else {
            if (drag.h.indexOf('w') >= 0) x0 = Math.min(Math.max(o.x + dx, 0), x1 - min);
            if (drag.h.indexOf('e') >= 0) x1 = Math.max(Math.min(x1 + dx, 1), x0 + min);
            if (drag.h.indexOf('n') >= 0) y0 = Math.min(Math.max(o.y + dy, 0), y1 - min);
            if (drag.h.indexOf('s') >= 0) y1 = Math.max(Math.min(y1 + dy, 1), y0 + min);
            var r = ratio();
            if (r) {                                             // keep the shape: the width leads, the height follows
                var wpx = (x1 - x0) * W, hpx = wpx / r;
                if (hpx > (drag.h.indexOf('n') >= 0 ? y1 : 1 - y0) * H) { hpx = (drag.h.indexOf('n') >= 0 ? y1 : 1 - y0) * H; wpx = hpx * r; }
                if (drag.h.indexOf('w') >= 0) x0 = x1 - wpx / W; else x1 = x0 + wpx / W;
                if (drag.h.indexOf('n') >= 0) y0 = y1 - hpx / H; else y1 = y0 + hpx / H;
            }
            st.crop = {x: x0, y: y0, w: x1 - x0, h: y1 - y0};
        }
        placeCrop();
    });
    cropEl.addEventListener('pointerup', function () { drag = null; syncSave(); });

    // ---- controls ------------------------------------------------------------------
    document.querySelectorAll('.ed-tab').forEach(function (t) {
        t.addEventListener('click', function () {
            mode = t.dataset.mode;
            document.querySelectorAll('.ed-tab').forEach(function (x) { x.classList.toggle('active', x === t); });
            document.querySelectorAll('.ed-panel').forEach(function (p) { p.hidden = p.dataset.panel !== mode; });
            render();
        });
    });
    document.querySelectorAll('.ed-chip, .ed-tag').forEach(function (b) {
        b.addEventListener('click', function () {
            aspect = b.dataset.aspect;
            tag = b.dataset.tag || null;                          // a platform tag names the saved file
            document.querySelectorAll('.ed-chip, .ed-tag').forEach(function (x) { x.classList.toggle('active', x === b); });
            if (aspect === 'free') st.crop = {x: 0, y: 0, w: 1, h: 1}; else { st.crop = {x: 0, y: 0, w: 1, h: 1}; fitAspect(); }
            render();
        });
    });
    document.getElementById('ed-rotate').addEventListener('click', function () {
        st.rot = (st.rot + 3) % 4; st.crop = {x: 0, y: 0, w: 1, h: 1}; fitAspect(); render();
    });
    document.getElementById('ed-flip').addEventListener('click', function () {
        st.flip = !st.flip; st.crop.x = 1 - st.crop.x - st.crop.w; render();
    });
    var angle = document.getElementById('ed-angle'), angleV = document.getElementById('ed-angle-v');
    angle.addEventListener('input', function () { st.angle = +angle.value; angleV.textContent = (+angle.value).toFixed(1) + '°'; render(); });
    angle.addEventListener('dblclick', function () { angle.value = 0; angle.dispatchEvent(new Event('input')); });
    var value = document.getElementById('ed-value'), valueV = document.getElementById('ed-value-v'), toolName = document.getElementById('ed-tool-name');
    document.querySelectorAll('.ed-tool').forEach(function (b) {
        b.addEventListener('click', function () {
            tool = b.dataset.tool;
            document.querySelectorAll('.ed-tool').forEach(function (x) { x.classList.toggle('active', x === b); });
            toolName.textContent = b.textContent.replace(/^-?\d+/, '').trim();
            value.value = Math.round(st[tool] * 100); valueV.textContent = value.value;
        });
    });
    value.addEventListener('input', function () {
        st[tool] = +value.value / 100; valueV.textContent = value.value;
        document.querySelector('[data-v="' + tool + '"]').textContent = value.value;
        document.querySelector('[data-tool="' + tool + '"]').classList.toggle('changed', +value.value !== 0);
        render();
    });
    value.addEventListener('dblclick', function () { value.value = 0; value.dispatchEvent(new Event('input')); });
    var compare = document.getElementById('ed-compare');
    ['pointerdown'].forEach(function (ev) { compare.addEventListener(ev, function () { comparing = true; render(); }); });
    ['pointerup', 'pointerleave'].forEach(function (ev) { compare.addEventListener(ev, function () { if (comparing) { comparing = false; render(); } }); });
    document.getElementById('ed-reset').addEventListener('click', function () {
        st = fresh(); aspect = 'free'; angle.value = 0; angleV.textContent = '0°'; value.value = 0; valueV.textContent = '0';
        tag = null;
        document.querySelectorAll('.ed-chip, .ed-tag').forEach(function (x) { x.classList.toggle('active', x.classList.contains('ed-chip') && x.dataset.aspect === 'free'); });
        document.querySelectorAll('.ed-tool-v').forEach(function (x) { x.textContent = '0'; });
        document.querySelectorAll('.ed-tool').forEach(function (x) { x.classList.remove('changed'); });
        render();
    });

    // ---- saving --------------------------------------------------------------------
    var save = document.getElementById('ed-save'), result = document.getElementById('ed-result');
    save.addEventListener('click', function () {
        var snapshot = JSON.stringify(st) + String(tag);
        save.disabled = true; save.textContent = 'Saving...';
        fetch(root.dataset.save, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': root.dataset.csrf},
                                  body: JSON.stringify({src: root.dataset.src, params: st, tag: tag})})
            .then(function (r) { return r.json(); })
            .then(function (j) {
                result.hidden = false;
                if (!j.ok) { result.textContent = j.error || 'Could not save.'; return; }
                lastSaved = snapshot;
                result.innerHTML = '<img class="ed-result-img" src="' + j.url + '" alt="">' +
                    '<span>Saved a new copy in <code>' + j.folder + '</code>:<br><a href="' + j.url + '" target="_blank">' + j.file + '</a> (' + j.size[0] + ' x ' + j.size[1] + ')</span>' +
                    '<button type="button" class="ed-btn" id="ed-finder">Show in Finder</button>' +
                    '<a class="ed-btn" href="' + j.resizer + '">Make platform sizes from it</a>' +
                    '<button type="button" class="ed-btn" id="ed-del">Delete this copy</button>' +
                    '<span class="brand-muted">Keep editing to save another version.</span>';
                document.getElementById('ed-del').addEventListener('click', function () {
                    if (!confirm('Move ' + j.file + ' to the Trash? The original photo is not touched.')) return;
                    fetch(root.dataset.delete, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': root.dataset.csrf}, body: JSON.stringify({file: j.file})})
                        .then(function (r) { return r.json(); }).then(function (d) { if (d.ok) { result.innerHTML = 'Moved to the Trash: ' + j.file; lastSaved = ''; syncSave(); } });
                });
                document.getElementById('ed-finder').addEventListener('click', function () {
                    fetch(j.reveal, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': root.dataset.csrf}, body: JSON.stringify({file: j.file})});
                });
            })
            .catch(function () { result.hidden = false; result.textContent = 'Could not save.'; })
            .then(function () { save.textContent = 'Save copy'; if (root.dataset.canSave !== '1') save.disabled = true; else syncSave(); });
    });

    root.editorState = function () { return JSON.parse(JSON.stringify(st)); };   // for checks and tests

    // ---- start ---------------------------------------------------------------------
    img.onload = function () { document.getElementById('ed-loading').hidden = true; render(); };
    img.src = root.dataset.preview;
    var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(render, 80); });
})();
