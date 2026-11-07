# Release Manager UI Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Release Manager UI with a strict CSS design token system, sidebar navigation, and restructured Release Detail, Engagement, and Promotion pages for a sleek dashboard aesthetic.

**Architecture:** Custom CSS redesign — no framework. Split monolithic `style.css` (6400 lines) into modular CSS files organized by concern. New sidebar + top bar layout via `base.html` changes. Release Detail gets tabbed interface, Engagement gets unified platform tabs, Promotion gets visual upgrade with slide-in panel. All vanilla JS, no framework.

**Tech Stack:** Flask/Jinja2 templates, custom CSS with CSS variables, vanilla JavaScript

**Spec:** `docs/superpowers/specs/2026-04-07-rm-ui-redesign-design.md`

---

## File Structure

### New files to create:
```
release_manager/static/css/
  tokens.css           -- CSS custom properties (colors, spacing, typography, radius, shadows)
  reset.css            -- Minimal reset/normalize
  layout.css           -- Sidebar, top bar, content area, responsive grid
  components.css       -- Buttons, badges, cards, inputs, dropdowns, modals, tabs, progress bars, toasts
  pages/
    dashboard.css      -- Dashboard release grid, social links
    release-detail.css -- Hero, tab bar, overview/calendar/checklist/distribution tabs
    engagement.css     -- Stats cards, platform tabs, contact cards, progress
    promotion.css      -- Metric cards, target list, slide-in panel, bulk actions
    artwork-resizer.css
    video-resizer.css
    seo-copy.css
    stats.css
    settings.css
  utilities.css        -- Spacing helpers, text alignment, visibility, flex shortcuts
```

### Files to modify:
- `release_manager/templates/base.html` — Replace top nav with sidebar + top bar layout
- `release_manager/templates/release_detail.html` — Hero + tabbed sections
- `release_manager/templates/engagement.html` — Stats row, platform tabs, redesigned cards
- `release_manager/templates/promotion.html` — Metric cards, larger targets, slide-in panel
- `release_manager/templates/dashboard.html` — Minor: remove blob dependency, inherit new layout
- `release_manager/static/app.js` — Add sidebar toggle, tab switching, slide-in panel, remove blob code

### Files to delete (after migration verified):
- `release_manager/static/style.css` — Replaced by modular CSS files

---

## Task 1: Design Tokens (`tokens.css`)

**Files:**
- Create: `release_manager/static/css/tokens.css`

- [ ] **Step 1: Create the tokens.css file**

Create `release_manager/static/css/tokens.css` with all design tokens. This is the foundation everything else depends on.

```css
/* ============================================================
   Design Tokens — Inch of Shadow Release Manager
   ============================================================ */

:root {
    /* --- Colors --- */
    --bg-base:          #060608;
    --bg-raised:        #0c0c10;
    --bg-surface:       #121218;
    --bg-surface-hover: #1a1a22;

    --accent:           #c9a84c;
    --accent-hover:     #e8d48b;
    --accent-dim:       rgba(201, 168, 76, 0.18);
    --accent-glow:      rgba(201, 168, 76, 0.25);

    --text-primary:     #ffffff;
    --text-secondary:   #a0a0b0;
    --text-muted:       #606070;

    --border:           rgba(255, 255, 255, 0.06);
    --border-strong:    rgba(255, 255, 255, 0.12);

    --success:          #4a7c59;
    --success-dim:      rgba(74, 124, 89, 0.15);
    --warning:          #b8860b;
    --warning-dim:      rgba(184, 134, 11, 0.15);
    --error:            #8b3a3a;
    --error-dim:        rgba(139, 58, 58, 0.15);
    --info:             #5a6e8a;
    --info-dim:         rgba(90, 110, 138, 0.15);

    /* --- Typography --- */
    --font-heading: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-body:    'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono:    'SF Mono', 'Menlo', 'Consolas', monospace;

    --text-xs:   12px;
    --text-sm:   13px;
    --text-base: 14px;
    --text-md:   16px;
    --text-lg:   20px;
    --text-xl:   24px;
    --text-2xl:  32px;

    --leading-tight:  1.3;
    --leading-normal: 1.6;
    --tracking-tight: -0.02em;

    /* --- Spacing (4px base) --- */
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --space-6: 32px;
    --space-7: 48px;
    --space-8: 64px;

    /* --- Border Radius --- */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;

    /* --- Shadows --- */
    --shadow-sm: 0 1px 3px rgba(0, 0, 8, 0.4);
    --shadow-md: 0 4px 12px rgba(0, 0, 8, 0.5);
    --shadow-lg: 0 8px 24px rgba(0, 0, 8, 0.6);
    --shadow-glow: 0 0 16px var(--accent-glow);

    /* --- Transitions --- */
    --transition-fast: 150ms ease;
    --transition-base: 250ms ease;

    /* --- Layout --- */
    --sidebar-width: 240px;
    --sidebar-collapsed: 64px;
    --topbar-height: 48px;
    --content-max-width: 1100px;

    /* --- Glass (sparingly) --- */
    --glass-bg: rgba(12, 12, 16, 0.8);
    --glass-blur: 12px;
}
```

- [ ] **Step 2: Verify the file was created**

Run: `ls -la release_manager/static/css/tokens.css`
Expected: File exists with the content above.

- [ ] **Step 3: Commit**

```bash
git add release_manager/static/css/tokens.css
git commit -m "feat(ui): add design token system for RM redesign"
```

---

## Task 2: CSS Reset (`reset.css`)

**Files:**
- Create: `release_manager/static/css/reset.css`

- [ ] **Step 1: Create reset.css**

```css
/* ============================================================
   Reset — Minimal normalize for RM
   ============================================================ */

/* Fonts — locally hosted */
@font-face {
    font-family: 'Space Grotesk';
    src: url('../fonts/SpaceGrotesk-Latin.woff2') format('woff2');
    font-weight: 400 700;
    font-style: normal;
    font-display: swap;
}
@font-face {
    font-family: 'Inter';
    src: url('../fonts/Inter-Latin.woff2') format('woff2');
    font-weight: 400 700;
    font-style: normal;
    font-display: swap;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    font-family: var(--font-body);
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    color: var(--text-secondary);
    background: var(--bg-raised);
}

h1, h2, h3, h4 {
    font-family: var(--font-heading);
    color: var(--text-primary);
    line-height: var(--leading-tight);
    letter-spacing: var(--tracking-tight);
}

h1 { font-size: var(--text-2xl); }
h2 { font-size: var(--text-lg); }
h3 { font-size: var(--text-md); }

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }

img { max-width: 100%; display: block; }

button, input, select, textarea {
    font-family: inherit;
    font-size: inherit;
    color: inherit;
    background: none;
    border: none;
    outline: none;
}

button { cursor: pointer; }

table { border-collapse: collapse; width: 100%; }

::selection { background: rgba(201, 168, 76, 0.3); color: var(--text-primary); }

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: var(--radius-sm); }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

/* Skip link */
.skip-link {
    position: absolute;
    top: -100%;
    left: var(--space-4);
    padding: var(--space-2) var(--space-4);
    background: var(--accent);
    color: var(--bg-base);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    font-weight: 600;
    z-index: 200;
}
.skip-link:focus { top: var(--space-2); }
```

- [ ] **Step 2: Commit**

```bash
git add release_manager/static/css/reset.css
git commit -m "feat(ui): add CSS reset with font-face declarations"
```

---

## Task 3: Layout — Sidebar + Top Bar (`layout.css` + `base.html`)

**Files:**
- Create: `release_manager/static/css/layout.css`
- Modify: `release_manager/templates/base.html`

- [ ] **Step 1: Create layout.css**

```css
/* ============================================================
   Layout — Sidebar, Top Bar, Content Area
   ============================================================ */

/* --- App Shell --- */
.app-shell {
    display: flex;
    min-height: 100vh;
}

/* --- Sidebar --- */
.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-width);
    height: 100vh;
    background: var(--bg-base);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    z-index: 100;
    transition: width var(--transition-base);
    overflow-x: hidden;
}

.sidebar.collapsed {
    width: var(--sidebar-collapsed);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    padding: var(--space-5) var(--space-4);
    border-bottom: 1px solid var(--border);
    text-decoration: none;
}

.sidebar-brand-text {
    font-family: var(--font-heading);
    font-size: var(--text-md);
    color: var(--text-primary);
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
}

.sidebar.collapsed .sidebar-brand-text {
    opacity: 0;
    width: 0;
}

.sidebar-brand-icon {
    width: 32px;
    height: 32px;
    min-width: 32px;
    background: var(--accent);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--bg-base);
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-md);
    margin-right: var(--space-3);
}

.sidebar.collapsed .sidebar-brand-icon {
    margin-right: 0;
}

/* --- Nav Groups --- */
.sidebar-nav {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4) 0;
}

.nav-group {
    margin-bottom: var(--space-4);
}

.nav-group-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    padding: 0 var(--space-4);
    margin-bottom: var(--space-1);
    white-space: nowrap;
    overflow: hidden;
}

.sidebar.collapsed .nav-group-label {
    opacity: 0;
    height: 0;
    margin: 0;
    padding: 0;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: var(--space-2) var(--space-4);
    color: var(--text-secondary);
    text-decoration: none;
    font-size: var(--text-sm);
    transition: background var(--transition-fast), color var(--transition-fast);
    border-left: 3px solid transparent;
    white-space: nowrap;
    overflow: hidden;
}

.nav-item:hover {
    background: var(--bg-surface);
    color: var(--text-primary);
}

.nav-item.active {
    background: var(--bg-surface);
    color: var(--text-primary);
    border-left-color: var(--accent);
}

.nav-item-icon {
    width: 20px;
    height: 20px;
    min-width: 20px;
    margin-right: var(--space-3);
    opacity: 0.6;
}

.nav-item.active .nav-item-icon { opacity: 1; }

.sidebar.collapsed .nav-item-icon { margin-right: 0; }

.nav-item-label {
    overflow: hidden;
    text-overflow: ellipsis;
}

.sidebar.collapsed .nav-item-label {
    opacity: 0;
    width: 0;
}

/* Sidebar bottom section */
.sidebar-bottom {
    padding: var(--space-3) var(--space-4);
    border-top: 1px solid var(--border);
}

.sidebar-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: var(--space-2);
    color: var(--text-muted);
    border-radius: var(--radius-md);
    transition: background var(--transition-fast);
}

.sidebar-toggle:hover {
    background: var(--bg-surface);
    color: var(--text-secondary);
}

/* Tooltip for collapsed sidebar */
.sidebar.collapsed .nav-item {
    position: relative;
    justify-content: center;
    padding: var(--space-2) 0;
}

.sidebar.collapsed .nav-item::after {
    content: attr(data-tooltip);
    position: absolute;
    left: calc(var(--sidebar-collapsed) + 8px);
    top: 50%;
    transform: translateY(-50%);
    background: var(--bg-surface);
    color: var(--text-primary);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity var(--transition-fast);
    box-shadow: var(--shadow-md);
    z-index: 110;
}

.sidebar.collapsed .nav-item:hover::after {
    opacity: 1;
}

/* New release button in sidebar */
.sidebar-new-release {
    display: flex;
    align-items: center;
    justify-content: center;
    width: calc(100% - var(--space-4) * 2);
    margin: var(--space-3) var(--space-4);
    padding: var(--space-2) var(--space-3);
    background: var(--accent);
    color: var(--bg-base);
    font-weight: 600;
    font-size: var(--text-sm);
    border-radius: var(--radius-md);
    text-decoration: none;
    transition: background var(--transition-fast);
    white-space: nowrap;
    overflow: hidden;
}

.sidebar-new-release:hover {
    background: var(--accent-hover);
    color: var(--bg-base);
}

.sidebar.collapsed .sidebar-new-release span {
    display: none;
}

/* --- Top Bar --- */
.topbar {
    position: fixed;
    top: 0;
    left: var(--sidebar-width);
    right: 0;
    height: var(--topbar-height);
    background: var(--bg-raised);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-5);
    z-index: 90;
    transition: left var(--transition-base);
}

.sidebar.collapsed ~ .main-area .topbar,
.app-shell.sidebar-collapsed .topbar {
    left: var(--sidebar-collapsed);
}

.topbar-breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-sm);
    color: var(--text-muted);
}

.topbar-breadcrumb a {
    color: var(--text-muted);
    text-decoration: none;
}

.topbar-breadcrumb a:hover { color: var(--text-secondary); }

.topbar-breadcrumb-sep {
    color: var(--text-muted);
    opacity: 0.4;
}

.topbar-breadcrumb-current {
    color: var(--text-secondary);
}

.topbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.topbar-release-ctx {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1) var(--space-3);
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    text-decoration: none;
    color: var(--text-secondary);
    font-size: var(--text-sm);
    transition: background var(--transition-fast);
}

.topbar-release-ctx:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
}

.topbar-release-art {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    object-fit: cover;
}

/* --- Content Area --- */
.main-area {
    flex: 1;
    margin-left: var(--sidebar-width);
    transition: margin-left var(--transition-base);
}

.app-shell.sidebar-collapsed .main-area {
    margin-left: var(--sidebar-collapsed);
}

.content {
    max-width: var(--content-max-width);
    margin: 0 auto;
    padding: calc(var(--topbar-height) + var(--space-6)) var(--space-7) var(--space-8);
}

/* --- Mobile --- */
.mobile-hamburger {
    display: none;
    background: none;
    border: none;
    color: var(--text-secondary);
    padding: var(--space-2);
    cursor: pointer;
}

.sidebar-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 99;
}

@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        width: var(--sidebar-width);
        z-index: 101;
    }

    .sidebar.mobile-open {
        transform: translateX(0);
    }

    .sidebar-overlay.visible {
        display: block;
    }

    .mobile-hamburger {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .main-area {
        margin-left: 0;
    }

    .topbar {
        left: 0;
    }

    .content {
        padding: calc(var(--topbar-height) + var(--space-5)) var(--space-4) var(--space-6);
    }
}
```

- [ ] **Step 2: Rewrite base.html with sidebar + top bar**

Replace the full content of `release_manager/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Release Manager{% endblock %} — Inch of Shadow</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/tokens.css') }}?v=1">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/reset.css') }}?v=1">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/layout.css') }}?v=1">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}?v=1">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/utilities.css') }}?v=1">
    {% block page_css %}{% endblock %}
    {% if theme_overrides %}
    <style>
        :root {
            {% for var, val in theme_overrides.items() %}
            {{ var }}: {{ val }};
            {% endfor %}
        }
    </style>
    {% endif %}
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>

    <div class="app-shell{% if sidebar_collapsed %} sidebar-collapsed{% endif %}">
        <!-- Sidebar -->
        <nav class="sidebar" id="sidebar" aria-label="Main navigation">
            <a href="{{ url_for('dashboard') }}" class="sidebar-brand">
                <span class="sidebar-brand-icon">I</span>
                <span class="sidebar-brand-text">Inch of Shadow</span>
            </a>

            <a href="{{ url_for('release_new') }}" class="sidebar-new-release" data-tooltip="New Release">
                <svg class="nav-item-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                <span>New Release</span>
            </a>

            <div class="sidebar-nav">
                <div class="nav-group">
                    <div class="nav-group-label">Releases</div>
                    <a href="{{ url_for('dashboard') }}" class="nav-item{% if request.endpoint == 'dashboard' %} active{% endif %}" data-tooltip="Dashboard">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                        <span class="nav-item-label">Dashboard</span>
                    </a>
                </div>

                <div class="nav-group">
                    <div class="nav-group-label">Tools</div>
                    <a href="{{ url_for('autopilot_page') }}" class="nav-item{% if request.endpoint == 'autopilot_page' %} active{% endif %}" data-tooltip="Autopilot">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
                        <span class="nav-item-label">Autopilot</span>
                    </a>
                    <a href="{{ url_for('artwork_resizer_page') }}" class="nav-item{% if request.endpoint == 'artwork_resizer_page' %} active{% endif %}" data-tooltip="Artwork Resizer">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                        <span class="nav-item-label">Artwork Resizer</span>
                    </a>
                    <a href="{{ url_for('video_resizer_page') }}" class="nav-item{% if request.endpoint == 'video_resizer_page' %} active{% endif %}" data-tooltip="Video Resizer">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
                        <span class="nav-item-label">Video Resizer</span>
                    </a>
                    <a href="{{ url_for('seo_copy_page') }}" class="nav-item{% if request.endpoint == 'seo_copy_page' %} active{% endif %}" data-tooltip="SEO Copy">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        <span class="nav-item-label">SEO Copy</span>
                    </a>
                </div>

                <div class="nav-group">
                    <div class="nav-group-label">Outreach</div>
                    <a href="{{ url_for('engagement_page') }}" class="nav-item{% if request.endpoint == 'engagement_page' %} active{% endif %}" data-tooltip="Engagement">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
                        <span class="nav-item-label">Engagement</span>
                    </a>
                    <a href="{{ url_for('promotion_page') }}" class="nav-item{% if request.endpoint == 'promotion_page' %} active{% endif %}" data-tooltip="Promotion">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        <span class="nav-item-label">Promotion</span>
                    </a>
                </div>

                <div class="nav-group">
                    <div class="nav-group-label">Analytics</div>
                    <a href="{{ url_for('stats_page') }}" class="nav-item{% if request.endpoint == 'stats_page' %} active{% endif %}" data-tooltip="Stats">
                        <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                        <span class="nav-item-label">Stats Dashboard</span>
                    </a>
                </div>
            </div>

            <div class="sidebar-bottom">
                <a href="{{ url_for('palette') }}" class="nav-item{% if request.endpoint == 'palette' %} active{% endif %}" data-tooltip="Settings">
                    <svg class="nav-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
                    <span class="nav-item-label">Settings</span>
                </a>
                <button class="sidebar-toggle" id="sidebar-toggle" aria-label="Toggle sidebar">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="11 17 6 12 11 7"/><polyline points="18 17 13 12 18 7"/></svg>
                </button>
            </div>
        </nav>

        <div class="sidebar-overlay" id="sidebar-overlay"></div>

        <!-- Main Area -->
        <div class="main-area">
            <header class="topbar">
                <div class="topbar-left">
                    <button class="mobile-hamburger" id="mobile-hamburger" aria-label="Open menu">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                    </button>
                    <nav class="topbar-breadcrumb" aria-label="Breadcrumb">
                        {% block breadcrumb %}
                        <span class="topbar-breadcrumb-current">Dashboard</span>
                        {% endblock %}
                    </nav>
                </div>
                <div class="topbar-right">
                    {% block topbar_right %}{% endblock %}
                </div>
            </header>

            <main id="main-content" class="content">
                {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                    <div class="flash flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
                {% endif %}
                {% endwith %}

                {% if error_title %}
                <div class="error-page">
                    <h1>{{ error_title }}</h1>
                    <p>{{ error_msg }}</p>
                    <a href="{{ url_for('dashboard') }}" class="btn btn-accent">Back to Dashboard</a>
                </div>
                {% else %}
                {% block content %}{% endblock %}
                {% endif %}
            </main>
        </div>
    </div>

    <div class="toast-container" id="toast-container" aria-live="polite"></div>
    <script src="{{ url_for('static', filename='app.js') }}?v=12"></script>
    {% block page_js %}{% endblock %}
</body>
</html>
```

**Key changes:**
- Replaced `<nav>` top bar with `<nav class="sidebar">` + `<header class="topbar">`
- Added `app-shell` flex container wrapping sidebar + main
- Added `{% block breadcrumb %}`, `{% block topbar_right %}`, `{% block page_css %}`, `{% block page_js %}` blocks
- Removed ambient glow blobs
- Navigation items now organized into groups (Releases, Tools, Outreach, Analytics)
- Each nav item has an SVG icon and `data-tooltip` for collapsed mode
- Mobile hamburger button + overlay for responsive drawer

- [ ] **Step 3: Start the app and verify the sidebar renders**

Run: `cd "/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode" && python -m release_manager.webapp`

Open `http://localhost:5001` in browser. Verify:
- Sidebar visible on the left with nav groups
- Top bar visible with breadcrumb
- Content area shifted right of sidebar
- Page may look broken (old CSS still referenced by page templates) — that's expected at this stage

- [ ] **Step 4: Commit**

```bash
git add release_manager/static/css/layout.css release_manager/templates/base.html
git commit -m "feat(ui): add sidebar navigation and top bar layout"
```

---

## Task 4: Components (`components.css`)

**Files:**
- Create: `release_manager/static/css/components.css`

- [ ] **Step 1: Create components.css with all shared components**

This file contains buttons, badges, cards, inputs, dropdowns, modals, tabs, progress bars, and toasts — all using design tokens. Migrate the relevant rules from the old `style.css`, converting all raw values to token references.

```css
/* ============================================================
   Components — Shared UI elements
   ============================================================ */

/* --- Buttons --- */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    font-size: var(--text-sm);
    font-weight: 600;
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    white-space: nowrap;
    min-height: 36px;
}

.btn-accent {
    background: var(--accent);
    color: var(--bg-base);
}
.btn-accent:hover {
    background: var(--accent-hover);
    color: var(--bg-base);
    transform: translateY(-1px);
}

.btn-secondary {
    background: var(--bg-surface);
    color: var(--text-secondary);
    border: 1px solid var(--border-strong);
}
.btn-secondary:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
}

.btn-sm {
    padding: var(--space-1) var(--space-3);
    font-size: var(--text-xs);
    min-height: 28px;
}

.btn-danger-ghost {
    color: var(--error);
    background: transparent;
}
.btn-danger-ghost:hover {
    background: var(--error-dim);
}

.btn-link {
    background: none;
    color: var(--accent);
    padding: 0;
    min-height: auto;
    font-weight: 400;
}
.btn-link:hover { color: var(--accent-hover); }

.btn-delete { color: var(--error); }
.btn-delete:hover { color: #b44; }

.btn:disabled, .btn[disabled] {
    opacity: 0.4;
    pointer-events: none;
}

/* --- Badges --- */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px var(--space-2);
    font-size: 11px;
    font-weight: 600;
    border-radius: var(--radius-sm);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.badge-single   { background: var(--accent-dim); color: var(--accent); }
.badge-ep       { background: var(--info-dim); color: var(--info); }
.badge-album    { background: var(--success-dim); color: var(--success); }

.badge-label    { background: rgba(201, 168, 76, 0.15); color: var(--accent); }
.badge-dj       { background: rgba(90, 110, 138, 0.15); color: #7a9abe; }
.badge-media    { background: rgba(160, 120, 180, 0.15); color: #b090c8; }
.badge-venue    { background: rgba(180, 140, 100, 0.15); color: #c4a478; }
.badge-promoter { background: rgba(100, 170, 140, 0.15); color: #78b89a; }
.badge-personal { background: rgba(140, 140, 160, 0.15); color: #9898a8; }
.badge-distributor { background: rgba(120, 140, 160, 0.15); color: #8898a8; }
.badge-artist   { background: rgba(170, 120, 130, 0.15); color: #c08898; }

.badge-dm { background: rgba(90, 110, 138, 0.2); color: var(--info); font-size: 10px; }
.badge-no-demos { background: var(--error-dim); color: var(--error); font-size: 10px; }

/* --- Cards --- */
.card {
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    padding: var(--space-4);
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-sm);
}

/* --- Forms --- */
.form-group { margin-bottom: var(--space-4); }

.form-label {
    display: block;
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: var(--space-1);
}

.form-input,
.form-select,
.form-textarea {
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-base);
    transition: border-color var(--transition-fast);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-dim);
}

.form-textarea { resize: vertical; min-height: 80px; }

.form-select {
    appearance: auto;
    cursor: pointer;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
}

/* --- Progress Bars --- */
.progress-bar {
    height: 6px;
    background: var(--bg-base);
    border-radius: 3px;
    overflow: hidden;
}

.progress-bar-lg { height: 8px; }

.progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
    transition: width var(--transition-base);
}

.progress-fill.complete {
    background: var(--success);
}

.progress-text {
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-top: var(--space-1);
}

/* --- Tabs --- */
.tab-bar {
    display: flex;
    gap: var(--space-5);
    border-bottom: 1px solid var(--border);
    margin-bottom: var(--space-5);
}

.tab-bar.sticky {
    position: sticky;
    top: var(--topbar-height);
    background: var(--bg-raised);
    z-index: 50;
    padding: var(--space-3) 0;
}

.tab-btn {
    padding: var(--space-2) 0;
    color: var(--text-muted);
    font-size: var(--text-sm);
    font-weight: 500;
    border-bottom: 3px solid transparent;
    transition: color var(--transition-fast), border-color var(--transition-fast);
    cursor: pointer;
    background: none;
    white-space: nowrap;
}

.tab-btn:hover { color: var(--text-secondary); }

.tab-btn.active {
    color: var(--text-primary);
    font-weight: 600;
    border-bottom-color: var(--accent);
}

.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* --- Modals --- */
.modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: 200;
    align-items: center;
    justify-content: center;
}

.modal-overlay.visible { display: flex; }

.modal {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-strong);
    box-shadow: var(--shadow-lg);
    max-width: 480px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-5);
    border-bottom: 1px solid var(--border);
}

.modal-header h3 {
    font-size: var(--text-md);
}

.modal-close {
    color: var(--text-muted);
    font-size: var(--text-lg);
    padding: var(--space-1);
    cursor: pointer;
    background: none;
    border: none;
}

.modal-body { padding: var(--space-5); }

.modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: var(--space-3);
    padding: var(--space-4) var(--space-5);
    border-top: 1px solid var(--border);
}

/* --- Toasts --- */
.toast-container {
    position: fixed;
    top: calc(var(--topbar-height) + var(--space-3));
    right: var(--space-4);
    z-index: 300;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.toast {
    padding: var(--space-3) var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    box-shadow: var(--shadow-md);
    cursor: pointer;
    animation: toast-in 200ms ease;
    max-width: 360px;
}

.toast-success { border-left: 3px solid var(--success); }
.toast-error   { border-left: 3px solid var(--error); }
.toast-info    { border-left: 3px solid var(--info); }

.toast-out {
    animation: toast-out 200ms ease forwards;
}

@keyframes toast-in {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes toast-out {
    from { opacity: 1; transform: translateX(0); }
    to   { opacity: 0; transform: translateX(20px); }
}

/* --- Sections --- */
.section {
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    padding: var(--space-5);
    margin-bottom: var(--space-5);
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
}

.section-header h2 {
    font-size: var(--text-lg);
}

/* --- Metric Cards --- */
.metric-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-5);
}

.metric-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    text-align: center;
}

.metric-value {
    font-size: var(--text-xl);
    font-weight: 700;
    font-family: var(--font-heading);
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: var(--space-1);
}

.metric-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* --- Slide-in Panel --- */
.slide-panel-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 150;
}

.slide-panel-overlay.visible { display: block; }

.slide-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 420px;
    max-width: 90vw;
    height: 100vh;
    background: var(--bg-surface);
    border-left: 1px solid var(--border-strong);
    box-shadow: var(--shadow-lg);
    z-index: 151;
    display: flex;
    flex-direction: column;
    transform: translateX(100%);
    transition: transform var(--transition-base);
}

.slide-panel.open { transform: translateX(0); }

.slide-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-5);
    border-bottom: 1px solid var(--border);
    min-height: 56px;
}

.slide-panel-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4) var(--space-5);
}

.slide-panel-footer {
    padding: var(--space-4) var(--space-5);
    border-top: 1px solid var(--border);
}

/* --- Floating Action Bar --- */
.floating-bar {
    display: none;
    position: fixed;
    bottom: var(--space-5);
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    padding: var(--space-3) var(--space-5);
    z-index: 80;
    align-items: center;
    gap: var(--space-4);
}

.floating-bar.visible { display: flex; }

/* --- Tables --- */
.data-table {
    width: 100%;
}

.data-table th {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: var(--space-2) var(--space-3);
    border-bottom: 1px solid var(--border);
    text-align: left;
}

.data-table td {
    padding: var(--space-3);
    border-bottom: 1px solid var(--border);
    font-size: var(--text-sm);
    color: var(--text-secondary);
}

.data-table tr:hover td {
    background: var(--bg-surface-hover);
}

/* --- Genre Pills --- */
.genre-pill {
    display: inline-block;
    padding: 2px var(--space-2);
    font-size: 11px;
    background: var(--bg-surface-hover);
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
}

/* --- Alerts --- */
.alert {
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-4);
    font-size: var(--text-sm);
}

.alert-overdue {
    background: var(--error-dim);
    border: 1px solid var(--error);
    color: var(--text-primary);
}

.alert-overdue a { color: var(--accent); }

/* --- Empty States --- */
.empty-state {
    text-align: center;
    padding: var(--space-8) var(--space-5);
    color: var(--text-muted);
}

.empty-state svg { margin: 0 auto var(--space-4); opacity: 0.3; }
.empty-state p { margin-bottom: var(--space-4); }

.empty-hint {
    color: var(--text-muted);
    font-size: var(--text-sm);
}
```

- [ ] **Step 2: Commit**

```bash
git add release_manager/static/css/components.css
git commit -m "feat(ui): add shared component styles (buttons, badges, cards, tabs, modals)"
```

---

## Task 5: Utilities (`utilities.css`)

**Files:**
- Create: `release_manager/static/css/utilities.css`

- [ ] **Step 1: Create utilities.css**

```css
/* ============================================================
   Utilities — Helper classes
   ============================================================ */

/* Spacing */
.mt-1 { margin-top: var(--space-1); }
.mt-2 { margin-top: var(--space-2); }
.mt-3 { margin-top: var(--space-3); }
.mt-4 { margin-top: var(--space-4); }
.mt-5 { margin-top: var(--space-5); }
.mb-1 { margin-bottom: var(--space-1); }
.mb-2 { margin-bottom: var(--space-2); }
.mb-3 { margin-bottom: var(--space-3); }
.mb-4 { margin-bottom: var(--space-4); }
.mb-5 { margin-bottom: var(--space-5); }

/* Flex */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }

/* Text */
.text-muted { color: var(--text-muted); }
.text-sm { font-size: var(--text-sm); }
.text-xs { font-size: var(--text-xs); }
.text-center { text-align: center; }
.font-heading { font-family: var(--font-heading); }

/* Visibility */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}

.hidden { display: none; }

/* Inline forms */
.inline-form { display: inline; }
```

- [ ] **Step 2: Commit**

```bash
git add release_manager/static/css/utilities.css
git commit -m "feat(ui): add utility CSS classes"
```

---

## Task 6: Dashboard Page CSS + Template Update

**Files:**
- Create: `release_manager/static/css/pages/dashboard.css`
- Modify: `release_manager/templates/dashboard.html`

- [ ] **Step 1: Create dashboard.css**

Migrate dashboard-specific styles from old `style.css`, converting to token references.

```css
/* ============================================================
   Dashboard Page
   ============================================================ */

.release-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-5);
    margin-bottom: var(--space-7);
}

.release-card-wrap {
    position: relative;
}

.release-card {
    display: flex;
    flex-direction: column;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast);
}

.release-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.card-artwork {
    aspect-ratio: 1;
    background: var(--bg-base);
    overflow: hidden;
}

.card-artwork img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.card-artwork-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: var(--text-muted);
    font-size: var(--text-sm);
}

.card-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4) var(--space-1);
}

.card-header h2 {
    font-size: var(--text-md);
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.card-meta {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: 0 var(--space-4);
    font-size: var(--text-sm);
    color: var(--text-muted);
}

.card-meta .genre {
    color: var(--accent);
    font-size: var(--text-xs);
}

.card-progress {
    padding: var(--space-3) var(--space-4);
}

.card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2) var(--space-4) var(--space-3);
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.overdue-badge {
    color: var(--error);
    font-weight: 600;
}

.next-deadline { color: var(--text-muted); }
.track-count { color: var(--text-muted); }

/* Card menu */
.card-menu-btn {
    position: absolute;
    top: var(--space-2);
    right: var(--space-2);
    padding: var(--space-2);
    color: var(--text-muted);
    background: var(--bg-surface);
    border-radius: var(--radius-sm);
    opacity: 0;
    transition: opacity var(--transition-fast);
    z-index: 5;
}

.release-card-wrap:hover .card-menu-btn { opacity: 1; }

.card-menu-dropdown {
    display: none;
    position: absolute;
    top: 40px;
    right: var(--space-2);
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    z-index: 10;
    overflow: hidden;
}

.card-menu-dropdown.open { display: block; }

.card-menu-delete {
    display: block;
    width: 100%;
    padding: var(--space-2) var(--space-4);
    text-align: left;
    color: var(--error);
    font-size: var(--text-sm);
    cursor: pointer;
    background: none;
    border: none;
}

.card-menu-delete:hover { background: var(--error-dim); }

/* Social Links section */
.socials-section { margin-top: var(--space-7); }

.socials-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
}

.socials-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.social-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
}

.social-icon { width: 20px; height: 20px; min-width: 20px; }

.social-info { flex: 1; overflow: hidden; }

.social-name {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-primary);
}

.social-url {
    font-size: var(--text-xs);
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
}

.social-copy {
    padding: var(--space-2);
    color: var(--text-muted);
    border-radius: var(--radius-sm);
    transition: color var(--transition-fast);
    cursor: pointer;
    background: none;
    border: none;
}

.social-copy:hover { color: var(--accent); }
```

- [ ] **Step 2: Update dashboard.html to use breadcrumb block and add page CSS**

At the top of `dashboard.html`, after `{% block title %}Dashboard{% endblock %}`, add:

```html
{% block page_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/dashboard.css') }}?v=1">
{% endblock %}
```

Remove the wrapping `<div class="dashboard">` — the `.content` class from base.html handles the container.

Replace the breadcrumb block:
```html
{% block breadcrumb %}
<span class="topbar-breadcrumb-current">Dashboard</span>
{% endblock %}
```

- [ ] **Step 3: Verify dashboard loads with new layout**

Run the app, open `http://localhost:5001`. Verify:
- Sidebar visible with Dashboard highlighted as active
- Release cards display in the grid
- No visual regressions on card layout

- [ ] **Step 4: Commit**

```bash
git add release_manager/static/css/pages/dashboard.css release_manager/templates/dashboard.html
git commit -m "feat(ui): redesign dashboard page with new design system"
```

---

## Task 7: Release Detail — Hero + Tabs

**Files:**
- Create: `release_manager/static/css/pages/release-detail.css`
- Modify: `release_manager/templates/release_detail.html`

- [ ] **Step 1: Create release-detail.css**

```css
/* ============================================================
   Release Detail Page — Hero + Tabbed Layout
   ============================================================ */

/* --- Hero --- */
.detail-hero {
    display: flex;
    gap: var(--space-5);
    margin-bottom: var(--space-5);
}

.detail-artwork {
    width: 200px;
    min-width: 200px;
    height: 200px;
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--bg-base);
}

.detail-artwork img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.detail-hero-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.detail-title-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-2);
}

.detail-title-row h1 {
    font-size: var(--text-2xl);
    margin: 0;
}

.detail-meta-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-3);
    color: var(--text-muted);
    font-size: var(--text-sm);
}

.detail-countdown {
    color: var(--text-secondary);
}

.detail-genres {
    display: flex;
    gap: var(--space-2);
}

.detail-progress-block {
    margin-bottom: var(--space-3);
}

.detail-progress-block .progress-bar {
    height: 8px;
    margin-bottom: var(--space-1);
}

.detail-actions {
    display: flex;
    gap: var(--space-2);
}

.artwork-upload {
    margin-top: var(--space-2);
}

/* Distribution status badge */
.dist-badge {
    font-size: 11px;
    font-weight: 600;
    padding: 2px var(--space-2);
    border-radius: var(--radius-sm);
    text-transform: uppercase;
}

.dist-badge-draft     { background: var(--bg-surface-hover); color: var(--text-muted); }
.dist-badge-submitted { background: var(--info-dim); color: var(--info); }
.dist-badge-approved  { background: var(--success-dim); color: var(--success); }
.dist-badge-live      { background: var(--success-dim); color: var(--success); }
.dist-badge-rejected  { background: var(--error-dim); color: var(--error); }

/* --- Tab Content --- */

/* Validate panel */
.validate-panel {
    margin-bottom: var(--space-4);
}

/* Banners */
.next-deadline-banner {
    padding: var(--space-3) var(--space-4);
    background: var(--accent-dim);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    margin-bottom: var(--space-4);
}

.next-deadline-banner.overdue {
    background: var(--error-dim);
    border: 1px solid var(--error);
}

.bcf-banner {
    padding: var(--space-3) var(--space-4);
    background: var(--warning-dim);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    margin-bottom: var(--space-4);
}

/* --- Overview tab --- */
.meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
}

.meta-item {
    padding: var(--space-3);
    background: var(--bg-base);
    border-radius: var(--radius-md);
}

.meta-wide { grid-column: 1 / -1; }

.meta-label {
    display: block;
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: var(--space-1);
}

.meta-value {
    font-size: var(--text-sm);
    color: var(--text-primary);
}

/* Tracks table */
.tracks-table {
    width: 100%;
}

.tracks-table th {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: var(--space-2) var(--space-3);
    border-bottom: 1px solid var(--border);
    text-align: left;
}

.tracks-table td {
    padding: var(--space-3);
    border-bottom: 1px solid var(--border);
    font-size: var(--text-sm);
    color: var(--text-secondary);
}

.tracks-table tr:hover td {
    background: var(--bg-surface-hover);
}

.track-actions {
    display: flex;
    gap: var(--space-2);
    justify-content: flex-end;
}

/* --- Calendar tab --- */
.cal-grid-wrap { overflow-x: auto; }

.cal-nav {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
}

.cal-month-label {
    font-weight: 600;
    color: var(--text-primary);
    min-width: 120px;
    text-align: center;
}

.cal-table {
    width: 100%;
    table-layout: fixed;
}

.cal-table th {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: var(--space-2);
    text-align: center;
}

.cal-cell {
    vertical-align: top;
    padding: var(--space-2);
    border: 1px solid var(--border);
    min-height: 70px;
    background: var(--bg-base);
}

.cal-cell.cal-empty { background: transparent; border-color: transparent; }
.cal-cell.cal-today { border-color: var(--accent); }
.cal-cell.cal-release-day { background: var(--accent-dim); }

.cal-day-num {
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-bottom: var(--space-1);
}

.cal-pill {
    display: inline-block;
    padding: 1px var(--space-2);
    font-size: 10px;
    border-radius: var(--radius-sm);
    margin: 1px;
    cursor: pointer;
    background: var(--bg-surface);
    color: var(--text-secondary);
    border: 1px solid var(--border);
}

.cal-pill.cal-pill-done {
    opacity: 0.5;
    text-decoration: line-through;
}

.cal-release-badge,
.cal-bcf-badge {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    padding: 1px var(--space-1);
    border-radius: 2px;
    margin-bottom: 2px;
}

.cal-release-badge { background: var(--accent); color: var(--bg-base); }
.cal-bcf-badge { background: var(--warning-dim); color: var(--warning); }

/* --- Checklist tab --- */
.checklist-categories {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: var(--space-4);
}

.checklist-cat-card {
    background: var(--bg-base);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    cursor: pointer;
    border: 1px solid var(--border);
    transition: border-color var(--transition-fast);
}

.checklist-cat-card:hover { border-color: var(--border-strong); }

.checklist-cat-card.expanded {
    grid-column: 1 / -1;
}

.checklist-cat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2);
}

.checklist-cat-name {
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--text-primary);
}

.checklist-cat-count {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.checklist-cat-tasks {
    display: none;
    margin-top: var(--space-3);
}

.checklist-cat-card.expanded .checklist-cat-tasks { display: block; }

.checklist-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--border);
    font-size: var(--text-sm);
    cursor: pointer;
}

.checklist-item:last-child { border-bottom: none; }

.checklist-item.done {
    opacity: 0.5;
}

.checklist-item.overdue .item-label { color: var(--error); }

.checklist-item input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--accent);
    cursor: pointer;
}

.item-label { flex: 1; color: var(--text-secondary); }
.item-date { font-size: var(--text-xs); color: var(--text-muted); }
.done-date { color: var(--success); }
.overdue-text { color: var(--error); }

.item-info {
    font-size: var(--text-sm);
    color: var(--text-muted);
    cursor: help;
}

/* --- Distribution tab --- */
.dist-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
}

/* --- Timeline section --- */
.timeline {
    position: relative;
    padding-left: var(--space-5);
}

.timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border);
}

.milestone {
    position: relative;
    padding: var(--space-2) 0;
}

.milestone-dot {
    position: absolute;
    left: calc(-1 * var(--space-5) + 4px);
    top: 12px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--bg-surface);
    border: 2px solid var(--border-strong);
}

.milestone.done .milestone-dot { background: var(--success); border-color: var(--success); }
.milestone.overdue .milestone-dot { background: var(--error); border-color: var(--error); }

.milestone-label {
    font-size: var(--text-sm);
    color: var(--text-primary);
}

.milestone-date {
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-left: var(--space-2);
}

.timeline-phase-label {
    font-size: var(--text-sm);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: var(--space-2);
}

.timeline-phase-post { margin-top: var(--space-4); }

/* --- SEO Copy section --- */
.seo-platform-card {
    background: var(--bg-base);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    margin-bottom: var(--space-3);
}

.seo-platform-card h3 {
    font-size: var(--text-md);
    margin-bottom: var(--space-3);
}

.seo-field { margin-bottom: var(--space-3); }

.seo-field-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-1);
}

.seo-field-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.char-counter {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.seo-field-body {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    line-height: var(--leading-normal);
}

.seo-tag-list { display: flex; flex-wrap: wrap; gap: var(--space-1); }

.seo-tag {
    display: inline-block;
    padding: 1px var(--space-2);
    font-size: 11px;
    background: var(--bg-surface);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
}

.trim-hint {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

/* --- Links section --- */
.links-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.link-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
}

.link-platform {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-secondary);
    min-width: 100px;
}

.link-url {
    font-size: var(--text-sm);
    color: var(--accent);
}

.links-form {
    display: none;
    margin-top: var(--space-4);
}

.links-form.visible { display: block; }

.links-form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
}

/* --- Responsive --- */
@media (max-width: 768px) {
    .detail-hero {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .detail-artwork {
        width: 160px;
        min-width: 160px;
        height: 160px;
    }

    .detail-actions { justify-content: center; }
    .meta-grid { grid-template-columns: 1fr; }
    .links-form-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 2: Rewrite release_detail.html with hero + tabs**

Replace the full `{% block content %}` section of `release_detail.html`. The key structural changes:

1. Add `{% block page_css %}` with the new CSS file
2. Add `{% block breadcrumb %}` with release link
3. **Hero section** — artwork left, info right (title, badge, genres, date/countdown, progress, actions, dist status)
4. **Tab bar** — Overview / Calendar / Checklist / Distribution / Timeline / SEO Copy / Links
5. **Tab panels** — each former section becomes a panel, only active one is visible
6. Existing inline `<script>` for calendar/SEO copy stays at the bottom

The template structure:

```html
{% extends "base.html" %}
{% block title %}{{ meta.title }}{% endblock %}

{% block page_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/release-detail.css') }}?v=1">
{% endblock %}

{% block breadcrumb %}
<a href="{{ url_for('dashboard') }}">Releases</a>
<span class="topbar-breadcrumb-sep">/</span>
<span class="topbar-breadcrumb-current">{{ meta.title }}</span>
{% endblock %}

{% block content %}
<div class="detail-page">

    <!-- Hero -->
    <div class="detail-hero">
        <div class="detail-artwork">
            {% if artwork_url %}
            <img src="{{ artwork_url }}" alt="{{ meta.title }}">
            {% else %}
            <span class="card-artwork-placeholder">No artwork</span>
            {% endif %}
            <form method="POST" action="{{ url_for('release_artwork', slug=rel.slug) }}" enctype="multipart/form-data" class="artwork-upload">
                <label class="btn btn-secondary btn-sm upload-btn">
                    Upload Artwork
                    <input type="file" name="artwork" accept="image/*" onchange="this.form.submit()" hidden>
                </label>
            </form>
        </div>
        <div class="detail-hero-info">
            <div class="detail-title-row">
                <h1>{{ meta.title }}</h1>
                <span class="badge badge-{{ meta.release_type|lower }}">{{ meta.release_type }}</span>
                {% set status = dist.get('status', 'draft') %}
                <span class="dist-badge dist-badge-{{ status }}">{{ status|title }}</span>
            </div>
            <div class="detail-meta-row">
                <span>{{ rel.release_date }}</span>
                <span class="detail-countdown">({{ rel.release_date|days_until }})</span>
                {% if meta.genre_primary %}
                <div class="detail-genres">
                    <span class="genre-pill">{{ meta.genre_primary }}</span>
                    {% if meta.genre_secondary %}
                    <span class="genre-pill">{{ meta.genre_secondary }}</span>
                    {% endif %}
                </div>
                {% endif %}
            </div>
            <div class="detail-progress-block">
                <div class="progress-bar progress-bar-lg">
                    <div class="progress-fill{% if pct == 100 %} complete{% endif %}" style="width: {{ pct }}%"></div>
                </div>
                <span class="progress-text checklist-progress">{{ done }}/{{ total }} tasks ({{ pct }}%)</span>
            </div>
            <div class="detail-actions">
                <a href="{{ url_for('release_edit', slug=rel.slug) }}" class="btn btn-secondary btn-sm">Edit Release</a>
                <button class="btn btn-secondary btn-sm btn-validate" data-slug="{{ rel.slug }}">Validate</button>
            </div>
        </div>
    </div>

    <!-- Validation Panel -->
    <div class="validate-panel" id="validate-panel"></div>

    <!-- Banners -->
    {% if next_dl %}
    <div class="next-deadline-banner{% if next_dl.id in overdue_tl %} overdue{% endif %}">
        <strong>Next:</strong> {{ next_dl.label }} — {{ next_dl.date }} ({{ next_dl.date|days_until }})
    </div>
    {% endif %}

    {% if bandcamp_friday %}
    <div class="bcf-banner">
        <strong>Bandcamp Friday {{ bandcamp_friday.date }}</strong> is
        {% if bandcamp_friday.days_away > 0 %}
            {{ bandcamp_friday.days_away }} day{{ 's' if bandcamp_friday.days_away != 1 else '' }} after your release
        {% else %}
            {{ bandcamp_friday.days_away|abs }} day{{ 's' if bandcamp_friday.days_away|abs != 1 else '' }} before your release
        {% endif %}
        — consider shifting to capture zero commission
    </div>
    {% endif %}

    <!-- Tab Bar -->
    <div class="tab-bar sticky" id="detail-tabs">
        <button class="tab-btn active" data-tab="overview">Overview</button>
        <button class="tab-btn" data-tab="calendar">Calendar</button>
        <button class="tab-btn" data-tab="checklist">Checklist</button>
        <button class="tab-btn" data-tab="distribution">Distribution</button>
        <button class="tab-btn" data-tab="timeline">Timeline</button>
        <button class="tab-btn" data-tab="seo">SEO Copy</button>
        <button class="tab-btn" data-tab="links">Links</button>
    </div>

    <!-- Overview Tab -->
    <div class="tab-panel active" id="tab-overview">
        <section class="section">
            <h2>Metadata</h2>
            <div class="meta-grid">
                <div class="meta-item"><span class="meta-label">Artist</span><span class="meta-value">{{ meta.artist }}</span></div>
                <div class="meta-item"><span class="meta-label">Copyright</span><span class="meta-value">{{ meta.copyright or '—' }}</span></div>
                <div class="meta-item"><span class="meta-label">Catalog #</span><span class="meta-value">{{ meta.catalog_number or '—' }}</span></div>
                {% if meta.description %}
                <div class="meta-item meta-wide"><span class="meta-label">Description</span><span class="meta-value">{{ meta.description }}</span></div>
                {% endif %}
            </div>
        </section>

        <section class="section">
            <div class="section-header">
                <h2>Tracks ({{ rel.tracks|length }})</h2>
                <a href="{{ url_for('track_new', slug=rel.slug) }}" class="btn btn-accent btn-sm">+ Add Track</a>
            </div>
            {% if rel.tracks %}
            <table class="tracks-table">
                <thead>
                    <tr>
                        <th>#</th><th>Title</th><th>BPM</th><th>Key</th><th>Duration</th><th>Genre</th><th>ISRC</th><th></th>
                    </tr>
                </thead>
                <tbody>
                    {% for t in rel.tracks %}
                    <tr>
                        <td>{{ t.number }}</td>
                        <td>{{ t.title }}</td>
                        <td>{{ t.bpm or '—' }}</td>
                        <td>{{ t.key or '—' }}</td>
                        <td>{{ t.duration or '—' }}</td>
                        <td>{{ t.genre_primary or '—' }}</td>
                        <td>{{ t.isrc or '—' }}</td>
                        <td class="track-actions">
                            <a href="{{ url_for('track_edit', slug=rel.slug, num=t.number) }}" class="btn-link">Edit</a>
                            <form method="POST" action="{{ url_for('track_delete', slug=rel.slug, num=t.number) }}" class="inline-form">
                                <button type="submit" class="btn-link btn-delete">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="empty-hint">No tracks yet. Add your first track to get started.</p>
            {% endif %}
        </section>
    </div>

    <!-- Calendar Tab -->
    <div class="tab-panel" id="tab-calendar">
        <section class="section">
            <h2>Release Calendar</h2>
            <div class="cal-grid-wrap">
                <div class="cal-nav">
                    <button type="button" class="btn btn-secondary btn-sm cal-prev" aria-label="Previous month">&larr;</button>
                    <span class="cal-month-label"></span>
                    <button type="button" class="btn btn-secondary btn-sm cal-next" aria-label="Next month">&rarr;</button>
                </div>
                {% for month_data in cal_grid.months %}
                <div class="cal-month" data-month-idx="{{ loop.index0 }}">
                    <table class="cal-table">
                        <thead>
                            <tr>
                                <th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for week in month_data.weeks %}
                            <tr>
                                {% for cell in week %}
                                {% if cell %}
                                <td class="cal-cell{% if cell.is_today %} cal-today{% endif %}{% if cell.is_release_day %} cal-release-day{% endif %}{% if cell.bandcamp_friday %} cal-bcf{% endif %}{% if cell.tasks %} cal-has-items{% endif %}">
                                    <div class="cal-day-num">{{ cell.day }}</div>
                                    {% if cell.bandcamp_friday %}
                                    <span class="cal-bcf-badge">BC Fri</span>
                                    {% endif %}
                                    {% if cell.is_release_day %}
                                    <span class="cal-release-badge">RELEASE</span>
                                    {% endif %}
                                    {% for item in cell.tasks %}
                                    <span class="cal-pill cal-cat-{{ item.category }}{% if item.done %} cal-pill-done{% endif %}"
                                          data-slug="{{ rel.slug }}"
                                          data-task-id="{{ item.id }}"
                                          data-done="{{ 'true' if item.done else 'false' }}"
                                          title="{{ item.label }}">
                                        {{ item.short or item.label }}
                                    </span>
                                    {% endfor %}
                                </td>
                                {% else %}
                                <td class="cal-cell cal-empty"></td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endfor %}
            </div>
        </section>
    </div>

    <!-- Checklist Tab -->
    <div class="tab-panel" id="tab-checklist">
        <section class="section">
            <h2>Checklist</h2>
            {% for cat_label, items in ordered_categories %}
            <div class="checklist-category">
                <h3>{{ cat_label }}</h3>
                {% for item in items %}
                <label class="checklist-item{% if item.done %} done{% endif %}{% if item.id in overdue_cl %} overdue{% endif %}">
                    <input type="checkbox"
                           data-slug="{{ rel.slug }}"
                           data-task-id="{{ item.id }}"
                           {% if item.done %}checked{% endif %}>
                    <span class="item-label">{{ item.label }}</span>
                    {% if tooltips.get(item.id) %}
                    <span class="item-info" data-tip="{{ tooltips[item.id] }}">&#9432;</span>
                    {% endif %}
                    {% if item.done and item.done_date %}
                    <span class="item-date done-date">Done {{ item.done_date }}</span>
                    {% elif item.due_date %}
                    <span class="item-date{% if item.id in overdue_cl %} overdue-text{% endif %}">{{ item.due_date|days_until }}</span>
                    {% endif %}
                </label>
                {% endfor %}
            </div>
            {% endfor %}
        </section>
    </div>

    <!-- Distribution Tab -->
    <div class="tab-panel" id="tab-distribution">
        <section class="section">
            <h2>Distribution</h2>
            <div class="meta-grid">
                <div class="meta-item">
                    <span class="meta-label">Distributor</span>
                    <span class="meta-value">{{ dist.distributor or '—' }}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Status</span>
                    <span class="meta-value">
                        <span class="dist-badge dist-badge-{{ dist.get('status', 'draft') }}">{{ dist.get('status', 'draft')|title }}</span>
                    </span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">UPC</span>
                    <span class="meta-value">{{ dist.upc or '—' }}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Release ID</span>
                    <span class="meta-value">{{ dist.get('distributor_id') or '—' }}</span>
                </div>
                {% if dist.submitted_date %}
                <div class="meta-item">
                    <span class="meta-label">Submitted</span>
                    <span class="meta-value">{{ dist.submitted_date }}</span>
                </div>
                {% endif %}
                {% if dist.get('approved_date') %}
                <div class="meta-item">
                    <span class="meta-label">Approved</span>
                    <span class="meta-value">{{ dist.approved_date }}</span>
                </div>
                {% endif %}
                {% if dist.live_date %}
                <div class="meta-item">
                    <span class="meta-label">Live</span>
                    <span class="meta-value">{{ dist.live_date }}</span>
                </div>
                {% endif %}
                {% if dist.notes %}
                <div class="meta-item meta-wide">
                    <span class="meta-label">Notes</span>
                    <span class="meta-value">{{ dist.notes }}</span>
                </div>
                {% endif %}
            </div>
        </section>
    </div>

    <!-- Timeline Tab -->
    <div class="tab-panel" id="tab-timeline">
        <section class="section">
            <h2>Timeline</h2>
            {% if tl_pre %}
            <h3 class="timeline-phase-label">Pre-Release</h3>
            <div class="timeline">
                {% for m in tl_pre %}
                <div class="milestone{% if m.done %} done{% endif %}{% if m.id in overdue_tl %} overdue{% endif %}">
                    <div class="milestone-dot"></div>
                    <div class="milestone-content">
                        <span class="milestone-label">{{ m.label }}</span>
                        <span class="milestone-date">{{ m.date }}{% if not m.done %} — {{ m.date|days_until }}{% endif %}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if tl_post %}
            <h3 class="timeline-phase-label timeline-phase-post">Post-Release</h3>
            <div class="timeline">
                {% for m in tl_post %}
                <div class="milestone{% if m.done %} done{% endif %}{% if m.id in overdue_tl %} overdue{% endif %}">
                    <div class="milestone-dot"></div>
                    <div class="milestone-content">
                        <span class="milestone-label">{{ m.label }}</span>
                        <span class="milestone-date">{{ m.date }}{% if not m.done %} — {{ m.date|days_until }}{% endif %}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </section>
    </div>

    <!-- SEO Copy Tab -->
    <div class="tab-panel" id="tab-seo">
        {% set seo = rel.get('seo_copy', {}) %}
        <section class="section">
            <h2>SEO Copy</h2>
            {% if seo %}
            <p class="trim-hint">
                Generated {{ seo.get('generated_at', '')|truncate(10, True, '') }}
                {% if seo.get('tone') %} / tone: {{ seo.tone }}{% endif %}
                <a href="{{ url_for('seo_copy_page', release=rel.slug) }}" class="btn btn-secondary btn-sm" style="margin-left:8px;">Regenerate</a>
            </p>

            {% set platforms = [
                ('SoundCloud', 'soundcloud', [('Description', 'description')]),
                ('Instagram', 'instagram', [('Caption', 'caption'), ('Hashtags', 'hashtags')]),
                ('YouTube', 'youtube', [('Titles', 'titles'), ('Description', 'description')]),
                ('Bandcamp', 'bandcamp', [('About', 'about'), ('Tags', 'tags')]),
                ('Beatport', 'beatport', [('Description', 'description')]),
                ('Spotify', 'spotify', [('Pitch', 'pitch'), ('Artist Pick', 'artist_pick')]),
                ('Apple Music', 'apple_music', [('Bio', 'bio')]),
            ] %}

            {% for label, key, fields in platforms %}
                {% set pdata = seo.get(key, {}) %}
                {% if pdata %}
                <div class="seo-platform-card">
                    <h3>{{ label }}</h3>
                    {% for flabel, fkey in fields %}
                        {% set val = pdata.get(fkey, '') %}
                        {% if val %}
                        <div class="seo-field">
                            <div class="seo-field-header">
                                <span class="seo-field-label">{{ flabel }}</span>
                                {% if val is string %}
                                <span class="char-counter">{{ val|length }} chars</span>
                                {% endif %}
                                <button type="button" class="btn btn-secondary btn-sm seo-copy-btn"
                                        data-text="{{ (val if val is string else val|join(', '))|e }}">Copy</button>
                            </div>
                            <div class="seo-field-body">
                                {% if val is string %}
                                    {{ val|e|replace('\n', '<br>'|safe) }}
                                {% elif val is iterable %}
                                    <span class="seo-tag-list">
                                    {% for item in val %}
                                        <span class="seo-tag">{{ item|e }}</span>
                                    {% endfor %}
                                    </span>
                                {% endif %}
                            </div>
                        </div>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endif %}
            {% endfor %}

            {% set premiere = seo.get('premiere_contacts', []) %}
            {% if premiere %}
            <div class="seo-platform-card">
                <h3>Premiere Contacts</h3>
                {% for c in premiere %}
                <div class="seo-field">
                    <div class="seo-field-body">
                        <strong>{{ c.name }}</strong>
                        {% if c.url %} — <a href="{{ c.url }}" target="_blank">{{ c.url|truncate(50) }}</a>{% endif %}
                        {% if c.reason %}<br><span class="trim-hint">{{ c.reason }}</span>{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% else %}
            <p class="empty-hint">No copy generated yet.
                <a href="{{ url_for('seo_copy_page', release=rel.slug) }}">Generate SEO copy</a>
                or use <code>/release-prep {{ meta.title }}</code> in Claude Code.
            </p>
            {% endif %}
        </section>
    </div>

    <!-- Links Tab -->
    <div class="tab-panel" id="tab-links">
        <section class="section">
            <div class="section-header">
                <h2>Platform Links</h2>
                <button class="btn btn-secondary btn-sm" id="toggle-links-form">Edit Links</button>
            </div>
            <div class="links-display">
                {% set has_links = rel.platform_links.values()|select|list|length > 0 %}
                {% if has_links %}
                <div class="links-grid">
                    {% for platform, url in rel.platform_links.items() %}
                    {% if url %}
                    <div class="link-item">
                        <span class="link-platform">{{ platform|platform_label }}</span>
                        <a href="{{ url }}" target="_blank" class="link-url">{{ url[:50] }}{% if url|length > 50 %}...{% endif %}</a>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% else %}
                <p class="empty-hint">No links yet. Add them as platforms go live.</p>
                {% endif %}
            </div>
            <form method="POST" action="{{ url_for('release_links', slug=rel.slug) }}" class="links-form" id="links-form">
                <div class="links-form-grid">
                    {% for platform in ALL_PLATFORMS %}
                    <div class="form-group">
                        <label for="link-{{ platform }}">{{ platform|platform_label }}</label>
                        <input type="url" id="link-{{ platform }}" name="{{ platform }}"
                               value="{{ rel.platform_links.get(platform, '') }}"
                               placeholder="https://..." class="form-input">
                    </div>
                    {% endfor %}
                </div>
                <div class="detail-actions">
                    <button type="submit" class="btn btn-accent btn-sm">Save Links</button>
                    <button type="button" class="btn btn-secondary btn-sm" id="cancel-links">Cancel</button>
                </div>
            </form>
        </section>
    </div>

</div>

<script>
/* SEO Copy button */
document.querySelectorAll('.seo-copy-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        var text = this.getAttribute('data-text')
            .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&');
        navigator.clipboard.writeText(text).then(function() {
            btn.textContent = 'Copied!';
            setTimeout(function() { btn.textContent = 'Copy'; }, 1500);
        });
    });
});

/* Calendar Grid */
(function() {
    var months = document.querySelectorAll('.cal-month');
    var label = document.querySelector('.cal-month-label');
    var prevBtn = document.querySelector('.cal-prev');
    var nextBtn = document.querySelector('.cal-next');
    if (!months.length) return;

    var currentIdx = 0;
    var todayIdx = -1;
    var releaseIdx = -1;
    months.forEach(function(m, i) {
        if (m.querySelector('.cal-today')) todayIdx = i;
        if (m.querySelector('.cal-release-day')) releaseIdx = i;
    });
    if (todayIdx >= 0) currentIdx = todayIdx;
    else if (releaseIdx >= 0) currentIdx = releaseIdx;

    function showMonth(idx) {
        months.forEach(function(m, i) {
            m.style.display = (i === idx) ? 'block' : 'none';
        });
        var monthNames = {{ cal_grid.months|map(attribute='month_name')|list|tojson }};
        label.textContent = monthNames[idx] || '';
        prevBtn.disabled = (idx === 0);
        nextBtn.disabled = (idx === months.length - 1);
    }

    prevBtn.addEventListener('click', function() {
        if (currentIdx > 0) { currentIdx--; showMonth(currentIdx); }
    });
    nextBtn.addEventListener('click', function() {
        if (currentIdx < months.length - 1) { currentIdx++; showMonth(currentIdx); }
    });

    showMonth(currentIdx);

    document.querySelectorAll('.cal-pill').forEach(function(pill) {
        pill.addEventListener('click', function() {
            var slug = this.dataset.slug;
            var taskId = this.dataset.taskId;
            var isDone = this.dataset.done === 'true';
            var action = isDone ? 'uncheck' : 'check';
            var el = this;

            fetch('/api/release/' + slug + '/' + action + '/' + taskId, { method: 'POST' })
                .then(function(res) {
                    if (!res.ok) throw new Error('failed');
                    return res.json();
                })
                .then(function(data) {
                    var newDone = !isDone;
                    el.dataset.done = newDone ? 'true' : 'false';
                    if (newDone) el.classList.add('cal-pill-done');
                    else el.classList.remove('cal-pill-done');

                    var cb = document.querySelector('.checklist-item input[data-task-id="' + taskId + '"]');
                    if (cb) {
                        cb.checked = newDone;
                        var item = cb.closest('.checklist-item');
                        if (newDone) { item.classList.add('done'); item.classList.remove('overdue'); }
                        else { item.classList.remove('done'); }
                    }

                    var prog = document.querySelector('.checklist-progress');
                    if (prog && data.total) {
                        var pct = Math.round(data.done * 100 / data.total);
                        prog.textContent = data.done + '/' + data.total + ' tasks (' + pct + '%)';
                        var fill = document.querySelector('.detail-progress-block .progress-fill');
                        if (fill) {
                            fill.style.width = pct + '%';
                            if (pct === 100) fill.classList.add('complete');
                            else fill.classList.remove('complete');
                        }
                    }
                });
        });
    });
})();
</script>
{% endblock %}
```

- [ ] **Step 3: Verify the release detail page loads with tabs**

Run the app, navigate to a release detail page. Verify:
- Hero section shows artwork, title, badges, progress
- Tab bar is visible below the hero
- Clicking tabs switches visible content
- Calendar still works (month nav, pill clicks)
- Checklist toggles still work

- [ ] **Step 4: Commit**

```bash
git add release_manager/static/css/pages/release-detail.css release_manager/templates/release_detail.html
git commit -m "feat(ui): redesign release detail with hero and tabbed layout"
```

---

## Task 8: JavaScript — Sidebar Toggle + Tab Switching

**Files:**
- Modify: `release_manager/static/app.js`

- [ ] **Step 1: Add sidebar toggle, tab switching, and slide-in panel JS**

Add the following code blocks to `app.js`, inside the existing `DOMContentLoaded` handler. Insert after the mobile nav toggle block (which will be replaced by the new sidebar code).

**Replace** the old mobile nav toggle block (lines ~8-16 of app.js) with:

```javascript
// ---- Sidebar toggle ----
var sidebar = document.getElementById('sidebar');
var sidebarToggle = document.getElementById('sidebar-toggle');
var appShell = document.querySelector('.app-shell');
if (sidebarToggle && sidebar && appShell) {
    // Restore collapsed state from localStorage
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        sidebar.classList.add('collapsed');
        appShell.classList.add('sidebar-collapsed');
    }
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        appShell.classList.toggle('sidebar-collapsed');
        localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    });
}

// ---- Mobile sidebar drawer ----
var mobileHamburger = document.getElementById('mobile-hamburger');
var sidebarOverlay = document.getElementById('sidebar-overlay');
if (mobileHamburger && sidebar && sidebarOverlay) {
    mobileHamburger.addEventListener('click', function() {
        sidebar.classList.toggle('mobile-open');
        sidebarOverlay.classList.toggle('visible');
    });
    sidebarOverlay.addEventListener('click', function() {
        sidebar.classList.remove('mobile-open');
        sidebarOverlay.classList.remove('visible');
    });
}
```

**Add** generic tab switching (works for release detail tabs, engagement platform tabs, and any future tabs):

```javascript
// ---- Generic tab switching ----
document.querySelectorAll('.tab-bar').forEach(function(tabBar) {
    tabBar.addEventListener('click', function(e) {
        var btn = e.target.closest('.tab-btn');
        if (!btn) return;
        var tabId = btn.dataset.tab;
        var container = tabBar.parentElement;

        // Deactivate all tabs in this bar
        tabBar.querySelectorAll('.tab-btn').forEach(function(t) { t.classList.remove('active'); });
        btn.classList.add('active');

        // Show matching panel, hide others
        container.querySelectorAll('.tab-panel').forEach(function(panel) {
            panel.classList.remove('active');
        });
        var target = container.querySelector('#tab-' + tabId);
        if (target) target.classList.add('active');
    });
});
```

**Add** slide-in panel toggle (for Promotion add targets):

```javascript
// ---- Slide-in panel ----
document.querySelectorAll('[data-open-panel]').forEach(function(trigger) {
    trigger.addEventListener('click', function() {
        var panelId = this.dataset.openPanel;
        var panel = document.getElementById(panelId);
        var overlay = document.getElementById(panelId + '-overlay');
        if (panel) panel.classList.add('open');
        if (overlay) overlay.classList.add('visible');
    });
});

document.querySelectorAll('[data-close-panel]').forEach(function(trigger) {
    trigger.addEventListener('click', function() {
        var panelId = this.dataset.closePanel;
        var panel = document.getElementById(panelId);
        var overlay = document.getElementById(panelId + '-overlay');
        if (panel) panel.classList.remove('open');
        if (overlay) overlay.classList.remove('visible');
    });
});

// Close panel on overlay click
document.querySelectorAll('.slide-panel-overlay').forEach(function(overlay) {
    overlay.addEventListener('click', function() {
        var panelId = this.id.replace('-overlay', '');
        var panel = document.getElementById(panelId);
        if (panel) panel.classList.remove('open');
        this.classList.remove('visible');
    });
});
```

**Remove** the old blob animation code if it exists in app.js (search for "blob" or "ambient" references and remove).

- [ ] **Step 2: Verify sidebar collapses and tabs switch**

Run the app. Verify:
- Clicking sidebar toggle collapses/expands sidebar
- Collapsed state persists after page reload (localStorage)
- On mobile width, hamburger opens sidebar as drawer
- Release detail tabs switch content correctly
- Escape key still closes modals

- [ ] **Step 3: Commit**

```bash
git add release_manager/static/app.js
git commit -m "feat(ui): add sidebar toggle, tab switching, and slide-in panel JS"
```

---

## Task 9: Engagement Page Redesign

**Files:**
- Create: `release_manager/static/css/pages/engagement.css`
- Modify: `release_manager/templates/engagement.html`

- [ ] **Step 1: Create engagement.css**

Key styles for the redesigned engagement page: stats cards at top, platform tabs, larger contact cards with avatar initials, progress feel.

```css
/* ============================================================
   Engagement Page
   ============================================================ */

/* Stats row */
.engagement-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-5);
}

.engagement-stat-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    text-align: center;
}

.engagement-stat-value {
    font-size: var(--text-xl);
    font-weight: 700;
    font-family: var(--font-heading);
    color: var(--text-primary);
}

.engagement-stat-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Controls row */
.engagement-controls {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
}

.engagement-controls select {
    padding: var(--space-2) var(--space-3);
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
}

/* Filters row */
.engagement-filters {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
}

.engagement-filters input[type="text"] {
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    width: 200px;
}

/* Contact cards */
.engagement-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.engagement-card {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    transition: border-color var(--transition-fast), opacity var(--transition-base), transform var(--transition-base);
}

.engagement-card:hover {
    border-color: var(--border-strong);
}

.engagement-card.done-out {
    opacity: 0;
    transform: translateX(20px);
}

/* Avatar */
.engagement-avatar {
    width: 44px;
    height: 44px;
    min-width: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--text-md);
    font-weight: 700;
    font-family: var(--font-heading);
    color: var(--text-primary);
}

.engagement-avatar-label    { background: rgba(201, 168, 76, 0.2); }
.engagement-avatar-dj       { background: rgba(90, 110, 138, 0.2); }
.engagement-avatar-media    { background: rgba(160, 120, 180, 0.2); }
.engagement-avatar-venue    { background: rgba(180, 140, 100, 0.2); }
.engagement-avatar-promoter { background: rgba(100, 170, 140, 0.2); }
.engagement-avatar-personal { background: rgba(140, 140, 160, 0.2); }

/* Card info */
.engagement-card-info {
    flex: 1;
    min-width: 0;
}

.engagement-card-name-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-1);
}

.engagement-card-name {
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.engagement-card-meta {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: var(--text-sm);
    color: var(--text-muted);
}

.engagement-card-meta .meta-genre { color: var(--accent); }

/* Card actions */
.engagement-card-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.engagement-card-actions .btn {
    min-height: 36px;
}

/* Profile link */
.card-profile-link {
    font-size: var(--text-xs);
    color: var(--accent);
    margin-top: var(--space-1);
    display: inline-block;
}

/* Platform sections (for queues that stack) */
.engagement-section {
    margin-bottom: var(--space-5);
}

.engagement-section .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3);
}

.section-header-left {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.section-icon { color: var(--text-muted); }

.queue-today-badge {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 1px var(--space-2);
    border-radius: var(--radius-sm);
}

.section-progress {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.engagement-count {
    font-size: var(--text-sm);
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}

.engagement-empty-sm {
    padding: var(--space-5);
    text-align: center;
    color: var(--text-muted);
    font-size: var(--text-sm);
}

/* SC stats */
.sc-stats {
    display: flex;
    gap: var(--space-3);
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-top: var(--space-1);
}

/* Collapsible sections */
.collapsible-section { margin-bottom: var(--space-4); }

.collapsible-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    cursor: pointer;
    color: inherit;
}

.collapsible-toggle[aria-expanded="true"] .collapsible-chevron {
    transform: rotate(180deg);
}

.collapsible-body {
    display: none;
    padding: var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 var(--radius-md) var(--radius-md);
}

.collapsible-toggle[aria-expanded="true"] + .collapsible-body {
    display: block;
}

.section-count-badge {
    font-size: 11px;
    font-weight: 600;
    padding: 1px var(--space-2);
    border-radius: var(--radius-sm);
    background: var(--bg-surface-hover);
    color: var(--text-muted);
}

.section-hint {
    font-size: var(--text-sm);
    color: var(--text-muted);
    margin-bottom: var(--space-3);
}

/* Discovery seeds */
.discovery-seeds {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin-bottom: var(--space-4);
}

.seed-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3);
    background: var(--bg-base);
    border-radius: var(--radius-md);
}

.seed-name {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-primary);
}

.seed-meta {
    display: flex;
    gap: var(--space-3);
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.seed-links {
    display: flex;
    gap: var(--space-2);
}

.seed-link {
    font-size: var(--text-xs);
    color: var(--accent);
}

/* Log follow form */
.log-follow-form { margin-top: var(--space-4); }

.log-follow-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.log-follow-at {
    font-size: var(--text-md);
    color: var(--text-muted);
}

.log-follow-input {
    flex: 1;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
}

.log-follow-platform-toggle {
    display: flex;
    gap: var(--space-1);
}

.platform-btn {
    padding: var(--space-2);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    background: none;
    border: 1px solid var(--border);
    cursor: pointer;
}

.platform-btn.active {
    color: var(--accent);
    border-color: var(--accent);
    background: var(--accent-dim);
}

/* Follows list */
.follows-list-toggle {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-3);
    color: var(--text-muted);
    font-size: var(--text-sm);
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
}

.follows-list-panel {
    display: none;
    margin-top: var(--space-2);
}

.follows-list-panel.open { display: block; }

.follows-list-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    font-size: var(--text-sm);
    border-bottom: 1px solid var(--border);
}

.follows-list-name {
    flex: 1;
    color: var(--text-primary);
}

.follows-list-days {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

/* Unfollow section */
.unfollow-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.unfollow-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border-radius: var(--radius-md);
}

.unfollow-name {
    font-size: var(--text-sm);
    color: var(--text-primary);
}

.unfollow-link { color: var(--accent); text-decoration: none; }

.unfollow-meta {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.unfollow-platform-badge {
    font-size: 10px;
    font-weight: 600;
    padding: 1px var(--space-1);
    border-radius: 2px;
    text-transform: uppercase;
}

.unfollow-instagram { background: rgba(193, 53, 132, 0.15); color: #c13584; }
.unfollow-soundcloud { background: rgba(255, 136, 0, 0.15); color: #ff8800; }

.btn-unfollow {
    font-size: var(--text-xs);
    padding: var(--space-1) var(--space-3);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
}

.btn-unfollow:hover { border-color: var(--error); color: var(--error); }

/* Comment generator */
.comment-widget-body {
    padding: var(--space-3);
    background: var(--bg-base);
    border-radius: var(--radius-md);
}

.comment-widget-tabs {
    display: flex;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
}

.comment-tab {
    padding: var(--space-1) var(--space-3);
    font-size: var(--text-xs);
    border-radius: var(--radius-sm);
    background: var(--bg-surface);
    color: var(--text-muted);
    cursor: pointer;
    border: none;
}

.comment-tab.active {
    background: var(--accent-dim);
    color: var(--accent);
}

.comment-widget-display {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.comment-widget-output {
    flex: 1;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    color: var(--text-secondary);
    cursor: pointer;
    min-height: 36px;
    display: flex;
    align-items: center;
}

.comment-dice {
    padding: var(--space-2);
    color: var(--text-muted);
    background: none;
    border: none;
    cursor: pointer;
}

.comment-dice:hover { color: var(--accent); }

/* History */
.history-list {
    display: flex;
    flex-direction: column;
}

.history-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    font-size: var(--text-sm);
    border-bottom: 1px solid var(--border);
}

.history-name { color: var(--text-primary); flex: 1; }
.history-action { color: var(--text-muted); }
.history-platform { font-size: var(--text-xs); color: var(--text-muted); }
.history-date { font-size: var(--text-xs); color: var(--text-muted); }

/* Genre tag popup */
.genre-tag-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 200;
    align-items: center;
    justify-content: center;
}

.genre-tag-overlay.visible { display: flex; }

.genre-tag-popup {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-strong);
    box-shadow: var(--shadow-lg);
    padding: var(--space-5);
    max-width: 400px;
    width: 90%;
}

.genre-tag-popup-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
}

.genre-tag-close {
    font-size: var(--text-lg);
    color: var(--text-muted);
    background: none;
    border: none;
    cursor: pointer;
}

.genre-tag-current { margin-bottom: var(--space-3); }

.genre-tag-current-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
}

.genre-tag-current-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1);
    margin-top: var(--space-1);
}

.genre-tag-quick-picks {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
}

.genre-pick {
    padding: var(--space-1) var(--space-3);
    font-size: var(--text-sm);
    background: var(--bg-base);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    cursor: pointer;
}

.genre-pick:hover { border-color: var(--accent); color: var(--accent); }

.genre-pick-personal { border-color: var(--info); color: var(--info); }

.genre-tag-custom {
    display: flex;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
}

.genre-tag-custom input {
    flex: 1;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
}

.genre-tag-hint {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

/* Category dropdown */
.cat-dropdown-overlay {
    position: fixed;
    inset: 0;
    z-index: 190;
}

.cat-dropdown {
    position: absolute;
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    padding: var(--space-2) 0;
    min-width: 140px;
}

.cat-dropdown-title {
    padding: var(--space-2) var(--space-3);
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
}

.cat-dropdown-opt {
    display: block;
    width: 100%;
    padding: var(--space-2) var(--space-3);
    text-align: left;
    font-size: var(--text-sm);
    color: var(--text-secondary);
    cursor: pointer;
    background: none;
    border: none;
}

.cat-dropdown-opt:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
}

/* Badge category edit */
.badge-category-edit { cursor: pointer; }

/* Release identity bar */
.release-identity-bar {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-5);
}

.release-identity-bar-hidden { display: none; }

.release-artwork-hero {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-sm);
    object-fit: cover;
}

.release-artwork-hero-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-base);
}

.release-identity-title {
    font-size: var(--text-md);
    margin: 0;
}

.release-context-badge {
    font-size: var(--text-xs);
    color: var(--accent);
}

/* Tag button */
.btn-tag-genre {
    font-size: 10px;
    padding: 1px var(--space-2);
    background: var(--bg-surface-hover);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    cursor: pointer;
}

.btn-tag-genre:hover { color: var(--accent); border-color: var(--accent); }

/* Remove button */
.btn-remove {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: var(--text-xs);
    cursor: pointer;
    padding: var(--space-1);
}

.btn-remove:hover { color: var(--error); }
```

- [ ] **Step 2: Update engagement.html template**

Add `{% block page_css %}` and `{% block breadcrumb %}` at the top. The structural change is adding avatar initials to each contact card. The existing template structure stays largely the same — the CSS does the heavy lifting.

Key changes to the template:
- Add page CSS block
- Add breadcrumb block
- Add avatar div to each engagement card: `<div class="engagement-avatar engagement-avatar-{{ contact.category }}">{{ contact.name[0]|upper }}</div>`
- Wrap card info in `<div class="engagement-card-info">` and actions in `<div class="engagement-card-actions">`

- [ ] **Step 3: Verify engagement page**

Run the app, navigate to engagement. Verify:
- Stats visible at top
- Contact cards have avatar initials
- Actions are comfortable size
- Platform sections render correctly
- Collapsible sections work

- [ ] **Step 4: Commit**

```bash
git add release_manager/static/css/pages/engagement.css release_manager/templates/engagement.html
git commit -m "feat(ui): redesign engagement page with stats cards and larger contact cards"
```

---

## Task 10: Promotion Page Visual Upgrade

**Files:**
- Create: `release_manager/static/css/pages/promotion.css`
- Modify: `release_manager/templates/promotion.html`

- [ ] **Step 1: Create promotion.css**

Key: metric cards for stats, larger target rows, slide-in panel for add targets, floating bulk action bar. Migrate promotion-specific styles from old `style.css` to token-based rules.

```css
/* ============================================================
   Promotion Page
   ============================================================ */

.promotion-page h1 {
    font-size: var(--text-2xl);
    margin-bottom: var(--space-1);
}

.promotion-subtitle {
    color: var(--text-muted);
    font-size: var(--text-sm);
    margin-bottom: var(--space-5);
}

.promotion-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: var(--space-5);
}

/* Release selector */
.promo-select {
    padding: var(--space-2) var(--space-3);
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    min-width: 200px;
}

/* Campaign stats — metric cards */
.promo-stats-section { margin-bottom: var(--space-5); }

.promo-stats-bar {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-3);
}

.promo-stat {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    text-align: center;
}

.promo-stat-value {
    font-size: var(--text-xl);
    font-weight: 700;
    font-family: var(--font-heading);
    color: var(--text-primary);
    display: block;
}

.promo-stat-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.promo-stat-targets .promo-stat-value { color: var(--text-primary); }
.promo-stat-sent .promo-stat-value    { color: var(--info); }
.promo-stat-replied .promo-stat-value { color: var(--accent); }
.promo-stat-played .promo-stat-value  { color: var(--success); }
.promo-stat-rejected .promo-stat-value { color: var(--error); }

.promo-progress-wrap {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.promo-progress-bar {
    flex: 1;
    height: 8px;
    background: var(--bg-base);
    border-radius: 4px;
    overflow: hidden;
}

.promo-progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 4px;
    transition: width var(--transition-base);
}

.promo-progress-pct {
    font-size: var(--text-sm);
    color: var(--text-muted);
    min-width: 36px;
}

/* Empty state */
.promo-empty-state {
    text-align: center;
    padding: var(--space-8);
    color: var(--text-muted);
}

.promo-empty-state svg { margin-bottom: var(--space-4); opacity: 0.3; }

.promo-empty-sm {
    text-align: center;
    padding: var(--space-5);
    color: var(--text-muted);
    font-size: var(--text-sm);
}

/* Contact discovery panel */
.promo-contacts-panel {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-5);
    margin-bottom: var(--space-5);
}

.promo-contacts-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
}

.promo-contacts-header h2 { font-size: var(--text-lg); }

.promo-added-counter {
    font-size: var(--text-sm);
    color: var(--text-muted);
    font-weight: 400;
}

.promo-genre-hint {
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-top: var(--space-1);
}

/* Filters */
.promo-filters { margin-bottom: var(--space-4); }

.promo-filter-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-3);
    flex-wrap: wrap;
}

.promo-search-input {
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    width: 200px;
}

.promo-cat-filters {
    display: flex;
    gap: var(--space-1);
}

.promo-cat-btn {
    padding: var(--space-1) var(--space-3);
    font-size: var(--text-xs);
    border-radius: var(--radius-sm);
    background: var(--bg-base);
    color: var(--text-muted);
    border: 1px solid var(--border);
    cursor: pointer;
}

.promo-cat-btn.active {
    background: var(--accent-dim);
    color: var(--accent);
    border-color: var(--accent);
}

.promo-score-filters {
    display: flex;
    align-items: center;
    gap: var(--space-1);
}

.promo-filter-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.promo-score-btn {
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
    border-radius: var(--radius-sm);
    background: var(--bg-base);
    color: var(--text-muted);
    border: 1px solid var(--border);
    cursor: pointer;
}

.promo-score-btn.active {
    background: var(--accent-dim);
    color: var(--accent);
    border-color: var(--accent);
}

/* Multi-select filters */
.promo-multi-filter { position: relative; }

.promo-filter-toggle {
    padding: var(--space-1) var(--space-3);
    font-size: var(--text-xs);
    border-radius: var(--radius-sm);
    background: var(--bg-base);
    color: var(--text-muted);
    border: 1px solid var(--border);
    cursor: pointer;
}

.filter-count {
    font-size: 10px;
    color: var(--accent);
}

.promo-filter-dropdown {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background: var(--bg-surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    padding: var(--space-2);
    z-index: 60;
    min-width: 200px;
    max-height: 250px;
    overflow-y: auto;
}

.promo-filter-dropdown.open { display: block; }

.promo-filter-search {
    width: 100%;
    padding: var(--space-2);
    background: var(--bg-base);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: var(--text-xs);
    margin-bottom: var(--space-2);
}

.promo-filter-option {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-1) var(--space-2);
    font-size: var(--text-xs);
    color: var(--text-secondary);
    cursor: pointer;
}

.promo-filter-option:hover { background: var(--bg-surface-hover); }

.promo-filter-actions {
    padding-top: var(--space-2);
    border-top: 1px solid var(--border);
}

.promo-filter-clear {
    font-size: var(--text-xs);
    color: var(--text-muted);
    background: none;
    border: none;
    cursor: pointer;
    padding: var(--space-1) var(--space-2);
}

.promo-email-filter-label {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: var(--text-xs);
    color: var(--text-muted);
    cursor: pointer;
}

/* Contact rows */
.promo-contact-list {
    max-height: 600px;
    overflow-y: auto;
}

.promo-contact-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border);
    transition: background var(--transition-fast);
}

.promo-contact-row:hover { background: var(--bg-surface-hover); }

.promo-contact-added { opacity: 0.5; }

.promo-contact-info { flex: 1; min-width: 0; }

.promo-contact-name-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    flex-wrap: wrap;
}

.promo-contact-name {
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--text-primary);
}

.promo-contact-subtype {
    font-size: 10px;
    color: var(--text-muted);
}

.promo-boss-tag {
    font-size: 10px;
    padding: 1px var(--space-2);
    border-radius: var(--radius-sm);
    background: rgba(201, 168, 76, 0.1);
    color: var(--accent);
}

.promo-boss-tag-dj { background: rgba(90, 110, 138, 0.1); color: var(--info); }

.promo-contact-email-icon { color: var(--text-muted); vertical-align: middle; }

.promo-score-pill {
    font-size: 11px;
    font-weight: 600;
    padding: 1px var(--space-2);
    border-radius: var(--radius-sm);
}

.score-high { background: var(--success-dim); color: var(--success); }
.score-mid  { background: var(--warning-dim); color: var(--warning); }
.score-low  { background: var(--bg-surface-hover); color: var(--text-muted); }

.promo-contact-meta {
    display: flex;
    gap: var(--space-3);
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-top: var(--space-1);
}

.promo-add-btn {
    padding: var(--space-2);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    cursor: pointer;
    min-width: 36px;
    min-height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.promo-add-btn:hover { border-color: var(--accent); color: var(--accent); }
.promo-add-btn:disabled { opacity: 0.3; cursor: default; }

.promo-list-info {
    padding: var(--space-3);
    text-align: center;
    font-size: var(--text-xs);
    color: var(--text-muted);
}

/* Press list section */
.promo-presslist-section {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-5);
}

.promo-presslist-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.promo-target-count {
    font-size: var(--text-sm);
    color: var(--text-muted);
    font-weight: 400;
}

/* Follow-up section */
.promo-followup-section {
    background: var(--bg-base);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    margin-bottom: var(--space-4);
}

.promo-followup-urgent { border: 1px solid var(--warning); }

.promo-followup-header {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-3);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-primary);
}

.promo-followup-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--warning);
    color: var(--bg-base);
    font-size: 11px;
    font-weight: 700;
}

.promo-group-count {
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-weight: 400;
}

.promo-followup-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--border);
}

.promo-followup-overdue { color: var(--warning); }

.promo-followup-days {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.promo-followup-days-urgent { color: var(--warning); font-weight: 600; }

/* Target groups */
.promo-status-group {
    margin-bottom: var(--space-3);
}

.promo-group-toggle {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border-radius: var(--radius-md);
    cursor: pointer;
    border: none;
    color: inherit;
}

.promo-group-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.promo-dot-not-sent { background: var(--text-muted); }
.promo-dot-sent     { background: var(--info); }
.promo-dot-replied  { background: var(--accent); }
.promo-dot-played   { background: var(--success); }
.promo-dot-charted  { background: var(--success); }
.promo-dot-rejected { background: var(--error); }

.promo-group-label {
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-primary);
}

.promo-group-chevron {
    margin-left: auto;
    transition: transform var(--transition-fast);
}

.promo-status-group.is-expanded .promo-group-chevron {
    transform: rotate(180deg);
}

.promo-group-body {
    display: none;
    padding: var(--space-2) 0;
}

.promo-status-group.is-expanded .promo-group-body { display: block; }

/* Target rows */
.promo-target-row {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-2);
}

.promo-target-row:hover { border-color: var(--border-strong); }

.promo-target-check {
    width: 16px;
    height: 16px;
    accent-color: var(--accent);
}

.promo-target-info { flex: 1; min-width: 0; }

.promo-target-name-row {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    flex-wrap: wrap;
}

.promo-target-name {
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--text-primary);
    text-decoration: none;
}

a.promo-target-name:hover { color: var(--accent); }

.promo-target-meta-inline {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.promo-target-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.promo-status-select {
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    min-height: 36px;
}

.promo-notes-btn {
    padding: var(--space-2);
    color: var(--text-muted);
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    cursor: pointer;
    min-width: 36px;
    min-height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.promo-notes-btn.has-notes { color: var(--accent); border-color: var(--accent); }

.promo-remove-btn {
    padding: var(--space-2);
    color: var(--text-muted);
    background: none;
    border: none;
    cursor: pointer;
}

.promo-remove-btn:hover { color: var(--error); }

.btn-hide { color: var(--text-muted); background: none; border: none; cursor: pointer; }
.btn-hide:hover { color: var(--error); }

/* Batch bar */
.promo-batch-bar {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border-radius: var(--radius-md);
}

.promo-batch-count {
    font-size: var(--text-sm);
    color: var(--text-secondary);
}

/* Genre badge pills */
.genre-badge-pill {
    display: inline-block;
    padding: 2px var(--space-2);
    font-size: 11px;
    background: var(--accent-dim);
    color: var(--accent);
    border-radius: var(--radius-sm);
}

.genre-badge-secondary {
    background: var(--bg-surface-hover);
    color: var(--text-secondary);
}

/* Email compose modal */
.email-compose-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: 200;
    align-items: center;
    justify-content: center;
}

.email-compose-overlay.visible { display: flex; }

.email-compose-modal {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-strong);
    box-shadow: var(--shadow-lg);
    max-width: 600px;
    width: 95%;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
}

.email-compose-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-5);
    border-bottom: 1px solid var(--border);
}

.email-compose-close {
    font-size: var(--text-lg);
    color: var(--text-muted);
    cursor: pointer;
    background: none;
    border: none;
}

.email-compose-body {
    padding: var(--space-5);
    overflow-y: auto;
    flex: 1;
}

.email-field { margin-bottom: var(--space-4); }

.email-label {
    display: block;
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: var(--space-1);
}

.email-input {
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
}

.email-select {
    width: 100%;
    padding: var(--space-2) var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
}

.email-textarea {
    width: 100%;
    padding: var(--space-3);
    background: var(--bg-base);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--text-sm);
    resize: vertical;
    min-height: 200px;
    font-family: var(--font-body);
    line-height: var(--leading-normal);
}

.email-compose-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4) var(--space-5);
    border-top: 1px solid var(--border);
}

.email-compose-actions {
    display: flex;
    gap: var(--space-2);
}

.email-rate-info {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.email-send-status {
    font-size: var(--text-sm);
    margin-top: var(--space-2);
}

/* Batch send modal */
.batch-send-queue {
    max-height: 200px;
    overflow-y: auto;
    margin-bottom: var(--space-3);
}

.batch-send-info {
    font-size: var(--text-xs);
    color: var(--text-muted);
}

.batch-progress-bar-wrap {
    height: 6px;
    background: var(--bg-base);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: var(--space-2);
}

.batch-progress-bar {
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
    transition: width var(--transition-fast);
}

.batch-progress-text {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    text-align: center;
}

.batch-progress-current {
    font-size: var(--text-xs);
    color: var(--text-muted);
    text-align: center;
    margin-top: var(--space-1);
}

.batch-progress-log {
    font-size: var(--text-xs);
    color: var(--text-muted);
    max-height: 100px;
    overflow-y: auto;
    margin-top: var(--space-2);
}

.promo-target-email-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: var(--space-1);
    color: var(--text-muted);
}

.promo-target-email-btn:hover { color: var(--accent); }

@media (max-width: 768px) {
    .promo-stats-bar { grid-template-columns: repeat(3, 1fr); }
    .promo-filter-row { flex-direction: column; align-items: flex-start; }
}
```

- [ ] **Step 2: Update promotion.html template**

Add `{% block page_css %}` and `{% block breadcrumb %}`. The existing template structure stays — the CSS handles the visual upgrade. Key class additions for consistency with the new design.

- [ ] **Step 3: Verify promotion page**

Run the app, navigate to promotion. Verify:
- Stats shown as metric cards (not cramped bar)
- Target rows have more space
- All interactive elements at comfortable size
- Filters work correctly

- [ ] **Step 4: Commit**

```bash
git add release_manager/static/css/pages/promotion.css release_manager/templates/promotion.html
git commit -m "feat(ui): redesign promotion page with metric cards and larger targets"
```

---

## Task 11: Remaining Page CSS Files

**Files:**
- Create: `release_manager/static/css/pages/artwork-resizer.css`
- Create: `release_manager/static/css/pages/video-resizer.css`
- Create: `release_manager/static/css/pages/seo-copy.css`
- Create: `release_manager/static/css/pages/stats.css`
- Create: `release_manager/static/css/pages/settings.css`
- Modify: remaining templates to add `{% block page_css %}` and `{% block breadcrumb %}`

- [ ] **Step 1: Create page CSS files for remaining pages**

Migrate relevant styles from old `style.css` for each page, converting all values to tokens. Each file should be self-contained for its page's unique styles (shared components come from `components.css`).

For each page CSS file, extract the relevant section from the old `style.css` and replace raw values with token references:
- Colors: `#xxx` -> `var(--token)`
- Spacing: `Npx` -> `var(--space-N)`
- Font sizes: `Npx` -> `var(--text-N)`
- Radius: `Npx` -> `var(--radius-N)`
- Shadows: raw values -> `var(--shadow-N)`

- [ ] **Step 2: Update remaining templates**

For each template (`artwork_resizer.html`, `video_resizer.html`, `seo_copy.html`, `stats.html`, `palette.html`):
- Add `{% block page_css %}` linking to the page's CSS file
- Add `{% block breadcrumb %}` with appropriate navigation
- Remove any wrapping container divs that duplicate what `.content` provides

- [ ] **Step 3: Verify all pages load correctly**

Navigate to every page in the app and verify:
- Sidebar active state matches current page
- Breadcrumb is correct
- No broken layouts
- All functionality still works (upload, resize, generate, etc.)

- [ ] **Step 4: Commit**

```bash
git add release_manager/static/css/pages/ release_manager/templates/
git commit -m "feat(ui): apply design system to artwork, video, SEO, stats, and settings pages"
```

---

## Task 12: Remove Old style.css + Final Cleanup

**Files:**
- Delete: `release_manager/static/style.css`
- Modify: `release_manager/templates/base.html` (if old CSS still referenced)

- [ ] **Step 1: Verify the old style.css is no longer referenced**

Search all templates for references to `style.css`:

Run: `grep -r "style.css" release_manager/templates/`

Expected: No results (all templates now use the modular CSS files via base.html).

- [ ] **Step 2: Delete the old style.css**

Run: `rm release_manager/static/style.css`

- [ ] **Step 3: Full smoke test**

Navigate to every page in the app:
1. Dashboard — cards render, social links work
2. Release detail — hero, all 7 tabs, calendar nav, checklist toggle, SEO copy buttons
3. Engagement — stats, platform queues, contact actions, collapsible sections
4. Promotion — stats cards, target list, filters, email compose
5. Artwork resizer — upload, focal point, platform checkboxes
6. Video resizer — same checks
7. SEO copy — generate, results
8. Stats — tabs, charts
9. Settings — palette picker

Verify: sidebar collapse/expand, mobile drawer, toast notifications, keyboard shortcuts (Escape).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore(ui): remove legacy style.css, complete CSS modularization"
```

---

## Task 13: Update stats.js Chart Colors

**Files:**
- Modify: `release_manager/static/stats.js`

- [ ] **Step 1: Update Chart.js color references to match new palette**

In `stats.js`, find where chart colors are defined (typically as hex arrays or rgba values) and update them to align with the new design tokens:
- Primary data color: `#c9a84c` (accent)
- Secondary: `#5a6e8a` (info)
- Success: `#4a7c59`
- Error: `#8b3a3a`
- Background grid: `rgba(255, 255, 255, 0.04)`
- Text labels: `#a0a0b0`

- [ ] **Step 2: Verify charts render with new colors**

Navigate to Stats Dashboard, check all tabs (Overview, Platforms, Releases, Trends). Charts should use the updated palette.

- [ ] **Step 3: Commit**

```bash
git add release_manager/static/stats.js
git commit -m "feat(ui): update chart colors to match new design system"
```
