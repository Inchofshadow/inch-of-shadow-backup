/* The two resizer pages (Artwork, Video): big preview of the source, click it to set the focal
   point, hover a size to see its crop, one-click sets, a live count on the button.
   Works on top of app.js, which still owns the focal grid, group toggles, drop zone and overlay. */
(function () {
    var stage = document.getElementById('rz-stage');
    if (!stage) return;
    var kind = stage.dataset.kind;
    var frame = document.getElementById('rz-frame'), empty = document.getElementById('rz-empty');
    var media = document.getElementById('rz-media');
    var crop = document.getElementById('rz-crop'), cropLabel = document.getElementById('rz-crop-label');
    var dot = document.getElementById('rz-focal-dot');
    var select = document.querySelector('.rz-select');
    var upload = document.getElementById('upload');
    var grid = document.querySelector('.rz-focal-grid');
    var focalInput = grid ? document.getElementById(grid.id === 'focal-grid' ? 'focal-input' : 'focal-input-video') : null;
    var focalName = document.getElementById('rz-focal-name');
    var cover = document.getElementById('rz-cover');
    var boxes = Array.prototype.slice.call(document.querySelectorAll('input[name="templates"]'));
    var submit = document.querySelector('.rz-go button[type="submit"]');
    var total = document.getElementById('rz-total');
    var srcW = 0, srcH = 0;
    var frames = {}, editing = null;                               // video: a frame per shape, dragged by hand

    // ---- the preview -------------------------------------------------------------
    function show(url) {
        if (!url) { frame.hidden = true; empty.hidden = false; srcW = srcH = 0; return; }
        media.src = url; frame.hidden = false; empty.hidden = true;
    }
    function measured() {
        srcW = kind === 'image' ? media.naturalWidth : media.videoWidth;
        srcH = kind === 'image' ? media.naturalHeight : media.videoHeight;
        if (kind === 'video' && media.duration && media.currentTime === 0) media.currentTime = Math.min(1, media.duration / 2);  // a real frame, not black
        placeDot();
    }
    media.addEventListener(kind === 'image' ? 'load' : 'loadedmetadata', measured);
    if (select) select.addEventListener('change', function () {
        if (upload) upload.value = '';
        show(select.value ? select.dataset.srcBase + select.value.split('/').map(encodeURIComponent).join('/') : '');
    });
    if (upload) upload.addEventListener('change', function () {
        if (upload.files && upload.files[0]) { if (select) select.value = ''; show(URL.createObjectURL(upload.files[0])); }
    });
    var zone = document.querySelector('.rz-drop');
    if (zone) zone.addEventListener('drop', function (e) {
        var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (f) { if (select) select.value = ''; show(URL.createObjectURL(f)); }
    });
    var editLink = document.getElementById('rz-edit-link');
    function syncEdit() {
        if (!editLink || !select) return;
        var v = select.value;
        editLink.hidden = !v;
        if (v) editLink.href = editLink.dataset.base + '?src=' + encodeURIComponent(v.indexOf('edits/') === 0 ? 'edit:' + v.slice(6) : 'artwork:' + v);
    }
    if (select) select.addEventListener('change', syncEdit);
    if (select && select.value) show(select.dataset.srcBase + select.value.split('/').map(encodeURIComponent).join('/'));
    syncEdit();

    // ---- the focal point: click the picture, or the small grid ---------------------
    var NAMES = [['top-left', 'top', 'top-right'], ['left', 'center', 'right'], ['bottom-left', 'bottom', 'bottom-right']];
    function focal() { return focalInput ? focalInput.value : 'center'; }
    function setFocal(name) {
        if (!grid) return;
        var btn = grid.querySelector('[data-focal="' + name + '"]');
        if (btn) btn.click();                                    // app.js keeps the input and the active state
    }
    if (grid) grid.addEventListener('click', function () { setTimeout(function () { placeDot(); if (focalName) focalName.textContent = focal(); }, 0); });
    media.addEventListener('click', function (e) {
        if (kind === 'video' && e.offsetY > media.clientHeight - 40) return;   // leave the video controls alone
        var r = media.getBoundingClientRect();
        var col = Math.min(2, Math.floor((e.clientX - r.left) / r.width * 3));
        var row = Math.min(2, Math.floor((e.clientY - r.top) / r.height * 3));
        setFocal(NAMES[row][col]);
        e.preventDefault();
    });
    function placeDot() {
        var f = focal(), x = f.indexOf('left') >= 0 ? 1 / 6 : f.indexOf('right') >= 0 ? 5 / 6 : .5;
        var y = f.indexOf('top') >= 0 ? 1 / 6 : f.indexOf('bottom') >= 0 ? 5 / 6 : .5;
        dot.style.left = (x * 100) + '%'; dot.style.top = (y * 100) + '%';
    }

    // ---- hover a size: its crop on the picture (same maths as compute_crop_box) -------
    function cropBox(tw, th) {
        var f = focal(), tr = tw / th, sr = srcW / srcH, w, h, x = 0, y = 0;
        if (cover && cover.checked && Math.abs(srcW - srcH) <= 2 && tw !== th) return {whole: true};
        var fr = frames[shape(tw, th)];
        if (fr) {                                                    // same maths as compute_crop_box in video_resizer.py
            if (sr > tr) { h = srcH; w = srcH * tr; } else if (sr < tr) { w = srcW; h = srcW / tr; } else { w = srcW; h = srcH; }
            w *= fr.z; h *= fr.z;
            x = Math.min(Math.max(0, fr.cx * srcW - w / 2), srcW - w);
            y = Math.min(Math.max(0, fr.cy * srcH - h / 2), srcH - h);
            return {x: x / srcW, y: y / srcH, w: w / srcW, h: h / srcH};
        }
        if (sr > tr) { h = srcH; w = srcH * tr; x = f.indexOf('left') >= 0 ? 0 : f.indexOf('right') >= 0 ? srcW - w : (srcW - w) / 2; }
        else if (sr < tr) { w = srcW; h = srcW / tr; y = f.indexOf('top') >= 0 ? 0 : f.indexOf('bottom') >= 0 ? srcH - h : (srcH - h) / 2; }
        else { w = srcW; h = srcH; }
        return {x: x / srcW, y: y / srcH, w: w / srcW, h: h / srcH};
    }
    document.querySelectorAll('.export-item').forEach(function (item) {
        item.addEventListener('mouseenter', function () {
            if (!srcW) return;
            var tw = +item.dataset.w, th = +item.dataset.h, b = cropBox(tw, th);
            var label = item.querySelector('.export-label').textContent + ', ' + tw + 'x' + th;
            if (b.whole) { crop.style.cssText = 'left:0;top:0;width:100%;height:100%'; cropLabel.textContent = label + ': the whole cover, on blurred bands'; }
            else {
                crop.style.cssText = 'left:' + b.x * 100 + '%;top:' + b.y * 100 + '%;width:' + b.w * 100 + '%;height:' + b.h * 100 + '%';
                var up = Math.min(srcW * b.w / tw, srcH * b.h / th) < 1;
                cropLabel.textContent = label + (up ? ': the source is smaller, it will be upscaled' : '');
            }
            crop.hidden = false;
        });
        item.addEventListener('mouseleave', function () { if (editing) drawEdit(); else crop.hidden = true; });
    });

    // ---- video: frame by hand, one box per shape -------------------------------------
    function gcd(a, b) { return b ? gcd(b, a % b) : a; }
    function shape(w, h) { var g = gcd(w, h); return (w / g) + ':' + (h / g); }
    var framesEl = document.getElementById('rz-frames');
    var framesIn = document.getElementById('rz-frames-input'), tools = document.getElementById('rz-frame-tools');
    var zoom = document.getElementById('rz-zoom');
    function wh(sh) { var p = sh.split(':'); return [+p[0], +p[1]]; }
    function saveFrames() {
        framesIn.value = Object.keys(frames).length ? JSON.stringify(frames) : '';
        framesEl.querySelectorAll('[data-shape]').forEach(function (c) {
            c.classList.toggle('active', c.dataset.shape === editing);
            c.textContent = c.dataset.shape + (frames[c.dataset.shape] ? ' ✓' : '');
        });
    }
    function current(sh) {                                           // the frame now: by hand, or where the focal point puts it
        if (frames[sh]) return frames[sh];
        var b = cropBox(wh(sh)[0], wh(sh)[1]);
        return {cx: b.x + b.w / 2, cy: b.y + b.h / 2, z: 1};
    }
    function drawEdit() {
        if (!editing || !srcW) return;
        var b = cropBox(wh(editing)[0], wh(editing)[1]);
        crop.style.cssText = 'left:' + b.x * 100 + '%;top:' + b.y * 100 + '%;width:' + b.w * 100 + '%;height:' + b.h * 100 + '%';
        cropLabel.textContent = editing + (frames[editing] ? ', by hand: drag to move' : ', from the focal point: drag to move');
        crop.hidden = false;
    }
    function stopEditing() { editing = null; crop.classList.remove('rz-crop-edit'); crop.hidden = true; if (tools) tools.hidden = true; if (framesEl) saveFrames(); }
    if (framesEl && kind === 'video') {
        try { frames = framesIn.value ? JSON.parse(framesIn.value) : {}; } catch (e) { frames = {}; }
        framesEl.querySelectorAll('[data-shape]').forEach(function (chip) {
            chip.addEventListener('click', function () {
                if (!srcW) { alert('Pick a video first.'); return; }
                if (editing === chip.dataset.shape) { stopEditing(); return; }
                editing = chip.dataset.shape;
                zoom.value = Math.round(current(editing).z * 100);
                crop.classList.add('rz-crop-edit'); tools.hidden = false;
                saveFrames(); drawEdit();
            });
        });
        zoom.addEventListener('input', function () {
            if (!editing) return;
            var f = current(editing);
            frames[editing] = {cx: f.cx, cy: f.cy, z: zoom.value / 100};
            saveFrames(); drawEdit();
        });
        document.getElementById('rz-frame-reset').addEventListener('click', function () {
            if (!editing) return;
            delete frames[editing]; zoom.value = 100; saveFrames(); drawEdit();
        });
        document.getElementById('rz-frame-done').addEventListener('click', stopEditing);
        var drag = null;
        crop.addEventListener('pointerdown', function (e) {
            if (!editing) return;
            var f = current(editing), r = media.getBoundingClientRect();
            drag = {x: e.clientX, y: e.clientY, cx: f.cx, cy: f.cy, z: f.z, w: r.width, h: r.height};
            crop.setPointerCapture(e.pointerId); e.preventDefault();
        });
        crop.addEventListener('pointermove', function (e) {
            if (!drag) return;
            var b = cropBox(wh(editing)[0], wh(editing)[1]);
            var cx = drag.cx + (e.clientX - drag.x) / drag.w, cy = drag.cy + (e.clientY - drag.y) / drag.h;
            frames[editing] = {cx: Math.min(Math.max(cx, b.w / 2), 1 - b.w / 2), cy: Math.min(Math.max(cy, b.h / 2), 1 - b.h / 2), z: drag.z};
            drawEdit();
        });
        crop.addEventListener('pointerup', function () { if (drag) { drag = null; saveFrames(); } });
        media.addEventListener('loadedmetadata', function () { if (editing) stopEditing(); });
        saveFrames();
    }

    // ---- sets and the count ---------------------------------------------------------
    function count() {
        var n = 0;
        boxes.forEach(function (b) { if (b.checked) n += 1; });
        document.querySelectorAll('[data-count-for]').forEach(function (c) {
            var g = c.dataset.countFor, all = 0, on = 0;
            boxes.forEach(function (b) { if (b.dataset.group === g) { all += 1; if (b.checked) on += 1; } });
            c.textContent = on ? on + ' of ' + all : '';
            var t = document.querySelector('.group-toggle[data-group="' + g + '"]');
            if (t) { t.checked = on === all; t.indeterminate = on > 0 && on < all; }
        });
        if (total) total.textContent = n ? n + ' ticked' : 'none ticked: all ' + boxes.length;
        if (submit) submit.textContent = n ? 'Make ' + n + (n === 1 ? ' size' : ' sizes') : 'Make every size';
    }
    document.addEventListener('change', function (e) { if (e.target.matches('input[name="templates"], .group-toggle')) setTimeout(count, 0); });
    // size presets only: the video page's Frame-by-hand shape chips share the class (gate review 2026-11-07)
    document.querySelectorAll('.rz-chip[data-preset]').forEach(function (chip) {
        chip.addEventListener('click', function () {
            var want = chip.dataset.preset ? chip.dataset.preset.split(',') : [];
            var all = want.indexOf('*') >= 0;
            boxes.forEach(function (b) {
                b.checked = all || b.value.split(',').some(function (t) { return want.indexOf(t) >= 0; });
                if (b.checked) { var d = b.closest('details'); if (d) d.open = true; }
            });
            if (cover) cover.checked = chip.dataset.cover === '1';
            document.querySelectorAll('.rz-chip[data-preset]').forEach(function (c) { c.classList.toggle('active', c === chip && !!chip.dataset.preset); });
            count();
        });
    });
    count(); placeDot();

    // ---- video: set the trim from where the preview is ---------------------------
    var markIn = document.getElementById('rz-mark-in'), markOut = document.getElementById('rz-mark-out');
    if (markIn) markIn.addEventListener('click', function () { if (media.duration) document.getElementById('trim_start').value = media.currentTime.toFixed(1); });
    if (markOut) markOut.addEventListener('click', function () { if (media.duration) document.getElementById('trim_end').value = media.currentTime.toFixed(1); });
})();
