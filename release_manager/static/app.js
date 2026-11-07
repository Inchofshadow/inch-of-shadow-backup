/* ============================================================
   Release Manager — Client-side interactions
   ============================================================ */

// ---- CSRF auto-injection for fetch (runs before DOMContentLoaded) ----
(function () {
    var tokenMeta = document.querySelector('meta[name="csrf-token"]');
    var csrfToken = tokenMeta ? tokenMeta.getAttribute('content') : '';
    if (!csrfToken) return;
    var origFetch = window.fetch;
    window.fetch = function (input, init) {
        init = init || {};
        var method = (init.method || 'GET').toUpperCase();
        if (['POST', 'PUT', 'DELETE', 'PATCH'].indexOf(method) === -1) {
            return origFetch.call(this, input, init);
        }
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        if (/^https?:\/\//i.test(url)) {
            try {
                var u = new URL(url, window.location.href);
                if (u.origin !== window.location.origin) {
                    return origFetch.call(this, input, init);
                }
            } catch (e) { /* fall through */ }
        }
        var headers = new Headers(init.headers || {});
        if (!headers.has('X-CSRFToken') && !headers.has('X-CSRF-Token')) {
            headers.set('X-CSRFToken', csrfToken);
        }
        init.headers = headers;
        return origFetch.call(this, input, init);
    };
})();

document.addEventListener('DOMContentLoaded', function () {

    // ---- Mobile nav toggle ----
    var navToggle = document.getElementById('nav-toggle');
    var navLinks = document.getElementById('nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            var expanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !expanded);
            navLinks.classList.toggle('open');
        });
    }

    // ---- Scroll-based section reveal ----
    if ('IntersectionObserver' in window) {
        var revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.section').forEach(function (section) {
            // Only apply scroll-reveal to sections below the fold
            var rect = section.getBoundingClientRect();
            if (rect.top > window.innerHeight) {
                section.classList.add('reveal-on-scroll');
                revealObserver.observe(section);
            }
        });
    }

    // ---- Toast notification system ----
    function showToast(message, type) {
        type = type || 'info';
        var container = document.getElementById('toast-container');
        if (!container) return;
        var toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.textContent = message;
        toast.addEventListener('click', function () { dismissToast(toast); });
        container.appendChild(toast);
        setTimeout(function () { dismissToast(toast); }, 4000);
    }
    function dismissToast(el) {
        if (el.classList.contains('toast-out')) return;
        el.classList.add('toast-out');
        setTimeout(function () { el.remove(); }, 300);
    }

    // Convert flash messages to toasts
    document.querySelectorAll('.flash').forEach(function (f) {
        var type = 'info';
        if (f.classList.contains('flash-success')) type = 'success';
        else if (f.classList.contains('flash-error')) type = 'error';
        showToast(f.textContent.trim(), type);
    });


    // ---- Checklist AJAX toggle ----
    document.querySelectorAll('.checklist-item input[type="checkbox"]').forEach(function (cb) {
        cb.addEventListener('change', function () {
            var slug = this.dataset.slug;
            var taskId = this.dataset.taskId;
            var action = this.checked ? 'check' : 'uncheck';
            var url = '/api/release/' + slug + '/' + action + '/' + taskId;
            var checkbox = this;
            var item = this.closest('.checklist-item');

            fetch(url, { method: 'POST' })
                .then(function (res) {
                    if (!res.ok) throw new Error('failed');
                    return res.json();
                })
                .then(function (data) {
                    // Update progress display
                    var prog = document.querySelector('.checklist-progress');
                    if (prog && data.total) {
                        var pct = Math.round(data.done * 100 / data.total);
                        prog.textContent = data.done + '/' + data.total + ' tasks (' + pct + '%)';

                        // Update progress bar
                        var fill = document.querySelector('.detail-progress .progress-fill');
                        if (fill) {
                            fill.style.width = pct + '%';
                            if (pct === 100) {
                                fill.classList.add('complete');
                            } else {
                                fill.classList.remove('complete');
                            }
                        }
                    }

                    // Toggle visual state
                    if (checkbox.checked) {
                        item.classList.add('done');
                        item.classList.remove('overdue');
                    } else {
                        item.classList.remove('done');
                    }
                })
                .catch(function () {
                    checkbox.checked = !checkbox.checked;
                    showToast('Failed to update checklist. Try again.', 'error');
                });
        });
    });


    // ---- Validate button ----
    var validateBtn = document.querySelector('.btn-validate');
    if (validateBtn) {
        validateBtn.addEventListener('click', function () {
            var slug = this.dataset.slug;
            var panel = document.getElementById('validate-panel');

            fetch('/api/release/' + slug + '/validate')
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (data.warnings.length === 0) {
                        panel.innerHTML = '<p class="validate-ok">All metadata complete. Ready for submission.</p>';
                    } else {
                        var p = document.createElement('p');
                        var strong = document.createElement('strong');
                        strong.textContent = data.warnings.length + ' issue' +
                            (data.warnings.length > 1 ? 's' : '') + ' found:';
                        p.appendChild(strong);
                        var ul = document.createElement('ul');
                        data.warnings.forEach(function (w) {
                            var li = document.createElement('li');
                            li.textContent = w;
                            ul.appendChild(li);
                        });
                        panel.innerHTML = '';
                        panel.appendChild(p);
                        panel.appendChild(ul);
                    }
                    panel.classList.add('visible');
                });
        });
    }


    // ---- Delete confirmation ----
    document.querySelectorAll('.btn-delete').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            if (!confirm('Delete this track? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });


    // ---- Toggle links form ----
    var toggleLinksBtn = document.getElementById('toggle-links-form');
    var linksForm = document.getElementById('links-form');
    var cancelLinksBtn = document.getElementById('cancel-links');

    if (toggleLinksBtn && linksForm) {
        toggleLinksBtn.addEventListener('click', function () {
            linksForm.classList.toggle('visible');
        });
    }
    if (cancelLinksBtn && linksForm) {
        cancelLinksBtn.addEventListener('click', function () {
            linksForm.classList.remove('visible');
        });
    }



    // ---- Platform SVG icons ----
    var platformIcons = {
        spotify: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>',
        'apple music': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.994 6.124a9.23 9.23 0 0 0-.24-2.19c-.317-1.31-1.062-2.31-2.18-3.043A5.022 5.022 0 0 0 19.7.24 10.6 10.6 0 0 0 17.48.024L16.394 0h-8.79l-1.08.024A10.6 10.6 0 0 0 4.3.24a5.024 5.024 0 0 0-1.87.65C1.312 1.562.567 2.562.25 3.872a9.23 9.23 0 0 0-.24 2.19L0 7.205v9.586l.01 1.088a9.23 9.23 0 0 0 .24 2.19c.317 1.31 1.062 2.31 2.18 3.043a5.024 5.024 0 0 0 1.87.65 10.6 10.6 0 0 0 2.224.216L7.604 24h8.79l1.08-.024a10.6 10.6 0 0 0 2.224-.216 5.024 5.024 0 0 0 1.87-.65c1.118-.733 1.863-1.733 2.18-3.043a9.23 9.23 0 0 0 .24-2.19l.01-1.088V7.205l-.004-1.081zM17.995 12.07v5.555c0 .54-.12.99-.367 1.38a2.298 2.298 0 0 1-1.012.89 3.653 3.653 0 0 1-1.122.34 6.3 6.3 0 0 1-.862.074c-.26 0-.52-.024-.77-.074a2.395 2.395 0 0 1-.712-.27 1.678 1.678 0 0 1-.53-.48 1.2 1.2 0 0 1-.21-.706c0-.34.095-.634.29-.88.193-.24.447-.43.76-.56.318-.14.668-.236 1.05-.29.387-.06.772-.11 1.163-.16.273-.04.468-.12.59-.23.12-.115.18-.3.18-.56V9.594l-5.994 1.87v6.736c0 .54-.12.99-.366 1.38a2.298 2.298 0 0 1-1.012.89 3.653 3.653 0 0 1-1.123.34 6.3 6.3 0 0 1-.862.074c-.26 0-.517-.024-.77-.074a2.395 2.395 0 0 1-.71-.27 1.678 1.678 0 0 1-.53-.48 1.2 1.2 0 0 1-.21-.706c0-.34.093-.634.29-.88.192-.24.446-.43.76-.56.317-.14.666-.236 1.048-.29.388-.06.773-.11 1.163-.16.273-.04.47-.12.59-.23.12-.115.18-.3.18-.56V8.4c0-.305.067-.558.2-.76.134-.2.335-.35.605-.44l6.69-2.13c.15-.04.3-.07.44-.07.195 0 .355.06.483.18.13.12.193.3.193.55v6.34z"/></svg>',
        beatport: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.429 13.259c-.587-1.104-1.534-1.92-2.769-2.386l-.003-.001c.462-.693.718-1.523.718-2.372a4.5 4.5 0 0 0-4.5-4.5c-.849 0-1.679.256-2.372.718l-.001-.003c-.466-1.234-1.282-2.182-2.386-2.769C8.791 1.283 7.2 1.25 5.743 2.145L4.5 2.875v6.75l1.243.73c.29.163.6.287.92.374A4.47 4.47 0 0 0 6.125 12c0 1.127.418 2.158 1.106 2.948a4.47 4.47 0 0 0-.374-.92l-.73-1.243h-6.75l-.73 1.243c-.895 1.457-.862 3.048-.2 4.373.587 1.104 1.534 1.92 2.769 2.386l.003.001A4.451 4.451 0 0 0 1.5 23a4.5 4.5 0 0 0 4.5 4.5c.849 0 1.679-.256 2.372-.718l.001.003c.466 1.234 1.282 2.182 2.386 2.769 1.324.662 2.916.695 4.373-.2L16.375 28.625V21.875z" transform="scale(0.8) translate(2.5,0)"/><circle cx="12" cy="12" r="3"/></svg>',
        soundcloud: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1.175 12.225c-.051 0-.094.046-.101.1l-.233 2.154.233 2.105c.007.058.05.098.101.098.05 0 .09-.04.099-.098l.255-2.105-.27-2.154c-.009-.06-.05-.1-.1-.1m-.899.828c-.06 0-.091.037-.104.094L0 14.479l.172 1.308c.013.06.045.094.104.094.053 0 .09-.04.104-.094l.195-1.308-.195-1.332c-.014-.053-.05-.094-.104-.094m1.8-.78c-.065 0-.105.042-.112.105L1.74 14.48l.224 2.005c.007.065.047.105.112.105.065 0 .105-.04.112-.105l.247-2.005-.247-2.1c-.007-.065-.047-.105-.112-.105m.899-.238c-.073 0-.12.047-.127.117l-.207 2.32.207 2.175c.007.073.054.117.127.117.073 0 .12-.044.127-.117l.228-2.175-.228-2.32c-.007-.07-.054-.117-.127-.117m.9-.032c-.08 0-.127.053-.135.128l-.186 2.352.186 2.198c.008.08.055.128.135.128s.127-.048.135-.128l.207-2.198-.207-2.352c-.008-.08-.055-.128-.135-.128m.902.008c-.088 0-.135.058-.143.14l-.163 2.344.163 2.22c.008.088.055.14.143.14.088 0 .135-.052.143-.14l.183-2.22-.183-2.344c-.008-.082-.055-.14-.143-.14m.9-.07c-.094 0-.143.063-.15.15l-.142 2.414.142 2.227c.007.094.056.15.15.15.094 0 .143-.056.15-.15l.158-2.227-.158-2.414c-.007-.087-.056-.15-.15-.15m.903-.072c-.1 0-.15.068-.158.16l-.12 2.486.12 2.236c.008.1.058.16.158.16.1 0 .15-.06.158-.16l.135-2.236-.135-2.486c-.008-.092-.058-.16-.158-.16m.9.053c-.108 0-.157.073-.165.17l-.098 2.433.098 2.242c.008.1.057.17.165.17s.157-.07.165-.17l.107-2.242-.107-2.433c-.008-.097-.057-.17-.165-.17m.902-.092c-.113 0-.165.08-.173.18l-.075 2.525.075 2.248c.008.108.06.18.173.18.113 0 .165-.072.173-.18l.083-2.248-.083-2.525c-.008-.1-.06-.18-.173-.18m1.804-.17c-.12 0-.18.087-.188.193l-.053 2.695.053 2.252c.008.113.068.193.188.193.12 0 .18-.08.188-.193l.06-2.252-.06-2.695c-.008-.106-.068-.193-.188-.193m.9 0c-.127 0-.188.093-.195.2l-.03 2.695.03 2.258c.007.12.068.2.195.2.127 0 .188-.08.195-.2l.033-2.258-.033-2.695c-.007-.107-.068-.2-.195-.2m3.155-1.3c-.455 0-.886.1-1.275.28A5.248 5.248 0 0 0 12.7 7.605c-.225-.075-.45.12-.45.355v8.475c0 .24.18.42.42.435h5.82a3.15 3.15 0 0 0 3.15-3.15 3.15 3.15 0 0 0-3.15-3.15z"/></svg>',
        bandcamp: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M0 18.75l7.437-13.5H24l-7.438 13.5H0z"/></svg>',
        youtube: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>',
        instagram: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>'
    };

    // Inject platform icons
    document.querySelectorAll('.social-icon[data-platform]').forEach(function (el) {
        var platform = el.getAttribute('data-platform');
        if (platformIcons[platform]) {
            el.innerHTML = platformIcons[platform];
        }
    });

    // ---- Release card 3-dot menu ----
    document.querySelectorAll('.card-menu-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var wrap = this.closest('.release-card-wrap');
            var dropdown = wrap.querySelector('.card-menu-dropdown');
            // Close all other open menus
            document.querySelectorAll('.card-menu-dropdown.open').forEach(function (d) {
                if (d !== dropdown) d.classList.remove('open');
            });
            dropdown.classList.toggle('open');
        });
    });

    // Close menu on click outside
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.card-menu-btn') && !e.target.closest('.card-menu-dropdown')) {
            document.querySelectorAll('.card-menu-dropdown.open').forEach(function (d) {
                d.classList.remove('open');
            });
        }
    });

    // Delete release
    document.querySelectorAll('.card-menu-delete').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            var slug = this.getAttribute('data-slug');
            var title = this.getAttribute('data-title');
            if (!confirm('Permanently delete "' + title + '"? This cannot be undone.')) return;
            var wrap = this.closest('.release-card-wrap');
            fetch('/api/release/' + encodeURIComponent(slug) + '/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.ok) {
                    wrap.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    wrap.style.opacity = '0';
                    wrap.style.transform = 'scale(0.95)';
                    setTimeout(function () { wrap.remove(); }, 300);
                    showToast('"' + title + '" deleted');
                } else {
                    showToast(data.error || 'Error deleting release', true);
                }
            })
            .catch(function () { showToast('Network error', true); });
        });
    });

    // ---- Social links — individual copy ----
    document.querySelectorAll('.social-copy').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var row = this.closest('.social-row');
            var url = row.dataset.url;
            var copyBtn = this;
            navigator.clipboard.writeText(url).then(function () {
                copyBtn.classList.add('copied');
                copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
                showToast(row.dataset.platform.charAt(0).toUpperCase() + row.dataset.platform.slice(1) + ' link copied', 'success');
                setTimeout(function () {
                    copyBtn.classList.remove('copied');
                    copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
                }, 1500);
            });
        });
    });

    // ---- Social links — copy all modal ----
    var copyAllBtn = document.getElementById('copy-all-links');
    var copyModal = document.getElementById('copy-modal');

    if (copyAllBtn && copyModal) {
        var modalClose = copyModal.querySelector('.modal-close');
        var modalCancel = copyModal.querySelector('.modal-cancel');
        var modalCopyBtn = document.getElementById('modal-copy-btn');
        var selectAllCb = document.getElementById('select-all-platforms');
        var platformCbs = copyModal.querySelectorAll('.modal-platform-cb');

        function openModal() {
            copyModal.classList.add('visible');
            // Reset all checkboxes to checked
            selectAllCb.checked = true;
            platformCbs.forEach(function (cb) { cb.checked = true; });
        }
        function closeModal() {
            copyModal.classList.remove('visible');
        }

        copyAllBtn.addEventListener('click', openModal);
        modalClose.addEventListener('click', closeModal);
        modalCancel.addEventListener('click', closeModal);
        copyModal.addEventListener('click', function (e) {
            if (e.target === copyModal) closeModal();
        });

        // Select all toggle
        selectAllCb.addEventListener('change', function () {
            var checked = this.checked;
            platformCbs.forEach(function (cb) { cb.checked = checked; });
        });
        // Update select-all when individual changes
        platformCbs.forEach(function (cb) {
            cb.addEventListener('change', function () {
                var allChecked = true;
                platformCbs.forEach(function (c) { if (!c.checked) allChecked = false; });
                selectAllCb.checked = allChecked;
            });
        });

        // Copy selected
        modalCopyBtn.addEventListener('click', function () {
            var lines = [];
            platformCbs.forEach(function (cb) {
                if (cb.checked) {
                    lines.push(cb.dataset.platform + ': ' + cb.dataset.url);
                }
            });
            if (lines.length === 0) {
                showToast('No platforms selected', 'error');
                return;
            }
            var text = lines.join('\n');
            navigator.clipboard.writeText(text).then(function () {
                showToast(lines.length + ' link' + (lines.length > 1 ? 's' : '') + ' copied to clipboard', 'success');
                closeModal();
            });
        });

        // Escape closes modal
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && copyModal.classList.contains('visible')) {
                closeModal();
                e.stopImmediatePropagation();
            }
        });
    }


    // ---- Focal point grid (artwork resizer + video resizer) ----
    [
        { grid: 'focal-grid', input: 'focal-input' },
        { grid: 'focal-grid-video', input: 'focal-input-video' },
    ].forEach(function (cfg) {
        var grid = document.getElementById(cfg.grid);
        var input = document.getElementById(cfg.input);
        if (grid && input) {
            grid.querySelectorAll('.focal-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    grid.querySelectorAll('.focal-btn').forEach(function (b) {
                        b.classList.remove('active');
                    });
                    this.classList.add('active');
                    input.value = this.dataset.focal;
                });
            });
        }
    });


    // ---- Video resizer: group toggle ----
    document.querySelectorAll('.group-toggle').forEach(function (toggle) {
        toggle.addEventListener('change', function () {
            var group = this.dataset.group;
            var checked = this.checked;
            document.querySelectorAll('input[data-group="' + group + '"]').forEach(function (cb) {
                if (cb !== toggle) cb.checked = checked;
            });
        });
    });

    // Update group header when individual items change
    document.querySelectorAll('.platform-group-items input[type="checkbox"]').forEach(function (cb) {
        cb.addEventListener('change', function () {
            var group = this.dataset.group;
            var items = document.querySelectorAll('.platform-group-items input[data-group="' + group + '"]');
            var toggle = document.querySelector('.group-toggle[data-group="' + group + '"]');
            if (!toggle) return;
            var allChecked = true;
            items.forEach(function (item) { if (!item.checked) allChecked = false; });
            toggle.checked = allChecked;
        });
    });


    // ---- Resizer submit feedback (video + artwork) ----
    document.querySelectorAll('#video-form, form.section').forEach(function (form) {
        var overlay = form.querySelector('.processing-overlay');
        var submitBtn = form.querySelector('button[type="submit"]');
        if (!overlay || !submitBtn) return;

        form.addEventListener('submit', function () {
            submitBtn.disabled = true;
            submitBtn.style.display = 'none';
            overlay.style.display = 'block';
        });
    });


    // ---- Drop zone (drag & drop file upload) ----
    // Prevent browser from opening dropped files outside drop zones
    document.addEventListener('dragover', function (e) { e.preventDefault(); });
    document.addEventListener('drop', function (e) { e.preventDefault(); });

    document.querySelectorAll('.drop-zone').forEach(function (zone) {
        var input = zone.querySelector('.drop-zone-input');
        var filename = zone.querySelector('.drop-zone-filename');
        var clearBtn = zone.querySelector('.drop-zone-clear');
        var form = zone.closest('form');

        // Store dropped file separately (DataTransfer→input.files can be unreliable)
        zone._droppedFile = null;

        function showFile(name) {
            filename.textContent = name;
            zone.classList.add('has-file');
        }

        function clearFile() {
            input.value = '';
            zone._droppedFile = null;
            zone.classList.remove('has-file');
            filename.textContent = '';
        }

        // Clicking the zone opens the file dialog
        zone.addEventListener('click', function (e) {
            if (e.target === clearBtn || e.target.closest('.drop-zone-clear')) return;
            input.click();
        });

        // Show filename when file is selected via browse
        input.addEventListener('change', function () {
            zone._droppedFile = null; // browse overrides any prior drop
            if (this.files && this.files.length > 0) {
                showFile(this.files[0].name);
            }
        });

        // Clear button
        clearBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            clearFile();
        });

        // Drag events — stopPropagation prevents document-level handlers from interfering
        zone.addEventListener('dragenter', function (e) {
            e.preventDefault();
            e.stopPropagation();
            zone.classList.add('dragover');
        });
        zone.addEventListener('dragover', function (e) {
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'copy';
            zone.classList.add('dragover');
        });
        zone.addEventListener('dragleave', function (e) {
            if (e.relatedTarget && zone.contains(e.relatedTarget)) return;
            zone.classList.remove('dragover');
        });
        zone.addEventListener('drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
            zone.classList.remove('dragover');

            var files = e.dataTransfer.files;
            if (!files || files.length === 0) return;

            var file = files[0];
            zone._droppedFile = file;

            // Try to assign to input for normal form submit
            try {
                var dt = new DataTransfer();
                dt.items.add(file);
                input.files = dt.files;
            } catch (err) {
                // Fallback: form submit interceptor below will handle it
            }

            showFile(file.name);
        });

        // Intercept form submit if DataTransfer→input.files failed
        if (form && !form._dropSubmitHooked) {
            form._dropSubmitHooked = true;
            form.addEventListener('submit', function (e) {
                // Find any drop zone in this form with a stored file
                var dropZone = form.querySelector('.drop-zone');
                if (!dropZone || !dropZone._droppedFile) return; // normal submit
                var fileInput = dropZone.querySelector('.drop-zone-input');
                if (fileInput.files && fileInput.files.length > 0) return; // DataTransfer worked

                // DataTransfer failed — submit manually via fetch
                e.preventDefault();
                var formData = new FormData(form);
                formData.set(fileInput.name, dropZone._droppedFile, dropZone._droppedFile.name);

                // Show processing overlay
                var submitBtn = form.querySelector('button[type="submit"]');
                var overlay = form.querySelector('.processing-overlay');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.style.display = 'none';
                }
                if (overlay) overlay.style.display = 'block';

                fetch(form.action || window.location.href, {
                    method: 'POST',
                    body: formData,
                }).then(function (res) {
                    return res.text();
                }).then(function (html) {
                    document.open();
                    document.write(html);
                    document.close();
                }).catch(function (err) {
                    if (overlay) overlay.style.display = 'none';
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.style.display = '';
                        submitBtn.textContent = 'Retry';
                    }
                });
            });
        }
    });


    // ---- Tooltip (JS-positioned) ----
    var tooltipEl = null;
    document.querySelectorAll('.item-info[data-tip]').forEach(function (info) {
        info.addEventListener('mouseenter', function () {
            if (!tooltipEl) {
                tooltipEl = document.createElement('div');
                tooltipEl.className = 'tooltip';
                document.body.appendChild(tooltipEl);
            }
            tooltipEl.textContent = this.getAttribute('data-tip');
            var rect = this.getBoundingClientRect();
            // Position above, centered
            tooltipEl.style.left = '0';
            tooltipEl.style.top = '0';
            tooltipEl.classList.add('visible');
            var tipRect = tooltipEl.getBoundingClientRect();
            var left = rect.left + rect.width / 2 - tipRect.width / 2;
            var top = rect.top - tipRect.height - 8;
            // Keep within viewport
            if (left < 8) left = 8;
            if (left + tipRect.width > window.innerWidth - 8) left = window.innerWidth - tipRect.width - 8;
            if (top < 8) { top = rect.bottom + 8; } // flip below if no room above
            tooltipEl.style.left = left + 'px';
            tooltipEl.style.top = top + 'px';
        });
        info.addEventListener('mouseleave', function () {
            if (tooltipEl) tooltipEl.classList.remove('visible');
        });
    });


    // ---- Collapsible sections ----
    document.querySelectorAll('.collapsible .section-toggle').forEach(function (toggle) {
        toggle.addEventListener('click', function () {
            var section = this.closest('.collapsible');
            var btn = this.querySelector('.btn-collapse');
            var isCollapsed = section.classList.toggle('collapsed');
            if (btn) btn.setAttribute('aria-expanded', !isCollapsed);

            // Remember state in localStorage
            if (section.id) {
                localStorage.setItem('collapse-' + section.id, isCollapsed ? '1' : '0');
            }
        });

        // Restore state from localStorage
        var section = toggle.closest('.collapsible');
        if (section && section.id) {
            var saved = localStorage.getItem('collapse-' + section.id);
            if (saved === '1') {
                section.classList.add('collapsed');
                var btn = toggle.querySelector('.btn-collapse');
                if (btn) btn.setAttribute('aria-expanded', 'false');
            }
        }
    });


    // ---- Keyboard shortcuts ----
    document.addEventListener('keydown', function (e) {
        // Ctrl/Cmd+S — save current form
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            var form = document.querySelector('.form-page form, .release-form, .links-form.visible');
            if (form) {
                e.preventDefault();
                form.requestSubmit ? form.requestSubmit() : form.submit();
            }
        }

        // Escape — close open panels
        if (e.key === 'Escape') {
            // Close links form
            var lf = document.getElementById('links-form');
            if (lf && lf.classList.contains('visible')) {
                lf.classList.remove('visible');
                return;
            }
            // Close validate panel
            var vp = document.getElementById('validate-panel');
            if (vp && vp.classList.contains('visible')) {
                vp.classList.remove('visible');
                return;
            }
        }
    });


    // ---- Unsaved changes warning ----
    var formDirty = false;
    document.querySelectorAll('.form-page form, .release-form').forEach(function (form) {
        form.addEventListener('input', function () { formDirty = true; });
        form.addEventListener('submit', function () { formDirty = false; });
    });
    window.addEventListener('beforeunload', function (e) {
        if (formDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });


    // ---- Metadata mode toggle (artwork + video resizer pages) ----
    var metaModeRadios = document.querySelectorAll('input[name="metadata_mode"]');
    var releaseFields  = document.getElementById('metadata-release-fields');
    var manualFields   = document.getElementById('metadata-manual-fields');

    if (metaModeRadios.length > 0 && (releaseFields || manualFields)) {
        function updateMetadataVisibility() {
            var checked = document.querySelector('input[name="metadata_mode"]:checked');
            if (!checked) return;
            var mode = checked.value;

            if (releaseFields) releaseFields.style.display = (mode === 'release') ? 'block' : 'none';
            if (manualFields)  manualFields.style.display  = (mode === 'release' || mode === 'manual') ? 'block' : 'none';

            // In release mode, fields are auto-filled from API but remain editable
            // so users can override values (e.g. add a description not in the release JSON)
        }

        metaModeRadios.forEach(function (radio) {
            radio.addEventListener('change', updateMetadataVisibility);
        });
        updateMetadataVisibility(); // set initial state

        // AJAX: populate manual fields when a release is selected
        var releaseSelect = document.getElementById('metadata_release');
        if (releaseSelect) {
            function fetchAndFill(slug) {
                if (!slug) return;
                fetch('/api/release/' + encodeURIComponent(slug) + '/metadata')
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        var map = {
                            'meta_title':       data.title,
                            'meta_artist':      data.artist,
                            'meta_copyright':   data.copyright,
                            'meta_description': data.description,
                            'meta_genre':       data.genre,
                        };
                        Object.keys(map).forEach(function (id) {
                            var el = document.getElementById(id);
                            if (el) el.value = map[id] || '';
                        });
                    })
                    .catch(function () {}); // fail silently
            }

            releaseSelect.addEventListener('change', function () {
                fetchAndFill(this.value);
            });

            // Auto-trigger if a release is already selected (preselected via ?release= param)
            if (releaseSelect.value) {
                fetchAndFill(releaseSelect.value);
            }
        }
    }

});
